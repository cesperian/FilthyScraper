# -*- coding: utf-8 -*-
import scrapy
import sqlite3
import json
from jsonfinder import jsonfinder, has_json
from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import FormRequest
from ..items import DetailsItem, PosterImageItem


class PatchdbSpider(scrapy.Spider):
    name = 'patchDB'
    # start_urls = ["https://www.imdb.com/find"]
    start_urls = ['http://quotes.toscrape.com/']

    def stripRes(self, res):
        return res.replace('\n','').strip()

    def post_find(self, response, title):
        details = DetailsItem()
        plot = response.css(".plot_summary_wrapper .summary_text::text").get()
        mpaa = response.css(".title_wrapper .subtext::text").get()
        duration = response.css(".title_wrapper .subtext time::text").get()
        actors = response.xpath("//div[@class='credit_summary_item'][last()]/a/text()").getall()
        directors = response.xpath("//div[@class='credit_summary_item'][1]/a/text()").getall()
        genres_rDate = response.css(".title_wrapper .subtext a::text").getall()
        imgLink = response.css(".poster a::attr(href)").get()
        imgName = "".join([c for c in title if c.isalpha() or c.isdigit()])
        imgUrl = response.css(".poster img::attr(src)").get()

        if imgUrl is not None:
            details['title'] = title
            details['image_names'] = [imgName + '_sm.' + (imgUrl.rpartition('.')[2])]
            details['image_urls'] = [imgUrl]
            details['plot'] = self.stripRes(plot)
            details['mpaa_rating'] = self.stripRes(mpaa) if bool(self.stripRes(mpaa)) else 'NR'
            details['duration'] = self.stripRes(duration)
            details['directors'] = directors
            details['actors'] = actors if actors[-1].find('See full') == -1 else actors[0:-1]
            details['release_date'] = self.stripRes(genres_rDate[-1])
            details['genres'] = genres_rDate[0:-1]
            # print(details)
            yield details
            yield response.follow(
                imgLink,
                callback=self.post_img_link,
                cb_kwargs=dict(title=imgName)
            )
        else:
            print('missing details')
            print(plot)
            print(actors)
            print(directors)
            print(mpaa)
            print(duration)
            print(genres_rDate)

    def post_img_link(self, response, title):
        id = (response.url).split('/')[-3]
        scripts = response.css("script::text").getall()
        scripts = ' '.join(scripts)
        pImg = PosterImageItem()
        for s, e, o in jsonfinder(scripts):
            if o is not None:
                imgUrl = o['galleries'][id]['allImages'][0]['src']
                # todo; refactor. get rid of nested cond...
                if bool(imgUrl):
                    pImg['image_urls'] = [imgUrl]
                    pImg['image_names'] = [title + '_lg.' + imgUrl.rpartition('.')[2]]
                    yield pImg

    def parse(self, response):
        f = open('patch_nullVals.json', 'r')
        titles = json.load(f)
        # print(titles[3:6])
        for t in titles[6:len(titles)]: # 3=BNB
            print('title = ' + t['title'])
            yield response.follow(
                t["url"].rpartition('?')[0],
                callback=self.post_find,
                cb_kwargs=dict(title=t['title'])
            )


