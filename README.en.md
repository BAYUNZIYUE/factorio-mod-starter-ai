# Factorio Mod Starter AI

[简体中文](README.md) | **English**

🤖 **An AI-optimized Factorio mod development template** with built-in packaging, publishing, and safety guidance.

---

## ✨ Features

- 🚀 **Automated Publishing**: Auto-package and publish to Mod Portal via GitHub Actions
- 🤖 **AI-Friendly**: Detailed boundary rules and stage constraints for AI-assisted development
- 📦 **Multi-Mod Support**: Develop multiple mods in one repository, publish selectively
- 📚 **Complete Documentation**: Setup guides, development specs, troubleshooting, and more
- 🔧 **Best Practices**: Follows Factorio modding conventions and stage boundaries
- 🎯 **Example Mod**: Fully functional example demonstrating proper structure

---

## 🚀 Quick Start

### 1. Use This Template

Click the "Use this template" button at the top of this page to create your own repository.

Or clone manually:

```bash
git clone https://github.com/your-username/factorio-mod-starter-ai.git my-mod-project
cd my-mod-project
rm -rf .git
git init
```

### 2. Create Your First Mod

```bash
# Copy example mod as starting point
cp -r example-mod/ my-awesome-mod/

# Edit mod info
vim my-awesome-mod/src/info.json
```

Update `info.json`:

```json
{
  "name": "my-awesome-mod",
  "version": "1.0.0",
  "factorio_version": "2.0",
  "title": "My Awesome Mod",
  "author": "Your Name",
  "description": "An awesome mod that does awesome things"
}
```

### 3. Test Packaging

```bash
export TARGET_MOD="my-awesome-mod"
export MOD_OUTPUT_DIR="./dist"
python3 pack_mods.py
```

### 4. Configure GitHub

1. Create GitHub repository
2. Configure `FACTORIO_TOKEN` Secret (see [Setup Guide](docs/SETUP.en.md))
3. Push code

### 5. Publish

```bash
git tag my-awesome-mod-v1.0.0
git push origin my-awesome-mod-v1.0.0

gh release create my-awesome-mod-v1.0.0 \
  --title "My Awesome Mod v1.0.0" \
  --notes "Initial release"
```

---

## ⚠️ Critical Warning

**Factorio Mod Portal does NOT support deletion:**

- ❌ Cannot delete mods once published
- ❌ Cannot delete versions once published
- ❌ Cannot retract releases

**When using AI assistance:**

- ⚠️ AI might accidentally trigger releases
- ⚠️ Test locally without configuring `FACTORIO_TOKEN`
- ⚠️ Manually publish first version to verify everything works
- ⚠️ Explicitly tell AI "do not create releases" during testing

See [Publishing Guide](docs/PUBLISHING.en.md) for detailed warnings and safe practices.

---

## 📁 Repository Structure

```
factorio-mod-starter-ai/
├── .github/
│   ├── AI_RULES.md              # AI collaboration rules (MANDATORY)
│   └── workflows/
│       └── publish-to-mod-portal.yml  # Auto-publish workflow
├── docs/
│   ├── SETUP.md                 # Environment setup
│   ├── MOD_DEVELOPMENT.md       # Development specs & stage boundaries
│   ├── PUBLISHING.md            # Publishing workflow
│   ├── SECURITY_AND_PITFALLS.md # Security & common pitfalls
│   └── TROUBLESHOOTING.md       # Common issues & solutions
├── example-mod/                 # Example mod
│   └── src/
│       ├── info.json            # Mod metadata
│       ├── settings.lua         # Settings stage
│       ├── data.lua             # Data stage
│       ├── control.lua          # Control stage
│       ├── changelog.txt
│       └── locale/en/locale.cfg
├── pack_mods.py                 # Packaging script
├── AGENTS.md                    # Repository boundary rules
├── CONTRIBUTING.md              # Contribution guide
└── README.md                    # This file
```

---

## 📖 Documentation

### For Developers

- [Setup Guide](docs/SETUP.en.md) - Configure environment and API keys
- [Mod Development](docs/MOD_DEVELOPMENT.en.md) - Directory structure, stage boundaries, best practices
- [Publishing Guide](docs/PUBLISHING.en.md) - How to publish to Mod Portal
- [Security & Pitfalls](docs/SECURITY_AND_PITFALLS.en.md) - Accounts, secrets, accidental releases, and leak prevention
- [Troubleshooting](docs/TROUBLESHOOTING.en.md) - Common issues and solutions

### For AI Assistants

- [AI_RULES.en.md](.github/AI_RULES.en.md) - **MANDATORY** rules for AI collaboration
- [AGENTS.en.md](AGENTS.en.md) - Repository boundary rules
- [Workflow Guide](.github/workflows/README.en.md) - CI/CD and publishing workflow notes

---

## 🎯 Factorio Stage Boundaries

**Critical concept for Factorio modding - violating these causes runtime errors:**

### Settings Stage (`settings.lua`)

