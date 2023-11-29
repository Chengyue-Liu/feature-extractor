#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from abc import abstractmethod
from typing import List

import numpy as np

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

    def init_repo_features(self):
        repo_features = []
        for f in os.listdir(self.feature_dir):
            if f.endswith('.json'):
                f_path = os.path.join(self.feature_dir, f)
                repo_features.append(RepoFeature.init_repo_feature_from_json_file(f_path))
        return repo_features

    def statistic(self, data, data_desc):
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

        # 输出统计结果
        print(data_desc)
        print("均值:", mean_value)
        print("最小值:", min_value)
        print("最大值:", max_value)
        print("中位数:", median_value)
        print("第一四分位数 (Q1):", q1)
        print("第三四分位数 (Q3):", q3)
        print()

    @abstractmethod
    def evaluate(self):
        pass
