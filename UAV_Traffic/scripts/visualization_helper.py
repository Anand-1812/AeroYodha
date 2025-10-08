import matplotlib.pyplot as plt
import networkx as nx
import json
import os

def draw_graph_with_path(G, pos, path=None, start=None, goal=None,
                         nofly_nodes=None, ax=None):
    """Draw graph and overlay a path (if provided)."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(9,6))
    # base graph
    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.4)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=80)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=8)

    # no-fly visualization
    if nofly_nodes:
        nf = [n for n in nofly_nodes if n in pos]
        nx.draw_networkx_nodes(G, pos, nodelist=nf, node_color='red', node_size=160, ax=ax)

    # path overlay
    if path and len(path) >= 2:
        edge_list = list(zip(path, path[1:]))
        nx.draw_networkx_nodes(G, pos, nodelist=path, node_color='orange', node_size=150, ax=ax)
        nx.draw_networkx_edges(G, pos, edgelist=edge_list, edge_color='orange', width=3, ax=ax)

    # start/goal markers
    if start and start in pos:
        ax.scatter([pos[start][0]], [pos[start][1]], s=220, marker='*', edgecolors='k', zorder=5)
        ax.text(pos[start][0], pos[start][1]+0.12, "START", fontsize=9)
    
    if goal and goal in pos:
        ax.scatter([pos[goal][0]], [pos[goal][1]], s=220, marker='X', edgecolors='k', zorder=5)
        ax.text(pos[goal][0], pos[goal][1]+0.12, "GOAL", fontsize=9)

    return ax

def export_graph(G, pos, filepath="graph.json"):
    """Export graph to JSON for frontend"""

    # If the provided path is already absolute or includes 'results', don't add it again
    if not os.path.isabs(filepath):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        filepath = os.path.join(base_dir, "results", os.path.basename(filepath))

    # Ensure the directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    graph_data = {
        "nodes": [{"id": n, "x": pos[n][0], "y": pos[n][1]} for n in G.nodes()],
        "edges": [{"source": u, "target": v, "weight": G[u][v]['weight']} for u, v in G.edges()],
    }

    with open(filepath, "w") as f:
        json.dump(graph_data, f, indent=2)

    print(f"Graph exported to {filepath}")
