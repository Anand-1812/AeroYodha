import requests
import json

def send_data_to_backend(uavs, step, url="http://localhost:3000/api/v1/uavs/"):
    """
    Send a step snapshot of UAVs to the backend.
    Matches the MongoDB UAV snapshot schema.
    """
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


def log_state(step, uavs, file="sim_log.jsonl"):
    """
    Append simulation state to local JSONL file.
    Each line = one step snapshot.
    """
    record = {
        "step": step,
        "uavs": [
            {
                "id": u.id,
                "x": float(u.pos[0]),
                "y": float(u.pos[1]),
                "reached": u.reached
            }
            for u in uavs
        ]
    }

    with open(file, "a") as f:
        f.write(json.dumps(record) + "\n")

