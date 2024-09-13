# CamIO Graph Builder

This repository provides utility code to build a graph for the [LLM CamIO](https://github.com/Coughlan-Lab/simple_camio/tree/llm) project.

## Overview

The CamIO Graph Builder allows you to create a detailed graph representation of tactile maps, complete with points of interest (PoIs), intersections, and street information. This graph serves as input for the CamIO system, enhancing accessibility by offering more comprehensive map data.

## Prerequisites

-   A scanned image of the tactile map you want to process.
-   Python environment with required dependencies (see `requirements.txt`).
-   A [Geoapify](https://apidocs.geoapify.com/playground/places) account to obtain PoI data.

## Step-by-Step Guide

### 1. Prepare the Map Scan

Obtain a scan of the tactile map that you want to convert into a graph. Ensure that the image is clear and includes all relevant intersections and streets.

### 2. Label the Map

Use the following command to launch the labeling process:

```bash
python labeler.py --template_image <path_to_map> --out_dir <output_directory>
```

#### Map Labeling Process:

-   You will be prompted to click on each intersection to add a node.
-   For each node, a random set of features will be generated (e.g., walklight presence, duration, street width). You can manually edit these attributes.
-   Once all intersections are labeled, click the **Street Phase** button.
-   A new window will open where you can add street names. Click **Create New Street** and select the nodes that belong to that street. Repeat for all streets.

Finally, click **Save** to save the labeled map in the specified output directory.

### 3. Add Points of Interest (PoIs)

1. Access [Geoapify](https://apidocs.geoapify.com/playground/places) to search for Points of Interest (PoIs) relevant to your map (e.g., restaurants, parks).
2. Download the PoI data as a JSON file and save it as `pois.json` in the same directory of the labeled map.

### 4. Customize and Run the Jupyter Notebook

1. Copy either `draw_detroit.ipynb` or `draw_new_york.ipynb` to a new notebook:

    - Use **draw_detroit.ipynb** if you have a small set of PoIs and want to remap New York PoIs onto your map.
    - Use **draw_new_york.ipynb** to map only your own PoIs.

2. Edit the content of the first cell to match your map details.

#### Additional Steps for `draw_detroit.ipynb`:

-   Rename `pois.json` to `map_pois.json`.
-   Create a `conversion.json` file like the one found in [`detroit_conant/conversion.json`](detroit_conant/conversion.json). This file maps New York streets to corresponding streets on your map using latitude and longitude.
-   Optionally, edit `pois_new_york.json` to remove references to New York, like street names and neighborhoods.

### 5. Visualize the Graph

Run the notebook to visualize your graph, including labeled intersections and PoIs. Save the output once complete.

### 6. Finalize the Map Model

In your map directory, you will find a new folder containing the model of your map. Complete any fields marked as "TODO" and use this model as input for the CamIO system.
