# Love2D Toolkit

This is a reusable Love2D game-making template. It gives an agent a clear
workflow for creating assets, wiring them into a game, building cutscenes, and
testing the result.

The included duck, slime, background, bomb, music, and cutscene are examples.
They are meant to be replaced by the game maker.

## Install And Run

Requirements:

- Love2D 11.5 or newer
- Python 3.11 or newer
- `lovec` for command-line previews, when available

Run the example from the repository root:

```cmd
love .
```

The title screen offers:

- **Start**: play the example cutscene, then enter the playground.
- **Playground**: open the game systems demo directly.

Preview a cutscene directly:

```cmd
lovec . --cutscene duck_slime_date
```

## What The Toolkit Provides

### 1. A Love2D game foundation

The root `main.lua` and `conf.lua` start Love2D. Runtime code lives in
`game/`, with reusable systems, entities, controllers, and game states.

Ask the agent:

> Explain where a new player character, enemy, state, and level definition belong.

The agent should inspect the existing folders and extend the current patterns.

### 2. Asset Lab for images and animations

Asset Lab creates and inspects characters, props, backgrounds, effects, image
versions, sprite sheets, and GIF previews. Open `asset_lab/index.html` directly
in a browser.

Ask the agent:

> Create a brand-new character named crystal_knight with a transparent pixel-art image.

The agent reads the Asset Lab manifest, runs a dry run, calls the selected
provider, validates the result, and updates the manifest. See
[ASSET_LAB_GUIDE.md](ASSET_LAB_GUIDE.md).

### 3. Controlled asset promotion

Lab files are not runtime files. When an asset is ready, the agent promotes the
selected image and animation into `media_assets/`, updates game data, and
regenerates the runtime asset manifest.

Ask the agent:

> Promote version 1 and the walk animation of crystal_knight into the game.

The agent should read the manifest and use the promotion helper. It should not
guess paths or copy GIF previews into the game.

### 4. Audio search, preview, and attribution

The audio workflow searches Freesound and curated catalog entries, previews
candidates in Asset Lab, imports the selected file, and promotes it into the
runtime audio manifest. Creator, source, and license information are always
recorded, including for CC0 assets.

Ask the agent:

> Find three short CC0 magic-impact sounds, show them in Asset Lab, and import the one I choose.

API keys stay in `.env`. Candidate catalogs and local previews are local work
files and are not committed. See [AUDIO_WORKFLOW.md](AUDIO_WORKFLOW.md).

### 5. Reusable gameplay systems

The template includes:

- Named keyboard and mouse input.
- Character controllers and shared movement.
- Sprite-sheet animation.
- 2.5D `x`, `ground_y`, and `z` positions.
- Stable draw ordering.
- Camera following, bounds, shake, and parallax backgrounds.
- Timers, effects, UI menus, dialogue, audio, and saves.
- Cached masks, sensors, and collision overlap reports.

Collision systems report overlaps. They do not apply automatic physics or game
responses. Ask the agent to add the response in the relevant game state or
entity after the overlap has been verified.

### 6. Declarative cutscene engine

Cutscenes are Lua scene files made from literal timeline commands. They can
control actor movement, facing, animation, dialogue cards, camera movement,
effects, music, sound, and fades.

Ask the agent:

> Add a scene where the wizard walks to the shrine, speaks two lines, plays a sound, and fades out.

The agent should edit a scene file, validate it, and preview it with `lovec`.
See [CUTSCENE_ENGINE_GUIDE.md](CUTSCENE_ENGINE_GUIDE.md).

### 7. Debugging and QA

The playground is the integration test for the template. Debug overlays show
positions, camera state, input, entities, masks, sensors, and collision reports.

```cmd
love . --debug
love . --debug-input --debug-camera --debug-state
love . --debug-masks --debug-sensors --debug-collisions
```

Ask the agent:

> Run the tests and launch the playground with input, camera, and sensor debugging enabled.

See [TESTING_AND_DEBUGGING.md](TESTING_AND_DEBUGGING.md).

## The Normal Agent Workflow

For a new feature, work through this sequence:

1. Describe the result you want in plain language.
2. Ask the agent to inspect the relevant manifest, game data, and existing code.
3. Let the agent identify the smallest existing systems to reuse.
4. Ask for a dry run or plan before provider calls and large changes.
5. Let the agent implement the change in the appropriate folder.
6. Run the focused tests and preview the result in Love2D or Asset Lab.
7. Iterate using exact errors, positions, paths, and screenshots.

For example:

> Add a fire spirit enemy. First create and preview its image and idle animation
> in Asset Lab. Then promote it, add its game data, give it a basic enemy
> controller, and show it in the playground. Run the relevant tests.

The agent should keep Asset Lab, runtime assets, game data, and cutscene scene
files synchronized rather than editing generated paths by hand.

## Useful Commands

```cmd
python -m unittest qa.asset_checks.test_asset_lab qa.game_checks.test_cutscene_engine
python cutscene_engine/tools/validate_scene.py duck_slime_date
python asset_lab/helpers/validate_lab_assets.py
python asset_lab/helpers/export_browser_manifest.py
```

Run the Love2D QA harness from `qa/love_checks` with `lovec .`.

## Guides

- [LOVE2D_TEMPLATE_TUTORIAL.md](LOVE2D_TEMPLATE_TUTORIAL.md): understand the architecture.
- [ASSET_LAB_GUIDE.md](ASSET_LAB_GUIDE.md): create, inspect, and promote visual assets.
- [AUDIO_WORKFLOW.md](AUDIO_WORKFLOW.md): find, license, import, and promote audio.
- [CUTSCENE_ENGINE_GUIDE.md](CUTSCENE_ENGINE_GUIDE.md): author and preview scenes.
- [TESTING_AND_DEBUGGING.md](TESTING_AND_DEBUGGING.md): verify and diagnose the template.
- [AGENTS.md](AGENTS.md): operational rules for the coding agent.
