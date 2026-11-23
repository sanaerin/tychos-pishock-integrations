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
    local event
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

                event = "PLAYER_LOST"

                if allIn then
                    event = "PLAYER_LOST_ALL_IN"
                end

                log(event)

                return originalLoss(self, ...)
            end

            p.BustOut = function(self, ...)
                event = "PLAYER_BUSTED"
                log(event)
                return originalBustOut(self, ...)
            end

            p._eventHooksInstalled = true

            return
        end
    end
end