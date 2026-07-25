-- Reusable one-shot animated effect.
local AnimationManager = require("game.systems.animation_manager")
local PositionManager = require("game.systems.position_manager")
local TimerManager = require("game.systems.timer_manager")

local Effect = {}
Effect.__index = Effect

function Effect.new(definition, loaded_asset)
  return setmetatable({
    id = definition.asset_id,
    definition = definition,
    asset = loaded_asset,
    position = PositionManager.new(definition.position),
    scale = definition.scale or 1,
    anchor_x = definition.anchor.x,
    anchor_y = definition.anchor.y,
    draw_layer = definition.draw_layer or 30,
    draw_order_id = definition.draw_order_id or definition.asset_id,
    animation_name = definition.animation,
    animation = AnimationManager.new(loaded_asset.animations),
    timer = TimerManager.new(),
    active = false,
    elapsed = 0
  }, Effect)
end

function Effect:trigger()
  self.animation:play(self.animation_name)
  self.active = true
  self.elapsed = 0
end

function Effect:update(dt)
  self.timer:update(dt)
  if not self.active then
    return
  end
  self.elapsed = self.elapsed + dt
  self.animation:update(dt)
  if not self.animation:is_playing() then
    self.active = false
  end
end

function Effect:get_collision_mask()
  if not self.active then
    return nil
  end
  return self.animation:get_current_mask()
end

function Effect:is_finished()
  return not self.active
end

function Effect:draw()
  if not self.active then
    return
  end
  local alpha = 1
  local flicker = self.definition.flicker
  if flicker then
    local frequency = flicker.frequency or 12
    local minimum_alpha = flicker.minimum_alpha or 0.35
    local wave = (math.sin(self.elapsed * frequency * math.pi * 2) + 1) / 2
    alpha = minimum_alpha + (1 - minimum_alpha) * wave
  end
  love.graphics.setColor(1, 1, 1, alpha)
  self.animation:draw(self.position.x, PositionManager.get_screen_y(self.position), self.scale, self.scale, self.anchor_x, self.anchor_y)
end

return Effect
