#!/usr/bin/env python
# -*- coding: utf-8 -*-
from data_preparation.decompressor import multiple_decompress
from data_preparation.tar_file_manager import get_tar_file_paths
from utils.json_util import dump_to_json

# @Time : 2023/11/21 16:54
# @Author : Liu Chengyue


if __name__ == '__main__':
    """
    解压文件
    """
    src_tar_paths, bin_tar_paths = get_tar_file_paths()
    # dump_to_json(src_tar_paths, "/root/DATA/liuchengyue/feature-extractor/src_tar_paths.json")
    # dump_to_json(bin_tar_paths, "/root/DATA/liuchengyue/feature-extractor/bin_tar_paths.json")

    multiple_decompress(src_tar_paths, bin_tar_paths)
    """
    nohup python data_prepare_runner.py &
    
    ps aux | grep "python data_prepare_runner.py" | grep -v grep | awk '{print $2}' | xargs kill
    ps aux | grep "unar" | grep -v grep | awk '{print $2}' | xargs kill
    ps aux | grep "rm -rf" | grep -v grep | awk '{print $2}' | xargs kill
    
    
    obs://large-file-storage/LiuChengyue/sync_nus_server/
    """
