#!/usr/bin/env python
# -*- coding: utf-8 -*-


# @Time : 2023/11/3 12:20
# @Author : Liu Chengyue
# @File : decrators.py
# @Software: PyCharm
import time
from functools import wraps

from loguru import logger


def log_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"{func.__name__} started!")
        result = func(*args, **kwargs)
        logger.success(f"{func.__name__} finished")
        return result

    return wrapper


def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        duration = round(time.perf_counter() - start_time, 2)
        logger.info(f"{func.__name__} took {duration} seconds to run")
        return result

    return wrapper
