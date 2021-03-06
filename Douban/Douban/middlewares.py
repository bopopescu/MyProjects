# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import random

import requests

from scrapy import signals
from scrapy.exceptions import CloseSpider

from twisted.internet import reactor
from twisted.internet.defer import Deferred

from Douban.agents import AGENTS


class DoubanSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RandomUserAgentMiddleware(object):
    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def process_request(self, request, spider):
        #agent = random.choice(AGENTS)
        agent = AGENTS[0]
        request.headers['User-Agent'] = agent


class ProxyMiddleware():
    def process_request(self, request, spider):
        proxy = requests.get('http://localhost:5000/api/proxy').json()['proxy']
        request.meta['proxy'] = proxy


class SleepMiddleware():
    sleep_time = 300

    def process_response(self, request, response, spider):
        engine = spider.crawler.engine

        def _resume():
            spider.logger.info('Spider resumed: %s' % spider.name)
            engine.unpause()

        if response.status == 400:
            spider.logger.info('Spider paused(throttle): %s' % spider.name)
            engine.pause()
            reactor.callLater(self.sleep_time, _resume)
            return request
        else:
            return response
