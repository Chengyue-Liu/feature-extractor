#!/usr/bin/env python
# -*- coding: utf-8 -*-


# @Time : 2023/11/3 11:37
# @Author : Liu Chengyue
# @File : entities.py
# @Software: PyCharm
import dataclasses
import json
from typing import List, Dict

from settings import EDGE_NUM_THRESHOLD
from utils.json_util import load_from_json
from uuid import uuid4


@dataclasses.dataclass
class Repository:
    def __init__(self,
                 repo_path, repo_type,
                 repo_id, version_id, repo_name, repo_version,
                 uuid=None,
                 version_key=None,
                 package_name=None,
                 release_id=None, arch_id=None, repo_release=None, repo_arch=None,
                 target_src_file_num=0,
                 elf_paths=None):
        self.uuid = uuid if uuid else str(uuid4())

        # basic
        self.repo_path = repo_path
        self.repo_type = repo_type

        # repo
        self.repo_id = repo_id
        self.repo_name = repo_name

        # version
        self.version_id = version_id
        self.version_key = version_key if version_key else f"{self.repo_id}-{self.version_id}"
        self.repo_version = repo_version

        # package, release
        self.package_name = package_name
        self.release_id = release_id
        self.repo_release = repo_release

        # arch
        self.arch_id = arch_id
        self.repo_arch = repo_arch

        # file
        self.target_src_file_num = target_src_file_num  # 源码目标文件的数量
        self.elf_paths = elf_paths  # elf文件路径

    @classmethod
    def init_repository_from_json_data(cls, json_data):
        repository = Repository(
            uuid=json_data["uuid"],
            repo_path=json_data["repo_path"],
            repo_type=json_data["repo_type"],
            repo_id=json_data["repo_id"],
            repo_name=json_data["repo_name"],
            repo_version=json_data["repo_version"],
            package_name=json_data["package_name"],
            version_id=json_data["version_id"],
            version_key=json_data["version_key"],
            repo_release=json_data["repo_release"],
            release_id=json_data["release_id"],
            repo_arch=json_data["repo_arch"],
            arch_id=json_data["arch_id"],
            target_src_file_num=json_data["target_src_file_num"],
            elf_paths=json_data["elf_paths"],
        )
        return repository

    @classmethod
    def init_repositories_from_json_file(cls, file_path):
        json_repositories = load_from_json(file_path)
        repositories = []
        for json_repository in json_repositories:
            repositories.append(cls.init_repository_from_json_data(json_repository))
        return repositories

    def custom_serialize(self):
        return {
            "uuid": self.uuid,
            "repo_path": self.repo_path,
            "repo_type": self.repo_type,
            "repo_id": self.repo_id,
            "version_id": self.version_id,
            "version_key": self.version_key,
            "release_id": self.release_id,
            "arch_id": self.arch_id,
            "repo_name": self.repo_name,
            "repo_version": self.repo_version,
            "package_name": self.package_name,
            "repo_release": self.repo_release,
            "repo_arch": self.repo_arch,
            "target_src_file_num": self.target_src_file_num,
            "elf_paths": self.elf_paths
        }


@dataclasses.dataclass
class FileFeature:
    def __init__(self, file_path: str, feature):
        self.file_path: str = file_path
        self.feature = feature

    def custom_serialize(self):
        return {
            "file_path": self.file_path,
            "feature": self.feature,
        }

    @classmethod
    def init_file_feature_from_json_data(cls, json_data):
        return FileFeature(
            file_path=json_data['file_path'],
            feature=json_data['feature']
        )


@dataclasses.dataclass
class RepoFeature:
    def __init__(self, repository: Repository, file_features: List[FileFeature]):
        self.repository: Repository = repository
        self.file_features: List[FileFeature] = file_features

    def custom_serialize(self):
        return {
            "repository": self.repository.custom_serialize(),
            "file_features": [ff.custom_serialize() for ff in self.file_features],
        }

    @classmethod
    def init_repo_feature_from_json_file(cls, file_path):
        with open(file_path) as f:
            data = json.load(f)
            repository = Repository.init_repository_from_json_data(data["repository"])
            file_features = [FileFeature.init_file_feature_from_json_data(file_feature_json) for file_feature_json in
                             data['file_features']]
            return RepoFeature(
                repository=repository,
                file_features=file_features
            )

    @classmethod
    def init_repo_feature_from_merged_json_file(cls, file_path):
        repos = []
        with open(file_path) as f:
            datas = json.load(f)
            for data in datas:
                repository = Repository.init_repository_from_json_data(data["repository"])
                file_features = [FileFeature.init_file_feature_from_json_data(file_feature_json) for file_feature_json
                                 in
                                 data['file_features']]
                repos.append(RepoFeature(
                    repository=repository,
                    file_features=file_features
                ))
        return repos


