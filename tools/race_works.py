"""Race-styled ships, hunting camps and forts (v0.15).

Ships: every race's sailing ships ("Longboat-Orcs" ...) are re-dyed and re-rigged from
the stock sprites: race sail cloth and hull wood plus a few lore touches (orcish spikes
and hide sails, night elf leaf prows, pandaren junk battens, Forsaken tatters and green
lanterns, Scourge bone and saronite, goblin and gnomish smokestacks ...). The small
owner-colour stripes on the stock sails are kept, so each player's colours still show.

Camps and forts: Unciv draws an owned tile's improvement as "<image>-<owner>" when that
image exists, so every race gets its own "Camp-<race>" / "Fort-<race>" (and the combined
"Plainstriders+Camp-<race>" ... images the tile set uses), in the same architecture as its
city centers (citycenters.STYLES). Original pixel art; Warcraft designs are only a guide
to what each people builds.
"""
import colorsys, math, os, random, zlib
from PIL import Image, ImageDraw
import late_units as LU
from mounts import shade
import citycenters as CC

P_UNITS = "TileSets/AbsoluteUnits/Units/"
HEX = "TileSets/HexaRealm/Tiles/"
DARK = (30, 24, 22)

# ======================================================================= ships
SHIPS = {   # mod name -> stock sprite
    "Fishing Skiff": "Work Boats", "Longboat": "Trireme", "War Galley": "Galleass",
    "Brigantine": "Caravel", "Buccaneer": "Privateer", "Frigate": "Frigate",
}

# race: sail, hull, accent, props
SHIP_STYLE = {
    "Humans":      dict(sail=(238, 234, 222), hull=(150, 105, 60), acc=(235, 195, 70), props=["figure"]),
    "Orcs":        dict(sail=(170, 70, 45), hull=(90, 62, 45), acc=(40, 35, 35), props=["spikes", "emblem"]),
    "Night Elves": dict(sail=(180, 160, 225), hull=(205, 205, 228), acc=(90, 190, 110), props=["leafprow", "glow"],
                        glow=(170, 225, 255)),
    "Dwarves":     dict(sail=(185, 170, 140), hull=(105, 100, 102), acc=(210, 160, 60), props=["rivets", "stack"]),
    "Gnomes":      dict(sail=(240, 205, 225), hull=(145, 165, 180), acc=(80, 170, 170), props=["stack", "gear"]),
    "Tauren":      dict(sail=(205, 172, 120), hull=(175, 120, 72), acc=(190, 60, 40), props=["stripes", "totem"]),
    "Trolls":      dict(sail=(195, 175, 115), hull=(190, 165, 90), acc=(80, 150, 90), props=["patches", "mask"]),
    "Blood Elves": dict(sail=(190, 40, 45), hull=(238, 228, 208), acc=(240, 200, 70), props=["figure", "glow"],
                        glow=(255, 190, 80)),
    "High Elves":  dict(sail=(242, 242, 250), hull=(232, 232, 242), acc=(50, 100, 200), props=["figure"]),
    "Pandaren":    dict(sail=(205, 95, 50), hull=(155, 48, 38), acc=(60, 150, 110), props=["battens", "dragon"]),
    "Forsaken":    dict(sail=(100, 95, 108), hull=(58, 52, 58), acc=(150, 230, 90), props=["tatter", "glow"],
                        glow=(140, 240, 90)),
    "Scourge":     dict(sail=(205, 205, 195), hull=(55, 66, 88), acc=(225, 225, 210), props=["tatter", "spikes", "glow"],
                        glow=(130, 210, 255)),
    "Draenei":     dict(sail=(205, 195, 238), hull=(155, 145, 190), acc=(160, 220, 255), props=["crystal"],
                        glow=(150, 220, 255)),
    "Goblins":     dict(sail=(205, 175, 95), hull=(145, 82, 52), acc=(150, 150, 155), props=["patches", "stack"]),
    "Worgen":      dict(sail=(118, 116, 122), hull=(78, 58, 46), acc=(200, 200, 205), props=["glow"],
                        glow=(255, 215, 120)),
    "Dark Iron Dwarves": dict(sail=(95, 85, 82), hull=(60, 52, 52), acc=(255, 120, 30), props=["rivets", "stack", "glow"],
                              glow=(255, 130, 50)),
    "Kul Tirans":  dict(sail=(240, 236, 224), hull=(110, 75, 45), acc=(30, 80, 110), props=["figure"]),
    "Zandalari Trolls": dict(sail=(240, 200, 80), hull=(150, 110, 60), acc=(40, 130, 110), props=["mask", "figure"]),
    "Naga": dict(sail=(60, 150, 140), hull=(70, 110, 100), acc=(240, 205, 90), props=["figure", "glow"], glow=(120, 240, 220)),
    "Nightborne": dict(sail=(110, 70, 170), hull=(90, 70, 110), acc=(232, 200, 110), props=["glow"], glow=(200, 150, 255)),
    "Highmountain Tauren": dict(sail=(190, 150, 100), hull=(110, 80, 55), acc=(120, 200, 225), props=["figure"]),
}


