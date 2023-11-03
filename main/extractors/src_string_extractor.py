#!/usr/bin/env python
# -*- coding: utf-8 -*-


# @Time : 2023/11/3 11:29
# @Author : Liu Chengyue
# @File : source_code_string_extractor.py
# @Software: PyCharm
from main.entities import FileFeature
from main.extractors.extractor import FeatureExtractor, NodeType


class SrcStringExtractor(FeatureExtractor):

    def extract_file_feature(self, file_path) -> FileFeature:
        # 初始化根节点
        node = self.init_root_node(file_path)

        # 提取字符串
        strings = self.extract_strings(node)

        # 组成特征
        file_feature = FileFeature(
            file_path=file_path,
            feature_dict={
                "strings": strings
            }

        )
        return file_feature

    def extract_strings(self, node):
        strings = []
        flag = False
        stack = []  # 使用栈来模拟递归调用
        stack.append(node)

        while stack:
            current_node = stack.pop()
            # 处理当前节点
            if current_node.type == NodeType.string_content.value:
                node_content_lines = self.parse_node_content(current_node)
                string_content = node_content_lines[0]
                if flag:
                    strings[-1] = strings[-1] + string_content
                else:
                    strings.append(string_content)
                flag = True
            else:
                if not (current_node.type == '"' or current_node.type == NodeType.string_literal.value):
                    flag = False

                if current_node.type == NodeType.preproc_include.value:
                    continue

            # 将子节点压入栈中
            stack.extend(reversed(current_node.children))
        return strings
