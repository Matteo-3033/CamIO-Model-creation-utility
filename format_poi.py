import json
from typing import Any, Dict, List

with open("src/poi.json", "r") as f:
    pois = json.load(f)["features"]

with open("out/edges.json", "r") as f:
    edges = json.load(f)

edges_index = {(e[0], e[1]): i for i, e in enumerate(edges)}


keys = [
    "country",
    "country_code",
    "state",
    "state_code",
    "county",
    "postcode",
    "details",
    "lon",
    "lat",
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
]

res: List[Dict[str, Any]] = list()

for poi in pois:
    poi = poi["properties"]

    for key in keys:
        if key in poi:
            del poi[key]

    poi["edge"] = edges_index[(poi["edge"][0], poi["edge"][1])]
    res.append(poi)


with open("out/poi.json", "w") as f:
    json.dump(res, f, indent=4)
