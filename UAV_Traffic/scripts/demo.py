import random
import matplotlib.pyplot as plt
import networkx as nx
import json
import os
import joblib
import numpy as np
from simulate_uav import build_grid_graph, UAV
from visualization_helper import draw_graph_with_path, export_graph
from path_planning import path_length
from backend_connector import send_data_to_backend, log_state

# Configure your no-fly nodes/edges here (keep nodes present but penalized)
NOFLY_NODES = ["N13", "N4"]   # change as you like (must match node IDs generated)
NOFLY_EDGES = []              # e.g. [("N2","N5")]
VERY_HIGH = 10**6

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



def apply_nofly_penalties(G, nofly_nodes=None, nofly_edges=None, penalty=VERY_HIGH):
    """Apply very high weights to no-fly nodes/edges instead of removing them."""
    nofly_nodes = nofly_nodes or []
    if nofly_edges is None:
        nofly_edges = []

    # penalize edges adjacent to no-fly nodes
    for node in nofly_nodes:
        if node in G:
            for neighbor in list(G.neighbors(node)):
                if G.has_edge(node, neighbor):
                    G[node][neighbor]['weight'] = penalty
                    G[neighbor][node]['weight'] = penalty

    # penalize listed edges
    for u, v in nofly_edges:
        if G.has_edge(u, v):
            G[u][v]['weight'] = penalty
            G[v][u]['weight'] = penalty


def merged_simulation(num_uavs=5, dt=0.25, sim_time=60, planner_algo='astar', seed=42):
    """Run UAV simulation with both visualization and backend/logging."""
    G, pos = build_grid_graph(rows=12, cols=8) 

    # apply no-fly penalties
    apply_nofly_penalties(G, nofly_nodes=NOFLY_NODES, penalty=VERY_HIGH)

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

    uavs = []
    for i in range(num_uavs):
        u = UAV(i, starts[i], goals[i], pos, G, speed=1.2 + random.random())
        u.compute_path(algo=planner_algo)
        uavs.append(u)

    # debug print of assignments
    print("Spawned UAVs (id: start -> goal, path_len):")
    for u in uavs:
        pl = path_length(G, u.path_nodes)
        print(f"  UAV{u.id}: {u.start_node} -> {u.goal_node}, path_nodes={u.path_nodes}, path_len={pl}")

    # plotting setup
    fig, ax = plt.subplots(figsize=(10, 6))
    steps = int(sim_time / dt)

    for step in range(steps):
        ax.clear()
        draw_graph_with_path(G, pos,path=None, start=None, goal=None ,nofly_nodes=NOFLY_NODES, ax=ax)

        # Node reservation with priority: lower id wins
        node_reservation = {}
        for u in sorted(uavs, key=lambda x: x.id):
            node_reservation[u.cur_node] = u.id

        # move UAVs with A*
        # for u in uavs:
            # u.move_step(dt, node_reservation)

        # move UAVs with ML
        for u in uavs:
            if u.reached:
                continue

            # --- Build ML features for this UAV ---
            cur_xy = u.pos
            goal_xy = pos[u.goal_node]

            # Compute neighbor features (similar to how you trained)
            neighbors = sorted(list(G.neighbors(u.cur_node)))
            max_neighbors = 4
            feature_vector = []
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



        # Visualization per step
        # xs = [u.pos[0] for u in uavs]
        # ys = [u.pos[1] for u in uavs]
        # ax.scatter(xs, ys, s=120, color='blue', zorder=5)
        
        for u in uavs:
            ax.scatter(u.pos[0], u.pos[1], color="blue", s=120, zorder=5)
            ax.text(u.pos[0]+0.1, u.pos[1]+0.1, f"U{u.id}", fontsize=8)
            # ax.set_title(f"Time : {step*dt:.2f}s")
            ax.clear()
        
        # plt.pause(0.1)

        draw_graph_with_path(G, pos, path=None, start=None, goal=None, nofly_nodes=NOFLY_NODES, ax=ax)

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

    def save_results_json(uavs, pos, filepath="results/sim_output.json"):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        data = {
            "grid":{str(k): v for k, v in pos.items()},
            "uavs":[]
        }
        for u in uavs:
            data["uavs"].append({
                "id":u.id,
                "start":u.start_node,
                "goal":u.goal_node,
                "speed":u.speed,
                "path":u.path_nodes,
                "trajectory":[tuple(map(float,p)) for p in u.trajectory]
            })
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Result saved to {filepath}")

    plt.show()
    save_results_json(uavs, pos, filepath="results/sim_output.json")
    export_graph(G, pos, filepath="graph.json")

if __name__ == "__main__":
    merged_simulation(num_uavs=5, dt=0.25, sim_time=60, planner_algo='astar', seed=42)