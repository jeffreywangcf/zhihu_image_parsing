# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhihuGirlsItem(scrapy.Item):
    img_url = scrapy.Field()
    belongs_question_url = scrapy.Field()
    author = scrapy.Field()
    text = scrapy.Field()
