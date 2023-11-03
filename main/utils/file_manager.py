#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json


# @Time : 2023/11/3 11:31
# @Author : Liu Chengyue
# @File : file_manager.py
# @Software: PyCharm


def dump_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
