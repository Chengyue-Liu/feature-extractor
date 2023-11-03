#!/usr/bin/env python
# -*- coding: utf-8 -*-


# @Time : 2023/10/24 14:16
# @Author : Liu Chengyue
# @File : generate_treesitter_languages..py
# @Software: PyCharm

from tree_sitter import Language

from main.settings import LANGUAGE_SO_FILE_PATH

Language.build_library(
    # Store the library in the `build` directory
    # 'resources/build/my-languages-mac.so',
    LANGUAGE_SO_FILE_PATH,

    # Include one or more languages
    [
        'feature_preparation/feature_extraction/vendor/tree-sitter-c',
        'feature_preparation/feature_extraction/vendor/tree-sitter-cpp'
    ]
)
