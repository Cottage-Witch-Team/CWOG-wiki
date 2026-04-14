# AE2 Changes

AE2 was rethemed and partially rebalanced for Cottage Witch.

## Remove AE2 name changes

Delete:

`Cottage Witch\kubejs\assets\ae2\lang\en_us.json`

## Remove custom AE2 recipes

Delete:

- `Cottage Witch\kubejs\server_scripts\recipes\ae2_recipes.js`
- `Cottage Witch\kubejs\server_scripts\recipes\recipe_removal_ae2.js`

## Re-enable disabled AE2 items

For versions `1.17.6+`, edit:

`Cottage Witch\kubejs\startup_scripts\globals\global_consts.js`

Remove items from the AE2 disabled items list.
