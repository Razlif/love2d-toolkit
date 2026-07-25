-- Small runtime proving ground for promoted assets.
local asset_manifest = require("game_data.asset_manifest")
local duck_definition = require("game_data.characters.barbarian_duck_wizard")
local slime_definition = require("game_data.characters.funky_blue_slime")
local explosion_definition = require("game_data.effects.magic_explosion")
local AssetLoader = require("game.systems.asset_loader")
local Character = require("game.entities.characters.character")
local Effect = require("game.entities.effects.effect")

local Playground = {
  duck = nil,
  slime = nil,
  explosion = nil
}

function Playground.enter()
  AssetLoader.load_manifest(asset_manifest)
  Playground.duck = Character.new(duck_definition, AssetLoader.get_character(duck_definition.asset_id))
  Playground.slime = Character.new(slime_definition, AssetLoader.get_character(slime_definition.asset_id))
  Playground.explosion = Effect.new(explosion_definition, AssetLoader.get_effect(explosion_definition.asset_id))
end

function Playground.update(dt)
  local world = {
    player = Playground.duck,
    characters = { Playground.duck, Playground.slime }
  }
  Playground.duck:update(dt, world)
  Playground.slime:update(dt, world)
  Playground.explosion:update(dt)
end

function Playground.draw()
  love.graphics.clear(0.08, 0.1, 0.14, 1)
  Playground.duck:draw()
  Playground.slime:draw()
  Playground.explosion:draw()
  love.graphics.setColor(1, 1, 1, 1)
  love.graphics.print("Asset Lab -> Love2D playground", 24, 24)
  love.graphics.print("Left/Right: move duck   Space: jump   E: explosion", 24, 48)
end

function Playground.keypressed(key)
  Playground.duck:keypressed(key)
  if key == "e" then
    Playground.explosion:trigger()
  end
end

return Playground
