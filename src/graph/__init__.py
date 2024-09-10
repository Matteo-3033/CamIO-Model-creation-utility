from .coords import (
    Coords,
    Position,
    coords_to_latlng,
    latlng_to_coords,
    latlng_distance,
    LatLngReference,
)
from .edge import Edge, default_features as edge_default_features
from .node import Node, default_features as node_default_features
from .graph import load_graph
from json import JSONEncoder
from typing import Any


class GraphEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, Coords):
            return [o.x, o.y]
        if isinstance(o, Node):
            return o.id
        if isinstance(o, Edge):
            return o.id
        return super().default(o)


__all__ = [
    "Coords",
    "Position",
    "Edge",
    "Node",
    "load_graph",
    "coords_to_latlng",
    "latlng_to_coords",
    "latlng_distance",
    "edge_default_features",
    "node_default_features",
    "GraphEncoder",
    "LatLngReference",
]
