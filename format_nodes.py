import json
from typing import Tuple

with open("src/nodes.txt", "r") as f:
    nodes = f.read().strip().split("\n")


def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return float(((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5)


res = list()

n0 = (290, 1550)
n3 = (355, 1440)
d_m = 76

d_pixel = distance(n0, n3)
meters_per_pixes = d_m / d_pixel

for node in nodes:
    name, coords = node.split(": ")
    x, y = coords[1:-1].split(", ")
    res.append([float(x) * meters_per_pixes, float(y) * meters_per_pixes])

with open("out/nodes.json", "w") as f:
    json.dump(res, f, indent=4)

print(f"Meters per pixel: {meters_per_pixes}")
