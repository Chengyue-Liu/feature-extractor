#!/usr/bin/env python
# -*- coding: utf-8 -*-
import collections
import json
import multiprocessing
import os
from multiprocessing.dummy import Pool

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

    if repo_name.startswith(("python-", "php-", "golang-")):
        return True

    return False


NOT_ELF_EXTENSION_SET = {'.gz', '.txt', '.Debian', '.cnf', '.h', '.png', '.html', '.hpp', '.py', '.hxx', '.xml',
                         '.json',
                         '.js', '.yml', '.cert', '.cmake', '.c', '.php', '.svg', '.lua', '.jpg', '.conf', '.gif', '.go',
                         '.cpp', '.dat',
                         '.sh', '.md', '.hh', '.stderr', '.TXT', '.css', '.xhtml', '.cert'}


def is_filter_file(elf_path):
    """
    过滤掉不是elf的文件，加速elf筛选

     [('.h', 1953766), ('', 1427686), ('.png', 1278914), ('.html', 1105294), ('.mo', 585211), ('.hpp', 511953),
     ('.py', 504704), ('.ko', 386544), ('.so', 300430), ('.svg', 272701), ('.hxx', 177003), ('.xml', 161375),
     ('.page', 152596), ('.o', 136618), ('.tfm', 115544), ('.json', 112022), ('.js', 107594), ('.rs', 85749),
      ('.a', 75816), ('.m', 74802)]
    :param elf_path:
    :return:
    """
    dir_name, elf_name = os.path.split(elf_path)
    pure_name, extension = os.path.splitext(elf_name)
    if extension in NOT_ELF_EXTENSION_SET:
        return True

    return False


def get_useful_version_dir_paths():
    repo_id = 0
    version_id = 0
    results = []
    for category_name in os.listdir(DECOMPRESSED_DEBIAN_FILE_DIR_PATH):
        category_path = os.path.join(DECOMPRESSED_DEBIAN_FILE_DIR_PATH, category_name)
        if not os.path.isdir(category_path):
            continue
        for repo_name in os.listdir(category_path):
            # 过滤其他语言
            if is_filter_repo(repo_name):
                continue
            # 不存在的过滤
            library_path = os.path.join(category_path, repo_name)
            if not os.path.isdir(library_path):
                continue
            repo_id += 1
            for version_number in os.listdir(library_path):
                # 不存在的过滤
                version_path = os.path.join(library_path, version_number)
                if not os.path.isdir(version_path):
                    continue
                version_id += 1
                if version_id % 1000 == 0:
                    logger.info(f"get_version_dir_paths progres: {version_id}")
                # 没有源码过滤
                src_path = os.path.join(version_path, "source")
                if not os.path.isdir(src_path):
                    continue
                # 没有二进制过滤
                binary_path = os.path.join(version_path, "binary")
                if not os.path.isdir(binary_path):
                    continue
                results.append((repo_id, repo_name, version_id, version_number, version_path))
    return results


def find_c_and_cpp_files(args):
    """
    找出所有的c/cpp文件
    :param args:
    :return:
    """
    repo_id, repo_name, version_id, version_number, version_path = args

    src_path = os.path.join(version_path, "source")
    target_file_paths = []
    if os.path.isdir(src_path):
        target_file_paths = [os.path.join(root, f) for root, dirs, files in os.walk(src_path)
                             for f in files
                             if f.endswith(tuple(TARGET_FILE_EXTENSION_SET))]

    return repo_id, repo_name, version_id, version_number, version_path, target_file_paths


def update_repo_elf_files(repo: Repository):
    """
    筛选elf
    :param repo:
    :return:
    """
    repo.elf_paths = [path for path in repo.elf_paths if is_elf_file(path)]
    return repo


