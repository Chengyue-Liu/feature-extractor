#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from loguru import logger

from settings import DEBIAN_FILE_DIR_PATH


# @Time : 2023/11/21 16:48
# @Author : Liu Chengyue
def is_src_package(file_name):
    pass


def is_bin_package(file_name):
    pass


def parse_info_from_file_name(file_name):
    pass


def get_tar_file_paths():
    src_tar_paths = []
    bin_tar_paths = []
    count = 0
    for root, dirs, files in os.walk(DEBIAN_FILE_DIR_PATH):
        for f_name in files:
            count += 1
            if count % 1000 == 0:
                logger.info(f"walk progress: {count}")

            f_path = os.path.join(root, f_name)
            if is_src_package(f_name):
                src_tar_paths.append(f_path)
            elif is_bin_package(f_name):
                bin_tar_paths.append(f_path)
    logger.info(f"walk finished. all count = {count}")
    return src_tar_paths, bin_tar_paths
