# Workflow Guide

[简体中文](README.md) | **English**

This directory contains GitHub Actions workflows used to package and publish Factorio mods.

## Current Workflow

### `publish-to-mod-portal.yml`

It is responsible for:

- packaging a specific mod when a GitHub Release is published
- packaging and publishing all mods when triggered manually
- uploading generated zip files to the Factorio Mod Portal

## Trigger Modes

### 1. Release trigger

When a GitHub Release is published, the workflow will:

1. extract the mod name from the tag
2. run `pack_mods.py` for that mod
3. upload the artifact using `FACTORIO_TOKEN`

Required tag format:

```text
<mod-name>-v<version>
```

### 2. Manual trigger

When you click **Run workflow** in GitHub Actions, the workflow will:

1. package all valid mods in the repository
2. upload them one by one to Mod Portal

## Key Dependencies

- `pack_mods.py`
- GitHub Secret: `FACTORIO_TOKEN`
- Correct mod structure: `<mod-name>/src/info.json`

## Risk Warning

- once a real `FACTORIO_TOKEN` is configured, this workflow can perform production publishing
- do not treat the workflow as a harmless test tool
- during testing, prefer not to configure real secrets
- read `docs/PUBLISHING.en.md` and `docs/SECURITY_AND_PITFALLS.en.md` before enabling real publishing

## Related Documents

- [Publishing Guide](../../docs/PUBLISHING.en.md)
- [Security & Pitfalls](../../docs/SECURITY_AND_PITFALLS.en.md)
- [AI Collaboration Rules](../AI_RULES.en.md)
