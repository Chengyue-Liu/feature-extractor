#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
from collections import Counter

from loguru import logger

from feature_evaluation.entities import SrcStringFeature, SrcFunctionNameFeature
from feature_evaluation.feature_evaluator import FeatureEvaluator
from feature_extraction.bin_feature_extractors.bin_string_extractor import BinStringExtractor
from feature_extraction.src_feature_extractors.src_string_and_funtion_name_extractor import \
    SrcStringAndFunctionNameExtractor
from settings import SRC_STRING_SCA_THRESHOLD, SRC_FUNCTION_NAME_SCA_THRESHOLD
from utils.elf_utils import extract_elf_strings


# @Time : 2023/11/22 15:49
# @Author : Liu Chengyue


class SrcFunctionNameEvaluator(FeatureEvaluator):
    def __init__(self):
        logger.info(f"{self.__class__.__name__} initing...")
        # bin_string_features
        super().__init__(SrcStringAndFunctionNameExtractor.__name__)

        # 转换特征
        self.src_function_name_feature_dict = dict()
        for repo_feature in self.repo_features:
            key = f"{repo_feature.repository.repo_id}-{repo_feature.repository.version_id}"
            if not self.src_function_name_feature_dict.get(key):
                self.src_function_name_feature_dict[key] = SrcFunctionNameFeature(repo_feature)
            else:
                self.src_function_name_feature_dict[key].function_names.update(
                    SrcFunctionNameFeature(repo_feature).function_names)

        # 特征计数
        self.src_function_name_num_dict = {
            key: len(src_function_name_feature.function_names)
            for key, src_function_name_feature in self.src_function_name_feature_dict.items()
        }

        # 特征倒排索引表
        self.function_name_repo_dict = dict()
        self.function_name_repo_version_dict = dict()
        for repo_feature in self.src_function_name_feature_dict.values():
            repo_id = repo_feature.repository.repo_id
            version_id = repo_feature.repository.version_id
            for function_name in repo_feature.function_names:
                if not (repo_id_set := self.function_name_repo_dict.get(function_name)):
                    self.function_name_repo_dict[function_name] = repo_id_set = set()
                repo_id_set.add(repo_id)

                if not (repo_version_id_set := self.function_name_repo_version_dict.get(function_name)):
                    self.function_name_repo_version_dict[function_name] = repo_version_id_set = set()
                repo_version_id_set.add((repo_id, version_id))
        logger.info(f"{self.__class__.__name__} inited...")

    def evaluate(self):
        # 分布统计
        repo_function_name_nums = [len(repo_feature.function_names) for repo_feature in
                                   self.src_function_name_feature_dict.values()]
        self.statistic(repo_function_name_nums, specific_values=[0, 1, 2, 3, 4, 5], data_desc="statistic_in_repo_view")

        function_name_seen_repository_num_list = [len(v) for v in self.function_name_repo_dict.values()]
        self.statistic(function_name_seen_repository_num_list, specific_values=[ 1, 2, 3, 4, 5],
                       data_desc="statistic_in_string_view")

        # sca 效果评估
        self.sca_evaluate()

    def sca(self, file_path):
        # 文件名称
        file_name = os.path.split(file_path)[-1]

        # 提取二进制字符串
        strings = extract_elf_strings(file_path)
        with open(f"{os.path.split(file_path)[-1]}.json", 'w') as f:
            json.dump(strings, f)
        # 根据字符串查询对应的library_id, version_id
        string_repo_id_version_id_tuple_list = []
        count = 0
        for string in strings:
            if string in self.function_name_repo_version_dict:
                # print(string)
                count += 1
            string_repo_id_version_id_tuple_list.extend(self.function_name_repo_version_dict.get(string, []))
        # print(os.path.split(file_path)[-1], count, len(self.function_name_repo_version_dict))
        # 统计每个版本匹配的数量
        counter = Counter(string_repo_id_version_id_tuple_list)
        all_results = counter.most_common(20)  # (repo_id, version_id), count

        # 筛选
        filtered_results = []
        for (repo_id, version_id), count in all_results:
            key = f"{repo_id}-{version_id}"
            string_num = self.src_function_name_num_dict.get(key)
            percent = round(count / string_num, 2)
            if percent > SRC_FUNCTION_NAME_SCA_THRESHOLD:
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

        precision, recall = self.cal_precision_and_recall(self.repo_sca_check_result)
        print(f"repo level sca result: {self.repo_sca_check_result}, precision: {precision}, recall: {recall}")

        precision, recall = self.cal_precision_and_recall(self.version_sca_check_result)
        print(f"repo level sca result: {self.repo_sca_check_result}, precision: {precision}, recall: {recall}")
