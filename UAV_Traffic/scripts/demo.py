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
model = None
label_encoder = None
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
    nofly_count = max(1,int(num_nodes * percent))
    nofly_nodes = random.sample(list(G.nodes()), nofly_count)
    for n in nofly_nodes:
        G.nodes[n]["nofly"] = True
    return list(nofly_nodes)

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

    if visualize:
        fig, ax = plt.subplots(figsize=(10, 6))

    steps = int(sim_time / dt)
    sim_snapshots = []

    #Tracking UAV movemnet history for inconsistent behaviour
    last_positions = {u.id: [] for u in uavs}
    stuck_counter = {u.id: 0 for u in uavs}  # count how many times stuck condition triggered
    priority_order = sorted([u.id for u in uavs], key=lambda x: (0 if x==0 else 1, x))

    for step in range(steps):
        cur_occupancy = {u.cur_node: u.id for u in uavs if not u.reached}
        desired = {}
        for u in uavs:
            if u.reached:
                desired[u.id] = None
                continue

            # prev_node = u.cur_node
            move = predict_next_move(model, label_encoder, u, u.goal_node, nofly_nodes)

            # Try ML move
            if move:
                cand = apply_move(u, move, G, pos)
                if cand in G.nodes and not G.nodes[cand].get("nofly", False):
                    candidate = cand
                else:
                    candidate = None
            if candidate is None:
                # ML failed — fallback to path planning
                G_safe = u.G.copy()
                G_safe.remove_nodes_from([n for n in nofly_nodes if n in G_safe])
                try:
                    new_path = compute_path(G_safe, pos, u.cur_node, u.goal_node, algo=planner_algo)

                except Exception:
                    new_path = None
                if new_path and len(new_path) > 1:
                    candidate = new_path[1]
                else:
                    candidate = None

            desired[u.id] = candidate

        # 2) Resolve conflicts by priority
        # Build node -> list(uav_id) mapping for desired targets
        targets = {}
        for uid, node in desired.items():
            if node is None:
                continue
            targets.setdefault(node, []).append(uid)

        # Winners set (uids allowed to move), losers will wait
        allowed_to_move = set()

        # Handle conflicts for nodes targeted by >1 UAV
        for node, uids in targets.items():
            if len(uids) == 1:
                # single claimant -> allowed (but check further below for occupancy swap)
                allowed_to_move.add(uids[0])
            else:
                # choose winner by priority_order (lowest index first)
                # priority_order is list of UAV ids sorted by priority
                for p in priority_order:
                    if p in uids:
                        allowed_to_move.add(p)
                        break
                # others are denied (they will wait)

        # Prevent swaps: if A wants B.cur_node and B wants A.cur_node -> allow higher priority only
        for u in uavs:
            uid = u.id
            cand = desired.get(uid)
            if cand is None:
                continue
            # If cand currently occupied by someone
            occ = cur_occupancy.get(cand)
            if occ is not None and occ != uid:
                # if occ wants to move into uid.cur_node (swap)
                occ_desired = desired.get(occ)
                if occ_desired == u.cur_node:
                    # decide by priority
                    # if uid has higher priority than occ -> keep uid allowed, deny occ
                    if priority_order.index(uid) <= priority_order.index(occ):
                        allowed_to_move.add(uid)
                        if occ in allowed_to_move:
                            allowed_to_move.remove(occ)
                    else:
                        # occ has higher priority -> ensure occ allowed
                        allowed_to_move.add(occ)
                        if uid in allowed_to_move:
                            allowed_to_move.remove(uid)

        # Also ensure nobody moves into a node that will be occupied by a higher-priority UAV that is not moving away
        # Build set of nodes that will remain occupied by higher priority UAVs
        staying_nodes = set()
        for u in uavs:
            # if this UAV is not allowed to move or had no desired -> it will stay
            if u.id not in allowed_to_move:
                staying_nodes.add(u.cur_node)

        # Remove from allowed_to_move any UAV that would move into a staying node occupied by higher priority
        for uid in list(allowed_to_move):
            target = desired.get(uid)
            if target in staying_nodes:
                # find occupying UAV id
                occupant = cur_occupancy.get(target)
                if occupant is not None:
                    # if occupant has higher priority than uid -> deny uid
                    if priority_order.index(occupant) <= priority_order.index(uid):
                        allowed_to_move.discard(uid)

        # 3) Apply allowed moves
        new_occupancy = dict(cur_occupancy)  # copy
        for u in uavs:
            uid = u.id
            cand = desired.get(uid)
            if uid in allowed_to_move and cand is not None:
                # final safety checks
                if cand in G.nodes and not G.nodes[cand].get("nofly", False):
                    # move
                    u.cur_node = cand
                    u.pos = np.array(pos[cand])
                    new_occupancy.pop(cur_occupancy.get(u.cur_node, None), None) if False else None
                # else: invalid -> do nothing
            else:
                # wait: no change
                pass

        # 4) Update trackers for oscillation/stuck detection
        for u in uavs:
            last_positions[u.id].append(u.cur_node)
            if len(last_positions[u.id]) > 8:
                last_positions[u.id].pop(0)

            # detect stuck (same pos many times or oscillation between two nodes)
            if len(last_positions[u.id]) >= 6:
                unique = len(set(last_positions[u.id]))
                if unique == 1:
                    stuck_counter[u.id] += 1
                elif unique == 2 and last_positions[u.id][-1] == last_positions[u.id][-3]:
                    stuck_counter[u.id] += 1
                else:
                    stuck_counter[u.id] = 0

                if stuck_counter[u.id] >= 3:
                    # recompute path on nofly-safe graph and force first hop
                    G_safe = u.G.copy()
                    G_safe.remove_nodes_from([n for n in nofly_nodes if n in G_safe])
                    new_path = compute_path(G_safe, pos, u.cur_node, u.goal_node, algo=planner_algo)
                    if new_path and len(new_path) > 1:
                        print(f"⚠️ UAV{u.id} stuck for too long. Recomputing path...")
                        u.cur_node = new_path[1]
                        u.pos = np.array(pos[new_path[1]])
                        # reset history/counter
                        last_positions[u.id] = [u.cur_node]
                        stuck_counter[u.id] = 0

            if u.cur_node == u.goal_node:
                u.reached = True

        # Send each step to backend
        # send_data_to_backend(uavs, step, nofly_nodes)

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
        plt.close(fig)


