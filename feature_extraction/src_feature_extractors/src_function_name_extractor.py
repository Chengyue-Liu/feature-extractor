#!/usr/bin/env python
# -*- coding: utf-8 -*-
import traceback
from abc import ABC

from loguru import logger

# @Time : 2023/11/3 11:29
# @Author : Liu Chengyue
# @File : source_code_string_extractor.py
# @Software: PyCharm
from feature_extraction.entities import FileFeature
from feature_extraction.src_feature_extractors.base_extractor import SrcFeatureExtractor, NodeType


class SrcFunctionNameExtractor(SrcFeatureExtractor):

    def extract_file_feature(self, file_path, root_node) -> FileFeature:

        # 提取字符串
        function_names = self.traverse_node(root_node)
        # 组成特征
        file_feature = FileFeature(
            file_path=file_path,
            features=list(set(function_names))

        )
        return file_feature

    def traverse_node(self, node):
        function_names = []
        stack = [node]  # 使用栈来模拟递归调用

        while stack:
            current_node = stack.pop()

            # 处理当前节点
            # 如果是字符串内容节点（双引号中间的部分）
            if current_node.type in {NodeType.preproc_include.value,
                                     NodeType.comment.value,
                                     NodeType.m_if,
                                     NodeType.m_ifdef,
                                     NodeType.m_ifndef,
                                     NodeType.m_elif,
                                     NodeType.m_else,
                                     NodeType.m_endif,
                                     }:
                continue

            if current_node.type == NodeType.function_definition.value:
                body_node = current_node.child_by_field_name('body')
                if not body_node:
                    continue

                # 解析函数类型，名称
                identifier_node = current_node.child_by_field_name('declarator')
                node_type = identifier_node.type
                node_name = self.parse_node_content(identifier_node)[0]
                if node_type == "function_declarator" and node_name.startswith("if ("):
                    continue
                elif '\t' in node_name:
                    continue

                node_name = process_node_name(node_name)
                function_names.append(node_name)

            elif current_node.type == NodeType.function_declarator.value:
                declarator_node = current_node.child_by_field_name('declarator')

                # 解析节点类型，名称
                identifier_node = declarator_node.child_by_field_name('declarator')
                if not identifier_node:
                    continue

                node_type = identifier_node.type
                node_name = self.parse_node_content(identifier_node)[0]
                # 这种是识别错了的
                if node_type == "function_declarator":
                    if node_name.startswith("if ("):
                        continue

                node_name = process_node_name(node_name)
                function_names.append(node_name)

            # 将子节点压入栈中
            stack.extend(reversed(current_node.children))
        return function_names


def process_node_name(node_name):
    if "(" in node_name:
        node_name = node_name.split('(')[0]

    node_name = node_name.replace("* ", "")
    return node_name