def _hsv(p):
    return colorsys.rgb_to_hsv(p[0] / 255, p[1] / 255, p[2] / 255)


def _tone(col, v, lo=0.45, hi=0.62):
    return tuple(max(0, min(255, int(c * (lo + hi * v)))) for c in col)


def _masks(base):
    """Classify the stock ship's pixels: sail cloth and hull wood."""
    px = base.load()
    sail, wood = set(), set()
    for y in range(base.height):
        for x in range(base.width):
            p = px[x, y]
            if p[3] < 200:
                continue
            h, s, v = _hsv(p)
            if s < 0.22 and v > 0.17:
                sail.add((x, y))
            elif 0.03 < h < 0.16 and s >= 0.22 and v > 0.18:
                wood.add((x, y))
    return sail, wood


def _put(im, x, y, col):
    if 0 <= x < im.width and 0 <= y < im.height:
        im.putpixel((int(x), int(y)), tuple(col) + (255,))


def style_ship(ls, race, unit):
    st = SHIP_STYLE[race]
    ls = [l.copy().convert("RGBA") for l in ls]
    base = ls[0]
    px = base.load()
    sail, wood = _masks(base)
    dark_sails = unit == "Buccaneer"
    for (x, y) in sail:
        v = _hsv(px[x, y])[2]
        col = st["sail"] if not dark_sails else shade(st["sail"], 0.62)
        px[x, y] = _tone(col, v, 0.35, 0.75) + (255,)
    for (x, y) in wood:
        v = _hsv(px[x, y])[2]
        px[x, y] = _tone(st["hull"], v, 0.35, 1.0) + (255,)
    if not wood:
        return ls
    wx = [x for x, _ in wood]; wy = [y for _, y in wood]
    sx = [x for x, _ in sail] or wx; sy = [y for _, y in sail] or wy
    bow = min(wood, key=lambda p: (p[0] - p[1] * 0.6))           # lower-left tip
    stern = max(wood, key=lambda p: (p[0] - p[1] * 0.2))
    top = min(sail | wood, key=lambda p: p[1]) if sail else stern
    sc = (sum(sx) / len(sx), sum(sy) / len(sy))                    # sail centroid
    rng = random.Random(zlib.crc32((race + unit).encode()))
    props = st["props"]
    acc = st["acc"]
    part = Image.new("RGBA", base.size)
    glow = Image.new("RGBA", base.size)

    removed = set()
    if "tatter" in props:     # ragged lower sail edges and holes
        for (x, y) in list(sail):
            below = (x, y + 1) not in sail and (x, y + 1) not in wood
            if below and rng.random() < 0.55:
                px[x, y] = (0, 0, 0, 0); removed.add((x, y))
                if rng.random() < 0.5 and (x, y - 1) in sail:
                    px[x, y - 1] = (0, 0, 0, 0); removed.add((x, y - 1))
            elif rng.random() < 0.03:
                px[x, y] = shade(st["sail"], 0.4) + (255,)
    if "battens" in props:    # junk sails: dark bamboo battens every 3 rows
        for (x, y) in sail:
            if y % 3 == 0:
                px[x, y] = shade(st["sail"], 0.5) + (255,)
    if "stripes" in props:    # painted bands on the hide sails
        for (x, y) in sail:
            if y % 6 in (0, 1):
                px[x, y] = (_tone(acc, 0.8) if y % 12 < 6 else _tone((60, 120, 170), 0.8)) + (255,)
    if "patches" in props:    # patched canvas
        for _ in range(4):
            cx, cy = rng.choice(sorted(sail)) if sail else (0, 0)
            for dx in range(2):
                for dy in range(2):
                    if (cx + dx, cy + dy) in sail:
                        px[cx + dx, cy + dy] = _tone(acc, 0.7) + (255,)
    if "rivets" in props:     # iron plates along the hull
        for (x, y) in wood:
            if (x + y) % 4 == 0 and (x, y - 1) in wood:
                px[x, y] = shade(st["hull"], 1.5) + (255,)
        for (x, y) in wood:
            if (x, y - 1) not in wood:
                px[x, y] = acc + (255,)
    if "emblem" in props and sail:   # a dark skull-and-tusk mark on the main sail
        cx, cy = int(sc[0]), int(sc[1])
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, -1), (1, -1), (-1, -1), (0, 1)):
            if (cx + dx, cy + dy) in sail:
                px[cx + dx, cy + dy] = acc + (255,)
        for dx in (-2, 2):
            if (cx + dx, cy + 1) in sail:
                px[cx + dx, cy + 1] = (235, 225, 200, 255)

    d = ImageDraw.Draw(part)
    if "spikes" in props:     # spikes on the stern and the masthead
        col = (230, 225, 210) if race == "Scourge" else (55, 50, 50)
        x, y = stern
        for k in range(3):
            d.line([(x - k * 2, y - 1), (x - k * 2 + 1, y - 4)], fill=col + (255,))
        tx, ty = top
        d.line([(tx, ty), (tx, ty - 3)], fill=col + (255,))
    if "figure" in props:     # a golden lion / phoenix / eagle at the bow
        x, y = bow
        d.polygon([(x - 1, y - 1), (x - 3, y - 3), (x - 1, y - 4), (x + 1, y - 2)], fill=acc + (255,))
    if "leafprow" in props:   # curling leaf prow
        x, y = bow
        d.line([(x, y), (x - 2, y - 2), (x - 2, y - 4), (x, y - 5)], fill=acc + (255,))
        _put(part, x + 1, y - 5, shade(acc, 1.3))
    if "dragon" in props:     # a green dragon head
        x, y = bow
        d.polygon([(x, y - 1), (x - 3, y - 2), (x - 4, y - 4), (x - 1, y - 4)], fill=acc + (255,))
        _put(part, x - 3, y - 4, (240, 200, 70))
    if "mask" in props:       # troll voodoo mask
        x, y = bow
        d.ellipse([x - 3, y - 4, x, y - 1], fill=(235, 225, 205, 255))
        _put(part, x - 2, y - 3, (30, 30, 30)); _put(part, x - 1, y - 3, (30, 30, 30))
    if "totem" in props:      # a small painted totem at the bow
        x, y = bow
        for k, c in enumerate(((190, 60, 40), (240, 200, 70), (60, 120, 170))):
            d.rectangle([x - 1, y - 2 - k * 2, x, y - 1 - k * 2], fill=c + (255,))
    if "stack" in props:      # smokestack at the stern
        x, y = stern
        d.rectangle([x - 3, y - 7, x - 2, y - 1], fill=(70, 70, 76, 255))
        gd = ImageDraw.Draw(glow)
        gd.ellipse([x - 5, y - 12, x - 1, y - 8], fill=(200, 200, 200, 230))
        gd.ellipse([x - 8, y - 15, x - 4, y - 11], fill=(220, 220, 220, 180))
    if "gear" in props:
        x, y = stern
        d.ellipse([x - 7, y - 4, x - 4, y - 1], fill=(205, 175, 85, 255))
        _put(part, x - 6, y - 3, (90, 80, 70))
    if "crystal" in props:    # a glowing naaru crystal at the bow and masthead
        for (x, y) in (bow, top):
            d.polygon([(x - 1, y - 1), (x, y - 5), (x + 1, y - 1)], fill=(170, 225, 255, 255))
    part = LU.outline(part)
    base.alpha_composite(part)
    if "glow" in props or "crystal" in props:   # lanterns / runes
        g = Image.new("RGBA", base.size)
        gd = ImageDraw.Draw(g)
        x, y = stern
        gd.ellipse([x - 2, y - 4, x, y - 2], fill=st["glow"] + (255,))
        if race in ("Scourge", "Forsaken", "Night Elves"):
            bx, by = bow
            gd.ellipse([bx - 1, by - 3, bx + 1, by - 1], fill=st["glow"] + (255,))
        base.alpha_composite(LU.glow_of(g, st["glow"], 1.0, 1.0))
        base.alpha_composite(g)
    base.alpha_composite(glow)
    # keep the owner-colour layers, minus anything the props now cover
    pp = part.load()
    for l in ls[1:]:
        lp = l.load()
        for y in range(l.height):
            for x in range(l.width):
                if pp[x, y][3] or (x, y) in removed:
                    lp[x, y] = (0, 0, 0, 0)
    return ls


