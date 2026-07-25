-- Tracks the active game state and handles transitions between states.
local StatesManager = {
  current = nil,
  current_name = nil,
  overlay = nil,
  overlay_name = nil
}

local states = {
  playground = require("game.game_states.playground")
}

local overlays = {
  pause = require("game.game_states.pause")
}

function StatesManager.change(name, ...)
  local next_state = states[name]
  assert(next_state, "Unknown game state: " .. tostring(name))
  if StatesManager.current and StatesManager.current.exit then
    StatesManager.current.exit()
  end
  StatesManager.current = next_state
  StatesManager.current_name = name
  if next_state.enter then
    next_state.enter(...)
  end
end

function StatesManager.load(...)
  StatesManager.change("playground", ...)
end

function StatesManager.update(dt)
  if StatesManager.overlay then
    if StatesManager.overlay.update then StatesManager.overlay.update(dt) end
    return
  end
  if StatesManager.current and StatesManager.current.update then
    StatesManager.current.update(dt)
  end
end

function StatesManager.draw()
  if StatesManager.current and StatesManager.current.draw then
    StatesManager.current.draw()
  end
  if StatesManager.overlay and StatesManager.overlay.draw then
    StatesManager.overlay.draw()
  end
end

function StatesManager.push_overlay(name, ...)
  assert(not StatesManager.overlay, "An overlay is already active")
  local overlay = overlays[name]
  assert(overlay, "Unknown overlay: " .. tostring(name))
  StatesManager.overlay = overlay
  StatesManager.overlay_name = name
  if overlay.enter then overlay.enter(...) end
end

function StatesManager.pop_overlay(...)
  if not StatesManager.overlay then return end
  if StatesManager.overlay.exit then StatesManager.overlay.exit(...) end
  StatesManager.overlay = nil
  StatesManager.overlay_name = nil
end

function StatesManager.get_debug_context()
  if StatesManager.current and StatesManager.current.get_debug_context then
    return StatesManager.current.get_debug_context()
  end
  return nil
end

function StatesManager.keypressed(key, scancode, isrepeat)
  if StatesManager.current and StatesManager.current.keypressed then
    StatesManager.current.keypressed(key, scancode, isrepeat)
  end
end

return StatesManager
