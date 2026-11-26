import requests

from config import get_config

BASE_URL = "https://api.pishock.com"


def get_headers():
    config = get_config()

    api_key = config["api_key"].strip()

    if not api_key:
        raise ValueError("PiShock API key is missing")

    return {"X-PiShock-Api-Key": api_key}


def get_account():
    response = requests.get(
        f"{BASE_URL}/Account",
        headers=get_headers(),
        timeout=10,
    )
    response.raise_for_status()

    return response.json()


def get_shockers(user_id):
    response = requests.get(
        f"{BASE_URL}/Share/GetShared",
        headers=get_headers(),
        timeout=10,
    )
    response.raise_for_status()

    shockers = response.json()
    shockers = [s for s in shockers if s["OwnerId"] == user_id and not s["Paused"]]

    if any(not s["IsV3"] for s in shockers):
        raise RuntimeError("All PiShock devices must support V3")

    return shockers


def operate(shocker_id, operation, duration, intensity):
    response = requests.post(
        f"{BASE_URL}/Shockers/OperateById/{shocker_id}",
        headers=get_headers(),
        json={
            "AgentName": "tychos-pishock-integrations",
            "Operation": operation,
            "Duration": int(float(duration) * 1000),  # duration in seconds to ms
            "Intensity": intensity,
        },
        timeout=10,
    )

    response.raise_for_status()
    return True
