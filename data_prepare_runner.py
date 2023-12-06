#!/usr/bin/env python
# -*- coding: utf-8 -*-
from loguru import logger

# @Time : 2023/11/21 16:54
# @Author : Liu Chengyue

from data_preparation.data_decompress.decompressor import multiple_decompress
from data_preparation.data_decompress.tar_file_manager import get_tar_file_paths
from data_preparation.data_info_generatot import generate_repositories_json
from data_preparation.data_statistics import statistic_data

if __name__ == '__main__':
    """
    解压文件，生成文件路径和id信息
    """
    # step 1: 获取tar 文件路径
    logger.info("step 1: 获取tar 文件路径")
    # src_tar_paths, bin_tar_paths = get_tar_file_paths()

    # step 2: 解压
    logger.info("step 2: 解压")
    # multiple_decompress(src_tar_paths, bin_tar_paths)

    # step 3: 生成源码和二进制文件路径
    logger.info("step 3: 生成源码和二进制文件路径")
    generate_repositories_json()

    # step 4: 简要统计
    statistic_data()


    """
    一些常用命令
    nohup python data_prepare_runner.py &
    
    ps aux | grep "python data_prepare_runner.py" | grep -v grep | awk '{print $2}' | xargs kill
    ps aux | grep "unar" | grep -v grep | awk '{print $2}' | xargs kill
    ps aux | grep "rm -rf" | grep -v grep | awk '{print $2}' | xargs kill
    
    
    obs://large-file-storage/LiuChengyue/sync_nus_server/
    """
