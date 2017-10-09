#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Xiaolong Cao'


import scrapy

class phoneItem(scrapy.Item):
    #手机ID
    p_id=scrapy.Field()
    #手机名称
    p_name=scrapy.Field()
    #手机价格
    p_price=scrapy.Field()
    #手机评论数
    p_comment_num=scrapy.Field()
    #手机销售方
    p_shop=scrapy.Field()
    #手机链接
    p_link=scrapy.Field()
    #手机图片地址
    p_image_url=scrapy.Field()
    #销量估算
    p_sales=scrapy.Field()
    #好评率
    p_good_rate=scrapy.Field()


