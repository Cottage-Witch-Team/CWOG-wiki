# Changes Cottage Witch made to Sophisticated Backpacks
- Removed the Crafting Recipes for base backpacks
- Added base backpacks as loot in End Cities
- Removed backpacks as loot in other tables (dungeon, village, etc.)
- Removed the Crafting Recipes for Stack Upgrades beyond tier 1
- Removed the recipes for other upgrades
  - Advanced Deposit Upgrade
  - Advanced Pump Upgrade
  - Battery Upgrade
  - Deposit Upgrade
  - Inception Upgrade
  - Pump Upgrade
- Hide all removed recipes in JEI
- Slow players holding 2 or more backpacks

# Make Backpacks Appear as Normal Loot
In ⁨`Cottage Witch\kubejs\data`⁩ delete the **folder** named ⁨`sophisticatedbackpacks`⁩

***

# Make Backpacks Craftable 
In ⁨`Cottage Witch\kubejs\server_scripts\recipes`⁩ open ⁨`reciperemoval.js`⁩ in a text document editor of your choice. Then remove this line: ⁨`{ output: 'sophisticatedbackpacks:backpack' }`⁩

***

# Add recipes for Stack Upgrades
In ⁨`Cottage Witch\kubejs\server_scripts\recipes`⁩ open ⁨`reciperemoval.js`⁩ in a text document editor of your choice. Then remove these lines: ⁨```{ output: 'sophisticatedbackpacks:stack_upgrade_tier_2' },
{ output: 'sophisticatedbackpacks:stack_upgrade_tier_3' },
{ output: 'sophisticatedbackpacks:stack_upgrade_tier_4' },```⁩
## THEN to show these items in JEI again:
In ⁨`Cottage Witch\kubejs\client_scripts`⁩ open ⁨`jeihide.js`⁩ in a text document editor of your choice. Then remove these lines: ⁨```'sophisticatedbackpacks:stack_upgrade_tier_2',
'sophisticatedbackpacks:stack_upgrade_tier_3',
'sophisticatedbackpacks:stack_upgrade_tier_4',```⁩

***

# Re-add recipes for other Backback Upgrades
In ⁨`Cottage Witch\kubejs\server_scripts\recipes`⁩ open ⁨`reciperemoval.js`⁩ in a text document editor of your choice. Then remove these lines: ⁨```{ output: 'sophisticatedbackpacks:advanced_deposit_upgrade' },
{ output: 'sophisticatedbackpacks:advanced_pump_upgrade' },
{ output: 'sophisticatedbackpacks:battery_upgrade' },
{ output: 'sophisticatedbackpacks:deposit_upgrade' },
{ output: 'sophisticatedbackpacks:inception_upgrade' },
{ output: 'sophisticatedbackpacks:pump_upgrade' },```⁩

*Note: The ⁨`sophisticatedbackpacks:xp_pump_upgrade`⁩ is in this script, but has a custom recipe, and requires the original recipe to be removed!* **Thus, this line does not need to be removed** unless you would like to use the original recipe.

## THEN to show these items in JEI again:
In ⁨`Cottage Witch\kubejs\client_scripts`⁩ open ⁨`jeihide.js`⁩ in a text document editor of your choice. Then remove these lines: ⁨```'sophisticatedbackpacks:advanced_deposit_upgrade',
'sophisticatedbackpacks:advanced_pump_upgrade',
'sophisticatedbackpacks:battery_upgrade',
'sophisticatedbackpacks:deposit_upgrade',
'sophisticatedbackpacks:inception_upgrade',
'sophisticatedbackpacks:pump_upgrade',```⁩

***

# Slowness When Holding 2+ Backpacks
In your singleplayer files go to `Cottage Witch\saves\<YOUR_WORLDNAME>\serverconfig` and open `sophisitcatedbacks-server.toml` in a text document editor of your choice.

If you are managing a server, look for `<worldname>\serverconfig` instead.

Scroll down to the section labelled `[server.nerfs]` and change `tooManyBackpacksSlowness = true` to `tooManyBackpacksSlowness = false`

_Restart your game/server to apply this change._


***

# After Saving Changes
Re-log into the world or run ⁨`/reload`⁩!