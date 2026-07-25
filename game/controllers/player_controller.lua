-- Converts keyboard state into player movement intent.
local PlayerController = {}
PlayerController.__index = PlayerController

function PlayerController.new()
  return setmetatable({ jump_requested = false }, PlayerController)
end

function PlayerController:keypressed(key)
  if key == "space" then
    self.jump_requested = true
  end
end

function PlayerController:get_intent()
  local horizontal = 0
  if love.keyboard.isDown("left") or love.keyboard.isDown("a") then
    horizontal = horizontal - 1
  end
  if love.keyboard.isDown("right") or love.keyboard.isDown("d") then
    horizontal = horizontal + 1
  end

  local intent = {
    horizontal = horizontal,
    jump = self.jump_requested
  }
  self.jump_requested = false
  return intent
end

return PlayerController
