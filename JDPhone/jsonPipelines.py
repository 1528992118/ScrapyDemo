#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Xiaolong Cao'

import json
#解决'ascii' codec can't encode character
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class JsonPipeline(object):
    def __init__(self):
        #打开文件
        self.file = open('data.json', 'w')
    #该方法用于处理数据
    def process_item(self, item, spider):
        #读取item中的数据
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        #写入文件
        self.file.write(line)
        #返回item
        return item
    #该方法在spider被开启时被调用。
    def open_spider(self, spider):
        pass

    # 该方法在spider被关闭时被调用。
    def close_spider(self, spider):
        self.file.close()
        print 'data.json closed'
