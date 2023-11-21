#!/usr/bin/env python
# -*- coding: utf-8 -*-


# @Time : 2023/11/3 11:41
# @Author : Liu Chengyue
# @File : constants.py
# @Software: PyCharm
C_EXTENSION_SET = {
    # c
    ".c",
    ".C",
    ".h",
    ".H",
}

CPP_EXTENSION_SET = {
    # c++
    ".cc",
    ".CC",
    ".hh",
    ".HH",

    ".cp",
    ".CP",
    ".hp",
    ".HP",

    ".cpp",
    ".CPP",
    ".hpp",
    ".HPP",

    ".cxx",
    ".CXX",
    ".hxx",
    ".HXX",

    ".c++",
    ".C++",
    ".h++",
    ".H++"
}

TARGET_FILE_EXTENSION_SET = {*C_EXTENSION_SET, *CPP_EXTENSION_SET}
