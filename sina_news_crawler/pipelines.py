from itemadapter import ItemAdapter
import json
import csv
import os
from datetime import datetime
from scrapy.exceptions import DropItem


class SinaNewsPipeline:
    def open_spider(self, spider):
        self.data_dir = 'sina_news_data'
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        self.json_file = open(f'{self.data_dir}/sina_news_{timestamp}.json', 'w', encoding='utf-8')
        self.json_file.write('[\n')
        self.first_item = True
        
        self.csv_file = open(f'{self.data_dir}/sina_news_{timestamp}.csv', 'w', encoding='utf-8-sig', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['标题', '链接', '摘要', '来源', '发布时间', '抓取时间', '分类'])

    def close_spider(self, spider):
        self.json_file.write('\n]')
        self.json_file.close()
        
        self.csv_file.close()
        
        spider.logger.info(f"数据已保存到 {self.data_dir}/")

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # 数据校验：标题或链接缺失的条目视为无效
        if not adapter.get('title') or not adapter.get('url'):
            raise DropItem(f"缺失标题或链接，丢弃: {adapter.get('url', '')[:60]}")

        if 'crawl_time' not in adapter or not adapter['crawl_time']:
            adapter['crawl_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if not self.first_item:
            self.json_file.write(',\n')
        else:
            self.first_item = False
        
        line = json.dumps(dict(adapter), ensure_ascii=False, indent=4)
        self.json_file.write(line)
        
        self.csv_writer.writerow([
            adapter.get('title', ''),
            adapter.get('url', ''),
            adapter.get('summary', ''),
            adapter.get('source', ''),
            adapter.get('publish_time', ''),
            adapter.get('crawl_time', ''),
            adapter.get('category', '')
        ])
        
        spider.logger.debug(f"已抓取新闻: {adapter['title']}")
        return item