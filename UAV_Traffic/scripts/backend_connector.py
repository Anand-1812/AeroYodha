import requests
import json


def send_data_to_backend(uavs, step, url="https://localhost:8000//api/v1/uavs/"):
    data = {
        "step": step,
        "uavs": [
            {
                "id": u.id,
                "x": u.pos[0],
                "y": u.pos[1],
                "start": u.start_node,
                "goal": u.goal_node,
                "reached": u.reached,
                "path": u.path_nodes,
            }
            for u in uavs
        ]
    }

    try:
        requests.post(url, json=data)
    except Exception as e:
        print("Error sending data", e)


def log_state(step, uavs, file="sim_log.jsonl"):
    with open(file, "a") as f:
        record = {
            "step": step,
            "uavs": [
                {"id": u.id, "pos": u.pos, "reached": u.reached}
                for u in uavs
            ]
        }
        f.write(json.dumps(record) + "\n")
