import json

with open("/workspace/SDS-in-a-box/sds_in_a_box/lambdas/file-indexer/config.json") as f:
    data = json.load(f)

pattern = data[0]['pattern']


for field in pattern: