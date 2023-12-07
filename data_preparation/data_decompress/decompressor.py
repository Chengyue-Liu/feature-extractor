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


def get_decompress_target_path(path):
    # 获取名称
    repo_dir, file_name = os.path.split(path)
    repo_category_dir, repo_name = os.path.split(repo_dir)
    _, repo_category_name = os.path.split(repo_category_dir)
    if ".orig" in file_name:
        file_name = file_name.split(".orig")[0]
        pacakge_name, repo_version = file_name.split("_")
        return os.path.join(DECOMPRESSED_DEBIAN_FILE_DIR_PATH, repo_category_name, repo_name, repo_version,
                            "source")
    elif file_name.endswith(".tar.gz") or file_name.endswith(".tar.xz"):
        pacakge_name, repo_version = file_name.split("_")
        return os.path.join(DECOMPRESSED_DEBIAN_FILE_DIR_PATH, repo_category_name, repo_name, repo_version,
                            "source")
    elif file_name.endswith(".deb") or file_name.endswith(".udeb"):
        file_name, extension = os.path.splitext(file_name)
        pacakge_name, lib_version_release, package_arch = file_name.split("_")
        if "-" in lib_version_release:
            repo_version, package_release = lib_version_release.split("-", 1)
        else:
            repo_version, package_release = lib_version_release, "0"
        return os.path.join(DECOMPRESSED_DEBIAN_FILE_DIR_PATH, repo_category_name, repo_name, repo_version,
                            "binary",
                            pacakge_name,
                            package_release, package_arch)
    else:
        print(path)
        raise


def find_data_tar_gz(dir_path):
    for root, dirs, files in os.walk(dir_path):
        for f in files:
            if f.startswith("data."):
                f_path = os.path.join(root, f)
                return f_path


def unar_decompress(archive_path, target_dir):
    try:
        command = f"unar {archive_path} -o {target_dir}  -q"
        subprocess.run(command, shell=True, check=True)
    except Exception as e:
        logger.error(f"error occurred when unar {archive_path} to {target_dir}. error: {e}")
        logger.error(traceback.format_exc())


def dpkg_decompress(file_path, target_folder):
    # 检查文件路径和目标文件夹是否存在
    if not os.path.exists(file_path):
        logger.info(f"Error: File '{file_path}' not found.")
        return

    if not os.path.exists(target_folder):
        logger.info(f"Error: Target folder '{target_folder}' not found.")
        return

    # 检查文件扩展名是否为 .deb 或 .udeb
    if not file_path.lower().endswith(('.deb', '.udeb')):
        logger.info(f"Error: Invalid file extension. The file must have a .deb or .udeb extension.")
        return

    # 构造 dpkg-deb 命令
    command = ['dpkg-deb', '-x', file_path, target_folder]

    try:
        # 调用 dpkg-deb 命令进行解压缩
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        logger.info(f"Error: Failed to extract contents. {e}")


def decompress(archive_path):
    try:
        # 获取target_dir
        target_dir = get_decompress_target_path(archive_path)

        # 如果目标文件夹已经存在，跳过
        if os.path.exists(target_dir):
            return
        os.makedirs(target_dir, exist_ok=True)

        # 二进制
        if archive_path.endswith(('.deb', ".udeb")):
            dpkg_decompress(archive_path, target_dir)
        # 源码
        else:
            unar_decompress(archive_path, target_dir)
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
