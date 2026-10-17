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
from mounts import Paint, shade
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


def ship_sprites(atlas):
    """{"Longboat-Orcs": [base, -1, -2], ...}"""
    out = {}
    for unit, src in SHIPS.items():
        ls = [atlas.crop(P_UNITS + src + s) for s in ("", "-1", "-2")]
        for race in SHIP_STYLE:
            out["%s-%s" % (unit, race)] = style_ship(ls, race, unit)
    return out


# ======================================================================= camps and forts
TW, TH = 64, 56


class Scene(CC.Scene):
    def piece(self, depth, fn, outline=DARK, glow=None):
        p = Paint(TW, TH)
        fn(p)
        im = p.render(outline)[0] if outline else p.render(None)[0]
        if glow:
            g = Image.new("RGBA", (TW, TH))
            g.alpha_composite(CC.glow_of(im, glow))
            g.alpha_composite(im)
            im = g
        self.add(depth, im)

    def render(self):
        out = Image.new("RGBA", (TW, TH))
        for _, im in sorted(self.items, key=lambda t: t[0]):
            out.alpha_composite(im)
        return out


FIRE = {"Forsaken": (140, 240, 90), "Scourge": (120, 200, 255), "Draenei": (170, 150, 255)}

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
}


def campfire(s, x, y, col):
    def stones(p):
        p.ell(x, y, 4, 2, (120, 115, 110), "ring")
        p.ell(x, y - 0.5, 2.5, 1.2, (60, 45, 35), "ash")
    s.piece(y, stones)
    def flame(p):
        p.poly([(x - 2, y - 1), (x + 2, y - 1), (x + 0.5, y - 6), (x - 0.5, y - 4)], col, "flame")
        p.dot(x, y - 2, (255, 245, 200), "core")
    s.piece(y + 0.5, flame, outline=None, glow=col)


def rack(s, x, y, hide=(170, 120, 80)):
    """A hide stretched on a round hoop frame, propped on a stick."""
    def f(p):
        p.line(x + 3, y, x + 6, y - 9, 1, (100, 70, 45), "stick")
        p.ell(x + 3, y - 6, 4.5, 5.5, (110, 78, 48), "hoop")
        p.ell(x + 3, y - 6, 3.2, 4.2, hide, "hide")
        p.dot(x + 2, y - 7, shade(hide, 1.15), "hl")
    s.piece(y, f)