def generate_repositories_json():
    # step 1: 找到版本文件夹
    logger.info(f"step 0: get_version_dir_paths")
    results = get_useful_version_dir_paths()

    # step 1: 多进程筛选源码c/cpp文件
    pool_size = multiprocessing.cpu_count()
    with Pool(pool_size) as pool:
        # 使用 pool.map 异步处理每个 repository
        results = list(tqdm(pool.imap_unordered(find_c_and_cpp_files, results), total=len(results),
                            desc="step 1: find c files"))

    # step 2: 初始化 src_repo, bin_repo
    src_repos = []
    bin_repos = []
    release_id = 0
    arch_id = 0
    for repo_id, repo_name, version_id, version_number, version_path, target_file_paths in tqdm(results,
                                                                                                total=len(results),
                                                                                                desc="step 2: generate_repositories_json"):
        # 没有c/cpp 源码，过滤掉
        if len(target_file_paths) == 0:
            continue

        # source
        src_path = os.path.join(version_path, "source")
        src_repo = Repository(
            repo_path=src_path,
            repo_type="source",
            repo_id=repo_id,
            repo_name=repo_name,
            version_id=version_id,
            repo_version=version_number,
            target_src_file_num=len(target_file_paths)
        )
        src_repos.append(src_repo)

        # binary
        binary_path = os.path.join(version_path, "binary")
        for package_name in os.listdir(binary_path):
            package_path = os.path.join(binary_path, package_name)
            if not os.path.isdir(package_path):
                continue
            for release_number in os.listdir(package_path):
                release_path = os.path.join(package_path, release_number)
                if not os.path.isdir(release_path):
                    continue
                release_id += 1
                for arch_name in os.listdir(release_path):
                    arch_path = os.path.join(release_path, arch_name)
                    if not os.path.isdir(arch_path):
                        continue
                    arch_id += 1
                    elf_paths = []
                    for root, dirs, files in os.walk(arch_path):
                        for file_name in files:
                            file_path = os.path.join(root, file_name)
                            if is_filter_file(file_path):
                                continue
                            # 此处只是筛选掉了明显不是的elf，添加进去的这些，也不代表都是ELF, 还需要后面进一步的确认。
                            elf_paths.append(file_path)
                    bin_repo = Repository(
                        repo_path=arch_path,
                        repo_type="binary",
                        repo_id=repo_id,
                        repo_name=repo_name,
                        version_id=version_id,
                        repo_version=version_number,
                        package_name=package_name,
                        release_id=release_id,
                        repo_release=release_number,
                        arch_id=arch_id,
                        repo_arch=arch_name,
                        elf_paths=elf_paths
                    )
                    bin_repos.append(bin_repo)

    # step 3: 多进程筛选bin repo 的 elf文件
    # pool_size = multiprocessing.cpu_count()
    # with Pool(pool_size) as pool:
    #     # 使用 pool.map 异步处理每个 repository
    #     bin_repos = list(tqdm(pool.imap_unordered(update_repo_elf_files, bin_repos),
    #                           total=len(bin_repos),
    #                           desc="step 3: filter elf files"))
    logger.info(f"extension_dict")
    extension_dict = dict()
    for repo in tqdm(bin_repos):
        for path in repo.elf_paths:
            dir_name, file_name = os.path.split(path)
            pure_name, extension = os.path.splitext(file_name)
            if extension not in extension_dict:
                extension_dict[extension] = 1
            else:
                extension_dict[extension] += 1
    with open('extension_dict.json', 'w') as f:
        json.dump(extension_dict, f, ensure_ascii=False, indent=4)

    # step 4: 过滤掉没有elf文件的二进制库
    logger.info(f"step 4: filter bin_repos")
    bin_repos = [repo for repo in bin_repos if repo.elf_paths]

    # step 5: 保存结果
    logger.info(f"saving json ...")
    dump_to_json([repo.custom_serialize() for repo in src_repos], SRC_REPOS_JSON)
    dump_to_json([repo.custom_serialize() for repo in bin_repos], BIN_REPOS_JSON)
    logger.info(f"src_repos: {len(src_repos)}, bin_repos: {len(bin_repos)}")
    logger.info(f"all finished.")
    return src_repos, bin_repos
