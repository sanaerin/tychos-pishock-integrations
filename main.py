from pishock import PiShockAPI

from config import api_key, sharecode, username

api = PiShockAPI(username, api_key, sharecode)

shocker = api.shocker(sharecode)


def shocker_ready():
    shocker.beep(duration=1)
    return shocker.is_ready()
