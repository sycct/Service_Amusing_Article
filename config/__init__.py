# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

# loading env config file
dotenv_path = os.path.join(os.getcwd(), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

zhihu_new_latest_url = os.environ.get('ZHIHU_NEWS_LATEST_URL')
zhihu_new_content_url = os.environ.get('ZHIHU_NEWS_CONTENT_URL')
# server info
remote_host = os.environ.get('REMOTE_UBUNTU_HOST')
remote_user = os.environ.get('REMOTE_UBUNTU_USER')
# bandwagong host server info
wagong_remote_host = os.environ.get('BANDWAGONG_REMOTE_UBUNTU_HOST')
wagong_port = os.environ.get('BANDWAGONG_PORT')
wagong_remote_user = os.environ.get('BANDWAGONG_REMOTE_UBUNTU_USER')
wagong_remote_password = os.environ.get('BANDWAGONG_REMOTE_UBUNTU_PASSWORD')
# 保存知乎日报图片远程文件路径
zhihu_cdn_path = os.environ.get('REMOTE_UBUNTU_ZHIHU_CDN_PATH')
# News API url
news_api_url = os.environ.get('NEWS_API_URL')
news_api_key = os.environ.get('NEWS_API_KEY')
