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

def get_category(lib_name):
    if lib_name.startswith("lib"):
        category = lib_name[:4]
    else:
        category = lib_name[:1]
    return category


def get_decompress_target_path(path):
    # 获取名称
    file_name = os.path.split(path)[-1]
    if ".orig" in file_name:
        file_name = file_name.split(".orig")[0]
        lib_name, lib_version = file_name.split("_")
        return os.path.join(DECOMPRESSED_DEBIAN_FILE_DIR_PATH, get_category(lib_name), lib_name, lib_version, "source")
    elif file_name.endswith(".tar.gz") or file_name.endswith(".tar.xz"):
        lib_name, lib_version = file_name.split("_")
        return os.path.join(DECOMPRESSED_DEBIAN_FILE_DIR_PATH, get_category(lib_name), lib_name, lib_version, "source")
    elif file_name.endswith(".deb") or file_name.endswith(".udeb"):
        file_name, extension = os.path.splitext(file_name)
        lib_name, lib_version_release, lib_arch = file_name.split("_")
        if "-" in lib_version_release:
            lib_version, lib_release = lib_version_release.split("-", 1)
        else:
            lib_version, lib_release = lib_version_release, "0"
        return os.path.join(DECOMPRESSED_DEBIAN_FILE_DIR_PATH, get_category(lib_name), lib_name, lib_version, "binary",
                            lib_release, lib_release)
    else:
        print(path)
        raise


def find_data_tar_gz(dir_path):
    for root, dirs, files in os.walk(dir_path):
        for f in files:
            if f.startswith("data."):
                f_path = os.path.join(root, f)
                return f_path


def unar(archive_path, target_dir):
    try:
        command = f"unar {archive_path} -o {target_dir}  -q"
        subprocess.run(command, shell=True, check=True)
    except Exception as e:
        logger.error(f"error occurred when unar {archive_path} to {target_dir}. error: {e}")
        logger.error(traceback.format_exc())


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
    for _ in tqdm(results, total=len(src_tar_paths), desc="unar_decompress"):
        pass
    pool.close()
    pool.join()
