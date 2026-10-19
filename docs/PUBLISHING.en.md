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
2. The first publish can be automated via `init_publish`; keep manual upload as a fallback
3. Test workflows in a safe repository without real secrets when possible
4. Explicitly tell AI not to create releases unless you authorize it

---

## Pre-Publish Checklist

- [ ] Update `src/info.json.version`
- [ ] Update `changelog.txt` (recommended, not required)
- [ ] Test the mod in-game
- [ ] Verify and package locally (`python3 verify_mod.py` + `python3 pack_mods.py`)
- [ ] Verify zip structure
- [ ] Configure `FACTORIO_TOKEN` only for a real publish

## Publishing a Single Mod (Recommended)

Use tag format `<mod-name>-v<version>`.

### Step 1: Update version information

Update `src/info.json`; update `changelog.txt` as well if you keep one (recommended).

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

# ⚠️ This publishes to Mod Portal for real; published versions cannot be deleted.
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

You no longer need to create the page manually first. The workflow checks whether the mod already exists: if not, it calls `init_publish` to create the mod and publish the first version.

### Step 1: verify and package locally

```bash
python3 verify_mod.py
export TARGET_MOD="your-new-mod"
python3 pack_mods.py
```

### Step 2: create the release

Make sure the token includes `ModPortal: Publish Mods` (create a new mod) and `ModPortal: Upload Mods` (later versions), then follow the normal tag/release flow. The workflow uses `init_publish` automatically.

### Step 3: manual fallback (optional)

If automatic creation fails because of permissions or platform issues, create the page manually:

1. Visit https://mods.factorio.com/
2. Sign in
3. Click **Upload mod**
4. Fill out the mod information
5. Upload the zip
6. Submit the form

Once the page exists, later versions use `releases/init_upload` automatically.

## Handling Failed Releases

### Wrong tag format

Delete the wrong tag and create a correctly formatted one.

### Version mismatch

The workflow runs `verify_mod.py --tag` before packaging and refuses to publish when they differ. You can also run `python3 verify_mod.py --target <mod-name> --tag <tag>` locally first.

### Mod does not exist

The workflow calls `init_publish` automatically for a new mod. If the error persists, check the token scopes, or create the initial mod page manually as a fallback.

### API key permission problems

Regenerate the key and enable `ModPortal: Publish Mods` and `ModPortal: Upload Mods` (add `ModPortal: Edit Mods` if you need to edit mod details).

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
3. Call `init_publish` for a new mod, or `releases/init_upload` for an existing mod
4. Upload the zip
5. Validate success

### Environment Variables

- `MOD_OUTPUT_DIR`
- `TARGET_MOD`
- `FACTORIO_TOKEN`

## Next Steps

- Read [Troubleshooting](TROUBLESHOOTING.en.md)
- Read the [Factorio Mod Portal API docs](https://wiki.factorio.com/Mod_publish_API)
