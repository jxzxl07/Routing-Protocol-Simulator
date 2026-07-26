from engine.graph import Graph


def bellman_ford(graph: Graph, s):
    vertices = graph.get_all_vertices()
    edges = graph.get_all_edges()
    d = {v: float('inf') for v in vertices}
    pi = {v: None for v in vertices}
    d[s] = 0

    for _ in range(len(vertices) - 1):
        for u, v, w in edges:
            if d[u] != float('inf') and d[v] > d[u] + w:
                d[v] = d[u] + w
                pi[v] = u

    for u, v, w in edges:
        if d[u] != float('inf') and d[v] > d[u] + w:
            return False, d, pi   # negative cycle
    return True, d, pi