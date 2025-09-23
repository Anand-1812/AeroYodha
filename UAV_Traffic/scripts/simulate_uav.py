import math
import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

# -------------------------------
# Utility
# -------------------------------
def euclid(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

# -------------------------------
# Graph generation
# -------------------------------
def build_random_graph(n_nodes=14, width=12, height=8, k_nearest=3, seed=42):
    random.seed(seed)
    np.random.seed(seed)
    G = nx.Graph()
    pos = {}
    for i in range(n_nodes):
        node = f"N{i}"
        pos[node] = (random.random()*width, random.random()*height)
        G.add_node(node)
    nodes = list(pos.keys())
    for a in nodes:
        dists = []
        for b in nodes:
            if a==b: continue
            d = euclid(pos[a], pos[b])
            dists.append((d,b))
        dists.sort(key=lambda x:x[0])
        for _, b in dists[:k_nearest]:
            if not G.has_edge(a,b):
                dist = euclid(pos[a], pos[b])
                G.add_edge(a,b,weight=dist)
    return G,pos

# -------------------------------
# UAV class (continuous + discrete)
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
        self.path_nodes = self.compute_path()
        self.pos = np.array(self.positions[start_node], dtype=float)
        self.trajectory = [tuple(self.pos)]
        self.wait_count = 0  # for replan if blocked

    def compute_path(self):
        try:
            return nx.shortest_path(self.G, self.cur_node, self.goal_node, weight='weight')
        except nx.NetworkXNoPath:
            return [self.cur_node]

    def nearest_node(self):
        return min(self.positions.keys(), key=lambda n: euclid(self.pos, self.positions[n]))

    def next_node(self):
        if self.reached or self.next_node_index >= len(self.path_nodes)-1:
            return None
        return self.path_nodes[self.next_node_index+1]

    def move_step(self, dt, node_reservation):
        """Move UAV along path. dt in seconds. Node_reservation prevents collisions."""
        if self.reached: return

        nxt_node = self.next_node()
        if nxt_node is None:  # at goal
            self.reached = True
            return

        # Check discrete node reservation
        reserved = node_reservation.get(nxt_node)
        if reserved is not None and reserved != self.id:
            # blocked, wait this step
            self.wait_count += 1
            self.trajectory.append(tuple(self.pos))
            return

        # Move continuous
        target_pos = np.array(self.positions[nxt_node])
        vec = target_pos - self.pos
        dist = np.linalg.norm(vec)
        step = self.speed*dt
        if step >= dist:
            # reach next node
            self.pos = target_pos.copy()
            self.cur_node = nxt_node
            self.next_node_index += 1
            self.trajectory.append(tuple(self.pos))
            self.wait_count = 0
            if self.cur_node == self.goal_node:
                self.reached = True
        else:
            self.pos += vec/dist*step
            self.trajectory.append(tuple(self.pos))

    def replan_if_stuck(self, node_reservation):
        """Replan if UAV waited too long."""
        if self.wait_count>=3:
            blocked_nodes = set(node_reservation.keys())
            G2 = self.G.copy()
            # Always allow the goal node
            blocked_nodes.discard(self.cur_node)
            blocked_nodes.discard(self.goal_node)
            for n in blocked_nodes:
                if n in G2:
                    G2.remove_node(n)

            if self.goal_node not in G2:
                return
            
            try:
                new_path = nx.shortest_path(G2, self.cur_node, self.goal_node, weight='weight')
                self.path_nodes = new_path
                self.next_node_index=0
                self.wait_count=0
            except nx.NetworkXNoPath:
                pass

# -------------------------------
# Simulation
# -------------------------------
def merged_simulation(num_uavs=5, dt=0.25, sim_time=60):
    G,pos = build_random_graph(n_nodes=14, width=12, height=8, k_nearest=3, seed=42)

    # Optional: remove some nodes as no-fly
    planning_graph = G.copy()
    nofly_nodes = set(random.sample(list(G.nodes()),2))
    planning_graph.remove_nodes_from(nofly_nodes)

    # Start/goal nodes
    candidate_nodes = list(planning_graph.nodes())
    starts = random.sample(candidate_nodes, num_uavs)
    goals = []
    for s in starts:
        g=random.choice(candidate_nodes)
        while g==s:
            g=random.choice(candidate_nodes)
        goals.append(g)

    # UAV objects
    uavs = [UAV(i, starts[i], goals[i], pos, planning_graph, speed=1.2) for i in range(num_uavs)]

    # Matplotlib init
    fig,ax=plt.subplots(figsize=(10,6))
    nx.draw_networkx_edges(G,pos,ax=ax,alpha=0.4)
    nx.draw_networkx_nodes(G,pos,ax=ax,node_size=80)
    nx.draw_networkx_labels(G,pos,ax=ax,font_size=8)
    if nofly_nodes:
        nx.draw_networkx_nodes(G,pos,nodelist=list(nofly_nodes),node_color='red',node_size=120,ax=ax)

    # Main simulation loop
    steps = int(sim_time/dt)
    for step in range(steps):
        # Discrete node reservation
        node_reservation = {u.cur_node: u.id for u in uavs if not u.reached}

        # Move UAVs
        for u in uavs:
            u.move_step(dt,node_reservation)

        # Replan if stuck
        for u in uavs:
            u.replan_if_stuck(node_reservation)

        # Visualization
        ax.clear()
        nx.draw_networkx_edges(G,pos,ax=ax,alpha=0.3)
        nx.draw_networkx_nodes(G,pos,ax=ax,node_size=60)
        nx.draw_networkx_labels(G,pos,ax=ax,font_size=7)
        if nofly_nodes:
            nx.draw_networkx_nodes(G,pos,nodelist=list(nofly_nodes),node_color='red',node_size=120,ax=ax)
        xs=[u.pos[0] for u in uavs]
        ys=[u.pos[1] for u in uavs]
        ax.scatter(xs,ys,s=120,color='blue')
        ax.set_title(f"Step {step}")
        plt.pause(0.1)

        if all(u.reached for u in uavs):
            print(f"All UAVs reached their goals at step {step}")
            break

    plt.show()

if __name__=="__main__":
    merged_simulation(num_uavs=5,dt=0.25,sim_time=60)
