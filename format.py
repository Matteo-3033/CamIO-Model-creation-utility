import argparse
from typing import Tuple

from format_edges import format_edges
from format_nodes import format_nodes
from format_pois import format_pois

import json


def parse_n1(node: str) -> Tuple[int, float, float]:
    l = node.split(",")

    index = int(l[0].strip().split("(")[1])
    lat = float(l[1].strip())
    lon = float(l[2].strip().split(")")[0])

    return index, lat, lon


def main(name: str, n1: Tuple[int, float, float], d_m: float) -> None:
    meters_per_pixel = format_nodes(n1[0], d_m)
    format_edges()
    format_pois(*n1)

    graph = dict()

    with open("out/nodes.json", "r") as f:
        graph["nodes"] = json.load(f)

    with open("out/edges.json", "r") as f:
        graph["edges"] = json.load(f)

    with open("out/streets.json", "r") as f:
        graph["streets"] = json.load(f)

    with open("out/pois.json", "r") as f:
        graph["pois"] = json.load(f)

    with open("out/nodes_features.json", "r") as f:
        graph["nodes_features"] = json.load(f)

    with open("out/edges_features.json", "r") as f:
        graph["edges_features"] = json.load(f)

    n1_coords = graph["nodes"][n1[0]]

    model = {
        "name": name,
        "template_image": "TODO",
        "meters_per_pixel": meters_per_pixel,
        "latlon_reference": {
            "coords": n1_coords,
            "lat": n1[1],
            "lon": n1[2],
        },
        "graph": graph,
        "context": {
            "name": "TODO",
            "description": "TODO",
            "scale": "TODO",
            "north": "TODO",
            "south": "TODO",
            "west": "TODO",
            "east": "TODO",
        },
    }

    with open("out/model.json", "w") as f:
        json.dump(model, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Format data")

    parser.add_argument("--name", help="Name of the map", type=str, required=True)
    parser.add_argument(
        "--n1",
        help="Index, latitude and longitude of a node the first node in src/nodex.txt is connected to, eg: (1, 40.748578611672315, -73.98532107282095)",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--d_m",
        help="Distance in meters between n1 and the first node in src/nodex.txt",
        type=float,
        required=True,
    )

    args = parser.parse_args()

    main(args.name, parse_n1(args.n1), args.d_m)
