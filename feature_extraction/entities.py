#!/usr/bin/env python
# -*- coding: utf-8 -*-


# @Time : 2023/11/3 11:37
# @Author : Liu Chengyue
# @File : entities.py
# @Software: PyCharm
import dataclasses
import enum
import os
from dataclasses import dataclass
from typing import List

from loguru import logger
from tqdm import tqdm

from settings import DECOMPRESSED_DEBIAN_FILE_DIR_PATH, SRC_TASKS_JSON, BIN_TASKS_JSON
from utils.json_util import dump_to_json, load_from_json


@dataclasses.dataclass
class Task:
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
    def generate_tasks_json(cls):
        src_tasks = []
        bin_tasks = []
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
                        src_task = Task(
                            repo_path=src_path,
                            repo_type="source",
                            repo_id=repo_id,
                            repo_name=library_name,
                            version_id=version_id,
                            repo_version=version_number,
                        )
                        src_tasks.append(src_task)
                        binary_path = os.path.join(library_path, version_number, "binary")
                        for release_number in os.listdir(binary_path):
                            release_id += 1
                            release_path = os.path.join(binary_path, release_number)
                            for arch_name in os.listdir(release_path):
                                arch_id += 1
                                arch_path = os.path.join(release_path, arch_name)
                                pbar.update(1)
                                src_task = Task(
                                    repo_path=arch_path,
                                    repo_type="source",
                                    repo_id=repo_id,
                                    repo_name=library_name,
                                    version_id=version_id,
                                    repo_version=version_number,
                                    release_id=release_id,
                                    repo_release=release_number,
                                    arch_id=arch_id,
                                    repo_arch=arch_name
                                )
                                bin_tasks.append(src_task)

        logger.info(f"saving json ...")
        dump_to_json([task.custom_serialize() for task in src_tasks], SRC_TASKS_JSON)
        dump_to_json([task.custom_serialize() for task in bin_tasks], BIN_TASKS_JSON)
        logger.info(f"all finished.")

    @classmethod
    def init_tasks_from_json(cls, json_path):
        json_tasks = load_from_json(json_path)
        tasks = []
        for json_task in json_tasks:
            task = Task(
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
            tasks.append(task)
        return tasks

    def custom_serialize(self):
        return {
            "repo_path": self.repo_path,
            "repo_type": self.repo_type,
            "repo_id": self.repo_id,
            "repo_name": self.repo_name,
            "version_id": self.version_id,
            "repo_version": self.repo_version,
            "release_id": self.release_id,
            "repo_release": self.repo_release,
            "arch_id": self.arch_id,
            "repo_arch": self.repo_arch,

        }


@dataclasses.dataclass
class FileFeature:
    def __init__(self, file_path: str, features):
        self.file_path: str = file_path
        self.features = features

    def custom_serialize(self):
        return {
            "file_path": self.file_path,
            "features": self.features,
        }


@dataclasses.dataclass
class RepoFeature:
    def __init__(self, task: Task, file_features: List[FileFeature]):
        self.task: Task = task
        self.file_features: List[FileFeature] = file_features

    def custom_serialize(self):
        return {
            "task": self.task.custom_serialize(),
            "feature_dict": [ff.custom_serialize() for ff in self.file_features],
        }
