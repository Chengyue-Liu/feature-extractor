#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
import traceback

from loguru import logger

from data_preparation.decompress_debian_package import get_decompress_target_path
from utils.json_util import load_from_json


# @Time : 2023/11/22 13:59
# @Author : Liu Chengyue

def select():
    # 加载原始数据
    src_tar_paths = load_from_json(
        "/Users/liuchengyue/Desktop/works/feature_analysis/feature-extractor/test_cases/src_tar_paths.json")
    bin_tar_paths = load_from_json(
        "/Users/liuchengyue/Desktop/works/feature_analysis/feature-extractor/test_cases/bin_tar_paths.json")

    # 过滤错误数据
    src_tar_paths = [path for path in src_tar_paths if "debian.tar." not in path and "orig-" not in path]

    src_tar_paths.extend(bin_tar_paths)
    for path in src_tar_paths:
        src_tar_name: str = os.path.split(path)[-1]
        try:
            decompress_target_path = get_decompress_target_path(src_tar_name)
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error(f"{src_tar_name}, error: {e}")
            raise


if __name__ == '__main__':
    select()
