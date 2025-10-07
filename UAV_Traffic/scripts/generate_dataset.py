"""
Generates synthetic dataset for UAV next-move supervision.
Writes:
 - results/dataset.jsonl   (raw JSON per-sample)
 - results/dataset_flat.csv (flattened tabular CSV)
 - results/dataset_train.csv, results/dataset_test.csv (after split)
"""
import os
import json
import random
import argparse
from collections import OrderedDict
from functools import partial
import numpy as np
from simulate_uav import build_grid_graph, UAV, apply_no_fly_zones
from path_planning import compute_path, path_length

# -------------------------
# Helpers
# -------------------------
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

def euclid(a, b):
    return float(((a[0]-b[0])**2 + (a[1]-b[1])**2)**0.5)

def label_next_node(G, pos, cur_node, goal_node, algo='dijkstra'):
    """
    Return the next node id from cur_node toward goal_node using `algo`.
    If no path -> return "WAIT".
    """
    path = compute_path(G, pos, cur_node, goal_node, algo=algo)
    if not path or len(path) < 2:
        return "WAIT"
    return path[1]

def sample_episode(G, pos, nofly_nodes, num_uavs, steps, planner_label_algo, dt=0.25):
    """
    Run a short scenario and collect samples.
    Returns list of sample dicts.
    """
    # choose start/goal positions (exclude nofly)
    candidate_nodes = [n for n in G.nodes() if n not in nofly_nodes and G.degree[n] > 0]
    if len(candidate_nodes) < num_uavs*2:
        raise ValueError("Not enough candidate nodes for UAVs")

    starts = random.sample(candidate_nodes, num_uavs)
    goals = []
    for s in starts:
        g = random.choice(candidate_nodes)
        while g == s:
            g = random.choice(candidate_nodes)
        goals.append(g)

    # Spawn UAVs (random speeds)
    uavs = []
    for i in range(num_uavs):
        u = UAV(i, starts[i], goals[i], pos, G, speed=1.0 + random.random()*0.8)
        u.compute_path(algo=planner_label_algo)  # init path
        uavs.append(u)

    samples = []
    for t in range(steps):
        # occupancy map (for features): nodes currently occupied by any UAV
        occupied = {u.cur_node: u.id for u in uavs if not u.reached}

        # record sample for each UAV
        for u in uavs:
            # Compose features
            cur_node = u.cur_node
            goal_node = u.goal_node
            cur_xy = pos[cur_node]
            goal_xy = pos[goal_node]
            # neighbors
            neighbors = []
            for nb in sorted(list(G.neighbors(cur_node))):
                nb_xy = pos[nb]
                edge_w = G[cur_node][nb].get('weight', euclid(cur_xy, nb_xy))
                is_nofly = 1 if nb in nofly_nodes else 0
                is_occupied = 1 if nb in occupied and occupied[nb] != u.id else 0
                neighbors.append({
                    "node": nb,
                    "dx": float(nb_xy[0] - cur_xy[0]),
                    "dy": float(nb_xy[1] - cur_xy[1]),
                    "edge_weight": float(edge_w),
                    "is_nofly": is_nofly,
                    "is_occupied": is_occupied
                })
            # global features
            dist_goal = euclid(cur_xy, goal_xy)
            sample = {
                "timestamp": t,
                "uav_id": u.id,
                "cur_node": cur_node,
                "cur_x": float(cur_xy[0]),
                "cur_y": float(cur_xy[1]),
                "goal_node": goal_node,
                "goal_x": float(goal_xy[0]),
                "goal_y": float(goal_xy[1]),
                "speed": float(u.speed),
                "dist_to_goal": float(dist_goal),
                "neighbors": neighbors,
            }
            # compute label (optimal next node using planner on the full graph)
            next_action = label_next_node(G, pos, cur_node, goal_node, algo=planner_label_algo)
            sample["label"] = next_action
            sample["next_action"]= next_action
            samples.append(sample)

        # Advance environment: move UAVs one time step (we keep node reservations simple)
        node_reservation = {u.cur_node: u.id for u in uavs if not u.reached}
        for u in uavs:
            u.move_step(dt, node_reservation)
        for u in uavs:
            u.replan_if_stuck(node_reservation)

    return samples

