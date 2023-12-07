import multiprocessing
import os
import shutil

from loguru import logger
from tqdm import tqdm


def get_paths(root_dir):
    dir_paths = []
    for root, dirs, files in os.walk(root_dir):
        for dir in dirs:
            dir_paths.append(os.path.join(root, dir))
            if (num := len(dir_paths)) % 1000 == 0:
                num = num/1000
                logger.info(f"get_paths: {num}k")
    dir_paths = list(reversed(dir_paths))
    return dir_paths


def remove_all(root_dir):
    logger.info(f"get paths")
    dir_paths = get_paths(root_dir)

    for dir_path in tqdm(dir_paths, total=len(dir_paths), desc="remove dirs"):
        shutil.rmtree(dir_path, ignore_errors=True)


if __name__ == '__main__':
    root_dir_path = "/Users/liuchengyue/Desktop/demo"
    remove_all(root_dir_path)
