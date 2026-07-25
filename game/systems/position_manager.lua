-- Owns the literal 2.5D position model: x, ground_y, and height z.
local PositionManager = {}

function PositionManager.new(data)
  data = data or {}
  return {
    x = data.x or 0,
    ground_y = data.ground_y or data.y or 0,
    z = data.z or 0
  }
end

function PositionManager.move(position, dx, dground_y, dz)
  position.x = position.x + (dx or 0)
  position.ground_y = position.ground_y + (dground_y or 0)
  position.z = position.z + (dz or 0)
end

function PositionManager.get_screen_y(position)
  return position.ground_y - position.z
end

function PositionManager.get_ground_y(position)
  return position.ground_y
end

function PositionManager.set_ground_position(position, x, ground_y)
  position.x = x
  position.ground_y = ground_y
end

return PositionManager
