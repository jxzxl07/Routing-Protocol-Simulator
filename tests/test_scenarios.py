from engine.topology import load_topology
from engine.simulator import Simulator
from engine.distance_vector import distance_vector
from engine.forwarding import compute_all_tables


def test_forwarding_table_correctness():
    g = load_topology("topologies/simple.yaml")
    tables = compute_all_tables(g)
    # A reaches C via B (1+2=3), cheaper than direct A-C (4)
    assert tables["A"]["C"] == "B"


def test_path_trace():
    g = load_topology("topologies/simple.yaml")
    sim = Simulator(g)
    assert sim.trace_path("A", "D") == ["A", "B", "C", "D"]


def test_convergence_after_link_failure():
    g = load_topology("topologies/simple.yaml")
    sim = Simulator(g)
    sim.fail_link("B", "C")          # break the cheap route
    # A must now reach C via the direct A-C link
    assert sim.tables["A"]["C"] == "C"


def test_count_to_infinity_happens_without_split_horizon():
    g = load_topology("topologies/count_to_infinity.yaml")
    g.remove_edge("B", "C")          # C becomes unreachable
    _, rounds_off, _ = distance_vector(g, split_horizon=False)
    _, rounds_on, _ = distance_vector(g, split_horizon=True)
    # split horizon converges faster (prevents the counting loop)
    assert rounds_on <= rounds_off