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
    def get_test_cases(cls, f_path=TEST_CASES_JSON_PATH):
        with open(f_path) as f:
            repo_jsons = json.load(f)
            test_cases = [
                TestCase(
                    ground_truth_repo_id=repo_json["repo_id"],
                    ground_truth_version_id=repo_json["version_id"],
                    file_path=repo_json["elf_path"],
                    file_strings=repo_json["strings"],
                )
                for repo_json in repo_jsons]
        return test_cases

    def custom_serialize(self):
        """
                self.ground_truth_repo_id = ground_truth_repo_id
        self.ground_truth_version_id = ground_truth_version_id
        self.file_path = file_path
        self.file_strings = file_strings

        :return:
        """
        return {
            "file_path": self.file_path,
            "file_name": os.path.basename(self.file_path),
            "ground_truth_repo_id": self.ground_truth_repo_id,
            "ground_truth_version_id": self.ground_truth_version_id,
            "strings_num": len(self.file_strings),
        }
