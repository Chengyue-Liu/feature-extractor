#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from abc import abstractmethod
from typing import List

import numpy as np
from loguru import logger
from tqdm import tqdm

from feature_extraction.bin_feature_extractors.bin_string_extractor import BinStringExtractor
from feature_extraction.entities import RepoFeature
from settings import FEATURE_RESULT_DIR


# @Time : 2023/11/22 15:49
# @Author : Liu Chengyue


class FeatureEvaluator:
    def __init__(self, extractor_name):
        # feature json dir
        self.feature_dir = os.path.join(FEATURE_RESULT_DIR, extractor_name)

        # repo features
        self.repo_features: List[RepoFeature] = self.init_repo_features()

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

    def init_repo_features(self):
        logger.info(f"init_repo_features...")
        repo_features = []
        feature_files = os.listdir(self.feature_dir)
        for f in tqdm(feature_files, total=len(feature_files), desc="init_repo_features"):
            if f.endswith('.json'):
                f_path = os.path.join(self.feature_dir, f)
                repo_features.append(RepoFeature.init_repo_feature_from_json_file(f_path))
        return repo_features

    def statistic(self, data: List[int], specific_values, data_desc="statistics"):
        if not data_desc:
            data_desc = "statistic_in_repo_view"
        # 计算均值
        mean_value = np.mean(data)

        # 计算最小值
        min_value = np.min(data)

        # 计算最大值
        max_value = np.max(data)

        # 计算中位数
        median_value = np.median(data)

        # 计算四分位数
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        q_90 = np.percentile(data, 90)

        # 输出统计结果
        logger.critical(data_desc)
        logger.critical(f"均值: {mean_value}")
        logger.critical(f"最小值: {min_value}")
        logger.critical(f"最大值: {max_value}")
        logger.critical(f"第一四分位数 (Q1): {q1}")
        logger.critical(f"中位数: {median_value}")
        logger.critical(f"第三四分位数 (Q3): {q3}")
        logger.critical(f"第90分位数 (Q_90): {q_90}")

        def cal_percent(count):
            return f"{round((count / len(data) * 100), 2)}%"

        for specific_value in specific_values:
            # 特定值数量
            specific_value_count = len([d for d in data if d == specific_value])
            logger.critical(
                f"{specific_value} count: {specific_value_count}, percent: {cal_percent(specific_value_count)}")

    def check(self, ground_truth_repo_id,
              ground_truth_version_id,
              sca_results):
        repo_tp_flag = False
        version_tp_flag = False
        for sca_repo_id, sca_version_id in sca_results:
            if ground_truth_repo_id == sca_repo_id:
                self.repo_sca_check_result["tp"] += 1
                repo_tp_flag = True
                if ground_truth_version_id == sca_version_id:
                    self.version_sca_check_result["tp"] += 1
                    version_tp_flag = True
                else:
                    self.version_sca_check_result["fp"] += 1
            else:
                self.repo_sca_check_result["fp"] += 1
                self.version_sca_check_result["fp"] += 1

        if not repo_tp_flag:
            self.repo_sca_check_result["fn"] += 1
        if not version_tp_flag:
            self.version_sca_check_result["fn"] += 1

    def cal_precision_and_recall(self, sca_check_result):
        precision = sca_check_result['tp'] / (sca_check_result['tp'] + sca_check_result['fp'])
        recall = sca_check_result['tp'] / (sca_check_result['tp'] + sca_check_result['fn'])
        return precision, recall

    @abstractmethod
    def evaluate(self):
        pass
