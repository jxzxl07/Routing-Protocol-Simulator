def distance_vector(graph, split_horizon=False, max_rounds=100):
    """
    Distributed distance-vector routing. Each node knows only its neighbours'
    vectors and exchanges them round by round. Returns (vectors, rounds, history).
    Set split_horizon=True to enable the loop-prevention that stops count-to-infinity.
    """
    nodes = graph.get_all_vertices()
    # Each node's vector: {dest: (cost, next_hop)}
    vectors = {n: {d: (float('inf'), None) for d in nodes} for n in nodes}
    for n in nodes:
        vectors[n][n] = (0, n)
        for nbr, w in graph.get_neighbours(n):
            vectors[n][nbr] = (w, nbr)

    history = []
    for r in range(max_rounds):
        changed = False
        snapshot = {n: dict(v) for n, v in vectors.items()}
        for n in nodes:
            for nbr, w in graph.get_neighbours(n):
                for dest in nodes:
                    nbr_cost, nbr_hop = snapshot[nbr][dest]
                    # Split horizon: don't use a route the neighbour learned via us
                    if split_horizon and nbr_hop == n:
                        continue
                    new_cost = w + nbr_cost
                    if new_cost < vectors[n][dest][0]:
                        vectors[n][dest] = (new_cost, nbr)
                        changed = True
        history.append({n: dict(v) for n, v in vectors.items()})
        if not changed:
            return vectors, r + 1, history
    return vectors, max_rounds, history