def camp_prop(s, race, prop, x, y):
    if prop in ("pennant", "pennant_blue"):
        s.piece(y, lambda p: CC.banner(p, x, y, (100, 80, 60), (40, 70, 160) if prop == "pennant" else (50, 100, 200), 10))
    elif prop == "tusks":
        def f(p):
            p.line(x - 2, y, x - 4, y - 7, 1, (235, 225, 200), "tusk")
            p.line(x + 2, y, x + 4, y - 7, 1, (235, 225, 200), "tusk2")
            CC.banner(p, x, y, (60, 50, 45), (170, 30, 25), 11)
        s.piece(y, f)
    elif prop == "moonlamp":
        s.piece(y, lambda p: (p.line(x, y, x, y - 8, 1, (90, 70, 110), "pole"),
                              p.line(x, y - 8, x + 2, y - 10, 1, (90, 70, 110), "hook")))
        s.piece(y + 0.5, lambda p: p.ell(x + 2, y - 9, 1.5, 1.5, (170, 225, 255), "moon"), glow=(150, 210, 255))
    elif prop == "keg":
        def f(p):
            p.ell(x, y - 3, 3, 3.5, (150, 100, 55), "keg")
            p.line(x - 3, y - 4, x + 3, y - 4, 1, (90, 85, 80), "hoop")
            p.line(x - 3, y - 1.5, x + 3, y - 1.5, 1, (90, 85, 80), "hoop2")
        s.piece(y, f)
    elif prop == "gear":
        def f(p):
            p.ell(x, y - 4, 3.5, 3.5, (200, 170, 80), "gear")
            p.ell(x, y - 4, 1.2, 1.2, (90, 80, 70), "hub")
            for k in range(8):
                a = k * math.pi / 4
                p.dot(x + math.cos(a) * 4.5, y - 4 + math.sin(a) * 4.5, (200, 170, 80), "gear")
        s.piece(y, f)
    elif prop == "totem":
        def f(p):
            for k, c in enumerate(((200, 60, 40), (240, 200, 70), (60, 120, 170))):
                p.poly([(x - 1.5, y - k * 3), (x + 1.5, y - k * 3), (x + 1.5, y - 3 - k * 3), (x - 1.5, y - 3 - k * 3)], c, "t%d" % k)
            p.line(x - 3.5, y - 9, x + 3.5, y - 9, 1, (240, 200, 70), "wing")
        s.piece(y, f)
    elif prop == "mask":
        def f(p):
            p.line(x, y, x, y - 9, 1, (110, 80, 50), "pole")
            p.ell(x, y - 9, 2.2, 2.6, (235, 225, 205), "mask")
            p.dot(x - 1, y - 10, (30, 30, 30), "eye"); p.dot(x + 1, y - 10, (30, 30, 30), "eye2")
            p.line(x - 1, y - 7.5, x + 1, y - 7.5, 1, (190, 50, 40), "paint")
        s.piece(y, f)
    elif prop == "orb":
        s.piece(y, lambda p: p.line(x, y, x, y - 5, 1, (220, 180, 70), "stand"))
        s.piece(y + 0.5, lambda p: p.ell(x, y - 9, 1.8, 1.8, (255, 200, 90), "orb"), glow=(255, 170, 60))
    elif prop == "lantern":
        s.piece(y, lambda p: (p.line(x, y, x, y - 9, 1, (90, 60, 40), "pole"), p.line(x, y - 9, x + 3, y - 9, 1, (90, 60, 40), "arm")))
        s.piece(y + 0.5, lambda p: p.ell(x + 3, y - 7, 1.5, 2, (230, 70, 50), "lantern"), glow=(255, 120, 60))
    elif prop == "cauldron":
        s.piece(y, lambda p: (p.ell(x, y - 2, 3.5, 2.5, (50, 48, 52), "pot"),))
        s.piece(y + 0.5, lambda p: p.ell(x, y - 4, 2.5, 0.9, (140, 240, 90), "brew"), glow=(130, 230, 80))
    elif prop == "bones":
        def f(p):
            for k in (-3, 0, 3):
                p.line(x + k, y, x + k * 1.3, y - 7, 1, (225, 222, 205), "rib%d" % k)
            p.ell(x, y - 8, 1.8, 1.5, (225, 222, 205), "skull")
        s.piece(y, f)
    elif prop == "crystal":
        s.piece(y + 0.5, lambda p: (p.poly([(x - 2, y), (x + 2, y), (x + 1, y - 8), (x - 1, y - 9)], (170, 150, 255), "cr"),
                                    p.poly([(x, y), (x + 2, y), (x + 1, y - 8)], (210, 200, 255), "crh")),
                glow=(160, 140, 255))
    elif prop == "barrel":
        def f(p):
            p.ell(x, y - 3, 3, 3.5, (110, 115, 120), "barrel")
            p.line(x - 3, y - 4, x + 3, y - 4, 1, (190, 90, 40), "band")
            p.dot(x, y - 6, (240, 210, 60), "fuse")
        s.piece(y, f)
    elif prop == "lamppost":
        s.piece(y, lambda p: (p.line(x, y, x, y - 10, 1, (50, 50, 55), "post"),))
        s.piece(y + 0.5, lambda p: p.ell(x, y - 10, 1.4, 1.6, (255, 215, 120), "lamp"), glow=(255, 200, 100))


def shelter(s, st, x, y, w=13, h=6):
    kind = st["kind"]
    def f(p):
        if kind == "tent" and not st.get("painted"):            # a ridge tent of canvas or silk
            p.poly([(x, y), (x + w, y), (x + w / 2, y - h - 5)], st["roof"], "front")
            p.poly([(x + w / 2, y - h - 5), (x + w, y), (x + w + 6, y - 3), (x + w / 2 + 6, y - h - 8)],
                   shade(st["roof"], 0.8), "side")
            p.poly([(x + w / 2 - 1.5, y), (x + w / 2 + 1.5, y), (x + w / 2, y - 4)], (60, 45, 35), "door")
            if st.get("trim"):
                p.line(x + 1, y - 1, x + w / 2, y - h - 4, 1, st["trim"], "trim")
                p.line(x + w / 2, y - h - 4, x + w - 1, y - 1, 1, st["trim"], "trim2")
        else:
            CC.house(p, x, y, w, h, st["wall"], st["roof"], kind=kind,
                     rh=(w * 0.9 if kind in ("cone", "tent") else w * 0.5 if kind == "thatch" else None),
                     trim=st.get("trim"))
    s.piece(y, f)


def camp(race):
    st = CAMP[race]
    s = Scene()
    shelter(s, st, 13, 28)
    rack(s, 6, 33, (110, 90, 70) if race in ("Forsaken", "Scourge") else (175, 125, 80))
    campfire(s, 39, 29, FIRE.get(race, (255, 150, 50)))
    camp_prop(s, race, st["prop"], 49, 27)
    return s.render()


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
}

# hexagon of wall foot points, back (top) to front
HL, HTL, HTR, HR, HBR, HBL = (7, 28), (17, 12), (47, 12), (57, 28), (47, 47), (17, 47)
BACK = [(HL, HTL), (HTL, HTR), (HTR, HR)]
FRONT = [(HR, HBR), (HBL, HL), (HBR, HBL)]


def _wall_segment(p, a, b, st, h, part):
    col = st["col"]
    kind = st["wall"]
    (x0, y0), (x1, y1) = a, b
    n = max(1, int(math.hypot(x1 - x0, y1 - y0)))
    face = shade(col, 0.85 if y1 != y0 else 1.0)
    if kind in ("palisade",):                  # sharpened log stakes
        for i in range(0, n + 1, 2):
            t = i / n
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            c = col if i % 4 == 0 else shade(col, 0.85)
            p.poly([(x - 1, y), (x + 1, y), (x + 1, y - h), (x, y - h - 2), (x - 1, y - h)], c, part)
        return
    if kind == "thorn":                        # living wood: twisting roots and thorns
        p.poly([(x0, y0), (x1, y1), (x1, y1 - h + 1), (x0, y0 - h + 1)], face, part)
        for i in range(0, n + 1, 3):
            t = i / n
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            p.line(x, y - h + 1, x + (1 if i % 2 else -1), y - h - 2, 1, shade(col, 1.25), part)
            if i % 6 == 0:
                p.ell(x, y - h, 1.6, 1.2, (90, 160, 100), part + "leaf")
        return
    p.poly([(x0, y0), (x1, y1), (x1, y1 - h), (x0, y0 - h)], face, part)
    top = shade(col, 1.12)
    p.line(x0, y0 - h, x1, y1 - h, 1, top, part + "top")
    for i in range(0, n + 1, 3):
        t = i / n
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        if kind == "stone":                    # crenellations
            if (i // 3) % 2 == 0:
                p.poly([(x - 1, y - h), (x + 1, y - h), (x + 1, y - h - 2), (x - 1, y - h - 2)], top, part)
            if st.get("trim"):
                p.dot(x, y - h + 1, st["trim"], part + "trim")
        elif kind == "metal":                  # riveted plates
            p.dot(x, y - h / 2, shade(col, 1.4) if not st.get("rust") else (190, 90, 40), part + "rivet")
            if (i // 3) % 3 == 0:
                p.line(x, y, x, y - h, 1, shade(col, 0.7), part + "seam")
        elif kind == "lacquer":                # red wall with a green tiled cap
            p.line(x - 1.5, y - h - 0.5, x + 1.5, y - h - 0.5, 1, st["rcol"], part + "cap")
        elif kind == "saronite":               # dark metal with bone spikes
            if (i // 3) % 2 == 0:
                p.line(x, y - h, x + 0.5, y - h - 3, 1, (225, 222, 205), part + "spike")
            p.dot(x, y - h / 2, (120, 200, 255), part + "rune")


def fort(race):
    st = FORT[race]
    h = 7 if st.get("heavy") else 6
    s = Scene()
    def back(p):
        for i, (a, b) in enumerate(BACK):
            _wall_segment(p, a, b, st, h, "b%d" % i)
    s.piece(10, back)
    # keep and barracks inside
    rk = st["roof"]
    def keep(p):
        CC.tower(p, 27, 32, 9, 14, st["col"], st["rcol"], kind=rk,
                 rh=(5 if rk not in ("tent", "thatch") else 9), trim=st.get("trim"))
    s.piece(32, keep)
    s.piece(36, lambda p: CC.house(p, 14, 36, 10, 5, st["col"], st["rcol"], kind=rk if rk not in ("pagoda",) else "hip",
                                   rh=(9 if rk in ("tent",) else None), trim=st.get("trim")))
    s.piece(34, lambda p: CC.banner(p, 44, 34, (80, 70, 60), st["flag"], 12))
    if st.get("lamp"):
        s.piece(37, lambda p: p.ell(40, 35, 1.4, 1.4, st["lamp"], "lamp"), outline=None, glow=st["lamp"])
    def front(p):
        for i, (a, b) in enumerate(FRONT):
            _wall_segment(p, a, b, st, h, "f%d" % i)
        gx, gy = 32, 47           # the gate
        p.poly([(gx - 3, gy), (gx + 3, gy), (gx + 3, gy - 5), (gx, gy - 6.5), (gx - 3, gy - 5)], (60, 40, 30), "gate")
    s.piece(48, front)
    for (tx, ty) in (HL, HR):     # corner towers
        s.piece(ty + 1, lambda p, tx=tx, ty=ty: CC.tower(p, tx - 3.5, ty + 1, 7, 11, st["col"], st["rcol"],
                                                         kind=rk if rk != "pagoda" else "hip",
                                                         rh=(4 if rk not in ("tent", "thatch") else 7), trim=st.get("trim")))
    return s.render()


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
