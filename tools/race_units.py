"""Unique units and buildings for the 13 non-Human races (v0.11), and their map sprites.

Each race gets two unique units and one unique building drawn from Warcraft lore,
following the Humans' template (wc_factions.HUMAN_UNITS / HUMAN_BUILDINGS): a base
unit or building to copy (by this mod's names) plus overrides.

Sprites start from the race's own version of the base sprite (race_sprites.make /
mounted), then add a few props drawn in code: pauldrons, banners, totems, kegs, hats,
glows. A handful (Abomination, Meat Wagon, Goblin Shredder, Glaive Thrower, Elven
Destroyer) are reworked more heavily. All art is original.
"""
import os
from PIL import Image, ImageDraw
import race_sprites as RS
import late_units as LU
from mounts import shade

P = "TileSets/AbsoluteUnits/Units/"


def _lore(*t):
    return [{"text": x} for x in t]


# (race, base unit (mod name), overrides) -- "replaces" and "uniqueTo" are filled in
UNITS = [
    # ---------------------------------------------------------------- Orcs
    ("Orcs", "Swordsman", {"name": "Grunt", "strength": 17,
        "addUniques": ["Heals [10] damage if it kills a unit"],
        "civilopediaText": _lore("The backbone of the Horde since the First War: big, green and armed with an axe nearly as heavy as the orc who swings it.",
                                 "Stronger than a Swordsman, and the thrill of battle heals 10 HP whenever it kills a unit.")}),
    ("Orcs", "Outrider", {"name": "Wolf Rider", "strength": 14,
        "dropUniques": ["[-33]% Strength <vs cities> <when attacking>"],
        "addUniques": ["No movement cost to pillage"],
        "civilopediaText": _lore("Orc raiders mounted on great wolves, the terror of the Alliance's farmlands since the Second War.",
                                 "Stronger than an Outrider, pillages without spending movement, and has no penalty attacking cities.")}),
    # ---------------------------------------------------------------- Trolls
    ("Trolls", "Ranger", {"name": "Headhunter", "strength": 9, "rangedStrength": 12,
        "addUniques": ["[+25]% Strength <when fighting in [Jungle] tiles>", "Double movement in [Jungle]"],
        "civilopediaText": _lore("Darkspear trolls who hurl barbed spears with deadly aim. At home in the jungles of Stranglethorn and the Echo Isles.",
                                 "Stronger than a Ranger, +25% Strength in jungle and moves through it at double speed.")}),
    ("Trolls", "Gyrocopter", {"name": "Batrider", "strength": 38, "rangedStrength": 40,
        "addUniques": ["[+33]% Strength <vs [Land] units>"],
        "civilopediaText": _lore("Troll riders on giant bats, dropping flasks of liquid fire on the enemy below.",
                                 "Stronger than a Gyrocopter, with +33% Strength against land units.")}),
    # ---------------------------------------------------------------- Tauren
    ("Tauren", "Vanguard", {"name": "Tauren Warrior", "strength": 25, "requiredResource": None,
        "civilopediaText": _lore("Towering warriors of Mulgore armed with great totems, fighting for the Earth Mother. Few things on Azeroth hit harder.",
                                 "Much stronger than a Vanguard and needs no Iron.")}),
    ("Tauren", "Mounted Archer", {"name": "Kodo Beast", "strength": 8, "rangedStrength": 10,
        "addUniques": ["[+10]% Strength bonus for [Military] units within [1] tiles"],
        "civilopediaText": _lore("A massive kodo carrying war drums and an archer. The beat of the drums drives the warriors around it forward.",
                                 "War Drums: nearby military units fight 10% harder.")}),
    # ---------------------------------------------------------------- Forsaken
    ("Forsaken", "Vanguard", {"name": "Abomination", "strength": 24, "requiredResource": None,
        "addUniques": ["[+15]% Strength <when defending>", "Heals [10] damage if it kills a unit"],
        "civilopediaText": _lore("A hulking construct of stitched-together corpses wielding a cleaver and hook, wrapped in a cloud of plague.",
                                 "Stronger than a Vanguard, needs no Iron, +15% Strength when defending, and heals 10 HP whenever it kills a unit.")}),
    ("Forsaken", "Catapult", {"name": "Meat Wagon", "strength": 8, "rangedStrength": 10, "movement": 3,
        "civilopediaText": _lore("A creaking cart that hurls plague-ridden corpses over city walls. It travels faster than any catapult.",
                                 "Stronger than a Catapult and has 3 movement.")}),
    # ---------------------------------------------------------------- Blood Elves
    ("Blood Elves", "Swordsman", {"name": "Spellbreaker", "strength": 16,
        "addUniques": ["[+25]% Strength <vs [Archery] units>"],
        "civilopediaText": _lore("Elite blood elf warriors trained to unravel enemy magic, armed with glaive and shield.",
                                 "Stronger than a Swordsman, with +25% Strength against archers and mages.")}),
    ("Blood Elves", "Knight", {"name": "Blood Knight", "strength": 22,
        "addUniques": ["Heals [15] damage if it kills a unit", "[+15]% Strength <when defending>"],
        "civilopediaText": _lore("The knights of Silvermoon, who once drew the Light from a captive naaru. They fight in crimson and gold.",
                                 "Stronger than a Knight, +15% Strength when defending, and heals 15 HP whenever it kills a unit.")}),
    # ---------------------------------------------------------------- Goblins
    ("Goblins", "Peasant", {"name": "Goblin Shredder", "movement": 3,
        "addUniques": ["[+1] Sight"],
        "civilopediaText": _lore("A walking lumber-machine with a goblin at the controls and a whirling saw for hands. It clears a forest faster than any peon.",
                                 "Moves 3 tiles per turn instead of 2, and sees farther.")}),
    ("Goblins", "Cannon", {"name": "Goblin Sapper", "strength": 14, "rangedStrength": 22,
        "renameUniques": {"[+200]% Strength <vs cities> <when attacking>": "[+250]% Strength <vs cities> <when attacking>"},
        "civilopediaText": _lore("Goblins with a barrel of blasting powder and no sense of self-preservation. Nothing knocks down walls quite like them.",
                                 "Stronger ranged attack than a Cannon, and +250% Strength attacking cities.")}),
    # ---------------------------------------------------------------- Dwarves
    ("Dwarves", "Musketeer", {"name": "Ironforge Rifleman", "strength": 27,
        "addUniques": ["[+25]% Strength <when fighting in [Hill] tiles>"],
        "civilopediaText": _lore("Dwarven riflemen of Ironforge, whose long rifles were the envy of the Alliance in the Second War.",
                                 "Stronger than a Musketeer, with +25% Strength in hills.")}),
    ("Dwarves", "Knight", {"name": "Ram Rider", "strength": 21,
        "dropUniques": ["No defensive terrain bonus"],
        "addUniques": ["[+25]% Strength <when fighting in [Hill] tiles>"],
        "civilopediaText": _lore("Dwarven cavalry on armored mountain rams, as sure-footed in the peaks of Dun Morogh as on the plain.",
                                 "Stronger than a Knight, keeps the defensive bonus of terrain, and gains +25% Strength in hills.")}),
    # ---------------------------------------------------------------- Gnomes
    ("Gnomes", "Outrider", {"name": "Mechanostrider Rider", "movement": 5, "requiredResource": None,
        "addUniques": ["[+1] Sight"],
        "civilopediaText": _lore("Gnomes mounted on mechanostriders: clockwork birds that never tire and never need feeding.",
                                 "Moves 5 tiles per turn, sees farther and needs no Horses.")}),
    ("Gnomes", "Mortar Team", {"name": "Gnomish Bombardier", "rangedStrength": 32, "range": 3,
        "civilopediaText": _lore("Gnomish artillery crews with a dangerous fondness for experimental shells.",
                                 "Stronger ranged attack than a Mortar Team, with range 3.")}),
    # ---------------------------------------------------------------- Night Elves
    ("Night Elves", "Outrider", {"name": "Huntress", "strength": 13,
        "addUniques": ["[+25]% Strength <when fighting in [Forest] tiles>", "Double movement in [Forest]"],
        "civilopediaText": _lore("Sentinels of the night elves riding nightsabers, each armed with a moonglaive.",
                                 "Stronger than an Outrider, with +25% Strength in forests and double movement through them.")}),
    ("Night Elves", "Ballista", {"name": "Glaive Thrower", "rangedStrength": 16, "range": 3,
        "civilopediaText": _lore("Night elf siege engines of living wood that hurl huge glaives at their targets.",
                                 "Stronger ranged attack than a Ballista, with range 3.")}),
    # ---------------------------------------------------------------- Draenei
    ("Draenei", "Vanguard", {"name": "Vindicator", "strength": 23,
        "addUniques": ["[+33]% Strength <vs [Barbarian] units>", "All adjacent units heal [+10] HP when healing"],
        "civilopediaText": _lore("Draenei paladins sworn to the Light and the naaru, enemies of the Burning Legion for thousands of years.",
                                 "Stronger than a Vanguard, +33% Strength against barbarians and demons, and adjacent units heal 10 HP more.")}),
    ("Draenei", "Knight", {"name": "Elekk Rider", "strength": 24, "movement": 3,
        "addUniques": ["[+15]% Strength <when defending>"],
        "civilopediaText": _lore("Draenei warriors mounted on armored elekks, slow but nearly unstoppable.",
                                 "Much stronger than a Knight and +15% Strength when defending, but moves 3 instead of 4.")}),
    # ---------------------------------------------------------------- Worgen
    ("Worgen", "Swordsman", {"name": "Worgen Stalker", "strength": 15, "requiredResource": None,
        "addUniques": ["[+25]% Strength <when fighting in [Forest] tiles>", "Double movement in [Forest]"],
        "civilopediaText": _lore("Gilneans who have embraced the curse of the worgen, hunting through the forests with tooth and claw.",
                                 "Stronger than a Swordsman, needs no Iron, +25% Strength in forests and double movement through them.")}),
    ("Worgen", "Rifleman", {"name": "Gilnean Rifleman", "strength": 37,
        "addUniques": ["[+1] Sight"],
        "civilopediaText": _lore("The disciplined riflemen of Gilneas, who held the Greymane Wall for years.",
                                 "Stronger than a Rifleman, and sees farther.")}),
    # ---------------------------------------------------------------- High Elves
    ("High Elves", "Ranger", {"name": "Farstrider", "rangedStrength": 13,
        "addUniques": ["[+1] Sight", "[+25]% Strength <when fighting in [Forest] tiles>"],
        "civilopediaText": _lore("The rangers of Quel'Thalas, who guard the elven forests with bow and blade.",
                                 "Stronger ranged attack than a Ranger, sees farther and gains +25% Strength in forests.")}),
    ("High Elves", "War Galley", {"name": "Elven Destroyer", "strength": 18, "rangedStrength": 20, "movement": 4,
        "civilopediaText": _lore("Swift elven warships, the best in the Alliance's fleets in the Second War.",
                                 "Stronger and faster than a War Galley.")}),
    # ---------------------------------------------------------------- Pandaren
    ("Pandaren", "Vanguard", {"name": "Brewmaster", "strength": 23, "requiredResource": None,
        "addUniques": ["[+20]% Strength <when defending>"],
        "civilopediaText": _lore("Pandaren fighters who mix the martial arts with a staff, a keg and a drunken, unpredictable style.",
                                 "Stronger than a Vanguard, needs no Iron, and +20% Strength when defending.")}),
    ("Pandaren", "Pikeman", {"name": "Shado-Pan Monk", "strength": 17, "movement": 3,
        "civilopediaText": _lore("The Shado-Pan, guardians of Pandaria's wall against the mantid and the Sha.",
                                 "Stronger than a Pikeman and moves 3 tiles per turn.")}),
]

UNITS += [
    # ---------------------------------------------------------------- Scourge
    ("Scourge", "Militia", {"name": "Ghoul", "strength": 10,
        "addUniques": ["Heals [10] damage if it kills a unit"],
        "civilopediaText": _lore("Ravenous undead raised by the plague, the foot soldiers of the Scourge.",
                                 "Stronger than Militia, and heals 10 HP whenever it kills a unit.")}),
    ("Scourge", "Peasant", {"name": "Acolyte",
        "civilopediaText": _lore("Living cultists of the Cult of the Damned, who serve the Lich King by raising buildings and spreading the blight.",
                                 "Like a Peasant; Acolytes spread the blight (Spread Blight) that Scourge buildings need.")}),
    ("Scourge", "Knight", {"name": "Death Knight", "strength": 24, "requiredResource": None,
        "addUniques": ["Heals [15] damage if it kills a unit"],
        "civilopediaText": _lore("Fallen champions raised by the Lich King, riding skeletal steeds and wielding runeblades.",
                                 "Much stronger than a Knight, needs no Horses, and heals 15 HP whenever it kills a unit.")}),
    ("Scourge", "Gryphon Rider", {"name": "Frost Wyrm", "strength": 52, "rangedStrength": 52,
        "addUniques": ["[+25]% Strength <vs [Land] units>"],
        "civilopediaText": _lore("The skeletal remains of great dragons, raised by Sapphiron's master and breathing killing frost.",
                                 "Stronger than a Gryphon Rider, with +25% Strength against land units.")}),
]

# (race, base building (mod name), overrides)
BLIGHT = "Must have an owned [Plagued Land] within [3] tiles"
BUILDINGS = [
    ("Scourge", "Town Hall", {"name": "Necropolis", "addStats": {"production": 1}, "addUniques": [BLIGHT],
        "civilopediaText": _lore("The Scourge's town hall: a dark citadel raised on blighted ground. +1 Production. Needs Plagued Land within 3 tiles.")}),
    ("Scourge", "Barracks", {"name": "Crypt", "addUniques": [BLIGHT],
        "civilopediaText": _lore("The crypt where the Scourge raises ghouls and trains its dead. Needs Plagued Land within 3 tiles.")}),
    ("Scourge", "Walls", {"name": "Ziggurat", "addStats": {"cityStrength": 3}, "addUniques": [BLIGHT],
        "civilopediaText": _lore("A spirit tower of the Scourge, stronger than ordinary walls. Needs Plagued Land within 3 tiles.")}),
    ("Orcs", "Shrine", {"name": "Altar of Storms", "addStats": {"culture": 1},
        "civilopediaText": _lore("The dark altar of the Horde, where Gul'dan's warlocks once worked their magic. Orc shamans now use it to gather power. +1 Culture, +1 Mana.")}),
    ("Orcs", "Granary", {"name": "Pig Farm", "addStats": {"production": 1},
        "civilopediaText": _lore("Orcish pig farms, a fixture of every Horde town since Warcraft II: pens of grunting boars feeding the warband. +1 Production.")}),
    ("Trolls", "Shrine", {"name": "Voodoo Lounge", "addStats": {"gold": 1, "culture": 1},
        "civilopediaText": _lore("A troll witch doctor's den, selling potions, charms and the blessings of the Loa. +1 Gold and +1 Culture.")}),
    ("Tauren", "Town Hall", {"name": "Great Totem", "addStats": {"faith": 1},
        "civilopediaText": _lore("A carved totem pole honoring the Earth Mother and the ancestors of the tribe. +1 Faith.")}),
    ("Forsaken", "Herb Garden", {"name": "Apothecarium", "addStats": {"science": 2},
        "civilopediaText": _lore("The laboratories of the Royal Apothecary Society, deep beneath the Undercity. +2 Science.")}),
    ("Blood Elves", "Arcane Sanctum", {"name": "Magisters' Sanctum", "addStats": {"science": 1, "culture": 1},
        "civilopediaText": _lore("A spire of Silvermoon where magisters study the arcane under the light of the sun. +1 Science and +1 Culture.")}),
    ("Goblins", "Market", {"name": "Goblin Bazaar", "addStats": {"gold": 2},
        "civilopediaText": _lore("A noisy goblin bazaar where anything can be bought, for a price. +2 Gold.")}),
    ("Dwarves", "Blacksmith", {"name": "Dwarven Forge", "addStats": {"production": 2},
        "civilopediaText": _lore("A dwarven forge in the tradition of Ironforge's Great Forge, its anvils ringing day and night. +2 Production.")}),
    ("Gnomes", "Workshop", {"name": "Tinker's Workshop", "addStats": {"science": 1},
        "civilopediaText": _lore("A gnomish workshop full of half-finished inventions, some of which even work. +1 Science.")}),
    ("Night Elves", "Shrine", {"name": "Moonwell", "addStats": {"food": 1},
        "civilopediaText": _lore("A pool of water blessed by Elune that restores those who drink from it. +1 Food.")}),
    ("Draenei", "Temple", {"name": "Crystal Sanctum", "addStats": {"science": 1},
        "civilopediaText": _lore("A draenei sanctuary of glowing crystal, raised in the image of the naaru. +1 Science.")}),
    ("Worgen", "Walls", {"name": "Gilnean Bulwark", "addStats": {"cityStrength": 3, "culture": 1},
        "civilopediaText": _lore("Massive Gilnean walls built in the tradition of the Greymane Wall. Stronger than ordinary walls, +1 Culture.")}),
    ("High Elves", "Walls", {"name": "Runestone", "addStats": {"cityStrength": 2, "science": 1},
        "civilopediaText": _lore("A runestone of Quel'Thalas, part of the magical barrier that protected the elves' lands. Stronger than ordinary walls, +1 Science.")}),
    ("Pandaren", "Granary", {"name": "Brewery", "addStats": {"gold": 1, "happiness": 1},
        "civilopediaText": _lore("A pandaren brewery in the Stormstout tradition, making ales that are famous across Azeroth. +1 Gold and +1 Happiness.")}),
]

ICONS_UNITS = {
    "Ghoul": ("skull", "fist"), "Acolyte": ("skull", "book"), "Death Knight": ("sword", "skull"),
    "Frost Wyrm": ("dragon", "skull"),
    "Grunt": ("axe", "fist"), "Wolf Rider": ("wolf", "axe"), "Headhunter": ("spear", "mask"),
    "Batrider": ("wing", "flame"), "Tauren Warrior": ("totem", "fist"), "Kodo Beast": ("drum", "bow"),
    "Abomination": ("skull", "chains"), "Meat Wagon": ("wheel", "skull"), "Spellbreaker": ("shield", "orb"),
    "Blood Knight": ("sword", "sun"), "Goblin Shredder": ("saw", "gear"), "Goblin Sapper": ("bomb", "flame"),
    "Ironforge Rifleman": ("gun", "mountain"), "Ram Rider": ("ram_head", "hammer"),
    "Mechanostrider Rider": ("gear", "boot"), "Gnomish Bombardier": ("cannon", "gear"),
    "Huntress": ("moon", "paw"), "Glaive Thrower": ("moon", "wheel"), "Vindicator": ("hammer", "naaru"),
    "Elekk Rider": ("shield", "crystal"), "Worgen Stalker": ("wolf", "moon"), "Gilnean Rifleman": ("gun", "lantern"),
    "Farstrider": ("bow", "leaf"), "Elven Destroyer": ("ship", "leaf"), "Brewmaster": ("chalice", "fist"),
    "Shado-Pan Monk": ("fist", "pagoda"),
}
ICONS_BUILDINGS = {
    "Necropolis": ("castle", "skull"), "Crypt": ("coffin", "skull"), "Ziggurat": ("ziggurat", "skull"),
    "Pig Farm": ("wheat", "tusk"), "Altar of Storms": ("ziggurat", "bolt"), "Voodoo Lounge": ("cauldron", "mask"), "Great Totem": "totem",
    "Apothecarium": ("flask", "skull"), "Magisters' Sanctum": ("spire", "sun"), "Goblin Bazaar": ("coins", "gear"),
    "Dwarven Forge": ("anvil", "flame"), "Tinker's Workshop": ("gears", "bolt"), "Moonwell": ("moon", "wave"),
    "Crystal Sanctum": ("crystals", "naaru"), "Gilnean Bulwark": ("castle", "wolf"), "Runestone": ("rune", "sparkle"),
    "Brewery": ("chalice", "wheat"),
}


# ======================================================================= sprites
def _part(size):
    im = Image.new("RGBA", size)
    return im, ImageDraw.Draw(im)


def _apply(ls, part, tint_layer=None):
    """Outline `part`, stamp it on the base; if tint_layer, also put it on that tint layer
    (so it takes the owner's colour)."""
    part = LU.outline(part)
    ls = LU.stamp(ls, part)
    if tint_layer:
        pp, lp = part.load(), ls[tint_layer].load()
        for y in range(part.height):
            for x in range(part.width):
                p = pp[x, y]
                if p[3] and p[:3] != LU.DARK:
                    g = max(p[:3])
                    lp[x, y] = (g, g, g, 255)
    return ls


def _glow(ls, color, draw):
    part, d = _part(ls[0].size)
    draw(d)
    g = LU.glow_of(part, color, 1.6, 1.2)
    out = Image.new("RGBA", ls[0].size)
    out.alpha_composite(g)
    out.alpha_composite(ls[0])
    out.alpha_composite(part)
    ls[0] = out
    return ls


ANCHOR = [0, 0]   # (head centre x, head top y), set by render() before the props are drawn


def _box(ls):
    """(x0, y0, x1, y1) around the head-and-shoulders of the figure, from ANCHOR."""
    cx, ty = ANCHOR
    return cx - 9, ty, cx + 9, ty + 40


def pauldrons(ls, col, spikes=False):
    x0, y0, x1, y1 = _box(ls)
    cx, top = (x0 + x1) // 2, y0
    part, d = _part(ls[0].size)
    for px_ in (cx - 7, cx + 5):
        d.ellipse([px_ - 3, top + 7, px_ + 3, top + 11], fill=col + (255,))
        if spikes:
            for k in (-2, 0, 2):
                d.line([(px_ + k, top + 7), (px_ + k, top + 4)], fill=(230, 222, 200, 255))
    return _apply(ls, part)


def back_banner(ls, pole=(95, 65, 40)):
    """A war banner on a pole strapped to the back, in the owner's colour."""
    x0, y0, x1, y1 = _box(ls)
    bx = x0 + 3
    part, d = _part(ls[0].size)
    d.line([(bx, y0 - 6), (bx, y0 + 16)], fill=pole + (255,), width=1)
    _apply(ls, part)
    flag, d2 = _part(ls[0].size)
    d2.polygon([(bx - 7, y0 - 6), (bx - 1, y0 - 6), (bx - 1, y0 + 3), (bx - 4, y0 + 1), (bx - 7, y0 + 3)], fill=(225, 225, 225, 255))
    return _apply(ls, flag, tint_layer=2)


def back_item(ls, kind):
    x0, y0, x1, y1 = _box(ls)
    bx, by = x0 + 3, y0 + 12
    part, d = _part(ls[0].size)
    if kind == "keg":
        d.ellipse([bx - 5, by - 1, bx + 3, by + 9], fill=(140, 90, 45, 255))
        for yy in (by + 2, by + 6):
            d.line([(bx - 5, yy), (bx + 3, yy)], fill=(90, 90, 95, 255))
    elif kind == "spears":
        for k in range(3):
            d.line([(bx - 4 + k * 2, by + 10), (bx - 1 + k * 2, by - 10)], fill=(120, 85, 50, 255))
            d.point((bx - 1 + k * 2, by - 11), fill=(200, 205, 210, 255))
    elif kind == "totem":
        d.rectangle([bx - 3, by - 14, bx + 1, by + 10], fill=(150, 100, 55, 255))
        for k, c in enumerate(((200, 60, 40), (60, 140, 200), (230, 200, 70))):
            d.rectangle([bx - 3, by - 13 + k * 6, bx + 1, by - 11 + k * 6], fill=c + (255,))
        d.polygon([(bx - 6, by - 14), (bx + 4, by - 14), (bx - 1, by - 18)], fill=(230, 222, 200, 255))
    elif kind == "bomb":
        d.ellipse([bx - 6, by - 2, bx + 3, by + 8], fill=(110, 75, 45, 255))
        d.text((bx - 4, by - 1), "", fill=(0, 0, 0, 255))
        d.rectangle([bx - 6, by + 2, bx + 3, by + 3], fill=(200, 40, 40, 255))
        d.line([(bx - 1, by - 2), (bx + 1, by - 6)], fill=(170, 150, 110, 255))
        d.point((bx + 1, by - 7), fill=(255, 220, 90, 255))
    elif kind == "cloak":
        d.polygon([(x0 + 5, y0 + 7), (x0 + 8, y0 + 7), (x0 + 6, y0 + 30), (x0 + 1, y0 + 28)], fill=(200, 200, 200, 255))
        return _apply(ls, part, tint_layer=1)
    return _apply(ls, part)


