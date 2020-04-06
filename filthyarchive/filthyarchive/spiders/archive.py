# -*- coding: utf-8 -*-
import scrapy

class ArchiveSpider(scrapy.Spider):
    name = 'getarchive'
    # allowed_domains = ['http://www.millbankusa.com/filthycritic/recent-shit']

    # reviews pp set by form post. Also takes qs use for now. Mod'd py for changing dropdown at bottom
    start_urls = ['http://www.millbankusa.com/filthycritic/recent-shit']
    # start_urls = ['http://www.millbankusa.com/filthycritic/recent-shit?limit=0']

    def parse(self, response):
        test = response.css("td a::attr(href)").get()
        # yield {'res': str(testEl.len())}
        if test is not None:
            yield response.follow(test, callback=self.procRev)

    def procRev(self, response):
        test = response.css("p::text").get()
        yield {'resFollow': test}
        # pass