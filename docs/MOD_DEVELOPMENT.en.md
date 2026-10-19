# Mod Development Guide

[简体中文](MOD_DEVELOPMENT.md) | **English**

This document covers the core concepts, directory structure, and best practices for Factorio mod development.

## Directory Structure

Each mod should use the following layout:

```text
<mod-name>/
├── README.md
└── src/
    ├── info.json
    ├── control.lua
    ├── data.lua
    ├── settings.lua
    ├── data-updates.lua
    ├── data-final-fixes.lua
    ├── settings-updates.lua
    ├── settings-final-fixes.lua
    ├── changelog.txt              # recommended, not required; root dir also works, but not both
    ├── thumbnail.png
    ├── locale/
    │   ├── en/
    │   │   └── locale.cfg
    │   └── zh-CN/
    │       └── locale.cfg
    ├── graphics/
    ├── sounds/
    ├── prototypes/
    ├── scripts/
    └── migrations/                # save migrations (optional)
```

`info.json` and at least one `.lua` entrypoint are mandatory; add other files as needed. `changelog.txt` is recommended but optional.

Factorio only loads `.lua` entry files. If you use TypeScript, compile it to `.lua` with TypeScriptToLua first; this template does not include that toolchain.

## Required `info.json` Fields

```json
{
  "name": "mod-name",
  "version": "1.0.0",
  "factorio_version": "2.0",
  "title": "Mod Title",
  "author": "Your Name",
  "description": "Mod description",
  "dependencies": ["base >= 2.0"]
}
```

Field meanings:

- `name`: internal mod identifier; must match the directory name (lowercase letters, digits, `-`, `_`; kebab-case recommended)
- `version`: semantic version (`major.minor.patch`)
- `factorio_version`: target Factorio major version; use a single major version such as `"2.0"`. Current stable is 2.0.x and 2.1 is still experimental; a 2.0 mod does not load automatically in 2.1
- `title`: player-visible mod title
- `author`: author name
- `description`: short description
- `dependencies`: dependency list (optional)

## Factorio Stage Boundaries

Factorio loading is not just three stages. Settings and Data run first; after prototypes are locked the control stage begins, and inside it the callbacks run in a defined order. Each stage exposes different APIs. **Breaking stage boundaries causes runtime errors.**

### Stage Order

```text
Game starts
  ↓
1. Settings stage
   - settings.lua
   - settings-updates.lua
   - settings-final-fixes.lua
  ↓
2. Data stage
   - data.lua
   - data-updates.lua
   - data-final-fixes.lua
  ↓
3. Prototype lock (prototypes can no longer be modified)
  ↓
4. Control stage: control.lua is loaded
   - script/remote/commands/settings/defines/log/require available at the top level
   - game and rendering are not available at the top level
  ↓
5. on_init (new save only)
  ↓
6. migrations (loading a save from an older mod version)
   - src/migrations/<mod-version>.lua
  ↓
7. on_load (existing save loads only; not for new saves/new mods; `storage` read-only)
  ↓
8. on_configuration_changed (mod or game version changed)
  ↓
9. Runtime events
```

### Settings Stage

Purpose: define mod settings.

Allowed:
- `data:extend` for settings prototypes

Forbidden:
- `game`, `script`, `remote`
- non-settings prototypes

### Data Stage

Purpose: define and modify game prototypes.

Allowed:
- `data:extend`
- `data.raw`
- `settings.startup`

Forbidden:
- `game`, `script`, `remote`, `rendering`
- runtime event handlers

### Control Stage

Purpose: runtime logic and event handling.

Available APIs (note where they are available):

- top level: `script`, `remote`, `commands`, plus `settings.global`, `defines`, `log`, `require`
- inside callbacks only (`on_init`, `on_configuration_changed`, event handlers): `game`, `rendering`
- runtime settings: `settings.global` (readable at the top level), `settings.get_player_settings(player)` (needs a player, callbacks only)

Forbidden:

- using `game` or `rendering` at the top level of `control.lua`
- accessing the `data` global (it is inaccessible in the control stage; prototypes are locked)

At the top level, `script`, `remote`, `commands`, `settings.global`, `defines`, `log`, and `require` are available; `game` and `rendering` are not. Any logic that needs `game` must live inside `on_init`, `on_configuration_changed`, or an event callback.

## Common Errors and Fixes

### Error 1: using `game` in the data stage

Typical error: `attempt to index global 'game' (a nil value)`

Fix: move runtime logic to `control.lua`.

### Error 2: accessing `data` in the control stage

Typical error: `attempt to index global 'data' (a nil value)`

Cause: the `data` global only exists during the data stage. It is not readable in the control stage (it is not merely read-only), and prototypes are locked.

Fix: move prototype changes into `data.lua` or `data-final-fixes.lua`.

### Error 3: defining non-settings prototypes in `settings.lua`

Fix: move those definitions into `data.lua`.

## File Load Order

### Settings stage order

1. `settings.lua`
2. `settings-updates.lua`
3. `settings-final-fixes.lua`

### Data stage order

1. `data.lua`
2. `data-updates.lua`
3. `data-final-fixes.lua`

Typical use:

- `data.lua`: define your own prototypes
- `data-updates.lua`: react to or modify other mods’ prototypes
- `data-final-fixes.lua`: ensure your final changes run last

## Localization

All player-facing text should be stored in `locale/`.

Example:

```ini
[item-name]
my-item=My Item

[item-description]
my-item=A useful item.

[mod-setting-name]
my-mod-enable-feature=Enable Feature
```

You can reference localized strings in prototypes using localized keys.

## Naming Conventions

### Mod directory name

- use kebab-case (lowercase + hyphens); underscores are also valid
- keep it identical to `info.json.name`
- example: `my-awesome-mod`

### Prototype names

- prefix them with the mod name to avoid conflicts
- use hyphens
- example: `my-mod-item`, `my-mod-recipe`

### File names

- keep Lua file names lowercase
- examples: `data.lua`, `data-updates.lua`, `control.lua`

## Dependency Management

Declare dependencies in `info.json`:

```json
{
  "dependencies": [
    "base >= 2.0",
    "? optional-mod >= 1.0",
    "! incompatible-mod",
    "(?) hidden-optional >= 1.0"
  ]
}
```

- no prefix: required dependency
- `?`: optional dependency
- `!`: incompatible dependency
- `(?)`: hidden optional dependency

Check optional dependencies in code with `mods["optional-mod"]`.

## Performance Tips

- avoid overly frequent `on_tick`
- prefer `script.on_nth_tick(...)`
- use event filters where possible
- cache repeated lookups when appropriate

## Save Compatibility

If you rename prototypes, add a migration under `src/migrations/`:

```text
<mod-name>/
└── src/
    └── migrations/
        └── <mod-version>.lua
```

For example, upgrading the mod from `1.0.0` to `1.1.0` means `src/migrations/1.1.0.lua`. The filename is the **mod version** (`info.json.version`), not the Factorio version. Factorio runs migration files whose version is newer than the mod version recorded in the save.

Also initialize global state with `script.on_init(...)` and handle upgrades with `script.on_configuration_changed(...)`.

## Debugging Tips

- use `log(...)` for file logging
- use `game.print(...)` for quick in-game debugging
- use `/c ...` carefully in the console for controlled testing

## Next Steps

- Read [Publishing Guide](PUBLISHING.en.md)
- Read [Troubleshooting](TROUBLESHOOTING.en.md)
- Read the [Factorio Lua API](https://lua-api.factorio.com/)
