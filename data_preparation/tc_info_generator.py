#!/usr/bin/env python
# -*- coding: utf-8 -*-
import collections
import json
import multiprocessing
import random
from multiprocessing import Pool

from loguru import logger
from tqdm import tqdm

from settings import BIN_REPOS_JSON, SRC_REPOS_JSON, \
    TC_BIN_REPOS_JSON, TEST_CASES_100_JSON_PATH, TEST_CASES_1000_JSON_PATH, TEST_CASES_10000_JSON_PATH, PROCESS_NUM
from utils.elf_utils import extract_elf_strings


# @Time : 2023/12/6 18:46
# @Author : Liu Chengyue


def generate_tc_information():
    tc_summary = {}
    # 加载源码信息
    src_repo_ids = load_src_repo_info(tc_summary)

    # 加载二进制信息
    bin_repo_test_cases_dict = load_bin_repo_info(src_repo_ids, tc_summary)

    # 随机选择测试用例，并保存到文件
    filter_and_dump_test_cases(bin_repo_test_cases_dict)


def filter_and_dump_test_cases(bin_repo_test_cases_dict):
    # 10000个
    tc_repo_files_10000 = generate_tc_repo_files(bin_repo_test_cases_dict, 4)
    with open(TEST_CASES_10000_JSON_PATH, 'w') as f:
        json.dump(tc_repo_files_10000, f, ensure_ascii=False)

    # 1000个
    tc_repo_files_1000 = generate_tc_repo_files(bin_repo_test_cases_dict, 4)
    with open(TEST_CASES_1000_JSON_PATH, 'w') as f:
        json.dump(tc_repo_files_1000, f, ensure_ascii=False)

    # 100个
    tc_repo_files_100 = generate_tc_repo_files(bin_repo_test_cases_dict, 4)
    with open(TEST_CASES_100_JSON_PATH, 'w') as f:
        json.dump(tc_repo_files_100, f, ensure_ascii=False)


def generate_tc_repo_files(bin_repo_test_cases_dict, sample_size=10000):
    # 先随机选择10000个库
    tc_repo_ids = random.sample(list(bin_repo_test_cases_dict.keys()), sample_size)

    # 然后随机选择他们的版本
    tc_repos = [random.sample(bin_repo_test_cases_dict[repo_id], 1)[0] for repo_id in tc_repo_ids]

    # 然后生成简要信息
    tc_repo_files = [
        {
            "repo_id": repo["repo_id"],
            "version_id": repo["version_id"],
            "elf_path": elf_path
        }
        for repo in tc_repos
        for elf_path in repo["elf_paths"]
    ]

    # 然后多进程并发提取他们的字符串
    pool = multiprocessing.Pool(processes=PROCESS_NUM)
    results = pool.imap_unordered(extract_tc_repo_strings, tc_repo_files)
    tc_repo_files = [r for r in tqdm(results, total=len(tc_repo_files), desc="extract_tc_repo_strings")]
    pool.close()
    pool.join()

    return tc_repo_files


def extract_tc_repo_strings(repo):
    repo["strings"] = extract_elf_strings(repo['elf_path'])
    return repo


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
