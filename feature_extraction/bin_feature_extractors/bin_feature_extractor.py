#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import multiprocessing
import os
from abc import abstractmethod
from typing import List

from loguru import logger
from tqdm import tqdm

from feature_extraction.entities import Repository, RepoFeature, FileFeature
from settings import PROCESS_NUM, FEATURE_RESULT_DIR
from utils.json_util import dump_to_json


# @Time : 2023/11/21 21:55
# @Author : Liu Chengyue


class BinFeatureExtractor:

    def __init__(self, repositories: List[Repository]):
        self.repositories = repositories
        self.result_dir = os.path.join(FEATURE_RESULT_DIR, self.__class__.__name__)
        os.makedirs(self.result_dir, exist_ok=True)

    @abstractmethod
    def extract_file_feature(self, path: str) -> FileFeature:
        pass

    def is_elf_file(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                # ELF 文件的前四个字节为 b'\x7fELF'
                return f.read(4) == b'\x7fELF'
        except IOError:
            return False

    def find_elf_files(self, repo_path):
        elf_files = []
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.isfile(file_path) and self.is_elf_file(file_path):
                    elf_files.append(file_path)
        return elf_files

    def extract_repo_feature(self, repository):
        # 保存路径
        result_path = os.path.join(self.result_dir,
                                   f"{repository.repo_id}-{repository.version_id}-{repository.release_id}-{repository.arch_id}.json")
        if os.path.exists(result_path):
            return

        # 找到目标文件
        elf_paths = self.find_elf_files(repository.repo_path)

        # 提取文件特征
        file_features = [self.extract_file_feature(path) for path in elf_paths]

        # 生成仓库特征
        repo_feature = RepoFeature(
            repository=repository,
            file_features=file_features
        )

        # 保存特征
        dump_to_json(repo_feature.custom_serialize(), result_path)

    def multiple_run(self):
        pool = multiprocessing.Pool(processes=PROCESS_NUM)

        results = pool.imap_unordered(self.extract_repo_feature, self.repositories)

        for _ in tqdm(results, total=len(self.repositories), desc="multiple run extract binary features"):
            pass
        pool.close()
        pool.join()
        pass
