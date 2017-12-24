# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from twisted.enterprise import adbapi
import MySQLdb
from MySQLdb import cursors

class ScrapyDemoPipeline(object):
    def process_item(self, item, spider):
        return item

class MysqlTwistedPipline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        db_name = settings['MYSQL_DBNAME']
        charset = settings['MYSQL_CHARSET']
        with open("/Users/Excited/localmysqlrootssh.txt") as file:
            lines = file.readlines()    #host, user, passwd, port
            #port = int(lines[3])
            param_dict = dict(
                host = lines[0].rstrip(),
                db = db_name,
                user = lines[1].rstrip(),
                passwd = lines[2].rstrip(),
                charset = charset,
                cursorclass = MySQLdb.cursors.DictCursor,
                use_unicode = True
            )
        dbpool = adbapi.ConnectionPool('MySQLdb', **param_dict)
        return cls(dbpool)

    def do_insert(self, cursor, item):
        insert_sql = """
            insert into `zhihu_girls`(`name`, `text`, `question_url`, `images_url`) value (%s, %s, %s, %s);
        """
        cursor.execute(insert_sql, (item['author'],
                                    item['text'],
                                    item['belongs_question_url'],
                                    "\t".join(item['img_url'])))

    def insert_error_handling(self, failure, item, spider):
        print(failure)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.insert_error_handling, item, spider)