-- Makes an enemy move toward the player on the horizontal axis.
local BasicEnemyController = {}
BasicEnemyController.__index = BasicEnemyController

function BasicEnemyController.new()
  return setmetatable({}, BasicEnemyController)
end

function BasicEnemyController:get_intent(character, world)
  local player = world and world.player
  if not player or math.abs(player.x - character.x) < 4 then
    return { horizontal = 0, jump = false }
  end

  return {
    horizontal = player.x > character.x and 1 or -1,
    jump = false
  }
end

return BasicEnemyController
