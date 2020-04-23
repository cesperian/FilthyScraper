# -*- coding: utf-8 -*-
import scrapy
import sqlite3
from jsonfinder import jsonfinder, has_json
from ..items import PosterImageItem


class TestcrawlSpider(scrapy.Spider):
    name = 'testcrawl'
    # allowed_domains = ['https://www.imdb.com/title/tt5807330/mediaviewer/rm57762304']
    start_urls = ['https://dorey.github.io/JavaScript-Equality-Table/']


    def __init__(self):
        self.conn = sqlite3.connect('filthy_archive.db')
        self.cursor = self.conn.cursor()

    def test(self, response, title):
        print('title = ' + title)

    def parse(self, response):
        self.cursor.execute("select * from reviews limit 10")
        rs = self.cursor.fetchall()
        self.conn.close()
        # print(rs[0][0])
        for t in rs[5:8]:
        #     print('rs = ')
            print(t[0])
            yield response.follow(self.start_urls[0], callback=self.test,cb_kwargs=dict(title=t[0]))
            # yield FormRequest.from_response(
            #     response,
            #     formdata={'q': t[0]},
            #     callback = self.post_search,
            #     cb_kwargs = {'title': t[0]})

        # print(test)
        # yield test