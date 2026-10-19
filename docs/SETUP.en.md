# Setup Guide

[简体中文](SETUP.md) | **English**

This document explains how to configure your development environment and Factorio API key for automated publishing.

## Prerequisites

- Python 3.x
- Git
- A GitHub account
- A Factorio account

## Local Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. Test the packaging script

Package one mod:

```bash
export TARGET_MOD="example-mod"
export MOD_OUTPUT_DIR="./dist"
python3 pack_mods.py
```

Package all mods:

```bash
export MOD_OUTPUT_DIR="./dist"
python3 pack_mods.py
```

Verify the output:

```bash
ls -lh dist/
```

### 3. Verify zip structure

```bash
unzip -l dist/example-mod_1.0.0.zip
```

Expected structure:

```text
example-mod_1.0.0/
├── info.json
├── control.lua
├── data.lua
├── settings.lua
├── changelog.txt
└── locale/
    └── en/
        └── locale.cfg
```

The `name_version/` root folder inside the zip is a template convention. Mod Portal only enforces the zip filename format `{name}_{version}.zip`.

## Configure the Factorio API Key

Before continuing, read [Security & Pitfalls](SECURITY_AND_PITFALLS.en.md).

Especially remember:

- never commit a real `FACTORIO_TOKEN`
- do not configure real secrets too early during testing
- do not treat automated publishing like a harmless test action

### 1. Generate the API key

1. Visit https://factorio.com/profile
2. Sign in to your Factorio account
3. Find the **API Keys** section
4. Click **Generate new API key**
5. Enable:
   - `ModPortal: Publish Mods` (create a new mod)
   - `ModPortal: Upload Mods` (upload a new version of an existing mod)
   - `ModPortal: Edit Mods` (edit mod details, if needed)
6. Click **Create**
7. Copy the key immediately; it is shown only once

### 2. Add the secret in GitHub

1. Open your GitHub repository
2. Go to **Settings → Secrets and variables → Actions**
3. Click **New repository secret**
4. Add:
   - Name: `FACTORIO_TOKEN`
   - Secret: your API key

### 3. Verify the setup

**Do not use a release or tag to verify configuration.** Run `python3 pack_mods.py` and `python3 verify_mod.py` locally instead. A release triggers a real publish as soon as it is created, and Mod Portal versions cannot be deleted.

```bash
python3 verify_mod.py    # validate info.json, entrypoints, and layout
python3 pack_mods.py     # write the archive to dist/
```

Only configure the secret when you are actually ready for a formal release.

## Environment Variables

### `MOD_OUTPUT_DIR`

Packaging output directory.

- Default: `dist` (in the repository root)
- Override when needed, e.g. `export MOD_OUTPUT_DIR="./out"`
- CI also uses `dist/`

### `TARGET_MOD`

Name of the mod to package.

- Empty: package all mods
- Set: package only the named mod

### `FACTORIO_TOKEN`

Factorio API key used to upload to Mod Portal.

- Not needed for local packaging tests
- Required in CI for real publishing

## Common Setup Problems

### Packaging fails because no mod is found

Error:

```text
未找到任何模组目录（需要存在 <mod>/src/info.json）
```

Fix:

1. Ensure the directory layout is `<mod-name>/src/info.json`
2. Ensure `info.json` exists and is valid
3. Ensure at least one entrypoint file exists

### Packaging fails because fields are missing

Error:

```text
example-mod: info.json 缺少字段: author, description
```

Fix by adding the required fields in `info.json`.

### GitHub Actions fails because `FACTORIO_TOKEN` is missing

Common symptom: unauthorized upload failure (`init_publish/init_upload failed (HTTP 401)`).

Fix:

1. Add the `FACTORIO_TOKEN` secret
2. Confirm the key includes `ModPortal: Publish Mods` and `ModPortal: Upload Mods`
3. Confirm the key is still valid

### First publish fails because the mod does not exist

Fix:

- For a brand-new mod, the workflow calls `init_publish` and creates the mod page automatically; no manual step is required.
- If `Mod does not exist` still appears, the workflow is using `releases/init_upload` (valid only for existing mods), or the token lacks the matching scope (`Publish Mods` / `Upload Mods`). Check the token scopes and retry.
- As a fallback, create the page manually on https://mods.factorio.com/ with "Upload mod" and upload the first version there.

## Next Steps

- Read [Mod Development](MOD_DEVELOPMENT.en.md)
- Read [Publishing Guide](PUBLISHING.en.md)
- Read [Troubleshooting](TROUBLESHOOTING.en.md)
