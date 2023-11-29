#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
from abc import ABC

from feature_extraction.bin_feature_extractors.bin_feature_extractor import BinFeatureExtractor
from feature_extraction.entities import FileFeature
from utils.elf_utils import extract_elf_strings


# @Time : 2023/11/21 21:55
# @Author : Liu Chengyue


class BinStringExtractor(BinFeatureExtractor, ABC):

    def extract_file_feature(self, path: str) -> FileFeature:
        strings = extract_elf_strings(path)

        file_feature = FileFeature(
            file_path=path,
            feature=strings
        )

        return file_feature
