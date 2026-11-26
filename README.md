<img width="745" height="428" alt="banner" src="https://github.com/user-attachments/assets/f9ecfcad-621a-4a4b-a63e-5fee5b795ceb" />


# Tycho's PiShock Integrations
<img width="602" height="432" alt="image" src="https://github.com/user-attachments/assets/73ce49a3-f766-42df-bc99-db2f46215361" />

Tycho's PiShock Integrations adds PiShock integrations to [Poker Night at the Inventory Remastered](https://store.steampowered.com/app/3897800/Poker_Night_at_the_Inventory/) that trigger when a player does poorly or loses. 

(Caution: This mod is a work in progress and has not been tested with real PiShock using a Share Code yet, use at your own risk)

# Requirements
- [PiShock](https://pishock.com/#/) device with username, API key and a share code 
- [Poker Night at the Inventory Remastered](https://store.steampowered.com/app/3897800/Poker_Night_at_the_Inventory/)

# Installing the mod

1. Download the latest release from the [Releases](https://github.com/sanaerin/tychos-pishock-integrations/releases/) page
2. Locate your Poker Night at the Inventory Remastered install folder
```
C:\Program Files (x86)\Steam\steamapps\common\Poker Night at the Inventory Remastered
```
3. Unzip the contents of the `TychosPiShockIntegrations.zip` into the folder

You should now see `TychosPiShockIntegrations.exe` in the base folder and the following files in the `Archives` folder:
```
_resdesc_50_Common_TychosPiShockIntegrations
CP_pc_Common_TychosPiShockIntegrations.ttarch2
```

# Configuration
After launching `TychosPiShockIntegrations.exe`, click Configure. It will open a newly created file called `pishock_config.ini`. Here you can configure your PiShock and the intensity and duration of events.

You can test if the configuration works with the Test button.

### Example Config
```
[PiShock]
username = sanaerin
api_key = 5c678926-d19e-4f86-42ad-21f5a76126dd
sharecode = 17519CD8GAS

[Events]
player_lost = true
player_lost_intensity = 50
player_lost_duration = 1
player_lost_all_in = true
player_lost_all_in_intensity = 80
player_lost_all_in_duration = 2
player_busted = true
player_busted_intensity = 90
player_busted_duration = 4
```
## Getting your Username and API key
You can get your username and API key from the [PiShock account page](https://login.pishock.com/Account)

Under the API Keys section, press Add New and give the API key a name and an expiration date. After the key is created copy the key shown into the `api_key` field in the config file (you only see this key once when creating it). 

<img width="663" height="305" alt="image" src="https://github.com/user-attachments/assets/332881c9-0111-4a2c-8f5d-51631399738d" />

## Getting your Share Code
Your Share Code can be found in [PiShock Control](https://pishock.com/#/control). According to the [docs](https://docs.pishock.com/pishock/pishock-v3-documentation.html) it should be found in the top-right Share button of the shocker controls. Create a new Share Code and copy it to `sharecode` in the config.

## Playing the game (finally)
Open Poker Night at the Inventory and Tycho's PiShock Integrations. The game status should turn from Unknown into In-game when an event happens (new game, player lost, etc.). 

<img width="155" height="62" alt="image" src="https://github.com/user-attachments/assets/d6069b31-6187-4cd3-8278-20dec5fbc497" />

When an event happens in the game, you should see it in the logs as well as the result of the shock. You can manage the shock conditions in the shock conditions section. 

## Todo at some point
- Find out when the game closes to update the game status in the ui

## Story time
Initially tried to create this mod using the custom scripting functions from [Tycho's Lua Hook](https://www.nexusmods.com/pokernightattheinventory/mods/17) to listen to events. I actually got pretty far in where just pressing a keybind like F5 would trigger the script to listen for events and write them down in a txt file. For some reason though, the game kills the lua script from running when going through the pause menu to create a new game (works fine if pressing new game from the gameover screen). With so much back and forth I tried pretty much every possible function/method that there was with the help of the awesome REPL tool from [TychosLuaHookREPL](https://github.com/FriedToadTurd/TychosLuaHookREPL). Eventually I noticed that a lot of mods come in this `.ttarch2` format, and there's a cool tool for Telltale games called [TTG Tools](https://github.com/HeitorSpectre/TTG-Tools) to create mods that just plug right into the game's folder. After a lot of trial and error, I found a place where the same script I had before could be plugged directly into and this way whenever the player object gets recreated, the script doesn't die and there's no need for keybinds or other mods! 

