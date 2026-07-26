class Graph:
    def __init__(self, directed=False):
        self.adj_list = {}
        self.directed = directed

    def add_vertex(self, vertex):
        if vertex not in self.adj_list:
            self.adj_list[vertex] = []

    def add_edge(self, u, v, weight=1):
        self.add_vertex(u)
        self.add_vertex(v)
        self.adj_list[u].append((v, weight))
        if not self.directed:
            self.adj_list[v].append((u, weight))

    def remove_edge(self, u, v):
        # For link-failure simulation
        if u in self.adj_list:
            self.adj_list[u] = [(n, w) for n, w in self.adj_list[u] if n != v]
        if not self.directed and v in self.adj_list:
            self.adj_list[v] = [(n, w) for n, w in self.adj_list[v] if n != u]

    def get_neighbours(self, u):
        return self.adj_list.get(u, [])

    def get_all_vertices(self):
        return list(self.adj_list.keys())

    def get_all_edges(self):
        edges = []
        for u in self.adj_list:
            for v, weight in self.adj_list[u]:
                edges.append((u, v, weight))
        return edges