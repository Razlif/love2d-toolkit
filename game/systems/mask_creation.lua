-- Builds cached alpha masks for static images and sprite-sheet frames.
local MaskCreation = {}

local function build_mask(image_data, x_offset, y_offset, width, height)
  local pixels = {}
  local opaque_pixels = {}
  local bounds = { left = width, top = height, right = -1, bottom = -1 }
  for y = 0, height - 1 do
    for x = 0, width - 1 do
      local _, _, _, alpha = image_data:getPixel(x_offset + x, y_offset + y)
      local opaque = alpha > 0
      pixels[y * width + x + 1] = opaque
      if opaque then
        opaque_pixels[#opaque_pixels + 1] = { x = x, y = y }
        bounds.left = math.min(bounds.left, x)
        bounds.top = math.min(bounds.top, y)
        bounds.right = math.max(bounds.right, x)
        bounds.bottom = math.max(bounds.bottom, y)
      end
    end
  end
  return {
    width = width,
    height = height,
    pixels = pixels,
    opaque_pixels = opaque_pixels,
    opaque_bounds = bounds
  }
end

function MaskCreation.from_image(image, image_data)
  image_data = image_data or image
  assert(image_data.getPixel, "MaskCreation.from_image requires readable ImageData")
  return build_mask(image_data, 0, 0, image_data:getWidth(), image_data:getHeight())
end

function MaskCreation.from_animation(animation)
  local image_data = animation.image_data
  assert(image_data, "Animation is missing readable ImageData for mask creation")
  local masks = {}
  for frame = 1, animation.frame_count do
    masks[frame] = build_mask(
      image_data,
      (frame - 1) * animation.frame_width,
      0,
      animation.frame_width,
      animation.frame_height
    )
  end
  return masks
end

function MaskCreation.get_pixel(mask, x, y)
  if x < 0 or y < 0 or x >= mask.width or y >= mask.height then
    return false
  end
  return mask.pixels[y * mask.width + x + 1] == true
end

function MaskCreation.sensor_from_mask(mask, anchor_x, anchor_y)
  if not mask or mask.opaque_bounds.right < 0 then
    return nil
  end
  local bounds = mask.opaque_bounds
  return {
    id = "auto_body",
    shape = "rectangle",
    offset_x = bounds.left - anchor_x,
    offset_y = bounds.top - anchor_y,
    width = bounds.right - bounds.left + 1,
    height = bounds.bottom - bounds.top + 1,
    generated = true
  }
end

return MaskCreation
