from typing import Dict, List, Tuple
import json
from .coords import Coords
from .node import Node
from .edge import Edge


def load_graph(src_dir: str) -> Tuple[List[Node], List[Edge], Dict[str, List[Edge]]]:
    with open(f"{src_dir}/nodes.json", "r") as f:
        nodes_data = json.load(f)
    with open(f"{src_dir}/nodes_features.json", "r") as f:
        nodes_features = json.load(f)
    nodes = [
        Node(i, Coords(*data[0]), features=data[1])
        for i, data in enumerate(zip(nodes_data, nodes_features))
    ]

    with open(f"{src_dir}/streets.json", "r") as f:
        streets_data: Dict[str, List[int]] = json.load(f)

    with open(f"{src_dir}/edges.json", "r") as f:
        edges_data: List[Tuple[int, int]] = json.load(f)

    edges: List[Edge] = list()
    streets: Dict[str, List[Edge]] = dict()

    for street_name, edges_indexes in streets_data.items():
        street_edges: List[Edge] = list()

        for edge_index in edges_indexes:
            edge_data = edges_data[edge_index]

            node1 = nodes[edge_data[0]]
            node1.adjacents_streets.append(street_name)
            node2 = nodes[edge_data[1]]
            node2.adjacents_streets.append(street_name)

            edge = Edge(
                node1,
                node2,
                street_name,
            )

            street_edges.append(edge)

        edges.extend(street_edges)
        streets[street_name] = street_edges

    return nodes, edges, streets
