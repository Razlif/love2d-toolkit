-- Small dependency-free JSON encoder/decoder for save files.
local Json = {}

local function is_array(value)
  if type(value) ~= "table" then
    return false
  end
  local count = 0
  for key in pairs(value) do
    if type(key) ~= "number" or key < 1 or key % 1 ~= 0 then
      return false
    end
    count = math.max(count, key)
  end
  for index = 1, count do
    if value[index] == nil then
      return false
    end
  end
  return true
end

local function escape_string(value)
  return value:gsub("[\\\"\n\r\t]", {
    ["\\"] = "\\\\",
    ["\""] = "\\\"",
    ["\n"] = "\\n",
    ["\r"] = "\\r",
    ["\t"] = "\\t"
  })
end

local function encode(value)
  if value == nil then
    return "null"
  elseif value == true then
    return "true"
  elseif value == false then
    return "false"
  elseif type(value) == "number" then
    assert(value == value and value ~= math.huge and value ~= -math.huge, "Cannot encode invalid number")
    return tostring(value)
  elseif type(value) == "string" then
    return '"' .. escape_string(value) .. '"'
  elseif type(value) == "table" then
    local parts = {}
    if is_array(value) then
      for index = 1, #value do
        parts[#parts + 1] = encode(value[index])
      end
      return "[" .. table.concat(parts, ",") .. "]"
    end
    for key, item in pairs(value) do
      assert(type(key) == "string", "JSON object keys must be strings")
      parts[#parts + 1] = encode(key) .. ":" .. encode(item)
    end
    table.sort(parts)
    return "{" .. table.concat(parts, ",") .. "}"
  end
  error("Cannot encode value of type " .. type(value))
end

function Json.encode(value)
  return encode(value)
end

local function decoder(text)
  local index = 1

  local function skip_space()
    while text:sub(index, index):match("%s") do
      index = index + 1
    end
  end

  local function parse_string()
    assert(text:sub(index, index) == '"', "Expected JSON string")
    index = index + 1
    local parts = {}
    while index <= #text do
      local character = text:sub(index, index)
      index = index + 1
      if character == '"' then
        return table.concat(parts)
      elseif character == "\\" then
        local escaped = text:sub(index, index)
        index = index + 1
        local replacements = { ['"'] = '"', ["\\"] = "\\", ["/"] = "/", b = "\b", f = "\f", n = "\n", r = "\r", t = "\t" }
        parts[#parts + 1] = replacements[escaped] or escaped
      else
        parts[#parts + 1] = character
      end
    end
    error("Unterminated JSON string")
  end

  local parse_value
  local function parse_array()
    index = index + 1
    local result = {}
    skip_space()
    if text:sub(index, index) == "]" then
      index = index + 1
      return result
    end
    while true do
      result[#result + 1] = parse_value()
      skip_space()
      local delimiter = text:sub(index, index)
      index = index + 1
      if delimiter == "]" then
        return result
      end
      assert(delimiter == ",", "Expected JSON array delimiter")
      skip_space()
    end
  end

  local function parse_object()
    index = index + 1
    local result = {}
    skip_space()
    if text:sub(index, index) == "}" then
      index = index + 1
      return result
    end
    while true do
      skip_space()
      local key = parse_string()
      skip_space()
      assert(text:sub(index, index) == ":", "Expected JSON object separator")
      index = index + 1
      result[key] = parse_value()
      skip_space()
      local delimiter = text:sub(index, index)
      index = index + 1
      if delimiter == "}" then
        return result
      end
      assert(delimiter == ",", "Expected JSON object delimiter")
    end
  end

  function parse_value()
    skip_space()
    local start = index
    local character = text:sub(index, index)
    if character == '"' then
      return parse_string()
    elseif character == "{" then
      return parse_object()
    elseif character == "[" then
      return parse_array()
    end
    if text:sub(index, index + 3) == "true" then
      index = index + 4
      return true
    elseif text:sub(index, index + 4) == "false" then
      index = index + 5
      return false
    elseif text:sub(index, index + 3) == "null" then
      index = index + 4
      return nil
    end
    local number = text:match("^-?%d+%.?%d*[eE]?[+-]?%d*", index)
    assert(number and number ~= "", "Invalid JSON value at " .. start)
    index = index + #number
    return tonumber(number)
  end

  local result = parse_value()
  skip_space()
  assert(index > #text, "Unexpected JSON content at " .. index)
  return result
end

function Json.decode(text)
  assert(type(text) == "string", "JSON text must be a string")
  return decoder(text)
end

return Json
