#!/usr/bin/env python
# -*- coding: utf-8 -*-
from data_preparation.file_path_manager import is_src_package

# @Time : 2023/11/21 17:26
# @Author : Liu Chengyue

with open("/Users/liuchengyue/Desktop/works/feature_analysis/feature-extractor/test_cases/ls-lR") as f:
    lines = f.readlines()
    for line in lines:
        if line.endswith('.tar.xz') and not line.endswith('.debian.tar.xz'):
            print(line)
