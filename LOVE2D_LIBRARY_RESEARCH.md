# Love2D Library Research

## Lesson 1: Utility Libraries And Architecture

### Projects reviewed

- `Nykenik24/love2d-tools`
- `vrld/hump`
- `airstruck/knife`
- `1bardesign/batteries`
- `kikito/anim8`
- `kikito/tween.lua`

### Main finding

These projects are mostly reusable Lua/Love2D libraries, not complete game architectures. They do not prescribe the game folder structure, asset pipeline, cutscene format, or QA workflow.

Their common architectural idea is small, composable, independently usable modules. The application owns the main loop and decides how those modules work together.

### Comparison with this template

Our template is more opinionated. It includes:

- Asset Lab and promotion workflow.
- Runtime game structure and game data.
- Cutscene engine.
- 2.5D positions, masks, sensors, and draw order.
- Agent-driven QA, telemetry, screenshots, and snapshots.

The libraries do not replace those project-specific systems.

### Lessons to investigate

- Animation grids, frame control, pause, looping, and flipping from `anim8`.
- Easing and interpolation from `tween.lua`.
- Signals and event dispatch from HUMP.
- Sequences, coroutines, behavior machines, and testing from Knife.
- Geometry, pathfinding, sorting, and state-machine helpers from Batteries.
- Small module boundaries and a clear library entry point from `love2d-tools`.

### Current decision

Do not add dependencies yet. Study several projects first, identify repeated patterns, then either implement small compatible versions or incorporate mature modules with their licenses and attribution preserved.

Keep our own implementations for asset manifests, QA telemetry, promotion tools, cutscenes, 2.5D conventions, masks, and sensors.

### Sources

- https://github.com/Nykenik24/love2d-tools
- https://github.com/vrld/hump
- https://github.com/airstruck/knife
- https://github.com/1bardesign/batteries
- https://github.com/kikito/anim8
- https://github.com/kikito/tween.lua

## Lesson 2: `love2d-starter-kit`

### Project reviewed

- `bthomas2622/love2d-starter-kit`

### What it is

This is closer to a complete starter application than a utility library. It includes a title menu, settings, controls, localization, audio, persistent settings, reusable UI controls, and a playable Snake example.

Its structure is direct and familiar:

- `src/states/` for screens and game flow.
- `src/ui/` for reusable interface elements.
- `src/utils/` for input, audio, localization, fonts, and JSON.
- `src/entities/` and `src/systems/` for expansion.
- `src/constants/` for centralized configuration.
- `assets/` grouped by resource type.

### Useful lessons

- A starter template should demonstrate a complete usable flow, not only empty modules.
- Settings, controls, audio, and localization are treated as first-class systems.
- Action-based input supports keyboard/gamepad mapping and remapping.
- A centralized configuration file makes window, UI, audio, input, and game tuning easy to find.
- Empty folders communicate future extension points, but working examples make the architecture understandable.

### Comparison with this template

The starter kit is a conventional game starter. Our template is broader and more agent-oriented: Asset Lab, promotion, game data, cutscenes, and QA are outside its scope.

Its `src/` naming is less literal for our goals, while our `game/`, `game_data/`, `media_assets/`, and `cutscene_engine/` separation makes the asset-to-runtime workflow clearer.

### Candidate ideas for our template

- Add a generic settings data file and settings screen later.
- Make gamepad input a planned extension of `InputManager`.
- Centralize user-facing configuration more clearly.
- Add localization as an optional system rather than assuming English text.
- Keep a small complete example game as the template’s living demonstration.

### Current decision

Learn from the structure and workflows, but do not copy the whole starter kit. Its menu, Snake gameplay, and settings are specific to its example. We should implement only the reusable patterns that fit our agent-driven workflow.

### Source

- https://github.com/bthomas2622/love2d-starter-kit

## Lesson 3: `love2d-kit`

### Project reviewed

- `Piory/love2d-kit`

### What it is

This is a small distribution/package project rather than a game framework. Its public README currently describes a library collection with `anim8` as the listed library, and installation is handled through LuaRocks.

### Main lesson

There is a difference between:

- A game architecture.
- A utility library.
- A package that distributes libraries.

`love2d-kit` is mainly the third category. It solves installation and reuse, not game states, entities, scenes, or gameplay structure.

### Useful lesson for our template

- Dependencies should have clear versions and licenses.
- A package entry point can make reusable modules easier to install.
- Bundling a library is only useful when it reduces setup friction.
- A small dependency collection should not be mistaken for a complete project architecture.

### Comparison with this template

