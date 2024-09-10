import argparse
import json
import os
from typing import Tuple

from format_edges import format_edges
from format_nodes import format_nodes
from format_pois import format_pois


def parse_n1(node: str) -> Tuple[int, float, float]:
    l = node.split(",")

    index = int(l[0].strip().split("(")[1])
    lat = float(l[1].strip())
    lon = float(l[2].strip().split(")")[0])

    return index, lat, lon


def main(
    src_dir: str,
    name: str,
    feets_per_inch,
    n0: int,
    n1: Tuple[int, float, float],
    d_feets: float,
) -> None:
    out_dir = f"{src_dir}/{src_dir}_out"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    feets_per_pixel = format_nodes(src_dir, n0, n1[0], d_feets)
    format_edges(src_dir)
    format_pois(src_dir, feets_per_inch, *n1)

    graph = dict()

    with open(f"{out_dir}/nodes.json", "r") as f:
        graph["nodes"] = json.load(f)

    with open(f"{out_dir}/edges.json", "r") as f:
        graph["edges"] = json.load(f)

    with open(f"{out_dir}/streets.json", "r") as f:
        graph["streets"] = json.load(f)

    with open(f"{out_dir}/pois.json", "r") as f:
        graph["points_of_interest"] = json.load(f)

    with open(f"{out_dir}/nodes_features.json", "r") as f:
        graph["nodes_features"] = json.load(f)

    with open(f"{out_dir}/edges_features.json", "r") as f:
        graph["edges_features"] = json.load(f)

    graph["reference_system"] = {
        "north": [0, 1],
        "south": [0, -1],
        "east": [1, 0],
        "west": [-1, 0],
    }

    n1_coords = graph["nodes"][n1[0]]
    graph["latlng_reference"] = {
        "coords": n1_coords,
        "lat": n1[1],
        "lng": n1[2],
    }

    model = {
        "name": name,
        "template_image": "TODO",
        "feets_per_pixel": feets_per_pixel,
        "feets_per_inch": feets_per_inch,
        "graph": graph,
        "context": {
            "name": "TODO",
            "description": "TODO",
            "scale": "TODO",
            "north_beyond_map": "TODO",
            "south_beyond_map": "TODO",
            "west_beyond_map": "TODO",
            "east_beyond_map": "TODO",
        },
    }

    with open(f"{out_dir}/model.json", "w") as f:
        json.dump(model, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Format data")

    parser.add_argument("--name", help="Name of the map", type=str, required=True)
    parser.add_argument(
        "--feets_per_inch",
        help="Feets per inch of the map",
        type=float,
        required=True,
    )
    parser.add_argument(
        "--n0",
        help="Index of a node in <src_dir>/nodes.json, eg: 0",
        type=int,
        default=0,
        required=False,
    )
    parser.add_argument(
        "--n1",
        help="Index, latitude and longitude of a node n0 is connected to, eg: (1, 40.748578611672315, -73.98532107282095)",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--d_feets",
        help="Distance in meters between n0 and n1",
        type=float,
        required=True,
    )
    parser.add_argument(
        "--src_dir",
        help="Source files directory",
        type=str,
        default="src",
        required=True,
    )

    args = parser.parse_args()

    main(
        args.src_dir,
        args.name,
        args.feets_per_inch,
        args.n0,
        parse_n1(args.n1),
        args.d_feets,
    )
