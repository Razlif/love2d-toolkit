# Audio Workflow

Audio follows the same path as art:

```text
search -> inspect -> preview -> import selected file -> promote -> play
```

## Search

Freesound searches require `FREESOUND_API_KEY` in `.env`. Searches are
metadata-first; they do not download ten files automatically. Local preview
files are downloaded when a candidate is explicitly imported.

```cmd
python asset_lab/helpers/audio_search.py --source freesound --kind sound --query "magic spell" --license cc0 --limit 10 --execute
```

Kenney and OpenGameArt are supported as curated catalog entries or supplied
URLs. The tools do not scrape those sites.

## License And Attribution

The workflow accepts CC0 and CC BY. Reject NC, ND, and unknown licenses unless
the workflow is deliberately extended. Even when attribution is optional,
record the creator, source page, source ID, license, and attribution note.

## Import And Promote

Select a candidate in Asset Lab, then import it:

```cmd
python asset_lab/helpers/audio_import.py --candidate-id oga_magic_spell_jaggedstone_3 --asset-id magic_bomb_spell --execute
```

Promote the imported file into the runtime registry:

```cmd
python asset_lab/helpers/promote_audio_asset.py --operation promote-new --kind sound --asset-id magic_bomb_spell --candidate-id oga_magic_spell_jaggedstone_3 --execute
```

Runtime files live under `media_assets/audio/music/` and
`media_assets/audio/sounds/`. Attribution is stored in
`media_assets/audio/ATTRIBUTIONS.json`; the generated Lua manifest is consumed
by `AudioManager`.

Use `promote-update` to replace an existing logical audio asset. Do not delete
unrelated manifest entries.

## Asset Lab Preview

Regenerate the browser manifest after catalog changes:

```cmd
python asset_lab/helpers/export_browser_manifest.py
```

Open `asset_lab/index.html`, choose Audio Library, and use the candidate play
controls. Remote previews can be played before import; imported candidates
also have local files. Missing previews remain visible as warnings.

## Runtime Use

Gameplay calls `AudioManager.play_music("game_ambient")` or
`AudioManager.play_sfx("magic_bomb_spell")`. Cutscenes use timeline commands
`play_music`, `play_sound`, and `stop_music`. A dialogue typing sound can be
registered as a normal sound effect and triggered by the dialogue system.
