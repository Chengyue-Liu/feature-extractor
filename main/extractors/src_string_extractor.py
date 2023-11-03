#!/usr/bin/env python
# -*- coding: utf-8 -*-
from main.entities import FileFeature
from main.extractors.extractor import FeatureExtractor


# @Time : 2023/11/3 11:29
# @Author : Liu Chengyue
# @File : source_code_string_extractor.py
# @Software: PyCharm


class SrcStringExtractor(FeatureExtractor):

    def extract_file_feature(self, file_path) -> FileFeature:
        with open(file_path) as f:
            lines = f.readlines()
            line_num = len(lines)

        file_feature = FileFeature(
            file_path=file_path,
            feature_dict={
                "line_num": line_num
            }
        )
        return file_feature
