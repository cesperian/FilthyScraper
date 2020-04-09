# -*- coding: utf-8 -*-
import scrapy
import sqlite3
from scrapy.pipelines.images import ImagesPipeline

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class FilthyarchivePipeline(object):

    def __init__(self):
        self.createConn()
        self.createTable()

    def createConn(self):
        self.conn = sqlite3.connect('filthy_archive.db')
        self.cursor = self.conn.cursor()

    def createTable(self):
        self.cursor.execute("""drop table if exists reviews""")
        self.cursor.execute("""
            create table reviews(
                title text,
                content text,
                year integer,
                rating integer,
                genre text,
                imagenames text
            )
        """)

    def process_item(self, item, spider):
        self.cursor.execute(
            """insert into reviews values (?,?,?,?,?,?)""",
            (
                item['title'],
                item['content'],
                item['year'],
                item['rating'],
                item['genre'],
                item['image_names']
            )
        )
        self.conn.commit()
        return item



class ImageNamePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        return [scrapy.Request(x, meta={'image_name': x.split('/')[-1]})
                for x in item.get('image_urls', [])]

    def file_path(self, request, response=None, info=None):
        return request.meta['image_name']