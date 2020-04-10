# -*- coding: utf-8 -*-
import scrapy
from ..items import FilthyarchiveItem

class ArchiveSpider(scrapy.Spider):
    name = 'getarchive'
    # allowed_domains = ['http://www.millbankusa.com/filthycritic/recent-shit']

    # reviews pp set by form post. Also takes qs, so use for now
    # Mod'd py for changing dropdown in snippets.txt
    start_urls = ['http://www.millbankusa.com/filthycritic/recent-shit?limit=0']
    # start_urls = ['http://www.millbankusa.com/filthycritic/recent-shit']
    # start_urls = ['http://www.millbankusa.com/filthycritic/recent-shit/593-you-ve-got-mail']

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
        targets = response.css("table.zebra td a::attr(href)").getall()
        if bool(targets): # if scraping >1 review..
            # targets = targets[0:3]
            # todo; change loop to 'follow_all()'
            for target in targets:
                yield response.follow(target, callback=self.parse)
            return

        review = FilthyarchiveItem()

        # title
        title = response.css("h1.title::text").get()
        review['title'] = title.replace("'",'&#39;')

        # rating, genres, year, reviews by Jimmy
        keywords = response.css(".tags li")

        # some reviews a rating in keywords, some dont
        # Mark all rbj with a 0-rating indicator
        # rating = keywords.css("a[href$='finger']::text").get()
        rating = response.css("div.content img[src*='finger']::attr(src)").get()
        byJimmy = keywords.css("a[href$='jimmy']").get()
        if rating is not None:
            ratings = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}
            review['rating'] = ratings.get(rating.split('/')[-1].split('_')[0])
        if byJimmy is not None:
            review['rating'] = 0

        review['genres'] = []
        for kw in keywords:
            k = kw.css('a::text').get().strip().lower()
            if len(k) == 4:
                review['year'] = k
            elif ('jimmy' not in k) and ('finger' not in k):
                review['genres'].append(k)

        # movie screenshots...
        imgUrls = response.css("p+ p img::attr(src)").getall()
        if imgUrls is not None:
            review['image_names'] = self.procNames(imgUrls)
            review['image_urls'] = self.relToAbs(imgUrls, response)

        review['content'] = ''
        content = response.css("div.content > *").getall()
        for children in content:
            # remove images from content
            frag = children.partition('<img')
            frag = (frag[0] + frag[2].partition('>')[2])
            # remove all attributes (deprecated, etc)
            while '">' in frag:
                attrEnd =  frag.partition('">')
                tagStart = attrEnd[0].rpartition('<')
                tag = tagStart[2].partition(' ')
                frag = (tagStart[0] + tagStart[1] + tag[0] + '>' + attrEnd[2])
            review['content'] += frag.replace('"', '&#34;').replace("'",'&#39;')
        yield review
