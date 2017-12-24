# -*- coding: utf-8 -*-
import scrapy
import re
import json
import time
import requests
from urllib import request
from PIL import Image
from zheye import zheye
from scrapy.loader import ItemLoader
from zhihu_girls.items import ZhihuGirlsItem

chrome_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14"

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['https://www.zhihu.com']
    start_urls = ['https://www.zhihu.com/collection/146079773?page=1']
    header = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhihu.com",
        "User-Agent": chrome_user_agent
    }

    def parse(self, response):
        all_urls = response.css(".zm-item > div > div > link::attr(href)").extract()
        next_page_selector = response.css(".zm-invite-pager > span:last-child > a::attr(href)")
        for question_url in list(map(lambda x: request.urljoin("https://www.zhihu.com/", x), all_urls)):
            yield scrapy.Request(question_url, callback=self.parse_detail, headers=self.header)
        if next_page_selector:
            next_url = request.urljoin(self.start_urls[0], next_page_selector.extract()[0])
            yield scrapy.Request(next_url, callback=self.parse, headers=self.header, dont_filter=True)

    def parse_detail(self, response):
        item_loader = ZhihuGirlsItem()
        text = "".join(response.css(".RichContent--unescapable > div > span::text").extract())
        pictures = response.css(".RichContent--unescapable > div:nth-child(1) > span:nth-child(1) > figure > noscript > img::attr(src)").extract()
        author_name = response.css(".ContentItem-meta > div > meta:nth-child(1)::attr(content)").extract()[0]
        question_url = response._url
        item_loader['img_url'] = pictures
        item_loader['belongs_question_url'] = question_url
        item_loader['author'] = author_name
        item_loader['text'] = text
        yield item_loader

    def start_requests(self):
        login_url = "https://www.zhihu.com/#signin"
        return [scrapy.Request(login_url, callback=self.login, headers=self.header)]

    def get_xsrf(self, session):
        index_url = 'https://www.zhihu.com'
        index_page = session.get(index_url, headers=self.header)
        html = index_page.text
        pattern = r'name="_xsrf" value="(.*?)"'
        _xsrf = re.findall(pattern, html)
        return _xsrf[0]

    def login(self, response):
        response_text = response.text
        match_obj = re.match('.*name="_xsrf" value="(.*?)"', response_text, re.DOTALL)
        if match_obj:
            session = requests.session()
            xsrf_text = self.get_xsrf(session)
            post_url = "https://www.zhihu.com/login/phone_num"
            with open("/Users/Excited/zhihuaccount.txt", "r") as file:
                lines = file.readlines()
            post_data = {
                "_xsrf": xsrf_text,
                "phone_num": lines[0].rstrip(),
                "password": lines[1].rstrip(),
                "captcha": ""
            }
            label = str(int(time.time() * 1000))
            image_captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login".format(label)
            text_captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login&lang=cn".format(label)
            captcha_version = "text"
            valid_captcha_version = ("image", "text")
            assert captcha_version in valid_captcha_version
            if captcha_version == valid_captcha_version[0]:
                yield scrapy.Request(image_captcha_url, headers=self.header,
                                     callback=self.image_captcha_handling, meta={"post_data": post_data, "post_url": post_url})
            else:
                yield scrapy.Request(text_captcha_url , headers=self.header,
                                     callback=self.text_captcha_handling, meta={"post_data": post_data, "post_url": post_url})
            return [scrapy.FormRequest(
                url=post_url,
                formdata=post_data,
                headers=self.header,
                callback=self.check_login
            )]
        raise ValueError("xsrf value not found")

    def check_login(self, response):
        text_json = json.loads(response.text)
        if "msg" in text_json and text_json["msg"] == "登录成功":
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.header)
            return
        raise AttributeError("login failed")

    def image_captcha_handling(self, response):
        with open("login_captcha.gif", "wb") as file:
            file.write(response.body)
            file.close()
        image = Image.open("login_captcha.gif")
        image.show()
        image.close()
        key_for_captcha = input("输入验证码\n>")
        post_data = response.meta.get("post_data", {})
        post_data["captcha"] = key_for_captcha
        post_url = response.meta.get("post_url", {})
        return [scrapy.FormRequest(
            url=post_url,
            formdata=post_data,
            headers=self.header,
            callback=self.check_login
        )]

    def text_captcha_handling(self, response):
        img_path = "login_captcha.gif"
        with open(img_path, "wb") as file:
            file.write(response.body)
            file.close()
        z = zheye()
        positions = z.Recognize(img_path)
        coords = list()
        if len(positions) == 2:
            if positions[0][1] > positions[1][1]:
                coords.append([positions[1][1], int(positions[1][0])])
                coords.append([positions[0][1], int(positions[0][0])])
            else:
                coords.append([positions[0][1], positions[0][0]])
                coords.append([positions[1][1], positions[1][0]])
            key_for_captcha = '{"img_size": [200, 44], "input_points": [[ % .2f, %.f], [%  .2f, %.f]]}' % (
                coords[0][0] / 2, coords[0][1] / 2,
                coords[1][0] / 2, coords[1][1] / 2
            )
        else:
            coords.append([positions[0][1], positions[0][0]])
            key_for_captcha = '{"img_size": [200, 44], "input_points": [[ % .2f, %.f]]}' % (
                coords[0][0] / 2, coords[0][1] / 2,
            )
        post_data = response.meta.get("post_data", "")
        post_url = response.meta.get("post_url", "")
        post_data['captcha'] = key_for_captcha
        post_data['captcha_type'] = "cn"
        return [scrapy.FormRequest(
            url=post_url,
            formdata=post_data,
            headers=self.header,
            callback=self.check_login
        )]