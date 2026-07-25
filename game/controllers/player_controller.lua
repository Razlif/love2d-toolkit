-- Converts keyboard state into player movement intent.
local InputManager = require("game.systems.input_manager")
local PlayerController = {}
PlayerController.__index = PlayerController

function PlayerController.new()
  return setmetatable({}, PlayerController)
end

function PlayerController:get_intent()
  local horizontal = 0
  if InputManager.is_down("move_left") then
    horizontal = horizontal - 1
  end
  if InputManager.is_down("move_right") then
    horizontal = horizontal + 1
  end

  local vertical = 0
  if InputManager.is_down("move_up") then
    vertical = vertical - 1
  end
  if InputManager.is_down("move_down") then
    vertical = vertical + 1
  end

  local intent = {
    horizontal = horizontal,
    vertical = vertical,
    jump = InputManager.consume_pressed("jump")
  }
  return intent
end

return PlayerController
