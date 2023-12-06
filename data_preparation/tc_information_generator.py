#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

from settings import BIN_REPOS_JSON


# @Time : 2023/12/6 18:46
# @Author : Liu Chengyue


def generate_tc_information():
    with open(BIN_REPOS_JSON) as f:
        bin_repos = json.load(f)
        for bin_repo in bin_repos:
            repo_path = bin_repo["repo_path"]

    pass
