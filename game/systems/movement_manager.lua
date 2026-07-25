-- Applies simple horizontal movement to an entity.
local MovementManager = {}

function MovementManager.update(entity, intent, settings, dt)
  local movement = settings or {}
  local speed = movement.speed or 0
  entity.x = entity.x + (intent.horizontal or 0) * speed * dt
end

return MovementManager
