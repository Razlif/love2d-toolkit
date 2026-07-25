local root = love.filesystem.getSource() .. "/../.."
package.path = root .. "/?.lua;" .. root .. "/?/init.lua;" .. package.path

local InputManager, TimerManager, PositionManager, DrawOrder, MaskCreation
local CollisionDetection, CameraManager, ParallaxManager, AudioManager
local Json, Menu
local DebugConfig

local function assert_equal(actual, expected, message)
  assert(actual == expected, string.format("%s: expected %s, got %s", message, tostring(expected), tostring(actual)))
end

local function run()
  InputManager = require("game.systems.input_manager")
  TimerManager = require("game.systems.timer_manager")
  PositionManager = require("game.systems.position_manager")
  DrawOrder = require("game.systems.draw_order")
  MaskCreation = require("game.systems.mask_creation")
  CollisionDetection = require("game.systems.collision_detection")
  CameraManager = require("game.systems.camera_manager")
  ParallaxManager = require("game.systems.parallax")
  AudioManager = require("game.systems.audio_manager")
  Json = require("game.systems.json")
  Menu = require("game.ui.ui_elements.default_menu")
  DebugConfig = require("game.debug_config")

  local debug_config = DebugConfig.from_args({ "--debug" })
  assert_equal(debug_config.enabled, true, "debug flag enabled")
  assert_equal(debug_config.masks, true, "debug masks enabled")
  local partial_config = DebugConfig.from_args({ "--debug-sensors" })
  assert_equal(partial_config.enabled, true, "partial debug enabled")
  assert_equal(partial_config.sensors, true, "partial sensor flag")
  assert_equal(partial_config.masks, false, "partial debug isolation")
  InputManager.keypressed("left")
  assert_equal(InputManager.is_down("move_left"), true, "held input")
  assert_equal(InputManager.consume_pressed("move_left"), true, "pressed input")
  InputManager.keyreleased("left")
  assert_equal(InputManager.is_down("move_left"), false, "released input")

  local timer = TimerManager.new()
  timer:after("once", 0.5)
  assert_equal(#timer:update(0.25), 0, "timer waits")
  assert_equal(#timer:update(0.25), 1, "timer fires")
  assert_equal(timer:is_active("once"), false, "one-shot timer clears")
  timer:every("repeat", 0.25)
  assert_equal(#timer:update(0.6), 1, "repeating timer fires")
  timer:cancel("repeat")

  local position = PositionManager.new({ x = 10, ground_y = 20, z = 4 })
  PositionManager.move(position, 5, 2, 3)
  assert_equal(position.x, 15, "position x")
  assert_equal(PositionManager.get_screen_y(position), 15, "screen y")

  local back = { position = { ground_y = 10 }, draw_layer = 20, draw_order_id = "back" }
  local front = { position = { ground_y = 20 }, draw_layer = 20, draw_order_id = "front" }
  assert_equal(DrawOrder.sort({ front, back })[1], back, "draw ordering")

  local image_data = love.image.newImageData(4, 4)
  image_data:setPixel(1, 1, 1, 1, 1, 1)
  local mask = MaskCreation.from_image(image_data)
  assert_equal(MaskCreation.get_pixel(mask, 1, 1), true, "mask opaque pixel")
  assert_equal(MaskCreation.get_pixel(mask, 0, 0), false, "mask transparent pixel")

  local function entity(id, x, enabled, sensors)
    return {
      id = id,
      position = { x = x, ground_y = 20, z = 0 },
      scale = 1,
      anchor_x = 0,
      anchor_y = 0,
      mask = mask,
      definition = { collision = { enabled = enabled, sensors = sensors or {} } }
    }
  end

  local first = entity("first", 0, true, {
    { id = "body", shape = "rectangle", offset_x = 0, offset_y = 0, width = 4, height = 4 }
  })
  local second = entity("second", 0, true)
  assert_equal(CollisionDetection.mask_overlaps(first, second), true, "mask overlap")
  local events = CollisionDetection.check({ first, second })
  assert_equal(#events, 2, "collision event count")
  assert_equal(events[1].source_id, "first", "collision source")
  assert_equal(events[2].sensor_id, "body", "sensor id")
  second.position.x = 20
  assert_equal(CollisionDetection.mask_overlaps(first, second), false, "mask non-overlap")
  second.position.x = 0
  second.definition.collision.enabled = false
  assert_equal(#CollisionDetection.check({ first, second }), 0, "disabled collision")

  second.definition.collision.enabled = true
  first.definition.collision.sensors = {}
  local auto_events = CollisionDetection.check({ first, second })
  assert_equal(auto_events[2].sensor_id, "auto_body", "automatic sensor")

  local camera = CameraManager.new({ width = 100, height = 50, responsive = false, bounds = { left = 0, top = 0, right = 500, bottom = 300 }, smoothing = 20 })
  local target = { x = 250, ground_y = 150 }
  camera:follow(target)
  camera:update(1)
  assert_equal(camera.x, 200, "camera follow")
  assert_equal(camera.y, 125, "camera vertical follow")
  camera:shake(4, 0.5)
  camera:update(0.25)
  assert(camera.shake_x ~= 0 or camera.shake_y ~= 0, "camera shake active")
  camera:update(0.25)
  assert_equal(camera.shake_x, 0, "camera shake expires")
  camera:set_zoom(2)
  camera:set_center(250, 150)
  local centered_x, centered_y = camera:world_to_screen(250, 150)
  assert_equal(centered_x, 50, "zoomed camera horizontal center")
  assert_equal(centered_y, 25, "zoomed camera vertical center")
  camera:set_zoom(1)
  camera:follow({
    get_camera_focus = function()
      return { x = 250, ground_y = 100 }
    end
  })
  camera:update(1)
  assert_equal(camera.x, 200, "camera follows visual focus x")
  assert_equal(camera.y, 75, "camera follows visual focus y")
  ParallaxManager.new({}):set_camera(camera)

  AudioManager.load_manifest({})
  local missing_audio_ok = pcall(function() AudioManager.play_music("missing") end)
  assert_equal(missing_audio_ok, false, "missing audio rejected")

  local decoded = Json.decode(Json.encode({ message = "hello", count = 2, enabled = true, values = { 1, 2 } }))
  assert_equal(decoded.message, "hello", "json string")
  assert_equal(decoded.values[2], 2, "json array")

  local confirmed = false
  local menu = Menu.new({ { label = "Test", on_confirm = function() confirmed = true end } })
  InputManager.keypressed("return")
  menu:update(InputManager)
  assert_equal(confirmed, true, "menu confirmation")
  InputManager.keyreleased("return")
end

local checks_passed = false

function love.load()
  love.filesystem.setIdentity("love2d_toolkit_test")
  love.filesystem.write("core_system_status.txt", "running")
  local ok, message = pcall(run)
  if not ok then
    love.filesystem.write("core_system_status.txt", "error: " .. tostring(message))
    print(message)
    os.exit(1)
  end
  love.filesystem.write("core_system_status.txt", "passed")
  checks_passed = true
end

function love.update()
  if checks_passed then
    love.event.quit(0)
  end
end
