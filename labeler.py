import argparse
import json
import os
import random as rd
import sys
import tkinter as tk
from enum import Enum
from typing import Any, Dict, Optional, Tuple

from PIL import Image, ImageTk

Coords = Tuple[float, float]

default_nodes_features = {
    "on_border": False,
    "crosswalk": True,
    "walk_light": False,
    "round-about": False,
    "walk_light_duration": "unknown",
    "street_width": "unknown",
    "tactile_paving": False,
}
nodes_values = {
    "on_border": [False],
    "crosswalk": [True, False],
    "walk_light": [True, False],
    "round-about": [True, False],
    "walk_light_duration": ["unknown", 15, 20, 30, 45],
    "street_width": ["unknown", 10, 12.5, 15, 20],
    "tactile_paving": [True, False],
}

default_edges_features = {
    "roadworks": False,
    "bike_lane": False,
    "slope": "flat",
    "surface": "concrete",
    "traffic_direction": "two_way",
    "stairs": False,
}
edges_values = {
    "roadworks": [True, False],
    "bike_lane": [True, False],
    "slope": ["flat", "uphill", "downhill"],
    "surface": ["concrete", "cobblestone"],
    "traffic_direction": ["two_way", "one_way_forward", "one_way_backward"],
    "stairs": [True, False],
}


def get_random_values(values: Dict[str, Any]) -> Dict[str, Any]:
    return {key: rd.choice(values[key]) for key in values}


class Point:
    def __init__(self, coords: Coords, index: int, features: Dict[str, Any]) -> None:
        self.coords = coords
        self.index = index
        self.features = features

        self.oval_id: Optional[int] = None
        self.label_id: Optional[int] = None

        if (
            not self.features.get("walk_light", False)
            and "walk_light_duration" in self.features
        ):
            del self.features["walk_light_duration"]

        if self.features.get("walk_light_duration", "unknown") != "unknown":
            self.features["walk_light_duration"] = float(
                self.features["walk_light_duration"]
            )

        if self.features["street_width"] != "unknown":
            self.features["street_width"] = float(self.features["street_width"])

        if self.features.get("walk_light", False):
            self.features["crosswalk"] = True

    @property
    def color(self) -> str:
        return "green" if not self.features["on_border"] else "blue"

    def draw(self, canvas: tk.Canvas) -> None:
        self.oval_id = canvas.create_oval(
            self.coords[0],
            self.coords[1],
            self.coords[0],
            self.coords[1],
            fill=self.color,
            width=5,
        )

        self.label_id = canvas.create_text(
            self.coords[0],
            self.coords[1],
            text=str(self.index),
            fill=self.color,
            anchor="sw",
        )

    def delete(self, canvas: tk.Canvas) -> None:
        if self.oval_id is not None:
            canvas.delete(self.oval_id)
        if self.label_id is not None:
            canvas.delete(self.label_id)

    def __getitem__(self, index: int) -> float:
        return self.coords[index]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return False

        return self.index == other.index


class Street:
    def __init__(self, index: int, name: str) -> None:
        self.index = index
        self.name = name

        self.points: list[Point] = list()
        self.line_ids: list[int] = list()
        self.features: list[Dict[str, Any]] = list()

    def add_point(
        self, point: Point, canvas: tk.Canvas, features: Optional[Dict[str, Any]] = None
    ) -> None:
        if point in self.points:
            return

        self.points.append(point)

        if len(self.points) == 1:
            return

        assert features is not None
        self.features.append(features)

        prev_point = self.points[-2]
        segment_id = canvas.create_line(
            prev_point[0],
            prev_point[1],
            point[0],
            point[1],
            width=5,
            fill="red",
        )
        self.line_ids.append(segment_id)

    def remove_last_point(self, canvas: tk.Canvas) -> None:
        if len(self.points) == 0:
            return

        self.points.pop()
        if len(self.points) == 0:
            return

        segment_id = self.line_ids.pop()
        canvas.delete(segment_id)

    def unfocus(self, canvas: tk.Canvas) -> None:
        for segment_id in self.line_ids:
            canvas.itemconfig(segment_id, fill="gray")

    def __getitem__(self, index: int) -> Point:
        return self.points[index]

    def __len__(self) -> int:
        return len(self.points)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Street):
            return False

        return self.index == other.index

    def __contains__(self, item: Point) -> bool:
        return item in self.points


