-- Convert love-api's enriched Lua table into a deterministic JSON index.
local source_path = assert(arg[2], "missing love-api source directory")
local output_path = assert(arg[3], "missing output path")

package.path = source_path .. '/?.lua;' .. source_path .. '/?/?.lua;' .. source_path .. '/?/types/?.lua;' .. source_path .. '/?/enums/?.lua;' .. package.path
local api = assert(require('love_api'))
local enrich = assert(require('extra'))
api = enrich(api)

local function is_array(value)
  if type(value) ~= "table" then return false end
  local count = 0
  for key in pairs(value) do
    if type(key) ~= "number" or key < 1 or key % 1 ~= 0 then return false end
    count = math.max(count, key)
  end
  for index = 1, count do if value[index] == nil then return false end end
  return true
end

local function escape(value)
  return value:gsub('[%z\1-\31\\"]', function(character)
    local replacements = { ['\\'] = '\\\\', ['"'] = '\\"', ['\b'] = '\\b', ['\f'] = '\\f', ['\n'] = '\\n', ['\r'] = '\\r', ['\t'] = '\\t' }
    return replacements[character] or string.format('\\u%04x', string.byte(character))
  end)
end

local function encode(value)
  if value == nil then return 'null' end
  if value == true then return 'true' end
  if value == false then return 'false' end
  if type(value) == 'number' then return tostring(value) end
  if type(value) == 'string' then return '"' .. escape(value) .. '"' end
  assert(type(value) == 'table', 'unsupported value: ' .. type(value))
  local parts = {}
  if is_array(value) then
    for index = 1, #value do parts[#parts + 1] = encode(value[index]) end
    return '[' .. table.concat(parts, ',') .. ']'
  end
  local keys = {}
  for key in pairs(value) do assert(type(key) == 'string', 'object keys must be strings'); keys[#keys + 1] = key end
  table.sort(keys)
  for _, key in ipairs(keys) do parts[#parts + 1] = encode(key) .. ':' .. encode(value[key]) end
  return '{' .. table.concat(parts, ',') .. '}'
end

local function simple_value(value)
  local kind = type(value)
  if kind == 'string' or kind == 'number' or kind == 'boolean' then return value end
  return nil
end

local function copy_list(items)
  local result = {}
  for _, item in ipairs(items or {}) do
    local copy = { type = item.type, name = item.name, default = item.default, description = item.description }
    if item.arraytype then copy.arraytype = item.arraytype end
    if item.table then copy.table = copy_list(item.table) end
    result[#result + 1] = copy
  end
  return result
end

local function copy_entry(item)
  local result = {
    id = item.id, name = item.name, fullname = item.fullname, what = item.what,
    description = item.description, minidescription = item.minidescription,
    module = item.module and item.module.fullname or nil,
    type = item.type_ and item.type_.name or nil,
  }
  if item.variants then
    result.variants = {}
    for _, variant in ipairs(item.variants or {}) do
      result.variants[#result.variants + 1] = {
        description = variant.description,
        arguments = copy_list(variant.arguments),
        returns = copy_list(variant.returns),
      }
    end
  end
  if item.constants then
    result.constants = {}
    for _, constant in ipairs(item.constants) do
      result.constants[#result.constants + 1] = { name = constant.name, description = constant.description }
    end
  end
  return result
end

local entries = {}
for _, item in ipairs(api.everything or {}) do
  if item.what == 'module' or item.what == 'type' or item.what == 'enum' or item.what == 'function' or item.what == 'method' or item.what == 'callback' then
    entries[#entries + 1] = copy_entry(item)
  end
end
table.sort(entries, function(a, b) return (a.fullname or a.name) < (b.fullname or b.name) end)

local index = {}
for number, entry in ipairs(entries) do
  if entry.fullname then index[entry.fullname] = number - 1 end
end

local result = { love_version = api.version, entries = entries, by_fullname = index, source_format = 'love-api enriched Lua table' }
local output = assert(io.open(output_path, 'wb'))
output:write(encode(result))
output:close()
love.event.quit()
