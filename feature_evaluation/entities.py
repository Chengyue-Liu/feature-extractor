#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Set

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
