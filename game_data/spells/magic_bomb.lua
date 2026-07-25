-- Disposable playground example data; users can replace this demo spell.
return {
  id = "magic_bomb",
  radius = 48,
  visual_radius = 12,
  damage = 1,
  cooldown = 1,
  placement_distance = 90,
  placement_y_offset = -20,
  draw_layer = 25,
  collision = {
    enabled = true,
    auto_sensor = false,
    sensors = {
      {
        id = "blast_radius",
        shape = "circle",
        offset_x = 0,
        offset_y = 0,
        radius = 48
      }
    }
  }
}
