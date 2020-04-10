# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FilthyarchiveItem(scrapy.Item):
    title = scrapy.Field()
    content = scrapy.Field()
    rating = scrapy.Field()
    genres = scrapy.Field()
    year = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    image_names = scrapy.Field()
