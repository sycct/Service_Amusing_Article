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
# bandwagon host server info
bandwagon_host_remote_host = os.environ.get('BANDWAGONHOST_REMOTE_UBUNTU_HOST')
bandwagon_host_remote_user = os.environ.get('BANDWAGONHOST_REMOTE_UBUNTU_USER')
bandwagon_host_remote_port = os.environ.get('BANDWAGONHOST_REMOTE_UBUNTU_PORT')
bandwagon_host_remote_password = os.environ.get('BANDWAGONHOST_REMOTE_UBUNTU_PASSWORD')
# VMISS US host server info
aws_lightsail_in_remote_host = os.environ.get('AWS_LIGHTSAIL_IN_REMOTE_UBUNTU_HOST')
aws_lightsail_in_remote_user = os.environ.get('AWS_LIGHTSAIL_IN_REMOTE_UBUNTU_USER')
aws_lightsail_in_remote_port = os.environ.get('AWS_LIGHTSAIL_IN_REMOTE_PORT')
# 保存知乎日报图片远程文件路径
zhihu_cdn_path = os.environ.get('REMOTE_UBUNTU_ZHIHU_CDN_PATH')
# News API url
news_api_url = os.environ.get('NEWS_API_URL')
news_api_key = os.environ.get('NEWS_API_KEY')
proxy_url = os.environ.get('PROXY_URL')
# 连接服务器重试次数
max_retries = os.environ.get('MAX_RETRIES')
# 每次重试中间时间间隔
retry_delay = os.environ.get('RETRY_DELAY')
