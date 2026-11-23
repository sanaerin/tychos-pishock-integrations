import time
from pathlib import Path

EVENT_FILE = Path("poker_events.txt")


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
