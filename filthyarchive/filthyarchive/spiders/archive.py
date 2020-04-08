# -*- coding: utf-8 -*-
import scrapy
from ..items import FilthyarchiveItem

class ArchiveSpider(scrapy.Spider):
    name = 'getarchive'
    # allowed_domains = ['http://www.millbankusa.com/filthycritic/recent-shit']

    # reviews pp set by form post. Also takes qs use for now. Mod'd py for changing dropdown at bottom
    start_urls = ['http://www.millbankusa.com/filthycritic/recent-shit']
    # start_urls = ['http://www.millbankusa.com/filthycritic/recent-shit?limit=0']

    def relToAbs(self, urls, response):
        absUrls = []
        for url in urls:
            absUrls.append(response.urljoin(url))
        return absUrls

    def procNames(self, names):
        prettyName = []
        for name in names:
            prettyName.append(name.split('/')[-1])
        return prettyName

    def parse(self, response):
        target = response.css("td a::attr(href)").get()
        # yield {'res': str(testEl.len())}
        if target is not None:
            yield response.follow(target, callback=self.procRev)

    def procRev(self, response):
        review = FilthyarchiveItem()

        review['title'] = response.css("h1.title::text").get()
        review['rating'] = response.css(".tag-list0 .label-info::text").get().strip().split(' ')[0]
        review['genre'] = response.css(".tag-list1 .label-info::text").get().strip()
        review['year'] = response.css(".tag-list2 .label-info::text").get().strip()

        # movie screenshots...
        imgUrls = response.css("p+ p img::attr(src)").getall()

        review['image_names'] = self.procNames(imgUrls)
        review['image_urls'] = self.relToAbs(imgUrls, response)

        # todo; ::text excludes nested <strong>'s. Find a way to 'flatten'
        # review['content'] = response.css("div.content > *::text").getall()

        review['content'] = []
        content = response.css("div.content > *").getall()
        for children in content:
            frag = children.partition('<img')
            review['content'].append(frag[0] + frag[2].partition('>')[2])

        yield review
