from binaryninja import *
from loguru import logger
from tqdm import tqdm

from feature_extraction.bin_feature_extractors.bin_feature_extractor import BinFeatureExtractor
from feature_extraction.entities import FileFeature


class BinCfgExtractor(BinFeatureExtractor):
    def extract_file_feature(self, path: str) -> FileFeature:
        file_feature = FileFeature(
            file_path=path,
            feature=[]
        )

        return file_feature


def ninja_binary(path):
    logger.info(f"parsing binary view ...")
    bv = BinaryViewType.get_view_of_file(path)
    for func in tqdm(bv.functions, total=len(bv.functions), desc="walk functions"):
        # 获取函数的基本块（Basic Block）
        basic_blocks = func.basic_blocks

        # 打印基本块的信息
        for bb in tqdm(basic_blocks, total=len(basic_blocks), desc="walk basic_blocks"):
            logger.info(f"Basic Block {bb.index} in Function {func.name}: {bb}")

            # 获取基本块的出边（outgoing edges）
            outgoing_edges = bb.outgoing_edges

            # 打印基本块的出边信息
            for edge in tqdm(outgoing_edges, total=len(outgoing_edges), desc="walk basic_blocks"):
                logger.info(f"  Outgoing Edge: {edge.source} -> {edge.target}")


if __name__ == '__main__':
    demo = "/Users/liuchengyue/Desktop/works/feature_analysis/feature-extractor/test_cases/decompressed_files/o/openssl/1.1.1n/binary/0+deb10u3/0+deb10u3/data/usr/bin/openssl"
    ninja_binary(demo)
