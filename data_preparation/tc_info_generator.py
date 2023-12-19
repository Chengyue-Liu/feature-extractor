#!/usr/bin/env python
# -*- coding: utf-8 -*-
import collections
import json
import random

from loguru import logger

from settings import BIN_REPOS_JSON, SRC_REPOS_JSON, \
    TC_BIN_REPOS_JSON, TEST_CASES_100_JSON_PATH, TEST_CASES_1000_JSON_PATH, TEST_CASES_10000_JSON_PATH


# @Time : 2023/12/6 18:46
# @Author : Liu Chengyue


def generate_tc_information():
    tc_summary = {}
    # 加载源码信息
    src_repo_ids = load_src_repo_info(tc_summary)

    # 加载二进制信息
    bin_repo_test_cases_dict = load_bin_repo_info(src_repo_ids, tc_summary)

    # 版本过滤【只保留最新，最旧和中间的一个版本】
    tc_100, tc_1000, tc_10000 = filter_test_cases(bin_repo_test_cases_dict)

    with open(TEST_CASES_100_JSON_PATH, 'w') as f:
        json.dump(tc_100, f, ensure_ascii=False)

    with open(TEST_CASES_1000_JSON_PATH, 'w') as f:
        json.dump(tc_1000, f, ensure_ascii=False)

    with open(TEST_CASES_10000_JSON_PATH, 'w') as f:
        json.dump(tc_10000, f, ensure_ascii=False)


def filter_test_cases(bin_repo_test_cases_dict):
    # 先筛选100个库，然后随机选择其中的1个版本
    tc_100_repo_ids = random.sample(list(bin_repo_test_cases_dict.keys()), 100)
    tc_100_repos = [random.sample(bin_repo_test_cases_dict[repo_id], 1)[0] for repo_id in tc_100_repo_ids]

    tc_1000_repo_ids = random.sample(list(bin_repo_test_cases_dict.keys()), 1000)
    tc_1000_repos = [random.sample(bin_repo_test_cases_dict[repo_id], 1)[0] for repo_id in tc_1000_repo_ids]

    tc_10000_repo_ids = random.sample(list(bin_repo_test_cases_dict.keys()), 10000)
    tc_10000_repos = [random.sample(bin_repo_test_cases_dict[repo_id], 1)[0] for repo_id in tc_10000_repo_ids]

    def count_elf_num(repos):
        count = 0
        for repo in repos:
            count += len(repo["elf_paths"])
        logger.info(f"elf_num: {count}")

    count_elf_num(tc_100_repos)
    count_elf_num(tc_1000_repos)
    count_elf_num(tc_10000_repos)

    return tc_100_repos, tc_1000_repos, tc_10000_repos


def load_bin_repo_info(src_repo_ids, tc_summary):
    bin_repo_test_cases_dict = collections.defaultdict(list)  # repo_id: repos

    with open(BIN_REPOS_JSON) as f:
        repo_id_set = set()
        repo_version_id_set = set()
        bin_repos = json.load(f)
        for bin_repo in bin_repos:
            repo_id = bin_repo["repo_id"]
            if repo_id not in src_repo_ids:
                continue
            repo_id_set.add(repo_id)
            version_id = bin_repo["version_id"]
            version_key = f"{repo_id}-{version_id}"
            repo_version_id_set.add(version_key)
            bin_repo_test_cases_dict[repo_id].append(bin_repo)
    bin_repo_num = len(repo_id_set)
    repo_version_num = len(repo_version_id_set)
    different_bin_repo_num = len(bin_repos)
    logger.info(f"\nbin_repo_num: {bin_repo_num}\n"
                f"repo_version_num: {repo_version_num}\n"
                f"different_bin_repo_num: {different_bin_repo_num}\n")

    tc_summary["bin_repo_num"] = bin_repo_num
    tc_summary["repo_version_num"] = repo_version_num
    tc_summary["different_bin_repo_num"] = different_bin_repo_num
    return bin_repo_test_cases_dict


def load_src_repo_info(tc_summary):
    src_repo_ids = set()
    src_repo_version_ids = set()
    with open(SRC_REPOS_JSON) as f:
        src_repos = json.load(f)
        all_src_repo_num = len(src_repos)
        for src_repo in src_repos:
            repo_id = src_repo["repo_id"]
            src_repo_ids.add(repo_id)
            version_id = src_repo["version_id"]
            version_key = f"{repo_id}-{version_id}"
            src_repo_version_ids.add(version_key)

    src_repo_num = len(src_repo_ids)
    src_repo_version_num = len(src_repo_version_ids)
    logger.info(f"\nsrc_repo_num: {src_repo_num}\n"
                f"src_repo_version_ids: {src_repo_version_num}\n")

    tc_summary["src_repo_num"] = src_repo_num
    tc_summary["src_repo_version_num"] = src_repo_version_num
    return src_repo_ids
