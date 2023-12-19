#!/usr/bin/env python
# -*- coding: utf-8 -*-
import multiprocessing

# @Time : 2023/11/21 16:48
# @Author : Liu Chengyue

from environs import Env

env = Env()
env.read_env()

# share
# 多进程数量
PROCESS_NUM = env.int("EXTRACTION_PROCESS_NUM", multiprocessing.cpu_count() - 1)

# data preparation
# debian tar 文件存储路径
DEBIAN_TAR_FILE_DIR_PATH = env.str("DEBIAN_TAR_FILE_DIR_PATH")
# debian 解压后的文件存储路径
DECOMPRESSED_DEBIAN_FILE_DIR_PATH = env.str("DECOMPRESSED_DEBIAN_FILE_DIR_PATH")
# 测试用例信息【所有的二进制包，每个选最新，最旧，和中间的随机版本】
TEST_CASES_JSON_PATH = env.str("TEST_CASES_JSON_PATH", "resources/repository_json/test_cases.json")
TEST_CASES_100_JSON_PATH = env.str("TEST_CASES_100_JSON_PATH", "resources/repository_json/test_cases_100.json")
TEST_CASES_1000_JSON_PATH = env.str("TEST_CASES_1000_JSON_PATH", "resources/repository_json/test_cases_1000.json")
TEST_CASES_10000_JSON_PATH = env.str("TEST_CASES_10000_JSON_PATH", "resources/repository_json/test_cases_10000.json")

# feature extraction
# tree sitter 编译好的解析器 so
LANGUAGE_SO_FILE_PATH = env.str("LANGUAGE_SO_FILE_PATH", "resources/build/my-languages-mac.so")

# 源码信息json
SRC_REPOS_JSON = env.str("SRC_REPOS_JSON", "resources/repository_json/src_repos.json")
# 二进制信息json
BIN_REPOS_JSON = env.str("BIN_REPOS_JSON", "resources/repository_json/bin_repos.json")
# 测试用例信息json
TC_BIN_REPOS_JSON = env.str("TC_BIN_REPOS_JSON", "resources/repository_json/tc_bin_repos.json")

# 特征存储路径
FEATURE_RESULT_DIR = env.str("FEATURE_RESULT_DIR", "features")

# CFG 特征最少的边的数量
EDGE_NUM_THRESHOLD = 5

# feature evaluation

TEST_CASE_SAMPLE_SIZE = env.int("TEST_CASE_SAMPLE_SIZE", 1000)

# bin string sca threshold
BIN_STRING_SCA_THRESHOLD = 0.6
SRC_STRING_SCA_THRESHOLD = 0.1
SRC_FUNCTION_NAME_SCA_THRESHOLD = 0.1
