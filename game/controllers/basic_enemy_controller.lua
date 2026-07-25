-- Makes an enemy move toward the player on the horizontal axis.
local BasicEnemyController = {}
BasicEnemyController.__index = BasicEnemyController

function BasicEnemyController.new()
  return setmetatable({}, BasicEnemyController)
end

function BasicEnemyController:get_intent(character, world)
  local player = world and world.player
  if not player then
    return { horizontal = 0, vertical = 0, jump = false }
  end

  local horizontal_distance = player.position.x - character.position.x
  local vertical_distance = player.position.ground_y - character.position.ground_y
  return {
    horizontal = math.abs(horizontal_distance) < 4 and 0 or (horizontal_distance > 0 and 1 or -1),
    vertical = math.abs(vertical_distance) < 4 and 0 or (vertical_distance > 0 and 1 or -1),
    jump = false
  }
end

return BasicEnemyController
