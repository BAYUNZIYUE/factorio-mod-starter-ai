# Workflow Guide

[简体中文](README.md) | **English**

This directory contains two GitHub Actions workflows.

## `verify.yml`

Runs on pushes to `main` and on pull requests, and never touches secrets:

1. `python3 verify_mod.py` validates all mod sources
2. packages `example-mod` as a smoke test
3. `python3 verify_mod.py --zip-dir dist` validates the zip layout

## `publish-to-mod-portal.yml`

Two jobs:

### `package` (always runs)

1. checkout: for a release, the **commit the tag points to**; for manual
   dispatch, the selected branch
2. parse the tag and validate `<mod-name>-v<major.minor.patch>`
3. `verify_mod.py --target <mod> --tag <tag>` checks that the directory name,
   `info.json`, and tag agree
4. package into `dist/`
5. validate the zip layout
6. upload the artifact

### `publish` (runs only when the upload condition is met)

1. download the artifact
2. `scripts/publish_mod.py` queries the Mod Portal:
   - mod missing → `init_publish` (scope `ModPortal: Publish Mods`)
   - mod exists → `releases/init_upload` (scope `ModPortal: Upload Mods`)
3. skips versions that already exist (idempotent, safe to retry)
4. queries releases again to confirm the version is visible

## Trigger modes

### 1. Release trigger

Publishing happens automatically when a non-prerelease GitHub Release is
published. Requirements:

- tag format `<mod-name>-v<major.minor.patch>`
- tag version matches `src/info.json` `version`
- prereleases never upload

### 2. Manual trigger

Click **Run workflow** in GitHub Actions:

| Input | Meaning |
|---|---|
| `target_mod` | required; only this mod directory is processed |
| `confirm` | empty = package only (dry-run); `PUBLISH` = actually upload |

`example-mod` is rejected and cannot be published manually.

## Approval and concurrency

- the `publish` job uses `environment: mod-portal-production`; configure
  required reviewers under Settings → Environments
- global `concurrency` serializes publishes so two jobs cannot hit the Mod
  Portal at the same time

## Key dependencies

- `pack_mods.py`, `verify_mod.py`, `scripts/publish_mod.py`
- GitHub Secret `FACTORIO_TOKEN` (grant `Publish Mods` / `Upload Mods` as needed)
- mod layout `<mod-name>/src/info.json`

## Risk warning

- with a real `FACTORIO_TOKEN`, a release publishes for real; Mod Portal
  versions cannot be deleted
- do not use releases/tags to test configuration; use `verify_mod.py` +
  `pack_mods.py` locally
- read `docs/PUBLISHING.en.md` and `docs/SECURITY_AND_PITFALLS.en.md` first

## Related documents

- [Publishing Guide](../../docs/PUBLISHING.en.md)
- [Security & Pitfalls](../../docs/SECURITY_AND_PITFALLS.en.md)
- [AI Collaboration Rules](../AI_RULES.en.md)
