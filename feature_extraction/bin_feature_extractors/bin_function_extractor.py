import collections

from binaryninja import *
from loguru import logger
from tqdm import tqdm

from feature_extraction.bin_feature_extractors.bin_feature_extractor import BinFeatureExtractor
from feature_extraction.entities import FileFeature, FunctionFeature, BasicBlockFeature


class BinFunctionExtractor(BinFeatureExtractor):
    def extract_file_feature(self, path: str) -> FileFeature:
        function_names, fcg_dict, function_features = ninja_binary(path)
        file_feature = FileFeature(
            file_path=path,
            feature={
                "function_names": function_names,
                "fcg": fcg_dict,
                "function_features": function_features
            }
        )
        return file_feature


def ninja_binary(path):
    logger.info(f"parsing binary view ...")
    bv = BinaryViewType.get_view_of_file(path)
    function_names = set()
    fcg_dict = collections.defaultdict(set)
    function_features = []
    for func in tqdm(bv.functions, total=len(bv.functions), desc="walk functions"):
        # fcg
        for callee in func.callees:
            fcg_dict[func.name].add(callee.name)

        # 函数名称
        if not(func.name.startswith("sub_") and len(func.name) == 9):
            function_name = None
        else:
            function_name = func.name
            function_names.add(function_name)

        # feature
        function_feature = FunctionFeature(function_name, func)
        function_features.append(function_feature)
    # 序列化
    function_names = list(function_names)
    fcg_dict = {caller_name: list(callee_names) for caller_name, callee_names in fcg_dict.items()}
    function_features = [ff_json_data for ff in function_features if (ff_json_data := ff.custom_serialize())]
    return function_names, fcg_dict, function_features
    # with open("demo.json", "w") as f:
    #     json_data = [ff_json_data for ff in function_features if (ff_json_data := ff.custom_serialize())]
    #     json.dump(json_data, f, ensure_ascii=False, indent=4)

# if __name__ == '__main__':
#     demo = "/Users/liuchengyue/Desktop/works/feature_analysis/feature-extractor/test_cases/decompressed_files/o/openssl/1.1.1n/binary/openssl/0+deb10u3/amd64/usr/bin/openssl"
#     ninja_binary(demo)
