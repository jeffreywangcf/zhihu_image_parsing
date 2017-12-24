# -*- coding: utf-8 -*-
import scrapy


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['https://www.zhihu.com']
    start_urls = ['https://www.zhihu.com/collection/146079773?page=1']

    def parse(self, response):
        pass
