import re
import json
import datetime

try:
    import urlparse as parse
except:
    from urllib import parse
import os

import scrapy
from scrapy.loader import ItemLoader

class ZhihuSpider(scrapy.Spider):
    name = "demo"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['https://www.zhihu.com/']

    #question的第一页answer的请求url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccollapsed_counts%2Creviewing_comments_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Crelationship.is_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.author.is_blocking%2Cis_blocked%2Cis_followed%2Cvoteup_count%2Cmessage_thread_token%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}"

    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhizhu.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
    }

    # custom_settings = {
    #     'COOKIES_ENABLED': True,
    # }

    def parse(self, response):
        """
        提取出html页面中的所有url 并跟踪这些url进行一步爬取
        如果提取的url中格式为 /question/xxx 就下载之后直接进入解析函数
        """


    def start_requests(self):
        return [scrapy.Request('https://www.zhihu.com/#signin', headers=self.headers, callback=self.login)]

    def get_xsrf(self, session):
        '''_xsrf 是一个动态变化的参数'''
        index_url = 'https://www.zhihu.com'
        # 获取登录时需要用到的_xsrf
        index_page = session.get(index_url, headers=self.headers)
        html = index_page.text
        pattern = r'name="_xsrf" value="(.*?)"'
        # 这里的_xsrf 返回的是一个list
        _xsrf = re.findall(pattern, html)
        return _xsrf[0]

    # 获取验证码
    def get_captcha(self, session):
        import time
        import requests
        try:
            from PIL import Image
        except:
            pass
        t = str(int(time.time() * 1000))
        captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
        r = session.get(captcha_url, headers=self.headers)
        with open('captcha.jpg', 'wb') as f:
            f.write(r.content)
            f.close()
        # 用pillow 的 Image 显示验证码
        # 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入
        try:
            im = Image.open('captcha.jpg')
            im.show()
            im.close()
        except:
            print(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
        captcha = input("please input the captcha\n>")
        return captcha

    def login(self, response):
        response_text = response.text
        match_obj = re.match('.*name="_xsrf" value="(.*?)"', response_text, re.DOTALL)
        xsrf = ''
        if match_obj:
            xsrf = (match_obj.group(1))
        import requests
        session = requests.session()
        if xsrf:
            post_url = "https://www.zhihu.com/login/phone_num"
            post_data = {
                "_xsrf": self.get_xsrf(session),
                "phone_num": "13811443775",
                "password": "001127",
                "captcha": ""
            }
            import time
            t = str(int(time.time() * 1000))
            captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + "&type=login&lang=cn"
            yield scrapy.Request(captcha_url, headers=self.headers, meta={"post_data":post_data}, callback=self.get_captcha_login)
            return [scrapy.FormRequest(
                url = post_url,
                formdata = post_data,
                headers=self.headers,
                callback=self.check_login
            )]

    def get_captcha_login(self, response):
        post_data = response.meta.get("post_data", "")
        try:
            from PIL import Image
        except:
            pass
        with open('captcha.gif', 'wb') as f:
            f.write(response.body)
            f.close()
        # 用pillow 的 Image 显示验证码
        # 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入

        from zheye import zheye
        z = zheye()
        positions = z.Recognize('captcha.gif')

        position_arr = []
        if len(positions)==2:
            if positions[1][1] < positions[0][1]:
                position_arr.append([positions[1][1], int(positions[1][0])])
                position_arr.append([positions[0][1], int(positions[0][0])])
            else:
                position_arr.append([positions[0][1], positions[0][0]])
                position_arr.append([positions[1][1], positions[1][0]])
        else:
            position_arr.append([positions[0][1], positions[0][0]])

        print(positions)

        if len(positions) == 2:
            post_data["captcha"] = '{"img_size": [200, 44], "input_points": [[%.2f, %.f], [%.2f, %.f]]}' % (
                position_arr[0][0] / 2, position_arr[0][1] / 2, position_arr[1][0] / 2, position_arr[1][1] / 2)
        else:
            post_data["captcha"] = '{"img_size": [200, 44], "input_points": [[%.2f, %.f]]}' % (
                position_arr[0][0] / 2, position_arr[0][1] / 2)
        post_data['captcha_type'] = "cn"
        print (post_data)
        return [scrapy.FormRequest(
            url = "https://www.zhihu.com/login/phone_num",
            formdata = post_data,
            headers=self.headers,
            callback=self.check_login
        )]

    def check_login(self, response):
        #验证服务器的返回数据判断是否成功
        text_json = json.loads(response.text)
        if "msg" in text_json and text_json["msg"] == "登录成功":
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers)