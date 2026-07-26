# Love2D Template Tutorial

This is a guided tour of the template, not a complete Love2D manual.

## The Loop

Love2D calls functions with specific names:

```lua
function love.load() end       -- once at startup
function love.update(dt) end   -- every frame; dt is seconds since the last frame
function love.draw() end       -- every frame, after update
function love.keypressed(key) end
```

Use `dt` for time-based movement: `x = x + speed * dt`. Love2D decides when
frames happen; the game uses elapsed seconds so behavior is stable across frame
rates.

## Template Flow

Root `main.lua` forwards Love callbacks to `game/main.lua`. The game loop passes
updates and drawing to `states_manager.lua`, which activates one game state such
as the title screen, playground, pause overlay, or cutscene.

State methods such as `enter`, `update`, and `draw` are template conventions,
not built-in Lua methods.

## Folders

- `game/systems/`: reusable services such as input, animation, camera, audio,
  timers, positions, draw order, masks, sensors, and saves.
- `game/entities/`: reusable character, effect, prop, and projectile objects.
- `game/controllers/`: player and AI intent producers.
- `game/game_states/`: screens and game flows.
- `game_data/`: readable Lua definitions and asset registries.
- `media_assets/`: runtime art and audio.

Controllers produce intent. Shared movement applies it. Entities own state and
rendering. States coordinate multiple entities.

## 2.5D Model

An entity has:

```lua
position = { x = 0, ground_y = 0, z = 0 }
```

`x` is horizontal, `ground_y` controls depth and draw order, and `z` is height
above the ground. Screen Y is `ground_y - z`. Masks and sensors report
overlaps; gameplay code decides what an overlap means.

## Asset Flow

Asset Lab is for creation and inspection. Runtime code loads only from
`media_assets/`, using entries in `game_data/asset_manifest.lua`. Promotion is
the deliberate bridge between them. See the Asset Lab and audio guides for the
full commands.

## Reusable Systems

- `InputManager`: named held and one-shot actions.
- `AnimationManager`: sprite-sheet frames and timing.
- `PositionManager`: 2.5D movement and screen coordinates.
- `DrawOrder`: stable depth sorting.
- `CameraManager` and `Parallax`: world scrolling and layered backgrounds.
- `AudioManager`: named music and sound effects.
- `TimerManager`: deterministic delays and repeats using `dt`.
- `MaskCreation` and `CollisionDetection`: cached masks, sensors, and reports.
- `SaveManager`: versioned user-local JSON saves.

## Cutscenes

`cutscene_engine/` is an independent module inside the normal Love2D runtime.
Scenes are declarative Lua timelines. They reuse asset, animation, position,
camera, audio, effect, and dialogue systems, but do not run gameplay AI or
controllers. See [CUTSCENE_ENGINE_GUIDE.md](CUTSCENE_ENGINE_GUIDE.md).

## API Reference

The repository includes a pinned Love2D 11.5 API index under
`dev_tools/love_docs/`. Query it before guessing about callbacks or function
signatures:

```cmd
python dev_tools/love_docs/love_docs.py lookup love.update
python dev_tools/love_docs/love_docs.py lookup love.graphics.newQuad
python dev_tools/love_docs/love_docs.py lookup love.graphics.captureScreenshot
```

It also covers `love.draw`, `love.graphics.newImage`, `love.filesystem`, and
input callbacks. The game does not load the reference at runtime.

## QA And Agent Inspection

The template includes two QA paths:

- Scripted runs use `qa/game_driver/drive_game.py` and produce isolated logs,
  snapshots, screenshots, and result bundles.
- Persistent sessions use `qa/run_game.py`. The optional localhost bridge lets
  an agent inspect the running game and submit normal keyboard or mouse actions.

The bridge is asynchronous and frame-oriented: submit a command, then read its
matching result and snapshot. It does not teleport entities or replace game
systems. See [TESTING_AND_DEBUGGING.md](TESTING_AND_DEBUGGING.md).
