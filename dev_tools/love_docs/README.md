# Love2D API Reference

This folder contains the searchable Love2D 11.5 API reference used by agents.
Queries are local and do not need network access or API keys.

```cmd
python dev_tools/love_docs/love_docs.py version
python dev_tools/love_docs/love_docs.py search camera
python dev_tools/love_docs/love_docs.py lookup love.graphics.captureScreenshot
python dev_tools/love_docs/love_docs.py check
```

Use `--json` when an agent needs structured output. Query only the relevant
module or function instead of placing the complete reference in context.

The index is generated from the pinned [`love-api`](https://github.com/love2d-community/love-api)
source for Love2D 11.5. Refresh it explicitly:

```cmd
python dev_tools/love_docs/update_api.py --check
python dev_tools/love_docs/update_api.py --execute
```

The update command uses the installed `lovec` or `love` executable, downloads
the pinned source into a temporary folder, validates the result, and replaces
the committed JSON index only after successful conversion.
