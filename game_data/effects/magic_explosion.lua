-- Gameplay configuration for the promoted magic explosion.
return {
  asset_id = "magic_explosion",
  position = { x = 700, ground_y = 300, z = 0 },
  scale = 4,
  anchor = { x = 32, y = 32 },
  draw_layer = 30,
  flicker = { frequency = 18, minimum_alpha = 0.3 },
  collision = { enabled = false, auto_sensor = true, sensors = {} },
  animation = "burst"
}
