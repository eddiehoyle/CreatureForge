#!/usr/bin/env python

"""
"""

import logging

def get_logger(name):

    if logging.Logger.manager.loggerDict.get(name):
        return logging.Logger.manager.loggerDict.get(name)

    else:

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        
        formatter = MyFormatter()
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.propagate = False

        return logger

class MyFormatter(logging.Formatter):

    WIDTH = 20

    def format(self, record):
        cpath = '%s:%s:%s' % (record.module, record.funcName, record.lineno)
        cpath = cpath[-self.WIDTH:].ljust(self.WIDTH)
        record.message = record.getMessage()
        s = "%s - %s" % (record.levelname, record.getMessage())

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + record.exc_text

        return s