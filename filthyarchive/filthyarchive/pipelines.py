# -*- coding: utf-8 -*-
import scrapy
from scrapy.pipelines.images import ImagesPipeline

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class FilthyarchivePipeline(object):
    def process_item(self, item, spider):
        return item

class ImageNamePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        return [scrapy.Request(x, meta={'image_name': x.split('/')[-1]})
                for x in item.get('image_urls', [])]

    def file_path(self, request, response=None, info=None):
        return request.meta['image_name']