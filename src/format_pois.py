import json
import random
import time
from typing import Any, Dict, List, Optional, Set
import re
from datetime import datetime

from graph import (
    Coords,
    Edge,
    load_graph,
    latlng_to_coords,
    LatLngReference,
    GraphEncoder,
)
from utils import *

seed = time.time()
random.seed(seed)
print(f"Seed: {seed}")


def get_edge(edges: List[Edge], coords: Coords) -> Edge:
    edge = min(
        filter(
            lambda edge: edge.contains(coords.project_on(edge)),
            edges,
        ),
        key=lambda edge: coords.distance_to_line(edge),
    )
    return edge


keys_to_remove = [
    "country",
    "country_code",
    "state",
    "state_code",
    "county",
    "postcode",
    "details",
    "state_code",
    "suburb",
    "formatted",
    "address_line1",
    "address_line2",
    "datasource",
    "place_id",
    "owner details",
    "brand_details",
    "operator_details",
    "network_details",
    "ref_other",
    "wiki_and_media",
    "name_international",
    "ref",
    "ref_other",
    "ele",
    "heritage",
    "opening_hours_covid19",
    "website_other",
    "geometry",
    "lat",
    "lon",
]

public_transports = {
    "train": "station",
    "subway": "station",
    "bus": "stop",
    "tram": "stop",
}


def format_categories(categories: List[str]) -> List[str]:
    res: Set[str] = set()
    freq: Dict[str, int] = dict()

    for category in categories:
        fields = category.split(".")
        freq[fields[0]] = freq.get(fields[0], 0) + 1

    for category in categories:
        fields = category.split(".")

        if category.startswith("wheelchair") or category.startswith("internet_access"):
            continue

        tmp = ""
        for i in range(len(fields) - 1):
            tmp += fields[i]
            if tmp in res:
                res.remove(tmp)
            tmp += "."

        if fields[-1] in public_transports.keys():
            res.add(f"{fields[-1]}_{public_transports[fields[-1]]}")
            res.add("public_transport")
        elif len(list(filter(lambda x: x.startswith(category), res))) == 0:
            res.add(category)

    return list(res)


poi_accessibility_defaults = {
    "wheelchair_accessible": False,
    "tactile_paving": False,
    "tactile_map": False,
    "reception": False,
    "stairs": False,
    "elevator": False,
}
poi_accessibility_values_commercial = {
    "wheelchair_accessible": [True, False],
    "tactile_paving": [False],
    "tactile_map": [False],
    "reception": [False],
    "stairs": [True, False],
    "elevator": [False],
}
poi_accessibility_values_office = {
    "wheelchair_accessible": [True, False],
    "tactile_paving": [True, False],
    "tactile_map": [False],
    "reception": [True, False],
    "stairs": [True, False],
    "elevator": [True, False],
}


