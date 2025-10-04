import random
import matplotlib.pyplot as plt
import networkx as nx
import json
import os
from simulate_uav import build_grid_graph, UAV
from visualization_helper import draw_graph_with_path
from path_planning import path_length
from backend_connector import send_data_to_backend, log_state

# Configure your no-fly nodes/edges here (keep nodes present but penalized)
NOFLY_NODES = ["N13", "N4"]   # change as you like (must match node IDs generated)
NOFLY_EDGES = []              # e.g. [("N2","N5")]
VERY_HIGH = 10**6


def apply_nofly_penalties(G, nofly_nodes=None, nofly_edges=None, penalty=VERY_HIGH):
    """Apply very high weights to no-fly nodes/edges instead of removing them."""
    nofly_nodes = nofly_nodes or []
    nofly_edges = nofly_edges or []

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
    apply_nofly_penalties(G, nofly_nodes=NOFLY_NODES, nofly_edges=NOFLY_EDGES, penalty=VERY_HIGH)

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
        draw_graph_with_path(G, pos, nofly_nodes=nofly_nodes, ax=ax)

        # Node reservation with priority: lower id wins
        node_reservation = {}
        for u in sorted(uavs, key=lambda x: x.id):
            node_reservation[u.cur_node] = u.id

        # move UAVs
        for u in uavs:
            u.move_step(dt, node_reservation)

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

if __name__ == "__main__":
    merged_simulation(num_uavs=5, dt=0.25, sim_time=60, planner_algo='astar', seed=42)
