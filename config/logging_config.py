#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import logging
import logging.handlers


class LoggingConfig(object):
    @staticmethod
    def init_logging(logging_name):
        # formal environment
        fh = logging.FileHandler(encoding='utf-8', mode='a', filename='./amusing_article.log')

        # set up logging to file - see previous section for more details
        logging.basicConfig(handlers=[fh],
                            level=logging.ERROR,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M')
        # define a Handler which writes INFO messages or higher to the sys.stderr
        console = logging.StreamHandler()
        console.setLevel(logging.WARNING)
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('').addHandler(console)

        # Now, define a couple of other loggers which might represent areas in your
        # application:

        return logging.getLogger(logging_name)
