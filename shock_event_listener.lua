ShockEventListener = ShockEventListener or {}
local mod = ShockEventListener

mod.playerName = "Player"

local function log(event)
    local f = io.open("poker_events.txt", "a")
    if f then
        f:write(event .. "\n")
        f:close()
    end
end

function mod.installHooks() -- need to run this every new game table, player is recreated each time
    local players = GameObject:GetTable():GetPlayers()
    for _, p in pairs(players) do
        if p:GetName() == mod.playerName then
            if p._eventHooksInstalled then return end

            local originalLoss = p.HandleLoss
            local originalBustOut = p.BustOut

            p.HandleLoss = function(self, ...)
                local allIn = false

                local ok, result = pcall(self.IsAllIn, self)
                if ok then
                    allIn = result == true
                end

                if allIn then
                    log("PLAYER_LOST_ALL_IN")
                else
                    log("PLAYER_LOST")
                end

                return originalLoss(self, ...)
            end

            p.BustOut = function(self, ...)
                log("PLAYER_BUSTED")
                return originalBustOut(self, ...)
            end

            p._eventHooksInstalled = true

            return
        end
    end
end