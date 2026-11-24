import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import ttk

from config import get_config, open_config, set_event_enabled

EVENT_FILE = Path("pishock_events.txt")
PISHOCK_ENABLED = True

shocker = None


def log(message):
    event_log.config(state=tk.NORMAL)
    event_log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
    event_log.see(tk.END)
    event_log.config(state=tk.DISABLED)


def connect_pishock():
    global api, shocker

    config = get_config()

    username = config["username"]
    api_key = config["api_key"]
    sharecode = config["sharecode"]

    if not PISHOCK_ENABLED:
        log("PiShock is disabled")
        return

    try:
        from pishock import PiShockAPI

        if not any([api_key, sharecode, username]):
            log("PiShock: Configuration empty, please configure!")
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
            readyLbl.config(text="Paused", foreground="yellow")
        else:
            log("PiShock is ready")
            readyLbl.config(text="Ready", foreground="green")

    except Exception as e:
        log(f"PiShock connection failed: {e}")
        readyLbl.config(text="Not ready", foreground="red")
        shocker = None


def handle_pishock(event):
    if not PISHOCK_ENABLED or shocker is None:
        log("PiShock is not connected")
        return

    if event == "TEST":
        shocker.vibrate(1, 25)

    config = get_config()

    event_config = config["events"].get(event)

    if event_config is None:
        return

    if not event_config["enabled"]:
        log(f"{event} is disabled")
        return

    intensity = event_config["intensity"]
    duration = event_config["duration"]

    try:
        log(f"Sending PiShock command for {event}...")
        shocker.shock(intensity, duration)
        log("PiShock command submitted")

    except Exception as e:
        log(f"PiShock action failed: {e}")


def handle_event(event):
    messages = {
        "PLAYER_BUSTED": "Player busted",
        "PLAYER_LOST_ALL_IN": "Player lost all-in",
        "PLAYER_LOST": "Player lost the hand",
        "EVENT_HOOKS_INSTALLED": "New table detected",
        "TEST": "Testing PiShock",
    }

    message = messages.get(event, f"Unknown event: {event}")
    log(f"Event: {message}")

    if messages.get(event):
        ingameLbl.config(text="In-game", foreground="green")

    handle_pishock(event)


def listen():
    EVENT_FILE.touch(exist_ok=True)

    global event_file
    event_file = EVENT_FILE.open("r", encoding="utf-8")
    event_file.seek(0, 2)  # check end of file

    log("Listening for events...")

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


# status panel
ttk.Label(status_frame, text="PiShock status").pack()
readyLbl = ttk.Label(status_frame, text="Not ready", foreground="red")
readyLbl.pack()

connect_pishock_btn = ttk.Button(
    status_frame, text="Check connection", width=20, command=connect_pishock
)
connect_pishock_btn.pack(pady=5)

configtest_frame = ttk.Frame(status_frame, width=150, height=100)
configtest_frame.pack(fill="x", pady=3)

configure_pishock_btn = ttk.Button(
    configtest_frame, text="Configure", width=12, command=open_config
)
configure_pishock_btn.pack(side="left", fill="x", expand=True, padx=(0, 2))

test_pishock_btn = ttk.Button(
    configtest_frame, text="Test", width=5, command=lambda: handle_event("TEST")
)
test_pishock_btn.pack(side="left", fill="x", expand=True, padx=(2, 0))


ttk.Label(status_frame, text="Game status").pack(pady=5)
ingameLbl = ttk.Label(status_frame, text="Waiting for change", foreground="grey")
ingameLbl.pack()


# shock conditions panel
config = get_config()


def update_event_setting(event, variable):
    set_event_enabled(event, variable.get())


hand_loss_enabled = (
    tk.BooleanVar(value=config["events"]["PLAYER_LOST"]["enabled"]) or True
)
all_in_loss_enabled = (
    tk.BooleanVar(value=config["events"]["PLAYER_LOST_ALL_IN"]["enabled"]) or True
)
busted_loss_enabled = (
    tk.BooleanVar(value=config["events"]["PLAYER_BUSTED"]["enabled"]) or True
)

buttons_frame = ttk.Frame(left_frame, width=150, height=300)
buttons_frame.pack(padx=10, pady=10, side=tk.LEFT, fill=tk.Y)

ttk.Label(buttons_frame, text="Shock conditions").pack(pady=5)
hand_loss_toggle = ttk.Checkbutton(
    buttons_frame,
    text="Lose hand",
    variable=hand_loss_enabled,
    command=lambda: update_event_setting("player_lost", hand_loss_enabled),
)
hand_loss_toggle.pack(anchor="w", pady=5)

all_in_loss_toggle = ttk.Checkbutton(
    buttons_frame,
    text="Lose all-in",
    variable=all_in_loss_enabled,
    command=lambda: update_event_setting("player_lost_all_in", all_in_loss_enabled),
)
all_in_loss_toggle.pack(anchor="w", pady=5)

busted_loss_toggle = ttk.Checkbutton(
    buttons_frame,
    text="Busted",
    variable=busted_loss_enabled,
    command=lambda: update_event_setting("player_busted", busted_loss_enabled),
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
