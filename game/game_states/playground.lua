-- Small runtime proving ground for promoted assets.
local asset_manifest = require("game_data.asset_manifest")
local duck_definition = require("game_data.characters.barbarian_duck_wizard")
local slime_definition = require("game_data.characters.funky_blue_slime")
local explosion_definition = require("game_data.effects.magic_explosion")
local bomb_definition = require("game_data.spells.magic_bomb")
local background_definition = asset_manifest.backgrounds.enchanted_wizard_training_meadow
local level_definition = require("game_data.levels.playground")
local AssetLoader = require("game.systems.asset_loader")
local Character = require("game.entities.characters.character")
local Effect = require("game.entities.effects.effect")
local MagicBomb = require("game.entities.magic_bomb")
local CollisionDetection = require("game.systems.collision_detection")
local DrawOrder = require("game.systems.draw_order")
local InputManager = require("game.systems.input_manager")
local CameraManager = require("game.systems.camera_manager")
local ParallaxManager = require("game.systems.parallax")
local AudioManager = require("game.systems.audio_manager")
local DebugOverlay = require("game.systems.debug_overlay")
local TimerManager = require("game.systems.timer_manager")

local function states_manager()
  return require("game.states_manager")
end

local Playground = {
  duck = nil,
  slime = nil,
  explosion = nil,
  bomb = nil,
  timer = nil,
  slime_health = 0,
  camera = nil,
  parallax = nil,
  last_collision_events = {},
  collision_debug = true
}

function Playground.enter()
  AssetLoader.load_manifest(asset_manifest)
  AudioManager.load_manifest(asset_manifest)
  Playground.duck = Character.new(duck_definition, AssetLoader.get_character(duck_definition.asset_id))
  Playground.slime = Character.new(slime_definition, AssetLoader.get_character(slime_definition.asset_id))
  Playground.explosion = Effect.new(explosion_definition, AssetLoader.get_effect(explosion_definition.asset_id))
  Playground.timer = TimerManager.new()
  Playground.slime_health = slime_definition.health or 3
  for _, character in ipairs({ Playground.duck, Playground.slime }) do
    local image_width = character.asset.image.width
    character.position.ground_y = level_definition.ground_y
    character.definition.movement.bounds = {
      left = level_definition.walkable_ground.left + character.anchor_x * character.scale,
      right = level_definition.walkable_ground.right - (image_width - character.anchor_x) * character.scale,
      top = level_definition.walkable_ground.top,
      bottom = level_definition.walkable_ground.bottom
    }
  end
  Playground.camera = CameraManager.new({
    width = 960,
    height = 540,
    bounds = {
      left = level_definition.world.left,
      top = level_definition.world.top,
      right = level_definition.world.right,
      bottom = level_definition.world.bottom
    },
    smoothing = 8
  })
  Playground.camera:follow(Playground.duck.position)
  Playground.parallax = ParallaxManager.new({
    {
      id = background_definition.id,
      image_path = background_definition.image.path,
      speed_x = 1,
      speed_y = 1,
      repeat_x = false,
      repeat_y = false,
      layer = 0
    }
  })
  Playground.parallax:set_camera(Playground.camera)
end

function Playground.update(dt)
  Playground.timer:update(dt)
  if InputManager.consume_pressed("ui_back") then
    states_manager().push_overlay("pause")
    return
  end
  if InputManager.consume_pressed("trigger_effect") and not Playground.timer:is_active("bomb_cooldown") and not Playground.bomb then
    local direction = Playground.duck.facing
    Playground.bomb = MagicBomb.new(
      bomb_definition,
      {
        x = Playground.duck.position.x - direction * bomb_definition.placement_distance,
        ground_y = Playground.duck.position.ground_y + bomb_definition.placement_y_offset,
        z = 0
      },
      Playground.duck.id
    )
    Playground.timer:after("bomb_cooldown", bomb_definition.cooldown)
  end

  local world = {
    player = Playground.duck,
    characters = { Playground.duck, Playground.slime }
  }
  Playground.duck:update(dt, world)
  Playground.slime:update(dt, world)
  if Playground.bomb then
    Playground.bomb:update(dt)
  end
  Playground.explosion:update(dt)
  Playground.camera:follow(Playground.duck.position)
  Playground.camera:update(dt)
  Playground.parallax:update(dt)

  local collision_entities = { Playground.duck }
  if Playground.bomb then collision_entities[#collision_entities + 1] = Playground.bomb end
  collision_entities[#collision_entities + 1] = Playground.slime
  collision_entities[#collision_entities + 1] = Playground.explosion
  Playground.last_collision_events = CollisionDetection.check(collision_entities, { debug = DebugOverlay.is_enabled() })
  for _, event in ipairs(Playground.last_collision_events) do
    if event.kind == "mask_overlap" and (
      (event.source_id == Playground.duck.id and event.target_id == Playground.slime.id) or
      (event.source_id == Playground.slime.id and event.target_id == Playground.duck.id)
    ) then
      Playground.duck:hit_flash(0.25)
      Playground.slime:hit_flash(0.25)
    end
    if event.kind == "sensor_overlap" and event.source_id == "magic_bomb" and event.target_id == Playground.slime.id and Playground.bomb then
      Playground.slime_health = math.max(0, Playground.slime_health - bomb_definition.damage)
      Playground.slime:hit_flash(0.45)
      Playground.explosion.position.x = Playground.bomb.position.x
      Playground.explosion.position.ground_y = Playground.bomb.position.ground_y
      Playground.bomb:detonate()
      Playground.bomb = nil
      Playground.explosion:trigger()
      Playground.camera:shake(10, 0.18)
      break
    end
  end
  DebugOverlay.report_collision_events(Playground.last_collision_events)
end

function Playground.get_debug_context()
  return {
    entities = { Playground.duck, Playground.slime, Playground.explosion, Playground.bomb },
    camera = Playground.camera,
    collision_events = Playground.last_collision_events
  }
end

function Playground.draw()
  love.graphics.clear(0.08, 0.1, 0.14, 1)
  Playground.camera:attach()
  Playground.parallax:draw()
  local drawables = DrawOrder.sort({
    Playground.duck,
    Playground.slime,
    Playground.explosion,
    Playground.bomb
  })
  for _, drawable in ipairs(drawables) do
    drawable:draw()
  end
  Playground.camera:detach()
  love.graphics.setColor(1, 1, 1, 1)
  love.graphics.print("Asset Lab -> Love2D playground", 24, 24)
  love.graphics.print("Arrows/WASD: move   Space: hop   E: plant bomb", 24, 48)
  love.graphics.print(string.format("Slime health: %d   Bomb: %s", Playground.slime_health, Playground.timer:is_active("bomb_cooldown") and "cooldown" or "ready"), 24, 72)
end

return Playground
