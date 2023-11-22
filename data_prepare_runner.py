#!/usr/bin/env python
# -*- coding: utf-8 -*-
from data_preparation.decompress_debian_package import multiple_decompress
from data_preparation.file_path_manager import get_tar_file_paths

# @Time : 2023/11/21 16:54
# @Author : Liu Chengyue


if __name__ == '__main__':
    src_tar_paths, bin_tar_paths = get_tar_file_paths()
    multiple_decompress(src_tar_paths, bin_tar_paths)
    """
    nohup python data_prepare_runner.py &
    
    ps aux | grep "python data_prepare_runner.py" | grep -v grep | awk '{print $2}' | xargs kill
    """
