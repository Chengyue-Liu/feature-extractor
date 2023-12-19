#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
from abc import abstractmethod
from typing import List

import numpy as np
from loguru import logger
from tqdm import tqdm

from feature_evaluation.entities import TestCase
from feature_extraction.entities import RepoFeature
from settings import FEATURE_RESULT_DIR


# @Time : 2023/11/22 15:49
# @Author : Liu Chengyue


class FeatureEvaluator:
    def __init__(self, extractor_name):
        # feature json dir
        self.extractor_name = extractor_name
        self.feature_dir = os.path.join(FEATURE_RESULT_DIR, extractor_name)
        self.merged_feature_path = os.path.join(self.feature_dir, f"{self.__class__.__name__}.json")

        # repo features
        self.repo_features: List[RepoFeature] = self.init_repo_features()

        # 初始化id集合
        logger.info(f"init ids")
        self.repo_ids = set()
        self.repo_version_ids = set()
        for repo_feature in tqdm(self.repo_features, total=len(self.repo_features), desc="init ids"):
            self.repo_ids.add(repo_feature.repository.repo_id)
            self.repo_version_ids.add(f"{repo_feature.repository.repo_id}-{repo_feature.repository.version_id}")

        logger.info(f"init ids finished")
        # result
        self.repo_sca_check_result = {
            "tp": 0,
            "fp": 0,
            "fn": 0,
            "tn": 0
        }
        self.version_sca_check_result = {
            "tp": 0,
            "fp": 0,
            "fn": 0,
            "tn": 0
        }

        self.evaluate_result = {}

    def merge_features(self):
        # todo 把所有的特征合并掉，方便加载
        logger.info(f"dump merged feature to {self.merged_feature_path}")
        data = [repo_feature.custom_serialize() for repo_feature in self.repo_features]
        with open(self.merged_feature_path, 'w') as f:
            json.dump(data, f, ensure_ascii=False)
        logger.info(f"dump finished.")

    def init_repo_features(self):
        """
        从文件初始化特征
        :return:
        """
        # 如果有合并的，就直接用合并的
        logger.info(f"init_repo_features...")
        repo_features = []
        feature_files = os.listdir(self.feature_dir)
        for f in tqdm(feature_files, total=len(feature_files), desc="init_repo_features"):
            if f.endswith('.json') and str(f[0]).isdigit():  # 不读取合并的特征
                f_path = os.path.join(self.feature_dir, f)
                repo_features.append(RepoFeature.init_repo_feature_from_json_file(f_path))
        logger.info(f"init_repo_features finished.")
        return repo_features

    def statistic_data(self, data: List[int], specific_values, sample_name="库", feature_name="特征"):
        sample_num = len(data)
        sum_value = sum(data)

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
        logger.critical(f"{sample_name} ---> {feature_name}")
        logger.critical(f"{sample_name}数量: {sample_num}")
        logger.critical(f"{feature_name}总计[未去重]: {sum_value}")
        logger.critical(f"{feature_name}均值: {mean_value}")
        logger.critical(f"{feature_name}最小值: {min_value}")
        logger.critical(f"{feature_name}最大值: {max_value}")
        logger.critical(f"{feature_name}第一四分位数 (Q1): {q1}")
        logger.critical(f"{feature_name}中位数: {median_value}")
        logger.critical(f"{feature_name}第三四分位数 (Q3): {q3}")
        logger.critical(f"{feature_name}第90分位数 (Q_90): {q_90}")

        def cal_percent(count):
            return f"{round((count / len(data) * 100), 2)}%"

        special_value_dict = {}
        for specific_value in specific_values:
            # 特定值数量
            specific_value_count = len([d for d in data if d == specific_value])
            logger.critical(
                f"{specific_value_count}个{sample_name}包含{specific_value}个{feature_name}, 占比: {cal_percent(specific_value_count)}")
            special_value_dict[specific_value] = {
                "count": specific_value_count,
                "percent": cal_percent(specific_value_count)
            }
        self.evaluate_result["data_desc"] = {
            "sample_name": sample_name,
            "feature_name": feature_name,
            "sample_num": sample_num,
            "sum_value": sum_value,
            "mean_value": mean_value,
            "min_value": min_value,
            "max_value": max_value,
            "q1": q1,
            "q3": q3,
            "q_90": q_90,
            "specific_values": special_value_dict,
        }

    def check(self, test_case,
              sca_results):
        # get ground truth
        ground_truth_repo_id = test_case.ground_truth_repo_id
        ground_truth_version_id = test_case.ground_truth_version_id

        repo_tp_flag = False
        version_tp_flag = False
        for sca_repo_id, sca_version_id in sca_results:
            if ground_truth_repo_id == sca_repo_id:
                self.repo_sca_check_result["tp"] += 1
                # print(ground_truth_repo_id)
                repo_tp_flag = True
                if ground_truth_version_id == sca_version_id:
                    self.version_sca_check_result["tp"] += 1
                    version_tp_flag = True
                else:
                    self.version_sca_check_result["fp"] += 1
            else:
                self.repo_sca_check_result["fp"] += 1
                self.version_sca_check_result["fp"] += 1

        # 存在但是没有找到
        if not repo_tp_flag:
            if ground_truth_repo_id in self.repo_ids:
                self.repo_sca_check_result["fn"] += 1
            else:
                self.repo_sca_check_result["tn"] += 1

        # 版本级别
        if not version_tp_flag:
            if f"{ground_truth_repo_id}-{ground_truth_version_id}" in self.repo_version_ids:
                self.version_sca_check_result["fn"] += 1
            else:
                self.version_sca_check_result["tn"] += 1

    def cal_precision_and_recall(self, sca_check_result):
        if (all_num := (sca_check_result['tp'] + sca_check_result['fp'])) != 0:
            precision = sca_check_result['tp'] / all_num
        else:
            precision = 0
        if (all_num := (sca_check_result['tp'] + sca_check_result['fn'])) != 0:
            recall = sca_check_result['tp'] / all_num
        else:
            recall = 0
        return round(precision, 2), round(recall, 2)

    def sca_evaluate(self, test_cases, threshold):
        # walk all binaries
        test_case_file_count = 0
        logger.info(f"start sca_evaluate")
        # walk all feature
        for test_case in tqdm(test_cases, total=len(test_cases), desc="sca_evaluate"):
            test_case: TestCase
            test_case_file_count += len(test_case.file_paths)
            for file_path in test_case.file_paths:
                # sca【设定一个阈值，只要超过阈值的都返回。】
                sca_results = self.sca(file_path)
                # check sca results【统计准确率】
                self.check(test_case, sca_results)
        logger.info(f"sca_evaluate finished.")

        self.sca_summary(len(test_cases), test_case_file_count, threshold)

    @abstractmethod
    def sca(self, file_path):
        pass

    @abstractmethod
    def sca_summary(self, test_case_count, test_case_file_count, threshold):
        pass
