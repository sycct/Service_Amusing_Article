#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import requests
from requests import HTTPError, ConnectionError, Timeout

from config import logging_config


class CommonUtil(object):
    def __init__(self):
        logger_name = 'base_util'
        init_logging = logging_config.LoggingConfig()
        self._logging = init_logging.init_logging(logger_name)

    def init_connection(self, url):
        # 连接网站
        try:
            session = requests.Session()
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"}
            html = session.get(url, headers=headers)
        except (ConnectionError, HTTPError, Timeout) as e:
            self._logging.error(f'执行 init_connection 函数出错，具体错误内容：{e}')
            return False
        try:
            bsObj = html.json()
            return bsObj
        except AttributeError as e:
            self._logging.error(f'执行 init_connection 函数出错，具体错误内容：{e}')
            return False

    @staticmethod
    def findAllFile(base):
        # 文件的目录，例如：E:\Code\Service_Amusing_Article\files 文件夹
        for root, ds, fs in os.walk(base):
            for f in fs:
                yield f
