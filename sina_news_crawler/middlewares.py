# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import random
from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message


class SinaNewsSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        pass

    def process_start_requests(self, start_requests, spider):
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class SinaNewsDownloaderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RandomUserAgentMiddleware(UserAgentMiddleware):
    def __init__(self, user_agents):
        self.user_agents = user_agents

    @classmethod
    def from_crawler(cls, crawler):
        return cls(user_agents=crawler.settings.getlist('USER_AGENTS'))

    def process_request(self, request, spider):
        user_agent = random.choice(self.user_agents)
        if user_agent:
            request.headers.setdefault(b'User-Agent', user_agent)
            spider.logger.debug(f"Using User-Agent: {user_agent}")


class RandomDelayMiddleware:
    """
    随机请求延迟中间件。

    说明：Scrapy 下载器为单线程事件循环，若在中间件中直接 time.sleep
    会阻塞整个引擎，导致所有并发请求排队。正确做法是通过
    request.meta['download_delay'] 设置每请求延迟，由下载器异步调度，
    不会阻塞其他请求。
    """

    def __init__(self, delay_range=(1, 3)):
        self.delay_range = delay_range

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def process_request(self, request, spider):
        delay = random.uniform(*self.delay_range)
        request.meta['download_delay'] = delay
        spider.logger.debug(f"Set per-request download delay: {delay:.2f}s")


class ProxyMiddleware:
    def __init__(self, proxies):
        self.proxies = proxies

    @classmethod
    def from_crawler(cls, crawler):
        return cls(proxies=crawler.settings.getlist('PROXIES'))

    def process_request(self, request, spider):
        if self.proxies:
            proxy = random.choice(self.proxies)
            request.meta['proxy'] = proxy
            spider.logger.debug(f"Using proxy: {proxy}")


class CustomRetryMiddleware(RetryMiddleware):
    def process_response(self, request, response, spider):
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            spider.logger.warning(f"Retrying {request.url} (status: {response.status})")
            return self._retry(request, reason, spider) or response
        return response