# -------------------------------
# Entry Point
# -------------------------------
if __name__ == "__main__":
    merged_simulation()
    print("🎯 Simulation completed successfully.")

# scripts/demo.py
# import os
# import json
# import random
# import joblib
# import numpy as np
# import matplotlib.pyplot as plt
# import pandas as pd

# from simulate_uav import build_grid_graph, UAV
# from path_planning import compute_path
# from visualization_helper import export_graph, draw_graph_with_path

# # -------------------------------
# # Configuration
# # -------------------------------
# RESULTS_DIR = "results"
# os.makedirs(RESULTS_DIR, exist_ok=True)

# MODEL_PATH = os.path.join(RESULTS_DIR, "uav_xgb_ml.pkl")
# ENCODER_PATH = os.path.join(RESULTS_DIR, "label_encoder.pkl")

# # Try to load ML model + label encoder. If not present, simulation will use planner fallback.
# model = None
# label_encoder = None
# try:
#     model = joblib.load(MODEL_PATH)
#     label_encoder = joblib.load(ENCODER_PATH)
#     print("✅ Loaded ML model and encoder successfully.")
# except Exception as e:
#     print(f"ℹ️ ML model/encoder not loaded (will use planner fallback). Reason: {e}")

# # -------------------------------
# # Utility functions
# # -------------------------------
# def add_nofly_zones(G, percent=0.02):
#     """Randomly mark a percentage of nodes as no-fly zones. Returns a set of nodes."""
#     num_nodes = len(G.nodes)
#     nofly_count = max(1, int(num_nodes * percent))
#     nofly_nodes = random.sample(list(G.nodes()), min(nofly_count, num_nodes))
#     for n in nofly_nodes:
#         G.nodes[n]["nofly"] = True
#     return set(nofly_nodes)

# def apply_move(uav, move, G, pos):
#     """Apply a directional move string ('UP', 'DOWN', 'LEFT', 'RIGHT', 'STAY') to the UAV."""
#     cur_r, cur_c = uav.cur_node
#     if move == "UP":
#         next_node = (cur_r - 1, cur_c)
#     elif move == "DOWN":
#         next_node = (cur_r + 1, cur_c)
#     elif move == "LEFT":
#         next_node = (cur_r, cur_c - 1)
#     elif move == "RIGHT":
#         next_node = (cur_r, cur_c + 1)
#     else:
#         next_node = uav.cur_node

#     # Only move if node valid and not no-fly
#     if next_node in G.nodes and not G.nodes[next_node].get("nofly", False):
#         uav.cur_node = next_node
#         uav.pos = np.array(pos[next_node], dtype=float)
#         return True
#     return False