**Can use:**
- `data:extend` (for settings only)

**Cannot use:**
- `game`, `script`, `remote` (runtime APIs)

### Data Stage (`data.lua`, `data-updates.lua`, `data-final-fixes.lua`)

**Can use:**
- `data:extend` (add prototypes)
- `data.raw` (read/write prototypes)
- `settings.startup` (read startup settings)

**Cannot use:**
- `game`, `script`, `remote` (runtime APIs)

### Control Stage (`control.lua`, `scripts/`)

**Can use:**
- `script` (event registration)
- `game` (game state access)
- `remote` (inter-mod communication)
- `settings.global`, `settings.player` (runtime settings)

**Cannot use:**
- `data:extend` (prototypes are locked)
- `data.raw` modifications (read-only)

**Common errors:**

```lua
-- ❌ WRONG: Using game in data stage
-- data.lua
if game.player then  -- ERROR: game is nil
  -- ...
end

-- ✅ CORRECT: Move to control stage
-- control.lua
script.on_event(defines.events.on_player_created, function(event)
  local player = game.get_player(event.player_index)
  -- ...
end)
```

See [MOD_DEVELOPMENT.en.md](docs/MOD_DEVELOPMENT.en.md) for detailed explanations.

---

## 🔧 Automated Publishing

### How It Works

1. **Create release** with tag format: `<mod-name>-v<version>`
2. **Workflow triggers** automatically
3. **Extracts mod name** from tag
4. **Packages mod** using `pack_mods.py`
5. **Uploads to Mod Portal** via API

### Tag Format

**Format:** `<mod-name>-v<version>`

**Examples:**
- ✅ `my-awesome-mod-v1.0.0`
- ✅ `another-mod-v2.1.0`
- ❌ `v1.0.0` (missing mod name)
- ❌ `my-mod_v1.0.0` (underscore instead of hyphen)

### Environment Variables

- `MOD_OUTPUT_DIR` - Packaging output directory
- `TARGET_MOD` - Specific mod to package (empty = all mods)
- `FACTORIO_TOKEN` - Factorio API Key (GitHub Secret)

---

## 🤖 AI-Assisted Development

This template is designed to work well with AI-assisted development and clear repository boundaries:

### Built-in AI Guardrails

- **Stage boundary rules** - Prevents AI from mixing data/control stage code
- **Naming conventions** - Enforces consistent naming patterns
- **Validation checks** - Catches common mistakes before packaging
- **Documentation** - Comprehensive guides for AI to reference

### Recommended AI Workflow

1. **Tell AI about stage boundaries** - Reference `.github/AI_RULES.en.md`
2. **Test locally first** - Don't configure `FACTORIO_TOKEN` during development
3. **Review AI changes** - Especially check stage boundaries
4. **Verify packaging** - Run `pack_mods.py` before publishing

### Common AI Mistakes to Watch For

- ❌ Using `game` API in data stage
- ❌ Modifying `data.raw` in control stage
- ❌ Creating releases during testing
- ❌ Incorrect tag format

---

## 🌍 Multi-Mod Workspace

Develop multiple mods in one repository:

### Add New Mod

```bash
mkdir my-new-mod
mkdir -p my-new-mod/src
# Create info.json, control.lua, data.lua, etc.
```

### Selective Publishing

Publish specific mod:

```bash
git tag my-new-mod-v1.0.0
git push origin my-new-mod-v1.0.0
```

Only `my-new-mod` will be packaged and published.

### Publish All Mods

Manually trigger workflow:

```bash
gh workflow run publish-to-mod-portal.yml
```

All mods will be packaged and published.

---

## 🛠️ Local Development

### Package Single Mod

```bash
export TARGET_MOD="example-mod"
export MOD_OUTPUT_DIR="./dist"
python3 pack_mods.py
```

### Package All Mods

```bash
export MOD_OUTPUT_DIR="./dist"
python3 pack_mods.py
```

### Verify Zip Structure

```bash
unzip -l dist/example-mod_1.0.0.zip
```

Should show:

```
example-mod_1.0.0/
├── info.json
├── control.lua
├── data.lua
├── settings.lua
├── changelog.txt
└── locale/en/locale.cfg
```

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.en.md](CONTRIBUTING.en.md) for guidelines.

### Ways to Contribute

- Fix documentation errors
- Improve example mod
- Enhance packaging script
- Add new documentation sections
- Report issues

---

## 📄 License

This template is licensed under MIT License. You can freely use, modify, and distribute.

Mod projects created using this template can use any license.

---

## 🙏 Acknowledgments

- Factorio development team for the excellent game and API
- Community for modding knowledge and best practices
- AI development tools for enabling better collaboration

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/BAYUNZIYUE/factorio-mod-starter-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/BAYUNZIYUE/factorio-mod-starter-ai/discussions)
- **Factorio Forums**: [Modding Help](https://forums.factorio.com/viewforum.php?f=82)

---

**Happy modding!** 🚂✨
