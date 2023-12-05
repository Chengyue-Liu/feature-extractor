#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from typing import List

from loguru import logger

from feature_evaluation.bin_feature_evaluators.bin_string_evaluator import BinStringEvaluator
from feature_evaluation.src_feature_evaluators.src_function_name_evaluator import SrcFunctionNameEvaluator
from feature_evaluation.src_feature_evaluators.src_string_evaluator import SrcStringEvaluator
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
    # bin string
    evaluator = BinStringEvaluator()
    evaluator.merge_features()
    evaluator.evaluate()

    # src string
    evaluator = SrcStringEvaluator()
    evaluator.merge_features()
    evaluator.evaluate()

    # src function name
    evaluator = SrcFunctionNameEvaluator()
    evaluator.merge_features()
    evaluator.evaluate()

    # 常用命令
    # nohup python feature_evaluator_runner.py &
    # ps aux | grep "python feature_evaluator_runner.py" | grep -v grep | awk '{print $2}' | xargs kill


if __name__ == '__main__':
    main()


# todo
"""
1. 把字符串，和函数名合并，搞明白，然后今晚跑一遍1000个测试用例的。
2. 明天周三，和字哥沟通一下现在的情况。

"""