-- Root Love2D entry point. Runtime code lives under game/.
local game = require("game.main")

function love.load(...)
  game.load(...)
end

function love.update(dt)
  game.update(dt)
end

function love.draw()
  game.draw()
end

function love.keypressed(key, scancode, isrepeat)
  game.keypressed(key, scancode, isrepeat)
end
