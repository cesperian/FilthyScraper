# -*- coding: utf-8 -*-
import scrapy
import sqlite3
from scrapy.pipelines.images import ImagesPipeline

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

class BlurbPipeline(object):

    def __init__(self):
        self.createConn()

    def createConn(self):
        self.conn = sqlite3.connect('filthy_archive.db')
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        self.cursor.execute(
            """update reviews set blurb = ? where title = ?""",
            (
                item['blurb'],
                item['title']
            )
        )
        self.conn.commit()
        self.conn.close()
        return item

class FilthyarchivePipeline(object):

    def __init__(self):
        self.createConn()
        self.createTable()

    def createConn(self):
        self.conn = sqlite3.connect('filthy_archive.db')
        self.cursor = self.conn.cursor()

    def createTable(self):
        self.cursor.execute("""drop table if exists reviews""")
        self.cursor.execute("""drop table if exists genres""")
        self.cursor.execute("""drop table if exists images""")
        self.cursor.execute("""
            create table reviews(
                title text,
                blurb text,
                content text,
                year integer,
                rating integer,
                imagenames,
                genres
            )
        """)
        # revisit this if setting up table rels..
        # self.cursor.execute("""
        #     create table genres(
        #         genre text
        #     )
        # """)
        # self.cursor.execute("""
        #     create table images(
        #         filename text
        #     )
        # """)

    def process_item(self, item, spider):
        self.cursor.execute(
            """insert into reviews values (?,?,?,?,?,?,?)""",
            (
                item['title'],
                None,
                item['content'],
                item['year'],
                item['rating'],
                ','.join(item['image_names']),
                ','.join(item['genres'])
            )
        )
        # revisit this if setting up table rels..
        # for g in item['genres']:
        #     self.cursor.execute(
        #         """insert into genres values (?)""", (g,)
        #     )
        #
        # if item['image_names']:
        #     for i in item['image_names']:
        #         self.cursor.execute(
        #             """insert into images values (?)""", (i,)
        #         )

        self.conn.commit()
        self.conn.close()
        return item



class ImageNamePipeline(ImagesPipeline):
    # 'image_name' per-image meta information different from 'image_names' item prop...
    def get_media_requests(self, item, info):
        # return [scrapy.Request(x, meta={'image_name': x.split('/')[-1]})
        #         for x in item.get('image_urls', [])]
        return [scrapy.Request(url, meta={'image_name': name})
                for url, name in zip(item.get('image_urls', []), item.get('image_names', []))]

    def file_path(self, request, response=None, info=None):
        return request.meta['image_name']
