# Love2D Toolkit

A small Love2D game template with:

- A reusable 2.5D game foundation.
- Asset Lab for images, animations, and audio.
- A declarative cutscene engine.
- Debugging and QA helpers.

The included duck, slime, background, bomb, music, and cutscene are examples.

## Boot

Clone the repository:

```cmd
git clone https://github.com/Razlif/love2d-toolkit.git
cd love2d-toolkit
```

Run the example:

```cmd
love .
```

Run a cutscene directly:

```cmd
lovec . --cutscene duck_slime_date
```

## Start With The Agent

Ask the agent:

> Read the repository, read the root documentation, inspect the Graphify graph,
> and explain how this toolkit is organized.

Graphify is local context for the agent. It is not a game asset or deliverable.

## Asset Lab

Open `asset_lab/index.html` in a browser.

![Asset Lab preview](asset_lab/asset_lab_screenshot.png)

The viewer shows characters, props, backgrounds, effects, image versions,
sprite sheets, and GIF animation previews. After refresh, it opens the last
created asset so the agent and user can inspect the newest result quickly.
The Audio Library button shows searchable candidates with play controls,
source, creator, license, and attribution information.

Ask the agent to:

> Read `asset_lab/manifest.json`, validate Asset Lab, and explain the available assets.

Useful commands:

```cmd
python asset_lab/helpers/validate_lab_assets.py
python asset_lab/helpers/export_browser_manifest.py
python asset_lab/helpers/sync_manifest.py --report
python asset_lab/helpers/create_lab_asset.py create-new --provider self --type effect --name magic_poof --prompt "small magic poof"
python asset_lab/helpers/create_lab_asset.py add-image-version --provider self --type character --name crystal_knight --mode with_reference --source-image-version 1 --prompt "blue crystal armor"
python asset_lab/helpers/create_lab_asset.py create-animation --provider self --type character --name crystal_knight --animation walk --source-image-version 1 --prompt "walking"
python asset_lab/helpers/promote_lab_asset.py --operation promote-new --type effect --asset-id magic_poof --image-version 1
```

Use the agent to create, inspect, and promote assets. It should read the
manifest first and use the helper commands rather than guessing paths.

See [ASSET_LAB_GUIDE.md](ASSET_LAB_GUIDE.md) and
[AUDIO_WORKFLOW.md](AUDIO_WORKFLOW.md).

## Cutscene Engine

Cutscenes are declarative Lua scenes in `cutscene_engine/scenes/`.

Ask the agent to edit a scene, then validate and preview it:

```cmd
python cutscene_engine/tools/validate_scene.py duck_slime_date
lovec . --cutscene duck_slime_date
```

The engine reuses the game systems for actors, movement, animation, camera,
dialogue, effects, music, and sound.

See [CUTSCENE_ENGINE_GUIDE.md](CUTSCENE_ENGINE_GUIDE.md).

## Game Design

Use `game_lore/` for story, characters, world rules, and design context. Ask
the agent to read the lore before changing game behavior or writing scenes.

The template is designed around small reusable systems, literal data files,
inspectable scenes, and fast agent-assisted iteration.

## More Docs

- [LOVE2D_TEMPLATE_TUTORIAL.md](LOVE2D_TEMPLATE_TUTORIAL.md)
- [TESTING_AND_DEBUGGING.md](TESTING_AND_DEBUGGING.md)
- [AGENTS.md](AGENTS.md)
