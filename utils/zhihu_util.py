#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
from datetime import datetime
from os import path
import requests
import uuid
from MySQLdb import DataError

from config import zhihu_new_latest_url, logging_config, zhihu_new_content_url, mysql_connection_pool, zhihu_cdn_path
from utils import common_util, images_util


class ZhiHuUtil(object):
    # 通过知乎 API 获取知乎日报文章，具体文档可以参考这里：https://github.com/nonoroazoro/Zhihu-Daily-Reader/blob/master/Zhihu-Daily-API.md
    def __init__(self):
        # 最新消息访问页面地址
        self._init_zhihu_news_latest_url = zhihu_new_latest_url
        logger_name = 'zhihu_daily'
        init_logging = logging_config.LoggingConfig()
        self._logging = init_logging.init_logging(logger_name)

        self._mysql = mysql_connection_pool.Mysql()
        self._init_common = common_util.CommonUtil()
        self._key_path = path.join(os.getcwd(), 'key\\wmiss_hk.pem')
        self._upload_image = images_util.ImagesUtil()
        # 获取当前的年月
        self._now = datetime.now()

    def zhihu_main(self):
        get_title_data = self.get_new_latest()
        if get_title_data:
            for item in get_title_data:
                title = item['title']
                list_img_url = item['list_image_url']
                get_list_img_url = self.save_image(list_img_url)
                get_id = item['id']
                get_hint = item['hint']
                get_content = self.get_zhihu_content(get_id)
                get_top_img = self.save_image(get_content['image'])
                content_body = get_content['body']
                self.save_zhihu_story(item['id'], title, get_list_img_url, get_top_img, get_hint, content_body)
            # 循环 files 文件夹下面的所有文件
            local_file_path = path.join(os.getcwd(), 'files')
            get_local_files = self._init_common.findAllFile(local_file_path)
            for file in get_local_files:
                # 上传单个文件到服务器
                remote_file_path = f'{zhihu_cdn_path}{self._now.year}/{self._now.month}'
                self._upload_image.update_image_main(local_file_name=file, remote_file_path=remote_file_path)
                # 删除单个文件
                delete_image = images_util.DeleteFileUtil()
                delete_image.delete_file(file)

    def get_new_latest(self):
        # 获取最新消息
        get_new_content = self._init_common.init_connection(self._init_zhihu_news_latest_url)
        if get_new_content:
            temp_list = []
            get_stories = get_new_content['stories']
            for item in get_stories:
                try:
                    images = item['images'][0]
                except KeyError:
                    images = 'https://staticx.dev/amusing/z/v2-23eb79a8d040db7ac15b2ac51dcee1fa.jpg'
                temp_list.append({'title': item['title'], 'list_image_url': images, 'hint': item['hint'],
                                  'content_url': item['url'], 'id': item['id']})
            return temp_list
        else:
            self._logging.error(f"获取知乎日报 news latest 数据失败。")

    def save_image(self, img_url):
        # 连接目标网站，获取内容，获取图片内容
        # img_url: https://pic1.zhimg.com/v2-1737233d284dea9e61db500f35da0451.jpg?source=8673f162
        img_content = requests.get(img_url)
        # 设置文件保存相对路径
        get_img_name = img_url.split('/')[3]
        img_name = get_img_name.split('?')[0]
        real_path = 'files/' + img_name
        # 文件保存绝对路径
        img_file_path = path.join(os.getcwd(), real_path)
        with open(img_file_path, 'wb') as f:
            # 写文件
            f.write(img_content.content)
        new_img_url = f"https://staticx.dev/amusing/z/{self._now.year}/{self._now.month}/" + img_name
        return new_img_url

    def get_zhihu_content(self, content_id):
        # url: https://news-at.zhihu.com/api/4/news/9747259
        get_content_url = zhihu_new_content_url + str(content_id)
        get_content = self._init_common.init_connection(get_content_url)
        if get_content:
            return get_content
        else:
            self._logging.error(f"获取知乎日报内容出现错误，知乎日报内容 id: {content_id}")
            return False

    def save_zhihu_story(self, content_id, title, list_img_url, top_img_url, hint, content):
        """
        将获取到的知乎日报内容保存到数据库
        :param content_id: 知乎日报文章 id
        :param title: 文章 title
        :param list_img_url: 列表小图 url
        :param top_img_url: 顶部大图 url
        :param hint: 文章作者及阅读时间
        :param content: 文章内容
        :return: 保存成功 True, 未保存成功 False，并记录日志
        """
        get_link_text = str(uuid.uuid4())
        insert_amusing_article_sql = f"INSERT INTO amusing_articles(TITLE, TOP_IMAGE_URL, TOP_IMAGE_ALT, TOP_IMAGE_TITLE, LIST_SMALL_IMAGE_URL, BODY_HTML, LINK_TEXT, article_info, URL, category_id, FORMAT_ID) VALUE (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        try:
            amusing_article_result = self._mysql.insert_one(sql=insert_amusing_article_sql,
                                                            value=(title, top_img_url, title, title, list_img_url,
                                                                   content, get_link_text, hint, str(uuid.uuid4()), 2,
                                                                   1))
        except DataError as e:
            self._logging.error(f"插入知乎文章出现错误，具体错误内容：{e}")
            return False
        self._mysql.end()
        if amusing_article_result:
            return True
        else:
            self._logging.error(f"保存知乎日报的内容出现错误，id 为：{content_id}")
            return False
