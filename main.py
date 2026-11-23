from pathlib import Path
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import configparser
import os

EVENT_FILE = Path("pishock_events.txt")
CONFIG_FILE = Path("pishock_config.ini")
PISHOCK_ENABLED = True

shocker = None

def log(message):
    event_log.config(state=tk.NORMAL)
    event_log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
    event_log.see(tk.END)
    event_log.config(state=tk.DISABLED)


def load_config():
    config = configparser.ConfigParser()
    
    if not CONFIG_FILE.exists():
        config["PiShock"] = {
            "username": "",
            "api_key": "",
            "sharecode": ""
        }
        
        with CONFIG_FILE.open("w") as f:
            config.write(f)
        
        log("Created config.ini")
    else:
        config.read(CONFIG_FILE)
        
    return config

config = load_config()
username = config.get("PiShock", "username", fallback="")
api_key = config.get("PiShock", "api_key", fallback="")
sharecode = config.get("PiShock", "sharecode", fallback="")

def open_config():
    if not CONFIG_FILE.exists:
        load_config() # creates config if it doesn't exist
        
    os.startfile(CONFIG_FILE.resolve())


def connect_pishock():
    global api, shocker

    if not PISHOCK_ENABLED:
        log("PiShock is disabled")
        return

    try:
        from pishock import PiShockAPI

        if not all([api_key, sharecode, username]):
            log("PiShock: Missing configuration, please configure")
            return

        log("Connecting to PiShock API...")

        api = PiShockAPI(username, api_key)
        shocker = api.shocker(sharecode)

        info = shocker.info()

        log("PiShock: Credentials and share code accepted")
        log(f"Device: {info.name}")
        log(f"Paused: {info.is_paused}")

        if info.is_paused:
            log("PiShock is paused")
        else:
            log("PiShock is ready")

    except Exception as e:
        log(f"PiShock connection failed: {e}")
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
    log(f"Event: {message}")

    handle_pishock(event)


def listen():
    EVENT_FILE.touch(exist_ok=True)

    global event_file
    event_file = EVENT_FILE.open("r", encoding="utf-8")
    event_file.seek(0, 2)  # check end of file

    print("Listening for events...")

    check_events()


def check_events():
    line = event_file.readline()

    while line:
        event = line.strip()

        if event:
            handle_event(event)

        line = event_file.readline()

    root.after(100, check_events)  # 100ms refresh for new events


root = tk.Tk()

root.title("Tycho's PiShock Integrations")
root.minsize(600, 400)

left_frame = ttk.Frame(root, width=150, height=400)
left_frame.pack(padx=10, pady=10, side=tk.LEFT, fill=tk.Y)

status_frame = ttk.Frame(left_frame, width=150, height=100)
status_frame.pack(padx=10, pady=10)

ttk.Label(status_frame, text="PiShock Status").pack()
readyLbl = ttk.Label(status_frame, text="NOT READY", foreground="red").pack()

connect_pishock_btn = ttk.Button(
    status_frame, text="Check connection", width=20, command=connect_pishock
)
connect_pishock_btn.pack(pady=5)

configure_pishock_btn = ttk.Button(status_frame, text="Configure", width=20, command=open_config)
configure_pishock_btn.pack(pady=5)

buttons_frame = ttk.Frame(left_frame, width=150, height=300)
buttons_frame.pack(padx=10, pady=10, side=tk.LEFT, fill=tk.Y)

hand_loss_enabled = tk.BooleanVar(value=True)
all_in_loss_enabled = tk.BooleanVar(value=True)
busted_loss_enabled = tk.BooleanVar(value=True)

ttk.Label(buttons_frame, text="Shock conditions").pack(pady=5)
hand_loss_toggle = ttk.Checkbutton(
    buttons_frame, text="Lose hand", variable=hand_loss_enabled
)
hand_loss_toggle.pack(anchor="w", pady=5)

all_in_loss_toggle = ttk.Checkbutton(
    buttons_frame, text="Lose all-in", variable=all_in_loss_enabled
)
all_in_loss_toggle.pack(anchor="w", pady=5)

busted_loss_toggle = ttk.Checkbutton(
    buttons_frame, text="Busted", variable=busted_loss_enabled
)
busted_loss_toggle.pack(anchor="w", pady=5)

right_frame = ttk.Frame(root, width=450, height=400)
right_frame.pack(padx=10, pady=10, side=tk.RIGHT, fill=tk.BOTH, expand=True)


# event logs
events_frame = ttk.Frame(right_frame)
events_frame.pack(fill=tk.BOTH, expand=True, pady=10)

event_scrollbar = ttk.Scrollbar(events_frame, orient=tk.VERTICAL)

event_log = tk.Text(
    events_frame, yscrollcommand=event_scrollbar.set, state=tk.DISABLED, wrap=tk.WORD
)

event_scrollbar.config(command=event_log.yview)

event_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
event_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

event_file = None


def close_app():
    if event_file:
        event_file.close()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", close_app)

listen()
root.mainloop()