# steam-era warships (content pass, Oct 2026): our own machine art (late_units), facing right
STEAM_SHIPS = {"Ironclad": "Ironclad", "Destroyer": "Destroyer", "Dreadnought": "Battleship",
               "Juggernaught": "Missile Cruiser"}


def style_steam(ls, race, unit):
    """Re-plate one of our steam warships in a race's hull colour and trim, with a pennant
    in its sail colour and its lore touches (figurehead, spikes, lanterns, crystals...).
    The owner-colour layers are kept."""
    st = SHIP_STYLE[race]
    ls = [l.copy().convert("RGBA") for l in ls]
    base = ls[0]
    px = base.load()
    hull, cloth = set(), set()
    for y in range(base.height):
        for x in range(base.width):
            p = px[x, y]
            if p[3] < 200:
                continue
            h, sat, v = _hsv(p)
            if y > 30 and 0.12 < v < 0.75 and (sat < 0.25 or 0.03 < h < 0.16):
                hull.add((x, y))
            elif unit == "Juggernaught" and sat < 0.1 and v > 0.8 and y < 30:
                cloth.add((x, y))
    # metal plating takes the race's hull colour (lighter so it reads at sea); the top rail is trimmed
    plate = st["hull"]
    while sum(plate) < 300:          # dark hulls (Forsaken, Scourge, Dark Irons) are lifted so they read at sea
        plate = shade(plate, 1.15)
    for (x, y) in hull:
        v = _hsv(px[x, y])[2]
        px[x, y] = _tone(plate, v, 0.45, 0.95) + (255,)
    for (x, y) in hull:
        if (x, y - 1) not in hull and px[x, y - 1][3] < 200:
            px[x, y] = st["acc"] + (255,)
    for (x, y) in cloth:
        px[x, y] = _tone(st["sail"], _hsv(px[x, y])[2], 0.4, 0.7) + (255,)
    if not hull:
        return ls
    bow = max(hull, key=lambda p: (p[0] - p[1] * 0.4))           # right-hand tip
    stern = min(hull, key=lambda p: (p[0] + p[1] * 0.4))
    top = min((p for p in hull), key=lambda p: p[1])
    mast = min(((x, y) for y in range(base.height) for x in range(base.width)
                if px[x, y][3] > 200 and _hsv(px[x, y])[2] < 0.55), key=lambda p: p[1])   # skip the smoke
    props, acc = st["props"], st["acc"]
    part = Image.new("RGBA", base.size)
    d = ImageDraw.Draw(part)
    # a pennant in the race's sail colour at the masthead
    mx, my = mast
    d.polygon([(mx, my), (mx - 6, my + 1), (mx, my + 3)], fill=st["sail"] + (255,))
    if "figure" in props or "leafprow" in props or "dragon" in props or "mask" in props or "totem" in props:
        x, y = bow
        d.polygon([(x, y - 1), (x + 2, y - 3), (x + 1, y - 5), (x - 1, y - 3)], fill=acc + (255,))
    if "spikes" in props:
        col = (230, 225, 210) if race == "Scourge" else (60, 52, 50)
        sx, sy = stern
        for k in range(3):
            d.line([(sx + 1 + k * 2, sy - 2), (sx - 1 + k * 2, sy - 5)], fill=col + (255,))
        bx, by = bow
        d.line([(bx, by - 1), (bx + 3, by - 2)], fill=col + (255,))
    if "rivets" in props:
        for (x, y) in hull:
            if x % 4 == 0 and (x, y - 2) not in hull and (x, y - 1) in hull:
                _put(base, x, y, shade(plate, 1.45))
    if "stripes" in props or "patches" in props:
        for (x, y) in hull:
            if (x // 3) % 3 == 0 and (x, y - 2) not in hull and (x, y - 1) in hull:
                _put(base, x, y, _tone(acc, 0.9))
    if "crystal" in props:
        x, y = bow
        d.polygon([(x - 2, y - 2), (x - 1, y - 7), (x, y - 2)], fill=(170, 225, 255, 255))
    if "gear" in props:
        x, y = stern
        d.ellipse([x + 1, y - 6, x + 4, y - 3], fill=(205, 175, 85, 255))
    part = LU.outline(part)
    base.alpha_composite(part)
    if "glow" in props or "crystal" in props:
        g = Image.new("RGBA", base.size)
        gd = ImageDraw.Draw(g)
        for (x, y) in (stern, (bow[0] - 4, bow[1] - 2)):
            gd.ellipse([x + 1, y - 3, x + 3, y - 1], fill=st["glow"] + (255,))
        base.alpha_composite(LU.glow_of(g, st["glow"], 1.0, 1.0))
        base.alpha_composite(g)
    pp = part.load()
    for l in ls[1:]:
        lp = l.load()
        for y in range(l.height):
            for x in range(l.width):
                if pp[x, y][3]:
                    lp[x, y] = (0, 0, 0, 0)
    return ls


def ship_sprites(atlas):
    """{"Longboat-Orcs": [base, -1, -2], "Ironclad-Orcs": ..., ...}"""
    out = {}
    for unit, src in SHIPS.items():
        ls = [atlas.crop(P_UNITS + src + s) for s in ("", "-1", "-2")]
        for race in SHIP_STYLE:
            out["%s-%s" % (unit, race)] = style_ship(ls, race, unit)
    for unit, src in STEAM_SHIPS.items():
        ls = LU.source_layers(atlas, src)
        for race in SHIP_STYLE:
            out["%s-%s" % (unit, race)] = style_steam(ls, race, unit)
    return out


# ======================================================================= camps and forts
TW, TH = 64, 56


FIRE = {"Forsaken": (140, 240, 90), "Scourge": (120, 200, 255), "Draenei": (170, 150, 255),
        "Dark Iron Dwarves": (255, 120, 40), "Naga": (120, 240, 220), "Nightborne": (200, 150, 255)}

# race: shelter kind and colours for the hunting camp, plus a camp prop
CAMP = {
    "Humans":      dict(kind="tent", wall=(235, 230, 215), roof=(232, 226, 210), prop="pennant"),
    "Orcs":        dict(kind="spiky", wall=(125, 80, 50), roof=(150, 70, 45), prop="tusks"),
    "Night Elves": dict(kind="leaf", wall=(215, 215, 235), roof=(110, 80, 170), prop="moonlamp"),
    "Dwarves":     dict(kind="flat", wall=(150, 140, 130), roof=(100, 95, 92), prop="keg"),
    "Gnomes":      dict(kind="dome", wall=(160, 170, 180), roof=(60, 150, 150), prop="gear"),
    "Tauren":      dict(kind="tent", wall=(190, 140, 90), roof=(195, 150, 100), prop="totem", painted=True),
    "Trolls":      dict(kind="thatch", wall=(150, 120, 80), roof=(190, 165, 90), prop="mask"),
    "Blood Elves": dict(kind="tent", wall=(190, 40, 45), roof=(190, 40, 45), prop="orb", trim=(240, 200, 70)),
    "High Elves":  dict(kind="tent", wall=(240, 240, 248), roof=(240, 240, 248), prop="pennant_blue", trim=(50, 100, 200)),
    "Pandaren":    dict(kind="pagoda", wall=(180, 50, 40), roof=(40, 130, 110), prop="lantern"),
    "Forsaken":    dict(kind="tent", wall=(95, 92, 100), roof=(95, 90, 102), prop="cauldron"),
    "Scourge":     dict(kind="spiky", wall=(80, 90, 110), roof=(45, 55, 75), prop="bones"),
    "Draenei":     dict(kind="dome", wall=(160, 145, 200), roof=(110, 90, 170), prop="crystal"),
    "Goblins":     dict(kind="flat", wall=(150, 110, 70), roof=(190, 90, 40), prop="barrel"),
    "Worgen":      dict(kind="gable", wall=(130, 125, 120), roof=(55, 60, 70), prop="lamppost"),
    "Dark Iron Dwarves": dict(kind="flat", wall=(80, 70, 70), roof=(50, 45, 46), prop="keg"),
    "Kul Tirans":  dict(kind="tent", wall=(230, 225, 210), roof=(40, 85, 110), prop="pennant_blue", trim=(230, 220, 190)),
    "Zandalari Trolls": dict(kind="thatch", wall=(185, 160, 105), roof=(235, 195, 70), prop="mask"),
    "Naga": dict(kind="dome", wall=(80, 150, 140), roof=(40, 110, 120), prop="crystal"),
    "Nightborne": dict(kind="dome", wall=(190, 180, 215), roof=(90, 50, 150), prop="orb", trim=(232, 200, 110)),
    "Highmountain Tauren": dict(kind="tent", wall=(170, 130, 90), roof=(120, 90, 60), prop="totem", painted=True),
}


def camp(race):
    """The race's hunting camp (drawn by improvement_art.py with the city-center renderer)."""
    import improvement_art as IA
    return IA.camp(race)


# ------------------------------------------------------------------ forts
# race: wall kind, wall colour, roof kind and colour for the corner towers and keep, banner
FORT = {
    "Humans":      dict(wall="stone", col=(200, 198, 190), roof="spire", rcol=(40, 70, 160), flag=(40, 70, 160)),
    "Orcs":        dict(wall="palisade", col=(120, 82, 52), roof="spiky", rcol=(70, 62, 60), flag=(170, 30, 25)),
    "Night Elves": dict(wall="thorn", col=(95, 80, 115), roof="leaf", rcol=(110, 80, 170), flag=(150, 210, 255)),
    "Dwarves":     dict(wall="stone", col=(135, 125, 118), roof="flat", rcol=(100, 95, 92), flag=(30, 70, 150), heavy=True),
    "Gnomes":      dict(wall="metal", col=(150, 158, 168), roof="dome", rcol=(60, 150, 150), flag=(240, 160, 200)),
    "Tauren":      dict(wall="palisade", col=(170, 120, 75), roof="tent", rcol=(195, 150, 100), flag=(190, 60, 40)),
    "Trolls":      dict(wall="palisade", col=(175, 150, 85), roof="thatch", rcol=(190, 165, 90), flag=(60, 140, 120)),
    "Blood Elves": dict(wall="stone", col=(235, 225, 205), roof="spire", rcol=(180, 30, 40), flag=(170, 25, 35),
                        trim=(240, 200, 70)),
    "High Elves":  dict(wall="stone", col=(235, 235, 240), roof="spire", rcol=(50, 100, 200), flag=(50, 100, 200),
                        trim=(220, 200, 120)),
    "Pandaren":    dict(wall="lacquer", col=(175, 55, 42), roof="pagoda", rcol=(40, 130, 110), flag=(240, 200, 70)),
    "Forsaken":    dict(wall="stone", col=(95, 95, 105), roof="spire", rcol=(60, 55, 70), flag=(120, 60, 140),
                        lamp=(140, 240, 90)),
    "Scourge":     dict(wall="saronite", col=(70, 82, 102), roof="spiky", rcol=(45, 55, 75), flag=(130, 200, 245),
                        lamp=(120, 200, 255)),
    "Draenei":     dict(wall="stone", col=(165, 150, 205), roof="spire", rcol=(110, 90, 170), flag=(160, 210, 255),
                        lamp=(170, 150, 255)),
    "Goblins":     dict(wall="metal", col=(150, 105, 70), roof="flat", rcol=(190, 90, 40), flag=(240, 200, 60), rust=True),
    "Worgen":      dict(wall="stone", col=(118, 115, 112), roof="gable", rcol=(55, 60, 70), flag=(120, 40, 40)),
    "Dark Iron Dwarves": dict(wall="stone", col=(78, 70, 70), roof="flat", rcol=(45, 40, 42), flag=(255, 120, 30), heavy=True,
                              lamp=(255, 130, 50)),
    "Kul Tirans":  dict(wall="stone", col=(205, 200, 188), roof="spire", rcol=(30, 70, 95), flag=(30, 80, 110)),
    "Zandalari Trolls": dict(wall="palisade", col=(195, 170, 100), roof="thatch", rcol=(235, 195, 70), flag=(40, 130, 110)),
    "Naga": dict(wall="stone", col=(90, 150, 140), roof="spire", rcol=(40, 110, 120), flag=(120, 230, 210), lamp=(120, 240, 220)),
    "Nightborne": dict(wall="stone", col=(195, 185, 220), roof="spire", rcol=(90, 50, 150), flag=(175, 125, 255),
                       trim=(232, 200, 110), lamp=(200, 150, 255)),
    "Highmountain Tauren": dict(wall="palisade", col=(160, 120, 80), roof="tent", rcol=(120, 90, 60), flag=(125, 200, 225)),
}

def fort(race):
    """The race's walled outpost (drawn by improvement_art.py with the city-center renderer)."""
    import improvement_art as IA
    return IA.fort(race)


def snow(im):
    """Snow on every upward-facing edge (for the tundra 'T' variants)."""
    out = im.copy()
    a = im.load(); o = out.load()
    for y in range(im.height):
        for x in range(im.width):
            above = a[x, y - 1] if y else (0, 0, 0, 0)
            if a[x, y][3] > 200 and a[x, y][:3] != DARK and (above[3] < 60 or above[:3] == DARK) \
                    and sum(a[x, y][:3]) > 150:
                o[x, y] = (245, 248, 252, 255)
                if y + 1 < im.height and a[x, y + 1][3] > 200 and (x + y) % 2:
                    o[x, y + 1] = (225, 232, 240, 255)
    return out


# ------------------------------------------------------------------ writing the tiles
def _owners(nations, city_states):
    """Owner name -> race style (city-states borrow the style of their city center)."""
    out = {n: n for n in nations if n in CAMP}
    for cs in city_states:
        st = CC.CITY_STATE_STYLE.get(cs)
        if st == "_dalaran":
            st = "High Elves"
        if st in CAMP:
            out[cs] = st
    return out


def _load(name, tiles_dir, atlas, back):
    path = os.path.join(tiles_dir, name + ".png")
    if os.path.exists(path):
        return Image.open(path).convert("RGBA")
    stock = HEX + back(name)
    if stock in atlas.regions:
        return atlas.crop(stock).convert("RGBA")
    return None


def _camp_offset(combined, camp_img):
    """Where the stock camp sits inside a combined image (it moves to make room)."""
    o, c = combined.load(), camp_img.load()
    w, h = combined.size
    pts = [(x, y, c[x, y][:3]) for x in range(w) for y in range(h) if c[x, y][3] > 200]
    best, bo = -1, (0, 0)
    for dx in range(-16, 17):
        for dy in range(-16, 17):
            k = 0
            for x, y, col in pts:
                X, Y = x + dx, y + dy
                if 0 <= X < w and 0 <= Y < h and o[X, Y][3] > 200 and o[X, Y][:3] == col:
                    k += 1
            if k > best:
                best, bo = k, (dx, dy)
    return bo


def _without_camp(combined, camp_img):
    """The resource part of a stock 'X+Camp' image: drop the stock camp's pixels."""
    dx, dy = _camp_offset(combined, camp_img)
    out = combined.copy()
    o, c = out.load(), camp_img.load()
    w, h = out.size
    mask = [[False] * h for _ in range(w)]
    for x in range(w):
        for y in range(h):
            if c[x, y][3]:
                for ex in (-1, 0, 1):
                    for ey in (-1, 0, 1):
                        X, Y = x + dx + ex, y + dy + ey
                        if 0 <= X < w and 0 <= Y < h:
                            mask[X][Y] = True
    palette = {c[x, y][:3] for x in range(w) for y in range(h) if c[x, y][3]}
    for x in range(w):
        for y in range(h):
            p = o[x, y]
            if not p[3] or not mask[x][y]:
                continue
            hh, s, v = _hsv(p)
            if p[:3] in palette or (s < 0.12 and v > 0.6) or p[3] < 200:
                o[x, y] = (0, 0, 0, 0)
    return out, (dx, dy)


def write_tiles(out_dir, tiles_atlas, nations, city_states, renames, rule_variants):
    """Write "<image>-<owner>" camp and fort tiles into the HexaRealm tile folder."""
    import re
    tiles_dir = os.path.join(out_dir, HEX)
    back_map = {v: k for k, v in renames.items()}
    def back(name):
        return "+".join(back_map.get(t, t) for t in name.split("+"))
    names = {"Camp", "Fort", "FortT"}
    pat = re.compile(r"^(.+)\+(Camp|CampT)$")
    for f in os.listdir(tiles_dir):
        if pat.match(f[:-4]):
            names.add(f[:-4])
    for vals in rule_variants.values():
        for v in vals:
            if pat.match(v) or v in ("Fort", "FortT"):
                names.add(v)
    stock_camp = tiles_atlas.crop(HEX + "Camp").convert("RGBA")
    owners = _owners(nations, city_states)
    camps = {r: camp(r) for r in set(owners.values())}
    forts = {r: fort(r) for r in set(owners.values())}
    n = 0
    for name in sorted(names):
        m = pat.match(name)
        if m:
            combined = None
            if m.group(2) == "CampT":     # the snowy camp is harder to cut out: use the plain one
                combined = _load(m.group(1) + "+Camp", tiles_dir, tiles_atlas, back)
            combined = combined or _load(name, tiles_dir, tiles_atlas, back)
            if combined is None:
                continue
            resource, off = _without_camp(combined, stock_camp)
            snowy = m.group(2) == "CampT" or m.group(1).endswith("T")
        elif name == "Camp":
            resource, snowy, off = None, False, (0, 0)
        else:
            resource, snowy, off = None, name == "FortT", (0, 0)
        for owner, race in owners.items():
            im = Image.new("RGBA", (TW, TH))
            art = camps[race] if "Camp" in name else forts[race]
            art = snow(art) if snowy else art
            if "Camp" in name and off != (0, 0):
                moved = Image.new("RGBA", (TW, TH))
                moved.paste(art, off, art)
                art = moved
            im.alpha_composite(art)
            if resource is not None:
                im.alpha_composite(resource)
            im.save(os.path.join(tiles_dir, "%s-%s.png" % (name, owner)))
            n += 1
    return n
