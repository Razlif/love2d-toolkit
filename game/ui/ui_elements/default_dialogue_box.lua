-- Dialogue box with optional timed text reveal.
local Theme = require("game.ui.theme")
local DialogueBox = {}
DialogueBox.__index = DialogueBox

function DialogueBox.new(data)
  data = data or {}
  return setmetatable({
    speaker = data.speaker or "",
    text = data.text or "",
    actor = data.actor,
    style = data.style or "footer",
    visible_characters = data.reveal_speed and 0 or #(data.text or ""),
    reveal_speed = data.reveal_speed or 0,
    elapsed = 0,
    x = data.x or 40,
    y = data.y or 400,
    width = data.width or 880,
    height = data.height or 100,
    theme = Theme.get(data.theme)
  }, DialogueBox)
end

function DialogueBox:update(dt)
  if self.visible_characters >= #self.text then return end
  self.elapsed = self.elapsed + dt * self.reveal_speed
  self.visible_characters = math.min(#self.text, math.floor(self.elapsed))
end

function DialogueBox:is_finished()
  return self.visible_characters >= #self.text
end

function DialogueBox:draw_footer()
  love.graphics.setColor(self.theme.colors.panel)
  love.graphics.rectangle("fill", self.x, self.y, self.width, self.height)
  love.graphics.setColor(self.theme.colors.panel_edge)
  love.graphics.rectangle("line", self.x, self.y, self.width, self.height)
  love.graphics.setColor(self.theme.colors.text)
  love.graphics.print(self.speaker, self.x + 16, self.y + 12)
  love.graphics.printf(self.text:sub(1, self.visible_characters), self.x + 16, self.y + 38, self.width - 32, "left")
end

function DialogueBox:draw_card(camera)
  local screen_width = love.graphics.getWidth()
  local screen_height = love.graphics.getHeight()
  local card_width = math.min(320, screen_width - 32)
  local card_height = 92
  local actor_x, actor_top, actor_bottom
  if self.actor and camera then
    actor_x, actor_top = camera:world_to_screen(
      self.actor.position.x,
      self.actor.position.ground_y - self.actor.anchor_y * self.actor.scale
    )
    actor_bottom = select(2, camera:world_to_screen(self.actor.position.x, self.actor.position.ground_y))
  else
    actor_x = screen_width / 2
    actor_top = screen_height / 2
    actor_bottom = screen_height / 2
  end

  local x = math.max(16, math.min(screen_width - card_width - 16, actor_x - card_width / 2))
  local y = actor_top - card_height - 18
  if y < 16 then y = actor_bottom + 18 end
  y = math.max(16, math.min(screen_height - card_height - 16, y))

  love.graphics.setColor(self.theme.colors.card_panel)
  love.graphics.rectangle("fill", x, y, card_width, card_height, 8, 8)
  love.graphics.setColor(self.theme.colors.card_edge)
  love.graphics.rectangle("line", x, y, card_width, card_height, 8, 8)
  love.graphics.setColor(self.theme.colors.card_speaker)
  love.graphics.print(self.speaker, x + 12, y + 10)
  love.graphics.setColor(self.theme.colors.card_text)
  love.graphics.printf(self.text:sub(1, self.visible_characters), x + 12, y + 34, card_width - 24, "left")
end

function DialogueBox:draw(camera)
  if self.style == "card" then
    self:draw_card(camera)
  else
    self:draw_footer()
  end
end

return DialogueBox
