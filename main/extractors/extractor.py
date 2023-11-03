#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time : 2023/11/3 11:35
# @Author : Liu Chengyue
# @File : extractor.py
# @Software: PyCharm
import multiprocessing
import os
from typing import List

from tqdm import tqdm

from main.constants import TARGET_FILE_EXTENSION_SET
from main.entities import FileFeature, RepoFeature, Task
from main.settings import EXTRACTION_PROCESS_NUM
from main.utils import file_manager


class FeatureExtractor:
    def __init__(self, tasks: List[Task], result_dir):
        self.tasks = tasks
        self.result_dir = result_dir

    def extract_file_feature(self, file_path) -> FileFeature:
        file_feature = FileFeature(
            file_path=file_path,
            feature_dict={}
        )
        return file_feature

    def extract_repo_feature(self, task: Task):
        repo_id = task.repo_id
        repo_path = task.repo_path

        # 筛选目标文件
        target_file_paths = [os.path.join(root, f) for root, dirs, files in os.walk(repo_path)
                             for f in files
                             if f.endswith(tuple(TARGET_FILE_EXTENSION_SET))]

        # 提取文件特征
        file_features = [self.extract_file_feature(path) for path in target_file_paths]

        # 生成仓库特征
        repo_feature = RepoFeature(
            repo_path=repo_path,
            file_features=file_features
        )

        # 保存特征
        result_path = os.path.join(self.result_dir, f"{repo_id}.json")
        file_manager.dump_json(repo_feature.custom_serialize(), result_path)

    def multiple_run(self):
        pool = multiprocessing.Pool(processes=EXTRACTION_PROCESS_NUM)

        results = pool.imap_unordered(self.extract_repo_feature, self.tasks)

        for _ in tqdm(results, total=len(self.tasks), desc="multiple run extract repo features"):
            pass
