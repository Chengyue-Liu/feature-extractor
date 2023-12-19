#!/usr/bin/env python
# -*- coding: utf-8 -*-
from loguru import logger

from data_preparation.data_decompress.decompressor import multiple_decompress
from data_preparation.data_decompress.tar_file_manager import get_tar_file_paths, filter_bin_tar_paths
from data_preparation.data_info_generatot import generate_repositories_json
from data_preparation.data_statistics import statistic_data
from data_preparation.tc_info_generator import generate_tc_information

# @Time : 2023/11/21 16:54
# @Author : Liu Chengyue

if __name__ == '__main__':
    """
    解压文件，生成文件路径和id信息
    """
    # step 1: 获取tar 文件路径
    logger.info("step 1: 获取tar 文件路径")
    # src_tar_paths, bin_tar_paths = get_tar_file_paths()
    # 大概的数量：未知

    # step x: 初步筛选掉非arm/amd64, 以及仅凭名称判断不是c/cpp语言的包
    logger.info("step x: 筛选bin 路径")
    # src_tar_paths, bin_tar_paths = filter_bin_tar_paths(src_tar_paths, bin_tar_paths)
    # 大概的数量：src_tar_paths: 71k, bin_tar_paths:310k

    # step 2: 解压
    logger.info("step 2: 解压")
    # multiple_decompress(src_tar_paths, bin_tar_paths)

    # step 3: 生成源码和二进制文件路径
    # 同时这里有第二次筛选：同时筛选掉没有c/cpp文件的源码，以及没有elf的二进制包
    logger.info("step 3: 生成源码和二进制文件路径")
    # generate_repositories_json()

    # 经过两次筛选后，剩余的大概的数量：
    # src_repo_num: 13523
    # src_repo_version_ids: 27294

    # bin_repo_num: 12575
    # repo_version_num: 25403
    # different_bin_repo_num: 128051


    # step 5: 筛选测试用例ps aux | grep "rsync" | grep -v grep | awk '{print $2}' | xargs kill
    logger.info("step 5: 筛选测试用例")
    generate_tc_information()

    # 测试用例数量
    # filtered_tc_repo_num: 12575
    # filtered_tc_repo_version_num: 14460
    # filtered_tc_elf_file_num: 74458


    logger.info(f"all finished.")
    """
    一些常用命令
    nohup python data_prepare_runner.py &
    
    ps aux | grep "python data_prepare_runner.py" | grep -v grep | awk '{print $2}' | xargs kill
    ps aux | grep "unar" | grep -v grep | awk '{print $2}' | xargs kill
    ps aux | grep "rsync -r --delete" | grep -v grep | awk '{print $2}' | xargs kill
    
    ps aux | grep "rm -rf" | grep -v grep | awk '{print $2}' | xargs kill
    
    nohup rsync -r --delete empty/ decompressed_files/ &
    nohup rsync -r --delete empty/ decompressed_debian_mirror/ &
    
    obs://large-file-storage/LiuChengyue/sync_nus_server/
    """
