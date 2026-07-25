-- Draws optional background layers at camera-relative speeds.
local ParallaxManager = {}
ParallaxManager.__index = ParallaxManager

function ParallaxManager.new(layers)
  return setmetatable({ layers = layers or {}, camera = nil, loaded = {} }, ParallaxManager)
end

function ParallaxManager:set_camera(camera)
  self.camera = camera
end

function ParallaxManager:update(_)
  -- Layers are static images for now; camera position is read during draw.
end

function ParallaxManager:load_layer(layer)
  if self.loaded[layer.id] then
    return self.loaded[layer.id]
  end
  if not love.filesystem.getInfo(layer.image_path) then
    print("Parallax layer missing, skipped: " .. tostring(layer.image_path))
    self.loaded[layer.id] = false
    return nil
  end
  local image = love.graphics.newImage(layer.image_path)
  image:setFilter("nearest", "nearest")
  self.loaded[layer.id] = image
  return image
end

function ParallaxManager:draw()
  if not self.camera then
    return
  end
  for _, layer in ipairs(self.layers) do
    local image = self:load_layer(layer)
    if image then
      local speed_x = layer.speed_x or 1
      local speed_y = layer.speed_y or 1
      local x = self.camera.x * (1 - speed_x)
      local y = self.camera.y * (1 - speed_y)
      local width = image:getWidth()
      local height = image:getHeight()
      local start_x = layer.repeat_x and x - (x % width) - width or x
      local end_x = layer.repeat_x and self.camera.x + self.camera.width + width or x
      local start_y = layer.repeat_y and y - (y % height) - height or y
      local end_y = layer.repeat_y and self.camera.y + self.camera.height + height or y
      local draw_x = start_x
      while draw_x <= end_x do
        local draw_y = start_y
        while draw_y <= end_y do
          love.graphics.draw(image, draw_x, draw_y)
          draw_y = draw_y + height
        end
        draw_x = draw_x + width
      end
    end
  end
end

return ParallaxManager
