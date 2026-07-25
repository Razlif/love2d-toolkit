-- Reusable keyboard-navigated menu.
local Button = require("game.ui.ui_elements.default_button")
local Menu = {}
Menu.__index = Menu

function Menu.new(items, data)
  data = data or {}
  local menu = setmetatable({ buttons = {}, selected_index = 1 }, Menu)
  for index, item in ipairs(items or {}) do
    menu.buttons[index] = Button.new({ label = item.label, x = data.x or 360, y = (data.y or 220) + (index - 1) * (data.spacing or 56), width = data.width or 240, height = data.height or 44, theme = data.theme, on_confirm = item.on_confirm })
  end
  menu:refresh_selection()
  return menu
end

function Menu:refresh_selection()
  for index, button in ipairs(self.buttons) do button.selected = index == self.selected_index end
end

function Menu:update(input)
  if #self.buttons == 0 then return nil end
  if input.consume_pressed("ui_up") then
    self.selected_index = (self.selected_index - 2) % #self.buttons + 1
    self:refresh_selection()
  elseif input.consume_pressed("ui_down") then
    self.selected_index = self.selected_index % #self.buttons + 1
    self:refresh_selection()
  elseif self.buttons[self.selected_index]:update(input) then
    return self.selected_index
  end
  return nil
end

function Menu:draw()
  for _, button in ipairs(self.buttons) do button:draw() end
end

return Menu
