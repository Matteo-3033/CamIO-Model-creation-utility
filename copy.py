import json

with open("src/poi.json", "r") as f:
    src = json.load(f)["features"]

with open("poi_new_york.txt", "r") as f:
    data = f.read().split("\n\n")

res = dict()
res["features"] = list()

for poi in data:
    lines = poi.strip().split("\n")

    name = None
    distance = None
    edge = None

    for line in lines:
        if line == "" or not line[0].isalpha():
            continue
        key, value = line.split(": ")
        if key == "name":
            name = value
        if key == "distance":
            distance = value
        if key == "edge":
            edge = value

    n1, n2 = edge.split(" - ")
    n1_n = int(n1[1:])
    n2_n = int(n2[1:])

    obj = list(filter(lambda x: x["properties"]["name"] == name, src))[0]

    obj["properties"]["distance"] = distance
    obj["properties"]["edge"] = [n1_n, n2_n]

    res["features"].append(obj)

with open("src/poi.json", "w") as f:
    json.dump(res, f, indent=4)
