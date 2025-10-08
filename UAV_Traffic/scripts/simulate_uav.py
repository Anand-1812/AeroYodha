# scripts/simulate_uav.py
import math
import random
import numpy as np
import networkx as nx
from path_planning import compute_path

# -------------------------------
# Graph generation
# -------------------------------

def build_grid_graph(rows, cols):
    G = nx.grid_2d_graph(rows, cols)
    pos = {(i, j): (j, -i) for i in range(rows) for j in range(cols)}
    for (i, j) in G.nodes():
        G.nodes[(i, j)]["pos"] = pos[(i, j)]
    for u, v in G.edges():
        G[u][v]["weight"] = 1.0
    return G, pos

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
        self.next_node_index = 0
        return True

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
# Simulation helper
# -------------------------------
def run_simulation(num_uavs=7, dt=0.25, sim_time=60):

    G, pos = build_grid_graph(rows=30, cols=30)

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

    for _ in range(steps):
        node_reservation = {u.cur_node: u.id for u in uavs if not u.reached}
        for u in uavs:
            u.move_step(dt, node_reservation)
        for u in uavs:
            u.replan_if_stuck(node_reservation)

        # Save backend snapshot
        snapshot = [
            {
                "_id": f"UAV{u.id}",
                "status": "flying" if not u.reached else "idle",
                "latitude": float(u.pos[0]),
                "longitude": float(u.pos[1]),
                "altitude": 100.0
            }
            for u in uavs
        ]
        snapshots.append(snapshot)

        if all(u.reached for u in uavs):
            break

    return snapshots

# -------------------------------
# Entry Point for testing
# -------------------------------
if __name__ == "__main__":
    snaps = run_simulation()
    # for s in snaps:
    #     print(s)
