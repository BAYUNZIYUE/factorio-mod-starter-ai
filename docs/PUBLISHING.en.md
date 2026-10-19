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

1. publish a fixed version with a higher version number (the old version cannot be overwritten; ship `1.0.1` to fix `1.0.0`)
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
git add your-mod/src/info.json
git add your-mod/src/changelog.txt   # or your-mod/changelog.txt if placed at the mod root
git commit -m "your-mod: Bump version to 1.0.1"
git push origin main
```

### Step 3: Create the tag and release

```bash
git tag your-mod-v1.0.1
git push origin your-mod-v1.0.1

# ⚠️ This publishes to Mod Portal for real; published versions cannot be deleted.
gh release create your-mod-v1.0.1 \
  --title "Example Mod v1.0.1" \
  --notes "Bug fixes and improvements"
```

### Step 4: Verify the publish

1. Open the **Actions** tab
2. Inspect **Publish to Factorio Mod Portal**
3. Confirm the **`Upload to Mod Portal` job actually ran and succeeded** (not skipped;
   dry-runs and prereleases skip it while the overall run still shows green)
4. Check the mod page and confirm the new version number is listed

## Publishing Multiple Mods

One release publishes one mod. For multiple mods, create one release per mod:

1. bump `info.json` for each mod (and update `changelog.txt`) and commit
2. create a tag/release per mod, for example `mod-a-v1.1.0` and `mod-b-v2.0.0`
3. each release triggers its own run for that mod only
4. confirm each run under Actions

To rehearse without publishing, dispatch with a target and leave `confirm`
empty (package only):

```bash
gh workflow run publish-to-mod-portal.yml -f target_mod=mod-a
```

> The `publish` job does not run: no Mod Portal query, no token needed, no publish
> script. The zip is still kept as a GitHub Actions artifact. A green run does not
> mean anything was published.

Then upload after checking the artifact (the `version` input must match
`info.json`):

```bash
gh workflow run publish-to-mod-portal.yml \
  -f target_mod=mod-a -f version=1.1.0 -f confirm=PUBLISH
```

## Tag Naming Rules

**Format:** `<mod-name>-v<version>`

Examples:

- ✅ `your-mod-v1.0.0`
- ✅ `another-mod-v2.1.0`
- ❌ `v1.0.0`
- ❌ `your-mod_v1.0.0`
- ❌ `your-mod-1.0.0`

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

- 401 = secret missing or invalid; regenerate and update `FACTORIO_TOKEN`
- 403 = valid key but wrong scope; regenerate the key and enable
  `ModPortal: Publish Mods` and `ModPortal: Upload Mods` (add
  `ModPortal: Edit Mods` if you edit details)

## Rolling Forward After a Bad Release

If a published version has a serious problem, publish a fixed follow-up version.

Remember: Mod Portal does not support normal deletion of published versions.

## How the Automation Works

### Triggers

1. Release published → package and publish one mod (the tagged commit)
2. Manual workflow dispatch → package/publish only `target_mod`; `confirm=PUBLISH` is required to upload

### Flow

1. Validate the tag/target against `info.json` (and, for dispatch, the `version` input)
2. Run `pack_mods.py`
3. Call `init_publish` for a new mod, or `releases/init_upload` for an existing mod
4. Upload the zip
5. Validate success

### Environment Variables

- `MOD_OUTPUT_DIR`: packaging output directory (local only; CI always uses `dist/`)
- `TARGET_MOD`
- `FACTORIO_TOKEN`

## Next Steps

- Read [Troubleshooting](TROUBLESHOOTING.en.md)
- Read the [Factorio Mod Portal API docs](https://wiki.factorio.com/Mod_publish_API)
