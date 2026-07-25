-- Standard keyboard-selectable UI button.
local Theme = require("game.ui.theme")
local Button = {}
Button.__index = Button

function Button.new(data)
  data = data or {}
  local theme = Theme.get(data.theme)
  return setmetatable({ label = data.label or "Button", x = data.x or 0, y = data.y or 0, width = data.width or 220, height = data.height or 44, selected = false, on_confirm = data.on_confirm, theme = theme }, Button)
end

function Button:update(input)
  if self.selected and input.consume_pressed("ui_confirm") then
    if self.on_confirm then self.on_confirm() end
    return true
  end
  return false
end

function Button:draw()
  local colors = self.theme.colors
  love.graphics.setColor(self.selected and colors.selected or colors.panel)
  love.graphics.rectangle("fill", self.x, self.y, self.width, self.height)
  love.graphics.setColor(colors.panel_edge)
  love.graphics.rectangle("line", self.x, self.y, self.width, self.height)
  love.graphics.setColor(colors.text)
  love.graphics.printf(self.label, self.x, self.y + 12, self.width, "center")
end

return Button
