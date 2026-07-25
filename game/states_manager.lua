-- Tracks the active game state and handles transitions between states.
local StatesManager = {
  current = nil,
  current_name = nil
}

local states = {
  playground = require("game.game_states.playground")
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
  if StatesManager.current and StatesManager.current.update then
    StatesManager.current.update(dt)
  end
end

function StatesManager.draw()
  if StatesManager.current and StatesManager.current.draw then
    StatesManager.current.draw()
  end
end

function StatesManager.keypressed(key, scancode, isrepeat)
  if StatesManager.current and StatesManager.current.keypressed then
    StatesManager.current.keypressed(key, scancode, isrepeat)
  end
end

return StatesManager
