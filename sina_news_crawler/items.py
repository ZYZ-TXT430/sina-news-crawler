# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SinaNewsItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    summary = scrapy.Field()
    source = scrapy.Field()
    publish_time = scrapy.Field()
    crawl_time = scrapy.Field()
    category = scrapy.Field()