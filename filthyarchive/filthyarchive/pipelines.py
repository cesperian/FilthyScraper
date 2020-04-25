# -*- coding: utf-8 -*-
import scrapy
import sqlite3
from scrapy.pipelines.images import ImagesPipeline

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


class ClearAssocPipeline(object):

    def __init__(self):
        self.createConn()

    def createConn(self):
        self.conn = sqlite3.connect('filthy_archive.db')
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        if bool(item['plot']): # otherwise this will try to process PosterImageItem items also
            self.cursor.execute(
                """
                    delete from movie_genres where movie_id = (
                        SELECT rowid FROM reviews where title = ?
                    )
                """,
                (
                    item['title'],
                )
            )
            self.cursor.execute(
                """
                    delete from movie_directors where movie_id = (
                        SELECT rowid FROM reviews where title = ?
                    )
                """,
                (
                    item['title'],
                )
            )
            self.cursor.execute(
                """
                    delete from movie_actors where movie_id = (
                        SELECT rowid FROM reviews where title = ?
                    )
                """,
                (
                    item['title'],
                )
            )

            self.conn.commit()
            # self.conn.close()
            return item


class DetailsPipeline(object):

    def __init__(self):
        self.createConn()

    def createConn(self):
        self.conn = sqlite3.connect('filthy_archive.db')
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        # add actors...
        for actor in item['actors']:
            self.cursor.execute(
                """
                    insert into actors(actor)
                    select ?
                    where not exists(
                        select 1 from actors where actor = ?
                    );
                """,
                (
                    actor,
                    actor
                )
            )
            self.cursor.execute(
                """
                    insert into movie_actors values(
                        (select rowid from reviews WHERE title = ?),
                        (select rowid from actors WHERE actor = ?)
                    );
                """,
                (
                    item['title'],
                    actor
                )
            )
        # end actors for:
        for d in item['directors']:
            self.cursor.execute(
                """
                    insert into directors(director)
                    select ?
                    where not exists(
                        select 1 from directors where director = ?
                    );
                """,
                (
                    d,
                    d
                )
            )
            self.cursor.execute(
                """
                    insert into movie_directors values(
                        (select rowid from reviews WHERE title = ?),
                        (select rowid from directors WHERE director = ?)
                    );
                """,
                (
                    item['title'],
                    d
                )
            )
        # end directors for:
        for g in item['genres']:
            self.cursor.execute(
                """
                    insert into genres(genre)
                    select ?
                    where not exists(
                        select 1 from genres where genre = ?
                    );
                """,
                (
                    g,
                    g
                )
            )
            self.cursor.execute(
                """
                    insert into movie_genres values(
                        (select rowid from reviews WHERE title = ?),
                        (select rowid from genres WHERE genre = ?)
                    );
                """,
                (
                    item['title'],
                    g
                )
            )
        # end genres for:

        # update reviews w imdb details...
        self.cursor.execute(
            """
                update reviews set
                    plot = ?,
                    mpaa_rating = ?,
                    duration = ?,
                    release_date = ?
                WHERE title = ?;
            """,
            (
                item['plot'],
                item['mpaa_rating'],
                item['duration'],
                item['release_date'],
                item['title']
            )
        )

        self.conn.commit()
        # self.conn.close()
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
