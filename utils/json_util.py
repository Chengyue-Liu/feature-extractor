#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os.path


# @Time : 2023/11/21 17:36
# @Author : Liu Chengyue


def dump_to_json(data, f_path):
    basedir, file_name = os.path.split(f_path)
    os.makedirs(basedir, exist_ok=True)
    with open(f_path, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_from_json(f_path):
    if not os.path.exists(f_path):
        raise Exception(f"file {f_path} NOT exists!")

    with open(f_path) as f:
        return json.load(f)
