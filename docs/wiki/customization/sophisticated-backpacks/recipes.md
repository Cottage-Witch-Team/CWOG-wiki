# Recipe and JEI Changes

## Removed by default

- Base backpack recipe
- Stack upgrade recipes above tier 1
- Several utility upgrades:
  - `advanced_deposit_upgrade`
  - `advanced_pump_upgrade`
  - `battery_upgrade`
  - `deposit_upgrade`
  - `inception_upgrade`
  - `pump_upgrade`

## Re-enable crafting

Edit:

`Cottage Witch\kubejs\server_scripts\recipes\reciperemoval.js`

Remove the matching output-removal lines for the items you want back.

## Re-show in JEI

Edit:

`Cottage Witch\kubejs\client_scripts\jeihide.js`

Remove the corresponding hidden item IDs.

## Note on XP Pump Upgrade

`sophisticatedbackpacks:xp_pump_upgrade` has a custom recipe in the pack, so keep that in mind before restoring its original recipe.
