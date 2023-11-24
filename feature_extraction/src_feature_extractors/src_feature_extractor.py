#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time : 2023/11/3 11:35
# @Author : Liu Chengyue
# @File : extractor.py
# @Software: PyCharm
import multiprocessing
import os
from abc import abstractmethod
from typing import List

from tqdm import tqdm

from feature_extraction.constants import TARGET_FILE_EXTENSION_SET
from feature_extraction.entities import FileFeature, RepoFeature, Task
from settings import PROCESS_NUM, FEATURE_RESULT_DIR
import enum

from loguru import logger

from feature_extraction.constants import C_EXTENSION_SET, CPP_EXTENSION_SET
from feature_extraction.entities import FileFeature

from tree_sitter import Language, Parser, Node

from settings import LANGUAGE_SO_FILE_PATH
from utils.json_util import dump_to_json


class NodeType(enum.Enum):
    # 识别错误
    error = "ERROR"

    function_declarator = "function_declarator"  # 函数声明
    function_definition = "function_definition"  # 函数定义
    string_literal = 'string_literal'  # 字符串节点
    string_content = 'string_content'  # 字符串内容
    escape_sequence = 'escape_sequence'  # 字符串内容
    preproc_include = 'preproc_include'  # 头文件
    comment = 'comment'  # 注释
    declaration = 'declaration'  # 变量声明
    initializer_list = 'initializer_list'  # 初始化列表
    preproc_def = 'preproc_def'  # 替换宏 #define AAA aaa, 或者普通定义 #define AAA
    extern = 'extern'  # 替换宏 #define AAA aaa, 或者普通定义 #define AAA

    # 六种常见的条件编译宏
    m_if = "#if"
    m_ifdef = "#ifdef"
    m_ifndef = "#ifndef"
    m_elif = "#elif"
    m_else = "#else"
    m_endif = "#endif"


class SrcFeatureExtractor:
    """
    1. 基类
    2. 实现了多进程并发处理多个repo的函数，以及遍历某个repo的所有文件的函数。
    3. 实现了初始化 tree sitter 根节点的方法： node = self.init_root_node(file_path)
    4. 实现了获取某个节点内容的方法： node_content_lines = self.parse_node_content(current_node)

    """

    def __init__(self, tasks: List[Task]):
        self.tasks = tasks
        self.result_dir = os.path.join(FEATURE_RESULT_DIR, self.__class__.__name__)
        os.makedirs(self.result_dir, exist_ok=True)

    @abstractmethod
    def extract_file_feature(self, file_path, root_node: Node) -> FileFeature:
        """
        输入文件地址，返回文件特征

        :param root_node:
        :param file_path:
        :return:
        """

    def extract_repo_feature(self, task: Task):
        """
        提取一个仓库特征的通用方法
        :param task:
        :return:
        """

        # 筛选目标文件
        target_file_paths = [os.path.join(root, f) for root, dirs, files in os.walk(task.repo_path)
                             for f in files
                             if f.endswith(tuple(TARGET_FILE_EXTENSION_SET))]

        # 提取文件特征
        file_features = []
        for path in target_file_paths:
            node = self.init_root_node(path)
            file_feature = self.extract_file_feature(path, node)
            file_features.append(file_feature)

        # 生成仓库特征
        repo_feature = RepoFeature(
            task=task,
            file_features=file_features
        )

        # 保存特征
        result_path = os.path.join(self.result_dir, f"{task.repo_id}-{task.version_id}.json")
        dump_to_json(repo_feature.custom_serialize(), result_path)

    def multiple_run(self):
        """
        多进程提取多个仓库的特征的通用方法
        :return:
        """
        pool = multiprocessing.Pool(processes=PROCESS_NUM)

        results = pool.imap_unordered(self.extract_repo_feature, self.tasks)

        for _ in tqdm(results, total=len(self.tasks), desc="multiple run extract source features"):
            pass
        pool.close()
        pool.join()

    def init_root_node(self, file_path):
        parser = Parser()
        if file_path.endswith(tuple(C_EXTENSION_SET)):
            parser.set_language(Language(LANGUAGE_SO_FILE_PATH, 'c'))
        elif file_path.endswith(tuple(CPP_EXTENSION_SET)):
            parser.set_language(Language(LANGUAGE_SO_FILE_PATH, 'cpp'))
        else:
            raise Exception(f"Unrecognized File Extension in Path: {file_path}")

        # 加载文件
        try:
            with open(file_path) as f:
                self.src_lines = f.readlines()
        except Exception as e:
            if "'utf-8' codec can't decode" in str(e):
                self.can_decode = False
            else:
                logger.error(f'path: {file_path}, error: {e}')
            self.src_lines = []

        self.tree = parser.parse(self.read_src_lines)
        return self.tree.root_node

    def read_src_lines(self, byte_offset, point):
        row, column = point
        if row >= len(self.src_lines) or column >= len(self.src_lines[row]):
            return None
        return self.src_lines[row][column:].encode('utf8')

    def parse_node_content(self, node):
        """

        :param start_point: 起始点
        :param end_point: 结束点
        :return: List[str]
        """
        start_row, start_column = node.start_point
        end_row, end_column = node.end_point

        content_lines = []
        if start_row >= len(self.src_lines):
            return content_lines

        elif start_row == end_row:
            content_lines.append(self.src_lines[start_row][start_column:end_column])
        else:
            # 起始行
            content_lines.append(self.src_lines[start_row][start_column:])
            # 中间行
            content_lines.extend(self.src_lines[start_row + 1:end_row])
            # 结束行
            content_lines.append(self.src_lines[end_row][:end_column + 1])
        return content_lines
