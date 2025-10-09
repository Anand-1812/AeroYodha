import os
import json
import random
import joblib
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from simulate_uav import build_grid_graph, UAV
from path_planning import compute_path
from visualization_helper import export_graph, draw_graph_with_path

# -------------------------------
# Configuration
# -------------------------------
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

MODEL_PATH = os.path.join(RESULTS_DIR, "uav_xgb_ml.pkl")
ENCODER_PATH = os.path.join(RESULTS_DIR, "label_encoder.pkl")

# Load trained ML model and label encoder
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
def add_nofly_zones(G, percent=0.02):
    """Randomly mark a percentage of nodes as no-fly zones."""
    num_nodes = len(G.nodes)
    nofly_count = int(num_nodes * percent)
    nofly_nodes = random.sample(list(G.nodes()), nofly_count)
    for n in nofly_nodes:
        G.nodes[n]["nofly"] = True
    return set(nofly_nodes)


def predict_next_move(model, label_encoder, u, goal_node, nofly_nodes):
    """Predict next move using ML model, handle stuck behavior and fallback if bad."""
    try:
        columns = [
            'episode', 'start_x', 'start_y', 'goal_x', 'goal_y',
            'uav_x', 'uav_y', 'distance_to_goal', 'nofly_zones'
        ]
        episode = 0  # static since simulation is not episodic
        goal_x, goal_y = goal_node
        cur_x, cur_y = u.cur_node
        start_x, start_y = u.start_node  # ✅ FIXED: actual start

        data = {
            'episode': [episode],
            'start_x': [start_x],
            'start_y': [start_y],
            'goal_x': [goal_x],
            'goal_y': [goal_y],
            'uav_x': [cur_x],
            'uav_y': [cur_y],
            'distance_to_goal': [np.hypot(goal_x - cur_x, goal_y - cur_y)],
            'nofly_zones': [sum(1 for nb in u.G.neighbors(u.cur_node) if nb in nofly_nodes)]
        }
        X = pd.DataFrame(data, columns=columns)

        next_node_encoded = model.predict(X)[0]
        next_node = label_encoder.inverse_transform([next_node_encoded])[0]

        # ✅ Safety: avoid moving back to the same node or to a no-fly zone
        if next_node == u.cur_node or next_node in nofly_nodes:
            return None

        return next_node

    except Exception as e:
        print(f"⚠️ ML prediction failed for UAV{u.id}: {e}")
        return None


def apply_move(uav, move, G, pos):
    """Apply the predicted move to the UAV."""
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
        next_node = uav.cur_node  # STAY or invalid

    # Only move if it's a valid graph node
    if next_node in G.nodes and not G.nodes[next_node].get("nofly",False):
        uav.cur_node = next_node
        uav.pos = np.array(pos[next_node])

# -------------------------------
# Main Simulation
# -------------------------------
def merged_simulation(num_uavs=7, dt=0.25, sim_time=60, planner_algo="astar", seed=None, visualize=True):
    if seed is not None:
        random.seed(seed) #Use fixed seed if provided
    else:
        random.seed() #Otherwise use randomize seed

    # Build environment graph
    G, pos = build_grid_graph(rows=30, cols=30)
    nofly_nodes = add_nofly_zones(G, percent=0.02)
    print(f"🟠 No-fly zones generated: {len(nofly_nodes)} nodes")

    # ✅ Create random but valid start/goal nodes
    candidate_nodes = [n for n in G.nodes() if n not in nofly_nodes]

    starts, goals = [], []
    for _ in range(num_uavs):
        start = random.choice(candidate_nodes)

        # Ensure the goal is not too close to the start
        possible_goals = [n for n in candidate_nodes if n != start]
        goal = random.choice(possible_goals)
        while abs(goal[0] - start[0]) + abs(goal[1] - start[1]) < 10:
            goal = random.choice(possible_goals)

        starts.append(start)
        goals.append(goal)


    # Initialize UAVs
    uavs = []
    for i in range(num_uavs):
        uav = UAV(i, starts[i], goals[i], pos, G, speed=1.2 + random.random())
        uav.compute_path(algo=planner_algo)
        uavs.append(uav)

    print("🚁 UAVs initialized:")
    for u in uavs:
        print(f"  UAV{u.id}: start={u.start_node}, goal={u.goal_node}, initial_path_len={len(u.path_nodes)}")

    # Setup visualization
    if visualize:
        fig, ax = plt.subplots(figsize=(10, 6))

    steps = int(sim_time / dt)
    sim_snapshots = []

    #Tracking UAV movemnet history for inconsistent behaviour
    last_positions = {u.id: [] for u in uavs}
    stuck_counter = {u.id: 0 for u in uavs}  # count how many times stuck condition triggered

    for step in range(steps):
        for u in uavs:
            if u.reached:
                continue

            prev_node = u.cur_node
            move = predict_next_move(model, label_encoder, u, u.goal_node, nofly_nodes)

            # Try ML move
            if move:
                apply_move(u, move, G, pos)
            else:
                # ML failed — fallback to path planning
                new_path = compute_path(G, pos, u.cur_node, u.goal_node, algo=planner_algo)
                if new_path and len(new_path) > 1:
                    u.cur_node = new_path[1]
                    u.pos = np.array(pos[new_path[1]])

            # Track recent movement history
            last_positions[u.id].append(u.cur_node)
            if len(last_positions[u.id]) > 8:  # keep last 8 steps
                last_positions[u.id].pop(0)

            # ✅ Detect “stuck” (e.g., oscillating or frozen)
            if len(last_positions[u.id]) >= 6:
                # Case 1: UAV hasn’t moved (same position for 6+ steps)
                if len(set(last_positions[u.id])) == 1:
                    stuck_counter[u.id] += 1

                # Case 2: UAV keeps bouncing between 2 nodes (oscillation)
                elif len(set(last_positions[u.id])) == 2 and last_positions[u.id][-1] == last_positions[u.id][-3]:
                    stuck_counter[u.id] += 1
                else:
                    stuck_counter[u.id] = 0  # reset if moving normally

                # Trigger fallback path only after repeated stalling
                if stuck_counter[u.id] >= 3:
                    new_path = compute_path(G, pos, u.cur_node, u.goal_node, algo=planner_algo)
                    if new_path and len(new_path) > 1:
                        print(f"⚠️ UAV{u.id} stuck for too long. Recomputing path...")
                        u.cur_node = new_path[1]
                        u.pos = np.array(pos[new_path[1]])
                    stuck_counter[u.id] = 0  # reset counter after recovery


            if u.cur_node == u.goal_node:
                u.reached = True

        # Record snapshot
        snapshot = [
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
        sim_snapshots.append(snapshot)

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

    # -------------------------------
    # Save results
    # -------------------------------
    with open(os.path.join(RESULTS_DIR, "sim_output.json"), "w") as f:
        json.dump(sim_snapshots, f, indent=4)
    print("💾 Saved simulation output to results/sim_output.json")

    export_graph(G, pos, filepath=os.path.join(RESULTS_DIR, "graph.json"))
    print("💾 Saved graph to results/graph.json")

    if visualize:
        plt.close(fig)


# -------------------------------
# Entry Point
# -------------------------------
if __name__ == "__main__":
    merged_simulation(num_uavs=7, dt=0.25, sim_time=60, planner_algo="astar", visualize=True)
    print("🎯 Simulation completed successfully.")
