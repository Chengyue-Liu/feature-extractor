#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os.path
import pickle
import sys

from loguru import logger
from tqdm import tqdm

from feature_evaluation.bin_feature_evaluators.bin_string_evaluator import BinStringEvaluator
from feature_evaluation.entities import TestCase
from feature_evaluation.feature_evaluator import FeatureEvaluator
from feature_evaluation.src_feature_evaluators.src_function_name_evaluator import SrcFunctionNameEvaluator
from feature_evaluation.src_feature_evaluators.src_string_evaluator import SrcStringEvaluator
from settings import SRC_STRING_SCA_THRESHOLD, TEST_CASES_JSON_PATH, TEST_CASES_10000_JSON_PATH, \
    TEST_CASES_1000_JSON_PATH, TEST_CASES_100_JSON_PATH, SRC_FUNCTION_NAME_SCA_THRESHOLD, BIN_STRING_SCA_THRESHOLD, \
    FEATURE_RESULT_DIR


# @Time : 2023/11/3 12:06
# @Author : Liu Chengyue
# @File : extractor_runner.py
# @Software: PyCharm


def merge_repo_features(root_feature_dir=FEATURE_RESULT_DIR):
    for feature_dir in os.listdir(root_feature_dir):
        feature_dir_path = os.path.join(root_feature_dir, feature_dir)
        logger.info(f"merge repo features...")
        repo_features = []
        feature_files = os.listdir(feature_dir_path)
        for f in tqdm(feature_files, total=len(feature_files), desc="merge repo features"):
            if f.endswith('.json') and str(f[0]).isdigit():  # 不读取合并的特征
                f_path = os.path.join(feature_dir_path, f)
                with open(f_path) as f:
                    repo_feature = json.load(f)
                    repo_features.append(repo_feature)
        merged_repo_feature_file_path = os.path.join(feature_dir_path, "merged_feature.pkl")

        logger.info(f"dumping... {merged_repo_feature_file_path}")
        with open(merged_repo_feature_file_path, 'wb') as f:
            pickle.dump(repo_features, f)
        logger.info(f"dumping... {merged_repo_feature_file_path} finished.")

    logger.info(f"merge repo features finished.")


def run_evaluator(evaluator: FeatureEvaluator, test_case_file_name, test_cases, threshold):
    # 设置测试用例
    evaluator.set_test_cases(test_case_file_name, test_cases)
    # 设置测试阈值
    evaluator.set_test_threshold(threshold)
    # sca 测试
    evaluator.sca_evaluate()
    # 保存结果
    evaluator.dump_sca_result()
    # 清理缓存
    evaluator.clear()


def main():
    # 初始化evaluator
    logger.info(f"init evaluators")
    src_string_evaluator = SrcStringEvaluator()
    src_function_name_evaluator = SrcFunctionNameEvaluator()
    bin_string_evaluator = BinStringEvaluator()

    # 特征数据统计
    logger.info(f"statistics")
    src_string_evaluator.statistic()
    src_string_evaluator.dump_statistic_result()

    src_function_name_evaluator.statistic()
    src_function_name_evaluator.dump_statistic_result()

    bin_string_evaluator.statistic()
    bin_string_evaluator.dump_statistic_result()

    # sca 评估
    for test_case_json_path in [TEST_CASES_100_JSON_PATH, TEST_CASES_1000_JSON_PATH, TEST_CASES_10000_JSON_PATH]:
        test_case_file_name = os.path.basename(test_case_json_path)
        logger.info(f"init testcases: {test_case_file_name}")
        test_cases = TestCase.get_test_cases(test_case_json_path)

        logger.info(
            f"run_src_string_evaluator, testcases: {test_case_file_name}, threshold: {SRC_STRING_SCA_THRESHOLD}")
        run_evaluator(src_string_evaluator, test_case_file_name, test_cases, SRC_STRING_SCA_THRESHOLD)

        logger.info(
            f"run_src_function_name_evaluator, testcases: {test_case_file_name}, threshold: {SRC_FUNCTION_NAME_SCA_THRESHOLD}")
        run_evaluator(src_function_name_evaluator, test_case_file_name, test_cases, SRC_FUNCTION_NAME_SCA_THRESHOLD)

        logger.info(
            f"run_bin_string_evaluator, testcases: {test_case_file_name}, threshold: {BIN_STRING_SCA_THRESHOLD}")
        run_evaluator(bin_string_evaluator, test_case_file_name, test_cases, BIN_STRING_SCA_THRESHOLD)

    logger.success(f"{test_case_file_name} all finished.")

    # 常用命令
    # nohup python feature_evaluator_runner.py &
    # ps aux | grep "python feature_evaluator_runner.py" | grep -v grep | awk '{print $2}' | xargs kill

    # 100, 1000, 10000


if __name__ == '__main__':
    logger.remove()
    logger.add(level="INFO", sink=sys.stdout)
    main()
    # merge_repo_features()
# todo
"""
1. 后续其他的特征，一定要存到postgres中。存在文件中，每次读取太慢了。

"""