from binaryninja import Function, BasicBlock


class BasicBlockFeature:
    """
    BasicBlock
    index： 基本块的索引，表示在函数中的顺序位置。
    start： 基本块的起始地址。
    end： 基本块的结束地址。
    length： 基本块的长度（以字节为单位）。
    incoming_edges： 进入基本块的边。
    outgoing_edges： 从基本块出去的边。
    instructions： 基本块中的指令列表。
    function： 包含该基本块的函数对象。
    arch： 与基本块相关的体系结构。
    low_level_il： 低级中间表示（Low Level Intermediate Language）的表示，用于分析和修改基本块的代码。
    medium_level_il： 中级中间表示（Medium Level Intermediate Language）的表示。
    high_level_il： 高级中间表示（High Level Intermediate Language）的表示。



    Edge
    source： 连接的起始基本块。
    target： 连接的目标基本块。
    type： 连接的类型。可以是以下枚举值之一：
        ControlFlowEdgeType.UnconditionalBranch: 无条件分支。
        ControlFlowEdgeType.TrueBranch: 条件分支的真分支。
        ControlFlowEdgeType.FalseBranch: 条件分支的假分支。
        ControlFlowEdgeType.IndirectBranch: 间接分支。
        ControlFlowEdgeType.CallEdge: 函数调用。
    back_edge： 一个布尔值，指示是否是循环中的反向边。
        branch_type： 如果连接是条件分支，表示分支的类型。可以是以下枚举值之一：
        BranchType.TrueBranch: 条件分支的真分支。
        BranchType.FalseBranch: 条件分支的假分支。
        BranchType.UnconditionalBranch: 无条件分支。
    """

    def __init__(self, bb: BasicBlock):
        self.index = int(bb.index)
        self.outgoing_edges = [(int(edge.source.index), int(edge.target.index)) for edge in bb.outgoing_edges]

        # ACFG Attributes
        self.length = bb.length
        self.incoming_edge_num = len(bb.incoming_edges)
        self.outgoing_edge_num = len(bb.outgoing_edges)
        self.instruction_num = bb.instruction_count

    def __repr__(self):
        return f"BasicBlock({self.index}), edge_num: {len(self.outgoing_edges)}"

    def custom_serialize(self):
        return {
            "index": self.index,
            "length": self.length,
            "incoming_edge_num": self.incoming_edge_num,
            "outgoing_edge_num": self.outgoing_edge_num,
            "instruction_num": self.instruction_num,
            "outgoing_edges": [f"{edge[0]}-{edge[1]}" for edge in self.outgoing_edges],
        }


class FunctionFeature:
    """
    Function

        name： 函数的名称。
        start： 函数的起始地址。
        end： 函数的结束地址。
        platform： 函数的平台信息。
        calling_convention： 函数的调用约定。
        arch： 与函数相关的体系结构。
        basic_blocks： 函数包含的基本块列表。
        parameters： 函数的参数列表。
        return_type： 函数的返回类型。
        symbol： 函数的符号信息。
        analysis_performance_info： 用于性能分析的信息。
        comment： 函数的注释。
        analysis_info： 有关函数分析状态的信息。
        low_level_il： 低级中间表示（Low Level Intermediate Language）的表示，用于分析和修改函数的代码。
        medium_level_il： 中级中间表示（Medium Level Intermediate Language）的表示。
        high_level_il： 高级中间表示（High Level Intermediate Language）的表示。
    """

    def __init__(self, function_name, func: Function):
        # 函数名称
        self.function_name = function_name

        # 其他信息
        self.caller_num = len(func.callers)
        self.callee_num = len(func.callees)
        self.parameter_num = len(func.parameter_vars)
        self.basic_block_num = len(func.basic_blocks)
        self.edge_num = 0

        # basic blocks
        self.basic_blocks: List[BasicBlockFeature] = []
        for bb in func.basic_blocks:
            self.basic_blocks.append(BasicBlockFeature(bb))
            self.edge_num += len(bb.outgoing_edges)

    def __repr__(self):
        return f"{self.function_name}, {self.basic_blocks}"

    def custom_serialize(self):
        json_data = dict()

        # 如果至少5个边，保存CFG
        if len(self.basic_blocks) >= EDGE_NUM_THRESHOLD:
            json_data = {
                "function_name": self.function_name,
                "caller_num": self.caller_num,
                "callee_num": self.callee_num,
                "parameter_num": self.parameter_num,
                "basic_block_num": self.basic_block_num,
                "edge_num": self.edge_num,
                "basic_blocks": [bbf.custom_serialize() for bbf in self.basic_blocks]
            }

        return json_data if json_data else None
