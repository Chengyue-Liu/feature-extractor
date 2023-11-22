#!/usr/bin/env python
# -*- coding: utf-8 -*-
import multiprocessing
import os.path
import shutil
import subprocess
import traceback
from typing import List

from loguru import logger
from tqdm import tqdm

from settings import DEBIAN_TAR_FILE_DIR_PATH, DECOMPRESSED_DEBIAN_FILE_DIR_PATH, PROCESS_NUM


# @Time : 2023/11/21 16:45
# @Author : Liu Chengyue

def parse_file_name(file_path: str):
    file_name = os.path.split(file_path)[-1]
    if "orig" in file_name:
        return file_name.split(".orig")[0]
    elif ".deb" in file_name:
        return file_name[:-4]
    elif ".udeb" in file_name:
        return file_name[:-5]
    else:
        return file_name


def get_decompress_target_path(path):
    # 获取名称
    file_name = parse_file_name(path)
    if "-" in file_name:
        name_version, release_arch = file_name.split("-")
        name, version = name_version.split("_")
        release, arch = release_arch.split("_")
        if name.startswith("lib"):
            category = name[:4]
        else:
            category = name[:1]
        return os.path.join(DECOMPRESSED_DEBIAN_FILE_DIR_PATH, category, name, version, "binary", release, arch)

    else:
        name, version = file_name.split("_")
        if name.startswith("lib"):
            category = name[:4]
        else:
            category = name[:1]
        return os.path.join(DECOMPRESSED_DEBIAN_FILE_DIR_PATH, category, name, version, "source")


def find_data_tar_gz(dir_path):
    for root, dirs, files in os.walk(dir_path):
        for f in files:
            if f.startswith("data."):
                f_path = os.path.join(root, f)
                return f_path


def unar(archive_path, target_dir):
    command = f"unar {archive_path} -o {target_dir}  -q"
    subprocess.run(command, shell=True, check=True)


def decompress(archive_path):
    try:
        # 获取target_dir
        target_dir = get_decompress_target_path(archive_path)

        # 如果目标文件夹已经存在，跳过
        if os.path.exists(target_dir):
            return

        # 二进制
        if archive_path.endswith('deb'):
            # 创建临时文件夹
            tmp_dir = f"{target_dir}_tmp"
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)
            os.makedirs(tmp_dir)

            # 解压 deb 到 临时文件夹
            unar(archive_path, tmp_dir)

            # 解压 data.tar.gz 到 目标文件夹
            data_file_path = find_data_tar_gz(tmp_dir)
            unar(data_file_path, target_dir)

            # 删除临时文件夹
            shutil.rmtree(tmp_dir)
        # 源码
        else:
            unar(archive_path, target_dir)
    except Exception as e:
        logger.error(f"error occurred when decompress {archive_path}, error: {e}")
        logger.error(traceback.format_exc())


def multiple_decompress(src_tar_paths: List[str], bin_tar_paths: List[str]):
    src_tar_paths.extend(bin_tar_paths)
    pool = multiprocessing.Pool(processes=PROCESS_NUM)

    # 多进程并发提取
    results = pool.imap_unordered(decompress, src_tar_paths)
    for _ in tqdm(results, total=len(src_tar_paths[:100]), desc="unar_decompress"):
        pass
    pool.close()
    pool.join()
