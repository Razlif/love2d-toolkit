-- Deterministic timers advanced only by the game's dt.
local TimerManager = {}
TimerManager.__index = TimerManager

function TimerManager.new()
  return setmetatable({ timers = {} }, TimerManager)
end

local function validate_id(id)
  assert(type(id) == "string" and id ~= "", "Timer id must be a non-empty string")
end

function TimerManager:after(id, duration)
  validate_id(id)
  assert(duration >= 0, "Timer duration cannot be negative")
  self.timers[id] = { remaining = duration, interval = duration, repeatable = false }
end

function TimerManager:every(id, interval)
  validate_id(id)
  assert(interval > 0, "Repeating timer interval must be greater than zero")
  self.timers[id] = { remaining = interval, interval = interval, repeatable = true }
end

function TimerManager:cancel(id)
  self.timers[id] = nil
end

function TimerManager:update(dt)
  assert(dt >= 0, "Timer dt cannot be negative")
  local fired = {}
  for id, timer in pairs(self.timers) do
    timer.remaining = timer.remaining - dt
    if timer.remaining <= 0 then
      fired[#fired + 1] = id
      if timer.repeatable then
        while timer.remaining <= 0 do
          timer.remaining = timer.remaining + timer.interval
        end
      else
        self.timers[id] = nil
      end
    end
  end
  table.sort(fired)
  return fired
end

function TimerManager:is_active(id)
  return self.timers[id] ~= nil
end

function TimerManager:clear()
  self.timers = {}
end

return TimerManager
