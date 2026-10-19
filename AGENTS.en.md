# AGENTS.md — Factorio Mod Starter AI

[简体中文](AGENTS.md) | **English**

This file is the single entry point for repository rules. Keep it short.
Read files under `docs/` only when needed; do not preload all documentation.

## What this repository is

A **Factorio mod development template**: multi-mod layout, packaging script,
GitHub Actions publishing, and AI collaboration constraints.
It is not a mod project. When you create a project from it, keep `AGENTS.md`
(it should be committed) and delete `example-mod/`.

Template vs. instance repository:

| Role | Location | Committed? |
|---|---|---|
| Project rules | `AGENTS.md` / `.github/AI_RULES.md` | yes |
| Personal environment notes (local paths, tokens, debugging notes) | `AGENTS.local.md` (already gitignored) | no |
| Build output | `dist/` | no (already in `.gitignore`) |

## Layout

```text
<mod-name>/
├── src/
│   ├── info.json              # required metadata (still needs one .lua entrypoint)
│   ├── control.lua            # runtime; game/rendering unavailable at top level
│   ├── data.lua               # prototypes; data-updates.lua / data-final-fixes.lua
│   ├── settings.lua           # settings; settings-updates.lua / settings-final-fixes.lua
│   ├── locale/<lang>/locale.cfg
│   ├── migrations/<mod-version>.lua   # filename is the MOD version
│   ├── scripts/               # runtime helpers
│   ├── prototypes/
│   ├── graphics/
│   └── changelog.txt          # recommended, not required; root dir also works, but not both
└── README.md
```

Hard rules:

- Directory name must equal `src/info.json` `name` (lowercase letters, digits,
  `-`, `_`, 3–50 characters)
- `version` must be `major.minor.patch`; `factorio_version` must be a two-part
  major version such as `"2.0"`
- Only `.lua` entrypoints are loaded. TypeScript must be compiled to `.lua`
  first with TypeScriptToLua; this template does not ship a build chain
- Only files under `src/` are packaged. Build output, temp files, `.git`,
  `node_modules`, `__pycache__`, `.DS_Store` are excluded
- `example-mod/` is excluded from packaging unless you pass
  `TARGET_MOD=example-mod` explicitly

## Stage boundaries (violating these breaks loading)

| Stage | Allowed | Forbidden |
|---|---|---|
| `settings*` | `data:extend` setting prototypes, `settings.startup` | `game`, `script`, runtime API |
| `data*` | `data:extend`, `data.raw`, prototype definitions/edits, `settings.startup` | `game`, `script`, `remote`, event registration |
| `control.lua` top level | `script` / `remote` / `commands` (registration), `settings.global`, `defines`, `log`, `require` | `game`, `rendering`, `data` (does not exist), `settings.get_player_settings` (needs a player) |
| Event handlers / `on_init` / `on_configuration_changed` | full runtime API, `game`, `rendering` | mutating prototypes (locked) |

Save load order: `control.lua` → `on_init` → migrations → `on_load` →
`on_configuration_changed` → event handlers.
`on_load` runs only for mods that were already part of the save (new saves/new
mods run `on_init` instead); `storage` is readable but not writable; `game` is
unavailable; the only legitimate uses are rebuilding metatables, re-registering
conditional handlers, and caching `storage` references.
`data` is **not accessible** in the control stage (it is not "read-only").

## Publishing (high risk, irreversible)

The Mod Portal has **no API to delete a published release**. Publishing requires
explicit authorization; never use a release/tag as a "test".

- Tag format: `<mod-name>-v<major.minor.patch>`, must match `src/info.json`
- First-time mod creation: `POST /api/v2/mods/init_publish`, token scope
  `ModPortal: Publish Mods`
- New release of an existing mod: `POST /api/v2/mods/releases/init_upload`,
  token scope `ModPortal: Upload Mods`
- The workflow checks whether the mod exists and picks the right endpoint;
  it skips versions that already exist (idempotent)
- It uploads only on a non-prerelease `release`, or on manual dispatch with
  `confirm=PUBLISH` and an explicit `target_mod`
- `FACTORIO_TOKEN` belongs in GitHub Secrets only; never commit it or print it

## Verification (definition of done)

```bash
python3 verify_mod.py                       # source: fields/name/version/entrypoint/changelog
TARGET_MOD="<mod>" python3 pack_mods.py     # package into dist/
python3 verify_mod.py --zip-dir dist        # zip: root dir/required files/junk/version
```

A change is done only when all three pass. CI runs the same checks on push/PR
(`.github/workflows/verify.yml`).

Notes:

- source verification includes `example-mod` by default (the template itself must
  stay valid); packaging excludes it unless `INCLUDE_EXAMPLE=1`
- `--zip-dir` only validates zips that already exist; run `pack_mods.py` first
- packaging does not clean old versions from `dist/`; clear it, or use
  `scripts/publish_mod.py --tag <tag>` when publishing (`pack_mods.py` has no
  `--tag` flag)
- do not run `scripts/publish_mod.py --all` locally; local publishing must use
  `--tag` after `verify_mod.py --zip-dir`

## Do not (without explicit authorization)

- Create a release, push a tag, or trigger a remote publish
- Write real tokens, passwords, or internal paths into tracked files
- Publish `example-mod/`
- Use runtime APIs in the `data` stage, or access `data` in the `control` stage
- Add `AGENTS.md` to `.gitignore` (it is project rule, not local state)

## Documentation on demand

| Need | Read |
|---|---|
| Setup from scratch | `docs/SETUP.en.md` |
| Layout/naming/stage details | `docs/MOD_DEVELOPMENT.en.md` |
| Publishing and troubleshooting | `docs/PUBLISHING.en.md` |
| Security and mis-publish risks | `docs/SECURITY_AND_PITFALLS.en.md` |
| Error lookup | `docs/TROUBLESHOOTING.en.md` |
| Full mandatory rules | `.github/AI_RULES.en.md` |
| CI behavior | `.github/workflows/README.en.md` |

## Known decisions

- Default output is `dist/` (not a fixed absolute path), identical locally and in CI
- `example-mod/` only demonstrates the layout and is excluded from publishing
- Bilingual docs use separate `*.en.md` files and must stay in sync. For facts
  (endpoints, fields, commands, CI behavior), code and workflows are the source
  of truth; fix the code first, then update both docs
- No headless smoke test is bundled; use `--mod-directory` with
  `--create`/`--dump-data` or the community FactorioTest when needed
