#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time : 2023/11/21 16:48
# @Author : Liu Chengyue

from environs import Env

env = Env()
env.read_env()

DEBIAN_TAR_FILE_DIR_PATH = env.str("DEBIAN_TAR_FILE_DIR_PATH")
DECOMPRESSED_DEBIAN_FILE_DIR_PATH = env.str("DECOMPRESSED_DEBIAN_FILE_DIR_PATH")