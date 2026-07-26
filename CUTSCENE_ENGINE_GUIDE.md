# Cutscene Engine Guide

The cutscene engine is a self-contained Lua module that runs inside the normal
Love2D process. It does not create a second game loop.

## Preview

Validate first:

```cmd
python cutscene_engine/tools/validate_scene.py duck_slime_date
love . --cutscene duck_slime_date
```

Escape skips the scene and returns to the previous state. Completion also
returns to the playground.

## Scene Shape

Scenes live in `cutscene_engine/scenes/` and return a Lua table containing an
ID, background, camera, actors, and timeline:

```lua
return {
  id = "example",
  actors = {
    duck = { asset_id = "barbarian_duck_wizard", position = { x = 600, ground_y = 766, z = 0 } }
  },
  timeline = {
    { command = "move", actor = "duck", x = 760, ground_y = 766, duration = 2 },
    { command = "say", actor = "duck", text = "Hello.", duration = 2 }
  }
}
```

Actors are lightweight cutscene wrappers. They do not receive player input,
gameplay AI, collision reactions, or controllers.

## Commands

The current vocabulary is:

- `wait`: hold for a duration.
- `move`: move one actor from its current position to target `x` and
  `ground_y` over a duration.
- `face`: set an actor's facing direction.
- `play_animation`: play a named animation for a duration.
- `say`: show a timed dialogue card with speaker and text.
- `camera_move`: move the camera to a target position over a duration.
- `camera_follow`: follow an actor.
- `camera_shake`: shake with amplitude and duration.
- `play_effect`: trigger a registered effect.
- `fade`: fade to or from a color.
- `play_sound`: play a runtime sound ID.
- `play_music`: play a runtime music ID, with optional loop and volume.
- `stop_music`: stop music with an optional fade duration.

Commands are sequential and advance with `dt`. Keep them literal and explicit;
the scene file is the director's blueprint.

## Reused Systems

The engine reuses AssetLoader, AnimationManager, PositionManager, CameraManager,
Parallax, DrawOrder, Effect, DialogueBox, TimerManager, Theme, and AudioManager.
It does not reuse gameplay movement, player input, enemy AI, or gameplay bomb
logic.

## Iteration Rules

Use existing asset IDs and animation names from the runtime manifest. Keep
camera targets explicit, validate after every timeline change, and use short
durations while testing framing and dialogue timing.
