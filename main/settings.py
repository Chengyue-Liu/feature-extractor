#!/usr/bin/env python
# -*- coding: utf-8 -*-
import multiprocessing

# @Time : 2023/11/3 11:50
# @Author : Liu Chengyue
# @File : settings.py
# @Software: PyCharm
from environs import Env
env = Env()
env.read_env()
EXTRACTION_PROCESS_NUM = env.int("EXTRACTION_PROCESS_NUM", multiprocessing.cpu_count() - 1)