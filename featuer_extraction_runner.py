#!/usr/bin/env python
# -*- coding: utf-8 -*-

from loguru import logger

from feature_extraction.bin_feature_extractors.bin_function_extractor import BinFunctionExtractor
from feature_extraction.bin_feature_extractors.bin_string_extractor import BinStringExtractor
from feature_extraction.entities import Repository
from feature_extraction.src_feature_extractors.src_feature_tree_sitter_extractor import SrcFeatureTreeSitterExtractor
from settings import BIN_REPOS_JSON, SRC_REPOS_JSON


# @Time : 2023/11/3 12:06
# @Author : Liu Chengyue
# @File : extractor_runner.py
# @Software: PyCharm


def main():
    # 提取特征
    logger.info(f"提取二进制普通特征")
    bin_repos = Repository.init_repositories_from_json_file(BIN_REPOS_JSON)
    extractor = BinStringExtractor(bin_repos)
    extractor.multiple_run()

    logger.info(f"提取二进制CFG等特征")
    extractor = BinFunctionExtractor(bin_repos)
    extractor.multiple_run()

    # 源码字符串
    logger.info(f"提取源码特征")
    src_repos = Repository.init_repositories_from_json_file(SRC_REPOS_JSON)
    extractor = SrcFeatureTreeSitterExtractor(src_repos)
    extractor.multiple_run()

    logger.info("all done.")


if __name__ == '__main__':
    main()
