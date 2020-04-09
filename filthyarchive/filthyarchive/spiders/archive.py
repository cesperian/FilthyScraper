# -*- coding: utf-8 -*-
import scrapy
from ..items import FilthyarchiveItem

class ArchiveSpider(scrapy.Spider):
    name = 'getarchive'
    # allowed_domains = ['http://www.millbankusa.com/filthycritic/recent-shit']

    # reviews pp set by form post. Also takes qs, so use for now
    # Mod'd py for changing dropdown in snippets.txt
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
        targets = response.css("td a::attr(href)").getall()
        # yield {'res': str(testEl.len())}
        if targets is not None:
            targets = targets[0:4]
            for target in targets:
                yield response.follow(target, callback=self.procRev)

    def procRev(self, response):
        review = FilthyarchiveItem()

        review['title'] = response.css("h1.title::text").get()

        keywords = response.css(".tags li")
        review['rating'] = keywords.css("a[href$='fingers']::text").get().strip().split(' ')[0]
        review['year'] = keywords.css("a[href*='tags/tag']::text").get().strip()
        genres = keywords.css("a:not([href*='tags/tag'])::text, a:not([href$='fingers'])::text").getall()
        review['genre'] = ''
        for g in genres:
            gArr = []
            gArr.append(g.strip())
            review['genre'] = "&".join(gArr)

        # movie screenshots...
        imgUrls = response.css("p+ p img::attr(src)").getall()
        imgNames = self.procNames(imgUrls)
        review['image_names'] = "&".join(imgNames)
        review['image_urls'] = self.relToAbs(imgUrls, response)

        # todo; ::text excludes nested <strong>'s. Find a way to 'flatten'
        # review['content'] = response.css("div.content > *::text").getall()

        review['content'] = ''
        content = response.css("div.content > *").getall()
        for children in content:
            frag = children.partition('<img')
            review['content'] += (frag[0] + frag[2].partition('>')[2])

        yield review
