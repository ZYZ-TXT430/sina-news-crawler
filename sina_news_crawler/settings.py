BOT_NAME = 'sina_news_crawler'

SPIDER_MODULES = ['sina_news_crawler.spiders']
NEWSPIDER_MODULE = 'sina_news_crawler.spiders'

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
]

DOWNLOADER_MIDDLEWARES = {
    'sina_news_crawler.middlewares.RandomUserAgentMiddleware': 543,
    'sina_news_crawler.middlewares.RandomDelayMiddleware': 544,
    'sina_news_crawler.middlewares.ProxyMiddleware': 545,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'sina_news_crawler.middlewares.CustomRetryMiddleware': 550,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 700,
}

# 随机请求延迟：Scrapy 原生会在 [0.5, 1.5] * DOWNLOAD_DELAY 范围内随机化，
# 配合 RandomDelayMiddleware 的每请求延迟，进一步打散访问节奏
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True

CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 2

RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [403, 404, 500, 502, 503, 504]

REDIRECT_ENABLED = True

HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

LOG_LEVEL = 'INFO'

FEED_EXPORT_ENCODING = 'utf-8'

ROBOTSTXT_OBEY = False

ITEM_PIPELINES = {
    'sina_news_crawler.pipelines.SinaNewsPipeline': 300,
}

PROXIES = [
]