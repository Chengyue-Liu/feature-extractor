#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from collections import Counter
from typing import List, Set

from feature_evaluation.feature_evaluator import FeatureEvaluator
from feature_extraction.bin_feature_extractors.bin_feature_extractor import BinFeatureExtractor
from feature_extraction.bin_feature_extractors.bin_string_extractor import BinStringExtractor
from feature_extraction.entities import RepoFeature, Repository
from settings import FEATURE_RESULT_DIR, BIN_STRING_SCA_THRESHOLD

import numpy as np


# @Time : 2023/11/22 15:49
# @Author : Liu Chengyue

class BinStringFeature:
    def __init__(self, repo_feature: RepoFeature):
        self.repository: Repository = repo_feature.repository
        self.strings: Set[str] = set()
        for file_feature in repo_feature.file_features:
            self.strings.update(file_feature.feature)


class BinStringEvaluator(FeatureEvaluator):
    def __init__(self):
        # bin_string_features
        super().__init__()

        # bin ---> strings
        self.bin_string_features: List[BinStringFeature] = [BinStringFeature(repo_feature)
                                                            for repo_feature in self.repo_features]

        # string ---> bins
        string_repo_dict = dict()
        string_repo_version_dict = dict()
        for repo_feature in self.bin_string_features:
            repo_id = repo_feature.repository.repo_id
            version_id = repo_feature.repository.version_id
            for string in repo_feature.strings:
                if not (repo_id_set := string_repo_dict.get(string)):
                    string_repo_dict[string] = repo_id_set = set()
                repo_id_set.add(repo_id)

                if not (repo_version_id_set := string_repo_version_dict.get(string)):
                    string_repo_version_dict[string] = repo_version_id_set = set()
                repo_version_id_set.add((repo_id, version_id))

        self.string_repo_dict = string_repo_dict
        self.string_repo_version_dict = string_repo_version_dict

        # result
        self.repo_sca_check_result = {
            "tp": 0,
            "fp": 0,
            "fn": 0,
        }
        self.version_sca_check_result = {
            "tp": 0,
            "fp": 0,
            "fn": 0,
        }

    def evaluate(self):
        # 分布统计
        repo_string_nums = [len(repo_feature.strings) for repo_feature in self.bin_string_features]
        self.statistic(repo_string_nums, "statistic_in_repo_view")

        string_seen_repository_num_list = [len(v) for v in self.string_repo_dict.values()]
        self.statistic(string_seen_repository_num_list, "statistic_in_string_view")

        # sca 效果评估
        self.sca_evaluate()

    def sca(self, strings):
        string_repo_id_version_id_tuple_list = []
        for string in strings:
            # repo level
            string_repo_id_version_id_tuple_list.extend(self.string_repo_version_dict.get(string, []))

        counter = Counter(string_repo_id_version_id_tuple_list)
        (repo_id, version_id), count = counter.most_common(1)[0]
        percent = count / len(strings)
        if percent > BIN_STRING_SCA_THRESHOLD:
            return repo_id, version_id
        else:
            return None, None

    def check(self, ground_truth_repo_id, ground_truth_version_id,
              sca_repo_id, sca_version_id):
        if not sca_repo_id:
            self.repo_sca_check_result["fn"] += 1
            self.version_sca_check_result["fn"] += 1
        else:
            if ground_truth_repo_id == sca_repo_id:
                self.repo_sca_check_result["tp"] += 1
                if ground_truth_version_id == sca_version_id:
                    self.version_sca_check_result["tp"] += 1
                else:
                    self.version_sca_check_result["fp"] += 1
            else:
                self.repo_sca_check_result["fp"] += 1
                self.version_sca_check_result["fp"] += 1

    def sca_evaluate(self):
        for bin_string_feature in self.bin_string_features:
            ground_truth_repo_id = bin_string_feature.repository.repo_id
            ground_truth_version_id = bin_string_feature.repository.repo_id
            strings = bin_string_feature.strings
            sca_repo_id, sca_version_id = self.sca(strings)
            self.check(ground_truth_repo_id, ground_truth_version_id, sca_repo_id, sca_version_id)

        def cal_precision_and_recall(sca_check_result):
            precision = sca_check_result['tp'] / (sca_check_result['tp'] + sca_check_result['fp'])
            recall = sca_check_result['tp'] / (sca_check_result['tp'] + sca_check_result['fn'])
            return precision, recall

        print(cal_precision_and_recall(self.repo_sca_check_result))
        print(cal_precision_and_recall(self.version_sca_check_result))
