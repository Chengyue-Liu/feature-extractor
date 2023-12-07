#!/usr/bin/env python
# -*- coding: utf-8 -*-


# @Time : 2023/11/3 11:37
# @Author : Liu Chengyue
# @File : entities.py
# @Software: PyCharm
import dataclasses
import json
from typing import List

from utils.json_util import load_from_json
from uuid import uuid4


@dataclasses.dataclass
class Repository:
    def __init__(self,
                 repo_path, repo_type,
                 repo_id, version_id, repo_name, repo_version,
                 uuid=None,
                 version_key=None,
                 package_name=None,
                 release_id=None, arch_id=None, repo_release=None, repo_arch=None,
                 target_src_file_num=0,
                 elf_paths=None):
        self.uuid = uuid if uuid else str(uuid4())

        # basic
        self.repo_path = repo_path
        self.repo_type = repo_type

        # repo
        self.repo_id = repo_id
        self.repo_name = repo_name

        # version
        self.version_id = version_id
        self.version_key = version_key if version_key else f"{self.repo_id}-{self.version_id}"
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
    def init_repository_from_json_data(cls, json_data):
        repository = Repository(
            uuid=json_data["uuid"],
            repo_path=json_data["repo_path"],
            repo_type=json_data["repo_type"],
            repo_id=json_data["repo_id"],
            repo_name=json_data["repo_name"],
            repo_version=json_data["repo_version"],
            package_name=json_data["package_name"],
            version_id=json_data["version_id"],
            version_key=json_data["version_key"],
            repo_release=json_data["repo_release"],
            release_id=json_data["release_id"],
            repo_arch=json_data["repo_arch"],
            arch_id=json_data["arch_id"],
            target_src_file_num=json_data["target_src_file_num"],
            elf_paths=json_data["elf_paths"],
        )
        return repository

    @classmethod
    def init_repositories_from_json_file(cls, file_path):
        json_repositories = load_from_json(file_path)
        repositories = []
        for json_repository in json_repositories:
            repositories.append(cls.init_repository_from_json_data(json_repository))
        return repositories

    def custom_serialize(self):
        return {
            "uuid": self.uuid,
            "repo_path": self.repo_path,
            "repo_type": self.repo_type,
            "repo_id": self.repo_id,
            "version_id": self.version_id,
            "version_key": self.version_key,
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
    def init_file_feature_from_json_data(cls, json_data):
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
    def init_repo_feature_from_json_file(cls, file_path):
        with open(file_path) as f:
            data = json.load(f)
            repository = Repository.init_repository_from_json_data(data["repository"])
            file_features = [FileFeature.init_file_feature_from_json_data(file_feature_json) for file_feature_json in
                             data['file_features']]
            return RepoFeature(
                repository=repository,
                file_features=file_features
            )
