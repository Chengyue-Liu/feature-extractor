#!/usr/bin/env python
# -*- coding: utf-8 -*-
import multiprocessing

# @Time : 2023/11/21 16:48
# @Author : Liu Chengyue

from environs import Env

env = Env()
env.read_env()

# share
PROCESS_NUM = env.int("EXTRACTION_PROCESS_NUM", multiprocessing.cpu_count())

# data preparation
DEBIAN_TAR_FILE_DIR_PATH = env.str("DEBIAN_TAR_FILE_DIR_PATH")
DECOMPRESSED_DEBIAN_FILE_DIR_PATH = env.str("DECOMPRESSED_DEBIAN_FILE_DIR_PATH")

# feature extraction
LANGUAGE_SO_FILE_PATH = env.str("LANGUAGE_SO_FILE_PATH", "resources/build/my-languages-mac.so")

SRC_REPOS_JSON = env.str("SRC_REPOS_JSON", "resources/repository_json/src_repos.json")
BIN_REPOS_JSON = env.str("BIN_REPOS_JSON", "resources/repository_json/bin_repos.json")

FEATURE_RESULT_DIR = env.str("FEATURE_RESULT_DIR", "features")

# feature evaluation

TEST_CASES_JSON_PATH = env.str("TEST_CASES_JSON_PATH", "resources/repository_json/test_cases.json")
TEST_CASE_SAMPLE_SIZE = env.int("TEST_CASE_SAMPLE_SIZE", 1000)

# bin string sca threshold
BIN_STRING_SCA_THRESHOLD = 0.6
SRC_STRING_SCA_THRESHOLD = 0.1
SRC_FUNCTION_NAME_SCA_THRESHOLD = 0.1
