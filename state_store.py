"""Shared helper for reading/writing the bot's persisted state file.

State is committed back to the repo by the GitHub Actions workflow after
each run, so uptime checks and job-alert dedup can remember what they saw
last time.
"""
import json
import os

STATE_PATH = os.path.join(os.path.dirname(__file__), "state", "bot_state.json")

DEFAULT_STATE = {
    "uptime": {},        # {url: "up" | "down"}
    "jobs_seen": [],      # list of RemoteOK job ids already alerted on
    "breach_known": {},   # {email: [breach_names_already_alerted]}
}


def load_state():
    try:
        with open(STATE_PATH, "r") as f:
            data = json.load(f)
        for key, default in DEFAULT_STATE.items():
            data.setdefault(key, default)
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return json.loads(json.dumps(DEFAULT_STATE))  # deep copy


def save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2, sort_keys=True)
