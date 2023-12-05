#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
from typing import Set, List

from feature_extraction.entities import RepoFeature, Repository


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
    def init_from_repo_feature_file_path(cls, f_path):
        with open(f_path) as f:
            repo_feature_json = json.load(f)
            repo_id = repo_feature_json["repository"]["repo_id"]
            version_id = repo_feature_json["repository"]["version_id"]
            file_paths = [ff["file_path"] for ff in repo_feature_json['file_features']]
            return TestCase(
                    ground_truth_repo_id=repo_id,
                    ground_truth_version_id=version_id,
                    file_paths=file_paths
                )