Our repository is an application template and workflow, not currently a Lua package. We need local, literal source files because the coding agent must inspect, modify, test, and trace them easily.

We may later add optional dependency installation or vendor one mature library, but we should not turn the toolkit into a package before its APIs stabilize.

### Current decision

Study its packaging approach, but do not adopt LuaRocks or copy its structure yet. The more immediate lesson is to track dependency versions and licenses if we incorporate `anim8`, `tween.lua`, or another external module.

### Source

- https://github.com/Piory/love2d-kit

## Lesson 4: `coqui-toolkit-love2d`

### Project reviewed

- `carmelosantana/coqui-toolkit-love2d`

### What it is

This is an external agent toolkit that controls Love2D projects. It is not just Lua code inside a game. Its host toolkit can scaffold projects, launch and stop Love2D processes, generate components and scenes, inspect logs, build `.love` files, export to the browser, and communicate with the running game.

### Important ideas

- Several starting templates for different game types.
- Explicit process lifecycle: create, run, stop, status, list, build, export.
- Project-local timestamped logs plus a stable `latest.log` path.
- Generated components and scenes with known types.
- A Lua-to-bot bridge for events and requests.
- Bundled searchable Love2D API documentation.
- A companion development skill for the agent.
- One explicit verified Love2D baseline version.

### Comparison with this template

This project is much closer to our long-term agent-driven vision. We already have pieces of the same idea:

- Asset Lab helpers.
- Cutscene validation.
- QA command bridge.
- Runtime screenshots and snapshots.
- Debug telemetry.
- Root agent instructions and guides.

It goes further in the outer orchestration layer: project creation, process management, code generation, web export, and searchable API knowledge.

### Lessons for our toolkit

1. Make runtime logs easy to find, with a stable latest-run pointer.
2. Give the agent deterministic scaffolding commands instead of asking it to invent files.
3. Add a small catalog of valid component and scene types.
4. Treat Love2D version compatibility as explicit project metadata.
5. Provide local API documentation or a focused Love2D reference for the agent.
6. Keep the game-facing bridge protocol independent from the outer agent transport.

### Current decision

Do not copy the PHP/Coqui implementation. Learn from its orchestration boundary. Our next useful additions would be a project-aware QA session index, a small deterministic scaffold generator, and a local Love2D API reference.

### Source

- https://github.com/carmelosantana/coqui-toolkit-love2d

## Lesson 5: Slab

### Project reviewed

- `flamendless/Slab`

### What it is

Slab is an immediate-mode GUI toolkit for Love2D. It is designed to be copied into an existing project and used with a small integration surface:

```lua
Slab.Initialize(args)
Slab.Update(dt)
Slab.BeginWindow("id", options)
Slab.Text("Hello")
Slab.EndWindow()
Slab.Draw()
```

It is MIT-licensed, source-based, and inspired by Dear ImGui.

### Immediate-mode meaning

The game describes the UI again during each update:

```text
if debug_enabled then
  draw debug window
  draw buttons
  draw current values
end
```

The UI library manages layout, focus, input, and drawing. The game keeps the actual data and behavior.

### Useful lessons

- Immediate-mode UI is excellent for debug panels, inspectors, editors, and developer tools.
- A small integration boundary makes a library easy to add temporarily.
- Stable control IDs allow the UI to preserve focus and interaction state.
- The game should own the data; the UI should display or edit it.
- Source-based libraries are easier for an agent to inspect and customize.

### Comparison with this template

Our current menus and dialogue use retained objects such as `Button`, `Menu`, and `DialogueBox`. That is appropriate for the game’s normal user interface.

Slab suggests a second UI mode for development:

- Runtime debug inspector.
- Entity and camera inspection.
- Cutscene timeline inspector.
- Asset and animation metadata panel.
- QA command/status panel.

### Current decision

Do not replace the existing game UI with Slab. Consider adding an optional immediate-mode developer UI later, especially for the Love2D cutscene editor and in-game QA inspection.

### Source

- https://github.com/flamendless/Slab

## Lesson 6: Awesome LÖVE Library Shortlist

### Project reviewed

- `love2d-community/awesome-love2d`

This is a categorized directory, not a single framework. It is useful for discovery, but each library still needs separate evaluation for activity, compatibility, license, and fit.

### Highest-value candidates for us

