"""Unit icons (Nov 2026): every unit's icon is cut from its own map sprite.

Run after all sprites are written. The figure is cropped, scaled to fill the icon, and reduced to three
flat tones (the game tints unit icons), with the sprite's ink lines left as gaps so armour, weapons and
faces still read at small sizes. Units with no sprite of the new kind get a drawn emblem instead.
"""
import json
import os

from PIL import Image

import building_icons as BI
import misc_icons as MI
import unit_art as UA

UNITS = "TileSets/AbsoluteUnits/Units"
SKIP = set()


def _layers(root, name):
    """The unit's own sprite, or failing that one faction's version of it (Humans first)."""
    for pack in ("Images.RaceUnits", "Images.WarcraftMap", "Images"):
        folder = os.path.join(root, pack, UNITS)
        if not os.path.isdir(folder):
            continue
        stems = [name]
        if not os.path.exists(os.path.join(folder, name + ".png")):
            own = sorted(f[:-4] for f in os.listdir(folder)
                         if f.startswith(name + "-") and f.endswith(".png") and not f[:-4].endswith(("-1", "-2"))
                         and f[len(name) + 1:-4].count("-") == 0)
            stems = [x for x in own if x.endswith("-Humans")] + own
        for stem in stems:
            base = os.path.join(folder, stem)
            if os.path.exists(base + ".png"):
                return [Image.open(base + suf + ".png").convert("RGBA") if os.path.exists(base + suf + ".png") else None
                        for suf in ("", "-1", "-2")]
    return None


def cut(layers):
    base = layers[0]
    if base.size[0] >= 188 and base.size[1] >= 160:
        box = (0, 0, 188, 160)
    elif base.size[0] >= 94 and base.size[1] >= 80:          # older half-size sprites
        box = (0, 0, 94, 80)
    else:
        return None
    g = [None if im is None else im.crop(box).resize((47, 40), Image.NEAREST) for im in layers]
    flat = g[0].copy()
    for extra, k in ((g[1], 200), (g[2], 150)):
        if extra is None:
            continue
        px = extra.load()
        for y in range(40):
            for x in range(47):
                if px[x, y][3]:
                    v = px[x, y][0] * k // 255
                    flat.putpixel((x, y), (v, v, v, 255))
    src = flat.load()
    out = Image.new("RGBA", (47, 40), (0, 0, 0, 0))
    o = out.load()
    for y in range(40):
        for x in range(47):
            r, gg, b, a = src[x, y]
            if a < 200 or (r, gg, b) == UA.INK:
                continue
            lum = (r * 3 + gg * 6 + b) // 10
            o[x, y] = (255, 255, 255, 255 if lum >= 140 else 205 if lum >= 85 else 150)
    box = out.getbbox()
    if not box or (box[2] - box[0]) < 6:
        return None
    crop = out.crop(box)
    k = min(96 / crop.width, 96 / crop.height)
    crop = crop.resize((max(1, int(crop.width * k)), max(1, int(crop.height * k))), Image.NEAREST)
    canvas = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    canvas.alpha_composite(crop, ((100 - crop.width) // 2, (100 - crop.height) // 2))
    return canvas


T = BI.from_tech
EMBLEMS = {     # units that are not figures on the map
    "Arcane Thruster": T("Liquid Fire"), "Navigation Crystal": T("Communication Crystals"), "Titan Engine": T("Steam Power"),
    "Stasis Vault": BI.vault, "Great Artist": T("Bardic Lore"), "Great Scientist": T("Scrying"), "Great Merchant": BI.coins,
    "Great Engineer": BI.hammer_gear, "Great Prophet": BI.brazier, "Great General": BI.banner, "Great Admiral": BI.anchor,
}


def _hammer(i):
    return i.hammer(16, 3, 29, 9)


HEROES = {      # a class emblem with a faction mark: no portraits, so no likenesses
    "Uther the Lightbringer": (_hammer, "sun"), "Grom Hellscream": (T("Bronze Working"), "flame"),
    "Malfurion Stormrage": (BI.tree, "moon"), "Muradin Bronzebeard": (T("Storm Hammers"), "crown"),
    "Kelsey Steelspark": (BI.mask, "gear"), "Baine Bloodhoof": (BI.totem, "crown"), "Rokhan": (BI.tiki, "sword"),
    "Kael'thas Sunstrider": (MI.bird, "flame"), "Alleria Windrunner": (T("Archery"), "star"), "Chen Stormstout": (BI.brewery, "leaf"),
    "Nathanos Blightcaller": (T("Archery"), "skull"), "Maraad": (_hammer, "gem"), "Gazlowe": (BI.wrench, "coin"),
    "Darius Crowley": (T("Animal War Training"), "sword"), "Dagran Thaurissan": (BI.anvil, "crown"),
    "Daelin Proudmoore": (BI.anchor, "crown"), "Rastakhan": (BI.pyramid, "crown"), "Lady Vashj": (BI.trident, "crown"),
    "Grand Magistrix Elisande": (BI.hourglass, "star"), "Huln Highmountain": (BI.horn_totem, "bolt"),
}
EMBLEMS.update(HEROES)


def _dragon(i):
    # a dragon's head in profile: horns swept back, jaw open
    i.P([(4, 30), (5, 18), (10, 10), (18, 7), (25, 9), (31, 14), (31, 17), (24, 18), (30, 22), (28, 25), (20, 22), (17, 30)])
    i.P([(10, 10), (2, 1), (8, 3), (15, 8)]).P([(16, 7), (12, 0), (17, 2), (21, 7)])
    i.P([(24, 18), (30, 22), (28, 25), (20, 22)], BI.M)
    i.E(20, 12, 1, t=BI.C)
    for x in (24, 27):
        i.P([(x, 18), (x + 1, 20), (x + 2, 18)], BI.C)
    return i.L([(7, 20), (12, 26)], 1, BI.C).L([(8, 15), (14, 20)], 1, BI.C)


def _horned(i):
    # a horned skull
    BI.skull(i)
    i.P([(7, 8), (0, 0), (2, 10), (6, 14)]).P([(25, 8), (31, 0), (29, 10), (26, 14)])
    return i


BOSSES = {      # raid bosses: plain emblems of what each is, not portraits
    "Kel'Thuzad": (T("Frost Enchantment"), "skull"), "Onyxia": (_dragon, "flame"), "Hakkar the Soulflayer": (BI.serpent, "drop"),
    "Ragnaros the Firelord": (MI.fel, "hammer"), "C'Thun": (T("Eye of Kilrogg"), "skull"), "Sapphiron": (_dragon, "gem"),
    "Deathwing the Destroyer": (_dragon, "crown"), "Gul'dan the Destroyer": (BI.skull, "flame"),
    "Kil'jaeden the Deceiver": (_horned, "flame"), "N'Zoth the Corruptor": (T("Secrets of the Void"), "eye"),
}
EMBLEMS.update(BOSSES)



def write_all(root, prefer_emblem=()):
    icons = os.path.join(root, "Images", "UnitIcons")
    if not os.path.isdir(icons):
        return 0
    units = json.load(open(os.path.join(root, "jsons", "Units.json")))
    n = 0
    for u in units:
        name = u["name"]
        if name in SKIP:
            continue
        img = None
        if name not in prefer_emblem and name not in EMBLEMS:
            layers = _layers(root, name)
            img = cut(layers) if layers else None
        if img is None and name in EMBLEMS:
            img = MI.render(EMBLEMS[name])
        if img is not None:
            img.save(os.path.join(icons, name + ".png"))
            n += 1
    return n
