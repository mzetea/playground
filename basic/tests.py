import unittest
from unittest.mock import patch

from main import Spider, DomainValidator, FOUND, INVALID_STATUS_MESSAGE, Resources


class TestObj:
    status_code = None

    def __init__(self, status_code):
        self.status_code = status_code


class TestSpider(unittest.TestCase):

    def test_set_domain(self):
        test_domain = "http://www.test.com"
        test_domain_expected = "http://test.com"
        resulting_domain = Spider.set_domain(test_domain)
        self.assertEqual(test_domain_expected, resulting_domain)
        test_domain2 = "http://abc.com"
        test_domain2_expected = test_domain2
        resulting_domain2 = Spider.set_domain(test_domain2)
        self.assertEqual(test_domain2_expected, resulting_domain2)

    def test_validator_url(self):
        response_obj = TestObj(FOUND)
        test_url = "http://www.test.com"
        with patch('requests.head', return_value=response_obj):
            valid, message = DomainValidator.validate_url(test_url)
            self.assertEqual(valid, True)
            self.assertEqual(message, 'Found')

        response_obj2 = TestObj(404)
        with patch('requests.head', return_value=response_obj2):
            valid, message = DomainValidator.validate_url(test_url)
            self.assertEqual(valid, False)
            self.assertEqual(message, INVALID_STATUS_MESSAGE)

    def test_resource_write(self):
        res = Resources()
        to_write = [], [], [], []
        key = 'test'

        res.write(key, to_write)
        self.assertEqual(res.read(key, 'parsed'), True)
        self.assertEqual(len(res.resources[key]), 5)

        all = res.read_all()
        self.assertEqual(all[key]['internal_links'], [])

    def test_spider(self):
        test_domain = "http://localhost:9090"
        spider = Spider(test_domain)
        self.assertEquals(spider.domain, test_domain)
        spider.retrieve_content()

        key = test_domain
        internal_links = ["http://localhost:9090/test2.html"]
        internal_images = ["http://localhost:9090/img.jpg"]
        external_links = ["http://www.google.com"]
        external_images = ["http://www.google.com/test.jpg"]

        read_res = spider.resources.read(key, 'internal_links')
        read_all = spider.resources.read_all()
        second = "http://localhost:9090/test2.html"
        self.assertEqual(read_res, internal_links)
        self.assertEqual(read_all[second]['internal_links'], [])
        self.assertEqual(read_all[second]['internal_images'], [])
        self.assertEqual(read_all[second]['external_links'], ['http://www.twitter.com'])
        self.assertEqual(read_all[second]['external_images'], [])

        self.assertEqual(read_all[test_domain]['internal_images'], internal_images)
        self.assertEqual(read_all[test_domain]['external_images'], external_images)
        self.assertEqual(read_all[test_domain]['external_links'], external_links)