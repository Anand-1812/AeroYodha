import random
import networkx as nx
import json
import os
import matplotlib.pyplot as plt
from simulate_uav import build_real_grid, UAV
from visualization_helper import draw_graph_with_path, export_graph
from path_planning import path_length
import requests

# -------------------------------
# Config
# -------------------------------
BACKEND_URL = "http://localhost:8000/api/v1/uavs/"
VERY_HIGH = 1e6
NUM_NOFLY = 5  # number of random no-fly nodes

# -------------------------------
# Backend helper
# -------------------------------
def send_data_to_backend(uavs, step, nofly_nodes=None, url=BACKEND_URL):
    """Send a step snapshot of UAVs to the backend."""
    data = {
        "step": step,
        "uavs": [
            {
                "id": u.id,
                "x": float(u.pos[0]),
                "y": float(u.pos[1]),
                "start": u.start_node,
                "goal": u.goal_node,
                "reached": u.reached,
                "path": u.path_nodes,
            }
            for u in uavs
        ],
        "noFlyZones": nofly_nodes or []
    }
    try:
        resp = requests.post(url, json=data, timeout=5)
        resp.raise_for_status()
        print(f"✅ Sent step {step} to backend")
    except Exception as e:
        print(f"❌ Error sending data at step {step}: {e}")

# -------------------------------
# No-fly penalties
# -------------------------------
def apply_nofly_penalties(G, nofly_nodes=None, nofly_edges=None, penalty=VERY_HIGH):
    nofly_nodes = nofly_nodes or []
    nofly_edges = nofly_edges or []
    for node in nofly_nodes:
        if node in G:
            for neighbor in list(G.neighbors(node)):
                if G.has_edge(node, neighbor):
                    G[node][neighbor]['weight'] = penalty
                    G[neighbor][node]['weight'] = penalty
    for u, v in nofly_edges:
        if G.has_edge(u, v):
            G[u][v]['weight'] = penalty
            G[v][u]['weight'] = penalty

# -------------------------------
# Main Simulation
# -------------------------------
def merged_simulation(num_uavs=5, dt=0.25, sim_time=60, planner_algo='astar', seed=42, visualize=True):
    """Run UAV simulation with dynamic no-fly zones and backend logging."""
    random.seed(seed)

    # Build grid graph
    G, pos = build_real_grid(rows=12, cols=8)

    # Dynamically generate no-fly zones
    all_nodes = list(G.nodes())
    NOFLY_NODES_DYNAMIC = random.sample(all_nodes, NUM_NOFLY)
    apply_nofly_penalties(G, nofly_nodes=NOFLY_NODES_DYNAMIC)

    # Candidate nodes exclude no-fly nodes
    candidate_nodes = [n for n in G.nodes() if G.degree[n] > 0 and n not in NOFLY_NODES_DYNAMIC]
    if len(candidate_nodes) < num_uavs:
        raise ValueError("Not enough candidate nodes for requested UAV count.")

    # Assign distinct start/goal pairs
    starts = random.sample(candidate_nodes, num_uavs)
    goals = []
    for s in starts:
        g = random.choice(candidate_nodes)
        while g == s:
            g = random.choice(candidate_nodes)
        goals.append(g)

    # Initialize UAVs
    uavs = []
    for i in range(num_uavs):
        u = UAV(i, starts[i], goals[i], pos, G, speed=1.2 + random.random())
        u.compute_path(algo=planner_algo)
        uavs.append(u)

    print("Spawned UAVs (id: start -> goal, path_len):")
    for u in uavs:
        pl = path_length(G, u.path_nodes)
        print(f"  UAV{u.id}: {u.start_node} -> {u.goal_node}, path_len={pl}")

    # Setup plotting
    if visualize:
        fig, ax = plt.subplots(figsize=(10, 6))

    steps = int(sim_time / dt)
    for step in range(steps):
        if visualize:
            ax.clear()
            draw_graph_with_path(G, pos, path=None, start=None, goal=None, nofly_nodes=NOFLY_NODES_DYNAMIC, ax=ax)

        # Node reservation for collision avoidance
        node_reservation = {u.cur_node: u.id for u in sorted(uavs, key=lambda x: x.id)}

        # Move UAVs
        for u in uavs:
            u.move_step(dt, node_reservation)

        # Send backend data
        send_data_to_backend(uavs, step, nofly_nodes=NOFLY_NODES_DYNAMIC)

        # Visualization per step
        if visualize:
            xs = [u.pos[0] for u in uavs]
            ys = [u.pos[1] for u in uavs]
            ax.scatter(xs, ys, s=120, color='blue', zorder=5)
            for u in uavs:
                ax.text(u.pos[0], u.pos[1]+0.08, f"U{u.id}", fontsize=8, zorder=6)
            ax.set_title(f"Time : {step*dt:.2f}s")
            plt.pause(0.1)

        if all(u.reached for u in uavs):
            print(f"✅ All UAVs reached goals at step {step}")
            break

    # Export graph for frontend
    export_graph(G, pos, filepath="graph.json")

    if visualize:
        plt.show()

# -------------------------------
# Entry Point
# -------------------------------
if __name__ == "__main__":
    merged_simulation(num_uavs=5, dt=0.25, sim_time=60, planner_algo='astar', seed=42, visualize=False)
    print("Simulation completed.")
