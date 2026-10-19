# AI Collaboration Rules

[简体中文](AI_RULES.md) | **English**

This file expands `AGENTS.md` and is meant to be read on demand. When the two
conflict, the stricter safety rule wins: **irreversible actions, credentials,
publishing**.

## 1. Fixed contracts

### Tag

```text
<mod-name>-v<major.minor.patch>
```

- The version must exactly match `src/info.json` `version`
- `mod-name` must match the directory name and `info.json.name`
- Do not use `v1.0.0`, `<mod>_v1.0.0`, or `<mod>-1.0.0`

### Mod Portal API

| Case | Endpoint | Token scope |
|---|---|---|
| First-time mod creation | `POST https://mods.factorio.com/api/v2/mods/init_publish` | `ModPortal: Publish Mods` |
| New release of an existing mod | `POST https://mods.factorio.com/api/v2/mods/releases/init_upload` | `ModPortal: Upload Mods` |
| Edit description/category | see the official Mod details API | `ModPortal: Edit Mods` |

- Auth: `Authorization: Bearer $FACTORIO_TOKEN`
- Both init endpoints take only `mod`; the version comes from `info.json` in the zip
- The init response returns an upload URL; upload with `multipart/form-data`,
  field name `file`
- Success responses contain `success: true`; failures contain `error` / `message`
- **There is no API to delete a published release.** A version number is permanent

### Environment variables

- `TARGET_MOD`: package only this mod
- `MOD_OUTPUT_DIR`: output directory, default `dist`
- `FACTORIO_TOKEN`: GitHub Secrets or local environment only, never committed

### Layout and entrypoints

```text
<mod-name>/src/info.json          # required metadata (still needs one .lua entrypoint)
<mod-name>/src/control.lua        # at least one .lua entrypoint
<mod-name>/src/data.lua
<mod-name>/src/settings.lua
```

- Required `info.json` fields: `name`, `version`, `factorio_version`, `title`,
  `author`, `description`
- `factorio_version` must be a two-part major version (`"2.0"`); a 2.0 mod does
  not load in 2.1 automatically
- Only `.lua` entrypoints are loaded. TypeScript must be compiled with
  TypeScriptToLua first; this template does not ship a build chain
- Migrations go in `src/migrations/<mod-version>.lua`; the filename is the MOD
  version, not the Factorio version
- `changelog.txt` is recommended but not required; if present, `Version:` must
  exist and match `info.json` (otherwise validation fails); missing 99 dashes or
  `Date:` only warns

## 2. Stage boundaries

### Settings

Allowed: `data:extend` setting prototypes, `settings.startup`
Forbidden: `game`, `script`, event registration, editing non-setting prototypes

### Data

Allowed: `data:extend`, `data.raw`, prototype definitions/edits, `settings.startup`
Forbidden: `game`, `script`, `remote`, event registration, game state access

### Control

At the top level of `control.lua`: `script`, `remote`, `commands` (registration),
plus `settings.global`, `defines`, `log`, `require`.
`game` and `rendering` are unavailable there; they become available in
`on_init`, `on_configuration_changed`, and event handlers.
`settings.get_player_settings(player)` needs a player object, so callbacks only.
`on_load` runs only for mods already part of the save (new saves/new mods run
`on_init`); `storage` is readable but not writable; `game` is unavailable; the
only legitimate uses are rebuilding metatables, re-registering conditional
handlers, and caching `storage` references.
The `data` global **does not exist** in the control stage (it is not
"read-only"); it can neither be read nor modified.

### Load order

```text
settings.lua → settings-updates.lua → settings-final-fixes.lua
data.lua → data-updates.lua → data-final-fixes.lua
control.lua
on_init
migrations (JSON first, then Lua)
on_load
on_configuration_changed
event handlers
```

### Examples

```lua
-- ✅ data.lua: prototypes only
data:extend({
  { type = "item", name = "my-item", icon = "__my-mod__/graphics/item.png",
    icon_size = 64, stack_size = 100 }
})

-- ❌ data.lua: runtime API does not exist
-- script.on_event(defines.events.on_tick, function() end)  -- script is nil
```

```lua
-- ✅ control.lua: top level registers only
script.on_event(defines.events.on_player_created, function(event)
  local player = game.get_player(event.player_index)
  if player then player.insert({ name = "iron-plate", count = 100 }) end
end)

-- ❌ control.lua top level: game is not available yet
-- game.print("loaded")  -- game is nil at this point
```

## 3. Publishing

Publishing is irreversible. Without explicit user authorization, do not create a
release, push a tag, or call the publishing API.

```bash
# 1. Verify locally
python3 verify_mod.py --target my-mod
TARGET_MOD=my-mod python3 pack_mods.py
python3 verify_mod.py --zip-dir dist --target my-mod

# 2. Tag and create a real release (requires authorization)
git tag my-mod-v1.0.0
git push origin my-mod-v1.0.0
gh release create my-mod-v1.0.0 --title "My Mod v1.0.0" --notes "..."

# 3. Manual dispatch (dry-run by default)
#    target_mod is required; confirm must be PUBLISH to upload
```

Workflow behavior:

- `release`: publishes the tagged commit only; prereleases are skipped
- Manual dispatch: packages the specified mod only; without `confirm=PUBLISH`
  nothing is uploaded
- Before upload it queries the Mod Portal: missing mod → `init_publish`,
  existing mod → `releases/init_upload`
- Existing versions are skipped, so retries are idempotent
- After upload it queries releases again to confirm the version is visible

## 4. Checklist (commands)

Creating/changing a mod:

- [ ] `python3 verify_mod.py --target <mod>`
- [ ] `TARGET_MOD=<mod> python3 pack_mods.py`
- [ ] `python3 verify_mod.py --zip-dir dist --target <mod>`
- [ ] Load it in-game at least once and check the log for Lua errors

Before publishing:

- [ ] `info.json.version` bumped
- [ ] top `changelog.txt` version matches `info.json`
- [ ] tag version matches `info.json`
- [ ] directory name, `info.json.name`, and tag prefix all match
- [ ] explicit user authorization obtained

## 5. Common errors

| Symptom | Cause | Fix |
|---|---|---|
| `attempt to index global 'game' (a nil value)` in data stage | runtime API in data | move to a control-stage event handler |
| `attempt to index global 'data' (a nil value)` in control | `data` accessed at runtime | move prototype edits to the data stage |
| `game` is nil at control top level | reading `game` during load | move to `on_init` or an event handler |
| Mod loads with no entrypoint | only `.ts`, no compiled `.lua` | run TypeScriptToLua, or use `.lua` |
| `ModAlreadyExists` | `init_publish` used for an existing mod | use `releases/init_upload` |
| 401 | secret missing or token invalid | regenerate and update `FACTORIO_TOKEN` |
| 403 | token is valid but lacks scope | `Publish Mods` for first publish, `Upload Mods` for releases; one key with both scopes is recommended |
| `Version mismatch` | tag/zip/info.json disagree | locate with `verify_mod.py --tag` |
| `.git`/`node_modules` inside the zip | old packaging script had no excludes | use the current `pack_mods.py` |

## 6. References

- [Mod structure](https://lua-api.factorio.com/latest/auxiliary/mod-structure.html)
- [Data lifecycle](https://lua-api.factorio.com/latest/auxiliary/data-lifecycle.html)
- [Mod publish API](https://wiki.factorio.com/Mod_publish_API)
- [Mod upload API](https://wiki.factorio.com/Mod_upload_API)
- [Lua API](https://lua-api.factorio.com/)
