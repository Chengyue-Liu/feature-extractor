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
from settings import SRC_STRING_SCA_THRESHOLD, SRC_FUNCTION_NAME_SCA_THRESHOLD, TEST_CASES_JSON_PATH
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

    def statistic(self):
        # 分布统计
        logger.info(f"src repo ---> function names")
        repo_function_name_nums = [len(repo_feature.function_names) for repo_feature in
                                   self.src_function_name_feature_dict.values()]
        self.repo_to_feature_statistic_result = self.statistic_data(repo_function_name_nums,
                                                                    specific_values=[0, 1, 2, 3, 4, 5]
                                                                    , sample_name="src_repo",
                                                                    feature_name="src_function_name")

        logger.info(f"src function names ---> repo")
        function_name_seen_repository_num_list = [len(v) for v in self.function_name_repo_dict.values()]
        self.feature_to_repo_statistic_result = self.statistic_data(function_name_seen_repository_num_list,
                                                                    specific_values=[1, 2, 3, 4, 5]
                                                                    , sample_name="src_function_name",
                                                                    feature_name="src_repo")

    def sca(self, strings):

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
        final_result = None
        max_percent = SRC_FUNCTION_NAME_SCA_THRESHOLD
        for (repo_id, version_id), count in all_results:
            key = f"{repo_id}-{version_id}"
            string_num = self.src_function_name_num_dict.get(key)
            percent = round(count / string_num, 2)
            if percent > SRC_FUNCTION_NAME_SCA_THRESHOLD:
                if percent > max_percent:
                    final_result = (repo_id, version_id, percent)

                # 拼成一个列表，为了以后报出多个结果做准备
        sca_results = [final_result, ] if final_result else []
        return sca_results
