import json
from typing import Any, Dict, List

from graph import Coords, GraphEncoder, Node
from graph import node_default_features as default_features


def get_node(node_obj: Dict[str, Any]) -> Node:
    return Node(
        node_obj["index"],
        Coords(*node_obj["coords"]),
        node_obj["features"],
    )


def format_features(features: Dict[str, Any]) -> Dict[str, Any]:
    features = {k.replace(" ", "_"): v for k, v in features.items()}

    for key, default_value in default_features.items():
        if key not in features:
            features[key] = default_value

    return features


def format_nodes(src_dir: str, n0_index: int, n1_index: int, d_feets: float) -> float:
    with open(f"{src_dir}/nodes.json", "r") as f:
        nodes = json.load(f)

    res_nodes = list()

    n0 = get_node(nodes[n0_index])
    n1 = get_node(nodes[n1_index])

    d_pixel = n0.distance_to(n1)
    feets_per_pixes = d_feets / d_pixel
    print(f"Feets per pixel: {feets_per_pixes}")

    res_features: List[Dict[str, Any]] = list()

    for node_obj in nodes:
        node = get_node(node_obj)
        res_nodes.append(node.coords * feets_per_pixes)
        res_features.append(format_features(node.features))

    with open(f"{src_dir}/{src_dir}_out/nodes.json", "w") as f:
        json.dump(res_nodes, f, indent=4, cls=GraphEncoder)

    with open(f"{src_dir}/{src_dir}_out/nodes_features.json", "w") as f:
        json.dump(res_features, f, indent=4, cls=GraphEncoder)

    return feets_per_pixes
