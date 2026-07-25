-- Whole-game flow coordinator.
local states_manager = require("game.states_manager")

local GameLoop = {}

function GameLoop.load(...)
  states_manager.load(...)
end

function GameLoop.update(dt)
  states_manager.update(dt)
end

function GameLoop.draw()
  states_manager.draw()
end

function GameLoop.keypressed(key, scancode, isrepeat)
  states_manager.keypressed(key, scancode, isrepeat)
end

return GameLoop
