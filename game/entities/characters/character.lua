-- Shared runtime character behavior.
local AnimationManager = require("game.systems.animation_manager")
local ControllerFactory = require("game.controllers.controller_factory")
local MovementManager = require("game.systems.movement_manager")

local Character = {}
Character.__index = Character

function Character.new(definition, loaded_asset)
  local character = setmetatable({
    definition = definition,
    asset = loaded_asset,
    controller = ControllerFactory.create(definition.controller),
    x = definition.position.x,
    y = definition.position.y,
    scale = definition.scale or 1,
    anchor_x = definition.anchor.x,
    anchor_y = definition.anchor.y,
    default_animation = definition.default_animation,
    animation = AnimationManager.new(loaded_asset.animations)
  }, Character)

  if character.default_animation then
    character.animation:play(character.default_animation)
  end
  return character
end

function Character:keypressed(key)
  if self.controller and self.controller.keypressed then
    self.controller:keypressed(key)
  end
end

function Character:play(name)
  self.animation:play(name)
end

function Character:update(dt, world)
  local intent = { horizontal = 0, jump = false }
  if self.controller then
    intent = self.controller:get_intent(self, world, dt)
  end

  MovementManager.update(self, intent, self.definition.movement, dt)
  if intent.jump and self.asset.animations.jump then
    self.animation:play("jump")
  end
  self.animation:update(dt)

  if self.default_animation and not self.animation:is_playing() then
    self.animation:play(self.default_animation)
  end
end

function Character:draw()
  love.graphics.setColor(1, 1, 1, 1)
  if self.animation:is_playing() then
    self.animation:draw(self.x, self.y, self.scale, self.anchor_x, self.anchor_y)
    return
  end
  love.graphics.draw(self.asset.image.texture, self.x, self.y, 0, self.scale, self.scale, self.anchor_x, self.anchor_y)
end

return Character
