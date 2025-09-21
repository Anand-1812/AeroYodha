import networkx as nx
import math

def build_airspace_graph():
    G = nx.DiGraph()

    # Add nodes: node_id, position
    G.add_node("A", pos=(0, 0))
    G.add_node("B", pos=(100, 0))
    G.add_node("C", pos=(100, 100))
    G.add_node("D", pos=(0, 100))

    # Function to compute distance
    def distance(p1, p2):
        return math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)

    # Add edges with metadata
    G.add_edge("A", "B", length=distance(G.nodes["A"]["pos"], G.nodes["B"]["pos"]), max_speed=10)
    G.add_edge("B", "C", length=distance(G.nodes["B"]["pos"], G.nodes["C"]["pos"]), max_speed=10)
    G.add_edge("C", "D", length=distance(G.nodes["C"]["pos"], G.nodes["D"]["pos"]), max_speed=10)
    G.add_edge("D", "A", length=distance(G.nodes["D"]["pos"], G.nodes["A"]["pos"]), max_speed=10)
    G.add_edge("A", "D", length=distance(G.nodes["A"]["pos"], G.nodes["C"]["pos"]), max_speed=7)  # diagonal
    G.add_edge("B", "D", length=distance(G.nodes["B"]["pos"], G.nodes["D"]["pos"]), max_speed=7)  # diagonal

    return G

def shortest_path(G, start, end):
    return nx.shortest_path(G, source=start, target=end, weight="length")

def add_no_fly_zone(G, blocked_edges):
    for src, dst in blocked_edges:
        if G.has_edge(src, dst):
            G.remove_edge(src, dst)

