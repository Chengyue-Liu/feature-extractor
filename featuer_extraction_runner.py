#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from typing import List

from loguru import logger

from feature_extraction.bin_feature_extractors.bin_string_extractors import BinStringExtractor
# @Time : 2023/11/3 12:06
# @Author : Liu Chengyue
# @File : extractor_runner.py
# @Software: PyCharm

from feature_extraction.decrators import timing_decorator, log_decorator
from feature_extraction.entities import Task
from feature_extraction.src_feature_extractors.src_string_and_funtion_name_extractor import SrcStringAndFunctionNameExtractor
from feature_extraction.src_feature_extractors.src_function_name_extractor import SrcFunctionNameExtractor
from settings import SRC_TASKS_JSON, BIN_TASKS_JSON


@timing_decorator
def run_src_extractor(tasks: List[Task]):
    logger.info(f"SrcStringAndFunctionNameExtractor, task num: {len(tasks)}")
    extractor = SrcStringAndFunctionNameExtractor(tasks)
    extractor.multiple_run()


@timing_decorator
def run_bin_extractor(tasks: List[Task]):
    logger.info(f"BinStringExtractor, task num: {len(tasks)}")
    extractor = BinStringExtractor(tasks)
    extractor.multiple_run()


def main():
    # 生成任务
    Task.generate_tasks_json()

    # 初始化任务
    src_tasks = Task.init_tasks_from_json(SRC_TASKS_JSON)
    bin_tasks = Task.init_tasks_from_json(BIN_TASKS_JSON)

    run_bin_extractor(bin_tasks)
    run_src_extractor(src_tasks)


if __name__ == '__main__':
    main()
