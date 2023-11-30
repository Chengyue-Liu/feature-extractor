import json

from settings import SRC_REPOS_JSON, BIN_REPOS_JSON

with open(SRC_REPOS_JSON) as f:
    repos = json.load(f)
    print(len(repos))

with open(BIN_REPOS_JSON) as f:
    repos = json.load(f)
    print(len(repos))
