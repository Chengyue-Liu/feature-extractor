#!/usr/bin/env python
# -*- coding: utf-8 -*-


# @Time : 2023/11/3 11:37
# @Author : Liu Chengyue
# @File : entities.py
# @Software: PyCharm
import dataclasses
import enum
from dataclasses import dataclass
from typing import List


@dataclasses.dataclass
class Task:
    def __init__(self, repo_id, repo_path):
        self.repo_id = repo_id
        self.repo_path = repo_path


@dataclasses.dataclass
class FileFeature:
    def __init__(self, file_path: str, features: list):
        self.file_path: str = file_path
        self.features: list = features

    def custom_serialize(self):
        return {
            "file_path": self.file_path,
            "features": self.features,
        }


@dataclasses.dataclass
class RepoFeature:
    def __init__(self, repo_path: str, file_features: List[FileFeature]):
        self.repo_path: str = repo_path
        self.file_features: List[FileFeature] = file_features

    def custom_serialize(self):
        return {
            "file_path": self.repo_path,
            "feature_dict": [ff.custom_serialize() for ff in self.file_features],
        }
