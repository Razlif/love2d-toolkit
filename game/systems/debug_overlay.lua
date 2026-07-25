-- Global debug layer shared by all game states.
local InputManager = require("game.systems.input_manager")
local DebugRenderer = require("game.systems.debug_renderer")

local DebugOverlay = {
  config = {
    enabled = false,
    masks = false,
    sensors = false,
    collisions = false,
    entities = false,
    camera = false,
    input = false,
    state = false,
    input_signature = "",
    state_elapsed = 0,
    last_collision_signature = ""
  }
}

local function set_all(value)
  DebugOverlay.config.enabled = value
  DebugOverlay.config.masks = value
  DebugOverlay.config.sensors = value
  DebugOverlay.config.collisions = value
  DebugOverlay.config.entities = value
  DebugOverlay.config.camera = value
  DebugOverlay.config.input = value
  DebugOverlay.config.state = value
end

function DebugOverlay.configure(config)
  config = config or {}
  DebugOverlay.config.enabled = config.enabled or false
  DebugOverlay.config.masks = config.masks or false
  DebugOverlay.config.sensors = config.sensors or false
  DebugOverlay.config.collisions = config.collisions or false
  DebugOverlay.config.entities = config.entities or false
  DebugOverlay.config.camera = config.camera or false
  DebugOverlay.config.input = config.input or false
  DebugOverlay.config.state = config.state or false
  DebugOverlay.config.input_signature = ""
  DebugOverlay.config.last_collision_signature = ""
  DebugOverlay.config.state_elapsed = 0
end

function DebugOverlay.is_enabled()
  return DebugOverlay.config.enabled
end

function DebugOverlay.report_collision_events(events)
  if not DebugOverlay.config.collisions then
    return
  end
  local parts = {}
  for _, event in ipairs(events or {}) do
    parts[#parts + 1] = string.format("%s:%s->%s", event.kind, event.source_id, event.target_id)
  end
  local signature = table.concat(parts, "|")
  if signature ~= DebugOverlay.config.last_collision_signature then
    DebugOverlay.config.last_collision_signature = signature
    if signature == "" then
      print("[debug] collisions cleared")
    else
      print("[debug] " .. signature)
    end
  end
end

local function format_keys(keys)
  return #keys == 0 and "none" or table.concat(keys, ",")
end

function DebugOverlay.report_input()
  if not DebugOverlay.config.input then
    return
  end
  local snapshot = InputManager.debug_snapshot()
  local signature = table.concat(snapshot.keys_down, ",")
  if signature == DebugOverlay.config.input_signature then
    return
  end
  DebugOverlay.config.input_signature = signature
  print(string.format(
    "[debug] input keys=%s left=%s right=%s jump=%s",
    format_keys(snapshot.keys_down),
    tostring(snapshot.move_left),
    tostring(snapshot.move_right),
    tostring(snapshot.jump)
  ))
end

function DebugOverlay.report_state(context, dt)
  if not DebugOverlay.config.state then
    return
  end
  DebugOverlay.config.state_elapsed = (DebugOverlay.config.state_elapsed or 0) + (dt or 0)
  if DebugOverlay.config.state_elapsed < 0.25 then
    return
  end
  DebugOverlay.config.state_elapsed = 0
  local parts = {}
  for _, entity in ipairs((context and context.entities) or {}) do
    local position = entity.position
    parts[#parts + 1] = string.format(
      "%s(x=%.1f,y=%.1f,z=%.1f)",
      entity.id or "entity", position.x, position.ground_y, position.z
    )
  end
  local camera = context and context.camera
  print(string.format(
    "[debug] state %s camera=(%.1f,%.1f) collisions=%d",
    table.concat(parts, " "),
    camera and camera.x or 0,
    camera and camera.y or 0,
    #(context and context.collision_events or {})
  ))
end

function DebugOverlay.update()
  if InputManager.consume_pressed("debug_toggle") then
    set_all(not DebugOverlay.config.enabled)
  end
  local toggles = {
    { action = "debug_masks", field = "masks" },
    { action = "debug_sensors", field = "sensors" },
    { action = "debug_collisions", field = "collisions" },
    { action = "debug_entities", field = "entities" },
    { action = "debug_camera", field = "camera" },
    { action = "debug_input", field = "input" },
    { action = "debug_state", field = "state" }
  }
  for _, toggle in ipairs(toggles) do
    if InputManager.consume_pressed(toggle.action) then
      DebugOverlay.config.enabled = true
      DebugOverlay.config[toggle.field] = not DebugOverlay.config[toggle.field]
    end
  end
end

local function draw_world(context)
  if not context or not context.camera then
    return
  end
  context.camera:attach()
  for _, entity in ipairs(context.entities or {}) do
    if DebugOverlay.config.entities then
      DebugRenderer.draw_position_label(entity)
    end
    if DebugOverlay.config.masks then
      DebugRenderer.draw_mask(entity)
    end
    if DebugOverlay.config.sensors then
      DebugRenderer.draw_sensors(entity)
    end
  end
  context.camera:detach()
end

function DebugOverlay.draw(context)
  if not DebugOverlay.config.enabled then
    return
  end
  draw_world(context)

  local lines = {}
  if DebugOverlay.config.collisions then
    for _, event in ipairs((context and context.collision_events) or {}) do
      lines[#lines + 1] = string.format("%s: %s -> %s", event.kind, event.source_id, event.target_id)
    end
  end
  if DebugOverlay.config.entities then
    for _, entity in ipairs((context and context.entities) or {}) do
      local position = entity.position
      local frame = entity.animation and entity.animation.current_frame or 1
      lines[#lines + 1] = string.format("%s x=%.1f ground_y=%.1f z=%.1f frame=%d", entity.id or "entity", position.x, position.ground_y, position.z, frame)
    end
  end
  if DebugOverlay.config.camera and context and context.camera then
    lines[#lines + 1] = string.format("camera x=%.1f y=%.1f", context.camera.x, context.camera.y)
  end
  love.graphics.setColor(1, 1, 1, 1)
  for index, line in ipairs(lines) do
    love.graphics.print(line, 16, 70 + (index - 1) * 18)
  end
end

return DebugOverlay
