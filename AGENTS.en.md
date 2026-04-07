# AGENTS.md - Factorio Mod Template Repository Rules

[简体中文](AGENTS.md) | **English**

This file defines the repository-level default constraints for `factorio-mod-starter-ai`. This is a **guidance-first template repository** designed to help developers build and publish Factorio mods with AI assistance.

## Repository Purpose

This repository provides:

- A complete multi-mod workspace structure
- Automated packaging and publishing
- AI collaboration rules and repository boundaries
- Development guides and best-practice documentation

**This is not a specific mod project.** It is a reusable starting template.

## Packaging Boundary

- Only root-level directories containing `src/info.json` are treated as packageable mods
- The packaging entry script is the repository root `pack_mods.py`
- The default packaging output directory is `/home/factorio-mod-zips/`, overridable with `MOD_OUTPUT_DIR`
- The sample mod `example-mod/` is for reference only and should be deleted or replaced in real projects

## Required Mod Layout

Each formal mod should use the following structure:

```text
<mod-name>/
├── README.md
└── src/
    ├── info.json
    ├── control.lua / control.ts
    ├── data.lua / data.ts
    ├── settings.lua / settings.ts
    ├── settings-updates.lua / settings-final-fixes.lua
    ├── data-updates.lua / data-final-fixes.lua
    ├── locale/
    ├── scripts/
    ├── prototypes/
    └── changelog.txt
```

## Factorio Stage Boundaries

These are critical rules. Violating them causes runtime errors.

- `settings*`: settings definitions only (`data:extend` for settings prototypes)
- `data*`: prototype definition and modification only (`data:extend`, `data.raw`)
- `control.lua` / `scripts/`: runtime API only (`script`, `game`, `defines`, etc.)
- **Never use runtime APIs in the `data` stage**
- **Never modify `data.raw` in the `control` stage**

Why this matters:

- Factorio exposes different APIs in different load stages
- The `data` stage has prototype APIs only, not gameplay runtime APIs
- The `control` stage has runtime APIs only and cannot redefine prototypes
- Violating these boundaries leads to `nil` errors or load failures

## Development Rules

- Keep all player-facing text synchronized in `locale/`
- When adding settings, also add `mod-setting-name` and `mod-setting-description`
- When changing prototype identifiers, check whether `migrations/` is required
- Keep `control.lua` thin; move complex runtime logic to `scripts/`
- Prioritize old-save compatibility and multiplayer determinism

## Workspace Hygiene

- Do not dump zip files, logs, screenshots, or temporary scripts in the repository root
- Put generated artifacts and debug output under `artifacts/` or `dist/`
- Local cache directories like `.local/`, `.sisyphus/`, and `.codex/` should never become deliverables
- Local packaging defaults to `/home/factorio-mod-zips/`; CI packaging uses `dist/`

## Before Finishing Work

Before finishing any change, verify:

1. `info.json` fields are complete and valid (`name`, `version`, `factorio_version`, `title`, `author`, `description`)
2. The `<mod>/src/` directory structure is still intact
3. At least one valid entrypoint exists (`control`, `data`, or `settings`)
4. `python3 pack_mods.py` still packages the mod successfully
5. Factorio stage-boundary rules are still respected

## Template Usage

When creating a new project from this template:

1. Copy or fork the repository structure
2. Delete or replace `example-mod/`
3. Configure the GitHub Secret `FACTORIO_TOKEN`
4. Read all documents under `docs/`
5. Follow the rules in `.github/AI_RULES.md`

## Documentation Structure

- `README.md` - Template overview and quick start
- `AGENTS.md` - Repository boundary rules
- `.github/AI_RULES.md` - Mandatory AI collaboration rules
- `CONTRIBUTING.md` - Contribution guide
- `docs/SETUP.md` - Environment setup guide
- `docs/MOD_DEVELOPMENT.md` - Mod development conventions
- `docs/PUBLISHING.md` - Publishing workflow guide
- `docs/SECURITY_AND_PITFALLS.md` - Security guidance and common pitfalls
- `docs/TROUBLESHOOTING.md` - Troubleshooting guide
