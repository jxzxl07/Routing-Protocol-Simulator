from engine.dijkstra import dijkstra


def build_forwarding_table(source, pi):
    # Destination -> next hop, derived from Dijkstra predecessors.
    table = {}
    for dest in pi:
        if dest == source or pi[dest] is None:
            continue
        hop = dest
        while pi[hop] != source:
            hop = pi[hop]
        table[dest] = hop
    return table


def compute_all_tables(graph):
    # Run Dijkstra from every node; return {node: forwarding table}.
    tables = {}
    for node in graph.get_all_vertices():
        _, pi = dijkstra(graph, node)
        tables[node] = build_forwarding_table(node, pi)
    return tables