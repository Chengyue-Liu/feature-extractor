#!/usr/bin/env python
# -*- coding: utf-8 -*-
from feature_evaluation.entities import TestCase

# @Time : 2023/12/5 14:42
# @Author : Liu Chengyue


if __name__ == '__main__':
    """
    生成测试用例信息【不要所有的，从二进制里面跳一部分出来】
    """
    TestCase.update_test_cases_json()
