""" Application entry point
Identify internal and external links and images
Follow internal links, ignore external
"""
import sys
import logging
from urllib .parse import urlparse

import requests
from bs4 import BeautifulSoup

#basic logger instance. it will output to the console. Can accept conf file
logger = logging.getLogger(__name__)


FOUND = 200
INVALID_DOMAIN_MESSAGE = "Invalid. Check logging for proper exception"
INVALID_STATUS_MESSAGE = "Cannot Parse url. Check logging for details"
VALID_INTERNALS = ["#", "/#"]

class DomainValidator:
    """ validate if domain exists.
    basic implementation, wrapped in class so further extension is possible
    """

    @staticmethod
    def validate_url(url):
        try:
            request_obj = requests.head(url, allow_redirects=True)
        except Exception as e:
            logger.exception(str(e))
            return False, INVALID_DOMAIN_MESSAGE
        if request_obj.status_code != FOUND:
            logger.exception(Exception(
                    "Provided URL cannot be accessed. Response status code was: %s" % str(request_obj.status_code)))
            return False, INVALID_STATUS_MESSAGE
        return True, 'Found'


class Resources:
    """ Basic resources class that proxies write and read.
    It can be overriden so that the application is able to scale in multiprocess mode with central storage for
    results
    """

    resources = None

    def __init__(self):
        #override this and instantiate resources as needed
        self.resources = {}

    def write(self, key, content):
        if not self.resources.get(key):
            self.resources[key] = dict.fromkeys(['internal_links', 'external_links',
                                                 'internal_images', 'external_images', 'parsed'])
        self.resources[key]['parsed'] = True
        self.resources[key]['internal_links'] = content[0]
        self.resources[key]['external_links'] = content[1]
        self.resources[key]['internal_images'] = content[2]
        self.resources[key]['external_images'] = content[3]

    def read(self, key, resource_type):
        try:
            return self.resources[key][resource_type]
        except KeyError:
            logger.exception("Cannot identify key in resources. Key was: %s, Resource type was: %s" % (key, resource_type))
            return None

    def read_all(self):
        return self.resources


class Spider:
    """ parse sites
    :returns links and images in @resources
    """

    domain = None
    resources = Resources()
    validator = DomainValidator
    soup = BeautifulSoup

    def __init__(self, input_domain):
        valid, message = DomainValidator.validate_url(input_domain)
        if not valid:
            print(message)
            sys.exit(1)
        self.domain = self.set_domain(input_domain)

    @staticmethod
    def set_domain(input_domain):
        url_obj = urlparse(input_domain)
        domain_name = "%s://%s" % (url_obj.scheme, url_obj.netloc.replace("www.", ""))
        return domain_name

    def retrieve_content(self, url=None):
        url = url if url else self.domain
        response = requests.get(url, allow_redirects=True)
        if response.status_code == FOUND:
            resources = self.identify_resources(response.content)
            to_write = self.resources.read(url, 'parsed')
            if to_write is None:
                self.resources.write(url, resources)
                for item in self.resources.read(url, 'internal_links'):
                    valid, message = self.validator.validate_url(item)
                    if valid:
                        self.retrieve_content(url=item)

    def identify_resources(self, content):
        content_object = self.soup(content, 'html5lib')
        internal_links = []
        external_links = []
        internal_images = []
        external_images = []

        links = content_object.find_all("a")
        images = content_object.find_all("img")

        for item in links:
            href = item.get('href')
            if not href:
                continue
            if self.is_internal_link(href):
                internal_links.append(href)
            else:
                external_links.append(href)
        for img in images:
            src = img.get('src')
            if not src:
                continue
            if self.is_internal_image(src):
                internal_images.append(src)
            else:
                external_images.append(src)

        return internal_links, external_links, internal_images, external_images

    def is_internal_link(self, link):
        if self.domain in link or link.startswith("#") or link.startswith("/#"):
            return True
        return False

    def is_internal_image(self, image):
        if self.domain in image:
            return True
        return False

if __name__ == "__main__":
    domain = input("Please enter a domain to scrape\n")
    spider = Spider(domain)
    spider.retrieve_content()
    print(spider.resources.read_all())
    import pdb; pdb.set_trace()

