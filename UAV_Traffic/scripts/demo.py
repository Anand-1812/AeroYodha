# scripts/implementation.py
import random
import matplotlib.pyplot as plt
import networkx as nx
from simulate_uav import build_random_graph, UAV
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
    G, pos = build_random_graph(n_nodes=14, width=12, height=8, k_nearest=3, seed=seed)

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

    # create UAVs and compute initial paths
    uavs = []
    for i in range(num_uavs):
        u = UAV(i, starts[i], goals[i], pos, G, speed=1.2)
        ok = u.compute_path(algo=planner_algo)
        if not ok:
            print(f"Warning: UAV {i} no initial path from {starts[i]} to {goals[i]}")
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
        node_reservation = {u.cur_node: u.id for u in uavs if not u.reached}

        # move UAVs
        for u in uavs:
            u.move_step(dt, node_reservation)

        # replanning if stuck
        for u in uavs:
            u.replan_if_stuck(node_reservation, wait_threshold=3)

        # prepare snapshot for backend/log
        snapshot = [{"id": u.id, "pos": u.pos, "goal": u.goal_node, "reached": u.reached} for u in uavs]

        # send and log
        send_data_to_backend(snapshot, step)
        log_state(step, snapshot)

        # live visualization
        ax.clear()
        draw_graph_with_path(G, pos, path=None, start=None, goal=None,
                             nofly_nodes=NOFLY_NODES, nofly_edges=NOFLY_EDGES, ax=ax)
        xs = [u.pos[0] for u in uavs]
        ys = [u.pos[1] for u in uavs]
        ax.scatter(xs, ys, s=120, color='blue', zorder=5)
        for u in uavs:
            ax.text(u.pos[0], u.pos[1] + 0.08, f"U{u.id}", fontsize=8, zorder=6)
        ax.set_title(f"Time : {step*dt:.2f}s")
        plt.pause(0.1)

        if all(u.reached for u in uavs):
            print(f"All UAVs reached their goals at step {step}")
            break

    plt.show()


def main():
    merged_simulation(num_uavs=5, dt=0.25, sim_time=60, planner_algo='astar', seed=42)


if __name__ == "__main__":
    main()
