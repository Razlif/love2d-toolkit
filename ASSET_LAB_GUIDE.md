# Asset Lab Guide

Asset Lab is a self-contained browser viewer plus CLI workflow. It creates and
inspects assets before they become runtime assets.

## Folders

Each asset lives under a literal type and name:

```text
asset_lab/lab_assets/characters/barbarian_duck_wizard/
  original_images/
  sprite_sheets/
  animation_gifs/
  metadata.json
  trace.jsonl
```

The manifest is the source of truth. Do not guess paths from filenames.

## Create And Validate

Run validation first:

```cmd
python asset_lab/helpers/validate_lab_assets.py
```

Use `create_lab_asset.py` for image and animation operations. The important
creative modes are `brand_new` (text only) and `with_reference` (a selected
existing image version). Animation creation names the source image version and
the animation, such as `jump` or `burst`.

Always inspect a dry run before an external provider call. The tool records a
request and trace without changing the manifest until execution succeeds.

## Drift

```cmd
python asset_lab/helpers/sync_manifest.py --report
python asset_lab/helpers/sync_manifest.py --apply
```

Missing manifest files are marked missing. Files on disk without entries are
recorded as orphans. Sync does not invent asset meanings, repair typos, or
promote files.

## Browser Viewer

Open `asset_lab/index.html` directly. It shows groups, versions, animations,
metadata, missing files, orphan warnings, and audio candidates. After manifest
changes:

```cmd
python asset_lab/helpers/export_browser_manifest.py
```

The generated browser files contain no API keys. Candidate catalogs and local
previews are ignored because they are local working data.

## Promote To Runtime

Promotion copies selected PNGs and sprite sheets to `media_assets/`, updates
`game_data/promoted_assets.json`, and regenerates `game_data/asset_manifest.lua`.
GIFs remain previews.

```cmd
python asset_lab/helpers/promote_lab_asset.py --operation promote-new --type effect --asset-id magic_explosion --image-version 1 --animation burst=1 --dry-run
python asset_lab/helpers/promote_lab_asset.py --operation promote-new --type effect --asset-id magic_explosion --image-version 1 --animation burst=1
```

Use `promote-update` for an existing runtime asset. It replaces only the
selected image or animation slot and keeps unrelated slots. Run validation and
the relevant tests after promotion.
