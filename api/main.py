from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from engine.topology import load_topology
from engine.simulator import Simulator
from engine.distance_vector import distance_vector

app = FastAPI(title="Routing Protocol Simulator")

TOPO_DIR = Path("topologies")
STATIC_DIR = Path("static")

# In-memory session (one simulator at a time — fine for a demo)
state = {"sim": None, "graph": None}


class CostChange(BaseModel):
    u: str
    v: str
    cost: int


class LinkFail(BaseModel):
    u: str
    v: str


class Trace(BaseModel):
    src: str
    dst: str


def graph_to_json(graph):
    return {
        "nodes": [{"id": n} for n in graph.get_all_vertices()],
        "edges": [
            {"source": u, "target": v, "cost": w}
            for u, v, w in graph.get_all_edges()
            if u < v  # each undirected edge once
        ],
    }


def full_state():
    sim = state["sim"]
    return {
        "graph": graph_to_json(state["graph"]),
        "tables": sim.tables if sim else {},
    }


@app.get("/api/topologies")
def list_topologies():
    return [p.stem for p in TOPO_DIR.glob("*.yaml")]


@app.post("/api/load/preloaded/{name}")
def load_preloaded(name: str):
    path = TOPO_DIR / f"{name}.yaml"
    if not path.exists():
        raise HTTPException(404, "Topology not found")
    graph = load_topology(str(path))
    state["graph"] = graph
    state["sim"] = Simulator(graph)
    return full_state()


@app.post("/api/load/upload")
async def load_upload(file: UploadFile = File(...)):
    content = (await file.read()).decode()
    try:
        graph = load_topology(content, is_file=False)
    except Exception as e:
        raise HTTPException(400, f"Invalid topology: {e}")
    state["graph"] = graph
    state["sim"] = Simulator(graph)
    return full_state()


@app.post("/api/fail-link")
def fail_link(body: LinkFail):
    sim = state["sim"]
    if not sim:
        raise HTTPException(400, "No topology loaded")
    sim.fail_link(body.u, body.v)
    if not _connected(state["graph"]):
        raise HTTPException(400, "That failure disconnects the network")
    return full_state()


@app.post("/api/change-cost")
def change_cost(body: CostChange):
    sim = state["sim"]
    if not sim:
        raise HTTPException(400, "No topology loaded")
    if body.cost < 0:
        raise HTTPException(400, "Cost cannot be negative")
    sim.change_cost(body.u, body.v, body.cost)
    return full_state()


@app.post("/api/trace")
def trace(body: Trace):
    sim = state["sim"]
    if not sim:
        raise HTTPException(400, "No topology loaded")
    return {"path": sim.trace_path(body.src, body.dst)}


@app.get("/api/distance-vector")
def dv(split_horizon: bool = False):
    graph = state["graph"]
    if not graph:
        raise HTTPException(400, "No topology loaded")
    vectors, rounds, _ = distance_vector(graph, split_horizon=split_horizon)
    return {
        "rounds": rounds,
        "vectors": {n: {d: c for d, (c, _) in v.items()} for n, v in vectors.items()},
    }


def _connected(graph):
    verts = graph.get_all_vertices()
    if not verts:
        return True
    seen, stack = set(), [verts[0]]
    while stack:
        u = stack.pop()
        if u in seen:
            continue
        seen.add(u)
        stack.extend(n for n, _ in graph.get_neighbours(u))
    return len(seen) == len(verts)


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory="static"), name="static")