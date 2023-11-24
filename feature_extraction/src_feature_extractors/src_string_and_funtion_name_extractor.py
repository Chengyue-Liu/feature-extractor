#!/usr/bin/env python
# -*- coding: utf-8 -*-


# @Time : 2023/11/3 11:29
# @Author : Liu Chengyue
# @File : source_code_string_extractor.py
# @Software: PyCharm


from feature_extraction.entities import FileFeature
from feature_extraction.src_feature_extractors.src_feature_extractor import SrcFeatureExtractor, NodeType


class SrcStringAndFunctionNameExtractor(SrcFeatureExtractor):

    def extract_file_feature(self, file_path, root_node) -> FileFeature:

        # 提取字符串
        strings = self.parse_strings(root_node)

        function_names = self.parse_function_names(root_node)

        # 组成特征
        file_feature = FileFeature(
            file_path=file_path,
            features={
                "strings": list(set(strings)),
                "function_names": list(set(function_names)),
            }

        )
        return file_feature

    def parse_strings(self, node):
        strings = []
        flag = False  # 上一个是不是字符串，主要用来合并多行字符串
        stack = [node]  # 使用栈来模拟递归调用

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

    def parse_function_names(self, node):
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
