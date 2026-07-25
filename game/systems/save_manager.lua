-- Versioned JSON saves in Love2D's user-local save directory.
local Json = require("game.systems.json")

local SaveManager = {}
local SCHEMA_VERSION = 1
local SAVE_DIRECTORY = "save_slots"

local function validate_slot(slot)
  assert(type(slot) == "string" and slot:match("^[%w_-]+$"), "Invalid save slot name")
end

local function path_for(slot)
  validate_slot(slot)
  return SAVE_DIRECTORY .. "/" .. slot .. ".json"
end

function SaveManager.save(slot, data)
  local path = path_for(slot)
  local temporary = path .. ".tmp"
  local payload = {
    schema_version = SCHEMA_VERSION,
    saved_at = os.time(),
    data = data
  }
  love.filesystem.createDirectory(SAVE_DIRECTORY)
  local written, write_error = love.filesystem.write(temporary, Json.encode(payload))
  assert(written, (write_error or "Could not write save") .. " [" .. love.filesystem.getSaveDirectory() .. "]")
  if love.filesystem.getInfo(path) then
    assert(love.filesystem.remove(path), "Could not replace save")
  end
  assert(love.filesystem.rename(temporary, path), "Could not finalize save")
  return true
end

function SaveManager.load(slot)
  local path = path_for(slot)
  if not love.filesystem.getInfo(path) then
    return nil, "missing"
  end
  local contents = love.filesystem.read(path)
  local ok, payload = pcall(Json.decode, contents)
  if not ok or type(payload) ~= "table" then
    return nil, "invalid_save"
  end
  if payload.schema_version ~= SCHEMA_VERSION then
    return nil, "unsupported_schema"
  end
  return payload.data
end

function SaveManager.exists(slot)
  return love.filesystem.getInfo(path_for(slot), "file") ~= nil
end

function SaveManager.delete(slot)
  local path = path_for(slot)
  if love.filesystem.getInfo(path) then
    return love.filesystem.remove(path)
  end
  return false
end

function SaveManager.list_slots()
  local slots = {}
  for _, filename in ipairs(love.filesystem.getDirectoryItems(SAVE_DIRECTORY)) do
    local slot = filename:match("^([%w_-]+)%.json$")
    if slot then
      slots[#slots + 1] = slot
    end
  end
  table.sort(slots)
  return slots
end

return SaveManager
