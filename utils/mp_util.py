#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os.path
import uuid
import html2text
from MySQLdb import DataError
from datetime import datetime

from config import logging_config, mysql_connection_pool
from utils import connection_util, proxy_util


class MPUtil(object):
    def __init__(self):
        # 要访问的目标URL
        self._url = 'https://mp.weixin.qq.com/s?__biz=Mzg4MDA3MTMzMw==&mid=2247484778&idx=1&sn=8a97c65b24038e4e661c7ffa7ceeb9be&chksm=cf7b82a0f80c0bb66d63687711b820fd3aa26c822d5076eda51f33f2a9aaa2c04049abbf52e7&scene=132#wechat_redirect'
        self._connection = connection_util.ProcessConnection()
        self._proxy = proxy_util.ProxyUtil()
        self._path = os.path.join(os.getcwd(), 'files')
        logger_name = 'mp'
        init_logging = logging_config.LoggingConfig()
        self._logging = init_logging.init_logging(logger_name)
        self._mysql = mysql_connection_pool.Mysql()

    def get_content(self):
        get_proxy = self._proxy.get_proxy_list()
        for item in get_proxy:
            # 代理服务器的IP地址和端口
            proxy_ip = item['ip']
            proxy_port = item['port']
            if item['https'] == '支持':
                # 构建代理字典
                proxies = {'http': f'http://{proxy_ip}:{proxy_port}', }
            else:
                proxies = {'https': f'http://{proxy_ip}:{proxy_port}'}
            # 发起请求，使用代理
            response = self._connection.init_connection(self._url, proxies=proxies)
            if response:
                # 查找标题元素
                title_element = response.find('h1', class_='rich_media_title')
                div_element = response.find('div', class_='rich_media_content')
                img_tags = div_element.find_all('img')
                # 遍历每个<img>标签
                for img in img_tags:
                    # 获取图片的URL
                    try:
                        img_url = img['data-src']
                    except KeyError:
                        continue
                    # 发送请求下载图片
                    img_response = self._connection.init_connection(url=img_url, proxies=proxies, binary=True)
                    # 解析原始地址的文件名和文件扩展名
                    try:
                        img_format = img['data-type']
                    except KeyError:
                        continue
                    # 检查响应状态码
                    if img_response:
                        img['class'] = img.get('class', []) + ['lazyload']
                        # 进行地址替换操作，例如将原始地址中的域名部分和文件名部分都替换为新的值
                        new_domain = 'staticx.dev'
                        new_filename = 'amusing'
                        # 提取图片文件名
                        img_filename = f'{str(uuid.uuid4())}.{img_format}'
                        new_img_url = f'https://{new_domain}/{new_filename}/{img_filename}'

                        # 保存图片到本地
                        with open(os.path.join(self._path, img_filename), 'wb') as f:
                            f.write(img_response)
                            print(f"图片 {img_filename} 下载成功")
                        # 替换图片标签中的 src 属性为新的地址
                        img['data-src'] = new_img_url
                    else:
                        print(f"图片 {img_url} 下载失败")
                # 删除style属性
                if 'style' in div_element.attrs:
                    del div_element['style']
                # 提取标题文本
                title = title_element.text.strip()
                content = div_element.prettify()
                # 检查请求的响应
                self.save_mp_content(title=title, content=content)
                print('请求成功')
                # 进行响应处理
            else:
                print('请求失败')
                continue

    def save_mp_content(self, title, content):
        """
        将获取到的知乎日报内容保存到数据库

        :param title: 文章 title
        :param content: 文章内容
        :return: 保存成功 True, 未保存成功 False，并记录日志
        """
        get_link_text = str(uuid.uuid4())
        # 列表小图 url
        list_img_url = 'https://staticx.dev/amusing/tulips-in-full-bloom.max_1062x443.jpg'
        # 顶部大图 url
        top_img_url = 'https://staticx.dev/amusing/tulips-in-full-bloom.max_1062x443.jpg'
        insert_amusing_article_sql = f"INSERT INTO amusing_articles(TITLE, TOP_IMAGE_URL, TOP_IMAGE_ALT, TOP_IMAGE_TITLE, LIST_SMALL_IMAGE_URL, BODY_HTML, LINK_TEXT, article_info, URL, category_id, FORMAT_ID) VALUE (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        try:
            amusing_article_result = self._mysql.insert_one(sql=insert_amusing_article_sql,
                                                            value=(title, top_img_url, title, title, list_img_url,
                                                                   content, get_link_text, None,
                                                                   str(uuid.uuid4()), 3, 1))
        except DataError as e:
            self._logging.error(f"插入知乎文章出现错误，具体错误内容：{e}")
            return False
        self._mysql.end()
        if amusing_article_result:
            return True
        else:
            self._logging.error(f"保存知乎日报的内容出现错误，id 为：")
            return False
