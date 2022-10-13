#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
from apscheduler.schedulers.blocking import BlockingScheduler

from utils import zhihu_util, news_api_util


class AmusingArticleMian(object):
    def __init__(self):
        self._zhihu = zhihu_util.ZhiHuUtil()
        self._news_api = news_api_util.NewsAPIUtil()

    def zhihu_run(self):
        self._zhihu.zhihu_main()

    def news_api_run(self):
        self._news_api.new_api_main()


if __name__ == '__main__':
    init_amusing = AmusingArticleMian()
    # 实例化一个调度器
    scheduler = BlockingScheduler(timezone='Asia/Shanghai')
    # 添加任务并设置触发方式每天8:30点执行一次
    scheduler.add_job(init_amusing.zhihu_run, 'cron', hour=8, minute=00)
    # 开始运行调度器
    try:
        scheduler.start()
    except KeyboardInterrupt:
        sys.exit(0)
