#!/usr/bin/env python
# -*- coding: utf-8 -*-

from feature_evaluation.bin_feature_evaluators.bin_string_evaluator import BinStringEvaluator
from feature_evaluation.src_feature_evaluators.src_function_name_evaluator import SrcFunctionNameEvaluator
from feature_evaluation.src_feature_evaluators.src_string_evaluator import SrcStringEvaluator


# @Time : 2023/11/3 12:06
# @Author : Liu Chengyue
# @File : extractor_runner.py
# @Software: PyCharm


def main():
    # 生成任务
    # bin string
    evaluator = BinStringEvaluator()
    evaluator.evaluate()

    # src string
    evaluator = SrcStringEvaluator()
    evaluator.evaluate()

    # src function name
    evaluator = SrcFunctionNameEvaluator()
    evaluator.evaluate()

    # 常用命令
    # nohup python feature_evaluator_runner.py &
    # ps aux | grep "python feature_evaluator_runner.py" | grep -v grep | awk '{print $2}' | xargs kill



if __name__ == '__main__':
    main()


# todo
"""
1. 后续其他的特征，一定要存到postgres中。存在文件中，每次读取太慢了。

"""