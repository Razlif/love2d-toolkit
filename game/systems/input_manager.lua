-- Centralizes keyboard and mouse state for controllers and game states.
local InputManager = {
  bindings = {
    move_left = { left = true, a = true },
    move_right = { right = true, d = true },
    move_up = { up = true, w = true },
    move_down = { down = true, s = true },
    jump = { space = true },
    trigger_effect = { e = true },
    ui_up = { up = true, w = true },
    ui_down = { down = true, s = true },
    ui_left = { left = true, a = true },
    ui_right = { right = true, d = true },
    ui_confirm = { ["return"] = true, space = true },
    ui_back = { escape = true },
    debug_toggle = { f3 = true },
    debug_masks = { f4 = true },
    debug_sensors = { f5 = true },
    debug_collisions = { f6 = true },
    debug_entities = { f7 = true },
    debug_camera = { f8 = true },
    debug_state = { f9 = true },
    debug_input = { f10 = true }
  },
  keys_down = {},
  pressed = {},
  mouse_buttons_down = {},
  mouse_pressed = {}
}

local function actions_for_key(key)
  local actions = {}
  for action, keys in pairs(InputManager.bindings) do
    if keys[key] then
      actions[#actions + 1] = action
    end
  end
  return actions
end

function InputManager.keypressed(key)
  InputManager.keys_down[key] = true
  for _, action in ipairs(actions_for_key(key)) do
    InputManager.pressed[action] = true
  end
end

function InputManager.keyreleased(key)
  InputManager.keys_down[key] = nil
end

function InputManager.mousepressed(x, y, button)
  InputManager.mouse_buttons_down[button] = { x = x, y = y }
  InputManager.mouse_pressed[button] = { x = x, y = y }
end

function InputManager.mousereleased(_, _, button)
  InputManager.mouse_buttons_down[button] = nil
end

function InputManager.is_down(action)
  for key in pairs(InputManager.bindings[action] or {}) do
    if InputManager.keys_down[key] then
      return true
    end
  end
  return false
end

function InputManager.consume_pressed(action)
  local was_pressed = InputManager.pressed[action] == true
  InputManager.pressed[action] = nil
  return was_pressed
end

function InputManager.is_mouse_down(button)
  return InputManager.mouse_buttons_down[button] ~= nil
end

function InputManager.debug_snapshot()
  local keys = {}
  for key in pairs(InputManager.keys_down) do
    keys[#keys + 1] = key
  end
  table.sort(keys)
  return {
    keys_down = keys,
    move_left = InputManager.is_down("move_left"),
    move_right = InputManager.is_down("move_right"),
    jump = InputManager.is_down("jump")
  }
end

function InputManager.consume_mouse_pressed(button)
  local event = InputManager.mouse_pressed[button]
  InputManager.mouse_pressed[button] = nil
  return event
end

function InputManager.end_frame()
  InputManager.pressed = {}
  InputManager.mouse_pressed = {}
end

return InputManager
