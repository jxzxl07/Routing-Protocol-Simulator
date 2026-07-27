from engine.forwarding import compute_all_tables


class Simulator:
    def __init__(self, graph):
        self.graph = graph
        self.tables = compute_all_tables(graph)

    def recompute(self):
        self.tables = compute_all_tables(self.graph)

    def fail_link(self, u, v):
        self.graph.remove_edge(u, v)
        self.recompute()

    def change_cost(self, u, v, new_cost):
        self.graph.remove_edge(u, v)
        self.graph.add_edge(u, v, new_cost)
        self.recompute()

    def trace_path(self, src, dst):
        # Follow forwarding tables hop by hop from src to dst.
        path = [src]
        current = src
        while current != dst:
            table = self.tables.get(current, {})
            if dst not in table:
                return None            # unreachable
            current = table[dst]
            path.append(current)
            if len(path) > len(self.graph.get_all_vertices()):
                return None            # loop guard
        return path