#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from collections import Counter
from typing import List, Set

from feature_evaluation.entities import SrcStringFeature, BinStringFeature
from feature_evaluation.feature_evaluator import FeatureEvaluator
from feature_extraction.bin_feature_extractors.bin_string_extractor import BinStringExtractor
from feature_extraction.entities import RepoFeature, Repository
from feature_extraction.src_feature_extractors.src_string_and_funtion_name_extractor import \
    SrcStringAndFunctionNameExtractor
from settings import BIN_STRING_SCA_THRESHOLD, BIN_REPOS_JSON, SRC_STRING_SCA_THRESHOLD
from utils.elf_utils import extract_elf_strings
from utils.json_util import load_from_json


# @Time : 2023/11/22 15:49
# @Author : Liu Chengyue


class SrcStringEvaluator(FeatureEvaluator):
    def __init__(self):
        # bin_string_features
        super().__init__(SrcStringAndFunctionNameExtractor.__name__)

        # 转换特征
        self.src_string_feature_dict = dict()
        for repo_feature in self.repo_features:
            key = f"{repo_feature.repository.repo_id}-{repo_feature.repository.version_id}"
            if not self.src_string_feature_dict.get(key):
                self.src_string_feature_dict[key] = SrcStringFeature(repo_feature)
            else:
                self.src_string_feature_dict[key].strings.update(SrcStringFeature(repo_feature).strings)

        # 特征计数
        self.src_string_num_dict = {
            key: len(strings.strings)
            for key, strings in self.src_string_feature_dict.items()
        }

        # 特征倒排索引表
        self.string_repo_dict = dict()
        self.string_repo_version_dict = dict()
        for repo_feature in self.src_string_feature_dict.values():
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
        repo_string_nums = [len(repo_feature.strings) for repo_feature in self.src_string_feature_dict.values()]
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
            string_num = self.src_string_num_dict.get(key)
            percent = round(count / string_num, 2)
            if percent > SRC_STRING_SCA_THRESHOLD:
                filtered_results.append((repo_id, version_id))
                # 预览扫描结果
                print(file_name, percent)

        return filtered_results



    def sca_evaluate(self):
        # walk all binaries
        fe = FeatureEvaluator(BinStringExtractor.__name__)
        # walk all feature
        for repo_feature in fe.repo_features:
            # get ground truth
            ground_truth_repo_id = repo_feature.repository.repo_id
            ground_truth_version_id = repo_feature.repository.repo_id

            # sca
            for file_feature in repo_feature.file_features:
                # sca
                sca_results = self.sca(file_feature.file_path)

                # check sca results
                self.check(ground_truth_repo_id, ground_truth_version_id, sca_results)

        def cal_precision_and_recall(sca_check_result):
            precision = sca_check_result['tp'] / (sca_check_result['tp'] + sca_check_result['fp'])
            recall = sca_check_result['tp'] / (sca_check_result['tp'] + sca_check_result['fn'])
            return precision, recall

        precision, recall = cal_precision_and_recall(self.repo_sca_check_result)
        print(f"repo level sca result: {self.repo_sca_check_result}, precision: {precision}, recall: {recall}")

        precision, recall = cal_precision_and_recall(self.version_sca_check_result)
        print(f"version level sca result: {self.repo_sca_check_result}, precision: {precision}, recall: {recall}")
