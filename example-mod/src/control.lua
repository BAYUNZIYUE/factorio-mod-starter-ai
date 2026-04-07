-- Control stage: Runtime logic and event handlers
-- This runs when a save is loaded or a new game is started
-- Available: script, game, remote, rendering (runtime APIs)
-- NOT available: data:extend, data.raw modifications (prototypes are locked)

-- Example: Give items to new players
script.on_event(defines.events.on_player_created, function(event)
  local player = game.get_player(event.player_index)
  if not player then return end
  
  -- Give the player some example items
  player.insert({name = "example-item", count = 10})
  
  -- Print a welcome message
  player.print("Welcome! You received 10 example items.")
end)

-- Example: Read runtime settings
script.on_event(defines.events.on_runtime_mod_setting_changed, function(event)
  local player = game.get_player(event.player_index)
  if not player then return end
  
  -- Read a player setting (if defined in settings.lua)
  -- local setting_value = settings.get_player_settings(player)["example-mod-setting"].value
  
  player.print("Settings changed!")
end)

-- Example: Simple tick handler (use sparingly for performance)
-- script.on_nth_tick(60, function(event)
--   -- This runs once per second (60 ticks)
--   game.print("One second passed")
-- end)
