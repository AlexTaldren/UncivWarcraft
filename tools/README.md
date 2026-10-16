# UncivWarcraft

A standalone base ruleset that turns Unciv into the world of Warcraft: the races of Azeroth as playable factions, a tech tree that runs through Azeroth's history, and Warcraft wonders, units and resources.

**Status: early alpha.** The Humans are fully built out; the other races are playable with their own leaders, abilities and cities but share the common unit roster for now.

## What's in it

**Eras** follow Azeroth's timeline: Age of Tribes → Age of Arathor → Age of the Dark Portal → Age of the Third War → Age of the Lich King → Age of the Cataclysm → Age of the Legion → Age of Azerite → Age of the Void.

**14 races**, each with a leader, unique ability, AI personality and city list: Humans, Orcs, Night Elves, Dwarves, Gnomes, Tauren, Trolls, Blood Elves, High Elves, Pandaren, Forsaken, Draenei, Goblins, Worgen.

**Humans (complete)** — led by Anduin Wrynn
- *The Human Spirit:* City-State influence decays 50% slower and rests 20 higher; +15% Great Person generation.
- **Footman** (replaces Swordsman): stronger, starts with Cover I, needs no Iron.
- **Paladin** (replaces Knight): stronger, heals adjacent units (Medic).
- **Mage** (replaces Crossbowman): stronger ranged attack that fires over hills and forests.
- **Chapel of the Light** (replaces Temple): +1 Faith, +1 Culture.

**Azeroth world map** (104 × 64): Kalimdor, the Eastern Kingdoms and Northrend, with every major zone in its place (Elwynn Forest, the Barrens, Dun Morogh, Tanaris, Icecrown and 50+ more), mountain ranges, lakes, rivers, the Maelstrom, Kezan, the Lost Isles and the Wandering Isle. Each race starts at its capital: Stormwind City, Orgrimmar, Darnassus, Ironforge, Gnomeregan, Thunder Bluff, Sen'jin Village, Silvermoon City, Quel'Danas, the Wandering Isle, Undercity, the Exodar, Bilgewater Harbor and Gilneas City. City-states sit at their real locations. Select *Custom* map in a new game; Azeroth is preselected for this ruleset.

**12 city-states:** Dalaran, Theramore, Stromgarde, Gadgetzan, Booty Bay, Ratchet, Everlook, Steamwheedle Port, Light's Hope, Cenarion Hold, Argent Vanguard, Feathermoon.

**10 religions:** Holy Light, Elune, Earth Mother, Shamanism, Loa, Cenarion Circle, August Celestials, Titans, Forgotten Shadow, Light of the Sunwell.

**Warcraft names throughout:** ~40 techs (Runic Script, Alchemy, Seaforium, Mana Fission, Portal Networks…), 45 units (Peasant, Steam Tank, Gyrocopter, Mana Bomb, Iron Colossus…), 40 world wonders (Karazhan, Ulduar, Icecrown Citadel, Zul'Gurub…), resources (Thorium, Azerite, Mageweave, Truesilver…), 14 natural wonders (Mount Hyjal, Teldrassil, Un'Goro Crater, The Maelstrom…), and Great People named after Warcraft heroes.

## Installing

**In Unciv (any device):** open *Mods*, search for **UncivWarcraft** and press *Download*. Or use *Download mod from URL* and paste this repository's GitHub address.

**Desktop, manually:** download this repository as a ZIP, unzip it, rename the folder to `UncivWarcraft`, and put it in Unciv's `mods` folder.

Then start a new game, choose **UncivWarcraft** as the base ruleset, and pick the *Custom* map type: the Azeroth map is preselected.

## Building from source

The mod is generated from Unciv's own Gods & Kings ruleset by the scripts in [`tools/`](tools/TOOLS.md), so it can be rebuilt for new Unciv versions. Edit the data files there (races, names, map layout) rather than the generated JSON.

## Credits

Unit pixel art, tile art and most icons come from Unciv's own base game, re-labelled for the new names. The race emblems, religion symbols, Human unit icons and the Paladin and Mage map sprites are original to this mod.

Warcraft and World of Warcraft are trademarks of Blizzard Entertainment. This is a non-commercial fan project, not affiliated with or endorsed by Blizzard.