- `lovebpm`: sync gameplay or cutscene events to musical timing. Especially relevant to the future music RPG.
- `LÖVE API` and LuaCATS Love2D definitions: local API reference and editor/agent context.
- `Lovebird` or `vudu`: live debugging and inspection ideas. Compare with our QA bridge before adopting.
- `love2d-community/love-api`: source for a searchable bundled API reference.
- `Jumper`: pathfinding for future NPCs and world navigation.
- `Flux`, HUMP timer, or `tween.lua`: easing and timed transitions for cameras, UI, and cutscenes.
- `busted` or `knife.test`: possible Lua-side unit testing, alongside our Python and Love2D checks.
- `baton`: future keyboard/gamepad action mapping.

### Useful but probably not needed now

- `anim8`: strong animation model, but our current animation manager already works.
- `Push` or `Resolution Solution`: resolution handling, if our camera/window layer becomes insufficient.
- `Peachy` or an Aseprite loader: only if we restore an Aseprite-based asset workflow.
- `Concord` or `tiny-ecs`: only if our character/entity model becomes difficult to manage.
- `parallax`, `Brady`, or `hump.camera`: useful references, but we already own camera and parallax systems.

### Deliberately defer

- Physics libraries, because our template uses report-only masks and sensors for 2.5D.
- Large UI replacements, because our normal UI and Slab-style developer UI have different purposes.
- Networking libraries, until the file QA bridge has a stable HTTP/WebSocket adapter boundary.

### Current recommendation

Study `lovebpm`, the Love2D API resources, one live-debugging tool, and one tweening library next. Do not add a dependency merely because it appears in the list.

### Source

- https://github.com/love2d-community/awesome-love2d

## Orchestration Roadmap

### Priority order

1. **Version baseline**: record the supported Love2D and template versions.
2. **Love2D API reference**: provide searchable local Love2D documentation for the agent.
3. **Stable run logs**: make timestamped runs and a latest-run location easy to find.
4. **Process manager**: start, inspect, pause, resume, and stop a shared Love2D session.
5. **Lua-agent bridge**: add a live transport between the running game and the external agent.
6. **Interactive live QA**: let the user play while the agent observes, diagnoses, and sends controlled commands.

### Live QA goal

```text
User runs and plays the game
  -> game emits events and state
  -> agent inspects logs and screenshots
  -> agent diagnoses a problem
  -> agent requests a snapshot, pauses, or sends a QA command
```

The current file bridge remains the deterministic batch and replay transport. A live bridge should reuse its command, event, snapshot, and result schemas.

### Bridge boundary

The first live bridge does not need a browser application. It needs:

- A small local bridge server process.
- A Love2D-side Lua client module.
- An agent-side client or command tool.
- A local-only HTTP or WebSocket transport.
- The existing QA protocol shared by all transports.

The process manager can start the bridge and the game together, track their IDs, and expose the latest logs and session state.

### Safety rules

- Bind to localhost by default.
- Validate every incoming command.
- Do not expose arbitrary Lua execution or filesystem access.
- Keep the file transport available for deterministic replay.
- Use WebSocket only when live event streaming is needed; HTTP polling is simpler for the first adapter.

## Lesson 7: Coqui Lua-To-Agent Bridge

### Bridge model

Each generated project receives a `lib/coqui_api.lua` module. The game configures an endpoint, polls for asynchronous responses during `love.update`, and sends structured events or prompts back to the bot.

Documented examples include:

- `coqui.configure({ endpoint = "http://localhost:3300" })`
- `coqui.poll()` for incoming responses.
- `coqui.sendEvent(...)` for game events.
- `coqui.sendPrompt(...)` for a request for help.

Native mode uses LuaSocket and `love.thread` for non-blocking HTTP. Browser mode uses JavaScript `fetch` through an injected `coqui_bridge.js` file.

### Important distinction

This is a game-to-agent communication API, not necessarily a complete QA driver. It lets the game report events and receive responses, while our QA bridge also needs deterministic input, screenshots, state snapshots, assertions, and replay.

### Lessons for our toolkit

- Keep a tiny game-facing bridge module.
- Make communication asynchronous so gameplay does not freeze.
- Send structured events rather than noisy text logs.
- Support separate native and browser transports behind one API.
- Reuse one protocol across file, HTTP, and WebSocket transports.
- Keep the bridge limited to localhost or an explicitly configured endpoint.
- Validate incoming commands and avoid exposing arbitrary file or code execution.

### Comparison with our QA bridge

Our current file bridge already has the safer protocol boundary and deterministic replay model. A future HTTP/WebSocket adapter could add the Coqui-style live interaction without changing our commands, telemetry, snapshots, or result bundles.

### Confidence note

The bridge conclusions above come from the project’s published package README. The GitHub source files were not available through the current web fetch, so implementation details beyond that documentation remain unverified.

### Source

- https://github.com/carmelosantana/coqui-toolkit-love2d