def format_facilities(facilities: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    facilities = {k.replace(" ", "_"): v for k, v in facilities.items()}

    if "wheelchair" in facilities:
        del facilities["wheelchair"]
    if "wheelchair_details" in facilities:
        del facilities["wheelchair_details"]

    for key in poi_accessibility_defaults.keys():
        if key in facilities:
            del facilities[key]

    if len(facilities.keys()) == 0:
        return None
    return facilities


def format_accessibility(
    categories: List[str], accessibility: Dict[str, Any], facilities: Dict[str, Any]
) -> Dict[str, Any]:
    facilities = {k.replace(" ", "_"): v for k, v in facilities.items()}
    accessibility = {k.replace(" ", "_"): v for k, v in accessibility.items()}

    if "wheelchair" in facilities:
        accessibility["wheelchair_accessible"] = facilities["wheelchair"]
    if "wheelchair_details" in facilities:
        accessibility["wheelchair_accessible"] = facilities["wheelchair_details"][
            "condition"
        ]

    for key in poi_accessibility_defaults.keys():
        if key in accessibility:
            accessibility[key] = accessibility[key]
        elif key in facilities:
            accessibility[key] = facilities[key]
        else:
            accessibility[key] = get_random_accessibility_values(categories, key)

    return accessibility


def get_random_accessibility_values(categories: List[str], key: str) -> Any:
    categories = [category.split(".")[0] for category in categories]

    if "catering" in categories or "commercial" in categories:
        return random.choice(poi_accessibility_values_commercial[key])

    if "office" in categories or "education" in categories:
        return random.choice(poi_accessibility_values_office[key])

    return poi_accessibility_defaults[key]


def format_opening_hours(opening_hours: str) -> str:
    def convert_to_am_pm(time_24h):
        time_obj = datetime.strptime(time_24h, "%H:%M")
        return time_obj.strftime("%I:%M %p").lstrip("0")

    if "24/7" in opening_hours:
        return "Open 24 hours, 7 days a week"

    try:
        pattern = r"(\w+(?:-\w+)?(?:,\w+(?:-\w+)?)*)?\s*(\d{2}:\d{2})-(\d{2}:\d{2})"
        matches = re.findall(pattern, opening_hours)

        if not matches:
            raise Exception("No matches found")

        result = []

        for match in matches:
            days = match[0].strip() if match[0] else ""
            start_time = convert_to_am_pm(match[1])
            end_time = convert_to_am_pm(match[2])

            if days:
                result.append(f"{days} {start_time} - {end_time}")
            else:
                result.append(f"{start_time} - {end_time}")

    except Exception:
        print(f"Could not parse opening hours: {opening_hours}")
        return ""

    return "; ".join(result)


def format_pois(
    src_dir: str,
    feets_per_inch: float,
    reference_node_index: int,
    reference_node_lat: float,
    reference_node_lon: float,
) -> None:
    poi_min_distance = POI_TO_POI_MIN_DISTANCE * feets_per_inch
    node_min_distance = POI_TO_NODE_MIN_DISTANCE * feets_per_inch
    edge_max_distance = POI_TO_EDGE_MAX_DISTANCE * feets_per_inch

    with open(f"{src_dir}/pois.json", "r") as f:
        pois = json.load(f)["features"]

    nodes, edges, streets = load_graph(f"{src_dir}/{src_dir}_out")
    reference_node = LatLngReference(
        nodes[reference_node_index].coords,
        reference_node_lat,
        reference_node_lon,
    )

    edges_index = {(e[0].index, e[1].index): i for i, e in enumerate(edges)}

    res: List[Dict[str, Any]] = list()
    done: Set[str] = set()

    for i, poi in enumerate(pois):
        poi = poi["properties"]

        if "name" not in poi:
            print(f"Skipping POI without name at index {i}")
            continue

        if poi["name"] in done:
            print(f"Skipping duplicate {poi['name']}")
            continue

        if "street" not in poi:
            print(f"Skipping POI without street: {poi['name']}")
            continue

        coords = latlng_to_coords(reference_node, Coords(poi["lat"], poi["lon"]))

        try:
            edge = get_edge(streets[poi["street"]], coords)
            poi["edge"] = edges_index[(edge[0].index, edge[1].index)]
        except Exception:
            print(f"Could not find edge for {poi['name']}")
            continue

        for key in keys_to_remove:
            if key in poi:
                del poi[key]

        if "categories" in poi:
            poi["categories"] = format_categories(poi["categories"])

        if "website" in poi:
            if "contact" not in poi:
                poi["contact"] = dict()
            poi["contact"]["website"] = poi["website"]
            del poi["website"]

        poi["accessibility"] = format_accessibility(
            poi.get("categories", list()),
            poi.get("accessibility", dict()),
            poi.get("facilities", dict()),
        )

        if "facilities" in poi:
            poi["facilities"] = format_facilities(poi["facilities"])
            if poi["facilities"] is None:
                del poi["facilities"]

        if "opening_hours" in poi:
            poi["opening_hours"] = format_opening_hours(poi["opening_hours"])

        closest_node = min(
            [edge[0], edge[1]], key=lambda node: node.distance_to(coords)
        )

        if closest_node.distance_to(coords) < node_min_distance:
            location_description = closest_node.get_position_description(poi["street"])
        else:
            location_description = edge.get_position_description(poi["street"])
        poi["location_description"] = location_description

        if (distance := closest_node.distance_to(coords)) < node_min_distance:
            direction = edge.versor
            direction *= 1 if edge.node1 == closest_node else -1
            coords = coords + direction * (node_min_distance - distance) * 3 / 2

        if (distance := coords.distance_to_line(edge)) > edge_max_distance:
            direction = (coords.project_on(edge) - coords).normalized()
            coords = coords + direction * (distance - edge_max_distance)

        poi["coords"] = coords

        res.append(poi)
        done.add(poi["name"])

    res.sort(key=lambda x: x["name"])

    for node in nodes:
        for i, poi in enumerate(res):
            if node.distance_to(poi["coords"]) < node_min_distance:
                print(f"{poi['name']} ({i}) is too close to node {node.index}")

    for i, poi in enumerate(res):
        for j in range(i + 1, len(res)):
            if res[j]["coords"].distance_to(poi["coords"]) < poi_min_distance:
                print(f"{poi['name']} ({i}) is too close to {res[j]['name']} ({j})")

    with open(f"{src_dir}/{src_dir}_out/pois.json", "w") as f:
        json.dump(res, f, indent=4, cls=GraphEncoder)
