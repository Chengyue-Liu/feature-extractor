#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
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
            self.strings.update(file_feature.feature)


class TestCase:
    def __init__(self, ground_truth_repo_id, ground_truth_version_id, file_paths):
        self.ground_truth_repo_id = ground_truth_repo_id
        self.ground_truth_version_id = ground_truth_version_id
        self.file_paths = file_paths

    @classmethod
    def get_test_cases(cls):
        """
        这个方法可以筛选测试用例，加快测试速度等等。

        :return:
        """
        test_cases, test_case_file_count = cls.init_from_test_cases_json_file()
        return test_cases, test_case_file_count

    @classmethod
    def init_test_cases_from_repo_feature_json_file(cls):
        """
        从库的特征生成测试用例
        :return:
        """
        feature_dir = os.path.join(FEATURE_RESULT_DIR, BinStringExtractor.__name__)
        feature_files = os.listdir(feature_dir)
        test_cases = []
        test_case_file_count = 0
        for f_name in tqdm(feature_files, total=len(feature_files), desc="init_repo_features"):
            if f_name.endswith('.json'):
                f_path = os.path.join(feature_dir, f_name)
                with open(f_path) as f:
                    repo_feature_json = json.load(f)
                    repo_id = repo_feature_json["repository"]["repo_id"]
                    version_id = repo_feature_json["repository"]["version_id"]
                    file_paths = [ff["file_path"] for ff in repo_feature_json['file_features']]
                    tc = TestCase(
                        ground_truth_repo_id=repo_id,
                        ground_truth_version_id=version_id,
                        file_paths=file_paths
                    )
                    test_cases.append(tc)
                    test_case_file_count += len(tc.file_paths)
        return test_cases, test_case_file_count

    @classmethod
    def init_from_test_cases_json_file(cls, f_path=TEST_CASES_JSON_PATH):
        """
        从测试用例文件生成测试用例
        """
        test_case_file_count = 0
        with open(f_path) as f:
            data = json.load(f)
            test_cases = []
            for tc_json in data:
                repo_id = tc_json["ground_truth_repo_id"]
                version_id = tc_json["ground_truth_version_id"]
                file_paths = tc_json["file_paths"]
                tc = TestCase(
                    ground_truth_repo_id=repo_id,
                    ground_truth_version_id=version_id,
                    file_paths=file_paths
                )
                test_cases.append(tc)
                test_case_file_count += len(tc.file_paths)
        return test_cases, test_case_file_count

    @classmethod
    def update_test_cases_json(cls, json_path=TEST_CASES_JSON_PATH):
        """
        更新测试用例文件
        :param json_path:
        :return:
        """
        test_cases, test_case_file_count = cls.init_test_cases_from_repo_feature_json_file()
        test_cases_json = [tc.custom_serialize() for tc in test_cases]
        with open(json_path, 'w') as f:
            json.dump(test_cases_json, f, ensure_ascii=False)

    def custom_serialize(self):
        return {
            "ground_truth_repo_id": self.ground_truth_repo_id,
            "ground_truth_version_id": self.ground_truth_version_id,
            "file_paths": self.file_paths,
        }