def headgear(ls, kind):
    x0, y0, x1, y1 = _box(ls)
    hx = (x0 + x1) // 2
    part, d = _part(ls[0].size)
    if kind == "horned_helm":
        d.ellipse([hx - 4, y0 - 1, hx + 4, y0 + 4], fill=(150, 150, 160, 255))
        d.line([(hx - 4, y0 + 1), (hx - 7, y0 - 3)], fill=(230, 222, 200, 255), width=2)
        d.line([(hx + 4, y0 + 1), (hx + 7, y0 - 3)], fill=(230, 222, 200, 255), width=2)
    elif kind == "crested_helm":
        d.ellipse([hx - 4, y0 - 1, hx + 4, y0 + 4], fill=(225, 190, 80, 255))
        d.line([(hx, y0 - 5), (hx + 1, y0)], fill=(240, 240, 255, 255), width=2)
    elif kind == "top_hat":
        d.rectangle([hx - 3, y0 - 6, hx + 3, y0 + 1], fill=(35, 35, 40, 255))
        d.line([(hx - 5, y0 + 1), (hx + 5, y0 + 1)], fill=(35, 35, 40, 255), width=1)
        d.line([(hx - 3, y0 - 1), (hx + 3, y0 - 1)], fill=(150, 40, 40, 255))
    elif kind == "straw_hat":
        d.polygon([(hx - 8, y0 + 2), (hx + 8, y0 + 2), (hx, y0 - 4)], fill=(215, 185, 110, 255))
    elif kind == "hood":
        d.pieslice([hx - 5, y0 - 2, hx + 5, y0 + 8], 180, 360, fill=(70, 130, 60, 255))
    elif kind == "goggles":
        d.line([(hx - 3, y0 + 3), (hx + 3, y0 + 3)], fill=(90, 200, 230, 255), width=2)
    elif kind == "cult_hood":
        d.pieslice([hx - 5, y0 - 2, hx + 5, y0 + 8], 180, 360, fill=(95, 50, 120, 255))
    elif kind == "crown":
        d.rectangle([hx - 4, y0 - 1, hx + 4, y0 + 1], fill=(235, 195, 70, 255))
        for k in (-4, 0, 4):
            d.line([(hx + k, y0 - 1), (hx + k, y0 - 4)], fill=(235, 195, 70, 255))
    elif kind == "red_hood":
        d.pieslice([hx - 5, y0 - 2, hx + 5, y0 + 8], 180, 360, fill=(170, 40, 35, 255))
    elif kind == "mask":
        d.rectangle([hx - 3, y0 + 1, hx + 4, y0 + 5], fill=(170, 120, 60, 255))
        d.point((hx + 2, y0 + 3), fill=(30, 20, 20, 255))
        d.line([(hx - 3, y0 - 2), (hx - 1, y0 + 1)], fill=(200, 60, 50, 255))
    return _apply(ls, part)


def weapon(ls, kind):
    x0, y0, x1, y1 = _box(ls)
    wx, wy = x1 - 1, y0 + 12
    part, d = _part(ls[0].size)
    if kind == "axe":
        d.line([(wx, wy + 14), (wx + 1, wy - 4)], fill=(110, 75, 45, 255), width=1)
        d.polygon([(wx + 1, wy - 5), (wx + 6, wy - 7), (wx + 6, wy + 1), (wx + 1, wy - 1)], fill=(185, 190, 200, 255))
    elif kind == "glaive":
        d.arc([wx - 3, wy - 6, wx + 7, wy + 4], 300, 120, fill=(215, 220, 235, 255), width=2)
        d.line([(wx + 2, wy - 1), (wx + 2, wy + 3)], fill=(110, 80, 60, 255))
    elif kind == "cleaver":
        d.polygon([(wx, wy), (wx + 6, wy - 2), (wx + 6, wy + 5), (wx, wy + 5)], fill=(170, 175, 180, 255))
        d.line([(wx - 1, wy + 5), (wx - 1, wy + 10)], fill=(100, 70, 50, 255), width=2)
    elif kind == "hammer":
        d.line([(wx, wy + 14), (wx + 1, wy - 3)], fill=(110, 75, 45, 255))
        d.rectangle([wx - 2, wy - 6, wx + 4, wy - 2], fill=(200, 175, 80, 255))
    elif kind == "staff":
        d.line([(wx, wy + 16), (wx + 1, wy - 8)], fill=(130, 90, 50, 255), width=1)
        d.ellipse([wx - 1, wy - 11, wx + 3, wy - 7], fill=(120, 80, 40, 255))
    elif kind == "totem_club":
        d.rectangle([wx - 1, wy - 8, wx + 3, wy + 6], fill=(150, 100, 55, 255))
        d.rectangle([wx - 1, wy - 6, wx + 3, wy - 4], fill=(200, 60, 40, 255))
        d.rectangle([wx - 1, wy - 1, wx + 3, wy + 1], fill=(60, 140, 200, 255))
    return _apply(ls, part)


