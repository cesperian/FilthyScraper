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

    def post_search(self, response):
        print("post search;")
        # resLink = response.xpath("//table[@class='findList']//tr[first()]/td[last()]/a/text()").get()
        # resLink = response.xpath("//table[@class='findList']//tr[position()=1]/td[position()=1]/a/text()").get()
        resLink = response.css("table.findList a::attr(href)").get()
        if resLink is not None:
            print('post search link = ' + resLink)
            return response.follow(resLink,callback=self.post_find)
        else:
            print('no post search link')

    def stripRes(self, res):
        return res.replace('\n','').strip()

    def post_find(self, response):
        details = DetailsItem()
        plot = response.css(".plot_summary_wrapper .summary_text::text").get()
        mpaa = response.css(".title_wrapper .subtext::text").get()
        duration = response.css(".title_wrapper .subtext time::text").get()
        actors = response.xpath("//div[@class='credit_summary_item'][last()]/a/text()").getall()
        directors = response.xpath("//div[@class='credit_summary_item'][1]/a/text()").getall()
        genres_rDate = response.css(".title_wrapper .subtext a::text").getall()
        imgLink = response.css(".poster a::attr(href)").get()
        imgName = response.css(".poster img::attr(title)").get()
        imgName = imgName.replace(' ','_').rpartition('_')[0]
        imgUrl = response.css(".poster img::attr(src)").get()
        # add proper file ext to use when setting img output path..
        imgName += ('_sm.' + (imgUrl.rpartition('.')[2]))

        if imgUrl is not None:
            details['image_names'] = [imgName]
            details['image_urls'] = [imgUrl]

        if plot is not None:
            details['plot'] = self.stripRes(plot)
            details['mpaa_rating'] = self.stripRes(mpaa)
            details['duration'] = self.stripRes(duration)
            details['directors'] = directors
            details['actors'] = actors if actors[-1].find('See full') == -1 else actors[0:-1]
            details['release_date'] = self.stripRes(genres_rDate[-1])
            details['genres'] = genres_rDate[0:-1]
        else:
            print('missing details')
            print(plot)
            print(actors)
            print(directors)
            print(mpaa)
            print(duration)
            print(genres_rDate)

        # print(details)
        yield details
        yield response.follow(imgLink, callback=self.post_img_link)


    def post_img_link(self, response):
        id = (response.url).split('/')[-3]
        scripts = response.css("script::text").getall()
        scripts = ' '.join(scripts)
        pImg = PosterImageItem()
        for s, e, o in jsonfinder(scripts):
            # print(s, ':', e)
            if o is not None:
                imgName = o['galleries'][id]['allTitles'][id]['displayName']
                imgUrl = o['galleries'][id]['allImages'][0]['src']
                imgName += '_lg.' + imgUrl.rpartition('.')[2]
                pImg['image_urls'] = [imgUrl]
                pImg['image_names'] = [imgName]
                yield pImg

    def parse(self, response):
        self.cursor.execute("select * from reviews limit 1")
        rs = self.cursor.fetchall()
        self.conn.close()
        print('title = ' + rs[0][0])
        title = rs[0][0]
        # return [FormRequest(url="https://www.imdb.com/find",
        #         formdata={'q': title},
        #         callback = self.post_search(response))]
        return FormRequest.from_response(
            response,
            formdata={'q': title},
            callback = self.post_search)