class Phase(Enum):
    POINTS = 0
    STREETS = 1


class Labeler:
    LINE_THICKNESS = 130
    SCALE = 2

    def __init__(self, template_path: str, out_dir: str = "out") -> None:
        self.out_dir = out_dir

        self.window = tk.Tk()
        self.window.title("Labeler")

        self.phase = Phase.POINTS
        self.points: list[Point] = list()
        self.streets: list[Street] = list()
        self.current_street: Optional[Street] = None

        self.load_image(template_path)
        self.create_image_window()
        self.create_features_window()

    def load_image(self, template_filename: str) -> None:
        image = Image.open(template_filename)
        self.image = image.resize(
            (int(image.width / self.SCALE), int(image.height / self.SCALE)),
            Image.Resampling.LANCZOS,
        )

    def create_image_window(self) -> None:
        self.change_phase_button = tk.Button(
            self.window,
            text="Street Phase" if self.phase == Phase.POINTS else "Save",
            command=self.on_change_phase,
        )
        self.change_phase_button.pack(side=tk.BOTTOM)

        self.canvas = tk.Canvas(
            self.window,
            height=int(self.image.height),
            width=int(self.image.width),
        )
        self.photo = ImageTk.PhotoImage(master=self.canvas, image=self.image)
        self.item = self.canvas.create_image(0, 0, image=self.photo, anchor="nw")

        self.canvas.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.canvas.bind("<Button-1>", self.on_point_selected)
        self.canvas.bind("<Delete>", self.on_delete_point)
        self.canvas.focus_set()

    def create_features_window(self) -> None:
        self.features_window = tk.Toplevel(self.window)
        self.features_window.title("Features Configuration")
        self.features_window.geometry("300x300+0+0")

        self.current_features = (
            get_random_values(nodes_values)
            if self.phase == Phase.POINTS
            else default_edges_features.copy()
        )

        if self.phase == Phase.POINTS:
            self.create_nodes_features_fields()
        else:
            self.create_edges_features_fields()

        self.features_window.bind(
            "<Key-b>", lambda _: self.on_feature_change("on_border", True)
        )

    def reset_features_window(self) -> None:
        self.features_window.destroy()

        if self.phase != Phase.STREETS or (
            self.current_street and len(self.current_street) > 0
        ):
            self.create_features_window()

    def create_nodes_features_fields(self) -> None:
        title = tk.Label(self.features_window, text=f"Node {len(self.points)}")
        title.config(font=("TkDefaultFont", 14, "bold"))
        title.pack(pady=5)

        for bool_value in [
            "on_border",
            "crosswalk",
            "tactile_paving",
            "walk_light",
            "round-about",
        ]:
            self.create_bool_field(bool_value)

        for str_value in ["walk_light_duration", "street_width"]:
            self.create_str_field(str_value)

    def create_edges_features_fields(self) -> None:
        assert self.current_street is not None
        title = tk.Label(
            self.features_window, text=f"Edge {self.current_street[-1].index} - ?"
        )
        title.config(font=("TkDefaultFont", 14, "bold"))
        title.pack(pady=5)

        for bool_value in ["roadworks", "bike_lane", "stairs"]:
            self.create_bool_field(bool_value)

        for str_value in ["slope", "surface", "traffic_direction"]:
            self.create_str_field(str_value)

    def create_bool_field(self, feature: str) -> None:
        value_var = tk.BooleanVar(value=self.current_features[feature])

        check_button = tk.Checkbutton(
            self.features_window,
            text=feature.replace("_", " ").title(),
            variable=value_var,
            onvalue=True,
            offvalue=False,
            command=lambda: self.on_feature_change(feature, value_var.get()),
        )
        check_button.pack()

    def create_str_field(self, feature: str) -> None:
        label = tk.Label(
            self.features_window, text=feature.replace("_", " ").title() + ":"
        )
        label.pack()

        value_var = tk.StringVar(value=self.current_features[feature])
        entry = tk.Entry(self.features_window, textvariable=value_var)
        entry.bind(
            "<Key>",
            lambda _: self.on_feature_change(feature, value_var.get()),
        )
        entry.pack()

    def on_feature_change(self, feature: str, value: Any) -> None:
        self.current_features[feature] = value

    def create_street_window(self) -> None:
        new_window = tk.Toplevel(self.window)
        new_window.title("Street Configuration")
        new_window.geometry(f"300x300+0+{self.window.winfo_screenheight() - 300}")

        title = tk.Label(new_window, text="Street Name:")
        title.config(font=("TkDefaultFont", 14, "bold"))
        title.pack(pady=5)

        street_name = tk.Entry(new_window, width=30)
        street_name.pack(pady=10)

        create_button = tk.Button(
            new_window,
            text="Create New Street",
            command=lambda: self.on_create_street(street_name.get()),
        )
        create_button.pack(pady=5)

        self.info = tk.Label(new_window, text="")
        self.info.pack(pady=5)

    def startLoop(self) -> None:
        self.window.mainloop()

    def on_point_selected(self, event: Any) -> None:
        coords = (event.x, event.y)

        if self.phase == Phase.POINTS:
            self.on_add_node(coords)
        else:
            self.append_node_to_street(coords)

    def on_add_node(self, coords: Coords) -> None:
        if self.get_nearest_point(coords) is not None:
            return

        point = Point(coords, index=len(self.points), features=self.current_features)
        point.draw(self.canvas)
        self.points.append(point)

        self.reset_features_window()

    def append_node_to_street(self, coords: Coords) -> None:
        if self.current_street is None:
            return

        point = self.get_nearest_point(coords)

        if point is None or point in self.current_street:
            return

        self.current_street.add_point(point, self.canvas, self.current_features)
        self.info.config(text=self.info.cget("text") + f"\nAdded point {point.index}")

        self.reset_features_window()

    def on_delete_point(self, _: Any) -> None:
        if self.phase == Phase.POINTS:
            if len(self.points) == 0:
                return

            point = self.points.pop()
            point.delete(self.canvas)
        elif self.current_street:
            if len(self.current_street) == 0:
                return

            self.current_street.remove_last_point(self.canvas)
            self.info.config(
                text=self.info.cget("text")
                + f"\nRemoved point {len(self.current_street)}"
            )

        self.reset_features_window()

    def get_nearest_point(self, coords: Coords) -> Optional[Point]:
        for point in self.points:
            if (coords[0] - point[0]) ** 2 + (coords[1] - point[1]) ** 2 < 49:
                return point
        return None

    def on_change_phase(self) -> None:
        if self.phase == Phase.POINTS:
            self.phase = Phase.STREETS
            self.create_street_window()
            self.reset_features_window()
        else:
            self.save()

        self.change_phase_button.config(
            text="Street Phase" if self.phase == Phase.POINTS else "Save"
        )

    def on_create_street(self, street_name: str) -> None:
        if street_name == "":
            return

        if self.current_street is not None:
            self.streets.append(self.current_street)
            self.current_street.unfocus(self.canvas)

        self.current_street = Street(index=len(self.streets), name=street_name)
        self.info.config(text=f"Street: {street_name}")

        self.reset_features_window()

    def save(self) -> None:
        if self.current_street and self.current_street not in self.streets:
            self.streets.append(self.current_street)

        self.save_nodes()
        self.save_edges()

        sys.exit(0)

    def save_nodes(self) -> None:
        points = [
            {
                "index": i,
                "coords": [point[0] * self.SCALE, point[1] * self.SCALE],
                "features": point.features,
            }
            for i, point in enumerate(self.points)
        ]

        with open(f"{self.out_dir}/nodes.json", "w") as f:
            json.dump(points, f, indent=4)

    def save_edges(self) -> None:
        edges = {
            street.name: [
                {
                    "node1": street[i].index,
                    "node2": street[i + 1].index,
                    "features": street.features[i],
                }
                for i in range(len(street) - 1)
            ]
            for street in self.streets
        }

        with open(f"{self.out_dir}/edges.json", "w") as f:
            json.dump(edges, f, indent=4)


def main(template_path: str, out_dir: str) -> None:
    try:
        labeler = Labeler(template_path, out_dir)
        labeler.startLoop()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--template_image", type=str, required=True)
    arg_parser.add_argument("--out_dir", type=str, default="out")
    args = arg_parser.parse_args()

    if not os.path.exists(args.template_image):
        print(f"Template file {args.template_image} does not exist.")
        sys.exit(0)

    if os.path.exists(args.out_dir):
        if not os.path.isdir(args.out_dir):
            print(f"{args.out_dir} is not a directory.")
            sys.exit(0)
    else:
        os.makedirs(args.out_dir)

    main(args.template_image, args.out_dir)
