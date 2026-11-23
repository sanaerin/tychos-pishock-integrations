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
    local ok, gameTable = pcall(function()
        return GameObject:GetTable()
    end)

    if not ok or not gameTable then
        log("TABLE_NOT_READY")
        return
    end

    local ok, players = pcall(function()
        return gameTable:GetPlayers()
    end)

    if not ok or not players then
        log("PLAYERS_NOT_READY")
        return
    end

    for _, p in pairs(players) do
        if p:GetName() == mod.playerName then
            if p._eventHooksInstalled then
                log("EVENT_HOOKS_ALREADY_INSTALLED")
                return
            end

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

            log("EVENT_HOOKS_INSTALLED")
            return
        end
    end
end
