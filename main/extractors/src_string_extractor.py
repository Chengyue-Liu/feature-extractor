#!/usr/bin/env python
# -*- coding: utf-8 -*-


# @Time : 2023/11/3 11:29
# @Author : Liu Chengyue
# @File : source_code_string_extractor.py
# @Software: PyCharm
from main.entities import FileFeature
from main.extractors.extractor import FeatureExtractor, NodeType


class SrcStringExtractor(FeatureExtractor):

    def extract_file_feature(self, file_path, node) -> FileFeature:

        # 提取字符串
        strings = self.traverse_node(node)

        # 组成特征
        file_feature = FileFeature(
            file_path=file_path,
            features=strings

        )
        return file_feature

    def traverse_node(self, node):
        function_names = []
        stack = []  # 使用栈来模拟递归调用
        stack.append(node)

        while stack:
            current_node = stack.pop()

            # 处理当前节点
            # 如果是字符串内容节点（双引号中间的部分）
            if current_node.type in {NodeType.function_declarator, NodeType.function_definition}:
                body_node = node.child_by_field_name('body')
                if not body_node:
                    return

                # 解析函数类型，名称
                identifier_node = node.child_by_field_name('declarator')
                node_type = identifier_node.type
                node_name = self.parse_node_content(identifier_node)[0]
                if node_type == "function_declarator" and node_name.startswith("if ("):
                    return
                elif '\t' in node_name:
                    return

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
