# backend_connector.py
import requests

# Set your backend URL here
BACKEND_URL = "http://localhost:8000/api/v1/uavs"

def send_data_to_backend(uavs, step, nofly_nodes):
    """
    Send a simulation step to the backend including UAVs and no-fly zones.
    """
    data = {
        "step": step,
        "uavs": [
            {
                "id": u.id,
                "x": float(u.pos[0]),
                "y": float(u.pos[1]),
                "start": list(u.start_node),
                "goal": list(u.goal_node),
                "reached": u.reached,
                "path": [list(n) for n in u.path_nodes]
            } for u in uavs
        ],
        "noFlyZones": [list(n) for n in nofly_nodes]
    }

    try:
        resp = requests.post(BACKEND_URL, json=data, timeout=5)
        resp.raise_for_status()
        print(f"✅ Sent step {step} to backend")
    except Exception as e:
        print(f"❌ Error sending step {step} to backend: {e}")
