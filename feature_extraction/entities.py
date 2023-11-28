#!/usr/bin/env python
# -*- coding: utf-8 -*-


# @Time : 2023/11/3 11:37
# @Author : Liu Chengyue
# @File : entities.py
# @Software: PyCharm
import dataclasses
import enum
import json
import os
from dataclasses import dataclass
from typing import List

from loguru import logger
from tqdm import tqdm

from settings import DECOMPRESSED_DEBIAN_FILE_DIR_PATH, SRC_REPOS_JSON, BIN_REPOS_JSON
from utils.json_util import dump_to_json, load_from_json


@dataclasses.dataclass
class Repository:
    def __init__(self,
                 repo_path, repo_type,
                 repo_id, version_id, repo_name, repo_version,
                 release_id=None, arch_id=None, repo_release=None, repo_arch=None):
        self.repo_path = repo_path
        self.repo_type = repo_type

        self.repo_id = repo_id
        self.repo_name = repo_name

        self.version_id = version_id
        self.repo_version = repo_version

        self.release_id = release_id
        self.repo_release = repo_release

        self.arch_id = arch_id
        self.repo_arch = repo_arch

    @classmethod
    def generate_repositories_json(cls):
        src_repos = []
        bin_repos = []
        repo_id = 0
        version_id = 0
        release_id = 0
        arch_id = 0
        with tqdm(total=1200000, desc="generate tasks") as pbar:
            for category_name in os.listdir(DECOMPRESSED_DEBIAN_FILE_DIR_PATH):
                category_path = os.path.join(DECOMPRESSED_DEBIAN_FILE_DIR_PATH, category_name)
                if not os.path.isdir(category_path):
                    continue
                for library_name in os.listdir(category_path):
                    repo_id += 1
                    library_path = os.path.join(category_path, library_name)
                    for version_number in os.listdir(library_path):
                        version_id += 1
                        src_path = os.path.join(library_path, version_number, "source")
                        pbar.update(1)
                        bin_repo = Repository(
                            repo_path=src_path,
                            repo_type="source",
                            repo_id=repo_id,
                            repo_name=library_name,
                            version_id=version_id,
                            repo_version=version_number,
                        )
                        src_repos.append(bin_repo)
                        binary_path = os.path.join(library_path, version_number, "binary")
                        for release_number in os.listdir(binary_path):
                            release_id += 1
                            release_path = os.path.join(binary_path, release_number)
                            for arch_name in os.listdir(release_path):
                                arch_id += 1
                                arch_path = os.path.join(release_path, arch_name)
                                pbar.update(1)
                                bin_repo = Repository(
                                    repo_path=arch_path,
                                    repo_type="binary",
                                    repo_id=repo_id,
                                    repo_name=library_name,
                                    version_id=version_id,
                                    repo_version=version_number,
                                    release_id=release_id,
                                    repo_release=release_number,
                                    arch_id=arch_id,
                                    repo_arch=arch_name
                                )
                                bin_repos.append(bin_repo)

        logger.info(f"saving json ...")
        dump_to_json([repo.custom_serialize() for repo in src_repos], SRC_REPOS_JSON)
        dump_to_json([repo.custom_serialize() for repo in bin_repos], BIN_REPOS_JSON)
        logger.info(f"all finished.")

    @classmethod
    def init_repository_from_json_data(cls, json_task):
        repository = Repository(
            repo_path=json_task["repo_path"],
            repo_type=json_task["repo_type"],
            repo_id=json_task["repo_id"],
            repo_name=json_task["repo_name"],
            repo_version=json_task["repo_version"],
            version_id=json_task["version_id"],
            repo_release=json_task["repo_release"],
            release_id=json_task["release_id"],
            repo_arch=json_task["repo_arch"],
            arch_id=json_task["arch_id"],
        )
        return repository

    @classmethod
    def init_repositories_from_json_file(cls, json_path):
        json_repositories = load_from_json(json_path)
        tasks = []
        for json_repository in json_repositories:
            tasks.append(cls.init_repository_from_json_data(json_repository))
        return tasks

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
            "repo_release": self.repo_release,
            "repo_arch": self.repo_arch,
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
    def init_repo_feature_from_json_file(self, json_path):
        with open(json_path) as f:
            data = json.load(f)
            repository = Repository.init_repository_from_json_data(data["repository"])
            file_features = [FileFeature.init_file_feature_from_json_data(file_feature_json) for file_feature_json in
                             data['file_features']]
            return RepoFeature(
                repository=repository,
                file_features=file_features
            )
