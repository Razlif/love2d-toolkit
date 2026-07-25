-- Disposable example scene using the existing promoted assets and background.
return {
  id = "duck_slime_intro",
  background = { asset_id = "enchanted_wizard_training_meadow" },
  camera = {
    bounds = { left = 0, top = 0, right = 1672, bottom = 941 },
    position = { x = 820, ground_y = 700 }
  },
  actors = {
    duck = {
      asset_id = "barbarian_duck_wizard",
      position = { x = 620, ground_y = 700, z = 0 },
      scale = 2,
      facing = "right",
      source_facing = -1
    },
    slime = {
      asset_id = "funky_blue_slime",
      position = { x = 1000, ground_y = 700, z = 0 },
      scale = 2,
      facing = "left",
      source_facing = -1
    }
  },
  timeline = {
    { command = "move", actor = "duck", x = 760, ground_y = 700, duration = 2 },
    { command = "say", actor = "duck", text = "What are you doing here?", duration = 2.5 },
    { command = "move", actor = "slime", x = 900, ground_y = 700, duration = 1.5 },
    { command = "say", actor = "slime", text = "Boing.", duration = 1.5 },
    { command = "play_animation", actor = "duck", name = "jump", duration = 0.625 },
    { command = "camera_shake", amplitude = 5, duration = 0.15 }
  }
}
