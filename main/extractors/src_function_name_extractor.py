#!/usr/bin/env python
# -*- coding: utf-8 -*-


# @Time : 2023/11/3 11:29
# @Author : Liu Chengyue
# @File : source_code_string_extractor.py
# @Software: PyCharm
from main.entities import FileFeature
from main.extractors.extractor import FeatureExtractor, NodeType


class SrcFunctionNameExtractor(FeatureExtractor):

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
        strings = []
        flag = False  # 上一个是不是字符串，主要用来合并多行字符串
        stack = []  # 使用栈来模拟递归调用
        stack.append(node)

        while stack:
            current_node = stack.pop()

            # 处理当前节点
            # 如果是字符串内容节点（双引号中间的部分）
            if current_node.type == NodeType.string_content.value:
                # 解析文本
                node_content_lines = self.parse_node_content(current_node)
                # 获取字符串内容
                string_content = node_content_lines[0]
                # 如果上一个节点是字符串就合并
                if flag:
                    strings[-1] = strings[-1] + string_content
                # 如果不是就直接添加
                else:
                    strings.append(string_content)
                # 标记上一个节点是字符串
                flag = True
            # 如果不是字符串节点
            else:
                # 判断 是否是 " 或者 字符串节点（带双引号的字符串内容），如果不是，改变标记为False
                if not (current_node.type == '"' or current_node.type == NodeType.string_literal.value):
                    flag = False

                # 继续判断，如果是开头的 include 声明，直接跳过
                if current_node.type == NodeType.preproc_include.value:
                    continue

            # 将子节点压入栈中
            stack.extend(reversed(current_node.children))
        return strings
