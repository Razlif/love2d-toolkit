# Agent Guidelines

These rules guide an agent working on the toolkit and on games made with it.
Keep changes small, literal, inspectable, and easy to test. Do not invent new
architecture when an existing system or folder already fits.

## Repository Boundaries

- `game/`: Love2D runtime systems, entities, controllers, and states.
- `game_data/`: editable Lua definitions and generated runtime registries.
- `media_assets/`: game-ready art and audio.
- `asset_lab/`: self-contained asset generation, intake, and inspection.
- `cutscene_engine/`: declarative cutscene playback and scene tools.
- `game_lore/`: story and world context.
- `qa/`: automated checks and Love2D harnesses.
- `dev_tools/`: future export and packaging tools.

The repository root is the Love2D source root. Keep root `main.lua` and
`conf.lua` small; route runtime behavior through `game/main.lua` and the state
manager.

## Runtime Rules

- Love callbacks are entry points, not places for game-specific logic.
- Reusable behavior belongs in `game/systems/`; reusable objects belong in
  `game/entities/`; screens belong in `game/game_states/`.
- Use the template's `x`, `ground_y`, and `z` position model for 2.5D.
- Draw order uses ground/bottom Y.
- Collision is mask/sensor overlap reporting only. Game logic decides the
  response; do not add Love2D physics to the MVP.
- Cutscene actors reuse rendering systems but never gameplay controllers, AI,
  or gameplay collision responses.

## Asset Lab Workflow

1. Read `asset_lab/manifest.json` before an operation.
2. Run `python asset_lab/helpers/validate_lab_assets.py`.
3. If drift exists, inspect with `python asset_lab/helpers/sync_manifest.py --report`.
4. Use `--apply` only to record missing files and orphan files; never guess an
   orphan's meaning.
5. Use dry runs before provider calls.
6. Use exact manifest paths and literal names; never guess a source path.

Creation modes are explicit:

- `brand_new`: text-only creation.
- `with_reference`: creation based on a selected existing image version.
- `create-animation`: animation based on a selected image version.

Promotion is an agent-controlled operation and does not require a separate
approval step. Use `--dry-run` first when the operation is unfamiliar.

```cmd
python asset_lab/helpers/promote_lab_asset.py --operation promote-new --type character --asset-id NAME --image-version 1 --animation jump=1
python asset_lab/helpers/promote_lab_asset.py --operation promote-update --type character --asset-id NAME --image-version 2
```

Promotion updates `media_assets/`, `game_data/promoted_assets.json`, and the
generated `game_data/asset_manifest.lua`. GIF previews stay in Asset Lab.

## Audio Rules

Use `audio_search.py` for metadata-first searches and `audio_import.py` only
for selected candidates. Allowed licenses are CC0 and CC BY. Always preserve
creator, source URL, source ID, license, and attribution text, including for
CC0 assets. API keys stay in `.env`; local catalogs and previews stay ignored.

Promote selected audio with `promote_audio_asset.py`, then regenerate the
runtime manifest. Do not scrape curated sites.

## Cutscene Rules

Scene files live in `cutscene_engine/scenes/`. Validate before previewing:

```cmd
python cutscene_engine/tools/validate_scene.py duck_slime_date
lovec . --cutscene duck_slime_date
```

Keep dialogue, movement, camera, effects, music, and sound cues in the scene
timeline. Use literal command names and valid asset IDs.

## Debugging And Graphify

Useful launch flags are `--debug`, `--debug-masks`, `--debug-sensors`,
`--debug-collisions`, `--debug-entities`, `--debug-camera`, `--debug-input`,
and `--debug-state`.

When `graphify-out/graph.json` exists, use `graphify query`, `graphify path`,
or `graphify explain` for codebase context. Graph output is local context and
must not be committed. After meaningful code changes, run `graphify update .`.
