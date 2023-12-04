#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from typing import List

from loguru import logger

from feature_extraction.bin_feature_extractors.bin_string_extractor import BinStringExtractor
# @Time : 2023/11/3 12:06
# @Author : Liu Chengyue
# @File : extractor_runner.py
# @Software: PyCharm

from feature_extraction.decrators import timing_decorator, log_decorator
from feature_extraction.entities import Repository
from feature_extraction.src_feature_extractors.src_string_and_funtion_name_extractor import SrcStringAndFunctionNameExtractor
from settings import SRC_REPOS_JSON, BIN_REPOS_JSON


@timing_decorator
def run_src_extractor(tasks: List[Repository]):
    logger.info(f"SrcStringAndFunctionNameExtractor, task num: {len(tasks)}")
    extractor = SrcStringAndFunctionNameExtractor(tasks)
    extractor.multiple_run()


@timing_decorator
def run_bin_extractor(repos: List[Repository]):
    logger.info(f"BinStringExtractor, task num: {len(repos)}")
    extractor = BinStringExtractor(repos)
    extractor.multiple_run()


def main():
    # 生成json信息
    logger.info(f"生成json信息")
    Repository.generate_repositories_json()

    # 从json信息初始化
    logger.info(f"从json信息初始化")
    # bin_repos = Repository.init_repositories_from_json_file(BIN_REPOS_JSON)
    src_repos = Repository.init_repositories_from_json_file(SRC_REPOS_JSON)

    # 提取特征
    logger.info(f"提取特征")
    # 二进制字符串
    # run_bin_extractor(bin_repos)
    # 源码字符串
    run_src_extractor(src_repos)

    logger.info("all done.")


if __name__ == '__main__':
    main()
