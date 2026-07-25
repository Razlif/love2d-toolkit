-- Reusable one-shot animated effect.
local AnimationManager = require("game.systems.animation_manager")

local Effect = {}
Effect.__index = Effect

function Effect.new(definition, loaded_asset)
  return setmetatable({
    definition = definition,
    asset = loaded_asset,
    x = definition.position.x,
    y = definition.position.y,
    scale = definition.scale or 1,
    anchor_x = definition.anchor.x,
    anchor_y = definition.anchor.y,
    animation_name = definition.animation,
    animation = AnimationManager.new(loaded_asset.animations),
    active = false
  }, Effect)
end

function Effect:trigger()
  self.animation:play(self.animation_name)
  self.active = true
end

function Effect:update(dt)
  if not self.active then
    return
  end
  self.animation:update(dt)
  if not self.animation:is_playing() then
    self.active = false
  end
end

function Effect:is_finished()
  return not self.active
end

function Effect:draw()
  if not self.active then
    return
  end
  love.graphics.setColor(1, 1, 1, 1)
  self.animation:draw(self.x, self.y, self.scale, self.anchor_x, self.anchor_y)
end

return Effect
