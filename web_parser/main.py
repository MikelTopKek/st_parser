import scrapy
from scrapy.crawler import CrawlerProcess

from web_parser.web_parser.spiders.item_spider import ItemSpider


def main():
    process = CrawlerProcess()
    process.crawl(ItemSpider)
    process.start()
