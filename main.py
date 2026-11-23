import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk

EVENT_FILE = Path("poker_events.txt")
PISHOCK_ENABLED = False

shocker = None
if PISHOCK_ENABLED:
    try:
        from pishock import PiShockAPI

        from config import api_key, sharecode, username

        api = PiShockAPI(username, api_key, sharecode)
        shocker = api.shocker(sharecode)

        # add beep when pishock is ready
        print("PiShock API initialized")
    except Exception as e:
        print(f"Error initializing PiShock API: {e}")
        shocker = None


def handle_pishock(event):
    if not PISHOCK_ENABLED or shocker is None:
        return
    # pishock events


def handle_event(event):
    messages = {
        "PLAYER_BUSTED": "Player busted",
        "PLAYER_LOST_ALL_IN": "Player lost all-in",
        "PLAYER_LOST": "Player lost the hand",
        "EVENT_HOOKS_ALREADY_INSTALLED": "Hooks already installed, game is running or waiting for new game",
        "EVENT_HOOKS_INSTALLED": "Hooks installed, new game started",
    }

    message = messages.get(event, f"Unknown event: {event}")
    print(f"Event: {message}")


def listen():
    EVENT_FILE.touch(exist_ok=True)

    with EVENT_FILE.open("r") as f:
        f.seek(0, 2)  # check end of file

        print("Listening for events...")

        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)  # refresh interval
                continue

            event = line.strip()
            handle_event(event)


root = tk.Tk()

root.title("Tycho's PiShock Integrations")
root.minsize(600, 400)

left_frame = ttk.Frame(root, width=150, height=400)
left_frame.pack(padx=10, pady=10, side=tk.LEFT, fill=tk.Y)

status_frame = ttk.Frame(left_frame, width=150, height=100)
status_frame.pack(padx=10, pady=10)

ttk.Label(status_frame, text="PiShock Status").pack()
readyLbl = ttk.Label(status_frame, text="NOT READY", foreground="red").pack()
connect_pishock_btn = ttk.Button(status_frame, text="Connect", width=10)
connect_pishock_btn.pack(pady=5)

configure_pishock_btn = ttk.Button(status_frame, text="Configure", width=10)
configure_pishock_btn.pack(pady=5)

buttons_frame = ttk.Frame(left_frame, width=150, height=300)
buttons_frame.pack(padx=10, pady=10, side=tk.LEFT, fill=tk.Y)

right_frame = ttk.Frame(root, width=450, height=400)
right_frame.pack(padx=10, pady=10, side=tk.RIGHT, fill=tk.BOTH, expand=True)

root.mainloop()
