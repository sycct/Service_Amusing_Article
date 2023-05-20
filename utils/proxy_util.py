#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from bs4 import BeautifulSoup

from utils import connection_util


class ProxyUtil(object):
    def __init__(self):
        self._url = 'https://ip.ihuan.me/'
        self._connection = connection_util.ProcessConnection()

    def get_proxy_list(self):
        content = self._connection.init_connection(self._url)
        if content:
            # 查找所有的表格行
            table_rows = content.find_all('tr')
            # 遍历每一行（跳过表头）
            proxy_list = [{'ip': row.find('a').text, 'port': row.find_all('td')[1].text,
                           'https': row.find_all('td')[4].text} for row in table_rows[1:]]
            return proxy_list
