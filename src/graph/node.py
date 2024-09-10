from utils import StrEnum
from typing import Any, Dict, Optional, Union, List
from .coords import Coords, Position


class Features(StrEnum):
    ON_BORDER = "on_border"
    CROSSWALK = "crosswalk"
    WALK_LIGHT = "walk_light"
    WALK_LIGHT_DURATION = "walk_light_duration"
    ROUND_ABOUT = "round-about"
    STREET_WIDTH = "street_width"
    TACTILE_PAVING = "tactile_paving"


default_features = {
    "on_border": False,
    "crosswalk": False,
    "walk_light": False,
    "round-about": False,
    "street_width": "unknown",
    "tactile_paving": False,
}


class IntersectionType(StrEnum):
    FOUR_WAY = "four-way"
    T = "T"
    UNKNOWN = ""

    def __add__(self, other: str) -> str:
        if self == IntersectionType.UNKNOWN:
            return other
        return f"{self.value} {other}"


class Node(Position):
    def __init__(
        self, index: int, coords: Coords, features: Optional[Dict[str, Any]] = None
    ) -> None:
        self.coords = coords
        self.index = index
        self.adjacents_streets: List[str] = list()

        self.features = features if features is not None else default_features

    @property
    def id(self) -> str:
        return f"n{self.index}"

    @property
    def on_border(self) -> bool:
        return bool(self.features.get(Features.ON_BORDER, False))

    @property
    def intersection_type(self) -> IntersectionType:
        if len(self.adjacents_streets) == 4:
            return IntersectionType.FOUR_WAY

        elif not self.on_border and len(self.adjacents_streets) == 3:
            return IntersectionType.T

        return IntersectionType.UNKNOWN

    def get_position_description(self, street: str) -> str:
        description = f"on {street}"
        if self.on_border:
            description += "near the border of the map"

        elif self.is_dead_end():
            description += "near the end of the street"

        else:
            streets = sorted(filter(lambda s: s != street, set(self.adjacents_streets)))
            if len(streets) == 0:
                description += "in the middle of a block"

            description += (
                "near the intersection with "
                + ", ".join(streets[:-1])
                + (" and " if len(streets) > 1 else "")
                + streets[-1]
            )

        return description

    def description(self, street: str) -> str:
        streets = list(filter(lambda s: s != street, set(self.adjacents_streets)))
        if len(streets) == 0:
            if self.on_border:
                return "the limit of the map"
            return "the end of the street"
        return (
            "the intersection with "
            + ", ".join(streets[:-1])
            + (" and " if len(streets) > 1 else "")
            + streets[-1]
        )

    def is_dead_end(self) -> bool:
        return not self.on_border and len(self.adjacents_streets) == 1

    def distance_to(self, coords: Union["Node", Coords]) -> float:
        if isinstance(coords, Node):
            return self.coords.distance_to(coords.coords)
        return self.coords.distance_to(coords)

    def manhattan_distance_to(self, other: Union["Node", Coords]) -> float:
        if isinstance(other, Node):
            return self.coords.manhattan_distance_to(other.coords)
        return self.coords.manhattan_distance_to(other)

    def closest_point(self, coords: Coords) -> Coords:
        return self.coords

    def is_on_same_street(self, other: "Node") -> bool:
        return bool(set(self.adjacents_streets) & set(other.adjacents_streets))

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
