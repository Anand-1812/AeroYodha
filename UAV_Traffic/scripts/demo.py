import random
import networkx as nx
import json
import os
import matplotlib.pyplot as plt
import joblib
import numpy as np
from simulate_uav import build_grid_graph, UAV
from visualization_helper import draw_graph_with_path, export_graph
from path_planning import path_length
import requests

# -------------------------------
# Config
# -------------------------------
NOFLY_NODES = [] #["N13", "N4"]
VERY_HIGH = 10**6
percent=0.06

model =joblib.load("results/uav_xgb_model.pkl")
le =joblib.load("results/label_encoder.pkl")

# AI

def extract_features(uav, pos, G, nofly_nodes, occupied, max_neighbors=4):
    cur_node = uav.cur_node
    goal_node = uav.goal_node
    cur_xy = pos[cur_node]
    goal_xy = pos[goal_node]

    # Global features
    dist_to_goal = np.sqrt((cur_xy[0] - goal_xy[0])**2 + (cur_xy[1] - goal_xy[1])**2)

    row = {
        "uav_id": uav.id,
        "cur_x": cur_xy[0],
        "cur_y": cur_xy[1],
        "goal_x": goal_xy[0],
        "goal_y": goal_xy[1],
        "speed": uav.speed,
        "dist_to_goal": dist_to_goal,
    }

    # Neighbors (fixed size = 4)
    neighbors = list(G.neighbors(cur_node))
    neighbors = sorted(neighbors)[:max_neighbors]
    for i in range(max_neighbors):
        if i < len(neighbors):
            nb = neighbors[i]
            nb_xy = pos[nb]
            row[f"nb{i}_dx"] = nb_xy[0] - cur_xy[0]
            row[f"nb{i}_dy"] = nb_xy[1] - cur_xy[1]
            row[f"nb{i}_w"] = G[cur_node][nb].get("weight", dist_to_goal)
            row[f"nb{i}_is_nofly"] = 1 if nb in nofly_nodes else 0
            row[f"nb{i}_is_occupied"] = 1 if nb in occupied and occupied[nb] != uav.id else 0
        else:
            row[f"nb{i}_dx"] = 0.0
            row[f"nb{i}_dy"] = 0.0
            row[f"nb{i}_w"] = 0.0
            row[f"nb{i}_is_nofly"] = 0
            row[f"nb{i}_is_occupied"] = 0

    return row

BACKEND_URL = "http://localhost:8000/api/v1/uavs/"

# -------------------------------
# Backend helper
# -------------------------------
def send_data_to_backend(uavs, step, url=BACKEND_URL):
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
        ]
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

def add_nofly_zones(G, percent):
    num_nodes = len(G.nodes)
    nofly_count = int(num_nodes * percent)
    nofly_nodes = random.sample(list(G.nodes()), nofly_count)
    for n in nofly_nodes:
        G.nodes[n]["nofly"] = True
    return set(nofly_nodes)

# def apply_nofly_penalties(G, nofly_nodes=None, nofly_edges=None, penalty=VERY_HIGH):
#     nofly_nodes = nofly_nodes or []

#     # penalize edges adjacent to no-fly nodes
#     for node in nofly_nodes:
#         if node in G:
#             for neighbor in list(G.neighbors(node)):
#                 if G.has_edge(node, neighbor):
#                     G[node][neighbor]['weight'] = penalty
#                     G[neighbor][node]['weight'] = penalty
    # for u, v in nofly_edges:
    #     if G.has_edge(u, v):
    #         G[u][v]['weight'] = penalty
    #         G[v][u]['weight'] = penalty

