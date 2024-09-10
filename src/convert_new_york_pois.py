import argparse
import json
import random
from typing import Set
import time

from graph import latlng_distance
from utils import POI_TO_POI_MIN_DISTANCE, str_dict

seed = 1726006792.478604
seed = time.time()
random.seed(seed)
print(f"Seed: {seed}")


keys_to_remove = [
    "district",
    "suburb",
    "state",
    "state_code",
    "county",
    "country",
    "country_code",
    "city",
    "postcode",
    "formatted",
    "address_line1",
    "address_line2",
    "datasource",
]


def main(src_dir: str, feets_per_inch: float) -> None:
    min_distance = POI_TO_POI_MIN_DISTANCE * feets_per_inch

    with open(f"pois_new_york.json", "r") as f:
        new_york_pois = json.load(f)["features"]

    with open(f"{src_dir}/map_pois.json", "r") as f:
        data = json.load(f)

    with open(f"{src_dir}/conversion.json", "r") as f:
        new_york_streets = json.load(f)

    to_remove: Set[int] = set()
    for i, poi in enumerate(new_york_pois):
        properties = poi["properties"]

        for key in keys_to_remove:
            if key in properties:
                del properties[key]

        properties["city"] = "Detroit"

        if properties["street"] not in new_york_streets.keys():
            print(f"Street not found: {properties['street']}")
            to_remove.add(i)
            continue

        conversion = new_york_streets[properties["street"]]
        properties["street"] = conversion[0]

        if "branch" in properties:
            properties["branch"] = conversion[0]

        poi_str = str_dict(properties).lower()
        if "ny" in poi_str or "new york" in poi_str or "new-york" in poi_str:
            print(f"New York references found in {properties['name']}")

        coord_found = False
        while not coord_found:
            properties["lon"] = random.uniform(*conversion[1])
            properties["lat"] = random.uniform(*conversion[2])

            coord_found = True
            for j in range(i):
                if (
                    latlng_distance(
                        properties["lat"],
                        properties["lon"],
                        new_york_pois[j]["properties"]["lat"],
                        new_york_pois[j]["properties"]["lon"],
                    )
                    < min_distance
                ):
                    coord_found = False
                    break

    data["features"] += [
        poi for i, poi in enumerate(new_york_pois) if i not in to_remove
    ]

    with open(f"{src_dir}/pois.json", "w") as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert New York PoIs")

    parser.add_argument(
        "--src_dir",
        help="Source files directory",
        type=str,
        default="src",
        required=True,
    )
    parser.add_argument(
        "--feets_per_inch",
        help="Feets per inch of the map",
        type=float,
        required=True,
    )

    args = parser.parse_args()
    main(args.src_dir, args.feets_per_inch)
