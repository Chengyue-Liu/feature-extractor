import json

from feature_extraction.entities import Repository
from settings import SRC_REPOS_JSON, BIN_REPOS_JSON

src_repos = Repository.init_repositories_from_json_file(SRC_REPOS_JSON)
bin_repos = Repository.init_repositories_from_json_file(BIN_REPOS_JSON)

src_repo_ids = {repo.repo_id for repo in src_repos}
src_version_ids = {f"{repo.repo_id}-{repo.version_id}" for repo in src_repos}

bin_repo_ids = {repo.repo_id for repo in bin_repos}
bin_version_ids = {f"{repo.repo_id}-{repo.version_id}" for repo in bin_repos}

print("repo_ids.difference", len(src_repo_ids.difference(bin_repo_ids)))
print("version_ids.difference", len(src_version_ids.difference(bin_version_ids)))
