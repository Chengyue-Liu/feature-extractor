#!/usr/bin/env python
# -*- coding: utf-8 -*-


# @Time : 2023/11/3 11:37
# @Author : Liu Chengyue
# @File : entities.py
# @Software: PyCharm
import dataclasses
import json
import multiprocessing
import os
from typing import List

import ijson
from loguru import logger
from tqdm import tqdm

from settings import DECOMPRESSED_DEBIAN_FILE_DIR_PATH, SRC_REPOS_JSON, BIN_REPOS_JSON
from utils.json_util import dump_to_json, load_from_json


@dataclasses.dataclass
class Repository:
    def __init__(self,
                 repo_path, repo_type,
                 repo_id, version_id, repo_name, repo_version,
                 package_name=None,
                 release_id=None, arch_id=None, repo_release=None, repo_arch=None,
                 target_src_file_num=0,
                 elf_paths=None):
        # basic
        self.repo_path = repo_path
        self.repo_type = repo_type

        # repo
        self.repo_id = repo_id
        self.repo_name = repo_name

        # version
        self.version_id = version_id
        self.repo_version = repo_version

        # package, release
        self.package_name = package_name
        self.release_id = release_id
        self.repo_release = repo_release

        # arch
        self.arch_id = arch_id
        self.repo_arch = repo_arch

        # file
        self.target_src_file_num = target_src_file_num  # 源码目标文件的数量
        self.elf_paths = elf_paths  # elf文件路径

    @classmethod
    def init_repository_from_json_data(cls, repo_json):
        repository = Repository(
            repo_path=repo_json["repo_path"],
            repo_type=repo_json["repo_type"],
            repo_id=repo_json["repo_id"],
            repo_name=repo_json["repo_name"],
            repo_version=repo_json["repo_version"],
            package_name=repo_json["package_name"],
            version_id=repo_json["version_id"],
            repo_release=repo_json["repo_release"],
            release_id=repo_json["release_id"],
            repo_arch=repo_json["repo_arch"],
            arch_id=repo_json["arch_id"],
            target_src_file_num=repo_json["target_src_file_num"],
            elf_paths=repo_json["elf_paths"],
        )
        return repository

    @classmethod
    def init_repositories_from_json_file(cls, json_path):
        json_repositories = load_from_json(json_path)
        repositories = []
        for json_repository in json_repositories:
            repositories.append(cls.init_repository_from_json_data(json_repository))
        return repositories

    def custom_serialize(self):
        return {
            "repo_path": self.repo_path,
            "repo_type": self.repo_type,
            "repo_id": self.repo_id,
            "version_id": self.version_id,
            "release_id": self.release_id,
            "arch_id": self.arch_id,
            "repo_name": self.repo_name,
            "repo_version": self.repo_version,
            "package_name": self.package_name,
            "repo_release": self.repo_release,
            "repo_arch": self.repo_arch,
            "target_src_file_num": self.target_src_file_num,
            "elf_paths": self.elf_paths

        }


@dataclasses.dataclass
class FileFeature:
    def __init__(self, file_path: str, feature):
        self.file_path: str = file_path
        self.feature = feature

    def custom_serialize(self):
        return {
            "file_path": self.file_path,
            "feature": self.feature,
        }

    @classmethod
    def init_file_feature_from_json_data(self, json_data):
        return FileFeature(
            file_path=json_data['file_path'],
            feature=json_data['feature']
        )


@dataclasses.dataclass
class RepoFeature:
    def __init__(self, repository: Repository, file_features: List[FileFeature]):
        self.repository: Repository = repository
        self.file_features: List[FileFeature] = file_features

    def custom_serialize(self):
        return {
            "repository": self.repository.custom_serialize(),
            "file_features": [ff.custom_serialize() for ff in self.file_features],
        }

    @classmethod
    def init_repo_feature_from_json_file(cls, json_path):
        with open(json_path) as f:
            data = json.load(f)
            repository = Repository.init_repository_from_json_data(data["repository"])
            file_features = [FileFeature.init_file_feature_from_json_data(file_feature_json) for file_feature_json in
                             data['file_features']]
            return RepoFeature(
                repository=repository,
                file_features=file_features
            )

    @classmethod
    def init_repo_features_from_json_data(cls, path):
        # 下面是单进程逻辑
        with open(path, 'rb') as file:
            repo_features = []
            count = 0
            for item in ijson.items(file, 'item'):
                count += 1
                if count % 1000 == 0:
                    logger.info(f"init_repo_features_from_json_data progress: {count}")
                repository = Repository.init_repository_from_json_data(item["repository"])
                file_features = [FileFeature.init_file_feature_from_json_data(file_feature_json)
                                 for file_feature_json in item['file_features']]
                repo_features.append(RepoFeature(
                    repository=repository,
                    file_features=file_features
                ))
            return repo_features

        # 下面的逻辑是多进程读取，但是也没感觉快多少。
        # with open(path, 'rb') as file:
        #     repo_features = []
        #     count = 0
        #
        #     def log_progress(chunk_count):
        #         logger.info(f"init_repo_features_from_json_data progress: {chunk_count}")
        #
        #     with multiprocessing.Pool() as pool:
        #         # 使用 imap_unordered 并行处理每个 item
        #         results = pool.imap_unordered(process, ijson.items(file, 'item'))
        #
        #         # 等待所有任务完成
        #         for result in results:
        #             count += 1
        #             if count % 1000 == 0:
        #                 log_progress(count)
        #             repo_features.append(result)
        #     return repo_features


def process(item):
    repository = Repository.init_repository_from_json_data(item["repository"])
    file_features = [FileFeature.init_file_feature_from_json_data(file_feature_json)
                     for file_feature_json in item['file_features']]
    return RepoFeature(
        repository=repository,
        file_features=file_features
    )
