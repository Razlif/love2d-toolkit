-- Returns a stable draw order without mutating the scene's entity list.
local DrawOrder = {}

local function layer_of(drawable)
  return drawable.draw_layer or 20
end

function DrawOrder.sort(drawables)
  local decorated = {}
  for index, drawable in ipairs(drawables) do
    decorated[index] = { drawable = drawable, index = index }
  end

  table.sort(decorated, function(first, second)
    local a = first.drawable
    local b = second.drawable
    local a_y = a.position and a.position.ground_y or 0
    local b_y = b.position and b.position.ground_y or 0
    if layer_of(a) ~= layer_of(b) then
      return layer_of(a) < layer_of(b)
    end
    if a_y ~= b_y then
      return a_y < b_y
    end
    local a_id = a.draw_order_id or first.index
    local b_id = b.draw_order_id or second.index
    return tostring(a_id) < tostring(b_id)
  end)

  local result = {}
  for index, item in ipairs(decorated) do
    result[index] = item.drawable
  end
  return result
end

return DrawOrder
