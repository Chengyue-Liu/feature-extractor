#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
from collections import Counter

from loguru import logger
from tqdm import tqdm

from feature_evaluation.entities import SrcStringFeature, SrcFunctionNameFeature
from feature_evaluation.feature_evaluator import FeatureEvaluator
from feature_extraction.bin_feature_extractors.bin_string_extractor import BinStringExtractor
from feature_extraction.src_feature_extractors.src_feature_tree_sitter_extractor import \
    SrcFeatureTreeSitterExtractor
from settings import SRC_STRING_SCA_THRESHOLD, SRC_FUNCTION_NAME_SCA_THRESHOLD
from utils.elf_utils import extract_elf_strings


# @Time : 2023/11/22 15:49
# @Author : Liu Chengyue


class SrcFunctionNameEvaluator(FeatureEvaluator):
    def __init__(self):
        logger.info(f"{self.__class__.__name__} initing...")
        # bin_string_features
        super().__init__(SrcFeatureTreeSitterExtractor.__name__)

        # 转换特征
        logger.info("convert feature")
        self.src_function_name_feature_dict = dict()
        for repo_feature in tqdm(self.repo_features, total=len(self.repo_features), desc="convert feature"):
            key = f"{repo_feature.repository.repo_id}-{repo_feature.repository.version_id}"
            if not self.src_function_name_feature_dict.get(key):
                self.src_function_name_feature_dict[key] = SrcFunctionNameFeature(repo_feature)
            else:
                self.src_function_name_feature_dict[key].function_names.update(
                    SrcFunctionNameFeature(repo_feature).function_names)

        # 特征计数
        logger.info("count feature")
        self.src_function_name_num_dict = {
            key: len(src_function_name_feature.function_names)
            for key, src_function_name_feature in self.src_function_name_feature_dict.items()
        }

        # 特征倒排索引表
        logger.info("倒排索引表")
        self.function_name_repo_dict = dict()
        self.function_name_repo_version_dict = dict()
        for repo_feature in tqdm(self.src_function_name_feature_dict.values(),
                                 total=len(self.src_function_name_feature_dict), desc="倒排索引表"):
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
        self.statistic_data(repo_function_name_nums, specific_values=[0, 1, 2, 3, 4, 5]
                            , sample_name="src_repo", feature_name="src_function_name")

        function_name_seen_repository_num_list = [len(v) for v in self.function_name_repo_dict.values()]
        self.statistic_data(function_name_seen_repository_num_list, specific_values=[1, 2, 3, 4, 5]
                            , sample_name="src_function_name", feature_name="src_repo")

        # sca 效果评估
        self.sca_evaluate(SRC_FUNCTION_NAME_SCA_THRESHOLD)

    def sca(self, file_path):
        # 文件名称
        file_name = os.path.split(file_path)[-1]

        # 提取二进制字符串
        strings = extract_elf_strings(file_path)

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
                # print(file_name, percent)

        return filtered_results

    def sca_summary(self, test_case_count, test_case_file_count, threshold):
        # basic summary
        logger.critical(f"repo_num: {len(self.repo_features)}, string_num: {len(self.function_name_repo_dict)}")
        logger.critical(f"testcase repo num:{test_case_count}, testcase file num:{test_case_file_count}")
        logger.critical(f"THRESHOLD: {threshold}")
        # repo
        precision, recall = self.cal_precision_and_recall(self.repo_sca_check_result)
        logger.critical(
            f"repo level sca result: {self.repo_sca_check_result}, precision: {precision}, recall: {recall}")
        # version
        precision, recall = self.cal_precision_and_recall(self.version_sca_check_result)
        logger.critical(
            f"repo level sca result: {self.version_sca_check_result}, precision: {precision}, recall: {recall}")
