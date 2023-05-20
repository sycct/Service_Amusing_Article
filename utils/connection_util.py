# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.error import HTTPError, URLError
from requests.exceptions import ProxyError, SSLError
import requests
from bs4 import BeautifulSoup

from config import logging_config


class ProcessConnection:
    def __init__(self):
        logger_name = 'connection_helper'
        self._logger_write_file = logging_config.LoggingConfig().init_logging(logger_name)

    def init_connection(self, url, *args, **kwargs):
        # 连接网站
        try:
            session = requests.session()
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"}
            if not kwargs:
                # 直接访问，未使用代理
                html = session.get(url, headers=headers, timeout=10)
            else:
                for key, value in kwargs.items():
                    if key == 'proxies':
                        # 使用了代理
                        html = session.get(url, headers=headers, proxies=value)
                    elif key == 'binary' and value is True:
                        # 二进制内容，例如图片，直接返回
                        return html.content
        except (HTTPError, URLError, ProxyError, SSLError) as e:
            self._logger_write_file.error('执行 get_sms_data 函数出错，具体错误内容：{message}'.format(message=e))
            return False
        try:
            bsObj = BeautifulSoup(html.text, features='html.parser')
            return bsObj
        except AttributeError as e:
            self._logger_write_file.error('执行 get_sms_data 函数出错，具体错误内容：{message}'.format(message=e))
            return False
