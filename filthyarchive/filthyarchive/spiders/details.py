# -*- coding: utf-8 -*-
import scrapy
import sqlite3
from jsonfinder import jsonfinder, has_json
from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import FormRequest
from ..items import DetailsItem, PosterImageItem

class DetailsSpider(scrapy.Spider):
    name = 'details'
    # allowed_domains = ['https://www.imdb.com/']
    # start_urls = ['https://www.imdb.com/']
    start_urls = ["https://www.imdb.com/find"]
    # start_urls = ['http://quotes.toscrape.com/']

    def __init__(self):
        self.conn = sqlite3.connect('filthy_archive.db')
        self.cursor = self.conn.cursor()

    def post_search(self, response, title):
        print("post search;")
        # resLink = response.xpath("//table[@class='findList']//tr[first()]/td[last()]/a/text()").get()
        # resLink = response.xpath("//table[@class='findList']//tr[position()=1]/td[position()=1]/a/text()").get()
        resLink = response.css("table.findList a::attr(href)").get()
        if resLink is not None:
            print('post search link = ' + resLink)
            args = response.cb_kwargs
            return response.follow(
                resLink,
                callback=self.post_find,
                cb_kwargs=dict(title=title)
            )
        else:
            print('no post search link')

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
        self.cursor.execute("select * from reviews")
        rs = self.cursor.fetchall()
        self.conn.close()
        for t in rs[21:len(rs)]:
            print('title = ' + t[0])
            yield FormRequest.from_response(
                response,
                formdata={'q': t[0]},
                callback = self.post_search,
                cb_kwargs = dict(title=t[0])
            )


