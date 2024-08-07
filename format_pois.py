import json
import math
from typing import Any, Dict, List, Tuple, Union


class Coords:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def distance_from(self, other: "Coords") -> float:
        return float(((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5)

    def __getitem__(self, index: int) -> float:
        return self.x if index == 0 else self.y

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        return str(self)


class Node:
    def __init__(self, index: int, coords: Coords) -> None:
        self.coords = coords
        self.index = index

    def distance_from(self, other: Union["Node", Coords]) -> float:
        if isinstance(other, Node):
            return self.coords.distance_from(other.coords)
        return self.coords.distance_from(other)

    def __getitem__(self, index: int) -> float:
        return self.coords[index]

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Node):
            return False
        return self.index == other.index

    def __str__(self) -> str:
        return f"{self.index} ({self.coords.x}, {self.coords.y})"

    def __repr__(self) -> str:
        return str(self)


class Edge:
    def __init__(self, node1: Node, node2: Node, street_name: str) -> None:
        self.node1 = node1
        self.node2 = node2
        self.street = street_name

    @property
    def m(self) -> float:
        return (self.node1[1] - self.node2[1]) / (self.node1[0] - self.node2[0])

    @property
    def q(self) -> float:
        return (self.node1[0] * self.node2[1] - self.node2[0] * self.node1[1]) / (
            self.node1[0] - self.node2[0]
        )

    def distance_from(self, coords: Coords) -> float:
        num = abs(self.m * coords.x + self.q - coords.y)
        den = (self.m**2 + 1) ** 0.5
        return float(num / den)

    def contains(self, coords: Coords) -> bool:
        return (
            self.node1[0] <= coords[0] <= self.node2[0]
            or self.node2[0] <= coords[0] <= self.node1[0]
            or self.node1[1] <= coords[1] <= self.node2[1]
            or self.node2[1] <= coords[1] <= self.node1[1]
        )

    def __getitem__(self, index: int) -> Node:
        return self.node1 if index == 0 else self.node2

    def __str__(self) -> str:
        return f"{self.node1} - {self.node2}"

    def __repr__(self) -> str:
        return str(self)


def load_graph() -> Tuple[List[Node], List[Edge], Dict[str, List[Edge]]]:
    with open("out/nodes.json", "r") as f:
        nodes_data = json.load(f)
        nodes = [Node(i, Coords(*coords)) for i, coords in enumerate(nodes_data)]

    with open("out/streets.json", "r") as f:
        streets_data: Dict[str, List[int]] = json.load(f)

    with open("out/edges.json", "r") as f:
        edges_data: List[Tuple[int, int]] = json.load(f)
        edges: List[Edge] = list()
        streets: Dict[str, List[Edge]] = dict()

        for street_name, edges_indexes in streets_data.items():
            street_edges: List[Edge] = list()

            for edge_index in edges_indexes:
                edge_data = edges_data[edge_index]

                node1 = nodes[edge_data[0]]
                node2 = nodes[edge_data[1]]

                edge = Edge(
                    node1,
                    node2,
                    street_name,
                )

                street_edges.append(edge)

            edges.extend(street_edges)
            streets[street_name] = street_edges

    return nodes, edges, streets


def convert_coords(
    reference_node: Tuple[Node, float, float], lat: float, lon: float
) -> Tuple[float, float]:
    # utm_coords = utm.from_latlon(lat, lon)
    # reference_utm = utm.from_latlon(reference_node[1], reference_node[2])

    dx = distance_lat_lon(reference_node[1], reference_node[2], reference_node[1], lon)
    dy = distance_lat_lon(reference_node[1], reference_node[2], lat, reference_node[2])

    return reference_node[0].coords.x + dx, reference_node[0].coords.y - dy


def get_edge(edges: List[Edge], coords: Coords) -> Edge:
    edge = min(
        filter(lambda edge: edge.contains(coords), edges),
        key=lambda edge: edge.distance_from(coords),
    )
    return edge


def distance_lat_lon(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371  # Radius of earth in KM

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dLat = lat2 - lat1
    dLon = lon2 - lon1

    a = (
        math.sin(dLat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dLon / 2) ** 2
    )

    c = 2 * math.asin(math.sqrt(a))
    d = R * c

    return d * 1000


def get_projected_distance(edge: Edge, p: Coords) -> float:
    p1 = edge[0]

    p2_x = (p.x + edge.m * p.y - edge.m * edge.q) / (edge.m**2 + 1)
    p2_y = (edge.m * p.x + edge.m**2 * p.y + edge.q) / (edge.m**2 + 1)
    p2 = Coords(p2_x, p2_y)

    return p1.distance_from(p2)


def format_pois(
    reference_node_index: int, reference_node_lat: float, reference_node_lon: float
) -> None:
    with open("src/pois.json", "r") as f:
        pois = json.load(f)["features"]

    nodes, edges, streets = load_graph()
    reference_node = (
        nodes[reference_node_index],
        reference_node_lat,
        reference_node_lon,
    )

    edges_index = {(e[0].index, e[1].index): i for i, e in enumerate(edges)}

    keys = [
        "country",
        "country_code",
        "state",
        "state_code",
        "county",
        "postcode",
        "details",
        "state_code",
        "formatted",
        "address_line1",
        "address_line2",
        "datasource",
        "place_id",
        "brand_details",
        "operator_details",
        "network_details",
        "ref_other",
        "wiki_and_media",
        "name_international",
        "website",
        "ref_other",
        "geometry",
    ]

    res: List[Dict[str, Any]] = list()

    for poi in pois:
        poi = poi["properties"]

        for key in keys:
            if key in poi:
                del poi[key]

        poi["coords"] = convert_coords(reference_node, poi["lat"], poi["lon"])
        del poi["lat"]
        del poi["lon"]

        edge = get_edge(streets[poi["street"]], Coords(*poi["coords"]))
        poi["edge"] = edges_index[(edge[0].index, edge[1].index)]

        poi["distance"] = get_projected_distance(edge, Coords(*poi["coords"]))

        res.append(poi)

    with open("out/pois.json", "w") as f:
        json.dump(res, f, indent=4)


if __name__ == "__main__":
    format_pois(3, 40.74605893499274, -73.99053528624474)
