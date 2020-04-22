# -*- coding: utf-8 -*-
import scrapy
from jsonfinder import jsonfinder, has_json
from ..items import PosterImageItem


class TestcrawlSpider(scrapy.Spider):
    name = 'testcrawl'
    # allowed_domains = ['https://www.imdb.com/title/tt5807330/mediaviewer/rm57762304']
    start_urls = ['https://www.imdb.com/title/tt5807330/mediaviewer/rm57762304']

    def parse(self, response):
        id = (response.url).split('/')[-3]
        scripts = response.css("script::text").getall()
        scripts = ' '.join(scripts)
        test = PosterImageItem()
        for s, e, o in jsonfinder(scripts):
            # print(s, ':', e)
            if o is None:
                print('String:', repr(scripts[s:e]))
            else:
                imgName = o['galleries'][id]['allTitles'][id]['displayName']
                imgUrl = o['galleries'][id]['allImages'][0]['src']
                imgName += '_lg.' + imgUrl.rpartition('.')[2]
                test['image_urls'] = [imgUrl]
                test['image_names'] = [imgName]

        print(test)
        yield test