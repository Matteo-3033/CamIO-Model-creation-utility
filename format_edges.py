import json

with open("src/edges.txt", "r") as f:
    edges = f.read().strip().split("\n")

with open("src/streets.txt", "r") as f:
    streets = f.read().strip().split("\n")

res_edges = list()
res_streets = dict()

for s, es in zip(streets, edges):
    s_id, s_name = s.split(": ")
    s_edges = list()

    es = es.split(": ")[1]
    for edges_str in es.split(", "):
        edges = edges_str.split(" - ")
        n1_str, n2_str = edges[0], edges[1].split(" (")[0]
        n1 = int(n1_str[1:])
        n2 = int(n2_str[1:])
        d = int(edges[1].split(" (")[1].split(" m)")[0])
        res_edges.append((n1, n2, d))
        s_edges.append(len(res_edges) - 1)

    res_streets[s_name] = s_edges

with open("out/edges.json", "w") as f:
    json.dump(res_edges, f, indent=4)

with open("out/streets.json", "w") as f:
    json.dump(res_streets, f, indent=4)
