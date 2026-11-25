(Caution: This mod is a work in progress, use at your own risk)

# Tycho's PiShock Integrations
<img width="602" height="432" alt="image" src="https://github.com/user-attachments/assets/73ce49a3-f766-42df-bc99-db2f46215361" />

Tycho's PiShock Integrations adds PiShock integrations to [Poker Night at the Inventory](https://store.steampowered.com/app/3897800/Poker_Night_at_the_Inventory/) that trigger when a player does poorly or loses. 

## Limitations at the moment
- Not tested with real PiShock using a sharecode yet

## Requirements
- [PiShock](https://pishock.com/#/) device with username, API key and a share code 
- [Poker Night at the Inventory](https://store.steampowered.com/app/3897800/Poker_Night_at_the_Inventory/)

## Setup and Configuration


### Installing the mod
1. Locate your Poker Night at the Inventory Remastered install folder
2. Copy the two mod files into the `Archives` folder
```
_resdesc_50_Common_TychosPiShockIntegrations
CP_pc_Common_TychosPiShockIntegrations.ttarch2
```

### Installing the PiShock mod 
(Coming soon)

## Story time
Initially tried to create this mod using the custom scripting functions from [Tycho's Lua Hook](https://www.nexusmods.com/pokernightattheinventory/mods/17) to listen to events. I actually got pretty far in where just pressing a keybind like F5 would trigger the script to listen for events and write them down in a txt file. For some reason though, the game kills the lua script from running when going through the pause menu to create a new game (works fine if pressing new game from the gameover screen). With so much back and forth I tried pretty much every possible function/method that there was with the help of the awesome REPL tool from [TychosLuaHookREPL](https://github.com/FriedToadTurd/TychosLuaHookREPL). Eventually I noticed that a lot of mods come in this `.ttarch2` format, and there's a cool tool for Telltale games called [TTG Tools](https://github.com/HeitorSpectre/TTG-Tools) to create mods that just plug right into the game's folder. After a lot of trial and error, I found a place where the same script I had before could be plugged directly into and this way whenever the player object gets recreated, the script doesn't die and there's no need for keybinds or other mods! 