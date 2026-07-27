import yaml
from engine.graph import Graph


def load_topology(source, is_file=True):
    # Build a Graph from YAML given as a file path or a raw string
    if is_file:
        with open(source) as f:
            data = yaml.safe_load(f)
    else:
        data = yaml.safe_load(source)

    if not data or "nodes" not in data or "edges" not in data:
        raise ValueError("Topology must define 'nodes' and 'edges'")

    nodes = data["nodes"]
    graph = Graph(directed=False)
    for n in nodes:
        graph.add_vertex(n)

    for e in data["edges"]:
        u, v, cost = e.get("from"), e.get("to"), e.get("cost", 1)
        if u not in nodes or v not in nodes:
            raise ValueError(f"Edge references unknown node: {u}-{v}")
        if cost < 0:
            raise ValueError(f"Negative cost not allowed: {u}-{v}")
        graph.add_edge(u, v, cost)

    return graph