#!/usr/bin/env python
# -*- coding: utf-8 -*-
import collections
import json
import random

from loguru import logger

from settings import BIN_REPOS_JSON, SRC_REPOS_JSON, TEST_CASES_JSON_PATH, TEST_CASE_SAMPLE_SIZE_PER_REPO, \
    TC_BIN_REPOS_JSON


# @Time : 2023/12/6 18:46
# @Author : Liu Chengyue


def generate_tc_information():
    tc_summary = {}
    # 加载源码信息
    src_repo_ids = load_src_repo_info(tc_summary)

    # 加载二进制信息
    bin_repo_test_cases_dict = load_bin_repo_info(src_repo_ids, tc_summary)

    # 筛选
    filter_test_cases(bin_repo_test_cases_dict, tc_summary)

    # 保存
    test_case_info = {
        "tc_summary": tc_summary,
        "bin_repo_test_cases_dict": bin_repo_test_cases_dict,
    }
    with open(TEST_CASES_JSON_PATH, 'w') as f:
        json.dump(test_case_info, f, ensure_ascii=False)

    # 额外保存一份 bin_repos 格式的
    tc_bin_repos = []
    for bin_repos in bin_repo_test_cases_dict.values():
        tc_bin_repos.extend(bin_repos)
    with open(TC_BIN_REPOS_JSON, 'w') as f:
        json.dump(tc_bin_repos, f, ensure_ascii=False)


def filter_test_cases(bin_repo_test_cases_dict, tc_summary):
    filtered_bin_repo_num = 0
    filtered_elf_file_num = 0
    for repo_id, repos in bin_repo_test_cases_dict.items():
        if len(test_cases := bin_repo_test_cases_dict[repo_id]) > TEST_CASE_SAMPLE_SIZE_PER_REPO:
            # 按照版本倒序排列
            test_cases.sort(key=lambda x: x["repo_release"], reverse=True)
            test_cases.sort(key=lambda x: x["repo_version"], reverse=True)

            # 取最新，最旧
            test_cases.append(repos[1])
            test_cases.append(repos[-1])

            # 然后从中间随机补充
            test_cases = random.sample(repos[1:-1], TEST_CASE_SAMPLE_SIZE_PER_REPO - 2)

        filtered_bin_repo_num += len(test_cases)
        for test_case in test_cases:
            filtered_elf_file_num += len(test_case["elf_paths"])
    logger.info(
        f"TEST_CASE_SAMPLE_SIZE_PER_REPO: {TEST_CASE_SAMPLE_SIZE_PER_REPO}\n"
        f"filtered_test_cases_num: {filtered_bin_repo_num}\n"
        f"filtered_elf_file_num: {filtered_elf_file_num}\n")

    tc_summary["TEST_CASE_SAMPLE_SIZE_PER_REPO"] = TEST_CASE_SAMPLE_SIZE_PER_REPO
    tc_summary["filtered_bin_repo_num"] = filtered_bin_repo_num
    tc_summary["filtered_elf_file_num"] = filtered_elf_file_num


def load_bin_repo_info(src_repo_ids, tc_summary):
    bin_repo_with_elf_num = 0
    bin_repo_with_elf_with_src_num = 0
    bin_repo_test_cases_dict = collections.defaultdict(list)  # repo_id: repos
    with open(BIN_REPOS_JSON) as f:
        bin_repos = json.load(f)
        all_bin_repo_num = len(bin_repos)
        for bin_repo in bin_repos:
            if not bin_repo["elf_paths"]:
                continue

            bin_repo_with_elf_num += 1
            repo_id = bin_repo["repo_id"]
            if repo_id not in src_repo_ids:
                continue

            bin_repo_with_elf_with_src_num += 1
            bin_repo_test_cases_dict[repo_id].append(bin_repo)
    logger.info(f"bin_repo_num: {all_bin_repo_num}\n"
                f"bin_repo_with_elf_num: {bin_repo_with_elf_num}\n"
                f"bin_repo_with_elf_with_src_num: {bin_repo_with_elf_with_src_num}\n")

    tc_summary["bin_repo_num"] = all_bin_repo_num
    tc_summary["bin_repo_with_elf_num"] = bin_repo_with_elf_num
    tc_summary["bin_repo_with_elf_with_src_num"] = bin_repo_with_elf_with_src_num
    return bin_repo_test_cases_dict


def load_src_repo_info(tc_summary):
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
    tc_summary["all_src_repo_num"] = all_src_repo_num
    tc_summary["src_repo_with_target_file_num"] = len(src_repo_ids)
    tc_summary["src_repo_version_with_target_file_num"] = len(src_repo_version_ids)
    return src_repo_ids
