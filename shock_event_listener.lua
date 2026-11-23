ShockEventListener = ShockEventListener or {}
local mod = ShockEventListener

mod.playerName = "Player"

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

                local event = "PLAYER_LOST"

                if allIn then
                    event = "PLAYER_LOST_ALL_IN"
                end

                local f = io.open("poker_events.txt", "a")
                if f then
                    f:write(event .. "\n")
                    f:close()
                end

                return originalLoss(self, ...)
            end

            p.BustOut = function(self, ...)
                local f = io.open("poker_events.txt", "a")
                if f then
                    f:write("PLAYER_BUSTED\n")
                    f:close()
                end

                return originalBustOut(self, ...)
            end

            p._eventHooksInstalled = true

            return
        end
    end
end

-- log("Shock event listener started")
