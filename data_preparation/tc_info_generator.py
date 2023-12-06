#!/usr/bin/env python
# -*- coding: utf-8 -*-
import collections
import json
import random

from loguru import logger

from settings import BIN_REPOS_JSON, SRC_REPOS_JSON, TEST_CASES_JSON_PATH, TEST_CASE_SAMPLE_SIZE_PER_REPO


# @Time : 2023/12/6 18:46
# @Author : Liu Chengyue


def generate_tc_information():
    # 加载源码信息
    src_repo_ids = load_src_repo_info()

    # 加载二进制信息
    bin_repo_test_cases_dict = load_bin_repo_info(src_repo_ids)

    # 筛选
    filter_test_cases(bin_repo_test_cases_dict)

    # 保存
    with open(TEST_CASES_JSON_PATH, 'w') as f:
        json.dump(bin_repo_test_cases_dict, f, ensure_ascii=False)


def filter_test_cases(bin_repo_test_cases_dict):
    bin_repo_test_case_num = 0
    bin_file_test_case_num = 0
    for repo_id, repos in bin_repo_test_cases_dict.items():
        if len(test_cases := bin_repo_test_cases_dict[repo_id]) > TEST_CASE_SAMPLE_SIZE_PER_REPO:
            test_cases = random.sample(repos, TEST_CASE_SAMPLE_SIZE_PER_REPO)
        bin_repo_test_case_num += len(test_cases)
        for test_case in test_cases:
            bin_file_test_case_num += len(test_case["elf_paths"])
    logger.info(
        f"TEST_CASE_SAMPLE_SIZE_PER_REPO: {TEST_CASE_SAMPLE_SIZE_PER_REPO}\n"
        f"tc repo num: {len(bin_repo_test_cases_dict)}\n"
        f"tc repo version num: {bin_repo_test_case_num}\n"
        f"tc file num: {bin_file_test_case_num}\n")


def load_bin_repo_info(src_repo_ids):
    bin_repo_num = 0
    bin_with_src_repo_num = 0
    bin_repo_test_cases_dict = collections.defaultdict(list)  # repo_id: repos
    with open(BIN_REPOS_JSON) as f:
        bin_repos = json.load(f)
        all_bin_repo_num = len(bin_repos)
        for bin_repo in bin_repos:
            if not bin_repo["elf_paths"]:
                continue
            bin_repo_num += 1
            repo_id = bin_repo["repo_id"]
            if repo_id in src_repo_ids:
                bin_repo_test_cases_dict[repo_id].append(bin_repo)
                bin_with_src_repo_num += 1
    logger.info(f"all bin package num: {all_bin_repo_num}\n"
                f"bin package with elf repo num: {bin_repo_num}\n"
                f"bin package with elf with src repo num: {bin_with_src_repo_num}\n")
    return bin_repo_test_cases_dict


def load_src_repo_info():
    src_repo_ids = set()
    src_repo_version_ids = set()
    with open(SRC_REPOS_JSON) as f:
        src_repos = json.load(f)
        all_src_repo_num = len(src_repos)
        for src_repo in src_repos:
            target_src_file_num = src_repo["target_src_file_num"]
            if not target_src_file_num:
                continue
            repo_id = src_repo["repo_id"]
            src_repo_ids.add(repo_id)
            version_id = src_repo["version_id"]
            version_key = f"{repo_id}-{version_id}"
            src_repo_version_ids.add(version_key)
    logger.info(f"all_src_repo_num: {all_src_repo_num}\n"
                f"src repo with target file num: {len(src_repo_ids)}\n"
                f"src repo version with target file num: {len(src_repo_version_ids)}\n")
    return src_repo_ids
