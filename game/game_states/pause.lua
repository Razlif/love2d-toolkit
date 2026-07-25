-- Pauses the current state without recreating it.
local InputManager = require("game.systems.input_manager")
local Menu = require("game.ui.ui_elements.default_menu")
local Theme = require("game.ui.theme")

local function states_manager()
  return require("game.states_manager")
end

local Pause = { menu = nil }

function Pause.enter()
  Pause.menu = Menu.new({
    { label = "Resume", on_confirm = function() states_manager().pop_overlay() end }
  }, { x = 360, y = 250 })
end

function Pause.update()
  if InputManager.consume_pressed("ui_back") then
    states_manager().pop_overlay()
    return
  end
  Pause.menu:update(InputManager)
end

function Pause.draw()
  local theme = Theme.get()
  love.graphics.setColor(theme.colors.overlay)
  love.graphics.rectangle("fill", 0, 0, love.graphics.getWidth(), love.graphics.getHeight())
  love.graphics.setColor(theme.colors.text)
  love.graphics.printf("PAUSED", 0, 150, love.graphics.getWidth(), "center")
  Pause.menu:draw()
end

return Pause
