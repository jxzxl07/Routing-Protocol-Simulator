from engine.graph import Graph
from engine.priority_queue import PriorityQueue


def dijkstra(graph: Graph, s):
    d = {v: float('inf') for v in graph.get_all_vertices()}
    pi = {v: None for v in graph.get_all_vertices()}
    d[s] = 0

    pq = PriorityQueue()
    for v in graph.get_all_vertices():
        pq.insert(v, d[v])

    finalised = set()
    while not pq.is_empty():
        u, dist_u = pq.extract_min()
        finalised.add(u)
        for v, w in graph.get_neighbours(u):
            if v not in finalised and d[v] > dist_u + w:
                d[v] = dist_u + w
                pi[v] = u
                pq.decrease_key(v, d[v])
    return d, pi