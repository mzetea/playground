The application requires python3 and the libraries specified in the reqs.txt file.

Create a python virtualenv
Activate environment
run "pip install -r reqs.txt"

cd basic
#run tests
python -m unittest

#run application
python main.py

Tradeoffs:
- 2 requests for each url, 1 for validation (head reques) and one for retrieving content
- tests are not 100% and cover only the basics
- app can be very very slow depending on IO
- currently is recursive but is set up in such way that can be scalled
- could/should have used scrapy for this but then there would not have been fun :) 

Decisions:
- resources object is meant to be overriden. Currently only a dictionary but offers 2 proxies to write and read data.
Resources object can hold centralized storage. Distributing this with celery for instance and a queue is as easy as setting them up
and adding apply_async() to the recursive call making it a task
