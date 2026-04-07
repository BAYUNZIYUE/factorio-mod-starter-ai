# AI Collaboration Rules

[简体中文](AI_RULES.md) | **English**

**This document is mandatory. All AI assistants working in this repository must follow it strictly.**

## Core Principles

1. **Preserve framework stability** - do not break the publishing system
2. **Follow naming conventions** - all names must follow the defined rules
3. **Verify before finishing** - changes must not break existing behavior
4. **Update docs alongside code** - documentation is part of the deliverable

---

## 🚫 Core Rules That Must Not Be Changed

### 1. Tag Naming Format

**Format:** `<mod-name>-v<version>`

**Examples:**
- ✅ `my-awesome-mod-v1.0.0`
- ✅ `another-mod-v2.1.0`
- ❌ `v1.0.0`
- ❌ `my-awesome-mod_v1.0.0`
- ❌ `my-awesome-mod-1.0.0`

The workflow depends on this format to extract the mod name.

### 2. Mod Directory Layout

**Required structure:**

```text
<mod-name>/
└── src/
    ├── info.json
    └── control.lua
```

At least one entry file is required:

- `control.lua` or `control.ts`
- `data.lua` or `data.ts`
- `settings.lua` or `settings.ts`

Never:

- place `info.json` in the mod root
- omit every entrypoint
- replace `src` with another directory name

### 3. API Endpoint

**Correct endpoint:** `https://mods.factorio.com/api/v2/mods/init_publish`

Never use:

- `init_upload`
- `releases/init_upload`
- any v1 endpoint variants

**Auth format:** `Authorization: Bearer $FACTORIO_TOKEN`

### 4. Environment Variable Names

**Defined variables (must not be renamed):**
- `TARGET_MOD` - specific mod to package
- `MOD_OUTPUT_DIR` - packaging output directory
- `FACTORIO_TOKEN` - Factorio API key

**Security requirements:**
- Never write the real `FACTORIO_TOKEN` value into repository files, docs, sample code, screenshots, or logs
- Never create tags or releases during testing just to “check the workflow”
- Unless the user explicitly authorizes it, AI may package locally only and must not trigger remote production publishing

### 5. Workflow Triggers

Current configuration:

```yaml
on:
  release:
    types: [published]
  workflow_dispatch:
```

Never:

- remove `workflow_dispatch`
- change the `release` trigger type casually

---

## ✅ What May Be Improved

### 1. Error Handling

You may improve workflow error handling, for example:

- clearer error messages
- safer failure handling
- better logging

### 2. Packaging Validation

You may improve `pack_mods.py` validation, for example:

- more field checks
- better error messages
- stronger file completeness checks

### 3. Documentation and Examples

You may improve:

- README files
- examples
- explanatory docs

---

## 🎯 Factorio Stage Boundary Rules

These are central to Factorio modding. Breaking them causes runtime errors.

### Settings Stage (`settings.lua`, `settings-updates.lua`, `settings-final-fixes.lua`)

Only:

- define mod settings prototypes
- use `data:extend` for settings

Never:

- use runtime APIs like `game`, `script`, or `defines.events`
- define non-settings prototypes here

### Data Stage (`data.lua`, `data-updates.lua`, `data-final-fixes.lua`)

Only:

- define and modify prototypes
- use `data:extend`
- read and write `data.raw`
- read startup settings

Never:

- use runtime APIs like `game`, `script`, or `remote`
- register runtime event handlers
- depend on gameplay state

### Control Stage (`control.lua`, `scripts/`)

Only:

- register event handlers
- use runtime APIs such as `game`, `script`, `remote`, and `rendering`
- read runtime settings
- manipulate gameplay state

Never:

- modify `data.raw`
- call `data:extend`
- define new prototypes

### Load Order

```text
Game starts
  ↓
1. Settings stage
2. Data stage
3. Prototype lock
4. Control stage
5. Runtime events
```

---

## 📋 Checklists

### When creating a new mod

- [ ] Use kebab-case for the directory name
- [ ] Create `src/info.json` with all required fields
- [ ] Create at least one entrypoint file
- [ ] Test packaging with `TARGET_MOD="your-mod-name" python3 pack_mods.py`
- [ ] Verify zip structure

### When modifying an existing mod

- [ ] Update `info.json.version`
- [ ] Update `changelog.txt` when needed
- [ ] Check stage-boundary correctness
- [ ] Test packaging successfully
- [ ] Verify the mod can load in-game

### When publishing a new version

- [ ] `info.json` version is correct
- [ ] `changelog.txt` is updated
- [ ] Tag format is `<mod-name>-v<version>`
- [ ] Mod name matches directory name
- [ ] Tag version matches `info.json`

---

## 🔍 Common Errors

### `attempt to index global 'game' (a nil value)` in data stage

Cause: runtime API used in `data.lua`

Fix:
- move runtime logic into `control.lua`
- keep data stage for prototypes only

### `data.raw is read-only` in control stage

Cause: prototype mutation attempted in `control.lua`

Fix:
- move prototype changes into `data.lua` or `data-final-fixes.lua`
- only read prototype information at runtime

### Workflow failed because tag format is wrong

Cause: tag does not match `<mod-name>-v<version>`

Fix:
- delete the wrong tag
- create the correct tag

### Packaging failed because no entrypoint exists

Cause: no `control`, `data`, or `settings` file under `src/`

Fix:
- add at least one supported entrypoint file
- ensure the extension is `.lua` or `.ts`

---

## 📚 References

- [Factorio Mod Portal API](https://wiki.factorio.com/Mod_publish_API)
- [Factorio Lua API](https://lua-api.factorio.com/)
- [Factorio Modding Tutorial](https://wiki.factorio.com/Tutorial:Modding_tutorial)
- [Data Lifecycle](https://lua-api.factorio.com/latest/Data-Lifecycle.html)

---

## 🤖 Extra Guidance for AI Assistants

Before changing code:

1. Read `AGENTS.md`
2. Check existing patterns in the repository
3. Verify stage-boundary correctness
4. Test packaging immediately after changes

When answering questions:

1. State clearly which stage the code belongs to
2. Provide complete examples with context
3. Call out common traps
4. Suggest how to verify the result

When creating features:

1. Plan stages first
2. Keep settings / data / control separated
3. Consider save compatibility and multiplayer determinism
4. Localize all player-facing text

**These are not suggestions. They are hard rules. Breaking them can make the publish system fail or make mods unusable.**
