# zhihu_image_parsing

我的第三个爬虫项目: Scrapy + MySQL + 倒立验证码识别 爬取知乎上的小姐姐们的照片

crawl project 3: (Scrapy + MySQL + catpcha recognition) -> images from posts

### 更新日志 log

最近发现知乎又双叒叕更新了。。这两天对这个repo模拟登录部分进行更新。

|日期|更新内容|
|:-:|:-:|
|1/30/2018|最新版知乎模拟登录（2018年初）|

|date|update|
|:-:|:-:|
|1/20/2018|up-to-date (2018-) Zhihu logging|

### 写在前面 notice
此爬虫适用于爬取任意知乎收藏夹。可以对[zhihu.py](https://github.com/JeffreyWang2864/zhihu_sexy_girls/blob/master/zhihu_girls/zhihu_girls/spiders/zhihu.py)里的`start_urls`进行修改。

The project is able crawl (almost) any zhihu favorites by simply modifying `start_urls` at [zhihu.py](https://github.com/JeffreyWang2864/zhihu_sexy_girls/blob/master/zhihu_girls/zhihu_girls/spiders/zhihu.py)

### 爬虫流程 procedure
1. 进行登录。获取验证码图片
2. 使用开源项目[者也](https://github.com/muchrooms/zheye)对图片的倒立文字进行识别
3. 上传倒立文字的坐标
4. 在收藏夹的首页获取每个回答的url和下一页的url
5. 对每个回答的文字，图片url，作者名字进行抓取，并将结果存放到`ZhihuGirlsItem`里
6. 根据图片url下载图片，存放在`GirlImages`文件夹中
7. 将本次获取到的结果放到数据库中

<strong></strong>

1. try login to zhihu.com and get captcha image
2. recognize the catpcha image with open source project [zheye](https://github.com/muchrooms/zheye)
3. post coordinates of upside-down Chinese characters to zhihu server
4. parsing the url of next page and urls of each stared answer.
5. gathering author's name, content and image urls from the answer and push them into `ZhihuGirlsItem`
6. download images to directory `GirlImages` base on the "image urls"
7. store data into database

### 利益相关 stakeholders
[Scrapy](https://github.com/scrapy/scrapy)

[python](https://www.python.org/)

[zheye](https://github.com/muchrooms/zheye)

### 演示图片 images
![sql_image](https://github.com/JeffreyWang2864/zhihu_sexy_girls/blob/master/images/sql_image.png)
![girls_image](https://github.com/JeffreyWang2864/zhihu_sexy_girls/blob/master/images/girls_image.png)
