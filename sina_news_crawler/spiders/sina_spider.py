# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
from sina_news_crawler.items import SinaNewsItem


class SinaSpider(scrapy.Spider):
    name = 'sina'
    allowed_domains = ['sina.com.cn', 'news.sina.com.cn']
    start_urls = ['https://news.sina.com.cn/']

    category_mapping = {
        '国内': 'domestic',
        '国际': 'international',
        '财经': 'finance',
        '体育': 'sports',
        '娱乐': 'entertainment',
        '科技': 'tech',
        '军事': 'military',
        '教育': 'education',
        '健康': 'health',
        '文化': 'culture',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 同一页面多个区块可能命中同一条新闻，用 URL 去重避免重复入库
        self.seen_urls = set()

    def parse(self, response):
        self.logger.info(f"开始解析新浪新闻首页: {response.url}")
        
        headlines = response.xpath('//div[contains(@class, "top-news")]')
        for headline in headlines:
            item = self.parse_headline(headline)
            if item:
                yield item
        
        news_items = response.xpath('//div[contains(@class, "news-item") or contains(@class, "list-item")]')
        for news_item in news_items:
            item = self.parse_news_item(news_item)
            if item:
                yield item
        
        rolling_news = response.xpath('//ul[contains(@class, "list") or contains(@class, "news-list")]/li')
        for news in rolling_news:
            item = self.parse_rolling_news(news)
            if item:
                yield item
        
        channels = response.xpath('//div[contains(@class, "channel") or contains(@class, "section")]')
        for channel in channels:
            category = channel.xpath('.//h2/text()').get() or channel.xpath('.//span/text()').get()
            news_links = channel.xpath('.//a[contains(@href, "sina.com.cn")]')
            for link in news_links:
                item = self.parse_channel_news(link, category)
                if item:
                    yield item

    def _dedupe(self, url):
        """按 URL 去重，返回 True 表示首次出现可继续处理。"""
        if not url:
            return False
        if url in self.seen_urls:
            return False
        self.seen_urls.add(url)
        return True

    def parse_headline(self, selector):
        try:
            title = selector.xpath('.//h1/text()').get() or selector.xpath('.//a/text()').get()
            url = selector.xpath('.//a/@href').get()
            
            if not title or not url:
                return None
            
            source = selector.xpath('.//span[contains(@class, "source")]/text()').get()
            publish_time = selector.xpath('.//span[contains(@class, "time")]/text()').get()
            
            item = SinaNewsItem()
            item['title'] = title.strip() if title else None
            item['url'] = url.strip() if url else None
            if not self._dedupe(item['url']):
                return None
            item['summary'] = None
            item['source'] = source.strip() if source else '新浪新闻'
            item['publish_time'] = publish_time.strip() if publish_time else None
            item['crawl_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['category'] = 'headline'
            
            return item
        except Exception as e:
            self.logger.error(f"解析头条新闻失败: {e}")
            return None

    def parse_news_item(self, selector):
        try:
            title = selector.xpath('.//a/text()').get()
            url = selector.xpath('.//a/@href').get()
            
            if not title or not url:
                return None
            
            summary = selector.xpath('.//p/text()').get()
            source = selector.xpath('.//span[contains(@class, "source")]/text()').get()
            publish_time = selector.xpath('.//span[contains(@class, "time")]/text()').get()
            category = selector.xpath('.//span[contains(@class, "category")]/text()').get()
            
            item = SinaNewsItem()
            item['title'] = title.strip() if title else None
            item['url'] = url.strip() if url else None
            if not self._dedupe(item['url']):
                return None
            item['summary'] = summary.strip() if summary else None
            item['source'] = source.strip() if source else '新浪新闻'
            item['publish_time'] = publish_time.strip() if publish_time else None
            item['crawl_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['category'] = self.category_mapping.get(category, 'other') if category else 'other'
            
            return item
        except Exception as e:
            self.logger.error(f"解析新闻列表项失败: {e}")
            return None

    def parse_rolling_news(self, selector):
        try:
            title = selector.xpath('.//a/text()').get()
            url = selector.xpath('.//a/@href').get()
            
            if not title or not url:
                return None
            
            publish_time = selector.xpath('.//span/text()').get()
            
            item = SinaNewsItem()
            item['title'] = title.strip() if title else None
            item['url'] = url.strip() if url else None
            if not self._dedupe(item['url']):
                return None
            item['summary'] = None
            item['source'] = '新浪新闻'
            item['publish_time'] = publish_time.strip() if publish_time else None
            item['crawl_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['category'] = 'rolling'
            
            return item
        except Exception as e:
            self.logger.error(f"解析滚动新闻失败: {e}")
            return None

    def parse_channel_news(self, selector, category):
        try:
            title = selector.xpath('./text()').get()
            url = selector.xpath('./@href').get()
            
            if not title or not url:
                return None
            
            item = SinaNewsItem()
            item['title'] = title.strip() if title else None
            item['url'] = url.strip() if url else None
            if not self._dedupe(item['url']):
                return None
            item['summary'] = None
            item['source'] = '新浪新闻'
            item['publish_time'] = None
            item['crawl_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['category'] = self.category_mapping.get(category, 'other') if category else 'other'
            
            return item
        except Exception as e:
            self.logger.error(f"解析频道新闻失败: {e}")
            return None