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
from settings import FEATURE_RESULT_DIR, TEST_CASES_JSON_PATH, SCA_RESULTS_DIR


# @Time : 2023/11/22 15:49
# @Author : Liu Chengyue


class FeatureEvaluator:
    def __init__(self, extractor_name):
        # 从文件加载原始特征
        self.extractor_name = extractor_name
        self.feature_dir = os.path.join(FEATURE_RESULT_DIR, extractor_name)
        self.merged_feature_path = os.path.join(self.feature_dir, f"{self.__class__.__name__}.json")
        self.repo_features: List[RepoFeature] = self.init_repo_features()

        # 初始化id集合
        logger.info(f"init ids")
        self.repo_ids = set()
        self.repo_version_ids = set()
        for repo_feature in tqdm(self.repo_features, total=len(self.repo_features), desc="init ids"):
            self.repo_ids.add(repo_feature.repository.repo_id)
            self.repo_version_ids.add(f"{repo_feature.repository.repo_id}-{repo_feature.repository.version_id}")
        logger.info(f"init ids finished")

        # 特征数据统计
        self.repo_to_feature_statistic_result = {}
        self.feature_to_repo_statistic_result = {}

        # sca 测试用例
        self.test_case_file_name = ""
        self.test_cases: List[TestCase] = []
        self.test_threshold = 0

        # sca 结果
        self.sca_results = []

        # sca 检查结果
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

        # sca 评估结果
        self.sca_evaluate_result = {}

    def set_test_cases(self, test_case_file_name: str, test_cases: List[TestCase]):
        self.test_case_file_name = test_case_file_name
        self.test_cases = test_cases

    def set_test_threshold(self, threshold):
        self.test_threshold = threshold

    def clear(self):
        # sca 结果
        self.sca_results = []

        # sca 检查结果
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

        # sca 评估结果
        self.sca_evaluate_result = {}

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
        logger.debug(f"{sample_name} ---> {feature_name}")
        logger.debug(f"{sample_name}数量: {sample_num}")
        logger.debug(f"{feature_name}总计[未去重]: {sum_value}")
        logger.debug(f"{feature_name}均值: {mean_value}")
        logger.debug(f"{feature_name}最小值: {min_value}")
        logger.debug(f"{feature_name}最大值: {max_value}")
        logger.debug(f"{feature_name}第一四分位数 (Q1): {q1}")
        logger.debug(f"{feature_name}中位数: {median_value}")
        logger.debug(f"{feature_name}第三四分位数 (Q3): {q3}")
        logger.debug(f"{feature_name}第90分位数 (Q_90): {q_90}")

        def cal_percent(count):
            return f"{round((count / len(data) * 100), 2)}%"

        feature_num_sample_count = {}
        for specific_value in specific_values:
            # 特定值数量
            specific_value_count = len([d for d in data if d == specific_value])
            logger.debug(
                f"{specific_value_count}个{sample_name}包含{specific_value}个{feature_name}, 占比: {cal_percent(specific_value_count)}")
            feature_num_sample_count[specific_value] = {
                "sample_count": specific_value_count,
                "percent": cal_percent(specific_value_count)
            }
        statistic_result = {
            "sample_name": sample_name,
            "feature_name": feature_name,
            "sample_num": sample_num,
            "feature_sum_value": int(sum_value),
            "feature_mean_value": int(mean_value),
            "feature_min_value": int(min_value),
            "feature_max_value": int(max_value),
            "feature_values_q1": int(q1),
            "feature_values_q3": int(q3),
            "feature_values_q_90": int(q_90),
            "feature_num_sample_count": feature_num_sample_count,
        }
        logger.info(f"""statistics: 
        {json.dumps(statistic_result, indent=4)}
        """)
        return statistic_result

    def check(self, test_case,
              sca_results):
        # get ground truth
        ground_truth_repo_id = test_case.ground_truth_repo_id
        ground_truth_version_id = test_case.ground_truth_version_id

        repo_tp_flag = False
        version_tp_flag = False
        for sca_repo_id, sca_version_id, percent in sca_results:
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

    def sca_evaluate(self):
        # walk all binaries
        logger.info(f"start sca_evaluate, test_cases: {self.test_case_file_name}, threshold: {self.test_threshold}")

        # walk all feature
        for test_case in tqdm(self.test_cases,
                              total=len(self.test_cases),
                              desc=f"{self.__class__.__name__} sca_evaluate, "
                                   f"test_case: {self.test_case_file_name}, "
                                   f"threshold: {self.test_threshold}"):
            # sca【设定一个阈值，只要超过阈值的都返回。】
            current_sca_results = self.sca(test_case.file_strings)
            # check sca results【统计准确率】
            self.check(test_case, current_sca_results)
            self.sca_results.append({
                "test_case": test_case.custom_serialize(),
                "sca_results": [
                    {
                        "repo_id": result[0],
                        "version_id": result[1],
                        "match_percent": result[2],
                        "repo_level_sca_status": "TP" if result[0] == test_case.ground_truth_repo_id else "FP",
                        "version_level_sca_status": "TP" if result[1] == test_case.ground_truth_version_id else "FP"
                    }
                    for result in current_sca_results]
            })
        logger.info(f"sca_evaluate finished.")

        self.sca_summary()

    @abstractmethod
    def statistic(self):
        pass

    @abstractmethod
    def sca(self, file_path):
        pass

    def sca_summary(self):
        # 计算准确率
        repo_precision, repo_recall = self.cal_precision_and_recall(self.repo_sca_check_result)
        version_precision, version_recall = self.cal_precision_and_recall(self.version_sca_check_result)

        # 保存最终结果
        self.sca_evaluate_result = {
            "test_case_file_name": self.test_case_file_name,
            "test_case_file_num": len(self.test_cases),
            "test_case_threshold": self.test_threshold,
            "repo_level_sca_summary": {
                **self.repo_sca_check_result,
                "precision": repo_precision,
                "recall": repo_recall,
            },
            "version_level+sca_summary": {
                **self.version_sca_check_result,
                "precision": version_precision,
                "recall": version_recall,
            },
            "sca_details": self.sca_results
        }

        # 日志预览
        preview = {
            "test_case_file_name": self.test_case_file_name,
            "test_case_file_num": len(self.test_cases),
            "test_case_threshold": self.test_threshold,
            "repo_level_sca_summary": {
                **self.repo_sca_check_result,
                "precision": repo_precision,
                "recall": repo_recall,
            },
            "version_level+sca_summary": {
                **self.version_sca_check_result,
                "precision": version_precision,
                "recall": version_recall,
            },
        }
        logger.info(json.dumps(preview, indent=4))

    def dump_sca_result(self):
        result_file_name = f"{self.__class__.__name__}--{self.test_case_file_name}--({self.test_threshold}).json"
        result_file_path = os.path.join(SCA_RESULTS_DIR, result_file_name)
        logger.debug(f"dumping {result_file_path}")
        with open(result_file_path, 'w') as f:
            json.dump(self.sca_evaluate_result, f, ensure_ascii=False, indent=4)
        logger.debug(f"dumping {result_file_path} finished.")

    def dump_statistic_result(self):
        repo_to_feature_statistics_file_name = f"{self.__class__.__name__}--repo_to_feature_statistics.json"
        repo_to_feature_statistics_file_path = os.path.join(SCA_RESULTS_DIR, repo_to_feature_statistics_file_name)

        logger.debug(f"dumping {repo_to_feature_statistics_file_path}")
        with open(repo_to_feature_statistics_file_path, 'w') as f:
            json.dump(self.repo_to_feature_statistic_result, f, ensure_ascii=False, indent=4)
        logger.debug(f"dumping finished.")

        feature_to_repo_statistics_file_name = f"{self.__class__.__name__}--feature_to_repo_statistics.json"
        feature_to_repo_statistics_file_path = os.path.join(SCA_RESULTS_DIR, feature_to_repo_statistics_file_name)
        with open(feature_to_repo_statistics_file_path, 'w') as f:
            json.dump(self.feature_to_repo_statistic_result, f, ensure_ascii=False, indent=4)

        logger.debug(f"dumping finished.")
