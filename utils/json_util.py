#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os.path

from loguru import logger


# @Time : 2023/11/21 17:36
# @Author : Liu Chengyue


def dump_to_json(data, f_path):
    f_path = os.path.abspath(f_path)
    basedir, file_name = os.path.split(f_path)
    os.makedirs(basedir, exist_ok=True)
    logger.critical(f"saving json ... DO NOT INTERRUPT!")
    with open(f_path, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logger.success(f"save json succeed!")


def load_from_json(f_path):
    if not os.path.exists(f_path):
        raise Exception(f"file {f_path} NOT exists!")

    with open(f_path) as f:
        return json.load(f)
