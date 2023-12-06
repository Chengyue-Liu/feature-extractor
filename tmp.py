import ijson
from tqdm import tqdm

from feature_extraction.entities import Repository, FileFeature, RepoFeature

path = "/Users/liuchengyue/Desktop/works/feature_analysis/feature-extractor/features/BinStringExtractor/BinStringEvaluator.json"
with open(path, 'rb') as file:
    repo_features = []
    for item in ijson.items(file, 'item'):
        repository = Repository.init_repository_from_json_data(item["repository"])
        file_features = [FileFeature.init_file_feature_from_json_data(file_feature_json) for file_feature_json in
                         item['file_features']]
        repo_features.append(RepoFeature(
            repository=repository,
            file_features=file_features
        ))
        print(repository.repo_id)