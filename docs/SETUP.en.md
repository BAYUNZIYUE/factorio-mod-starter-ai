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
   - `ModPortal: Publish Mods`
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

Only do this when you are ready for a real publish flow. For early testing, prefer local packaging only.

```bash
git tag example-mod-v1.0.0
git push origin example-mod-v1.0.0

gh release create example-mod-v1.0.0 \
  --title "Example Mod v1.0.0" \
  --notes "Initial release"
```

Then inspect GitHub Actions:

1. Open the **Actions** tab
2. Find **Publish to Factorio Mod Portal**
3. Confirm all steps passed

## Environment Variables

### `MOD_OUTPUT_DIR`

Packaging output directory.

- Default: `/home/factorio-mod-zips`
- CI: `${{ github.workspace }}/dist`
- Local: `./dist`

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

Common symptom: unauthorized upload failure.

Fix:

1. Add the `FACTORIO_TOKEN` secret
2. Confirm the key includes `ModPortal: Publish Mods`
3. Confirm the key is still valid

### First publish fails because the mod does not exist

Fix:

1. Create the mod page manually on https://mods.factorio.com/
2. Upload the first version manually
3. Use automation for later versions

## Next Steps

- Read [Mod Development](MOD_DEVELOPMENT.en.md)
- Read [Publishing Guide](PUBLISHING.en.md)
- Read [Troubleshooting](TROUBLESHOOTING.en.md)
