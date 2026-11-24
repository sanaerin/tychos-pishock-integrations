ShockEventListener = ShockEventListener or {}
local mod = ShockEventListener

mod.playerName = "Player"

local log = function(event)
    local f = io.open("pishock_events.txt", "a")
    if f then
        f:write(event .. "\n")
        f:close()
    end
end

if not mod.hooksInstalled then
    local originalHandleLoss = HumanPlayer.HandleLoss
    local originalBustOut = HumanPlayer.BustOut

    HumanPlayer.HandleLoss = function(self, ...)
        if self:GetName() == mod.playerName then
            if self:IsAllIn() then
                log("PLAYER_LOST_ALL_IN")
            else
                log("PLAYER_LOST")
            end
        end

        return originalHandleLoss(self, ...)
    end

    HumanPlayer.BustOut = function(self, ...)
        if self:GetName() == mod.playerName then
            log("PLAYER_BUSTED")
        end

        return originalBustOut(self, ...)
    end

    mod.hooksInstalled = true
    log("EVENT_HOOKS_INSTALLED")
end
