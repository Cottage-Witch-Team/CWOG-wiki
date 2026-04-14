# This Page Moved
Use: `wiki/customization/remove-balance-changes/index.md`

# Removing Changes

# Ars Nouveau

## Containment Jars

Located in `\Cottage Witch\kubejs\server_scripts\tags\entity_tags.js` labelled by `"ars_nouveau:jar_blacklist"`, this
file adds tags to entities that prevents them from being jarred in containment jars. Remove any entries on this list if
you want to be able to contain them again.

## Drygmies

Located in `\Cottage Witch\kubejs\server_scripts\tags\entity_tags.js` labelled by `"ars_nouveau:drygmy_blacklist"`, this
file adds tags to entities that prevents drygmies from getting drops from this entity.
> For example: "artifacts:mimic" is a part of this list. This means a Drygmy will not spawn loot that would drop from a
> mimic if it is nearby or in a containment jar.

# AE2

AE2 is a mod that does not thematically align with Cottage Witch. The mod was reskinned/renamed in an effort to match
the theme of Cottage Witch as much as possible. The crafting recipes were also altered in an effort to make the crafting
similar to Refined Storage. **You can find a guide for AE2 with these name changes in the quest book on the Storage
page.** Please also see this google sheet for name changes and which items are
disabled: https://docs.google.com/spreadsheets/d/19Y4Njg2MBKYcq7xsaS4VLc79Lw6JUeCSLle57f421RI/edit?gid=1940790781#gid=1940790781

## Remove name changes

Delete the file located here: `Cottage Witch\kubejs\assets\ae2\lang\en_us.json`

## Remove the custom recipes

Delete the files located here: `Cottage Witch\kubejs\server_scripts\recipes\ae2_recipes.js` and
`Cottage Witch\kubejs\server_scripts\recipes\recipe_removal_ae2.js`

**For versions 1.17.6 and up**
> Remove the AE2 disabled items list found in `\Cottage Witch\kubejs\startup_scripts\global\global_consts.js`.

# Spawn Egg Drop

## Drop Chance

Spawn Eggs have a chance to drop by killing a valid entity with a Reaper/Scythe. This is something completely custom
added by the Cottage Witch team. The base drop chance is 1%.

This can be updated in `\Cottage Witch\kubejs\server_scripts\loot_editing\mob_egg_drops.js` on the first line.

## Droppable Eggs

**For versions 1.17.6 and up**
> This list can be found in `\Cottage Witch\kubejs\startup_scripts\global\global_consts.js`.

**For versions 1.17.5 and below**
> This list can be found in `\Cottage Witch\kubejs\server_scripts\loot_editing\mob_egg_drops.js`

This list contains commented out spawn eggs along with a short reason as to why. To add these spawn eggs as a drop when
killing that mob remove the comment at the start of the line (the "//").

# Removed & Hidden Items

## Unobtainable Items

These are items that have no crafting recipe and are hidden in JEI.

**For versions 1.17.6 and up**
> This list can be found in `\Cottage Witch\kubejs\startup_scripts\global\global_consts.js`.

**For versions 1.17.5 and below**
> This list can be found in `\Cottage Witch\kubejs\server_scripts\recipes\recipe_removal.js`

To make these items craftable again, remove them from the list. To make these items appear in JEI, remove them from the
`\Cottage Witch\kubejs\client_scripts\jeihide.js` file
