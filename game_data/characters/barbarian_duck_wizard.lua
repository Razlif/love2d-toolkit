-- Gameplay configuration for the promoted barbarian duck wizard.
return {
  asset_id = "barbarian_duck_wizard",
  controller = "player",
  position = { x = 700, ground_y = 700, z = 0 },
  scale = 2,
  anchor = { x = 32, y = 64 },
  facing = { enabled = true, default = "right", source = "left", flip_mode = "horizontal" },
  draw_layer = 20,
  movement = { speed = 120, vertical_speed = 60 },
  hop_animation = "jump",
  hop_on_press = false,
  collision = {
    enabled = true,
    auto_sensor = true,
    sensors = {}
  }
}
