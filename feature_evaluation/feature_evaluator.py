#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time : 2023/11/22 00:19
# @Author : Liu Chengyue

"""
1. 构建一个特征库
2. 遍历任务文件，进行扫描
3. 看是否扫描到了自己
"""
import os
from abc import abstractmethod
from typing import List, Set

from feature_extraction.entities import Task
from utils.json_util import load_from_json


class FeatureEvaluator:
    def __init__(self):
        self.tasks: List[Task] = []
        self.repo_features: List = []

    def load_task_and_features(self, feature_dir):
        """
        加载任务和特征
        :param feature_dir:
        :return:
        """
        for file_name in os.listdir(feature_dir):
            if file_name.endswith(".json"):
                repo_feature = load_from_json(os.path.join(feature_dir, file_name))

                task_json = repo_feature["task"]
                task = Task.init_task_from_json_data(task_json)
                self.tasks.append(task)
                self.repo_features.append(repo_feature)

    @abstractmethod
    def detect(self):
        pass

    @abstractmethod
    def evaluate(self):
        pass
