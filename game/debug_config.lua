-- Parses launch-time debug flags into a small runtime configuration.
local DebugConfig = {}

local categories = { "masks", "sensors", "collisions", "entities", "camera", "input", "state" }

local function base_config()
  return {
    enabled = false,
    masks = false,
    sensors = false,
    collisions = false,
    entities = false,
    camera = false,
    input = false,
    state = false,
    cutscene_id = nil,
    qa = false,
    qa_run_dir = nil
  }
end

local function enable_all(config)
  config.enabled = true
  for _, category in ipairs(categories) do
    config[category] = true
  end
end

function DebugConfig.from_args(arguments)
  local config = base_config()
  local index = 1
  while index <= #(arguments or {}) do
    local argument = arguments[index]
    if argument == "--debug" then
      enable_all(config)
    elseif argument == "--debug-masks" then
      config.enabled = true
      config.masks = true
    elseif argument == "--debug-sensors" then
      config.enabled = true
      config.sensors = true
    elseif argument == "--debug-collisions" then
      config.enabled = true
      config.collisions = true
    elseif argument == "--debug-entities" then
      config.enabled = true
      config.entities = true
    elseif argument == "--debug-camera" then
      config.enabled = true
      config.camera = true
    elseif argument == "--debug-input" then
      config.enabled = true
      config.input = true
    elseif argument == "--debug-state" then
      config.enabled = true
      config.state = true
    elseif argument == "--qa" then
      config.qa = true
    elseif argument == "--qa-run-dir" then
      config.qa = true
      config.qa_run_dir = arguments[index + 1]
      index = index + 1
    end
    if argument == "--cutscene" then
      config.cutscene_id = arguments[index + 1]
      index = index + 1
    end
    index = index + 1
  end
  return config
end

return DebugConfig
