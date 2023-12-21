#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from collections import Counter

from loguru import logger
from tqdm import tqdm

from feature_evaluation.entities import BinStringFeature
from feature_evaluation.feature_evaluator import FeatureEvaluator
from feature_extraction.bin_feature_extractors.bin_string_extractor import BinStringExtractor
from settings import BIN_STRING_SCA_THRESHOLD, TEST_CASES_JSON_PATH
from utils.elf_utils import extract_elf_strings


# @Time : 2023/11/22 15:49
# @Author : Liu Chengyue


class BinStringEvaluator(FeatureEvaluator):
    def __init__(self):
        logger.info(f"{self.__class__.__name__} initing...")
        # bin_string_features
        super().__init__(BinStringExtractor.__name__)

        # 转换特征
        logger.info("convert feature")
        self.bin_string_feature_dict = dict()
        for repo_feature in tqdm(self.repo_features, total=len(self.repo_features), desc="convert feature"):
            key = f"{repo_feature.repository.repo_id}-{repo_feature.repository.version_id}"
            if not self.bin_string_feature_dict.get(repo_feature.repository.version_key):
                self.bin_string_feature_dict[key] = BinStringFeature(repo_feature)
            else:
                self.bin_string_feature_dict[key].strings.update(BinStringFeature(repo_feature).strings)

        # 计数
        logger.info("count feature")
        self.bin_string_num_dict = {
            key: len(strings.strings)
            for key, strings in self.bin_string_feature_dict.items()
        }

        # string ---> bins
        logger.info("倒排索引表")
        self.string_repo_dict = dict()
        self.string_repo_version_dict = dict()
        for repo_feature in tqdm(self.bin_string_feature_dict.values(), total=len(self.bin_string_feature_dict),
                                 desc="倒排索引表"):
            repo_id = repo_feature.repository.repo_id
            version_id = repo_feature.repository.version_id
            for string in repo_feature.strings:
                if not (repo_id_set := self.string_repo_dict.get(string)):
                    self.string_repo_dict[string] = repo_id_set = set()
                repo_id_set.add(repo_id)

                if not (repo_version_id_set := self.string_repo_version_dict.get(string)):
                    self.string_repo_version_dict[string] = repo_version_id_set = set()
                repo_version_id_set.add((repo_id, version_id))
        logger.info(f"{self.__class__.__name__} inited")

    def statistic(self):
        # 分布统计
        logger.info(f"src repo ---> bin strings")
        repo_string_nums = [len(repo_feature.strings) for repo_feature in self.bin_string_feature_dict.values()]
        self.repo_to_feature_statistic_result = self.statistic_data(repo_string_nums,
                                                                    specific_values=[0, 1, 2, 3, 4, 5],
                                                                    sample_name="bin_repo",
                                                                    feature_name="bin_string")

        logger.info(f"bin strings ---> src repo")
        string_seen_repository_num_list = [len(v) for v in self.string_repo_dict.values()]
        self.feature_to_repo_statistic_result = self.statistic_data(string_seen_repository_num_list,
                                                                    specific_values=[1, 2, 3, 4, 5],
                                                                    sample_name="bin_string",
                                                                    feature_name="bin_repo")

    def sca(self, strings):
        # 根据字符串查询对应的library_id, version_id
        string_repo_id_version_id_tuple_list = []
        for string in strings:
            string_repo_id_version_id_tuple_list.extend(self.string_repo_version_dict.get(string, []))

        # 统计每个版本匹配的数量
        counter = Counter(string_repo_id_version_id_tuple_list)
        all_results = counter.most_common(20)  # (repo_id, version_id), count

        # 筛选
        final_result = None
        max_percent = BIN_STRING_SCA_THRESHOLD
        for (repo_id, version_id), count in all_results:
            key = f"{repo_id}-{version_id}"
            string_num = self.bin_string_num_dict.get(key)
            percent = round(count / string_num, 2)
            if percent > BIN_STRING_SCA_THRESHOLD:
                if percent > max_percent:
                    final_result = (repo_id, version_id, percent)

                # 拼成一个列表，为了以后报出多个结果做准备
            sca_results = [final_result, ] if final_result else []
            return sca_results
