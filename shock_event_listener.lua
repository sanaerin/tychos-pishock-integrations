ShockEventListener = ShockEventListener or {}
local mod = ShockEventListener

mod.playerName = "Player"

function mod.installHooks() -- need to run this every new game table, player is recreated each time
    local players = GameObject:GetTable():GetPlayers()

    for _, p in pairs(players) do
        if p:GetName() == mod.playerName then
            if p._eventHooksInstalled then return end

            local originalLoss = p.HandleLoss

            p.HandleLoss = function(self, ...)
                local allIn = false

                local ok, result = pcall(self.IsAllIn, self)
                if ok then
                    allIn = result == true
                end

                local f = io.open("poker_events.txt", "a")
                if f then
                    if allIn then
                        f:write("PLAYER_LOST_ALL_IN\n")
                    else
                        f:write("PLAYER_LOST\n")
                    end
                    f:close()
                end

                return originalLoss(self, ...)
            end

            p._eventHooksInstalled = true

            return
        end
    end
end

-- log("Shock event listener started")
