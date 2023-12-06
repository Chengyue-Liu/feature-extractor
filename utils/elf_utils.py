#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
from typing import Set, List

from feature_extraction.entities import FileFeature


# @Time : 2023/11/29 16:05
# @Author : Liu Chengyue

def is_elf_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            # ELF 文件的前四个字节为 b'\x7fELF'
            return f.read(4) == b'\x7fELF'
    except IOError:
        return False

def extract_elf_strings(path: str) -> List[str]:
    cmd = f"strings {path}"
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = proc.stdout.decode()
    strings = list({s for s in output.split("\n") if len(s) >= 5})
    return strings
