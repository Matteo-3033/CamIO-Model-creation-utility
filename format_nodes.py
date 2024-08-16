import json
from typing import Tuple, List, Dict, Any


def get_node(node_str: str) -> Tuple[float, float, bool]:
    if ":" in node_str:
        node_str = node_str.split(":")[1].strip()

    n1_str, n2_str, *on_border = node_str.split(",")

    n1_str = n1_str.strip()
    n2_str = n2_str.strip()

    n0 = float(n1_str.split("(")[1])
    n1 = float(n2_str.split(")")[0])

    return n0, n1, len(on_border) > 0


nodes_features_defaults = {
    "crosswalk": False,
    "walk_light": False,
    "round-about": False,
    "walk_light_duration": "unknown",
    "street_width": "unknown",
    "tactile_paving": False,
    "stairs": False,
    "elevator": False,
}


def format_features(features: Dict[str, Any]) -> Dict[str, Any]:
    features = {k.replace(" ", "_"): v for k, v in features.items()}

    for key, default_value in nodes_features_defaults.items():
        if key not in features:
            features[key] = default_value

    return features


def format_nodes(n1_index: int, d_m: float) -> float:
    with open("src/nodes.txt", "r") as f:
        nodes = f.read().strip().split("\n")

    with open("src/nodes_features.json", "r") as f:
        features = json.load(f)

    def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        return float(((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5)

    res_nodes = list()

    n0 = get_node(nodes[0])[:-1]
    n1 = get_node(nodes[n1_index])[:-1]

    d_pixel = distance(n0, n1)
    meters_per_pixes = d_m / d_pixel
    print(f"Meters per pixel: {meters_per_pixes}")

    res_features: List[Dict[str, Any]] = list()

    for i, node in enumerate(nodes):
        x, y, on_border = get_node(node)
        res_nodes.append([float(x) * meters_per_pixes, float(y) * meters_per_pixes])

        if str(i) in features:
            res_features.append(
                format_features({"on_border": on_border, **features[str(i)]})
            )
        else:
            res_features.append(format_features({"on_border": on_border}))

        # print(
        #    f"{len(res) - 1}: ({x}, {y}) -> ({float(x) * meters_per_pixes}, {float(y) * meters_per_pixes})"
        # )

    with open("out/nodes.json", "w") as f:
        json.dump(res_nodes, f, indent=4)

    with open("out/nodes_features.json", "w") as f:
        json.dump(res_features, f, indent=4)

    return meters_per_pixes


if __name__ == "__main__":
    format_nodes(3, 76.06)
