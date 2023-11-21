#!/usr/bin/env python
# -*- coding: utf-8 -*-
from data_preparation.file_path_manager import is_src_package

# @Time : 2023/11/21 17:26
# @Author : Liu Chengyue

with open("/Users/liuchengyue/Desktop/works/feature_analysis/feature-extractor/test_cases/ls-lR") as f:
    lines = f.readlines()
    extension_dict = {}
    cur_dir = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue
        elif line.startswith('total'):
            continue
        elif line.startswith('./'):
            cur_dir = f"/{line[2:-1]}"
        elif "/pool/main" not in cur_dir:
            continue

        if '.' not in line:
            continue

        if line.startswith('.'):
            continue

        if line .startswith('drwxr'):
            continue

        if line.endswith('.debian.tar.xz'):
            continue
        if line.endswith('asc'):
            continue
        if line.endswith('dsc'):
            continue
        extension = line.rsplit('.', 1)[-1]

        if " " in extension:
            continue

        if '/' in extension:
            continue

        if extension[0].isdigit():
            continue

        if extension not in extension_dict:
            extension_dict[extension] = line

    for k, v in extension_dict.items():
        print(k, v)

    print(list(sorted(extension_dict.keys())))