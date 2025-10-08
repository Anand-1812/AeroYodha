import os
import json
import random
import argparse
import pandas as pd
from tqdm import tqdm
from pathlib import Path

from simulate_uav import build_grid_graph, UAV
from path_planning import compute_path
from demo import add_nofly_zones

MAX_NEIGHBORS = 4

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

def parse_node(node):
    _, coords = node.split("N")[-1], node #safety
    r ,c = map(int, node.replace("N", "").split("_"))
    return r, c

def generate_random_coordinates(rows, cols):
    r = random.randint(0, rows - 1)
    c = random.randint(0, cols - 1)
    return (r,c)

def generate_dataset(args):

    random.seed(args.seed)
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    data = []

    print(f"\n🚀 Generating dataset with {args.episodes} episodes × {args.num_uavs} UAVs per episode")
    print(f"Grid: {args.rows}x{args.cols}, Label Algo: {args.label_algo}\n")

    for ep in tqdm(range(args.episodes), desc="Generating Episodes"):
        # Build grid and apply no-fly zones
        graph, pos = build_grid_graph(args.rows, args.cols)
        no_fly_zones = add_nofly_zones(graph, percent=args.nofly_percent)

        for _ in range(args.num_uavs):
            start = generate_random_coordinates(args.rows, args.cols)
            goal = generate_random_coordinates(args.rows, args.cols)

            # Avoid same start and goal
            if start == goal:
                continue

            try:
                path = compute_path(graph, pos, start, goal, algo=args.label_algo)

                if not path or len(path) < 2:
                    continue

                # Record step-by-step data
                for i in range(len(path) - 1):
                    current = path[i]
                    next_step = path[i + 1]

                    curr_x , curr_y = current
                    next_x, next_y = next_step
                    goal_x, goal_y = goal
                    start_x, start_y = start

                    dx = next_x - curr_x
                    dy = next_y - curr_y

                    # Encode move direction
                    if dx == 1 and dy == 0:
                        move = "DOWN"
                    elif dx == -1 and dy == 0:
                        move = "UP"
                    elif dx == 0 and dy == 1:
                        move = "RIGHT"
                    elif dx == 0 and dy == -1:
                        move = "LEFT"
                    else:
                        move = "STAY"

                    # print(f"Episode {ep}, UAV start={start}, goal={goal}, path_len={len(path)}")

                    data.append({
                        "episode": ep,
                        "start_x": start_x,
                        "start_y": start_y,
                        "goal_x": goal_x,
                        "goal_y": goal_y,
                        "uav_x": curr_x,
                        "uav_y": curr_y,
                        "distance_to_goal": ((goal_x - curr_x) ** 2 + (goal_y - curr_y) ** 2) ** 0.5,
                        "nofly_zones": list(no_fly_zones),
                        "next_move": move
                    })

            except Exception as e:
                print(f"Failed for start={start}, goal={goal}: {e}")

    if not data:
        print("Warning : No data generated")


    # Save as JSONL
    jsonl_path = os.path.join(RESULTS_DIR,"uav_dataset.jsonl")
    with open(jsonl_path, "w") as f:
        for entry in data:
            f.write(json.dumps(entry) + "\n")

    print(f"✅ Dataset saved to {jsonl_path}")

    # Flatten for CSV
    df = pd.DataFrame(data)
    csv_path = os.path.join(RESULTS_DIR,"uav_dataset.csv")
    df.to_csv(csv_path, index=False)
    print(f"✅ CSV dataset saved to {csv_path}")

    # Split into train/test
    train_df = df.sample(frac=args.train_fraction, random_state=args.seed)
    test_df = df.drop(train_df.index)

    train_df.to_csv(os.path.join(RESULTS_DIR,"uav_train.csv"), index=False)
    test_df.to_csv(os.path.join(RESULTS_DIR,"uav_test.csv"), index=False)

    print("✅ Train/test split completed.")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=500)
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--num_uavs", type=int, default=5)
    parser.add_argument("--rows", type=int, default=30)
    parser.add_argument("--cols", type=int, default=30)
    parser.add_argument("--nofly_per_episode", type=int, default=2)
    parser.add_argument("--label_algo", type=str, default="astar", choices=["dijkstra","astar","bfs"])
    parser.add_argument("--out_jsonl", type=str, default="dataset.jsonl")
    parser.add_argument("--out_csv", type=str, default="dataset_flat.csv")
    parser.add_argument("--train_fraction", type=float, default=0.8)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--nofly_percent", type=float, default=0.06)
    args = parser.parse_args()
    generate_dataset(args)
