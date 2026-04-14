# Spawn Egg Drop System

Spawn eggs can be dropped by killing valid mobs with a Reaper/Scythe.

## Change drop chance

File:

`Cottage Witch\kubejs\server_scripts\loot_editing\mob_egg_drops.js`

The base chance is defined at the top of the file (default was documented as `1%`).

## Change allowed egg list

For versions `1.17.6+`:

`Cottage Witch\kubejs\startup_scripts\globals\global_consts.js`

For versions `1.17.5 and below`:

`Cottage Witch\kubejs\server_scripts\loot_editing\mob_egg_drops.js`

Uncomment entries to make additional spawn eggs droppable.