# -------------------------
# Flatten helper -> CSV columns
# -------------------------
def flatten_sample(sample, max_neighbors=4):
    """
    Create a flat dict of fixed-width neighbor features so we can save CSV rows.
    For grid, max_neighbors = 4.
    If fewer neighbors, pad with zeros and 'NONE' node id.
    """
    row = OrderedDict()
    row["uav_id"] = sample["uav_id"]
    row["timestamp"] = sample["timestamp"]
    row["cur_node"] = sample["cur_node"]
    row["cur_x"] = sample["cur_x"]
    row["cur_y"] = sample["cur_y"]
    row["goal_node"] = sample["goal_node"]
    row["goal_x"] = sample["goal_x"]
    row["goal_y"] = sample["goal_y"]
    row["speed"] = sample["speed"]
    row["dist_to_goal"] = sample["dist_to_goal"]

    # neighbors fixed slots
    for i in range(max_neighbors):
        if i < len(sample["neighbors"]):
            nb = sample["neighbors"][i]
            row[f"nb{i}_node"] = nb["node"]
            row[f"nb{i}_dx"] = nb["dx"]
            row[f"nb{i}_dy"] = nb["dy"]
            row[f"nb{i}_w"] = nb["edge_weight"]
            row[f"nb{i}_is_nofly"] = nb["is_nofly"]
            row[f"nb{i}_is_occupied"] = nb["is_occupied"]
        else:
            row[f"nb{i}_node"] = "NONE"
            row[f"nb{i}_dx"] = 0.0
            row[f"nb{i}_dy"] = 0.0
            row[f"nb{i}_w"] = 0.0
            row[f"nb{i}_is_nofly"] = 0
            row[f"nb{i}_is_occupied"] = 0

    # label
    row["label"] = sample["label"]
    row["next_action"]=sample["next_action"]
    return row

# -------------------------
# Main generator
# -------------------------
def main(args):
    random.seed(args.seed)
    all_samples = []

    for ep in range(args.episodes):
        # Randomize no-fly nodes per episode if requested
        G, pos = build_grid_graph(rows=args.rows, cols=args.cols)
        # choose some random no-fly nodes
        nofly_nodes = set()
        if args.nofly_per_episode > 0:
            # ensure we pick from nodes with degree>0
            cand = [n for n in G.nodes() if G.degree[n] > 0]
            nofly_nodes = set(random.sample(cand, min(args.nofly_per_episode, len(cand))))
            apply_no_fly_zones(G, nofly_nodes)

        samples = sample_episode(G, pos, nofly_nodes, num_uavs=args.num_uavs,
                                 steps=args.steps, planner_label_algo=args.label_algo,
                                 dt=args.dt)
        # append
        all_samples.extend(samples)

        if (ep + 1) % max(1, args.episodes // 10) == 0:
            print(f"  episode {ep+1}/{args.episodes} -> total_samples={len(all_samples)}")

    # write raw jsonl
    jsonl_path = os.path.join(RESULTS_DIR, args.out_jsonl)
    with open(jsonl_path, "w") as jf:
        for s in all_samples:
            jf.write(json.dumps(s) + "\n")
    print("Wrote", jsonl_path)

    # flatten and write csv
    import csv
    csv_path = os.path.join(RESULTS_DIR, args.out_csv)
    max_neighbors = 4
    with open(csv_path, "w", newline="") as cf:
        writer = None
        for s in all_samples:
            row = flatten_sample(s, max_neighbors=max_neighbors)
            if writer is None:
                writer = csv.DictWriter(cf, fieldnames=list(row.keys()))
                writer.writeheader()
            writer.writerow(row)
    print("Wrote", csv_path)

    # train/test split (simple random split)
    random.shuffle(all_samples)
    n = len(all_samples)
    cut = int(n * args.train_fraction)
    train = all_samples[:cut]
    test = all_samples[cut:]

    out_dir = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(out_dir, exist_ok=True)

    train_path = os.path.join(RESULTS_DIR, args.out_csv.replace(".csv", "_train.csv"))
    test_path = os.path.join(RESULTS_DIR, args.out_csv.replace(".csv", "_test.csv"))
    # reuse flattening to write
    for name, dataset, path in [("train", train, train_path), ("test", test, test_path)]:
        with open(name + "_tmp.csv", "w", newline="") as ftmp:
            writer = None
            for s in dataset:
                row = flatten_sample(s, max_neighbors=max_neighbors)
                if writer is None:
                    writer = csv.DictWriter(ftmp, fieldnames=list(row.keys()))
                    writer.writeheader()
                writer.writerow(row)
        os.replace(name + "_tmp.csv", path)

    print("Wrote train/test CSVs:", train_path, test_path)
    print("Total samples:", len(all_samples))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=500, help="How many episodes (random scenarios)")
    parser.add_argument("--steps", type=int, default=30, help="How many time steps per episode")
    parser.add_argument("--num_uavs", type=int, default=3)
    parser.add_argument("--rows", type=int, default=8)
    parser.add_argument("--cols", type=int, default=8)
    parser.add_argument("--nofly_per_episode", type=int, default=2)
    parser.add_argument("--label_algo", type=str, default="dijkstra", choices=["dijkstra","astar","bfs"])
    parser.add_argument("--out_jsonl", type=str, default="dataset.jsonl")
    parser.add_argument("--out_csv", type=str, default="dataset_flat.csv")
    parser.add_argument("--train_fraction", type=float, default=0.8)
    parser.add_argument("--dt", type=float, default=0.25)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    main(args)