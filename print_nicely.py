import json
from typing import Any, Dict, List


def str_dict(d: Dict[Any, Any], indent: int = 0) -> str:
    res = ""

    for key, value in d.items():
        res += " " * indent + str(key) + ": "
        if isinstance(value, dict):
            res += "\n" + str_dict(value, indent + 4)
        elif isinstance(value, list):
            res += "[\n"
            for item in value:
                res += " " * (indent + 4) + str(item) + ",\n"
            if len(value) > 0:
                res = res[:-2] + "\n"
            res += " " * indent + "]\n"
        else:
            res += str(value) + "\n"

    return res


with open("out/pois.json", "r") as f:
    pois = json.load(f)

keys = [
    # "coords",
    # "edge"
]

with open("out/edges.json", "r") as f:
    edges = json.load(f)

for poi in pois:
    for key in keys:
        if key in poi:
            del poi[key]

    if "edge" in poi:
        edge = edges[poi["edge"]]
        poi["edge"] = f"n{edge[0]} - n{edge[1]}"

text = ""
for poi in pois:
    text += str_dict(poi) + "\n\n"

with open("pois.txt", "w") as f:
    f.write(text)
