# -*- coding: utf-8 -*-
"""新浪新闻爬虫解析逻辑单元测试（无需真实网络）。"""
import pytest
from scrapy.http import HtmlResponse

from sina_news_crawler.spiders.sina_spider import SinaSpider
from sina_news_crawler.items import SinaNewsItem


def make_response(html):
    return HtmlResponse(
        url='https://news.sina.com.cn/',
        body=html.encode('utf-8'),
        encoding='utf-8',
    )


HTML_SAMPLE = """
<html>
<body>
  <div class="top-news">
    <h1>头条新闻标题</h1>
    <a href="https://news.sina.com.cn/headline/1.html">头条新闻标题</a>
    <span class="source">新浪新闻</span>
    <span class="time">2026-09-21 10:00</span>
  </div>

  <div class="news-item">
    <a href="https://news.sina.com.cn/c/2.html">国内要闻一</a>
    <p>这是摘要内容</p>
    <span class="source">新华社</span>
    <span class="category">国内</span>
  </div>

  <div class="news-item">
    <a href="https://news.sina.com.cn/c/3.html">国际要闻二</a>
    <span class="category">国际</span>
  </div>

  <ul class="news-list">
    <li><a href="https://news.sina.com.cn/r/4.html">滚动新闻一</a><span>12:30</span></li>
    <li><a href="https://news.sina.com.cn/r/5.html">滚动新闻二</a></li>
  </ul>

  <div class="channel">
    <h2>体育</h2>
    <a href="https://news.sina.com.cn/s/6.html">体育频道新闻</a>
  </div>

  <div class="news-item">
    <a href="https://news.sina.com.cn/dup/7.html">重复新闻</a>
    <span class="category">财经</span>
  </div>
  <div class="top-news">
    <a href="https://news.sina.com.cn/dup/7.html">重复新闻</a>
  </div>
</body>
</html>
"""


def collect_items(spider, html):
    """解析 HTML 并返回 (items, response)。"""
    response = make_response(html)
    items = list(spider.parse(response))
    return items, response


class TestSinaSpider:

    def test_parse_all_sections(self):
        """各区块（头条/列表/滚动/频道）应被正确解析。"""
        spider = SinaSpider()
        items, _ = collect_items(spider, HTML_SAMPLE)

        # 头条1 + 列表2 + 滚动2 + 频道1 + 重复1(去重后应只剩5条唯一URL)
        urls = {item['url'] for item in items}
        assert len(urls) == 6, f"应有6条唯一URL，实际 {len(urls)}: {urls}"
        assert len(items) == 6, f"去重后应剩6条，实际 {len(items)}"

        assert all(isinstance(item, SinaNewsItem) for item in items)

    def test_headline_category(self):
        """头条新闻分类应为 headline。"""
        spider = SinaSpider()
        items, _ = collect_items(spider, HTML_SAMPLE)
        headline = next(i for i in items if i['category'] == 'headline')
        assert headline['title'] == '头条新闻标题'
        assert headline['source'] == '新浪新闻'
        assert headline['publish_time'] == '2026-09-21 10:00'
        assert headline['crawl_time']

    def test_category_mapping(self):
        """中文分类应映射为英文标识。"""
        spider = SinaSpider()
        items, _ = collect_items(spider, HTML_SAMPLE)
        categories = {i['title']: i['category'] for i in items}
        assert categories['国内要闻一'] == 'domestic'
        assert categories['国际要闻二'] == 'international'
        assert categories['体育频道新闻'] == 'sports'

    def test_rolling_news(self):
        """滚动新闻分类应为 rolling，无分类时默认'新浪新闻'。"""
        spider = SinaSpider()
        items, _ = collect_items(spider, HTML_SAMPLE)
        rolling = [i for i in items if i['category'] == 'rolling']
        assert len(rolling) == 2
        assert rolling[0]['source'] == '新浪新闻'

    def test_dedupe_by_url(self):
        """同一 URL 只保留首条。"""
        spider = SinaSpider()
        assert spider._dedupe('https://a.com/x')
        assert not spider._dedupe('https://a.com/x')
        assert spider._dedupe('https://a.com/y')

    def test_missing_title_returns_none(self):
        """缺少标题的条目应被丢弃（返回 None）。"""
        spider = SinaSpider()
        html = '<html><body><div class="news-item"><a href="https://news.sina.com.cn/x.html"></a></div></body></html>'
        items, _ = collect_items(spider, html)
        assert items == []
