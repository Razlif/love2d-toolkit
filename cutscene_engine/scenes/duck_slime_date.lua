-- Example of a timed, camera-led conversation with a comic interruption.
return {
  id = "duck_slime_date",

  background = {
    asset_id = "enchanted_wizard_training_meadow"
  },

  camera = {
    bounds = {
      left = 0,
      top = 0,
      right = 1672,
      bottom = 941
    },
    position = { x = 835, ground_y = 700 },
    zoom = 1
  },

  actors = {
    duck = {
      asset_id = "barbarian_duck_wizard",
      position = { x = 515, ground_y = 766, z = 0 },
      scale = 2,
      facing = "left",
      source_facing = -1
    },
    slime = {
      asset_id = "funky_blue_slime",
      position = { x = 1080, ground_y = 766, z = 0 },
      scale = 2,
      facing = "left",
      source_facing = -1
    }
  },

  timeline = {
    { command = "camera_zoom", zoom = 2, actor = "duck", duration = 1 },
    {
      command = "say",
      actor = "duck",
      text = "Man... I wish I could ask Slime out on a date.",
      style = "card",
      duration = 3.5
    },
    { command = "wait", duration = 1 },
    { command = "face", actor = "duck", direction = "right", duration = 0.3 },
    { command = "face", actor = "duck", direction = "left", duration = 0.3 },
    { command = "face", actor = "duck", direction = "right", duration = 0.3 },
    { command = "camera_follow", actor = "duck" },
    {
      command = "move",
      actor = "duck",
      x = 965,
      ground_y = 766,
      movement = "game",
      animation = "jump",
      loop = true
    },
    { command = "camera_move", x = 1050, ground_y = 766, duration = 0.8 },
    { command = "camera_zoom", zoom = 1.6, focus_x = 1050, focus_ground_y = 766, duration = 0.8 },
    { command = "say", actor = "duck", text = "Hi, Slime.", style = "card", duration = 1.5 },
    { command = "say", actor = "slime", text = "Hi, Duck.", style = "card", duration = 1.5 },
    { command = "say", actor = "duck", text = "Say, Slime... you want to go out with me?", style = "card", duration = 3 },
    { command = "camera_move", x = 1140, ground_y = 766, duration = 0.6 },
    {
      command = "move",
      actor = "slime",
      x = 1500,
      ground_y = 766,
      movement = "game",
      speed = 240,
      animation = "idle_bounce",
      loop = true
    },
    { command = "camera_shake", amplitude = 7, duration = 0.35 },
    { command = "camera_move", x = 835, ground_y = 766, duration = 0.8 },
    { command = "camera_zoom", zoom = 1, focus_x = 835, focus_ground_y = 766, duration = 0.8 },
    { command = "say", actor = "duck", text = "Why, God! Why!", style = "card", duration = 2.2 },
    { command = "fade", alpha = 1, duration = 1.5 },
    { command = "wait", duration = 1 }
  }
}
