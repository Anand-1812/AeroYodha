# scripts/path_planning.py
import math
import networkx as nx

def euclid_pos(u, v, pos):
    """Euclidean distance between node u and v given pos dict."""
    (ux, uy), (vx, vy) = pos[u], pos[v]
    return math.hypot(ux - vx, uy - vy)

def path_length(G, path):
    """Sum of edge weights along a path. Returns 0 for length-1 path or None if path is None."""
    if not path:
        return None
    if len(path) < 2:
        return 0.0
    total = 0.0
    for a, b in zip(path, path[1:]):
        # if weight missing, treat as 1.0
        w = G[a][b].get('weight', 1.0)
        total += w
    return total

def bfs_path(G, source, target):
    """Unweighted shortest path (fewest hops). Returns list or None."""
    if source not in G or target not in G:
        return None
    if source == target:
        return [source]
    try:
        return nx.shortest_path(G, source=source, target=target)  # no weight -> BFS/unweighted
    except nx.NetworkXNoPath:
        return None

def dijkstra_path(G, source, target, weight='weight'):
    """Dijkstra (weighted) shortest path. Returns list or None."""
    if source not in G or target not in G:
        return None
    if source == target:
        return [source]
    try:
        return nx.dijkstra_path(G, source, target, weight=weight)
    except nx.NetworkXNoPath:
        return None

def astar_path(G, pos, source, target, weight='weight'):
    """A* using Euclidean heuristic on pos dict. Returns list or None."""
    if source not in G or target not in G:
        return None
    if source == target:
        return [source]
    try:
        h = lambda u, v=target: euclid_pos(u, v, pos)
        return nx.astar_path(G, source, target, heuristic=h, weight=weight)
    except nx.NetworkXNoPath:
        return None

# small helper to pick by name
def compute_path(G, pos, source, target, algo='astar'):
    algo = (algo or 'astar').lower()
    if algo == 'astar':
        return astar_path(G, pos, source, target)
    if algo == 'dijkstra':
        return dijkstra_path(G, source, target)
    if algo == 'bfs':
        return bfs_path(G, source, target)
    # fallback to dijkstra if unknown
    return dijkstra_path(G, source, target)
