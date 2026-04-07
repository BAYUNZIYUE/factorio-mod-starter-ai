-- Settings stage: Define mod settings
-- This runs before data stage
-- Available: data:extend (for settings only)
-- NOT available: game, script (runtime APIs)

data:extend({
  -- Startup setting (requires game restart to change)
  {
    type = "bool-setting",
    name = "example-mod-enable-feature",
    setting_type = "startup",
    default_value = true,
    order = "a"
  },
  
  -- Runtime setting (can be changed during gameplay)
  {
    type = "int-setting",
    name = "example-mod-bonus-amount",
    setting_type = "runtime-global",
    default_value = 10,
    minimum_value = 1,
    maximum_value = 100,
    order = "b"
  },
  
  -- Per-player setting
  {
    type = "bool-setting",
    name = "example-mod-show-messages",
    setting_type = "runtime-per-user",
    default_value = true,
    order = "c"
  }
})
