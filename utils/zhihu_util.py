#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
from os import path
import requests
import uuid
import paramiko
from MySQLdb import DataError

from config import zhihu_new_latest_url, logging_config, zhihu_new_content_url, mysql_connection_pool, \
    remote_host, remote_user, zhihu_cdn_path, vmiss_us_remote_host, vmiss_us_remote_user
from utils import common_util


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
        self._vmiss_us_key_path = path.join(os.getcwd(), 'key\\VMISSLosAngeles.pem')

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
                # vmiss hk 服务器
                self.update_files_to_ubuntu_server(file, remote_host, remote_user)
                # vmiss us 服务器
                self.update_files_to_vmiss_us_ubuntu_server(file, vmiss_us_remote_host, vmiss_us_remote_user)
                # 删除单个文件
                self.delete_file(file)

    def get_new_latest(self):
        # 获取最新消息
        get_new_content = self._init_common.init_connection(self._init_zhihu_news_latest_url)
        if get_new_content:
            get_stories = get_new_content['stories']
            get_new_latest_list = [{'title': item['title'], 'list_image_url': item['images'][0], 'hint': item['hint'],
                                    'content_url': item['url'], 'id': item['id']} for item in get_stories]
            return get_new_latest_list
        else:
            self._logging.error(f"获取知乎日报 news latest 数据失败。")

    @staticmethod
    def save_image(img_url):
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
        new_img_url = "https://staticx.dev/amusing/z/" + img_name
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
        insert_amusing_article_sql = f"INSERT INTO amusing_articles(TITLE, TOP_IMAGE_URL, TOP_IMAGE_ALT, TOP_IMAGE_TITLE, LIST_SMALL_IMAGE_URL, BODY_HTML, LINK_TEXT, article_info, URL, category_id) VALUE (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        try:
            amusing_article_result = self._mysql.insert_one(sql=insert_amusing_article_sql,
                                                            value=(title, top_img_url, title, title, list_img_url,
                                                                   content, get_link_text, hint, str(uuid.uuid4()), 2))
        except DataError as e:
            self._logging.error(f"插入知乎文章出现错误，具体错误内容：{e}")
            return False
        self._mysql.end()
        if amusing_article_result:
            return True
        else:
            self._logging.error(f"保存知乎日报的内容出现错误，id 为：{content_id}")
            return False

    def update_files_to_ubuntu_server(self, send_file_name, host, user, port=None):
        """
        将单个文件上传到远程服务器
        :param host: 服务器地址
        :param port: 服务器端口，空为默认22
        :param user: 用户名
        :param send_file_name: 图片的文件名
        :return:
        """
        port = int(port) if port else 22
        ssh = paramiko.SSHClient()
        private_key = paramiko.RSAKey.from_private_key_file(self._key_path)
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(pkey=private_key, hostname=host, port=port, username=user)
        sftp = ssh.open_sftp()
        # 本地文件路径
        local_file_path = path.join(os.getcwd(), f'files/{send_file_name}')
        # 远程文件路径
        remote_path = zhihu_cdn_path + send_file_name
        sftp.put(local_file_path, remote_path)
        sftp.close()
        ssh.close()

    def update_files_to_vmiss_us_ubuntu_server(self, send_file_name, host, user, port=None):
        """
        将单个文件上传到 vmiss us 远程服务器
        :param host: 服务器地址
        :param port: 服务器端口，空为默认22
        :param user: 用户名
        :param send_file_name: 图片的文件名
        :return:
        """
        port = int(port) if port else 22
        ssh = paramiko.SSHClient()
        private_key = paramiko.RSAKey.from_private_key_file(self._vmiss_us_key_path)
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(pkey=private_key, hostname=host, port=port, username=user)
        sftp = ssh.open_sftp()
        # 本地文件路径
        local_file_path = path.join(os.getcwd(), f'files/{send_file_name}')
        # 远程文件路径
        remote_path = zhihu_cdn_path + send_file_name
        sftp.put(local_file_path, remote_path)
        sftp.close()
        ssh.close()

    def delete_file(self, file_name):
        # 文件路径
        local_file_path = path.join(os.getcwd(), f'files/{file_name}')
        # 如果文件存在
        if os.path.exists(local_file_path):
            # 删除文件
            os.remove(local_file_path)
        else:
            # 则返回文件不存在
            self._logging.error('no such file:%s' % file_name)
