#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from typing import List

from loguru import logger

from feature_evaluation.bin_string_evaluator import BinStringEvaluator
from feature_extraction.bin_feature_extractors.bin_string_extractor import BinStringExtractor
# @Time : 2023/11/3 12:06
# @Author : Liu Chengyue
# @File : extractor_runner.py
# @Software: PyCharm

from feature_extraction.decrators import timing_decorator, log_decorator
from feature_extraction.entities import Repository
from feature_extraction.src_feature_extractors.src_string_and_funtion_name_extractor import SrcStringAndFunctionNameExtractor
from settings import SRC_REPOS_JSON, BIN_REPOS_JSON



def main():
    # 生成任务
    evaluator = BinStringEvaluator()
    evaluator.evaluate()


if __name__ == '__main__':
    main()