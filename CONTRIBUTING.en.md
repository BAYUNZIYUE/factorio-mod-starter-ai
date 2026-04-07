# Contributing Guide

[简体中文](CONTRIBUTING.md) | **English**

Welcome, and thanks for improving this template. This document explains how to use the template and how to contribute changes back to it.

## Using This Template

### Method 1: Use GitHub Template

1. Open this repository page
2. Click **Use this template**
3. Create your own repository
4. Clone it locally and start building

### Method 2: Copy Manually

```bash
git clone https://github.com/your-username/factorio-mod-starter-ai.git my-mod-project
cd my-mod-project
rm -rf .git
git init
git add .
git commit -m "Initial commit from template"
```

## Creating Your First Mod

### 1. Delete or Rework the Sample Mod

```bash
rm -rf example-mod/
```

Or copy it as a starting point:

```bash
cp -r example-mod/ my-awesome-mod/
```

### 2. Update Mod Metadata

Edit `my-awesome-mod/src/info.json`:

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

### 3. Implement Your Features

Modify the files you need:

- `settings.lua` - mod settings
- `data.lua` - prototype definitions
- `control.lua` - runtime logic
- `locale/` - localized text

### 4. Test Packaging

```bash
export TARGET_MOD="my-awesome-mod"
export MOD_OUTPUT_DIR="./dist"
python3 pack_mods.py
```

### 5. Configure GitHub

1. Create the GitHub repository
2. Add the `FACTORIO_TOKEN` secret
3. Push your code

### 6. Publish the First Version

```bash
git tag my-awesome-mod-v1.0.0
git push origin my-awesome-mod-v1.0.0

gh release create my-awesome-mod-v1.0.0 \
  --title "My Awesome Mod v1.0.0" \
  --notes "Initial release"
```

## Contributing Back to the Template

If you want to improve the template itself, pull requests are welcome.

### Good Contribution Areas

- Fix documentation gaps or unclear wording
- Improve the example mod
- Strengthen the packaging script
- Improve workflow reliability
- Add new documentation sections

### Pull Request Flow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/improve-docs`
3. Commit your changes: `git commit -m "Improve documentation"`
4. Push to your fork: `git push origin feature/improve-docs`
5. Open a pull request

### Style Guidelines

- Follow PEP 8 for Python
- Use 2-space indentation for Lua
- Use Markdown for documentation
- Write clear commit messages

## Mod Development Best Practices

### Naming

- Use kebab-case for mod directory names
- Keep the directory name identical to `info.json.name`
- Example: `my-awesome-mod`

### Versioning

- Use semantic versioning: `major.minor.patch`
- Update both `info.json` and `changelog.txt` before each release
- Use tag format: `<mod-name>-v<version>`

### Code Organization

- Keep `control.lua` small; move complex logic into `scripts/`
- Use `prototypes/` to organize prototype definitions
- Put all player-facing text into `locale/`

### Testing

- Test all features in-game
- Test compatibility with common mods where relevant
- Test old-save loading when prototype identifiers change

### Documentation

- Add a `README.md` in each mod directory
- Document features, settings, and known issues
- Provide screenshots or video demos if useful

## Multi-Mod Workspace Usage

This template supports multiple mods in a single repository.

### Add a New Mod

1. Create a new directory in the repository root
2. Follow the standard layout: `<mod-name>/src/info.json`
3. Test packaging: `TARGET_MOD="new-mod" python3 pack_mods.py`

### Publish One Specific Mod

```bash
git tag mod-a-v1.0.0
git push origin mod-a-v1.0.0
```

Only `mod-a` will be packaged and published.

### Publish All Mods

```bash
gh workflow run publish-to-mod-portal.yml
```

## AI Collaboration Rules

If you use AI assistants while building mods, follow `.github/AI_RULES.md`.

### Key Rules

- Do not change core naming conventions (tag format, directory layout)
- Do not change the API endpoint or environment variable names
- Respect Factorio stage boundaries strictly
- Always test packaging and publishing behavior after relevant changes

### Stage Boundaries Matter Most

- `settings.lua`: define settings only; never use `game` or `script`
- `data.lua`: define prototypes only; never use runtime APIs
- `control.lua`: runtime logic only; never mutate `data.raw`

Breaking these rules leads to runtime errors.

## Troubleshooting

When you hit a problem:

1. Read the [Troubleshooting Guide](docs/TROUBLESHOOTING.en.md)
2. Check GitHub Actions logs
3. Check the Factorio log file
4. Search issues for similar failures

## License

This template uses the MIT License. You may use, modify, and distribute it freely.

Mods created from this template may use any license you choose.

## References

- [Factorio Lua API](https://lua-api.factorio.com/)
- [Factorio Mod Portal API](https://wiki.factorio.com/Mod_publish_API)
- [Factorio Modding Tutorial](https://wiki.factorio.com/Tutorial:Modding_tutorial)
- [Data Lifecycle](https://lua-api.factorio.com/latest/Data-Lifecycle.html)

## Contact

- GitHub Issues - report bugs or request improvements
- GitHub Discussions - ask questions or discuss usage
- Factorio forums - share your modding experience

Thanks for using and improving this template.
