#!/usr/bin/env python
# -*- coding: utf-8 -*-
from loguru import logger

from feature_evaluation.bin_feature_evaluators.bin_string_evaluator import BinStringEvaluator
from feature_evaluation.entities import TestCase
from feature_evaluation.src_feature_evaluators.src_function_name_evaluator import SrcFunctionNameEvaluator
from feature_evaluation.src_feature_evaluators.src_string_evaluator import SrcStringEvaluator


# @Time : 2023/11/3 12:06
# @Author : Liu Chengyue
# @File : extractor_runner.py
# @Software: PyCharm


def main():
    # 生成任务
    logger.info(f"init testcases")
    test_cases = TestCase.get_test_cases()

    # bin string
    # evaluator = BinStringEvaluator()
    # evaluator.evaluate(test_cases)

    # src string
    # evaluator = SrcStringEvaluator()
    # evaluator.evaluate(test_cases)
    #
    # # src function name
    evaluator = SrcFunctionNameEvaluator()
    evaluator.evaluate(test_cases)

    # 常用命令
    # nohup python feature_evaluator_runner.py &
    # ps aux | grep "python feature_evaluator_runner.py" | grep -v grep | awk '{print $2}' | xargs kill


    # 100, 1000, 10000

if __name__ == '__main__':
    main()


# todo
"""
1. 后续其他的特征，一定要存到postgres中。存在文件中，每次读取太慢了。

"""