#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
 抓取数据存入MySql数据库
'''


import db
import time
import json
import settings
from db import Dict
from scrapy import log


__author__ = 'Xiaolong Cao'


def toDict(d):
    D = Dict()
    for k, v in d.iteritems():
        D[k] = toDict(v) if isinstance(v, dict) else v
    return D

configs = toDict(settings.CONFIGS)

class mysqlPipeline(object):
    def __init__(self):
        db.create_engine(**configs.db)

    def process_item(self, item, spider):
        p_id = item['p_id']
        count=db.select_int('select count(*) from jd_phone where p_id=?', str(p_id))
        if  count is not None and int(count) > 0:
            db.update('update jd_phone set p_name = ?,p_price = ? ,p_comment_num = ? ,p_shop = ? ,p_link = ?,p_image_url = ?,p_sales = ?,p_good_rate = ?,p_msg_create_time = ? where p_id= ?'
                      ,str(item['p_name'])
                      ,str(item['p_price'])
                      ,str(item['p_comment_num'])
                      ,str(item['p_shop'])
                      ,str(item['p_link'])
                      ,str(item['p_image_url'])
                      ,str(item['p_sales'])
                      ,str(item['p_good_rate'])
                      ,self.now_time()
                      ,str(item['p_id']))
        else:
            u1=dict( p_id = str(item['p_id'])
                    ,p_name =  str(item['p_name'])
                    ,p_price =  str(item['p_price'])
                    ,p_comment_num =  str(item['p_comment_num'])
                    ,p_shop =  str(item['p_shop'])
                    ,p_link =  str(item['p_link'])
                    ,p_image_url =  str(item['p_image_url'])
                    ,p_sales= str(item['p_sales'])
                    ,p_good_rate =  str(item['p_good_rate'])
                    ,p_msg_create_time=self.now_time())
            db.insert('jd_phone',**u1)
        return item

    def _handle_error(self, e):
        log.err(e)

    def now_time(self):
        return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))



