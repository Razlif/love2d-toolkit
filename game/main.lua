-- Runtime callback facade. The root main.lua forwards Love callbacks here.
local game_loop = require("game.game_loop")

local Main = {}

function Main.load(...)
  game_loop.load(...)
end

function Main.update(dt)
  game_loop.update(dt)
end

function Main.draw()
  game_loop.draw()
end

function Main.keypressed(key, scancode, isrepeat)
  game_loop.keypressed(key, scancode, isrepeat)
end

return Main
