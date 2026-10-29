# Faction music slots

Drop a track into a faction's folder and the build names it and sets its volume.
Each faction can have its own theme, peace music and war music.

1. Make the folder `music/factions/<Faction>/`. The faction names are in the table below; upper or lower case both work.
2. Put an `.mp3` or `.ogg` file in it, with a mood word anywhere in the file name:
   - `Theme`: plays when you meet the faction and during its turns
   - `Peace`: plays while that faction is at peace
   - `War`: plays while that faction is at war
   - `Golden`, `Ambient`, `Victory` and `Defeat` also work.

   A file with no mood word becomes the faction's `Theme`.
3. Build the mod. For example, `Lordaeron Strings Peace.mp3` in `music/factions/Humans/` becomes
   `music/Humans - Lordaeron Strings - Peace.mp3`. Unciv looks for exactly that pattern:
   the name starts with the nation and ends with the mood. The build also lowers every track
   to the same gentle volume as the rest of the mod's music.

If a folder's name doesn't match any faction, the build skips it and logs a warning.

| Faction | Folder |
|---|---|
| Blood Elves | `music/factions/Blood Elves/` |
| Dark Iron Dwarves | `music/factions/Dark Iron Dwarves/` |
| Draenei | `music/factions/Draenei/` |
| Dwarves | `music/factions/Dwarves/` |
| Forsaken | `music/factions/Forsaken/` |
| Gnomes | `music/factions/Gnomes/` |
| Goblins | `music/factions/Goblins/` |
| High Elves | `music/factions/High Elves/` |
| Highmountain Tauren | `music/factions/Highmountain Tauren/` |
| Humans | `music/factions/Humans/` |
| Kul Tirans | `music/factions/Kul Tirans/` |
| Naga | `music/factions/Naga/` |
| Night Elves | `music/factions/Night Elves/` |
| Nightborne | `music/factions/Nightborne/` |
| Orcs | `music/factions/Orcs/` |
| Pandaren | `music/factions/Pandaren/` |
| Scourge | `music/factions/Scourge/` |
| Tauren | `music/factions/Tauren/` |
| Trolls | `music/factions/Trolls/` |
| Worgen | `music/factions/Worgen/` |
| Zandalari Trolls | `music/factions/Zandalari Trolls/` |
