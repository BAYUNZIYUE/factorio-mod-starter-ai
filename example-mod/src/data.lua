-- Data stage: Define prototypes (items, recipes, entities, etc.)
-- This runs during game startup, before the game world is created
-- Available: data:extend, data.raw
-- NOT available: game, script, remote (runtime APIs)

-- Example: Add a simple item
data:extend({
  {
    type = "item",
    name = "example-item",
    icon = "__base__/graphics/icons/iron-plate.png",
    icon_size = 64,
    subgroup = "raw-material",
    order = "a[example]",
    stack_size = 100
  }
})

-- Example: Modify an existing prototype
-- This is safe in data stage
if data.raw["item"]["iron-plate"] then
  -- Increase iron plate stack size
  data.raw["item"]["iron-plate"].stack_size = 200
end
