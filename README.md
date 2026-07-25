# Love2D Toolkit

A small Love2D game template with reusable gameplay systems, an Asset Lab,
audio intake, and a declarative cutscene engine.

## Requirements

- Love2D 11.5 or newer
- Python 3.11 or newer for Asset Lab and QA helpers
- `lovec` for command-line Love2D runs, when available

## Run The Example

From the repository root:

```cmd
love .
```

The example opens with a title screen. Start the scene, or choose Playground
to inspect the duck, slime, bomb, camera, animation, audio, UI, and debug
systems.

Preview the cutscene directly:

```cmd
lovec . --cutscene duck_slime_date
```

## Asset Lab

Open `asset_lab/index.html` directly in a browser. After changing the manifest,
regenerate the browser copy:

```cmd
python asset_lab/helpers/export_browser_manifest.py
```

See [ASSET_LAB_GUIDE.md](ASSET_LAB_GUIDE.md) and
[AUDIO_WORKFLOW.md](AUDIO_WORKFLOW.md).

## Tests

```cmd
python -m unittest qa.asset_checks.test_asset_lab qa.game_checks.test_cutscene_engine
```

Run the Love2D QA harness from `qa/love_checks` with `lovec .`.

## Guides

- [LOVE2D_TEMPLATE_TUTORIAL.md](LOVE2D_TEMPLATE_TUTORIAL.md)
- [ASSET_LAB_GUIDE.md](ASSET_LAB_GUIDE.md)
- [AUDIO_WORKFLOW.md](AUDIO_WORKFLOW.md)
- [CUTSCENE_ENGINE_GUIDE.md](CUTSCENE_ENGINE_GUIDE.md)
- [TESTING_AND_DEBUGGING.md](TESTING_AND_DEBUGGING.md)
- [AGENTS.md](AGENTS.md)
