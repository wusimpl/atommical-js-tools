import json
import sys

with open(sys.argv[1], 'r') as f:
    data = json.load(f)

# 提取并打印address字段
print(data.get("address", "未找到地址"))
