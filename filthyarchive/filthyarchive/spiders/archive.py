# -*- coding: utf-8 -*-
import scrapy


class ArchiveSpider(scrapy.Spider):
    name = 'archive'
    allowed_domains = ['http://www.millbankusa.com/filthycritic/recent-shit']
    start_urls = ['http://http://www.millbankusa.com/filthycritic/recent-shit/']

    def parse(self, response):
        pass
