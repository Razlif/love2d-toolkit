-- Whole-game flow coordinator.
local states_manager = require("game.states_manager")
local InputManager = require("game.systems.input_manager")
local AudioManager = require("game.systems.audio_manager")
local DebugOverlay = require("game.systems.debug_overlay")

local GameLoop = {}

function GameLoop.load(debug_config, ...)
  DebugOverlay.configure(debug_config)
  states_manager.load({ cutscene_id = debug_config and debug_config.cutscene_id }, ...)
end

function GameLoop.update(dt)
  AudioManager.update(dt)
  DebugOverlay.update()
  states_manager.update(dt)
  DebugOverlay.report_input()
  DebugOverlay.report_state(states_manager.get_debug_context(), dt)
  InputManager.end_frame()
end

function GameLoop.draw()
  states_manager.draw()
  DebugOverlay.draw(states_manager.get_debug_context())
end

function GameLoop.keypressed(key, scancode, isrepeat)
  InputManager.keypressed(key, scancode, isrepeat)
end

function GameLoop.keyreleased(key, scancode)
  InputManager.keyreleased(key, scancode)
end

function GameLoop.mousepressed(x, y, button)
  InputManager.mousepressed(x, y, button)
end

function GameLoop.mousereleased(x, y, button)
  InputManager.mousereleased(x, y, button)
end

return GameLoop
