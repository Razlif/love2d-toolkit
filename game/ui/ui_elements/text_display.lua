-- Draws positioned and wrapped text using the active UI theme.
local Theme = require("game.ui.theme")
local TextDisplay = {}
TextDisplay.__index = TextDisplay

function TextDisplay.new(data)
  data = data or {}
  local theme = Theme.get(data.theme)
  return setmetatable({ text = data.text or "", x = data.x or 0, y = data.y or 0, width = data.width, font = data.font or love.graphics.newFont(theme.font_size), color = data.color or theme.colors.text, align = data.align or "left" }, TextDisplay)
end

function TextDisplay:draw()
  love.graphics.setFont(self.font)
  love.graphics.setColor(self.color)
  if self.width then
    love.graphics.printf(self.text, self.x, self.y, self.width, self.align)
  else
    love.graphics.print(self.text, self.x, self.y)
  end
end

return TextDisplay
