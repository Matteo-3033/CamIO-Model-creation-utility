import json
from typing import Tuple


def get_node(node_str: str) -> Tuple[float, float]:
    if ":" in node_str:
        node_str = node_str.split(":")[1].strip()

    n1_str, n2_str = node_str.split(",")

    n1_str = n1_str.strip()
    n2_str = n2_str.strip()

    n0 = float(n1_str.split("(")[1])
    n1 = float(n2_str.split(")")[0])

    return n0, n1


def format_nodes(n1_index: int, d_m: float) -> float:
    with open("src/nodes.txt", "r") as f:
        nodes = f.read().strip().split("\n")

    def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        return float(((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5)

    res = list()

    n0 = get_node(nodes[0])
    n1 = get_node(nodes[n1_index])

    d_pixel = distance(n0, n1)
    meters_per_pixes = d_m / d_pixel
    print(f"Meters per pixel: {meters_per_pixes}")

    for node in nodes:
        x, y = get_node(node)
        res.append([float(x) * meters_per_pixes, float(y) * meters_per_pixes])
        # print(
        #    f"{len(res) - 1}: ({x}, {y}) -> ({float(x) * meters_per_pixes}, {float(y) * meters_per_pixes})"
        # )

    with open("out/nodes.json", "w") as f:
        json.dump(res, f, indent=4)

    return meters_per_pixes


if __name__ == "__main__":
    format_nodes(3, 76.06)
