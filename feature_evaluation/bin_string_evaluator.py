#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from abc import ABC
from typing import Set

from feature_evaluation.feature_evaluator import FeatureEvaluator
from feature_extraction.bin_feature_extractors.bin_string_extractors import BinStringExtractor
from settings import FEATURE_RESULT_DIR


# @Time : 2023/11/22 15:49
# @Author : Liu Chengyue


class BinStringEvaluator(FeatureEvaluator, ABC):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        feature_dir = os.path.join(FEATURE_RESULT_DIR, BinStringExtractor.__name__)
        self.load_task_and_features(feature_dir)

    def convert_repo_feature(self, repo_feature):
        file_features = repo_feature['file_features']
        file_bin_strings = set()
        for file_feature in file_features:
            file_bin_strings.update(file_feature['features'])

        return file_bin_strings

    def compare(self, repo_feature, to_compare_repo_feature):
        repo_file_bin_strings = self.convert_repo_feature(repo_feature)
        to_compare_repo_file_bin_strings = self.convert_repo_feature(to_compare_repo_feature)

        intersection = repo_file_bin_strings.intersection(to_compare_repo_file_bin_strings)
        similarity = round((len(intersection) / len(to_compare_repo_file_bin_strings)) * 100, 2)

        return similarity

    def detect(self):
        for repo_feature in self.repo_features:
            repo_id = repo_feature['task']['repo_id']
            highest_similarity = 0
            most_possible_repo = None
            for to_compare_repo_feature in self.repo_features:
                to_compare_repo_id = to_compare_repo_feature['task']['repo_id']
                similarity = self.compare(repo_feature, to_compare_repo_feature)
                print(repo_id, to_compare_repo_id, similarity)
                if similarity > highest_similarity:
                    highest_similarity = similarity
                    most_possible_repo = to_compare_repo_feature["task"]
            most_possible_repo_id = most_possible_repo['repo_id']
            if not highest_similarity > 70:
                detect_result = "FN"
            else:
                if most_possible_repo_id == repo_id:
                    detect_result = "TP"
                else:
                    detect_result = "FP"
            print(detect_result, highest_similarity, repo_feature['task'], ' ---> ', most_possible_repo)

    def evaluate(self):
        """
        评估：
            1. 覆盖率
            2. 检测精度
            3. 时间，性能开销
            4. 鲁棒性？
        :return:
        """
        # 覆盖率
        self.evaluate_coverage()
        self.detect()

    def evaluate_coverage(self):
        no_feature_repo_count = 0
        for repo_feature in self.repo_features:
            file_features = repo_feature['file_features']
            file_bin_strings = set()
            for file_feature in file_features:
                file_bin_strings.update(file_feature['features'])
            if not file_bin_strings:
                no_feature_repo_count += 1
        repo_num = len(self.repo_features)
        coverage = (repo_num - no_feature_repo_count) / repo_num
        print(repo_num, no_feature_repo_count, coverage)
