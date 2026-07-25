-- Draws world-space debug geometry for any entity with the runtime entity contract.
local PositionManager = require("game.systems.position_manager")
local CollisionDetection = require("game.systems.collision_detection")

local DebugRenderer = {}

local function screen_position(entity)
  return entity.position.x, PositionManager.get_screen_y(entity.position)
end

function DebugRenderer.draw_mask(entity)
  local mask = entity.get_collision_mask and entity:get_collision_mask()
  if not mask then
    return
  end
  local x0, y0 = screen_position(entity)
  love.graphics.setColor(0.1, 0.9, 1, 0.24)
  for y = mask.opaque_bounds.top, mask.opaque_bounds.bottom do
    for x = mask.opaque_bounds.left, mask.opaque_bounds.right do
      if mask.pixels[y * mask.width + x + 1] then
        local render_facing = entity.get_render_facing and entity:get_render_facing() or entity.render_facing or entity.facing or 1
        local display_x = render_facing == 1 and x or mask.width - 1 - x
        love.graphics.rectangle(
          "fill",
          x0 + (display_x - entity.anchor_x) * entity.scale,
          y0 + (y - entity.anchor_y) * entity.scale,
          entity.scale,
          entity.scale
        )
      end
    end
  end
end

function DebugRenderer.draw_sensors(entity)
  local sensors = CollisionDetection.get_sensors(entity)
  for _, sensor in ipairs(sensors) do
    if sensor.shape == "circle" then
      love.graphics.setColor(1, 0.75, 0.15, 0.9)
      love.graphics.circle("line", sensor.x, sensor.y, sensor.radius)
    else
      love.graphics.setColor(sensor.generated and 1 or 0.95, sensor.generated and 0.55 or 0.2, 0.1, 0.9)
      love.graphics.rectangle("line", sensor.x, sensor.y, sensor.width, sensor.height)
    end
  end
end

function DebugRenderer.draw_position_label(entity)
  local x, y = screen_position(entity)
  local position = entity.position
  local label = string.format(
    "%s\nx=%.0f y=%.0f z=%.0f",
    entity.id or "entity",
    position.x,
    position.ground_y,
    position.z
  )
  love.graphics.setColor(1, 1, 0.75, 1)
  love.graphics.print(label, x - 42, y - (entity.anchor_y * entity.scale) - 34)
end

return DebugRenderer
