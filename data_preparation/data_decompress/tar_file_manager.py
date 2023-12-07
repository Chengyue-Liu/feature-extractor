#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from loguru import logger

from settings import DEBIAN_TAR_FILE_DIR_PATH
from tqdm import tqdm


# @Time : 2023/11/21 16:48
# @Author : Liu Chengyue
def is_src_package(file_name):
    if (".orig" in file_name and "orig-" not in file_name and not file_name.endswith('sc')) \
            or (file_name.endswith('.tar.gz') and not file_name.endswith('.debian.tar.gz')) \
            or (file_name.endswith('.tar.xz') and not file_name.endswith('.debian.tar.xz')):
        return True

    return False


def is_bin_package(file_name):
    if file_name.endswith('.deb') or file_name.endswith('.udeb'):
        return True

    return False


def get_tar_file_paths():
    src_tar_paths = []
    bin_tar_paths = []
    with tqdm(total=1390665, desc="get_tar_file_paths") as pbar:
        for root, dirs, files in os.walk(DEBIAN_TAR_FILE_DIR_PATH):
            for f_name in files:
                pbar.update(1)

                f_path = os.path.join(root, f_name)
                if is_src_package(f_name):
                    src_tar_paths.append(f_path)
                elif is_bin_package(f_name):
                    bin_tar_paths.append(f_path)

    logger.success(f"src_tar_paths num: {len(src_tar_paths)}, bin_tar_paths num: {len(bin_tar_paths)}")
    return src_tar_paths, bin_tar_paths


def filter_bin_tar_paths(bin_tar_paths):
    filtered_bin_tar_paths = []
    for bin_tar_path in bin_tar_paths:
        skip = False
        for arch in {"_armel", "_armhf", "_i386", "_mips", "_ppc", "_s390", "_riscv"}:
            if arch in os.path.split(bin_tar_path)[-1]:
                skip = True
                break

        if skip:
            continue

        filtered_bin_tar_paths.append(bin_tar_path)

    logger.info(f"{len(bin_tar_paths)} ---> {len(filtered_bin_tar_paths)}")