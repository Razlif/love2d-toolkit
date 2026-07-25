-- Gameplay configuration for the promoted funky blue slime.
return {
  asset_id = "funky_blue_slime",
  controller = "basic_enemy",
  position = { x = 900, ground_y = 700, z = 0 },
  scale = 2,
  anchor = { x = 32, y = 64 },
  facing = { enabled = true, default = "right", source = "left", flip_mode = "horizontal" },
  draw_layer = 20,
  default_animation = "idle_bounce",
  default_animation_loop = true,
  movement = { speed = 45, vertical_speed = 30 },
  health = 3,
  collision = { enabled = true, auto_sensor = true, sensors = {} }
}
