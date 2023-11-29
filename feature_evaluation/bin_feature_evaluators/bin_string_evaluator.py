#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from collections import Counter
from typing import List

from feature_evaluation.entities import BinStringFeature
from feature_evaluation.feature_evaluator import FeatureEvaluator
from feature_extraction.bin_feature_extractors.bin_string_extractor import BinStringExtractor
from settings import BIN_STRING_SCA_THRESHOLD
from utils.elf_utils import extract_elf_strings


# @Time : 2023/11/22 15:49
# @Author : Liu Chengyue


class BinStringEvaluator(FeatureEvaluator):
    def __init__(self):
        # bin_string_features
        super().__init__(BinStringExtractor.__name__)

        # 转换特征
        self.bin_string_feature_dict = dict()
        for repo_feature in self.repo_features:
            key = f"{repo_feature.repository.repo_id}-{repo_feature.repository.version_id}"
            if not self.bin_string_feature_dict.get(key):
                self.bin_string_feature_dict[key] = BinStringFeature(repo_feature)
            else:
                self.bin_string_feature_dict[key].strings.update(BinStringFeature(repo_feature).strings)

        # 计数
        self.bin_string_num_dict = {
            key: len(strings.strings)
            for key, strings in self.bin_string_feature_dict.items()
        }

        # string ---> bins
        self.string_repo_dict = dict()
        self.string_repo_version_dict = dict()
        for repo_feature in self.bin_string_feature_dict.values():
            repo_id = repo_feature.repository.repo_id
            version_id = repo_feature.repository.version_id
            for string in repo_feature.strings:
                if not (repo_id_set := self.string_repo_dict.get(string)):
                    self.string_repo_dict[string] = repo_id_set = set()
                repo_id_set.add(repo_id)

                if not (repo_version_id_set := self.string_repo_version_dict.get(string)):
                    self.string_repo_version_dict[string] = repo_version_id_set = set()
                repo_version_id_set.add((repo_id, version_id))

    def evaluate(self):
        # 分布统计
        repo_string_nums = [len(repo_feature.strings) for repo_feature in self.bin_string_feature_dict.values()]
        self.statistic(repo_string_nums, "statistic_in_repo_view")

        string_seen_repository_num_list = [len(v) for v in self.string_repo_dict.values()]
        self.statistic(string_seen_repository_num_list, "statistic_in_string_view")

        # sca 效果评估
        self.sca_evaluate()

    def sca(self, file_path):
        # 文件名称
        file_name = os.path.split(file_path)[-1]

        # 提取二进制字符串
        strings = extract_elf_strings(file_path)

        # 根据字符串查询对应的library_id, version_id
        string_repo_id_version_id_tuple_list = []
        for string in strings:
            string_repo_id_version_id_tuple_list.extend(self.string_repo_version_dict.get(string, []))

        # 统计每个版本匹配的数量
        counter = Counter(string_repo_id_version_id_tuple_list)
        all_results = counter.most_common(20)  # (repo_id, version_id), count

        # 筛选
        filtered_results = []
        for (repo_id, version_id), count in all_results:
            key = f"{repo_id}-{version_id}"
            string_num = self.bin_string_num_dict.get(key)
            percent = round(count / string_num, 2)
            if percent > BIN_STRING_SCA_THRESHOLD:
                filtered_results.append((repo_id, version_id))
                # 预览扫描结果
                print(file_name, percent)
        return filtered_results

    def sca_evaluate(self):
        # walk all feature
        for repo_feature in self.repo_features:
            # get ground truth
            ground_truth_repo_id = repo_feature.repository.repo_id
            ground_truth_version_id = repo_feature.repository.repo_id

            # sca
            for file_feature in repo_feature.file_features:
                # sca
                sca_results = self.sca(file_feature.file_path)

                self.check(ground_truth_repo_id, ground_truth_version_id, sca_results)

        precision, recall = self.cal_precision_and_recall(self.repo_sca_check_result)
        print(f"repo level sca result: {self.repo_sca_check_result}, precision: {precision}, recall: {recall}")

        precision, recall = self.cal_precision_and_recall(self.version_sca_check_result)
        print(f"repo level sca result: {self.repo_sca_check_result}, precision: {precision}, recall: {recall}")
