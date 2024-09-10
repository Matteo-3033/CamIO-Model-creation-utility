from utils import StrEnum
from typing import Any, Dict, Optional, Set, List, Iterator
from .coords import Coords, Position, StraightLine
from .node import Node


class Features(StrEnum):
    ROADWORK = "roadwork"
    SLOPE = "slope"
    BIKE_LANE = "bike_lane"
    SURFACE = "surface"
    TRAFFIC_DIRECTION = "traffic_direction"
    STAIRS = "stairs"


default_features = {
    "roadwork": False,
    "slope": "flat",
    "bike_lane": False,
    "surface": "concrete",
    "traffic_direction": "two_way",
    "stairs": False,
}


class Edge(StraightLine, Position):
    def __init__(
        self,
        node1: Node,
        node2: Node,
        street_name: str,
        features: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.node1 = node1
        self.node2 = node2
        self.street = street_name
        self.features = features if features is not None else default_features

        self.between_streets: Set[str] = set()
        self.length = self.node1.distance_to(self.node2)

    @property
    def id(self) -> str:
        return f"{self.node1.id} - {self.node2.id}"

    @property
    def m(self) -> float:
        if self.node1[0] == self.node2[0]:
            return float("inf")

        return (self.node1[1] - self.node2[1]) / (self.node1[0] - self.node2[0])

    @property
    def q(self) -> float:
        if self.node1[0] == self.node2[0]:
            return self.node1[0]

        return (self.node1[0] * self.node2[1] - self.node2[0] * self.node1[1]) / (
            self.node1[0] - self.node2[0]
        )

    @property
    def versor(self) -> Coords:
        return (self.node2.coords - self.node1.coords).normalized()

    def contains(self, coords: Coords) -> bool:
        return 0 < self.versor.dot(coords - self.node1.coords) < self.length

    def is_adjacent(self, other: "Edge") -> bool:
        return (
            self.node1 == other.node1
            or self.node1 == other.node2
            or self.node2 == other.node1
            or self.node2 == other.node2
        )

    def distance_to(self, coords: "Coords") -> float:
        if self.contains(coords.project_on(self)):
            return coords.distance_to_line(self)

        return min(
            self.node1.distance_to(coords),
            self.node2.distance_to(coords),
        )

    def closest_point(self, coords: "Coords") -> "Coords":
        projection = coords.project_on(self)
        if self.contains(projection):
            return projection

        return min(
            [self.node1, self.node2],
            key=lambda node: node.distance_to(coords),
        ).coords

    def get_position_description(self, street: str) -> str:
        location_description = (
            f"on {street}, "
            f"between {self.node1.get_position_description(street)} "
            f"and {self.node2.get_position_description(street)}"
        )

        return location_description

    def __getitem__(self, index: int) -> Node:
        return (self.node1, self.node2)[index]

    def __str__(self) -> str:
        return self.id

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Edge):
            return False
        return self.node1 == other.node1 and self.node2 == other.node2

    def __iter__(self) -> Iterator[Node]:
        return iter((self.node1, self.node2))

    def __hash__(self) -> int:
        return hash(self.id)

    def get_distance_description(self, coords: Coords) -> str:
        if not self.contains(coords):
            raise ValueError("Coords are not on the edge")

        distance = self.node1.distance_to(coords)
        length = self.length

        if distance < 0.33 * length:
            return "one third a block"
        if distance < 0.66 * length:
            return "half a block"
        return "two third a block"