# -------------------------------
# Main Simulation
# -------------------------------
def merged_simulation(num_uavs=7, dt=0.25, sim_time=60, planner_algo='astar', seed=42):
    """Run UAV simulation with both visualization and backend/logging."""
    random.seed(seed)
    G, pos = build_grid_graph(rows=12, cols=8)
    add_nofly_zones(G, nofly_nodes=NOFLY_NODES)

    # candidate nodes exclude isolated or no-fly
    candidate_nodes = [n for n in G.nodes() if G.degree[n] > 0 and n not in NOFLY_NODES]
    if len(candidate_nodes) < num_uavs:
        raise ValueError("Not enough candidate nodes for requested UAV count.")

    # assign distinct start/goal pairs
    starts = random.sample(candidate_nodes, num_uavs)
    goals = []
    for s in starts:
        g = random.choice(candidate_nodes)
        while g == s:
            g = random.choice(candidate_nodes)
        goals.append(g)

    # initialize UAVs
    uavs = []
    for i in range(num_uavs):
        u = UAV(i, starts[i], goals[i], pos, G, speed=1.2 + random.random())
        u.compute_path(algo=planner_algo)
        uavs.append(u)

    print("Spawned UAVs (id: start -> goal, path_len):")
    for u in uavs:
        pl = path_length(G, u.path_nodes)
        print(f"  UAV{u.id}: {u.start_node} -> {u.goal_node}, path_len={pl}")

    # plotting setup
    fig, ax = plt.subplots(figsize=(10, 6))
    steps = int(sim_time / dt)

    for step in range(steps):
        ax.clear()
        draw_graph_with_path(G, pos, path=None, start=None, goal=None, nofly_nodes=NOFLY_NODES, ax=ax)

        # Node reservation
        node_reservation = {u.cur_node: u.id for u in sorted(uavs, key=lambda x: x.id)}

        # move UAVs
        for u in uavs:
            if u.reached:
                continue

            # --- Build ML features for this UAV ---
            cur_xy = u.pos
            goal_xy = pos[u.goal_node]

            # Compute neighbor features (similar to how you trained)
            neighbors = sorted(list(G.neighbors(u.cur_node)))
            next_idx = model.predict(x)[0]
            max_neighbors = 6
            feature_vector = []
            if 0 <= next_idx < len(neighbors):
                next_node = neighbors[next_idx]
                if next_node not in NOFLY_NODES and next_node not in node_reservation:
                    u.cur_node = next_node
                    u.pos = pos[next_node]
            else:
                pass  #fallback

            for i in range(max_neighbors):
                if i < len(neighbors):
                    nb = neighbors[i]
                    nb_xy = pos[nb]
                    dx = nb_xy[0] - cur_xy[0]
                    dy = nb_xy[1] - cur_xy[1]
                    edge_w = G[u.cur_node][nb].get('weight', ((dx)**2 + (dy)**2)**0.5)
                    is_nofly = 1 if nb in NOFLY_NODES else 0
                    is_occupied = 1 if nb in node_reservation and node_reservation[nb] != u.id else 0
                    feature_vector.extend([dx, dy, edge_w, is_nofly, is_occupied])
                else:
                    # pad missing neighbors
                    feature_vector.extend([0.0, 0.0, 0.0, 0, 0])

            # global features
            dist_goal = ((goal_xy[0]-cur_xy[0])**2 + (goal_xy[1]-cur_xy[1])**2)**0.5
            feature_vector.append(dist_goal)
            feature_vector.append(float(u.speed))

            # Convert to numpy array
            X = np.array(feature_vector).reshape(1, -1)

            # Predict next action (node)
            next_node_encoded = model.predict(X)[0]

            # Decode next_node_encoded back to node id if needed
            # For example, if you used LabelEncoder:
            # next_node = label_encoder.inverse_transform([next_node_encoded])[0]

            # Move UAV to predicted node if safe
            if next_node_encoded in G.neighbors(u.cur_node) and next_node_encoded not in NOFLY_NODES and next_node_encoded not in node_reservation:
                u.cur_node = next_node_encoded
                u.pos = pos[next_node_encoded]
            else:
                # fallback: wait or take original planner path
                pass



        # Send data to backend
        send_data_to_backend(uavs, step)

        # # Send data to backend
        # send_data_to_backend(uavs, step)

        # Visualization per step
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

    # optional: save results & graph export
    export_graph(G, pos, filepath="graph.json")

    plt.show()

# -------------------------------
# Entry Point
# -------------------------------
if __name__ == "__main__":
    merged_simulation(num_uavs=5, dt=0.25, sim_time=60, planner_algo='astar', seed=42)
    print("Simulation completed.")

