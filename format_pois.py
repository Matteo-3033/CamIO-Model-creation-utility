import json
import math
from typing import Any, Dict, List, Set, Tuple, Union, Optional


class Coords:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def distance_to(self, other: "Coords") -> float:
        return float(((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5)

    def manhattan_distance_to(self, other: "Coords") -> float:
        return abs(self.x - other.x) + abs(self.y - other.y)

    def distance_to_edge(self, edge: "Edge") -> float:
        num = abs(edge.m * self.x + edge.q - self.y)
        den = (edge.m**2 + 1) ** 0.5

        return float(num / den)

    def project_on(self, edge: "Edge") -> "Coords":
        p_x = (self.x + edge.m * self.y - edge.m * edge.q) / (edge.m**2 + 1)
        p_y = (edge.m * self.x + edge.m**2 * self.y + edge.q) / (edge.m**2 + 1)

        return Coords(p_x, p_y)

    def __add__(self, other: Union["Coords", float]) -> "Coords":
        if isinstance(other, Coords):
            return Coords(self.x + other.x, self.y + other.y)
        return Coords(self.x + other, self.y + other)

    def __sub__(self, other: Union["Coords", float]) -> "Coords":
        if isinstance(other, Coords):
            return Coords(self.x - other.x, self.y - other.y)
        return Coords(self.x - other, self.y - other)

    def __mul__(self, other: float) -> "Coords":
        return Coords(self.x * other, self.y * other)

    def __truediv__(self, other: float) -> "Coords":
        return Coords(self.x / other, self.y / other)

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
        self.adjacents_street: Set[str] = set()

    @property
    def id(self) -> str:
        return f"n{self.index}"

    @property
    def description(self) -> str:
        if len(self.adjacents_street) == 1:
            return f"end of {next(iter(self.adjacents_street))}"

        streets = list(self.adjacents_street)
        streets_str = ", ".join(streets[:-1]) + " and " + streets[-1]

        return f"intersection between {streets_str}"

    def distance_from(self, other: Union["Node", Coords]) -> float:
        if isinstance(other, Node):
            return self.coords.distance_to(other.coords)
        return self.coords.distance_to(other)

    def manhattan_distance_from(self, other: Union["Node", Coords]) -> float:
        if isinstance(other, Node):
            return self.coords.manhattan_distance_to(other.coords)
        return self.coords.manhattan_distance_to(other)

    def __getitem__(self, index: int) -> float:
        return self.coords[index]

    def __str__(self) -> str:
        return f"{self.id}: {self.coords}"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Node):
            return False
        return self.index == other.index


class Edge:
    def __init__(self, node1: Node, node2: Node, street_name: str) -> None:
        self.node1 = node1
        self.node2 = node2
        self.street = street_name
        self.between_streets: Set[str] = set()
        self.length = self.node1.distance_from(self.node2)

    @property
    def id(self) -> str:
        return f"{self.node1.id} - {self.node2.id}"

    @property
    def m(self) -> float:
        return (self.node1[1] - self.node2[1]) / (self.node1[0] - self.node2[0])

    @property
    def q(self) -> float:
        return (self.node1[0] * self.node2[1] - self.node2[0] * self.node1[1]) / (
            self.node1[0] - self.node2[0]
        )

    def contains(self, coords: Coords) -> bool:
        return (
            self.node1[0] <= coords[0] <= self.node2[0]
            or self.node2[0] <= coords[0] <= self.node1[0]
            or self.node1[1] <= coords[1] <= self.node2[1]
            or self.node2[1] <= coords[1] <= self.node1[1]
        )

    def is_adjacent(self, other: "Edge") -> bool:
        return (
            self.node1 == other.node1
            or self.node1 == other.node2
            or self.node2 == other.node1
            or self.node2 == other.node2
        )

    def __getitem__(self, index: int) -> Node:
        return self.node1 if index == 0 else self.node2

    def __str__(self) -> str:
        return self.id

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Edge):
            return False
        return self.node1 == other.node1 and self.node2 == other.node2

    def __hash__(self) -> int:
        return hash(self.id)


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


def get_edge(edges: List[Edge], coords: Coords, debug=False) -> Edge:
    if debug:
        l = list(filter(lambda edge: edge.contains(coords.project_on(edge)), edges))
    edge = min(
        filter(
            lambda edge: edge.contains(coords.project_on(edge)),
            edges,
        ),
        key=lambda edge: coords.distance_to_edge(edge),
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
    "owner details",
    "brand_details",
    "operator_details",
    "network_details",
    "ref_other",
    "wiki_and_media",
    "name_international",
    "ref",
    "ref_other",
    "ele",
    "heritage",
    "opening_hours_covid19",
    "website_other",
    "geometry",
]

