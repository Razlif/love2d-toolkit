-- Root Love2D configuration entry point.
local config = require("game.conf")

function love.conf(t)
  config.configure(t)
end
