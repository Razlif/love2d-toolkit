-- Smooth 2D camera with bounds and deterministic screen shake.
local CameraManager = {}
CameraManager.__index = CameraManager

local function clamp(value, minimum, maximum)
  if maximum < minimum then
    return minimum
  end
  return math.max(minimum, math.min(maximum, value))
end

function CameraManager.new(config)
  config = config or {}
  local camera = setmetatable({
    width = config.width or 960,
    height = config.height or 540,
    x = 0,
    y = 0,
    target = nil,
    bounds = config.bounds,
    smoothing = config.smoothing or 8,
    shake_remaining = 0,
    shake_duration = 0,
    shake_amplitude = 0,
    shake_time = 0,
    shake_x = 0,
    shake_y = 0
  }, CameraManager)
  return camera
end

function CameraManager:follow(position)
  self.target = position
end

function CameraManager:set_bounds(bounds)
  self.bounds = bounds
end

function CameraManager:update(dt)
  if self.target then
    local desired_x = self.target.x - self.width / 2
    local desired_y = self.target.ground_y - self.height / 2
    local amount = math.min(1, dt * self.smoothing)
    self.x = self.x + (desired_x - self.x) * amount
    self.y = self.y + (desired_y - self.y) * amount
  end

  if self.bounds then
    self.x = clamp(self.x, self.bounds.left, self.bounds.right - self.width)
    self.y = clamp(self.y, self.bounds.top, self.bounds.bottom - self.height)
  end

  if self.shake_remaining > 0 then
    self.shake_remaining = math.max(0, self.shake_remaining - dt)
    self.shake_time = self.shake_time + dt
    local strength = self.shake_remaining / self.shake_duration
    self.shake_x = math.sin(self.shake_time * 71) * self.shake_amplitude * strength
    self.shake_y = math.cos(self.shake_time * 97) * self.shake_amplitude * strength
  else
    self.shake_x = 0
    self.shake_y = 0
  end
end

function CameraManager:shake(amplitude, duration)
  assert(amplitude >= 0 and duration > 0, "Camera shake requires a positive duration")
  self.shake_amplitude = amplitude
  self.shake_duration = duration
  self.shake_remaining = duration
  self.shake_time = 0
end

function CameraManager:attach()
  love.graphics.push()
  love.graphics.translate(-self.x + self.shake_x, -self.y + self.shake_y)
end

function CameraManager:detach()
  love.graphics.pop()
end

function CameraManager:world_to_screen(x, y)
  return x - self.x + self.shake_x, y - self.y + self.shake_y
end

function CameraManager:screen_to_world(x, y)
  return x + self.x - self.shake_x, y + self.y - self.shake_y
end

return CameraManager
