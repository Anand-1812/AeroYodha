import networkx as nx
import matplotlib.pyplot as plt

# Create an empty graph
G = nx.Graph()

# Add nodes (waypoints)
G.add_node("A")
G.add_node("B")
G.add_node("C")

# Add edges (paths between waypoints)
G.add_edge("A", "B", weight=3.6)  # Path from A to B
G.add_edge("B", "C", weight=4.0)
G.add_edge("A", "C", weight=5.0)

# Positions of nodes in 2D space (x, y)
positions = {
    "A": (0, 0),
    "B": (2, 3),
    "C": (4, 0),
}

# Add nodes and edges to graph
G.add_nodes_from(positions.keys())
G.add_edges_from([("A", "B"), ("B", "C"), ("A", "C")])

# Draw the network
nx.draw(G, pos=positions, with_labels=True, node_size=1000, node_color="skyblue", font_size=12, font_weight="bold")
plt.title("Basic UAV Traffic Network")
plt.show()