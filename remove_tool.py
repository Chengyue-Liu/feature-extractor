import os
import shutil

from loguru import logger
from tqdm import tqdm


def get_paths(root_dir):
    file_paths = []
    dir_paths = []
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            file_paths.append(os.path.join(root, f))

        for dir in dirs:
            dir_paths.append(os.path.join(root, dir))
    dir_paths = list(reversed(dir_paths))
    return file_paths, dir_paths


def remove_all(root_dir):
    logger.info(f"get paths")
    file_paths, dir_paths = get_paths(root_dir)
    for file_path in tqdm(file_paths, total=len(file_paths), desc="remove file"):
        try:
            os.remove(file_path)
        except:
            continue

    for dir_path in tqdm(dir_paths, total=len(dir_paths), desc="remove dirs"):
        shutil.rmtree(dir_path, ignore_errors=True)


if __name__ == '__main__':
    root_dir_path = input()
    remove_all(root_dir_path)
