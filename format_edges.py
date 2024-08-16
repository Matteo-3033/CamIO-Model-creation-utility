import json
from typing import Tuple, Dict, Any


def get_nodes(edges_str: str) -> Tuple[int, int]:
    n1_str, n2_str = edges_str.split("-")

    if n1_str[0] == "n":
        n1_str = n1_str[1:]
    if n2_str[0] == "n":
        n2_str = n2_str[1:]

    return int(n1_str), int(n2_str)


edges_features_defaults = {
    "roadworks": False,
    "bike_lane": False,
    "slope": "flat",
    "surface": "asphalt",
    "traffic_direction": "two_way",
    "tactile_paving": False,
    "stairs": False,
}


def format_features(features: Dict[str, Any]) -> Dict[str, Any]:
    features = {k.replace(" ", "_"): v for k, v in features.items()}

    for key, default_value in edges_features_defaults.items():
        if key not in features:
            features[key] = default_value

    return features


def format_edges() -> None:
    with open("src/edges.txt", "r") as f:
        edges = f.read().strip().split("\n")

    with open("src/streets.txt", "r") as f:
        streets = f.read().strip().split("\n")

    with open("src/edges_features.json", "r") as f:
        features = json.load(f)

    res_edges = list()
    res_streets = dict()
    res_features = list()

    for s, es in zip(streets, edges):
        _, s_name = s.split(": ")
        s_edges = list()

        es = es.split(": ")[1]
        for edges_str in es.split(", "):
            n1, n2 = get_nodes(edges_str)

            if edges_str in features:
                res_features.append(format_features(features[edges_str]))
            else:
                res_features.append(format_features(dict()))

            res_edges.append((n1, n2))
            s_edges.append(len(res_edges) - 1)

        res_streets[s_name] = s_edges

    with open("out/edges.json", "w") as f:
        json.dump(res_edges, f, indent=4)

    with open("out/streets.json", "w") as f:
        json.dump(res_streets, f, indent=4)

    with open("out/edges_features.json", "w") as f:
        json.dump(res_features, f, indent=4)


if __name__ == "__main__":
    format_edges()
