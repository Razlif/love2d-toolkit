# Testing And Debugging

## Automated Tests

Run the Python suites from the repository root:

```cmd
python -m unittest qa.asset_checks.test_asset_lab qa.game_checks.test_cutscene_engine
```

Run the Love2D harness from `qa/love_checks`:

```cmd
cd qa/love_checks
lovec .
cd ../..
```

Validate a cutscene by ID:

```cmd
python cutscene_engine/tools/validate_scene.py duck_slime_date
```

Validate Asset Lab files and regenerate its browser manifest when needed:

```cmd
python asset_lab/helpers/validate_lab_assets.py
python asset_lab/helpers/export_browser_manifest.py
```

## Debug Flags

Run the game with any combination of:

```cmd
love . --debug
love . --debug-input --debug-camera --debug-state
love . --debug-masks --debug-sensors --debug-collisions
```

The flags show input, camera, state, entity, mask, sensor, and collision
information without changing gameplay responses. Collision remains report-only.

## Common Failures

- **Asset missing:** read `game_data/asset_manifest.lua`, then confirm the
  referenced file exists under `media_assets/`.
- **Manifest drift:** run `sync_manifest.py --report`; do not guess orphan
  meanings.
- **Browser is stale:** regenerate `asset_lab/manifest.js` and refresh the page.
- **Audio does not play:** check the runtime path, logical ID, file format, and
  generated audio manifest. Check attribution metadata before replacing files.
- **Wrong camera framing:** inspect entity position, camera target, bounds, and
  window dimensions with `--debug-camera`.
- **Input does not work:** use `--debug-input`; controllers should query named
  InputManager actions, not Love keyboard state directly.
- **Cutscene command fails:** validate the scene and check actor, animation,
  effect, sound, and music IDs against the runtime manifest.
- **Sprite collision looks wrong:** enable mask and sensor debugging. Sensors
  are broad prechecks; masks provide the pixel overlap report.

Keep traces, test output, and error messages attached to the change being
debugged. Do not commit API keys, local audio catalogs, previews, save files,
or generated Graphify output.
