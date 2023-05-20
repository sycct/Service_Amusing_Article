# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import MySQLdb
import os
from retrying import retry


class ConnConfig:
    """Redis和MySQL连接"""

    def __init__(self):
        # Local Test Connection string
        self.mysql_host = os.environ.get('MYSQL_HOST')
        self.mysql_port = int(os.environ.get('MYSQL_PORT'))
        self.mysql_user = os.environ.get('MYSQL_USER')
        self.mysql_password = os.environ.get('MYSQL_PASSWORD')
        self.mysql_database = os.environ.get('MYSQL_DATABASE')
        self.charset = 'utf8mb4'

    @retry(stop_max_attempt_number=10, wait_fixed=2)
    def conn_mysql(self):
        """连接MySQL数据库，链接失败，重试10次，每次间隔2s"""
        # 打开数据库连接
        db = MySQLdb.connect(host=self.mysql_host, port=self.mysql_port, user=self.mysql_user,
                             passwd=self.mysql_password,
                             db=self.mysql_database, charset=self.charset)
        return db
