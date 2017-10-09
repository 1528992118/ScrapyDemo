#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
 京东手机数据抓取分析
'''

__author__ = 'Xiaolong Cao'

import re
import json
import copy
import time
import scrapy
import numpy as np
import pandas as pd
# 导入图表库以进行图表绘制
import matplotlib.pyplot as plt
from JDPhone.phoneItems import phoneItem


class MySpider(scrapy.Spider):
    name = "jd-phone"

    start_urls = []

    for page in range(1, 5):
        start_urls.append("https://list.jd.com/list.html?cat=9987,653,655&page=" + str(page))

    def parse(self, response):
        for good in response.xpath(u'//li[@class="gl-item"]'):
            item = phoneItem()
            item['p_id'] = good.xpath(u'.//@data-sku').extract_first()
            item['p_name'] = re.sub(r'\s+', '', good.xpath(u'.//div[@class="p-name"]/a/em/text()').extract_first())
            item['p_shop'] = good.xpath(u'.//div[@class="p-shop"]/@data-shop_name').extract_first()
            item['p_link'] = good.xpath(u'.//div[@class="p-img"]/a[@target="_blank"]/@href').extract_first()
            item['p_image_url'] = 'http:' + str(
                good.xpath(u'.//div[@class="p-img"]/a[@target="_blank"]/img/@src').extract_first())
            if item['p_image_url'] is None:
                item['p_image_url'] = 'http:' + str(
                    good.xpath(u'.//div[@class="p-img"]/a[@target="_blank"]/img/@data-lazy-img').extract_first())
            pduid = time.time()
            p_price_url = 'https://p.3.cn/prices/mgets?pduid=' + str(pduid) + '&skuIds=J_' + item['p_id']
            yield scrapy.Request(p_price_url, meta={'item': item}, callback=self.parse_price, dont_filter=True)

    def parse_price(self, response):
        item = response.meta['item']
        data = json.loads(response.body_as_unicode())
        if data is not None and isinstance(data, list):
            for item_data in data:
                item['p_price'] = item_data.get('p', "")
        else:
            item['p_price'] = None
        p_comment_url = u"https://club.jd.com/comment/productCommentSummaries.action?my=pinglun&referenceIds=" + item[
            'p_id']
        yield scrapy.Request(p_comment_url, meta={'item': item}, callback=self.parse_comment, dont_filter=True)

    def parse_comment(self, response):
        item = response.meta['item']
        data = json.loads(response.body_as_unicode())
        if data is not None and data['CommentsCount'] is not None:
            comment_data = data['CommentsCount']
            for item_data in comment_data:
                if item_data['GoodRateShow'] is not None:
                    item['p_good_rate'] = item_data['GoodRateShow']
                else:
                    item['p_good_rate'] = None
                if item_data['CommentCountStr'] is not None:
                    p_comment_num = str(item_data['CommentCountStr'])
                    if p_comment_num.find('+') > 0:
                        p_comment_num = p_comment_num.strip().strip('+')
                        if p_comment_num.find(u'万') > 0:
                            p_comment_num = p_comment_num.strip().strip(u'万')
                            p_comment_num = float(p_comment_num) * 10000
                            item['p_comment_num'] = p_comment_num
                            # 销售量估计
                            item['p_sales'] = str(p_comment_num * 10 / 1000) + 'k'
                        else:
                            item['p_comment_num'] = p_comment_num
                            item['p_sales'] = str(int(float(p_comment_num) * 10 / 1000)) + 'k'
                    else:
                        item['p_comment_num'] = p_comment_num
                        # 销售量估计
                        item['p_sales'] = str(int(float(p_comment_num) * 10 / 1000)) + 'k'
                else:
                    item['p_comment_num'] = None
                    item['p_sales'] = None
        else:
            item['p_comment_num'] = None
            item['p_good_rate'] = None
            item['p_sales'] = None
        return item

    def close(spider, reason):
        shop_list = spider.phone_occur_times_table_list()
        shop_list_copy = copy.deepcopy(shop_list)
        # 不排序
        # dic = {'手机品牌': shop_list.keys(), '出现次数': shop_list.values()}
        # 按出现次数降序排序
        (phone_brands, occurrence_times) = spider.order_phone_occurrence_times(shop_list)
        dic_1 = {'手机品牌': phone_brands, '出现次数': occurrence_times}
        df = pd.DataFrame(dic_1)
        print df
        # 综合排序下出现手机次数图表
        # spider.generate_phone_occur_times_table(df)
        spider.Histogram(df)
        for k,v in shop_list_copy.items():
            shop_list_copy[k] = v[1]
        dic_2= {'手机品牌': shop_list_copy.keys(), '好评率': shop_list_copy.values()}
        df = pd.DataFrame(dic_2)
        spider.line_chart(df)



    def order_phone_occurrence_times(self, shop_list):
        if isinstance(shop_list, dict):
            for k,v in shop_list.items():
                shop_list[k]=v[0]
            shop_list = sorted(shop_list.iteritems(), key=lambda d: d[1], reverse=True)
            phone_brands = []
            occurrence_times = []
            for item in shop_list:
                phone_brands.append(item[0])
                occurrence_times.append(item[1])
        else:
            ([], [])
        return (phone_brands, occurrence_times)

    # 折线图
    def line_chart(self, df):
        occur_times = df['好评率']
        # 图表字体为华文细黑，字号为15
        plt.rc('font', family='Microsoft YaHei', size=15)
        # 创建一个一维数组赋值给a
        a = np.arange(12)
        # 创建折线图，数据源为不同品牌手机出现次数，标记点，标记线样式，线条宽度，标记点颜色和透明度
        plt.plot(occur_times, 'g^', occur_times, 'g-', color='#99CC01', linewidth=3, markeredgewidth=3,
                 markeredgecolor='#99CC01', alpha=0.8)
        # 添加x轴标签
        plt.xlabel(u'手机品牌')
        # 添加y周标签
        plt.ylabel(u'好评率')
        # 添加图表标题
        plt.title(u'JD手机综合排序')
        # 添加图表网格线，设置网格线颜色，线形，宽度和透明度
        plt.grid(color='#95a5a6', linestyle='--', linewidth=1, axis='y', alpha=0.4)
        # 设置数据分类名称
        plt.xticks(a, (df['手机品牌']))
        # 输出图表
        plt.show()

    # 柱状图
    def Histogram(self, df):
        occur_times = df['出现次数']
        # 图表字体为华文细黑，字号为15
        plt.rc('font', family='Microsoft YaHei', size=15)
        # 创建一个一维数组赋值给a
        a = np.arange(12)
        # 创建柱状图，数据源为按用户等级汇总的贷款金额，设置颜色，透明度和外边框颜色
        plt.bar(a, occur_times, color='#99CC01', alpha=0.8, align='center', edgecolor='white')
        plt.xlabel(u'手机品牌')
        # 添加y周标签
        plt.ylabel(u'出现次数')
        # 添加图表标题
        plt.title(u'JD手机综合排序')
        # 设置图例的文字和在图表中的位置
        plt.legend(['出现次数'], loc='upper right')
        # 设置背景网格线的颜色，样式，尺寸和透明度
        plt.grid(color='#95a5a6', linestyle='--', linewidth=1, axis='y', alpha=0.4)
        # 设置数据分类名称
        plt.xticks(a, (df['手机品牌']))
        # 显示图表
        plt.show()

    def phone_occur_times_table_list(self):
        default_num = 0
        shop_list = {'小米': [default_num,default_num], '华为': [default_num,default_num], '乐视': [default_num,default_num], 'OPPOR': [default_num,default_num], 'VIVO': [default_num,default_num],
                     '魅族': [default_num,default_num],
                     'Apple': [default_num,default_num], '三星': [default_num,default_num], '锤子': [default_num,default_num], '一加': [default_num,default_num], '诺基亚': [default_num,default_num],
                     '其他': [default_num,default_num]}
        with open('E:/PycharmWorkSpace/Scrapy/JDPhone/data.json', 'r') as data_str:
            for line in data_str.readlines():
                data_obj = json.loads(line)
                brand = data_obj['p_name']
                if brand.find(u'小米') >= 0:
                    shop_list['小米'] [0]= shop_list['小米'] [0] + 1
                    shop_list['小米'][1] = shop_list['小米'][1] + data_obj['p_good_rate']
                elif brand.find(u'华为') >= 0 or brand.find(u'荣耀') >= 0:
                    shop_list['华为'] [0]= shop_list['华为'][0] + 1
                    shop_list['华为'][1] = shop_list['华为'][1] + data_obj['p_good_rate']
                elif brand.find(u'乐视') >= 0:
                    shop_list['乐视'] [0]= shop_list['乐视'][0] + 1
                    shop_list['乐视'][1] = shop_list['乐视'][1] + data_obj['p_good_rate']
                elif brand.find(u'OPPOR') >= 0:
                    shop_list['OPPOR'] [0]= shop_list['OPPOR'][0] + 1
                    shop_list['OPPOR'][1] = shop_list['OPPOR'][1] + data_obj['p_good_rate']
                elif brand.find(u'VIVO') >= 0 or brand.find(u'vivo') >= 0:
                    shop_list['VIVO'] [0]= shop_list['VIVO'][0] + 1
                    shop_list['VIVO'][1] = shop_list['VIVO'][1] + data_obj['p_good_rate']
                elif brand.find(u'魅族') >= 0:
                    shop_list['魅族'] [0]= shop_list['魅族'][0] + 1
                    shop_list['魅族'][1] = shop_list['魅族'][1] + data_obj['p_good_rate']
                elif brand.find(u'Apple') >= 0:
                    shop_list['Apple'] [0]= shop_list['Apple'][0] + 1
                    shop_list['Apple'][1] = shop_list['Apple'][1] + data_obj['p_good_rate']
                elif brand.find(u'三星') >= 0:
                    shop_list['三星'] [0]= shop_list['三星'][0] + 1
                    shop_list['三星'][1] = shop_list['三星'][1] + data_obj['p_good_rate']
                elif brand.find(u'锤子') >= 0:
                    shop_list['锤子'] [0]= shop_list['锤子'][0] + 1
                    shop_list['锤子'][1] = shop_list['锤子'][1] + data_obj['p_good_rate']
                elif brand.find(u'一加') >= 0:
                    shop_list['一加'] [0]= shop_list['一加'] [0]+ 1
                    shop_list['一加'][1] = shop_list['一加'][1] + data_obj['p_good_rate']
                elif brand.find(u'诺基亚') >= 0:
                    shop_list['诺基亚'] [0]= shop_list['诺基亚'][0] + 1
                    shop_list['诺基亚'][1] = shop_list['诺基亚'][1] + data_obj['p_good_rate']
                else:
                    shop_list['其他'] [0]= shop_list['其他'][0] + 1
                    shop_list['其他'][1] = shop_list['其他'][1] + data_obj['p_good_rate']
        for k, v in shop_list.items():
            if v[0] is not 0:
                avg_good_rate = v[1]/v[0]
                shop_list[k]=(v[0],avg_good_rate)
        return shop_list