public_transports = {
    "train": "station",
    "subway": "station",
    "bus": "stop",
    "tram": "stop",
}


def format_categories(categories: List[str]) -> List[str]:
    res: Set[str] = set()
    freq: Dict[str, int] = dict()

    for category in categories:
        fields = category.split(".")
        freq[fields[0]] = freq.get(fields[0], 0) + 1

    for category in categories:
        fields = category.split(".")

        if category.startswith("wheelchair") or category.startswith("internet_access"):
            continue

        tmp = ""
        for i in range(len(fields) - 1):
            tmp += fields[i]
            if tmp in res:
                res.remove(tmp)
            tmp += "."

        if fields[-1] in public_transports.keys():
            res.add(f"{fields[-1]}_{public_transports[fields[-1]]}")
            res.add("public_transport")
        elif len(list(filter(lambda x: x.startswith(category), res))) == 0:
            res.add(category)

    return list(res)


poi_features_defaults = {
    "wheelchair_accessible": False,
    "tactile_paving": False,
    "tactile_map": False,
    "reception": False,
    "stairs": False,
}


def format_facilities(facilities: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    facilities = {k.replace(" ", "_"): v for k, v in facilities.items()}

    if "wheelchair" in facilities:
        del facilities["wheelchair"]
    if "wheelchair_details" in facilities:
        del facilities["wheelchair_details"]

    for key in poi_features_defaults.keys():
        if key in facilities:
            del facilities[key]

    if len(facilities.keys()) == 0:
        return None
    return facilities


def format_accessibility(
    accessibility: Dict[str, Any], facilities: Dict[str, Any]
) -> Dict[str, Any]:
    facilities = {k.replace(" ", "_"): v for k, v in facilities.items()}
    accessibility = {k.replace(" ", "_"): v for k, v in accessibility.items()}

    if "wheelchair" in facilities:
        accessibility["wheelchair_accessible"] = facilities["wheelchair"]
    if "wheelchair_details" in facilities:
        accessibility["wheelchair_accessible"] = facilities["wheelchair_details"][
            "condition"
        ]

    for key, default_value in poi_features_defaults.items():
        if key in accessibility:
            accessibility[key] = accessibility[key]
        elif key in facilities:
            accessibility[key] = facilities[key]
        else:
            accessibility[key] = default_value

    return accessibility


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

    res: List[Dict[str, Any]] = list()
    done: Set[str] = set()

    for i, poi in enumerate(pois):
        poi = poi["properties"]

        # print(f"Processing {poi['name']}")
        if "name" not in poi:
            print(f"Skipping POI without name at index {i}")
            continue

        if poi["name"] in done:
            print(f"Skipping duplicate {poi['name']}")
            continue

        if "street" not in poi:
            print(f"Skipping {poi['name']}")
            continue

        for key in keys:
            if key in poi:
                del poi[key]

        if "categories" in poi:
            poi["categories"] = format_categories(poi["categories"])

        if "website" in poi:
            if "contact" not in poi:
                poi["contact"] = dict()
            poi["contact"]["website"] = poi["website"]
            del poi["website"]

        poi["accessibility"] = format_accessibility(
            poi.get("accessibility", dict()), poi.get("facilities", dict())
        )

        if "facilities" in poi:
            poi["facilities"] = format_facilities(poi["facilities"])
            if poi["facilities"] is None:
                del poi["facilities"]

        poi["coords"] = convert_coords(reference_node, poi["lat"], poi["lon"])
        del poi["lat"]
        del poi["lon"]

        coords = Coords(*poi["coords"])

        try:
            edge = get_edge(streets[poi["street"]], Coords(*poi["coords"]))
            poi["edge"] = edges_index[(edge[0].index, edge[1].index)]
        except Exception as e:
            print(f"Could not find edge for {poi['name']}")
            continue

        # poi["distance"] = coords.project_on(edge).distance_to(edge[0].coords)

        res.append(poi)
        done.add(poi["name"])

    res.sort(key=lambda x: x["name"])

    with open("out/pois.json", "w") as f:
        json.dump(res, f, indent=4)


if __name__ == "__main__":
    format_pois(3, 40.74605893499274, -73.99053528624474)
