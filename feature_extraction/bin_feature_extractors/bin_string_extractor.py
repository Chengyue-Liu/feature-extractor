#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
from abc import ABC

from feature_extraction.bin_feature_extractors.bin_feature_extractor import BinFeatureExtractor
from feature_extraction.entities import FileFeature


# @Time : 2023/11/21 21:55
# @Author : Liu Chengyue


class BinStringExtractor(BinFeatureExtractor, ABC):

    def extract_file_feature(self, path: str) -> FileFeature:
        cmd = f"strings {path}"
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output = proc.stdout.decode()
        strings = list({s for s in output.split("\n")})

        file_feature = FileFeature(
            file_path=path,
            feature=strings
        )

        return file_feature
