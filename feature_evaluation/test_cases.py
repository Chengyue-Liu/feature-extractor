#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
from typing import List

from tqdm import tqdm

from feature_evaluation.entities import TestCase
from feature_extraction.bin_feature_extractors.bin_string_extractor import BinStringExtractor
from feature_extraction.entities import Repository, FileFeature, RepoFeature
from settings import FEATURE_RESULT_DIR


# @Time : 2023/12/5 14:00
# @Author : Liu Chengyue

def gemerate(json_path):
    with open(json_path) as f:
        data = json.load(f)
        repository = Repository.init_repository_from_json_data(data["repository"])
        file_features = [FileFeature.init_file_feature_from_json_data(file_feature_json)
                         for file_feature_json in data['file_features']]
        return RepoFeature(
            repository=repository,
            file_features=file_features
        )


def get_test_cases() -> List[TestCase]:
    feature_dir = os.path.join(FEATURE_RESULT_DIR, BinStringExtractor.__name__)
    feature_files = os.listdir(feature_dir)
    test_cases = []
    for f in tqdm(feature_files, total=len(feature_files), desc="init_repo_features"):
        if f.endswith('.json'):
            f_path = os.path.join(feature_dir, f)
            test_cases.append(TestCase.init_from_repo_feature_file_path(f_path))
    return test_cases
