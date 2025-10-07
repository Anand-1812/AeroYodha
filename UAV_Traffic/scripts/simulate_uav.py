# scripts/simulate_uav.py
import math
import random
import numpy as np
import networkx as nx
from path_planning import compute_path  # path planning algorithms

# -------------------------------
# Utility
# -------------------------------
def euclid(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

# -------------------------------
# Graph generation
# -------------------------------

# def build_grid_graph(rows=30, cols=30):
    # G = nx.grid_2d_graph(rows, cols)  # creates a lattice grid
    # pos = {(i, j): (i, j) for i, j in G.nodes()}  # positions = coordinates
    
    # # Convert to string node labels if you want consistency
    # mapping = {node: f"N{node[0]}_{node[1]}" for node in G.nodes()}
    # G = nx.relabel_nodes(G, mapping)
    # pos = {mapping[node]: coord for node, coord in pos.items()}

    # # Add weights (e.g., Euclidean distance)
    # for u, v in G.edges():
    #     (x1, y1), (x2, y2) = pos[u], pos[v]
    #     G[u][v]['weight'] = ((x1-x2)**2 + (y1-y2)**2)**0.5

    # return G, pos

def build_grid_graph(rows, cols):
    G = nx.grid_2d_graph(rows, cols)
    pos = {(i, j): (j, -i) for i in range(rows) for j in range(cols)}
    for (i, j) in G.nodes():
        G.nodes[(i, j)]["pos"] = pos[(i, j)]
    for u, v in G.edges():
        G[u][v]["weight"] = 1.0
    return G, pos


#---------------------------------
# No-fly zones application
#---------------------------------

# def apply_no_fly_zones(G, nofly_nodes):
#     VERY_HIGH = 1e6
#     for node in nofly_nodes:
#         if node in G.nodes:
#             for neighbor in list(G.neighbors(node)):
#                 if G.has_edge(node, neighbor):
#                     G[node][neighbor]['weight'] = VERY_HIGH
#                     G[neighbor][node]['weight'] = VERY_HIGH 
#     return G       

# -------------------------------
# UAV class
# -------------------------------
class UAV:
    def __init__(self, uid, start_node, goal_node, positions, graph, speed=1.5):
        self.id = uid
        self.positions = positions
        self.G = graph
        self.speed = speed
        self.start_node = start_node
        self.goal_node = goal_node
        self.reached = False
        self.cur_node = start_node
        self.next_node_index = 0
        self.path_nodes = [self.cur_node]
        self.pos = np.array(self.positions[start_node], dtype=float)
        self.trajectory = [tuple(self.pos)]
        self.wait_count = 0

    def compute_path(self, algo='astar'):
        path = compute_path(self.G, self.positions, self.cur_node, self.goal_node, algo=algo)
        if path is None:
            self.path_nodes = [self.cur_node]
            self.next_node_index = 0
            return False
        self.path_nodes = path
        # if current node is not at index 0 in returned path, set index appropriately
        # try:
        #     self.next_node_index = self.path_nodes.index(self.cur_node)
        # except ValueError:
            # if cur_node not in path (rare), set to 0
        self.next_node_index = 0
        return True

    # def nearest_node(self):
    #     return min(self.positions.keys(), key=lambda n: euclid(self.pos, self.positions[n]))

    def next_node(self):
        if self.reached or self.next_node_index >= len(self.path_nodes) - 1:
            return None
        return self.path_nodes[self.next_node_index + 1]

    def move_step(self, dt, node_reservation):
        if self.reached:
            return
        
        nxt_node = self.next_node()
        if nxt_node is None:
            self.reached = True
            return

        reserved = node_reservation.get(nxt_node)
        if reserved is not None and reserved != self.id:
            self.wait_count += 1
            self.trajectory.append(tuple(self.pos))
            return

        # Move continuous toward next node
        target_pos = np.array(self.positions[nxt_node], dtype=float)
        vec = target_pos - self.pos
        dist = np.linalg.norm(vec)

        if dist == 0:
            self.cur_node = nxt_node
            self.next_node_index += 1
            self.trajectory.append(tuple(self.pos))
            self.wait_count = 0
            if self.cur_node == self.goal_node:
                self.reached = True
            return

        step = self.speed * dt
        if step >= dist:
            self.pos = target_pos.copy()
            self.cur_node = nxt_node
            self.next_node_index += 1
            self.trajectory.append(tuple(self.pos))
            self.wait_count = 0
            if self.cur_node == self.goal_node:
                self.reached = True
        else:
            self.pos = self.pos.astype(float)
            self.pos += (vec / dist) * step
            self.trajectory.append(tuple(self.pos))

    def replan_if_stuck(self, node_reservation, wait_threshold=3):
        if self.wait_count < wait_threshold:
            return

        blocked = set(node_reservation.keys())
        G2 = self.G.copy()
        blocked.discard(self.cur_node)
        blocked.discard(self.goal_node)
        for n in blocked:
            if n in G2:
                G2.remove_node(n)

        for algo in ['astar', 'dijkstra', 'bfs']:
            path = compute_path(G2, self.positions, self.cur_node, self.goal_node, algo=algo)
            if path:
                self.path_nodes = path
                try:
                    self.next_node_index = self.path_nodes.index(self.cur_node)
                except ValueError:
                    self.next_node_index = 0
                self.wait_count = 0
                return

# -------------------------------
# Simulation helper for backend
# -------------------------------
def run_simulation(num_uavs=5, dt=0.25, sim_time=60, seed=42):
    G, pos = build_grid_graph(n_nodes=14, width=12, height=8, k_nearest=3, seed=seed)

    candidate_nodes = list(G.nodes())
    starts = random.sample(candidate_nodes, num_uavs)
    goals = []
    for s in starts:
        g = random.choice(candidate_nodes)
        while g == s:
            g = random.choice(candidate_nodes)
        goals.append(g)

    uavs = [UAV(i, starts[i], goals[i], pos, G, speed=1.2) for i in range(num_uavs)]

    steps = int(sim_time / dt)
    snapshots = []

    for step in range(steps):
        node_reservation = {u.cur_node: u.id for u in uavs if not u.reached}
        for u in uavs:
            u.move_step(dt, node_reservation)
        for u in uavs:
            u.replan_if_stuck(node_reservation)

        # Save backend snapshot
        snapshot = [
            {
                "_id": f"UAV{u.id}",
                "type": "commercial",
                "status": "flying" if not u.reached else "idle",
                "latitude": float(u.pos[0]),
                "longitude": float(u.pos[1]),
                "altitude": 100.0,
                "batteryLevel": round(random.uniform(50, 100), 2)
            }
            for u in uavs
        ]
        snapshots.append(snapshot)

        if all(u.reached for u in uavs):
            break

    return snapshots

if __name__ == "__main__":
    snaps = run_simulation()
    for s in snaps:
        print(s)
