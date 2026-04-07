# Security & Pitfalls Summary

[简体中文](SECURITY_AND_PITFALLS.md) | **English**

This document summarizes the biggest risks we hit while building and validating this template. Two goals matter most:

1. **Do not leak accounts, tokens, API keys, or publishing permissions**
2. **Do not let AI or automation publish test content to a platform that is hard to roll back**

---

## 1. Most Important Conclusions

### 1. Factorio Mod Portal publishing is effectively hard to undo

- Published mods should never be treated like disposable test artifacts
- Published versions cannot be deleted normally
- Recovery usually means publishing a fix, deprecating the bad version, or contacting support

That means: **do not treat “create release” as a casual test action.**

### 2. `FACTORIO_TOKEN` is a production-grade secret

If a repository has a real `FACTORIO_TOKEN` and an active publishing workflow, then all of these can trigger a real publish:

- AI creating a release by mistake
- a human pushing the wrong tag
- copying a command into the wrong repository
- publishing from the wrong branch or context

Treat this token as production access, not as normal configuration.

### 3. Test locally before testing in the cloud

Validate locally first:

- `info.json`
- directory structure
- generated zip contents
- tag naming

Only move to the release flow after these are correct.

---

## 2. Account and Secret Safety Rules

### Never commit these into the repository

- Factorio API keys
- GitHub personal access tokens
- temporary GitHub Actions credentials
- browser cookies
- `.env` files
- drafts containing real emails, usernames, or author identities
- raw curl commands containing sensitive headers

Especially dangerous patterns:

- `Authorization: Bearer ...`
- `FACTORIO_TOKEN=...`
- terminal history containing publishing commands
- screenshots of Actions logs

### Store secrets in GitHub Secrets only

Correct:

- add `FACTORIO_TOKEN` in **Settings → Secrets and variables → Actions**

Wrong:

- writing it into `README.md`
- placing it in `docs/`
- embedding it into shell scripts
- committing `.env`
- pasting it into AI prompts

### Do not hard-code real account metadata in the template

Use placeholders such as:

- `Your Name`
- `your-username`
- `your-repo`
- `your-mod`

Avoid leaving behind:

- real GitHub usernames
- real email addresses
- real Factorio author names
- outdated repository URLs copied from previous projects

### Screenshots and logs can leak information too

Common leak sources:

- GitHub Actions screenshots
- browser autofill account names
- terminal history
- account details visible in Mod Portal pages
- release pages showing organization or repository data

Mask them before sharing.

---

## 3. AI-Specific Risks

### AI may turn “explain the release flow” into “perform the release flow”

This is one of the most dangerous failure modes.

When you tell AI things like:

- “check how publishing works”
- “test the workflow”
- “review the release process”

some agents may go ahead and:

- create tags
- create GitHub releases
- trigger the workflow

Be explicit:

- “inspect only; do not create a release”
- “package locally only; do not trigger remote publishing”
- “do not push tags or create releases unless I explicitly authorize it”

### Do not give AI real publishing power during testing

Recommended approach:

- during development: **do not configure `FACTORIO_TOKEN`**
- add the real secret only when preparing a real release
- if you want to test workflow behavior, use a throwaway repo or a repo without real secrets

### Do not paste secrets directly into AI chats

Wrong:

- “Here is my API key, configure it for me.”
- “Here is my bearer token, test the upload.”

Correct:

- you add the secret manually in GitHub
- you only tell AI the variable name, not the value

---

## 4. Pitfalls We Actually Hit

### 1. Wrong assumption: Mod Portal content can be deleted later

It is safer to treat Mod Portal publishing as near-irreversible.

### 2. API endpoints are easy to get wrong

Confirmed endpoint:

- `https://mods.factorio.com/api/v2/mods/init_publish`

Common wrong guesses:

- `init_upload`
- old paths
- guessed v1/v2 variants

Lesson: always verify external API details against official docs.

### 3. First publish and later automated publishes are different

The first release often requires manually creating the mod page first.

Lesson: first release manually, later releases automatically.

### 4. Repository metadata can leak identities

Template repos often leak through metadata rather than code:

- old repo names in README files
- old author names in `info.json`
- real usernames in examples
- outdated links in docs

Lesson: audit every document, example, and metadata field, not just the code.

---

## 5. Recommended Safe Workflow

### Phase 1: development

- do not configure `FACTORIO_TOKEN`
- do not create releases
- do not push test tags
- package locally only

```bash
export TARGET_MOD="your-mod"
export MOD_OUTPUT_DIR="./dist"
python3 pack_mods.py
```

### Phase 2: pre-release review

Check:

- `info.json` version is correct
- `changelog.txt` is updated
- tag format is correct
- mod name matches directory name
- zip contents are correct
- docs do not leak tokens or old metadata
- the repo does not contain `.env`, screenshots, or sensitive logs

### Phase 3: first formal release

- verify repository and Mod Portal page setup manually
- verify secrets are configured correctly
- verify this is not just a test build
- prefer a manual first release

### Phase 4: later automated releases

Use automated tags, GitHub releases, and upload workflows only after the first release path is proven to work.

---

## 6. Pre-Commit and Pre-Release Checklist

Before committing:

- [ ] No token, cookie, `.env`, or key screenshot is being committed
- [ ] No real account names remain in examples
- [ ] No test command uses the wrong real repository by accident
- [ ] README/docs do not contain outdated repo names or stale links
- [ ] `FACTORIO_TOKEN` was not configured prematurely for testing
- [ ] No release was created just for a trial run

Before publishing:

- [ ] I understand Mod Portal content is not normally deletable
- [ ] This is not a test version
- [ ] Tag format is `<mod-name>-v<version>`
- [ ] Tag version matches `info.json`
- [ ] AI was not silently authorized to create releases on its own

---

## 7. One-Line Safety Prompt for AI

When you are about to discuss publishing with AI, prepend this instruction:

> Do local checks and packaging only. Do not create tags, do not create GitHub releases, and do not trigger any remote publish unless I explicitly authorize it.

This single sentence reduces accidental publishing risk significantly.

---

## 8. Read These Together

- `docs/SETUP.en.md` - environment setup and secret handling
- `docs/PUBLISHING.en.md` - publishing flow and non-deletion warning
- `.github/AI_RULES.en.md` - hard AI collaboration rules
- `AGENTS.en.md` - repository boundaries and working constraints
