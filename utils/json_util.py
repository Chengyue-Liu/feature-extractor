#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json


# @Time : 2023/11/21 17:36
# @Author : Liu Chengyue


def dump_to_json(data, f_path):
    with open(f_path, 'w') as f:
        json.dump(data, f, ensure_ascii=False)


def load_from_json(f_path):
    with open(f_path) as f:
        return json.load(f)