def glow_aura(ls, color, where="weapon"):
    x0, y0, x1, y1 = _box(ls)
    if where == "weapon":
        return _glow(ls, color, lambda d: d.ellipse([x1 - 1, y0 + 4, x1 + 3, y0 + 8], fill=color + (255,)))
    return _glow(ls, color, lambda d: d.ellipse([(x0 + x1) // 2 - 2, y0 + 12, (x0 + x1) // 2 + 2, y0 + 16], fill=color + (255,)))


def recolor_metal(ls, col):
    """Re-dye grey metal (low saturation, bright) to `col`, keeping the shading."""
    return LU.recolor(ls, lambda h, s, v: s < 0.15 and v > 0.45,
                      lambda v: tuple(int(c * (0.55 + 0.6 * v)) for c in col))


# ---- heavier reworks
def abomination(ls):
    base, l1, l2 = RS.reshape(ls, 1.35, 1.08)
    ls = [base, l1, l2]
    ANCHOR[:] = _anchor(ls)
    LU.recolor(ls, lambda h, s, v: True if 0.02 <= h <= 0.2 and 0.15 <= s <= 0.6 else False,
               lambda v: tuple(int(c * (0.6 + 0.6 * v)) for c in (150, 165, 135)))
    x0, y0, x1, y1 = LU.bbox_all(ls)
    part, d = _part(base.size)
    for k in range(3):                                   # stitches across the belly
        yy = y0 + 16 + k * 6
        d.line([(x0 + 6, yy), (x1 - 6, yy + 1)], fill=(60, 40, 40, 255))
        for xx in range(x0 + 7, x1 - 6, 3):
            d.line([(xx, yy - 1), (xx, yy + 2)], fill=(60, 40, 40, 255))
    ls = LU.stamp(ls, part)
    ls = weapon(ls, "cleaver")
    return _glow(ls, (140, 220, 80), lambda d: [d.ellipse([x0 + 2 + i * 7, y0 + 6 + (i % 2) * 5, x0 + 4 + i * 7, y0 + 8 + (i % 2) * 5],
                                                         fill=(150, 230, 90, 140)) for i in range(4)])


def meat_wagon(ls):
    LU.recolor(ls, lambda h, s, v: 0.04 <= h <= 0.14 and s > 0.3, lambda v: tuple(int(c * (0.5 + 0.6 * v)) for c in (90, 85, 70)))
    x0, y0, x1, y1 = LU.bbox_all(ls)
    part, d = _part(ls[0].size)
    for i, (dx, dy) in enumerate(((4, 14), (10, 12), (16, 14), (8, 9))):
        d.ellipse([x0 + dx, y0 + dy, x0 + dx + 6, y0 + dy + 4], fill=(150, 160, 130, 255))
    d.ellipse([x0 + 12, y0 + 6, x0 + 16, y0 + 10], fill=(225, 215, 190, 255))     # a skull on top
    ls = _apply(ls, part)
    return _glow(ls, (140, 220, 80), lambda d: d.ellipse([x0 + 6, y0 + 4, x0 + 20, y0 + 10], fill=(150, 230, 90, 90)))


def glaive_thrower(ls):
    LU.recolor(ls, lambda h, s, v: 0.04 <= h <= 0.14 and s > 0.3, lambda v: tuple(int(c * (0.55 + 0.6 * v)) for c in (150, 120, 170)))
    x0, y0, x1, y1 = LU.bbox_all(ls)
    part, d = _part(ls[0].size)
    d.arc([x0 + 2, y0 - 2, x0 + 14, y0 + 10], 200, 20, fill=(220, 225, 240, 255), width=2)
    return _apply(ls, part)


def elven_destroyer(ls):
    LU.recolor(ls, lambda h, s, v: s < 0.25 and v > 0.6, lambda v: tuple(int(c * (0.7 + 0.35 * v)) for c in (235, 235, 225)))
    x0, y0, x1, y1 = LU.bbox_all(ls)
    part, d = _part(ls[0].size)
    d.polygon([(x0 + 14, y0 + 1), (x0 + 22, y0 + 3), (x0 + 14, y0 + 5)], fill=(70, 150, 70, 255))
    d.line([(x0 + 4, y1 - 12), (x1 - 4, y1 - 12)], fill=(220, 180, 70, 255))
    return _apply(ls, part)


def shredder():
    """A goblin shredder: a two-legged lumber machine with a saw arm and a goblin pilot."""
    def f(p):
        GR, GRD = (110, 110, 118), (80, 80, 88)
        p.ell(73, 59, 12, 2, (0, 0, 0), "shadow")
        for x, b in ((67, -2), (79, 2)):
            p.line(x, 40, x + b, 50, 3, GRD, "leg%d" % x)
            p.line(x + b, 50, x, 57, 3, GRD, "shin%d" % x)
            p.line(x - 3, 58, x + 3, 58, 2, (60, 60, 66), "foot%d" % x)
        p.poly([(63, 26), (83, 26), (82, 42), (64, 42)], GR, "body")
        p.poly([(66, 30), (80, 30), (79, 38), (67, 38)], (220, 220, 220), "plate", layer=2)
        p.ell(73, 22, 5, 4, (90, 150, 60), "pilot")                   # the goblin pilot
        p.dot(75, 21, (240, 230, 90), "eye")
        p.line(70, 19, 66, 16, 1, (90, 150, 60), "ear")
        p.line(77, 19, 81, 16, 1, (90, 150, 60), "ear2")
        p.line(84, 30, 90, 34, 3, GRD, "arm")
        p.ell(91, 35, 4, 4, (200, 205, 210), "saw")
        p.line(62, 30, 57, 38, 3, GRD, "arm2")
        p.line(60, 24, 60, 14, 2, (70, 70, 76), "stack")
    def lit(p):
        p.ell(60, 11, 2, 1.5, (190, 190, 190), "smoke")
    return LU.paint_layers((95, 81), f, ((lit, (200, 200, 200)),))


# per unit: (source sprite, race used to dress it, mode, list of prop steps)
SPRITES = {
    "Ghoul": ("Warrior", "Scourge", "full", [lambda l: pauldrons(l, (90, 95, 110), spikes=True)]),
    "Acolyte": ("Worker", "Scourge", "full", [lambda l: headgear(l, "cult_hood")]),
    "Death Knight": ("Knight", "Scourge", "mounted", [back_banner, lambda l: glow_aura(l, (140, 210, 255))]),
    "Wisp": (None, None, "paint", [lambda: wisp()]),
    "Gilnean Hunter": ("Composite Bowman", None, "raw", [lambda l: headgear(l, "top_hat")]),
    "Worgen Ravager": ("Swordsman", "Worgen", "full", [lambda l: pauldrons(l, (60, 55, 50), spikes=True), lambda l: back_item(l, "cloak")]),
    "Grunt": ("Swordsman", "Orcs", "full", [lambda l: pauldrons(l, (70, 60, 55), spikes=True), lambda l: weapon(l, "axe")]),
    "Wolf Rider": ("Horseman", "Orcs", "mounted", [back_banner]),
    "Headhunter": ("Composite Bowman", "Trolls", "full", [lambda l: back_item(l, "spears"), lambda l: headgear(l, "mask")]),
    "Tauren Warrior": ("Swordsman", "Tauren", "full", [lambda l: weapon(l, "totem_club"), lambda l: pauldrons(l, (120, 80, 45))]),
    "Kodo Beast": ("Chariot Archer", "Tauren", "mounted", [back_banner]),
    "Abomination": ("Swordsman", "Forsaken", "full", [abomination]),
    "Meat Wagon": ("Catapult", "Forsaken", "crew", [meat_wagon]),
    "Spellbreaker": ("Swordsman", "Blood Elves", "full", [lambda l: pauldrons(l, (215, 180, 70)), lambda l: weapon(l, "glaive"),
                                                          lambda l: glow_aura(l, (140, 230, 90))]),
    "Blood Knight": ("Knight", "Blood Elves", "mounted", [back_banner, lambda l: glow_aura(l, (255, 200, 90))]),
    "Goblin Shredder": (None, None, "paint", [shredder]),
    "Goblin Sapper": ("Scout", "Goblins", "full", [lambda l: back_item(l, "bomb"), lambda l: headgear(l, "goggles")]),
    "Ironforge Rifleman": ("Musketman", "Dwarves", "full", [lambda l: headgear(l, "horned_helm")]),
    "Ram Rider": ("Knight", "Dwarves", "mounted", [back_banner]),
    "Mechanostrider Rider": ("Horseman", "Gnomes", "mounted", [lambda l: headgear(l, "goggles")]),
    "Gnomish Bombardier": ("Artillery", "Gnomes", "full", [lambda l: headgear(l, "goggles")]),
    "Huntress": ("Horseman", "Night Elves", "mounted", [lambda l: weapon(l, "glaive"), lambda l: glow_aura(l, (170, 200, 255))]),
    "Glaive Thrower": ("Trebuchet", "Night Elves", "crew", [glaive_thrower]),
    "Vindicator": ("Swordsman", "Draenei", "full", [lambda l: headgear(l, "crested_helm"), lambda l: weapon(l, "hammer"),
                                                        lambda l: glow_aura(l, (255, 230, 140))]),
    "Elekk Rider": ("Knight", "Draenei", "mounted", [back_banner]),
    "Worgen Stalker": ("Swordsman", "Worgen", "full", [lambda l: back_item(l, "cloak")]),
    "Gilnean Rifleman": ("Rifleman", "Worgen", "full", [lambda l: headgear(l, "top_hat")]),
    "Farstrider": ("Composite Bowman", "High Elves", "full", [lambda l: headgear(l, "hood"), lambda l: back_item(l, "cloak")]),
    "Elven Destroyer": ("Galleass", None, "ship", [elven_destroyer]),
    "Brewmaster": ("Spearman", "Pandaren", "full", [lambda l: back_item(l, "keg"), lambda l: headgear(l, "straw_hat"),
                                                         lambda l: weapon(l, "staff")]),
    "Shado-Pan Monk": ("Pikeman", "Pandaren", "full", [lambda l: headgear(l, "red_hood")]),
}


def _anchor(ls):
    """Head centre: the first solid run from the top that sits over the figure's feet
    (so raised weapons, banners and shields are skipped)."""
    base = ls[0]
    a = base.split()[3].load()
    x0, y0, x1, y1 = base.getbbox()
    feet = [x for x in range(x0, x1) for y in range(y1 - 4, y1) if a[x, y] > 128]
    fx = sum(feet) / len(feet) if feet else (x0 + x1) / 2
    for y in range(y0, y0 + (y1 - y0) // 2):
        runs, run = [], []
        for x in range(x0, x1 + 1):
            if x < x1 and a[x, y] > 128:
                run.append(x)
            elif run:
                runs.append(run); run = []
        good = [r for r in runs if len(r) >= 4 and abs((r[0] + r[-1]) / 2 - fx) <= 7 and all(
            sum(a[x, y + k] > 128 for x in range(r[0], r[-1] + 1)) >= len(r) - 1 for k in (1, 2, 3))]
        if good:
            r = min(good, key=lambda r: abs((r[0] + r[-1]) / 2 - fx))
            return (r[0] + r[-1]) // 2, y
    return int(fx), y0


def wisp():
    """A wisp: a glowing spirit orb with a trailing tail of light."""
    def f(p):
        pass
    def lit(p):
        p.ell(73, 44, 5, 5, (190, 240, 255), "orb")
        p.ell(73, 44, 2.5, 2.5, (250, 255, 255), "core")
        for i in range(1, 6):
            p.ell(73 - i * 2.2, 47 + i * 1.6, 3.2 - i * 0.45, 2.4 - i * 0.35, (150, 220, 255), "tail%d" % i)
        for x, y in ((68, 38), (79, 41), (77, 50)):
            p.dot(x, y, (220, 250, 255), "spark%d%d" % (x, y))
    return LU.paint_layers((95, 81), f, ((lit, (140, 220, 255)),))


def render(atlas, name):
    src, race, mode, steps = SPRITES[name]
    if mode == "paint":
        ls = None
    elif mode == "raw":
        ls = LU.source_layers(atlas, src)
    elif mode == "mounted":
        ls = RS.mounted(atlas, [atlas.crop(P + src + s) for s in ("", "-1", "-2")], race, src)
    elif mode == "ship":
        ls = [atlas.crop(P + src + s) for s in ("", "-1", "-2")]
    else:
        ls = RS.make(LU.source_layers(atlas, src), race, src, mode)
    ls = [l.copy() for l in ls] if ls else None
    if ls:
        ANCHOR[:] = _anchor(ls)
    for step in steps:
        ls = step(ls) if ls is not None else step()
    return ls


def write_all(atlas, images_dir):
    n = 0
    for name in list(SPRITES) + list(_PAINTED_RENDER):
        layers = _PAINTED_RENDER[name](atlas) if name in _PAINTED_RENDER else render(atlas, name)
        for s, im in zip(("", "-1", "-2"), layers):
            path = os.path.join(images_dir, P, name + s + ".png")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            im.save(path)
            n += 1
    return n


# ======================================================================= heroes (v0.12)
def _hero(src, race, mode, props, glow):
    return (src, race, mode, list(props) + [lambda l: headgear(l, "crown"), lambda l: glow_aura(l, glow, "body")])

HERO_SPRITES = {
    "Uther the Lightbringer": _hero("Swordsman", None, "raw", [lambda l: weapon(l, "hammer")], (255, 225, 130)),
    "Grom Hellscream": _hero("Swordsman", "Orcs", "full", [lambda l: weapon(l, "axe"), lambda l: pauldrons(l, (60, 50, 45), spikes=True)], (255, 120, 80)),
    "Malfurion Stormrage": _hero("Spearman", "Night Elves", "full", [lambda l: weapon(l, "staff"), lambda l: headgear(l, "horned_helm")], (140, 255, 160)),
    "Muradin Bronzebeard": _hero("Swordsman", "Dwarves", "full", [lambda l: weapon(l, "hammer")], (150, 210, 255)),
    "Kelsey Steelspark": _hero("Scout", "Gnomes", "full", [lambda l: headgear(l, "goggles")], (255, 200, 120)),
    "Baine Bloodhoof": _hero("Swordsman", "Tauren", "full", [lambda l: weapon(l, "totem_club")], (255, 210, 140)),
    "Rokhan": _hero("Spearman", "Trolls", "full", [lambda l: headgear(l, "mask"), lambda l: back_item(l, "spears")], (160, 255, 170)),
    "Kael'thas Sunstrider": _hero("Spearman", "Blood Elves", "full", [lambda l: weapon(l, "staff")], (255, 150, 60)),
    "Alleria Windrunner": _hero("Composite Bowman", "High Elves", "full", [lambda l: back_item(l, "cloak")], (170, 230, 255)),
    "Chen Stormstout": _hero("Spearman", "Pandaren", "full", [lambda l: back_item(l, "keg"), lambda l: weapon(l, "staff")], (255, 220, 140)),
    "Nathanos Blightcaller": _hero("Composite Bowman", "Forsaken", "full", [lambda l: headgear(l, "hood")], (150, 240, 110)),
    "Maraad": _hero("Swordsman", "Draenei", "full", [lambda l: weapon(l, "hammer")], (255, 235, 160)),
    "Gazlowe": _hero("Scout", "Goblins", "full", [lambda l: headgear(l, "goggles"), lambda l: back_item(l, "bomb")], (255, 200, 90)),
    "Darius Crowley": _hero("Swordsman", "Worgen", "full", [lambda l: back_item(l, "cloak")], (200, 200, 230)),
    "Kel'Thuzad": _hero("Worker", "Scourge", "full", [lambda l: headgear(l, "cult_hood"), lambda l: weapon(l, "staff")], (140, 210, 255)),
    "Dagran Thaurissan": _hero("Swordsman", "Dark Iron Dwarves", "full", [lambda l: weapon(l, "hammer")], (255, 130, 50)),
    "Daelin Proudmoore": _hero("Musketman", "Kul Tirans", "full", [lambda l: back_item(l, "cloak")], (150, 210, 255)),
    "Rastakhan": _hero("Spearman", "Zandalari Trolls", "full", [lambda l: headgear(l, "mask"), lambda l: weapon(l, "staff")], (255, 215, 90)),
}
SPRITES.update(HERO_SPRITES)


# ======================================================================= clerics (v0.13)
def _cleric_sprites():
    import wc_playstyles as PS
    out = {"Cleric": ("Great Prophet", None, "raw", [lambda l: glow_aura(l, (255, 235, 160), "body")])}
    glow = {"Night Elves": (150, 255, 170), "Orcs": (140, 200, 255), "Trolls": (160, 255, 170),
            "Gnomes": (190, 255, 120), "Goblins": (190, 255, 120), "Pandaren": (170, 240, 220)}
    for race, (name, _) in PS.CLERICS.items():
        src = "Great Prophet"
        out[name] = (src, None if race == "Humans" else race, "raw" if race == "Humans" else "full",
                     [lambda l, g=glow.get(race, (255, 235, 160)): glow_aura(l, g, "body")]
                     + ([lambda l: headgear(l, "goggles")] if race in ("Gnomes", "Goblins") else []))
    return out
SPRITES.update(_cleric_sprites())


# ======================================================================= v0.17
# A later-era unique unit for every race (so races stay distinct past the steam age),
# a second unique building, and the uniques of the three new races.
UNITS += [
    ("Orcs", "Cavalry", {"name": "Raider", "strength": 36,
        "dropUniques": ["[-33]% Strength <vs cities> <when attacking>"],
        "addUniques": ["No movement cost to pillage", "[+25]% Strength <vs [Mounted] units>"],
        "civilopediaText": _lore("Wolf riders armed with chains and grappling hooks, trained to drag down walls, riders and siege engines alike.",
                                 "Stronger than Cavalry, no penalty attacking cities, pillages without spending movement and +25% Strength against mounted units.")}),
    ("Dwarves", "War Golem", {"name": "Steam Armor", "strength": 66,
        "addUniques": ["[+25]% Strength <when fighting in [Hill] tiles>"],
        "civilopediaText": _lore("A dwarf in a walking suit of riveted steel and boiler-plate, the pride of Ironforge's engineers.",
                                 "Stronger than a War Golem, with +25% Strength in hills.")}),
    ("Gnomes", "Siege Engine", {"name": "Spider Tank", "strength": 74, "movement": 6,
        "addUniques": ["Ignores terrain cost"],
        "civilopediaText": _lore("A gnomish tank on eight clockwork legs that climbs over rubble, hills and anything else in its way.",
                                 "Stronger and faster than a Siege Engine, and ignores terrain movement costs.")}),
    ("Night Elves", "War Golem", {"name": "Mountain Giant", "strength": 64, "requiredResource": None,
        "dropUniques": ["No defensive terrain bonus"],
        "addUniques": ["[+25]% Strength <when fighting in [Forest] tiles>", "[+15]% Strength <when defending>"],
        "civilopediaText": _lore("Ancient giants of living stone and moss who answer the night elves' call to defend the forests.",
                                 "Stronger than a War Golem, needs no Azerite, keeps terrain defence, +25% Strength in forests and +15% when defending.")}),
    ("Draenei", "War Golem", {"name": "Lightforged Warframe", "strength": 64,
        "addUniques": ["All adjacent units heal [+10] HP when healing", "[+33]% Strength <vs [Barbarian] units>"],
        "civilopediaText": _lore("A towering frame of Light-infused metal from the Army of the Light, piloted by a Lightforged draenei.",
                                 "Stronger than a War Golem, heals adjacent units 10 HP more, and +33% Strength against barbarians and demons.")}),
    ("Worgen", "War Golem", {"name": "Harvest Golem", "strength": 62,
        "addUniques": ["[+20]% Strength <when defending>", "[+1] Sight"],
        "civilopediaText": _lore("Gilneas's farm golems, refitted with plate and cannon to hold the walls against the Scourge and the Forsaken.",
                                 "Stronger than a War Golem, +20% Strength when defending, and sees farther.")}),
    ("High Elves", "Mountaineer", {"name": "Ranger-Lord", "strength": 32, "rangedStrength": 34,
        "addUniques": ["[+1] Sight", "[+25]% Strength <when fighting in [Forest] tiles>"],
        "civilopediaText": _lore("The masters of the Farstriders, whose enchanted arrows outrange any rifle.",
                                 "Stronger than a Mountaineer, sees farther and gains +25% Strength in forests.")}),
    ("Trolls", "Musketeer", {"name": "Troll Berserker", "strength": 27,
        "addUniques": ["Heals [10] damage if it kills a unit", "[+15]% Strength <when attacking>"],
        "civilopediaText": _lore("Headhunters who drink a voodoo brew and charge into battle in a frenzy, throwing axes as they go.",
                                 "Stronger than a Musketeer, +15% Strength when attacking, and heals 10 HP whenever it kills a unit.")}),
    ("Tauren", "Gyrocopter", {"name": "Wind Rider", "strength": 37, "rangedStrength": 37, "range": 7,
        "civilopediaText": _lore("Tauren and orc riders on wyverns, the Horde's answer to the gryphon riders of the Alliance.",
                                 "Stronger than a Gyrocopter, with a longer range (7).")}),
    ("Forsaken", "Rifleman", {"name": "Deathstalker", "strength": 36,
        "addUniques": ["[+1] Sight", "Ignores Zone of Control"],
        "civilopediaText": _lore("The Banshee Queen's assassins and scouts, undead rangers who slip between enemy lines.",
                                 "Stronger than a Rifleman, sees farther and ignores zones of control.")}),
    ("Blood Elves", "Gyrocopter", {"name": "Dragonhawk Rider", "strength": 38, "rangedStrength": 38,
        "addUniques": ["[+25]% Strength <vs [Land] units>"],
        "civilopediaText": _lore("Blood elf riders on fiery dragonhawks, raised in the aviaries of Eversong.",
                                 "Stronger than a Gyrocopter, with +25% Strength against land units.")}),
    ("Goblins", "Bomber Zeppelin", {"name": "Goblin Zeppelin", "strength": 55, "rangedStrength": 58,
        "addUniques": ["[+33]% Strength <vs cities>"],
        "civilopediaText": _lore("A patched-together goblin airship loaded with more explosives than is strictly safe.",
                                 "Stronger than a Bomber Zeppelin, with +33% Strength against cities.")}),
    ("Pandaren", "Gryphon Rider", {"name": "Cloud Serpent Rider", "strength": 50, "rangedStrength": 50,
        "addUniques": ["[+15] HP when healing"],
        "civilopediaText": _lore("Riders of the Order of the Cloud Serpent on the jade serpents of Pandaria.",
                                 "Stronger than a Gryphon Rider and heals 15 HP more each turn it heals.")}),
    ("Scourge", "Mountaineer", {"name": "Crypt Fiend", "strength": 32, "rangedStrength": 32, "requiredResource": None,
        "addUniques": ["[+50]% Strength <vs [Sky Fighter] units>", "Heals [10] damage if it kills a unit"],
        "civilopediaText": _lore("Undead nerubians that spit acid and web flying enemies out of the sky.",
                                 "Stronger than a Mountaineer, +50% Strength against flying fighters, and heals 10 HP whenever it kills a unit.")}),
    # ---------------------------------------------------------------- Dark Iron Dwarves
    ("Dark Iron Dwarves", "Pikeman", {"name": "Fireguard", "strength": 18,
        "addUniques": ["[+25]% Strength <when fighting in [Hill] tiles>", "[+15]% Strength <when defending>"],
        "civilopediaText": _lore("Dark Iron guards in blackened plate, their halberds still glowing from the forges of Shadowforge City.",
                                 "Stronger than a Pikeman, +25% Strength in hills and +15% when defending.")}),
    ("Dark Iron Dwarves", "War Golem", {"name": "Dark Iron Golem", "strength": 66,
        "addUniques": ["[+15]% Strength <when attacking>"],
        "civilopediaText": _lore("Hulking constructs of dark iron with a furnace for a heart, built by the forgemasters of Blackrock Depths.",
                                 "Stronger than a War Golem, with +15% Strength when attacking.")}),
    # ---------------------------------------------------------------- Kul Tirans
    ("Kul Tirans", "Frigate", {"name": "Kul Tiran Man-o'-War", "strength": 28, "rangedStrength": 32, "movement": 6,
        "civilopediaText": _lore("The great warships of Kul Tiras, the island kingdom whose admiralty has ruled the seas of the Eastern Kingdoms for generations.",
                                 "Faster and better armed than any frigate.")}),
    ("Kul Tirans", "Musketeer", {"name": "Admiralty Gunner", "strength": 27,
        "addUniques": ["Eliminates combat penalty for attacking across a coast", "[+1] Sight"],
        "civilopediaText": _lore("Kul Tiran marines of the Proudmoore Admiralty, as at home storming a beach as standing on a deck.",
                                 "Stronger than a Musketeer, attacks from ships without penalty and sees farther.")}),
    # ---------------------------------------------------------------- Zandalari Trolls
    ("Zandalari Trolls", "Outrider", {"name": "Raptor Rider", "strength": 13, "movement": 5,
        "addUniques": ["[+25]% Strength <when fighting in [Jungle] tiles>"],
        "civilopediaText": _lore("Zandalari riders on swift raptors bred in the jungles of Zuldazar.",
                                 "Stronger and faster than an Outrider, with +25% Strength in jungle.")}),
    ("Zandalari Trolls", "Knight", {"name": "Direhorn Rider", "strength": 23,
        "dropUniques": ["[-33]% Strength <vs cities> <when attacking>"],
        "addUniques": ["[+20]% Strength <when attacking>"],
        "civilopediaText": _lore("Zandalari warriors on armored direhorns, whose charge can break a shield wall or a city gate.",
                                 "Stronger than a Knight, no penalty attacking cities, and +20% Strength when attacking.")}),
]

BUILDINGS += [
    ("Orcs", "Workshop", {"name": "War Mill", "addStats": {"production": 1},
        "addUniques": ["[+15]% Production when constructing [Military] units [in this city]"],
        "civilopediaText": _lore("Where the Horde's axes are forged and its catapults built, as in every orcish town since the Second War. +1 Production and +15% Production toward military units.")}),
    ("Dwarves", "Foundry", {"name": "Great Forge", "addStats": {"production": 2},
        "civilopediaText": _lore("A forge in the image of the Great Forge at the heart of Ironforge, its rivers of molten metal never cooling. +2 Production.")}),
    ("Gnomes", "Arcane Laboratory", {"name": "Gnomeregan Laboratory", "addStats": {"science": 2},
        "civilopediaText": _lore("A laboratory in the tradition of Gnomeregan's tinkers, full of gears, steam and the occasional small explosion. +2 Science.")}),
    ("Night Elves", "Keep", {"name": "Tree of Life", "addStats": {"food": 2, "cityStrength": 2},
        "civilopediaText": _lore("A great ancient that is both the heart and the shelter of a night elf town. +2 Food and stronger defences than a Keep.")}),
    ("Draenei", "Library", {"name": "Crystal Hall", "addStats": {"faith": 1},
        "civilopediaText": _lore("A hall of glowing crystals where draenei scholars record the teachings of the naaru. +1 Faith.")}),
    ("Worgen", "Keep", {"name": "Greymane Watchtower", "addStats": {"culture": 1, "cityStrength": 2},
        "civilopediaText": _lore("A watchtower of the Greymane Wall, built to keep Gilneas apart from the world. +1 Culture and stronger defences than a Keep.")}),
    ("High Elves", "Mage Tower", {"name": "Elven Spire", "addStats": {"culture": 1, "happiness": 1},
        "civilopediaText": _lore("A slender spire of white stone and blue glass, home to the magisters of Quel'Thalas. +1 Culture and +1 Happiness.")}),
    ("Trolls", "Temple", {"name": "Loa Shrine", "addStats": {"culture": 1},
        "civilopediaText": _lore("A shrine to the loa, the wild gods of the trolls, hung with masks and offerings. +1 Culture.")}),
    ("Tauren", "Herb Garden", {"name": "Spirit Lodge", "addStats": {"faith": 1, "food": 1, "happiness": 1},
        "civilopediaText": _lore("A lodge where tauren spirit walkers commune with the ancestors and the Earth Mother. +1 Faith, +1 Food and +1 Happiness.")}),
    ("Forsaken", "Foundry", {"name": "Plague Cauldron", "addStats": {"science": 1},
        "civilopediaText": _lore("Great bubbling cauldrons where the apothecaries brew new plagues. +1 Science.")}),
    ("Blood Elves", "Foundry", {"name": "Mana Forge", "addStats": {"production": 1},
        "civilopediaText": _lore("A blood elf forge that draws raw energy from mana itself. +1 Production, +1 Mana.")}),
    ("Goblins", "Bank", {"name": "Trade Prince's Bank", "addStats": {"gold": 2},
        "civilopediaText": _lore("A Bilgewater Cartel bank: secure vaults, generous loans, ruinous interest. +2 Gold.")}),
    ("Pandaren", "Temple", {"name": "Jade Pagoda", "addStats": {"culture": 1, "happiness": 1},
        "civilopediaText": _lore("A pagoda of carved jade where monks meditate on the balance of all things. +1 Culture and +1 Happiness.")}),
    ("Scourge", "Foundry", {"name": "Slaughterhouse", "addStats": {"production": 1}, "addUniques": [BLIGHT],
        "civilopediaText": _lore("Where the Scourge stitches together abominations and gathers corpses for its wagons. +1 Production. Needs Plagued Land within 3 tiles.")}),
    ("Dark Iron Dwarves", "Blacksmith", {"name": "Shadowforge Furnace", "addStats": {"production": 2},
        "civilopediaText": _lore("A furnace fed by the fires beneath Blackrock Mountain, where the Dark Irons work their black metal. +2 Production.")}),
    ("Kul Tirans", "Shipyard", {"name": "Admiralty Drydock", "addStats": {"production": 1, "happiness": 1},
        "addUniques": ["New [Water] units start with [15] XP [in this city]"],
        "civilopediaText": _lore("The drydocks of the Proudmoore Admiralty, where the finest ships on Azeroth are built. +1 Production, +1 Happiness, and new ships start with 15 experience.")}),
    ("Zandalari Trolls", "Market", {"name": "Golden Pyramid", "addStats": {"gold": 1, "culture": 1},
        "civilopediaText": _lore("A pyramid capped in gold in the manner of Dazar'alor, seat of the Zandalari's wealth and pride. +1 Gold and +1 Culture over a Market.")}),
]

ICONS_UNITS.update({
    "Raider": ("wolf", "chains"), "Steam Armor": ("golem", "gear"), "Spider Tank": ("gears", "feet"),
    "Mountain Giant": ("mountain", "fist"), "Lightforged Warframe": ("golem", "naaru"),
    "Harvest Golem": ("golem", "wheat"), "Ranger-Lord": ("bow", "crown"), "Troll Berserker": ("axe", "mask"),
    "Wind Rider": ("wing", "spear"), "Deathstalker": ("skull", "eye"), "Dragonhawk Rider": ("wing", "flame"),
    "Goblin Zeppelin": ("zeppelin", "bomb"), "Cloud Serpent Rider": ("dragon", "jade"),
    "Crypt Fiend": ("net", "skull"), "Fireguard": ("spear", "flame"), "Dark Iron Golem": ("golem", "flame"),
    "Admiralty Gunner": ("gun", "anchor"),
    "Raptor Rider": ("paw", "spear"), "Direhorn Rider": ("horn", "shield"),
})
ICONS_BUILDINGS.update({
    "War Mill": ("saw", "axe"), "Great Forge": ("anvil", "hammer"), "Gnomeregan Laboratory": ("gears", "flask"),
    "Tree of Life": ("tree", "heart"), "Crystal Hall": ("crystals", "book"), "Greymane Watchtower": ("tower", "wolf"),
    "Elven Spire": ("spire", "sparkle"), "Loa Shrine": ("temple", "mask"), "Spirit Lodge": ("tent", "feather_plume"),
    "Plague Cauldron": ("cauldron", "skull"), "Mana Forge": ("anvil", "orb"), "Trade Prince's Bank": ("coins", "key"),
    "Jade Pagoda": ("pagoda", "jade"), "Slaughterhouse": ("chains", "skull"), "Shadowforge Furnace": ("anvil", "flame"),
    "Admiralty Drydock": ("ship", "hammer"), "Golden Pyramid": ("ziggurat", "coins"),
})


# ---- v0.17 sprites (the Human and Orc uniques are painted in wc_style_units.py)
def wyvern_recolor(col):
    """Re-dye a flying mount's feathers/hide (mid-saturation warm hues) to `col`."""
    return lambda ls: LU.recolor(ls, lambda h, s, v: s > 0.18 and v > 0.25 and not (0.55 < h < 0.75),
                                 lambda v: tuple(int(c * (0.45 + 0.65 * v)) for c in col)) or ls


def _recolored(fn):
    def step(ls):
        fn(ls)
        return ls
    return step


def mountain_giant(ls):
    base, l1, l2 = RS.reshape(ls, 1.45, 1.3)
    ls = [base, l1, l2]
    ANCHOR[:] = _anchor(ls)
    LU.recolor(ls, lambda h, s, v: v > 0.2, lambda v: tuple(int(c * (0.45 + 0.6 * v)) for c in (128, 132, 118)))
    x0, y0, x1, y1 = LU.bbox_all(ls)
    part, d = _part(base.size)
    for i in range(6):                                       # moss on the shoulders and back
        d.ellipse([x0 + 3 + i * 4, y0 + 6 + (i % 3), x0 + 7 + i * 4, y0 + 9 + (i % 3)], fill=(80, 130, 60, 255))
    return _apply(ls, part)


def crypt_fiend(ls):
    base, l1, l2 = RS.reshape(ls, 1.4, 0.85)
    ls = [base, l1, l2]
    ANCHOR[:] = _anchor(ls)
    LU.recolor(ls, lambda h, s, v: True if v > 0.15 and s > 0.1 else False,
               lambda v: tuple(int(c * (0.4 + 0.7 * v)) for c in (60, 70, 105)))
    x0, y0, x1, y1 = LU.bbox_all(ls)
    part, d = _part(base.size)
    for k in range(3):                                       # spider legs
        d.line([(x0 + 4 + k * 5, y1 - 10), (x0 - 1 + k * 4, y1 - 1)], fill=(45, 50, 75, 255), width=2)
        d.line([(x1 - 4 - k * 5, y1 - 10), (x1 + 1 - k * 4, y1 - 1)], fill=(45, 50, 75, 255), width=2)
    ls = _apply(ls, part)
    return _glow(ls, (140, 230, 120), lambda d: d.ellipse([x1 - 6, y0 + 4, x1 - 3, y0 + 7], fill=(150, 240, 120, 255)))


def direhorn(atlas):
    """A Zandalari rider on a direhorn (a kodo-sized beast with a bony frill and horns)."""
    import mounts
    src_layers = [atlas.crop(P + "Knight" + s) for s in ("", "-1", "-2")]
    w, h = src_layers[0].size
    rider = RS.make(LU.source_layers(atlas, "Swordsman"), "Zandalari Trolls", "Swordsman")
    cw = rider[0].width
    canvas = (cw, round(h * cw / w))
    bb = src_layers[0].getbbox()
    def dire(p, v, armored):
        sx, sy = mounts.kodo(p, 2, armored)
        p.poly([(50, 10), (58, 6), (60, 14), (54, 18)], (190, 160, 120), "frill")
        p.line(56, 14, 63, 9, 2, (238, 228, 196), "horn")
        return sx, sy
    return mounts.compose(rider, "Zandalari Trolls", 1, True, canvas, round(bb[3] / h * canvas[1]),
                          (bb[0] + bb[2]) / 2 / w * cw, mount=dire)


SPRITES.update({
    "Steam Armor": ("Landship", None, "raw", [_recolored(lambda l: recolor_metal(l, (185, 140, 80)))]),
    "Spider Tank": ("Tank", None, "raw", [_recolored(lambda l: recolor_metal(l, (90, 175, 170))),
                                           lambda l: headgear(l, "goggles")]),
    "Mountain Giant": ("Swordsman", "Tauren", "full", [mountain_giant]),
    "Lightforged Warframe": ("Landship", None, "raw", [_recolored(lambda l: recolor_metal(l, (245, 210, 120))),
                                                       lambda l: glow_aura(l, (255, 235, 150), "body")]),
    "Harvest Golem": ("Landship", None, "raw", [_recolored(lambda l: recolor_metal(l, (150, 110, 70)))]),
    "Ranger-Lord": ("Composite Bowman", "High Elves", "full", [lambda l: headgear(l, "hood"), lambda l: back_item(l, "cloak"),
                                                                lambda l: glow_aura(l, (170, 220, 255))]),
    "Troll Berserker": ("Swordsman", "Trolls", "full", [lambda l: weapon(l, "axe"), lambda l: headgear(l, "mask")]),
    "Deathstalker": ("Rifleman", "Forsaken", "full", [lambda l: headgear(l, "hood"), lambda l: back_item(l, "cloak")]),
    "Crypt Fiend": ("Composite Bowman", "Scourge", "full", [crypt_fiend]),
    "Fireguard": ("Pikeman", "Dark Iron Dwarves", "full", [lambda l: headgear(l, "horned_helm"),
                                                             lambda l: glow_aura(l, (255, 130, 50))]),
    "Dark Iron Golem": ("Landship", None, "raw", [_recolored(lambda l: recolor_metal(l, (85, 72, 70))),
                                                  lambda l: glow_aura(l, (255, 120, 40), "body")]),
    "Admiralty Gunner": ("Musketman", "Kul Tirans", "full", [lambda l: headgear(l, "top_hat")]),
    "Raptor Rider": ("Horseman", "Zandalari Trolls", "mounted", [lambda l: headgear(l, "mask")]),
})
_PAINTED_RENDER = {"Direhorn Rider": direhorn}
