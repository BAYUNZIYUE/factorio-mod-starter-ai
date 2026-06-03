# AGENTS.md - Factorio Mod Template Repository Rules

[简体中文](AGENTS.md) | **English**

This file is the project-level persistent memory for this repository. This is a **Factorio mod development template repository** designed to help developers build and publish Factorio mods with AI assistance. New sessions entering the repository should read this file first, then `.github/AI_RULES.md` and the documents under `docs/`.

> **After cloning**: If you create your own mod project from this template, add this file (`AGENTS.md`) to `.gitignore` after cloning. In the template repository, AGENTS.md is a deliverable (version-controlled). In a concrete mod project, however, it is local, per-instance memory that should not sync across instances — your build environment, debugging experience, and project decisions should not be accidentally committed to Git history.

## Project Overview

This is a **Factorio mod development template repository**, not a specific mod project.

It provides:
- A complete multi-mod workspace structure
- Automated packaging script (`pack_mods.py`) and GitHub Actions publishing workflow
- AI collaboration rules (`.github/AI_RULES.md`) and repository boundary rules (this file)
- Development guides and best-practice documentation (`docs/`)
- Bilingual support (Chinese/English docs, README, contribution guide)

When creating a new project from this template, clone the repository and delete `example-mod/` to start developing.

## Tech Stack

- Factorio 2.0 mod development, primarily Lua with `*.lua` / `*.ts` entry point conventions
- Python 3 packaging script: `pack_mods.py`
- GitHub Actions: `.github/workflows/publish-to-mod-portal.yml` (auto-publish to Mod Portal)
- Documentation format: Markdown (Chinese/English bilingual)

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

## Architecture Guide

- `pack_mods.py` scans all root-level directories containing `src/info.json` and treats them as packageable mods
- Formal mods must be at the repository root using the `<mod-name>/src/` structure; the directory name should match the `name` field in `src/info.json`
- `example-mod/` is a sample shipped with the template, demonstrating the complete `<mod>/src/` structure and a minimal runnable entry point
- The template itself contains no actual mod business code; after cloning, users delete `example-mod/` and create their own mods following `<mod-name>/src/info.json`
- `.github/workflows/publish-to-mod-portal.yml` handles automatic publishing; `.github/AI_RULES.md` is the mandatory AI collaboration specification

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

## Build & Verification

- Package all mods: `python3 pack_mods.py`
- Package a single mod: `TARGET_MOD="<mod-name>" python3 pack_mods.py`
- Required `info.json` fields: `name`, `version`, `factorio_version`, `title`, `author`, `description`
- Each mod needs at least one entry point (`control`/`data`/`settings`) to package successfully
- After changing mod structure, packaging script, or publishing flow, re-verify packaging at minimum

## Project Tools

- `pack_mods.py`: Unified packaging entry point; default output at `MOD_OUTPUT_DIR`, fallback to `/home/factorio-mod-zips`; supports `TARGET_MOD` for single-mod packaging
- `.github/workflows/publish-to-mod-portal.yml`: Auto-packages and publishes to Factorio Mod Portal when a GitHub Release is created
- `.github/AI_RULES.md`: Mandatory rules for AI assistants, covering tag format, API endpoint, directory structure, and other non-negotiable items
- `docs/SETUP.md`: Complete guide for setting up a development environment from scratch
- `docs/MOD_DEVELOPMENT.md`: Mod development conventions, directory structure, and naming rules
- `docs/PUBLISHING.md`: Detailed workflow for manual and automatic mod publishing
- `docs/TROUBLESHOOTING.md`: Common issue troubleshooting guide

## Environment Configuration

- `TARGET_MOD`: Package only the specified mod; when empty, package all formal mods
- `MOD_OUTPUT_DIR`: Packaging output directory; script default is `/home/factorio-mod-zips`
- `FACTORIO_TOKEN`: API key required for publishing to Mod Portal (generate at https://factorio.com/profile, enable `ModPortal: Publish Mods`), configured as a GitHub Secret
- CI output convention is `dist/`; local development convention is `/home/factorio-mod-zips/`

## Conventions & Standards

- Document priority: `.github/AI_RULES.md` > `CONTRIBUTING.md` > `README.md` > this file
- Release tag format is fixed as `<mod-name>-v<version>`; do not modify
- Publishing API endpoint is fixed as `https://mods.factorio.com/api/v2/mods/init_publish`; do not change to `init_upload`
- Environment variable names `TARGET_MOD`, `MOD_OUTPUT_DIR`, `FACTORIO_TOKEN` must not be renamed
- `settings*` defines settings only; `data*` handles prototypes and `data.raw` only; `control.lua` / `scripts/` handles runtime API only
- Keep player-facing text in `locale/`; when adding settings, also add `mod-setting-name` and `mod-setting-description`
- Do not dump zip files, logs, screenshots, or temporary scripts in the repository root; put outputs under `artifacts/` or `dist/`
- Local cache directories like `.local/`, `.sisyphus/`, `.codex/` should never become deliverables

## Known Issues & Design Decisions

- `example-mod/` is a sample mod shipped with the template, not a deliverable. It demonstrates structure; users should delete or replace it after cloning
- Local packaging output (`/home/factorio-mod-zips/`) and CI output (`dist/`) intentionally differ: the fixed local path simplifies testing, while the CI temp directory avoids residue
- Bilingual documentation (Chinese primary, English translation) uses separate files (`*.en.md`) rather than an i18n directory to simplify GitHub rendering and contribution workflows
- The template does not include a headless smoke test workflow, as verification needs vary widely across mods; projects needing smoke tests can add their own GitHub Actions workflow or consult the Factorio modding community for existing solutions
