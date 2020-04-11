# -*- coding: utf-8 -*-
import scrapy
from ..items import BlurbItem

class BlurbsSpider(scrapy.Spider):
    name = 'blurbs'
    # allowed_domains = ['https://www.bigempire.com/filthy/archive.html']
    start_urls = ['https://www.bigempire.com/filthy/archive.html']

    def parse(self, response):
        rows = response.xpath("//table//table//tr")
        blurbObj = BlurbItem()
        for r in rows[118:125]:
            title = r.xpath(".//a//text()").get()
            blurb = r.xpath(".//td[last()-1]//text()").get()
            if (title is not None) and (blurb is not None):
                title = title.replace('\n','').strip()
                blurb = blurb.replace('\n','').strip()
                blurbObj['title'] = ' '.join(title.split())
                blurbObj['blurb'] = ' '.join(blurb.split())
                print(blurbObj)
                yield blurbObj