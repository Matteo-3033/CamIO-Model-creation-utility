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


with open("src/pois.json", "r") as f:
    pois = json.load(f)["features"]

keys = [
    "country",
    "country_code",
    "state",
    "state_code",
    "county",
    "postcode",
    "details",
    "state_code",
    "formatted",
    "address_line1",
    "address_line2",
    "datasource",
    "place_id",
    "brand_details",
    "operator_details",
    "network_details",
    "ref_other",
    "wiki_and_media",
    "name_international",
    "website",
    "ref_other",
    "geometry",
    "distance",
    "edge",
]

res: List[Dict[str, Any]] = list()

for poi in pois:
    poi = poi["properties"]

    for key in keys:
        if key in poi:
            del poi[key]

    res.append(poi)

text = ""
for poi in res:
    text += str_dict(poi) + "\n\n"

with open("poi_new_york.txt", "w") as f:
    f.write(text)
