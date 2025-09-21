from simulation.graph import build_airspace_graph, shortest_path, add_no_fly_zone

def test_shortest_path():
    G = build_airspace_graph()
    path = shortest_path(G, "A", "C")
    assert path[0] == "A" and path[-1] == "C"
    add_no_fly_zone(G, [("A","C")])
    print(path)