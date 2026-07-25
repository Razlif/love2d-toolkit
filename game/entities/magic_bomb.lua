-- Disposable playground example: a proximity bomb with a circular sensor.
local PositionManager = require("game.systems.position_manager")
local TimerManager = require("game.systems.timer_manager")

local MagicBomb = {}
MagicBomb.__index = MagicBomb

function MagicBomb.new(definition, position, owner_id)
  return setmetatable({
    id = "magic_bomb",
    definition = definition,
    position = PositionManager.new(position),
    owner_id = owner_id,
    draw_layer = definition.draw_layer or 25,
    draw_order_id = "magic_bomb",
    anchor_x = 0,
    anchor_y = 0,
    scale = 1,
    timer = TimerManager.new(),
    active = true
  }, MagicBomb)
end

function MagicBomb:update(dt)
  self.timer:update(dt)
end

function MagicBomb:detonate()
  self.active = false
end

function MagicBomb:is_active()
  return self.active
end

function MagicBomb:draw()
  if not self.active then
    return
  end
  local x = self.position.x
  local y = PositionManager.get_screen_y(self.position)
  love.graphics.setColor(0.45, 0.15, 1, 0.22)
  love.graphics.circle("fill", x, y, self.definition.radius + 8)
  love.graphics.setColor(0.75, 0.35, 1, 1)
  love.graphics.circle("fill", x, y, self.definition.visual_radius)
  love.graphics.setColor(1, 0.9, 1, 1)
  love.graphics.circle("fill", x - 3, y - 3, math.max(2, self.definition.visual_radius * 0.25))
end

return MagicBomb
