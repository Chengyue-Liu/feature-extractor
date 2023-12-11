#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from loguru import logger
from tqdm import tqdm

from feature_extraction.constants import TARGET_FILE_EXTENSION_SET
from feature_extraction.entities import Repository
from settings import DECOMPRESSED_DEBIAN_FILE_DIR_PATH, SRC_REPOS_JSON, BIN_REPOS_JSON
from utils.elf_utils import is_elf_file
from utils.json_util import dump_to_json


# @Time : 2023/12/6 18:25
# @Author : Liu Chengyue

def is_filter_repo(repo_name):
    """
    虽然在解压之前已经过滤过一次了，但是还是有很多漏网之鱼，这里补充过滤一下。

    :param repo_name:
    :return:
    """
    if repo_name.endswith(("-perl", "-java")):
        return True

    if repo_name.startswith(("python-", "php-","golang-")):
        return True

    return False


def get_version_dir_paths():
    repo_id = 0
    version_id = 0
    results = []
    start_count = dict()
    for category_name in os.listdir(DECOMPRESSED_DEBIAN_FILE_DIR_PATH):
        category_path = os.path.join(DECOMPRESSED_DEBIAN_FILE_DIR_PATH, category_name)
        if not os.path.isdir(category_path):
            continue
        for repo_name in os.listdir(category_path):
            if is_filter_repo(repo_name):
                continue
            library_path = os.path.join(category_path, repo_name)
            if not os.path.isdir(library_path):
                continue
            if "-" in repo_name:
                repo_name_start = repo_name.split("-")[0]
                if repo_name_start not in start_count:
                    start_count[repo_name_start] = 1
                else:
                    start_count[repo_name_start] += 1
            repo_id += 1
            for version_number in os.listdir(library_path):
                version_path = os.path.join(library_path, version_number)
                if not os.path.isdir(version_path):
                    continue
                version_id += 1
                if version_id % 1000 == 0:
                    logger.info(f"get_version_dir_paths progres: {version_id}")
                results.append((repo_id, repo_name, version_id, version_number, version_path))
    start_count = {k:start_count[k] for k in sorted(start_count,key=lambda x:start_count[x])}
    print(start_count)
    return results


def generate_repositories_json():
    logger.info(f"get_version_dir_paths")
    results = get_version_dir_paths()

    src_repos = []
    bin_repos = []
    release_id = 0
    arch_id = 0
    for repo_id, repo_name, version_id, version_number, version_path in tqdm(results, total=len(results),
                                                                             desc="generate_repositories_json"):

        # source
        src_path = os.path.join(version_path, "source")
        if os.path.isdir(src_path):
            target_file_paths = [os.path.join(root, f) for root, dirs, files in os.walk(src_path)
                                 for f in files
                                 if f.endswith(tuple(TARGET_FILE_EXTENSION_SET))]
            if len(target_file_paths) == 0:
                print(repo_name)
    #         bin_repo = Repository(
    #             repo_path=src_path,
    #             repo_type="source",
    #             repo_id=repo_id,
    #             repo_name=repo_name,
    #             version_id=version_id,
    #             repo_version=version_number,
    #             target_src_file_num=len(target_file_paths)
    #         )
    #         src_repos.append(bin_repo)
    #
    #     # binary
    #     binary_path = os.path.join(version_path, "binary")
    #     if not os.path.isdir(binary_path):
    #         continue
    #
    #     for package_name in os.listdir(binary_path):
    #         package_path = os.path.join(binary_path, package_name)
    #         if not os.path.isdir(package_path):
    #             continue
    #         for release_number in os.listdir(package_path):
    #             release_path = os.path.join(package_path, release_number)
    #             if not os.path.isdir(release_path):
    #                 continue
    #             release_id += 1
    #             for arch_name in os.listdir(release_path):
    #                 arch_path = os.path.join(release_path, arch_name)
    #                 if not os.path.isdir(arch_path):
    #                     continue
    #                 arch_id += 1
    #                 elf_paths = []
    #                 for root, dirs, files in os.walk(arch_path):
    #                     for file_name in files:
    #                         file_path = os.path.join(root, file_name)
    #                         if is_elf_file(file_path):
    #                             elf_paths.append(file_path)
    #                 bin_repo = Repository(
    #                     repo_path=arch_path,
    #                     repo_type="binary",
    #                     repo_id=repo_id,
    #                     repo_name=repo_name,
    #                     version_id=version_id,
    #                     repo_version=version_number,
    #                     package_name=package_name,
    #                     release_id=release_id,
    #                     repo_release=release_number,
    #                     arch_id=arch_id,
    #                     repo_arch=arch_name,
    #                     elf_paths=elf_paths
    #                 )
    #                 bin_repos.append(bin_repo)
    #
    # logger.info(f"saving json ...")
    # dump_to_json([repo.custom_serialize() for repo in src_repos], SRC_REPOS_JSON)
    # dump_to_json([repo.custom_serialize() for repo in bin_repos], BIN_REPOS_JSON)
    # logger.info(f"all finished.")

    return src_repos, bin_repos
