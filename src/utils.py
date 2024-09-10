from enum import Enum
from typing import Any, Mapping

POI_TO_POI_MIN_DISTANCE = 0.35  # inch
POI_TO_NODE_MIN_DISTANCE = 0.25  # inch
POI_TO_EDGE_MAX_DISTANCE = 0.30  # inch


def str_format(v: Any) -> str:
    return str(v).replace("_", " ")


def str_dict(d: Mapping[Any, Any], indent: int = 0) -> str:
    res = ""

    for key, value in d.items():
        res += " " * indent + str_format(key) + ": "
        if isinstance(value, dict):
            res += "\n" + str_dict(value, indent + 4)
        elif isinstance(value, list):
            if len(value) == 0:
                res += "[]\n"
            elif len(value) == 1:
                res += "[ " + str_format(value[0]) + " ]\n"
            else:
                res += "[\n"
                for item in value:
                    res += " " * (indent + 4) + str_format(item) + ",\n"
                res += " " * indent + "]\n"
        else:
            res += str_format(value) + "\n"

    return res


class StrEnum(str, Enum):
    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return str(self)