# def build_feature_row_for_model(u, nofly_nodes):
#     """
#     Build a DataFrame row that (attempts to) match training features.
#     We try to be compatible with common training shapes:
#       - start_x,start_y,goal_x,goal_y,uav_x,uav_y,distance_to_goal,nofly_zones
#     If your trained model used different columns, prediction may fail and we fallback.
#     """
#     start_x, start_y = u.start_node
#     goal_x, goal_y = u.goal_node
#     cur_x, cur_y = u.cur_node
#     dist = float(np.hypot(goal_x - cur_x, goal_y - cur_y))
#     # Represent nofly_zones feature as count of nearby nofly neighbors (simple)
#     nf_count = int(sum(1 for nb in u.G.neighbors(u.cur_node) if nb in nofly_nodes))
#     row = {
#         "start_x": [start_x],
#         "start_y": [start_y],
#         "goal_x": [goal_x],
#         "goal_y": [goal_y],
#         "uav_x": [cur_x],
#         "uav_y": [cur_y],
#         "distance_to_goal": [dist],
#         "nofly_zones": [nf_count],
#     }
#     return pd.DataFrame(row)

# def try_predict_move(u_model, encoder, u, nofly_nodes):
#     """
#     Try to predict a *direction* ('UP','DOWN','LEFT','RIGHT','STAY') or None.
#     Handles mismatch exceptions and returns None on failure.
#     NOTE: This assumes training labels were direction strings. If your label encoder
#     maps strings differently adjust accordingly.
#     """
#     if u_model is None:
#         return None

#     try:
#         X = build_feature_row_for_model(u, nofly_nodes)

#         # Some XGBoost wrappers / versions expect same column ordering as trained.
#         # If model exposes feature_names_in_, reorder columns; otherwise try as-is.
#         cols_expected = getattr(u_model, "feature_names_in_", None)
#         if cols_expected is not None:
#             # Only keep columns that model expects (and are available). Fill missing with 0.
#             data = {}
#             for c in cols_expected:
#                 if c in X.columns:
#                     data[c] = X[c].values
#                 else:
#                     # If model expects 'episode' or other fields, give dummy value 0
#                     data[c] = [0]
#             X = pd.DataFrame(data, columns=list(cols_expected))

#         # If model is sklearn XGBClassifier, call predict
#         pred_enc = u_model.predict(X)[0]

#         # If label_encoder maps to strings, decode
#         if encoder is not None:
#             pred_label = encoder.inverse_transform([pred_enc])[0]
#         else:
#             # if model already returns strings (rare), use it
#             pred_label = pred_enc

#         # If model predicted a direction word, return it. If it returned node id
#         # (like 'N1_2'), convert it into a direction relative to current node.
#         if isinstance(pred_label, str):
#             if pred_label in {"UP","DOWN","LEFT","RIGHT","STAY"}:
#                 return pred_label
#             # If label looks like a node tuple or "N..." string, attempt to parse
#             if isinstance(pred_label, str) and pred_label.startswith("N"):
#                 # parse "N{r}_{c}" style
#                 try:
#                     _, coords = pred_label.replace("N", "").split("_", 1)
#                     r_str, c_str = coords.split("_") if "_" in coords else (pred_label, "")
#                 except Exception:
#                     # fallback: cannot decode; return None
#                     return None
#         # otherwise return None (fallback)
#         return None

#     except Exception as e:
#         # Print compact reason and fallback
#         print(f"⚠️ ML prediction failed for UAV{u.id}: {e}")
#         return None

# # -------------------------------
# # Main Simulation
# # -------------------------------
# def merged_simulation(
#     num_uavs=7,
#     dt=0.25,
#     sim_time=60,
#     planner_algo="astar",
#     seed=None,
#     visualize=True,
#     nofly_percent=0.02,
# ):
    
#     if seed is not None:
#         random.seed(seed)
#         np.random.seed(seed)
#     else:
#         random.seed()
#         np.random.seed()

#     # Build environment graph (30x30 default)
#     rows, cols = 30, 30
#     G, pos = build_grid_graph(rows=rows, cols=cols)

#     # Create no-fly zones (random)
#     nofly_nodes = add_nofly_zones(G, percent=nofly_percent)
#     print(f"🟠 No-fly zones generated: {len(nofly_nodes)} nodes")

#     # Choose random but valid starts/goals (not in nofly)
#     candidate_nodes = [n for n in G.nodes() if n not in nofly_nodes]

