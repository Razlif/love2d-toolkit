# Agent Guidelines

This file currently describes how agents should help build this template.
Later, before the toolkit is treated as user-facing, rewrite it as guidance for
making games with the finished template.

## Working Style

- Keep changes small and easy to inspect.
- Prefer literal, obvious file and folder names.
- Do not add architecture unless it solves an immediate template need.
- Preserve the current folder structure unless the user agrees to change it.
- Use mock assets only when they already exist in the project.

## Project Boundaries

- `game/` contains Love2D runtime code.
- `game_data/` contains structured Lua data used by the game.
- `media_assets/` contains game-ready art, audio, fonts, and UI assets.
- `asset_lab/` is self-contained asset generation and inspection.
- `game_lore/` contains story, world, and context notes.
- `qa/` contains checks, reports, and testing helpers.
- `dev_tools/` contains export, build, and packaging tools.
- `cutscene_engine/` is a placeholder until the base game template is stable.

## Love2D Rules

- The repository root is the Love2D source root; root `main.lua` and `conf.lua`
  forward into the `game/` code folder.
- Use Love2D callbacks only as entry points: `love.load`, `love.update`,
  `love.draw`, and input callbacks.
- Keep `main.lua` small.
- Route app flow through `states_manager.lua`.
- Put reusable behavior in `game/systems/`.
- Put reusable entity templates in `game/entities/`.
- Put game state screens in `game/game_states/`.

## 2.5D Rules

- Use `x`, `y`, and `z` position values.
- Treat `x/y` as screen or world ground-plane position.
- Treat `z` as height above ground.
- Draw order should use ground or bottom Y, not raw image top-left Y.
- MVP collision uses masks, sensors, and overlap detection.
- Do not use the Love2D physics engine for MVP 2.5D gameplay.
- Collision detection reports overlaps; game logic decides the response.

## Asset Workflow

- Generated or test assets start inside `asset_lab/lab_assets/`.
- Approved game assets move manually into `media_assets/`.
- Game data records in `game_data/` describe how assets are used.
- Do not auto-promote lab assets into the game without user approval.
- Keep mock duck/slime assets as replaceable examples only.

## Asset Lab Rules

Asset Lab is a controlled asset intake system. The agent must use the helper
commands and the manifest instead of inventing paths.

Preflight:

- Read `asset_lab/manifest.json` before every Asset Lab operation.
- Run `python asset_lab/helpers/validate_lab_assets.py` before creating assets.
- If validation reports drift, run
  `python asset_lab/helpers/sync_manifest.py --report`, then stop and report the
  issue unless the user asks to repair it.
- Use `python asset_lab/helpers/sync_manifest.py --apply` only to mark missing
  manifest files and register orphan files. Never use sync to guess an orphan's
  meaning or promote it into a real asset.
- Before live provider calls, run
  `python -m unittest qa.asset_checks.test_asset_lab -v`.

Command approval:

- Always run the creator once without `--execute` first.
- Inspect the dry-run output and request JSON.
- Before running any `--execute` Asset Lab command, print the exact terminal
  command to the user and wait for approval.
- This approval rule is especially important for `pixellab`, `autosprite`, and
  `self`.

Creator commands:

- `create-new --type character|prop|background|effect`: create a new asset
  folder and image `v001`.
- `add-image-version --mode brand_new`: add another image version from text
  only. This does not send an existing image to the provider.
- `add-image-version --mode with_reference --source-image-version v001`: add
  another image version using a specific existing image version as reference.
- `create-animation`: create a sprite sheet/GIF from an existing image version.
- `check-provider-account --provider autosprite`: check AutoSprite account
  access before paid/provider-side work.
- `prepare-provider-character --provider autosprite`: upload a manifest image
  version and store the returned provider character id in manifest state.

Promotion commands:

- `python asset_lab/helpers/promote_lab_asset.py --operation promote-new
  --type character --asset-id NAME --image-version N --animation NAME=N`: add
  an approved Asset Lab asset to the runtime game asset set.
- Use `--operation promote-update` for an already promoted asset. It replaces
  the selected runtime image or animation slot and leaves unrelated slots
  unchanged.
- Use `--dry-run` to inspect the promotion plan. Normal promotion executes
  directly; no separate user approval step is required.
- Promotion copies PNG images and sprite sheets into `media_assets/`, updates
  `game_data/promoted_assets.json` and generated `game_data/asset_manifest.lua`,
  and does not copy GIF previews.
- Never provide arbitrary source or destination paths. Resolve exact versions
  from `asset_lab/manifest.json`.

After execution:

- Run `python asset_lab/helpers/validate_lab_assets.py`.
- Run `python asset_lab/helpers/export_browser_manifest.py` after manifest
  changes so the frontend viewer receives the current asset index.
- If validation fails, do not create more assets until the issue is understood.
- If files are missing or orphaned, run
  `python asset_lab/helpers/sync_manifest.py --report`.
- Use trace and metadata files for debugging. Use manifest PNG/GIF paths as the
  important asset references.

Path and naming rules:

- Do not guess asset paths. Use manifest paths when an existing asset or image
  version is involved.
- Asset names and animation names are slugified. Check spelling carefully before
  creating new names.
- `asset_lab/manifest.json` is the source of truth for what Asset Lab knows
  about. Files on disk without manifest entries are drift.
- Be explicit with the user about `brand_new` versus `with_reference`; they are
  different creative operations and may produce very different consistency.
- For `create-animation`, pass `--source-image-version`; do not pass a manually
  guessed image path.
- Each image/animation entry should keep `prompt`, `variation_group_id`, and
  `prompt_metadata`. The asset `type` lives on the asset record and is repeated
  as `asset_type` inside `prompt_metadata` for easier agent scanning.
- Use the same `--variation-group-id` for sibling variations created from one
  user request. If omitted, the creator generates one.

Provider notes:

- `self`: no API call. On `--execute`, the tool registers pending manifest paths
  and prints exact file creation instructions. Save the requested PNG/GIF files
  at those exact paths, then validate.
- For `self with_reference`, use the printed source image path as the visual
  reference when creating the next version.
- `pixellab`: external provider; use only after dry-run, tests, validation, and
  user approval.
- `autosprite`: stateful provider. Do not request AutoSprite spritesheets until
  the asset has `provider_state.autosprite.character_id` in
  `asset_lab/manifest.json`.

## Data Rules

- Prefer Lua tables for project data.
- Keep data readable by non-programmers where possible.
- Character files may include their own asset references for MVP simplicity.
- Split asset registries later only if reuse becomes painful.

## Graphify

This project may have a local knowledge graph in `graphify-out/`.

- Use Graphify for local context, not as a deliverable.
- Do not commit `graphify-out/`.
- For codebase questions, prefer `graphify query "<question>"` when useful.
- After meaningful code changes, run `graphify . --code-only` or
  `graphify update .` if available.
- Do not run report, HTML, or community generation unless the user asks.

## Cutscene Engine

- Scene files live in `cutscene_engine/scenes/` and use declarative Lua timelines.
- Validate a scene before previewing it with `python cutscene_engine/tools/validate_scene.py duck_slime_intro`.
- Preview the example inside the normal Love2D runtime with `lovec . --cutscene duck_slime_intro`.
- Preview the date scene with `lovec . --cutscene duck_slime_date`.
- Cutscene actors reuse generic rendering systems from `game/`, but never gameplay controllers, AI, or gameplay collision responses.
- Keep dialogue, movement, camera commands, and effects in the scene timeline so scenes remain easy to inspect and reorder.
