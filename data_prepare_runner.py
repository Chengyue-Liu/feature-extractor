#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time : 2023/11/21 16:54
# @Author : Liu Chengyue

from data_preparation.data_decompress.decompressor import multiple_decompress
from data_preparation.data_decompress.tar_file_manager import get_tar_file_paths

if __name__ == '__main__':
    # 获取tar 文件路径
    src_tar_paths, bin_tar_paths = get_tar_file_paths()

    # 解压
    multiple_decompress(src_tar_paths, bin_tar_paths)

    # todo 生成源码和二进制文件路径

    # todo 生成测试用例路径
    """
    一些常用命令
    nohup python data_prepare_runner.py &
    
    ps aux | grep "python data_prepare_runner.py" | grep -v grep | awk '{print $2}' | xargs kill
    ps aux | grep "unar" | grep -v grep | awk '{print $2}' | xargs kill
    ps aux | grep "rm -rf" | grep -v grep | awk '{print $2}' | xargs kill
    
    
    obs://large-file-storage/LiuChengyue/sync_nus_server/
    """
