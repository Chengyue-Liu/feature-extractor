#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import random
from typing import Set, List

from tqdm import tqdm

from feature_extraction.bin_feature_extractors.bin_string_extractor import BinStringExtractor
from feature_extraction.entities import RepoFeature, Repository
from settings import FEATURE_RESULT_DIR, TEST_CASES_JSON_PATH


# @Time : 2023/11/29 15:53
# @Author : Liu Chengyue

class SrcStringFeature:
    def __init__(self, repo_feature: RepoFeature):
        self.repository: Repository = repo_feature.repository
        self.strings: Set[str] = set()
        for file_feature in repo_feature.file_features:
            self.strings.update(file_feature.feature["strings"])


class SrcFunctionNameFeature:
    def __init__(self, repo_feature: RepoFeature):
        self.repository: Repository = repo_feature.repository
        self.function_names: Set[str] = set()
        for file_feature in repo_feature.file_features:
            self.function_names.update(file_feature.feature["function_names"])


class BinStringFeature:
    def __init__(self, repo_feature: RepoFeature):
        self.repository: Repository = repo_feature.repository
        self.strings: Set[str] = set()
        for file_feature in repo_feature.file_features:
            self.strings.update(file_feature.feature["strings"])


class TestCase:
    def __init__(self, ground_truth_repo_id, ground_truth_version_id, file_path, file_strings):
        self.ground_truth_repo_id = ground_truth_repo_id
        self.ground_truth_version_id = ground_truth_version_id
        self.file_path = file_path
        self.file_strings = file_strings

    @classmethod
    def get_test_cases(cls):
        """
        这个方法可以筛选测试用例，加快测试速度等等。

        :return:
        """
        return cls.init_from_test_cases_json_file()

    @classmethod
    def init_from_test_cases_json_file(cls, f_path=TEST_CASES_JSON_PATH):
        """
        从测试用例文件生成测试用例
        """
        with open(f_path) as f:
            repo_jsons = json.load(f)
            test_cases = []
            for repo_json in repo_jsons:
                repo_id = repo_json["repo_id"]
                version_id = repo_json["version_id"]
                file_paths = repo_json["elf_paths"]
                tc = TestCase(
                    ground_truth_repo_id=repo_id,
                    ground_truth_version_id=version_id,
                    file_paths=file_paths
                )
                test_cases.append(tc)
        return test_cases
