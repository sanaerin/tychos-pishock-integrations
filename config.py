import configparser
import os
from pathlib import Path

CONFIG_FILE = Path("pishock_config.ini")


def load_config():
    config = configparser.ConfigParser()

    config["PiShock"] = {
        "api_key": "",
    }

    config["Events"] = {
        "player_lost": "true",
        "player_lost_intensity": "50",
        "player_lost_duration": "1",
        "player_lost_all_in": "true",
        "player_lost_all_in_intensity": "80",
        "player_lost_all_in_duration": "2",
        "player_busted": "true",
        "player_busted_intensity": "90",
        "player_busted_duration": "4",
    }

    if CONFIG_FILE.exists():
        config.read(CONFIG_FILE)

    with CONFIG_FILE.open("w") as f:
        config.write(f)

    return config


def get_config():
    config = load_config()

    return {
        "api_key": config.get("PiShock", "api_key"),
        "events": {
            "PLAYER_LOST": {
                "enabled": config.getboolean("Events", "player_lost"),
                "intensity": config.getint("Events", "player_lost_intensity"),
                "duration": config.getint("Events", "player_lost_duration"),
            },
            "PLAYER_LOST_ALL_IN": {
                "enabled": config.getboolean("Events", "player_lost_all_in"),
                "intensity": config.getint("Events", "player_lost_all_in_intensity"),
                "duration": config.getint("Events", "player_lost_all_in_duration"),
            },
            "PLAYER_BUSTED": {
                "enabled": config.getboolean("Events", "player_busted"),
                "intensity": config.getint("Events", "player_busted_intensity"),
                "duration": config.getint("Events", "player_busted_duration"),
            },
        },
    }


def open_config():
    if not CONFIG_FILE.exists():
        load_config()  # creates config if it doesn't exist

    os.startfile(CONFIG_FILE.resolve())


def set_event_enabled(event, enabled):
    config = load_config()
    config.set("Events", event, str(enabled).lower())

    with CONFIG_FILE.open("w") as f:
        config.write(f)
