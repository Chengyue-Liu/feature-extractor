#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from collections import Counter

from tqdm import tqdm
from loguru import logger

from feature_evaluation.entities import SrcStringFeature
from feature_evaluation.feature_evaluator import FeatureEvaluator
from feature_extraction.bin_feature_extractors.bin_string_extractor import BinStringExtractor
from feature_extraction.src_feature_extractors.src_string_and_funtion_name_extractor import \
    SrcStringAndFunctionNameExtractor
from settings import SRC_STRING_SCA_THRESHOLD
from utils.elf_utils import extract_elf_strings


# @Time : 2023/11/22 15:49
# @Author : Liu Chengyue


class SrcStringEvaluator(FeatureEvaluator):
    def __init__(self):
        logger.info(f"{self.__class__.__name__} initing...")
        # bin_string_features
        super().__init__(SrcStringAndFunctionNameExtractor.__name__)

        # 转换特征
        logger.info(f"convert feature")
        self.src_string_feature_dict = dict()
        for repo_feature in tqdm(self.repo_features, total=len(self.repo_features), desc="convert feature"):
            key = f"{repo_feature.repository.repo_id}-{repo_feature.repository.version_id}"
            if not self.src_string_feature_dict.get(key):
                self.src_string_feature_dict[key] = SrcStringFeature(repo_feature)
            else:
                self.src_string_feature_dict[key].strings.update(SrcStringFeature(repo_feature).strings)

        # 特征计数
        logger.info(f"count feature")
        self.src_string_num_dict = {
            key: len(src_string_feature.strings)
            for key, src_string_feature in self.src_string_feature_dict.items()
        }

        # 特征倒排索引表
        logger.info(f"特征倒排索引表")
        self.string_repo_dict = dict()
        self.string_repo_version_dict = dict()
        for repo_feature in tqdm(self.src_string_feature_dict.values(),
                                 total=len(self.src_string_feature_dict),
                                 desc="特征倒排索引表"):
            repo_id = repo_feature.repository.repo_id
            version_id = repo_feature.repository.version_id
            for string in repo_feature.strings:
                if not (repo_id_set := self.string_repo_dict.get(string)):
                    self.string_repo_dict[string] = repo_id_set = set()
                repo_id_set.add(repo_id)

                if not (repo_version_id_set := self.string_repo_version_dict.get(string)):
                    self.string_repo_version_dict[string] = repo_version_id_set = set()
                repo_version_id_set.add((repo_id, version_id))
        logger.info(f"{self.__class__.__name__} inited...")

    def evaluate(self):
        # 分布统计
        logger.info(f"generate repo_string_nums")
        repo_string_nums = [len(repo_feature.strings) for repo_feature in self.src_string_feature_dict.values()]
        self.statistic(repo_string_nums, "statistic_in_repo_view")

        logger.info(f"generate string_seen_repository_num_list")
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
            # 确认匹配结果
            if percent > SRC_STRING_SCA_THRESHOLD:
                filtered_results.append((repo_id, version_id))
                # 预览扫描结果
                print(file_name, percent)

        return filtered_results

    def sca_evaluate(self):
        # walk all binaries
        logger.info(f"init testcases")
        fe = FeatureEvaluator(BinStringExtractor.__name__)
        logger.info(f"start sca_evaluate")
        # walk all feature
        for repo_feature in tqdm(fe.repo_features, total=len(fe.repo_features), desc="sca_evaluate"):
            # get ground truth
            ground_truth_repo_id = repo_feature.repository.repo_id
            ground_truth_version_id = repo_feature.repository.repo_id

            # sca
            for file_feature in repo_feature.file_features:
                # sca【设定一个阈值，只要超过阈值的都返回。】
                sca_results = self.sca(file_feature.file_path)

                # check sca results【统计准确率】
                self.check(ground_truth_repo_id, ground_truth_version_id, sca_results)
        logger.info(f"sca_evaluate finished.")
        logger.critical(f"SRC_STRING_SCA_THRESHOLD: {SRC_STRING_SCA_THRESHOLD}")

        precision, recall = self.cal_precision_and_recall(self.repo_sca_check_result)
        logger.critical(f"repo level sca result: {self.repo_sca_check_result}, precision: {precision}, recall: {recall}")

        precision, recall = self.cal_precision_and_recall(self.version_sca_check_result)
        logger.critical(f"repo level sca result: {self.repo_sca_check_result}, precision: {precision}, recall: {recall}")
