# Troubleshooting Guide

[简体中文](TROUBLESHOOTING.md) | **English**

This document lists common problems and their solutions.

## Packaging Problems

### Problem 1: No mod directories found

Cause: incorrect directory structure.

Fix:

1. Ensure the layout is:

```text
<mod-name>/
└── src/
    └── info.json
```

2. Ensure `info.json` exists and is readable
3. Ensure the mod directory is in the repository root

### Problem 2: missing fields in `info.json`

Cause: one or more required fields are absent.

Fix: add all required fields such as `name`, `version`, `factorio_version`, `title`, `author`, and `description`.

### Problem 3: missing entrypoint file

Cause: no valid `control`, `data`, or `settings` entry file exists under `src/`.

Fix: create at least one of:

- `control.lua` / `control.ts`
- `data.lua` / `data.ts`
- `settings.lua` / `settings.ts`

## Publishing Problems

### Problem 1: `FACTORIO_TOKEN` is missing or invalid

Fix:

1. Generate a new key at https://factorio.com/profile
2. Enable `ModPortal: Publish Mods`
3. Add it as the GitHub secret `FACTORIO_TOKEN`

### Problem 2: mod does not exist on Mod Portal

Cause: the first release requires a mod page to exist first.

Fix:

1. Package the mod locally
2. Open https://mods.factorio.com/
3. Upload the first version manually
4. Use automation after the page exists

### Problem 3: wrong tag format

Cause: the tag does not match `<mod-name>-v<version>`.

Fix:

1. Delete the wrong tag
2. Create the correct one

### Problem 4: version mismatch

Cause: the tag version and `info.json.version` differ.

Fix: keep them identical.

### Problem 5: workflow is still using old code

Cause: workflow changes were not pushed to `main`.

Fix:

1. commit the workflow file
2. push to `main`
3. rerun the workflow if needed

## Runtime Errors

### `attempt to index global 'game' (a nil value)`

Cause: runtime APIs were used during the data stage.

Fix: move that logic to `control.lua`.

### `data.raw is read-only`

Cause: prototype mutation attempted during the control stage.

Fix: move prototype changes into `data.lua` or `data-final-fixes.lua`.

### `attempt to index global 'script' (a nil value)`

Cause: `script` API used in the data stage.

Fix: register events in `control.lua` only.

### `Unknown key "localised_name"`

Cause: the prototype type does not support that field.

Fix: verify the supported fields in the official API docs.

## Localization Problems

### Text is not localized

Cause: wrong `locale.cfg` path or formatting.

Fix:

1. ensure the path is `src/locale/en/locale.cfg`
2. ensure the file format is correct
3. ensure the file is UTF-8 without BOM

### Chinese text appears garbled

Cause: wrong file encoding.

Fix: save the file as UTF-8 without BOM.

## Dependency Problems

### Wrong load order

Cause: dependency not declared in `info.json`.

Fix: add the dependency explicitly.

### Optional dependency is assumed to exist

Fix: check it in code using `mods["optional-mod"]`.

## Performance Problems

### The game stutters

Cause: logic runs too frequently on `on_tick`.

Fix: prefer `script.on_nth_tick(...)` and event filters.

### Save loads slowly

Cause: too much data is stored in `global`.

Fix:

1. store only necessary data
2. store indices instead of whole objects where possible
3. clean stale data regularly

## Compatibility Problems

### Old saves fail to load

Cause: prototype names changed without a migration.

Fix: add a script under `migrations/<version>.lua`.

### Multiplayer desyncs

Cause: non-deterministic logic such as raw timestamps or uncontrolled randomness.

Fix: use Factorio’s deterministic APIs and patterns.

## Debugging Tips

- use `log(...)` for detailed logging
- use `/c ...` commands carefully for testing
- use `game.reload_mods()` only when the type of change allows it

## Getting Help

If none of the above works:

1. read the official Factorio docs
2. search the Factorio forums
3. ask in the Factorio Discord community
4. search or open GitHub issues

When asking for help, include:

- the full error message
- relevant `info.json` content
- the relevant code snippet
- Factorio version
- mod version
