#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from typing import List

# @Time : 2023/11/3 12:06
# @Author : Liu Chengyue
# @File : extractor_runner.py
# @Software: PyCharm

from main.decrators import timing_decorator, log_decorator
from main.entities import Task
from main.extractors.extractor import FeatureExtractor
from main.extractors.src_function_name_extractor import SrcFunctionNameExtractor
from main.extractors.src_string_extractor import SrcStringExtractor


def generate_tasks(repo_dir: str) -> List[Task]:
    """

    task: [repo_id, repo_path]
    :param repo_dir:
    :return:
    """
    # todo 这是一个临时的方法
    tasks = []
    repo_id = 0
    for root, dirs, files in os.walk(repo_dir):
        for dir_name in dirs:
            repo_id += 1
            repo_path = os.path.join(root, dir_name)
            task = Task(repo_id, repo_path)
            tasks.append(task)
        break
    return tasks


@log_decorator
@timing_decorator
def run_src_string_extractor(tasks: List[Task], result_dir):
    extractor = SrcStringExtractor(tasks, result_dir)
    extractor.multiple_run()


@log_decorator
@timing_decorator
def run_src_function_name_extractor(tasks: List[Task], result_dir):
    extractor = SrcFunctionNameExtractor(tasks, result_dir)
    extractor.multiple_run()


def main():
    repo_dir = "test_cases/source_code"
    result_dir = "results/strings"

    tasks = generate_tasks(repo_dir)
    run_src_string_extractor(tasks, result_dir)
    # run_src_function_name_extractor(tasks, result_dir)


if __name__ == '__main__':
    main()
