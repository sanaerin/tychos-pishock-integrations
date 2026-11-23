import time
from pathlib import Path

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
    print(f"Event: {event}")

    if event == "PLAYER_BUSTED":
        print("Player busted")
    elif event == "PLAYER_LOST_ALL_IN":
        print("Player lost all-in")
    elif event == "PLAYER_LOST":
        print("Player lost")


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


if __name__ == "__main__":
    listen()
