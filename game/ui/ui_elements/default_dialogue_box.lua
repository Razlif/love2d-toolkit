-- Dialogue box with optional timed text reveal.
local Theme = require("game.ui.theme")
local DialogueBox = {}
DialogueBox.__index = DialogueBox

function DialogueBox.new(data)
  data = data or {}
  return setmetatable({ speaker = data.speaker or "", text = data.text or "", visible_characters = data.reveal_speed and 0 or #(data.text or ""), reveal_speed = data.reveal_speed or 0, elapsed = 0, x = data.x or 40, y = data.y or 400, width = data.width or 880, height = data.height or 100, theme = Theme.get(data.theme) }, DialogueBox)
end

function DialogueBox:update(dt)
  if self.visible_characters >= #self.text then return end
  self.elapsed = self.elapsed + dt * self.reveal_speed
  self.visible_characters = math.min(#self.text, math.floor(self.elapsed))
end

function DialogueBox:is_finished()
  return self.visible_characters >= #self.text
end

function DialogueBox:draw()
  love.graphics.setColor(self.theme.colors.panel)
  love.graphics.rectangle("fill", self.x, self.y, self.width, self.height)
  love.graphics.setColor(self.theme.colors.panel_edge)
  love.graphics.rectangle("line", self.x, self.y, self.width, self.height)
  love.graphics.setColor(self.theme.colors.text)
  love.graphics.print(self.speaker, self.x + 16, self.y + 12)
  love.graphics.printf(self.text:sub(1, self.visible_characters), self.x + 16, self.y + 38, self.width - 32, "left")
end

return DialogueBox
