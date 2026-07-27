# Routing Protocol Simulator

An interactive network routing simulator that implements and compares the two
fundamental routing paradigms — **link-state** (Dijkstra) and **distance-vector**
(Bellman-Ford) — with live topology editing, dynamic route recalculation,
packet path tracing, and a visual demonstration of the classic
**count-to-infinity** failure mode.

> **Live demo:** https://routing-sim.wonderfuldesert-1933bece.uksouth.azurecontainerapps.io/

## Overview

Every router in a network must decide, for each destination, which neighbour to
forward a packet to — the *next hop*. Routing protocols are the algorithms that
compute those decisions and keep them correct as the network changes. This
simulator implements both major families:

- **Link-state routing (Dijkstra)** — each router learns the entire topology and
  computes shortest paths independently. The paradigm behind **OSPF** and **IS-IS**.
- **Distance-vector routing (Bellman-Ford)** — each router knows only its
  neighbours' distance vectors and converges through iterative exchange. The
  paradigm behind **RIP** and **EIGRP**.

The interesting result is that on a stable network **both produce identical
shortest-path tables** — they solve the same problem. The differences appear in
*how they converge* and *how they fail*, which the simulator makes visible.

## Features

- Load predefined topologies or upload custom ones as YAML.
- Interactive graph rendering with Cytoscape.js, showing nodes and link costs.
- Toggle between link-state and distance-vector routing.
- Per-router forwarding tables (next-hop) computed live.
- **Packet path tracing** — animated hop-by-hop routing between any two nodes.
- Dynamic recalculation on link failure and cost changes.
- **Count-to-infinity demonstration** with a split-horizon on/off toggle.
- Input validation: rejects negative costs and failures that disconnect the network.
- Single-container deployment (FastAPI serves both the API and the frontend).

## Architecture

The project separates a pure-Python routing engine from a thin web layer, so the
core algorithms are fully testable in isolation.

```text
routing-sim/
├── engine/                  # Pure Python — no web dependencies
│   ├── graph.py             # Adjacency-list network model
│   ├── priority_queue.py    # Custom binary min-heap with O(log n) decrease_key
│   ├── dijkstra.py          # Link-state shortest paths
│   ├── bellman_ford.py      # Centralised distance-vector (with cycle detection)
│   ├── distance_vector.py   # Distributed distance-vector (split-horizon toggle)
│   ├── forwarding.py        # Next-hop forwarding tables from shortest paths
│   ├── topology.py          # YAML topology loading and validation
│   └── simulator.py         # Orchestrator: link events, recompute, path trace
├── api/
│   └── main.py              # FastAPI: REST endpoints + serves the frontend
├── static/
│   └── index.html           # Cytoscape.js single-page app
├── topologies/              # Predefined YAML topologies
├── tests/                   # Scenario and unit tests
├── Dockerfile
└── requirements.txt
```

## Routing Algorithms

**Link-state (Dijkstra).** Each router holds the full topology and runs Dijkstra
from itself, using a custom binary min-heap with an O(log n) `decrease_key`
backed by a hash map. Shortest-path predecessors are then converted into next-hop
forwarding tables. Complexity: O((V + E) log V).

**Distance-vector (Bellman-Ford).** Modelled as a distributed exchange: each node
starts knowing only its direct links, and repeatedly recomputes its distance
vector from its neighbours' advertised vectors until the network converges. This
is the Bellman-Ford relaxation, run with local knowledge only —
`cost(D) = min over neighbours N of (cost(N) + N's cost to D)`. Complexity per
node: O(V · E).

**Count-to-infinity.** Because distance-vector routers act on local information,
a link failure can cause a stale route to circulate: two routers bounce an
ever-increasing cost off each other, "counting to infinity" before recognising a
destination is unreachable. **Split horizon** — not advertising a route back to
the neighbour it was learned from — prevents this. Link-state never suffers the
problem, because every router can see the failure directly. The simulator
demonstrates all three cases.

## Topology Format

```yaml
nodes: [A, B, C, D]
edges:
  - {from: A, to: B, cost: 1}
  - {from: B, to: C, cost: 2}
  - {from: A, to: C, cost: 4}
  - {from: C, to: D, cost: 1}
```

Costs must be non-negative. Every edge must reference declared nodes. Uploaded
topologies are validated before use.

## Running Locally

Requires Python 3.12.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload
```

Open http://localhost:8000/ for the app, or http://localhost:8000/docs for the
interactive API.

## Tests

```bash
python3 -m pytest
```

The suite covers priority-queue and algorithm correctness, and the three
scenario guarantees:

- **Forwarding-table accuracy** — next hops match the true shortest paths.
- **Convergence after link failure** — routes recompute correctly around a break.
- **Count-to-infinity behaviour** — distance-vector counts up without split
  horizon and converges quickly with it.

## Docker & Deployment

The API and frontend are served as a single container.

```bash
docker build -t routing-sim .
docker run -p 8000:8000 routing-sim
```

Deployed to Azure Container Apps from a Docker Hub image:

```bash
docker buildx build --platform linux/amd64 -t jxzxl/routing-sim:latest --push .

az containerapp create \
  --name routing-sim \
  --resource-group cricket-rg \
  --environment cricket-env \
  --image docker.io/jxzxl/routing-sim:latest \
  --target-port 8000 --ingress external \
  --cpu 0.5 --memory 1Gi --min-replicas 0 --max-replicas 1
```

`--min-replicas 0` scales the service to zero when idle. Tear down with
`az group delete --name cricket-rg --yes --no-wait`.

## Usage

1. Select a predefined topology or upload your own, then load it.
2. Choose **Link-State** or **Distance-Vector** and press **Simulate** to compute
   routing tables.
3. **Trace** a packet between two nodes to watch it route hop by hop.
4. **Fail a link** or **change a cost** to see routes dynamically recalculate.
5. In distance-vector mode, toggle **split horizon** and re-simulate to observe
   count-to-infinity appear and be prevented.

## Tech Stack

Python, FastAPI, Cytoscape.js, Docker, Azure Container Apps, pytest.