#     # ✅ Ensure there are enough free nodes
#     if len(candidate_nodes) < num_uavs * 2:
#         raise RuntimeError(
#             "Not enough candidate nodes for requested UAV count. "
#             "Lower num_uavs or reduce nofly_percent."
#         )

#     starts, goals = [], []
#     used_nodes = set()  # to prevent overlap

#     for _ in range(num_uavs):
#         # pick start not used before and not in no-fly
#         s = random.choice([n for n in candidate_nodes if n not in used_nodes])
#         used_nodes.add(s)

#         # pick goal that is different, not used, not in no-fly
#         g = random.choice([n for n in candidate_nodes if n != s and n not in used_nodes])
#         used_nodes.add(g)

#         starts.append(s)
#         goals.append(g)

#     # Create UAV objects
#     uavs = []
#     for i in range(num_uavs):
#         u = UAV(i, starts[i], goals[i], pos, G, speed=1.2 + random.random())
#         # compute initial discrete path on the graph (for fallback)
#         u.compute_path(algo=planner_algo)
#         uavs.append(u)

#     print("🚁 UAVs initialized:")
#     for u in uavs:
#         print(f"  UAV{u.id}: start={u.start_node}, goal={u.goal_node}, initial_path_len={len(u.path_nodes)}")

#     # visualization setup
#     if visualize:
#         fig, ax = plt.subplots(figsize=(10, 6))

#     # Simulation parameters
#     steps = int(sim_time / dt)
#     sim_snapshots = []

#     # For collision avoidance and priority: UAV0 highest priority (lowest id wins)
#     # Node reservation will be updated each step
#     # For stuck detection:
#     last_positions = {u.id: [] for u in uavs}
#     stuck_counter = {u.id: 0 for u in uavs}

#     for step in range(steps):
#         # build node reservation: nodes currently occupied -> priority by ID (lower id wins)
#         node_reservation = {}
#         for u in sorted(uavs, key=lambda uu: uu.id):
#             if not u.reached:
#                 node_reservation[u.cur_node] = u.id

#         # process UAVs in priority order (UAV0 first)
#         for u in sorted(uavs, key=lambda uu: uu.id):
#             if u.reached:
#                 continue

#             prev = u.cur_node

#             # Try ML prediction (robust)
#             move = try_predict_move(model, label_encoder, u, nofly_nodes)

#             moved = False
#             if move:
#                 print("Using ML")
#                 # if ML suggests a direction, compute intended node and check reservation/ no-fly
#                 cur_r, cur_c = u.cur_node
#                 if move == "UP":
#                     intended = (cur_r - 1, cur_c)
#                 elif move == "DOWN":
#                     intended = (cur_r + 1, cur_c)
#                 elif move == "LEFT":
#                     intended = (cur_r, cur_c - 1)
#                 elif move == "RIGHT":
#                     intended = (cur_r, cur_c + 1)
#                 else:
#                     intended = u.cur_node

#                 # check validity, no-fly, and reservation (priority)
#                 if (intended in G.nodes and not G.nodes[intended].get("nofly", False)
#                         and (intended not in node_reservation or node_reservation[intended] > u.id)):
#                     # claim node: remove old reservation and assign new
#                     node_reservation.pop(u.cur_node, None)
#                     node_reservation[intended] = u.id
#                     u.cur_node = intended
#                     u.pos = np.array(pos[intended], dtype=float)
#                     moved = True
#             if not moved:
#                 print("Using Fallback")
#                 # fallback path planner: try to follow next node in discrete path
#                 # Ensure u.path_nodes up to date; if not, recompute
#                 if not u.path_nodes or u.cur_node not in u.path_nodes:
#                     ok = u.compute_path(algo=planner_algo)
#                 # try to step to next node in path if exists
#                 nxt = None
#                 try:
#                     if u.path_nodes and len(u.path_nodes) > 1:
#                         # path may start with current node; find index
#                         if u.cur_node in u.path_nodes:
#                             idx = u.path_nodes.index(u.cur_node)
#                             if idx + 1 < len(u.path_nodes):
#                                 nxt = u.path_nodes[idx + 1]
#                         else:
#                             # recompute path
#                             u.compute_path(algo=planner_algo)
#                             if u.cur_node in u.path_nodes:
#                                 idx = u.path_nodes.index(u.cur_node)
#                                 if idx + 1 < len(u.path_nodes):
#                                     nxt = u.path_nodes[idx + 1]
#                 except Exception:
#                     nxt = None

