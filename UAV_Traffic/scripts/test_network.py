import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 1)])
nx.draw(G, with_labels=True)
plt.show()
