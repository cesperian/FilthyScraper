# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class BlurbItem(scrapy.Item):
    title = scrapy.Field()
    blurb = scrapy.Field()

class FilthyarchiveItem(scrapy.Item):
    title = scrapy.Field()
    content = scrapy.Field()
    rating = scrapy.Field()
    genres = scrapy.Field()
    year = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    image_names = scrapy.Field()

class DetailsItem(scrapy.Item):
    title = scrapy.Field()
    actors = scrapy.Field()
    directors = scrapy.Field()
    genres = scrapy.Field()
    plot = scrapy.Field()
    mpaa_rating = scrapy.Field()
    duration = scrapy.Field()
    release_date = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    image_names = scrapy.Field()

class PosterImageItem(scrapy.Item):
    image_urls = scrapy.Field()
    images = scrapy.Field()
    image_names = scrapy.Field()