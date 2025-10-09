# demo.py
import os
import json
import random
import joblib
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from simulate_uav import build_grid_graph, UAV
from path_planning import compute_path
from visualization_helper import export_graph, draw_graph_with_path
from backend_connector import send_data_to_backend  # Import the sender

# -------------------------------
# Configuration
# -------------------------------
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

MODEL_PATH = os.path.join(RESULTS_DIR, "uav_xgb_ml.pkl")
ENCODER_PATH = os.path.join(RESULTS_DIR, "label_encoder.pkl")

# Load trained ML model and encoder
try:
    model = joblib.load(MODEL_PATH)
    label_encoder = joblib.load(ENCODER_PATH)
    print("✅ Loaded ML model and encoder successfully.")
except Exception as e:
    print(f"❌ Error loading model or encoder: {e}")
    exit(1)

# -------------------------------
# Utility functions
# -------------------------------
def add_nofly_zones(G, percent=0.06):
    num_nodes = len(G.nodes)
    nofly_count = int(num_nodes * percent)
    nofly_nodes = random.sample(list(G.nodes()), nofly_count)
    for n in nofly_nodes:
        G.nodes[n]["nofly"] = True
    return list(nofly_nodes)

def predict_next_move(model, label_encoder, u, goal_node, nofly_nodes):
    columns = [
        'episode', 'start_x', 'start_y', 'goal_x', 'goal_y',
        'uav_x', 'uav_y', 'distance_to_goal', 'nofly_zones'
    ]
    episode = 0
    data = {
        'episode': [episode],
        'start_x': [u.pos[0]],
        'start_y': [u.pos[1]],
        'goal_x': [u.goal_pos[0]] if hasattr(u, 'goal_pos') else [0],
        'goal_y': [u.goal_pos[1]] if hasattr(u, 'goal_pos') else [0],
        'uav_x': [u.pos[0]],
        'uav_y': [u.pos[1]],
        'distance_to_goal': [
            np.hypot(u.goal_pos[0] - u.pos[0], u.goal_pos[1] - u.pos[1])
            if hasattr(u, 'goal_pos') else 0
        ],
        'nofly_zones': [sum(1 for nb in u.G.neighbors(u.cur_node) if nb in nofly_nodes)]
    }
    X = pd.DataFrame(data, columns=columns)
    try:
        next_node_encoded = model.predict(X)[0]
        next_node = label_encoder.inverse_transform([next_node_encoded])[0]
        return next_node
    except Exception as e:
        print(f"⚠️ ML prediction failed for UAV{u.id}: {e}")
        return None

def apply_move(uav, move, G, pos):
    cur_x, cur_y = uav.cur_node
    if move == "UP":
        next_node = (cur_x - 1, cur_y)
    elif move == "DOWN":
        next_node = (cur_x + 1, cur_y)
    elif move == "LEFT":
        next_node = (cur_x, cur_y - 1)
    elif move == "RIGHT":
        next_node = (cur_x, cur_y + 1)
    else:
        next_node = uav.cur_node
    if next_node in G.nodes:
        uav.cur_node = next_node
        uav.pos = np.array(pos[next_node])

# -------------------------------
# Main Simulation
# -------------------------------
def merged_simulation(num_uavs=7, dt=0.25, sim_time=60, planner_algo="astar", seed=42, visualize=True):
    random.seed(seed)
    G, pos = build_grid_graph(rows=30, cols=30)
    nofly_nodes = add_nofly_zones(G, percent=0.06)
    print(f"🟠 No-fly zones generated: {len(nofly_nodes)} nodes")

    candidate_nodes = [n for n in G.nodes() if n not in nofly_nodes]
    starts = random.sample(candidate_nodes, num_uavs)
    goals = []
    for s in starts:
        g = random.choice(candidate_nodes)
        while g == s:
            g = random.choice(candidate_nodes)
        goals.append(g)

    uavs = []
    for i in range(num_uavs):
        uav = UAV(i, starts[i], goals[i], pos, G, speed=1.2 + random.random())
        uav.compute_path(algo=planner_algo)
        uavs.append(uav)

    if visualize:
        fig, ax = plt.subplots(figsize=(10, 6))

    steps = int(sim_time / dt)
    for step in range(steps):
        for u in uavs:
            if u.reached:
                continue
            move = predict_next_move(model, label_encoder, u, u.goal_node, nofly_nodes)
            if move:
                apply_move(u, move, G, pos)
            else:
                new_path = compute_path(G, pos, u.cur_node, u.goal_node, algo=planner_algo)
                if new_path and len(new_path) > 1:
                    u.cur_node = new_path[1]
                    u.pos = np.array(pos[new_path[1]])
            if u.cur_node == u.goal_node:
                u.reached = True

        # Send each step to backend
        send_data_to_backend(uavs, step, nofly_nodes)

        # Visualization
        if visualize:
            ax.clear()
            draw_graph_with_path(G, pos, path=None, start=None, goal=None, nofly_nodes=nofly_nodes, ax=ax)
            xs = [u.pos[0] for u in uavs]
            ys = [u.pos[1] for u in uavs]
            ax.scatter(xs, ys, s=100, color="blue")
            for u in uavs:
                ax.text(u.pos[0], u.pos[1] + 0.08, f"U{u.id}", fontsize=8)
            ax.set_title(f"Step {step} / {steps}")
            plt.pause(0.05)

        if all(u.reached for u in uavs):
            print(f"✅ All UAVs reached goals at step {step}")
            break

    # Save final results locally
    with open(os.path.join(RESULTS_DIR, "sim_output.json"), "w") as f:
        json.dump([
            {
                "id": u.id,
                "x": float(u.pos[0]),
                "y": float(u.pos[1]),
                "start": list(u.start_node),
                "goal": list(u.goal_node),
                "reached": u.reached,
                "path": [list(n) for n in u.path_nodes]
            } for u in uavs
        ], f, indent=4)

    export_graph(G, pos, filepath=os.path.join(RESULTS_DIR, "graph.json"))
    if visualize:
        plt.show()

# -------------------------------
# Entry Point
# -------------------------------
if __name__ == "__main__":
    merged_simulation()
    print("🎯 Simulation completed successfully.")
