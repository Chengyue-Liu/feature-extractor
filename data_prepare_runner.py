#!/usr/bin/env python
# -*- coding: utf-8 -*-
from data_preparation.decompress_debian_package import decompress
from data_preparation.file_path_manager import get_tar_file_paths

# @Time : 2023/11/21 16:54
# @Author : Liu Chengyue


if __name__ == '__main__':
    src_tar_paths, bin_tar_paths = get_tar_file_paths()
    decompress(src_tar_paths, bin_tar_paths)
