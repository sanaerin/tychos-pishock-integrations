ShockEventListener = ShockEventListener or {}
local mod = ShockEventListener

mod.playerName = "Player"
mod.allInSeen = mod.allInSeen or false

local function log(event)
    local f = io.open("poker_events.txt", "a")
    if f then
        f:write(event .. "\n")
        f:close()
    end
end

function mod.scan()
    local gameTable = GameObject:GetTable()
    local plrs = gameTable:GetPlayers()

    for _, p in pairs(plrs) do
        if p:GetName() == mod.playerName then
            local chips = p.chips
            local pot = p.chipsInPot

            if chips == 0 and pot > 0 then
                if not mod.allInSeen then
                    mod.allInSeen = true
                    log("ALL_IN_DETECTED")
                end
            elseif mod.allInSeen and pot == 0 then
                if chips == 0 then
                    log("ALL_IN_LOST")
                else
                    log("ALL_IN_WON")
                end

                mod.AllInSeen = false
            end
            return
        end
    end
    log("Player not found")
end

log("Shock event listener started")
