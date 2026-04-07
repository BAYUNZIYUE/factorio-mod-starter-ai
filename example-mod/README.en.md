# Example Mod

[简体中文](README.md) | **English**

This sample mod demonstrates the basic structure and best practices for Factorio mod development.

## Features

- Adds a simple item called `Example Item`
- Gives new players 10 example items automatically
- Demonstrates correct Factorio stage-boundary usage
- Includes examples of startup, runtime-global, and per-player settings
- Includes localization support

## File Structure

```text
example-mod/
├── README.md
└── src/
    ├── info.json           # Mod metadata
    ├── settings.lua        # Settings stage definitions
    ├── data.lua            # Data stage prototype definitions
    ├── control.lua         # Control stage runtime logic
    ├── changelog.txt       # Version changelog
    └── locale/
        └── en/
            └── locale.cfg  # English localization
```

## Stage Boundaries

### Settings Stage (`settings.lua`)
- **Allowed**: define mod settings
- **Forbidden**: runtime APIs like `game` and `script`

### Data Stage (`data.lua`)
- **Allowed**: define and modify prototypes with `data:extend` and `data.raw`
- **Forbidden**: runtime APIs like `game` and `script`

### Control Stage (`control.lua`)
- **Allowed**: runtime logic and event handling
- **Forbidden**: modifying prototypes (`data.raw` is read-only here)

## How to Use It

1. Copy this directory as the starting point for a new mod
2. Update the mod metadata in `src/info.json`
3. Modify or remove the sample code as needed
4. Add your own features

## Development Tips

- All player-facing text should live in `locale/`
- Use `data-final-fixes.lua` when your changes must run after other mods
- Put complex runtime logic into `scripts/` to keep `control.lua` small
- If you rename prototypes, consider adding `migrations/` for save compatibility

## References

- [Factorio Lua API](https://lua-api.factorio.com/)
- [Data Lifecycle](https://lua-api.factorio.com/latest/Data-Lifecycle.html)
- [Modding Tutorial](https://wiki.factorio.com/Tutorial:Modding_tutorial)
