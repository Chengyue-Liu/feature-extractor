#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
from typing import Set, List

from loguru import logger

from feature_extraction.entities import FileFeature

# @Time : 2023/11/29 16:05
# @Author : Liu Chengyue
specific_files = ["ELF", "DLL", "PE"]

# 不扫描的文件后缀列表
black_list = ['.crt', '.key', '.debug', '.pem', '.gox', '.html', '.jpg', '.mp3', '.gz', '.rsrc', '.md', '.cpp',
              '.hpp', '.cmake', '.README', '.tgz', '.jp2', '.jxr', '.ri']
while_list = ['.img', ]


def is_elf_file(file_path):
    # try:
    #     with open(file_path, 'rb') as f:
    #         # ELF 文件的前四个字节为 b'\x7fELF'
    #         return f.read(4) == b'\x7fELF'
    # except IOError:
    #     return False

    try:
        file_extension = os.path.splitext(os.path.basename(file_path))[-1]
        if file_extension in while_list:
            return True
        if file_extension in black_list:
            return False

        file_info = subprocess.check_output(["file", file_path], timeout=1).decode("utf-8")
        # 判断是否包含关键信息
        if any(specific_file in file_info for specific_file in specific_files):
            logger.debug(f'file_info: {file_path}: {file_info}')
            return True
        else:
            return False
    except Exception as e:
        logger.error(e)
        return False


def extract_elf_strings(path: str) -> List[str]:
    cmd = f"strings {path}"
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = proc.stdout.decode()
    strings = list({s for s in output.split("\n") if len(s) >= 5})
    return strings
