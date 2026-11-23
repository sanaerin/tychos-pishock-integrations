import configparser
import os
from pathlib import Path

CONFIG_FILE = Path("pishock_config.ini")


def load_config():
    config = configparser.ConfigParser()

    if not CONFIG_FILE.exists():
        config["PiShock"] = {"username": "", "api_key": "", "sharecode": ""}

        with CONFIG_FILE.open("w") as f:
            config.write(f)
    else:
        config.read(CONFIG_FILE)

    return config


def get_config():
    config = load_config()

    return {
        "username": config.get("PiShock", "username", fallback=""),
        "api_key": config.get("PiShock", "api_key", fallback=""),
        "sharecode": config.get("PiShock", "sharecode", fallback=""),
    }


def open_config():
    if not CONFIG_FILE.exists():
        load_config()  # creates config if it doesn't exist

    os.startfile(CONFIG_FILE.resolve())