#                 if nxt and nxt in G.nodes and not G.nodes[nxt].get("nofly", False) and (nxt not in node_reservation or node_reservation[nxt] > u.id):
#                     node_reservation.pop(u.cur_node, None)
#                     node_reservation[nxt] = u.id
#                     u.cur_node = nxt
#                     u.pos = np.array(pos[nxt], dtype=float)
#                     moved = True
#                 else:
#                     # can't move this step; stay (reservation already exists)
#                     moved = False

#             # Track movement history for oscillation/stuck detection
#             last_positions[u.id].append(u.cur_node)
#             if len(last_positions[u.id]) > 8:
#                 last_positions[u.id].pop(0)

#             # detect stuck: not moving or oscillating between 2 nodes
#             if len(last_positions[u.id]) >= 6:
#                 if len(set(last_positions[u.id])) == 1:
#                     stuck_counter[u.id] += 1
#                 elif len(set(last_positions[u.id])) == 2 and last_positions[u.id][-1] == last_positions[u.id][-3]:
#                     stuck_counter[u.id] += 1
#                 else:
#                     stuck_counter[u.id] = 0

#                 if stuck_counter[u.id] >= 3:
#                     # force replanning using compute_path (ignore reservations for recalculation)
#                     new_path = compute_path(u.G, pos, u.cur_node, u.goal_node, algo=planner_algo)
#                     if new_path and len(new_path) > 1:
#                         u.path_nodes = new_path
#                         # immediately take next node if available and safe
#                         next_node = new_path[1]
#                         if next_node in G.nodes and not G.nodes[next_node].get("nofly", False) and (next_node not in node_reservation or node_reservation[next_node] > u.id):
#                             node_reservation.pop(u.cur_node, None)
#                             node_reservation[next_node] = u.id
#                             u.cur_node = next_node
#                             u.pos = np.array(pos[next_node], dtype=float)
#                             print(f"⚠️ UAV{u.id} stuck for too long. Recomputed path and moved to {next_node}")
#                     stuck_counter[u.id] = 0

#             # reached?
#             if u.cur_node == u.goal_node:
#                 u.reached = True

#         # end for each UAV

#         # record snapshot (for backend / results)
#         snapshot = [
#             {
#                 "id": int(u.id),
#                 "x": float(u.pos[0]),
#                 "y": float(u.pos[1]),
#                 "start": list(u.start_node),
#                 "goal": list(u.goal_node),
#                 "reached": bool(u.reached),
#                 "path": [list(n) for n in u.path_nodes],
#             } for u in uavs
#         ]
#         sim_snapshots.append(snapshot)

#         # Visualization
#         if visualize:
#             ax.clear()
#             draw_graph_with_path(G, pos, path=None, start=None, goal=None, nofly_nodes=nofly_nodes, ax=ax)
#             xs = [u.pos[0] for u in uavs]
#             ys = [u.pos[1] for u in uavs]
#             ax.scatter(xs, ys, s=100, color="blue", zorder=6)
#             for u in uavs:
#                 ax.text(u.pos[0], u.pos[1] + 0.08, f"U{u.id}", fontsize=8, zorder=7)
#             ax.set_title(f"Step {step} / {steps}")
#             plt.pause(0.05)

#         # stop if all reached
#         unreached = [u.id for u in uavs if not u.reached]
#         if unreached:
#             print(f"⚠️ Simulation ended but {len(unreached)} UAV(s) did not reach their goals: {unreached}")
#         else:
#             print("✅ All UAVs reached their goals successfully.")


#     # End of steps loop

#     # Save simulation snapshots (one file)
#     out_path = os.path.join(RESULTS_DIR, "sim_output.json")
#     with open(out_path, "w") as f:
#         json.dump(sim_snapshots, f, indent=2)
#     print(f"💾 Saved simulation output to {out_path}")

#     # Export graph with nofly flags (export_graph should write into RESULTS_DIR)
#     export_graph(G, pos, filepath="graph.json")  # our export_graph writes to results folder internally
#     print(f"💾 Saved graph to {os.path.join(RESULTS_DIR, 'graph.json')}")

#     # close plot
#     if visualize:
#         plt.close(fig)


# # -------------------------------
# # Entry Point
# # -------------------------------
# if __name__ == "__main__":
#     # You can pass seed=None for non-deterministic starts & goals (random)
#     merged_simulation(num_uavs=7, dt=0.25, sim_time=60, planner_algo="astar", seed=None, visualize=True, nofly_percent=0.02)
#     print("🎯 Simulation completed successfully.")

