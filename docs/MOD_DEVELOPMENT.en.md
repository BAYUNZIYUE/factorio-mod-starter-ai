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
    ├── changelog.txt
    ├── thumbnail.png
    ├── locale/
    │   ├── en/
    │   │   └── locale.cfg
    │   └── zh-CN/
    │       └── locale.cfg
    ├── graphics/
    ├── sounds/
    ├── prototypes/
    └── scripts/
```

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

- `name`: internal mod identifier; must match the directory name and use kebab-case
- `version`: semantic version (`major.minor.patch`)
- `factorio_version`: minimum supported Factorio version
- `title`: player-visible mod title
- `author`: author name
- `description`: short description
- `dependencies`: dependency list (optional)

## Factorio Stage Boundaries

Factorio mod loading is split into three major stages, and each stage has different APIs. **Breaking stage boundaries causes runtime errors.**

### Stage Order

```text
Game starts
  ↓
1. Settings stage
2. Data stage
3. Prototype lock (`data.raw` becomes effectively read-only at runtime)
4. Control stage
5. Runtime events
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

Allowed:
- `script`
- `game`
- `remote`
- `rendering`
- `settings.global`, `settings.player`

Forbidden:
- `data:extend`
- mutating `data.raw`

## Common Errors and Fixes

### Error 1: using `game` in the data stage

Typical error: `attempt to index global 'game' (a nil value)`

Fix: move runtime logic to `control.lua`.

### Error 2: mutating prototypes in the control stage

Typical error: `data.raw is read-only`

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

- use kebab-case
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

If you rename prototypes, consider adding `migrations/` scripts.

Also initialize global state with `script.on_init(...)` and handle upgrades with `script.on_configuration_changed(...)`.

## Debugging Tips

- use `log(...)` for file logging
- use `game.print(...)` for quick in-game debugging
- use `/c ...` carefully in the console for controlled testing

## Next Steps

- Read [Publishing Guide](PUBLISHING.en.md)
- Read [Troubleshooting](TROUBLESHOOTING.en.md)
- Read the [Factorio Lua API](https://lua-api.factorio.com/)
