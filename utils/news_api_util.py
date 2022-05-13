#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import requests
from datetime import datetime
from MySQLdb import DataError

from config import logging_config, mysql_connection_pool, news_api_url, news_api_key


class NewsAPIUtil(object):
    def __init__(self):
        logger_name = 'News_API'
        init_logging = logging_config.LoggingConfig()
        self._logging = init_logging.init_logging(logger_name)
        self._mysql = mysql_connection_pool.Mysql()
        self._news_api_keywords = ['apple', 'tesla', 'Volkswagen', 'finance', 'futures', 'economy', 'Entrepreneurship',
                                   'business', 'web3']

    def new_api_main(self):
        for keyword in self._news_api_keywords:
            get_articles = self.get_news_api_json(keyword)
            if get_articles:
                for item in get_articles:
                    self.save_original_data(item['title'], item['urlToImage'], 3, item['author'], item['url'], 0)

    def get_news_api_json(self, keyword):
        # news api url exp: https://newsapi.org/v2/everything?q=apple&from=2022-04-13&to=2022-04-13&sortBy=popularity&apiKey=40522fe626924885bbbbb73aebe890f8
        news_api_url_format = news_api_url + '/v2/everything?q=' + keyword + '&from=' + \
                              datetime.utcnow().strftime('%Y-%m-%d') + '&to=' + datetime.utcnow().strftime('%Y-%m-%d') \
                              + '&sortBy=popularity&apiKey=' + news_api_key
        # 通过 News API 获取文章相关信息
        get_new_api_json = requests.get(news_api_url_format)
        r = get_new_api_json.json()
        if r['status'] == 'ok':
            get_articles = r['articles']
            articles = [{'author': item['author'], 'title': item['title'], 'url': item['url'],
                         'urlToImage': item['urlToImage']} for item in get_articles]
            return articles
        else:
            self._logging.error('通过 News API 获取数据失败，请检查！')
            return False

    def save_original_data(self, title, img_url, category_id, author, url, status):
        query_url_sql = f"SELECT * FROM amusing_original_articles WHERE url='{url}';"
        query_url = self._mysql.get_one(sql=query_url_sql)
        if query_url:
            return True
        else:
            insert_original_sql = f"INSERT INTO amusing_original_articles(title, author, status, url, url_to_image, category_id) VALUE (%s,%s,%s,%s,%s,%s);"
            try:
                insert_original_result = self._mysql.insert_one(sql=insert_original_sql,
                                                                value=(title, author, status, url, img_url,
                                                                       category_id,))
            except DataError as e:
                self._logging.error(f"插入 amusing_original_articles 数据失败，具体错误内容： {e}")
                return False
            self._mysql.end()
            if insert_original_result:
                return True
            else:
                self._logging.error("保存通过 News API 获取的数据失败,请检查！")
                return False
