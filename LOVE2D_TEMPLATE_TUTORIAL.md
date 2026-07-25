# Love2D Template Tutorial

This tutorial explains Love2D through this template's structure. It is not a
full Love2D manual. It teaches the parts needed to understand and extend this
toolkit.

## 1. The Love2D Loop

Love2D looks for specific function names:

- `love.load()` runs once when the game starts.
- `love.update(dt)` runs every frame before drawing.
- `love.draw()` runs every frame after update.
- `love.keypressed(key)` runs when a key is pressed.
- Mouse and gamepad callbacks work the same way.

In this template, these callbacks should stay small. They should pass work into
the game systems.

## 2. Main Entry Files

`main.lua`

The first file Love2D runs. It forwards callbacks into `game/main.lua`, keeping
the repository root available to both `game/` code and `media_assets/`.

Expected job:

- Load core systems.
- Initialize the state manager.
- Start the first state.
- Forward Love2D callbacks.

`conf.lua`

The root Love2D config entry point. It forwards configuration to
`game/conf.lua`.

Expected job:

- Set the window title.
- Set the window size.
- Configure Love2D version/settings.

`game/main.lua` and `game/game_loop.lua`

Runtime callback facade and shared update/draw flow.

Expected job:

- Provide a central place for frame-level flow if `main.lua` gets too busy.

`game/states_manager.lua`

Controls which game state is active.

Expected job:

- Switch states.
- Call active state `enter`, `update`, `draw`, and `exit`.
- Forward input to the active state.

## 3. Game States

Folder:

```txt
game/game_states/
```

A game state is one current screen or mode of the game.

Examples:

- Splash
- Main menu
- Playground
- Pause
- Settings
- Cutscene
- Dialogue
- World map
- Game over

Only one main state is usually active at a time.

A state usually has:

```lua
function State:enter(params)
end

function State:update(dt)
end

function State:draw()
end

function State:keypressed(key)
end

function State:exit()
end
```

These are not built into Love2D. They are this template's convention.

## 4. Systems

Folder:

```txt
game/systems/
```

Systems are reusable logic used by states and entities.

Important systems:

- `asset_loader.lua`: loads images, sounds, fonts, and data.
- `animation_manager.lua`: handles frame animation.
- `input_manager.lua`: tracks keyboard/mouse input.
- `position_manager.lua`: handles `x`, `y`, `z` position logic.
- `draw_order.lua`: sorts entities by ground/bottom Y.
- `collision_detection.lua`: detects mask/sensor overlaps.
- `mask_creation.lua`: builds masks and sensors from assets.
- `camera_manager.lua`: handles scrolling, following, and shake.
- `parallax.lua`: draws layered moving backgrounds.
- `audio_manager.lua`: plays sound/music.
- `timer_manager.lua`: handles waits, cooldowns, and timed events.
- `save_manager.lua`: saves and loads data.

## 5. Entities

Folder:

```txt
game/entities/
```

Entities are reusable object templates.

Groups:

- `characters/`: player, NPCs, enemies.
- `props/`: world objects.
- `backgrounds/`: background layers.
- `effects/`: visual effects.
- `projectiles/`: thrown/fired objects.
- `collectibles/`: pickups.
- `event_areas/`: invisible zones/triggers.

Entities usually contain behavior. Their editable values should come from
`game_data/`.

## 6. Game Data

Folder:

```txt
game_data/
```

Game data is structured Lua data. It should be readable and easy to edit.

Groups:

- `characters/`
- `props/`
- `backgrounds/`
- `effects/`
- `levels/`
- `scenes/`

Example idea:

```lua
return {
  id = "mock_duck",
  display_name = "Mock Duck",
  asset = {
    image = "media_assets/characters/duck/idle.png",
    animations = {
      idle = { frame_count = 4, fps = 6 }
    }
  },
  movement = {
    speed = 90
  }
}
```

For MVP, character data can include asset references directly. Split asset
registries later only if reuse becomes painful.

## 7. Media Assets

Folder:

```txt
media_assets/
```

This holds game-ready assets.

Groups:

- `characters/`
- `props/`
- `backgrounds/`
- `effects/`
- `audio/`
- `fonts/`
- `ui/`

The game should load from `media_assets/`, not directly from `asset_lab/`.

## 8. Asset Lab

Folder:

```txt
asset_lab/
```

Asset Lab is a self-contained workspace for generating and inspecting assets.

Flow:

1. Generate or add test assets inside `asset_lab/lab_assets/`.
2. Preview them in the browser UI.
3. Iterate with the agent.
4. When approved, manually promote assets into `media_assets/`.
5. Add or update matching `game_data/` records.

Asset Lab should not automatically modify the game without approval.

## 9. 2.5D Position Model

This template targets 2.5D games.

Use:

- `x`: horizontal ground position
- `y`: vertical ground position on screen/world
- `z`: height above ground

Drawing uses screen position:

```txt
draw_x = x
draw_y = y - z
```

Draw order should use ground/bottom Y, not image top-left Y.

That means an entity higher on the screen draws behind an entity lower on the
screen.

## 10. Collision Model

MVP collision is not physics-engine based.

Use:

- Masks
- Sensors
- Overlap detection
- Custom game responses

The collision system reports:

```txt
A overlaps B
```

Then the game decides what happens:

- Stop movement
- Trigger dialogue
- Take damage
- Bounce
- Collect item
- Start cutscene

This keeps the system flexible for 2.5D animation-heavy games.

## 11. Playground

Folder/file:

```txt
game/game_states/playground.lua
```

The playground is the first real test area.

It should eventually test:

- Loading duck/slime mock assets
- Movement
- Animation
- Draw order
- Z jumping
- Masks/sensors
- Simple collision reports
- Camera/parallax later

The playground is where systems prove they work before becoming part of the
template.

## 12. Future Cutscene Engine

Folder:

```txt
cutscene_engine/
```

This is empty for now.

Later it should control:

- Character movement
- Animation changes
- Dialogue
- Camera movement
- Timing
- Music/sound cues
- Scene blocking

The base game template comes first. The cutscene engine should reuse the same
entity, animation, position, audio, and camera systems where possible.
