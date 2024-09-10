import json
from typing import Any, Dict
from graph import edge_default_features as default_features


def format_features(features: Dict[str, Any]) -> Dict[str, Any]:
    features = {k.replace(" ", "_"): v for k, v in features.items()}

    for key, default_value in default_features.items():
        if key not in features:
            features[key] = default_value

    return features


def format_edges(src_dir: str) -> None:
    with open(f"{src_dir}/edges.json", "r") as f:
        edges = json.load(f)

    res_edges = list()
    res_streets = dict()
    res_features = list()

    for s_name, edges in edges.items():
        s_edges = list()

        for edge in edges:
            res_features.append(format_features(edge["features"]))
            res_edges.append((edge["node1"], edge["node2"]))
            s_edges.append(len(res_edges) - 1)

        res_streets[s_name] = s_edges

    with open(f"{src_dir}/{src_dir}_out/edges.json", "w") as f:
        json.dump(res_edges, f, indent=4)

    with open(f"{src_dir}/{src_dir}_out/streets.json", "w") as f:
        json.dump(res_streets, f, indent=4)

    with open(f"{src_dir}/{src_dir}_out/edges_features.json", "w") as f:
        json.dump(res_features, f, indent=4)
