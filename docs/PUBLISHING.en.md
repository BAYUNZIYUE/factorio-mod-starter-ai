# Publishing Guide

[简体中文](PUBLISHING.md) | **English**

This document explains how to publish mods to the Factorio Mod Portal.

## ⚠️ Critical Warning

Read this before using automated publishing.

### Factorio Mod Portal does not support normal deletion of published content

- ❌ You cannot treat published mods like disposable test artifacts
- ❌ Published versions cannot simply be deleted
- ❌ Test releases cannot be casually rolled back

If you publish by mistake, your options are limited:

1. upload a replacement version
2. deprecate the bad version
3. contact official support and ask for help

### Extra caution when working with AI

This template is AI-friendly, but that also creates risk:

- AI may accidentally create a release during testing
- do not configure a real `FACTORIO_TOKEN` during early experimentation
- test with local packaging first
- verify mod name, version, and content before any formal release

### Safe practice recommendations

1. Keep testing local until you are ready
2. Prefer a manual first publish
3. Test workflows in a safe repository without real secrets when possible
4. Explicitly tell AI not to create releases unless you authorize it

---

## Pre-Publish Checklist

- [ ] Update `src/info.json.version`
- [ ] Update `changelog.txt`
- [ ] Test the mod in-game
- [ ] Test packaging locally
- [ ] Verify zip structure
- [ ] Confirm `FACTORIO_TOKEN` is configured only when needed

## Publishing a Single Mod (Recommended)

Use tag format `<mod-name>-v<version>`.

### Step 1: Update version information

Update `src/info.json` and `changelog.txt`.

### Step 2: Commit the changes

```bash
git add example-mod/src/info.json example-mod/src/changelog.txt
git commit -m "example-mod: Bump version to 1.0.1"
git push origin main
```

### Step 3: Create the tag and release

```bash
git tag example-mod-v1.0.1
git push origin example-mod-v1.0.1

gh release create example-mod-v1.0.1 \
  --title "Example Mod v1.0.1" \
  --notes "Bug fixes and improvements"
```

### Step 4: Verify the publish

1. Open the **Actions** tab
2. Inspect **Publish to Factorio Mod Portal**
3. Confirm all steps succeeded
4. Check the mod page on Mod Portal

## Publishing Multiple Mods

You can manually trigger the workflow to package and publish all mods.

### Step 1: Update versions for all relevant mods

### Step 2: Commit the changes

```bash
git add .
git commit -m "Bump versions for multiple mods"
git push origin main
```

### Step 3: Trigger the workflow manually

Web UI:

1. Open the workflow page in GitHub Actions
2. Click **Run workflow**
3. Select `main`
4. Run it

GitHub CLI:

```bash
gh workflow run publish-to-mod-portal.yml
```

## Tag Naming Rules

**Format:** `<mod-name>-v<version>`

Examples:

- ✅ `example-mod-v1.0.0`
- ✅ `another-mod-v2.1.0`
- ❌ `v1.0.0`
- ❌ `example-mod_v1.0.0`
- ❌ `example-mod-1.0.0`

Important:

- `<mod-name>` must exactly match the directory name
- `<version>` must match `info.json.version`
- the workflow extracts the mod name from the tag

## Versioning Rules

Use semantic versioning:

- `major` - breaking changes
- `minor` - backward-compatible features
- `patch` - backward-compatible fixes

## First Release of a New Mod

The first release often requires manually creating the Mod Portal page.

### Step 1: package locally

```bash
export TARGET_MOD="your-new-mod"
export MOD_OUTPUT_DIR="./dist"
python3 pack_mods.py
```

### Step 2: upload manually on Mod Portal

1. Visit https://mods.factorio.com/
2. Sign in
3. Click **Upload mod**
4. Fill out the mod information
5. Upload the zip
6. Submit the form

### Step 3: use automation for later versions

Once the mod page exists, later releases can use automated publishing.

## Handling Failed Releases

### Wrong tag format

Delete the wrong tag and create a correctly formatted one.

### Version mismatch

Ensure the tag version matches `info.json.version`.

### Mod does not exist

Create the initial mod page manually first.

### API key permission problems

Regenerate the key and ensure `ModPortal: Publish Mods` is enabled.

## Rolling Forward After a Bad Release

If a published version has a serious problem, publish a fixed follow-up version.

Remember: Mod Portal does not support normal deletion of published versions.

## How the Automation Works

### Triggers

1. Release published → package and publish one mod
2. Manual workflow dispatch → package and publish all mods

### Flow

1. Extract mod name from tag
2. Run `pack_mods.py`
3. Call `init_publish`
4. Upload the zip
5. Validate success

### Environment Variables

- `MOD_OUTPUT_DIR`
- `TARGET_MOD`
- `FACTORIO_TOKEN`

## Next Steps

- Read [Troubleshooting](TROUBLESHOOTING.en.md)
- Read the [Factorio Mod Portal API docs](https://wiki.factorio.com/Mod_publish_API)
