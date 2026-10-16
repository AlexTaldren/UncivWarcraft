"""Race-specific map sprites, generated from Unciv's AbsoluteUnits pixel art.

For every person-type unit and every race, this writes "<Unit>-<Race>" sprite layers,
which Unciv picks automatically for units owned by that race. Each race gets:
  - its own skin palette (green orcs, blue/teal/purple trolls, furred tauren, ...)
  - body proportions (stocky dwarves, small gnomes, tall lanky trolls, huge tauren)
  - features drawn in pixel art: beards, tusks, horns, long ears, panda masks
The design follows broad fantasy archetypes, not Blizzard's artwork.
"""
import colorsys, hashlib, os, random
from PIL import Image

P = "TileSets/AbsoluteUnits/Units/"


# ------------------------------------------------------------------ helpers
def is_skin(px):
    r, g, b, a = px
    if a < 200:
        return False
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return 0.02 <= h <= 0.085 and 0.22 <= s <= 0.55 and 0.38 <= v <= 0.80


def ramp(c1, c2, n):
    return [tuple(int(c1[i] + (c2[i] - c1[i]) * k / (n - 1)) for i in range(3)) for k in range(n)]


def recolor_skin(im, palette):
    """Map each skin pixel to the palette by brightness, keeping the shading."""
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            p = px[x, y]
            if is_skin(p):
                v = max(p[:3]) / 255
                t = min(1, max(0, (v - 0.40) / 0.35))
                c = palette[int(t * (len(palette) - 1) + 0.5)]
                px[x, y] = c + (p[3],)
    return im


def bbox_all(layers):
    boxes = [l.getbbox() for l in layers if l.getbbox()]
    return (min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes))


def reshape(layers, sx, sy):
    """Scale the figure around its feet (bottom centre), identically on every layer."""
    if sx == 1 and sy == 1:
        return layers
    x0, y0, x1, y1 = bbox_all(layers)
    w, h = x1 - x0, y1 - y0
    nw, nh = max(1, round(w * sx)), max(1, round(h * sy))
    cx, bottom = (x0 + x1) / 2, y1
    out = []
    for l in layers:
        piece = l.crop((x0, y0, x1, y1)).resize((nw, nh), Image.NEAREST)
        canvas = Image.new("RGBA", l.size)
        canvas.alpha_composite(piece, (int(round(cx - nw / 2)), max(0, bottom - nh)))
        out.append(canvas)
    return out


def head_box(base):
    """Locate the face: skin pixels in the upper part of the figure."""
    x0, y0, x1, y1 = base.getbbox()
    px = base.load()
    pts = [(x, y) for y in range(y0, y0 + int((y1 - y0) * 0.42)) for x in range(x0, x1) if is_skin(px[x, y])]
    if len(pts) < 3:
        return None
    # keep the topmost cluster (the head), not hands raised high
    top = min(p[1] for p in pts)
    pts = [p for p in pts if p[1] <= top + 6]
    xs = sorted(p[0] for p in pts)
    mid = xs[len(xs) // 2]
    pts = [p for p in pts if abs(p[0] - mid) <= 4]
    return (min(p[0] for p in pts), min(p[1] for p in pts),
            max(p[0] for p in pts), max(p[1] for p in pts))


def put(px, w, h, x, y, c):
    if 0 <= x < w and 0 <= y < h:
        px[x, y] = c + (255,)


# ------------------------------------------------------------------ features
# Figures in this art face right; features are drawn as small pixel shapes in a
# separate layer, then outlined in dark pixels like the rest of the art.
OUTLINE = (30, 24, 22)
OVERLAYS = []   # set by make(): the tinted layers that sit on top of the base


class Feature:
    def __init__(self, size):
        self.layer = Image.new("RGBA", size)
        self.px = self.layer.load()
        self.w, self.h = size

    def dot(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[x, y] = tuple(c) + (255,)

    def apply(self, base, outline=True):
        ol = None
        if outline:
            ol = Image.new("RGBA", base.size)
            op, bp = ol.load(), base.load()
            for y in range(self.h):
                for x in range(self.w):
                    if self.px[x, y][3]:
                        continue
                    if any(0 <= x + dx < self.w and 0 <= y + dy < self.h and self.px[x + dx, y + dy][3]
                           for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) and bp[x, y][3] < 200:
                        op[x, y] = OUTLINE + (255,)
            base.alpha_composite(ol)
        base.alpha_composite(self.layer)
        # the faction-colour layers are drawn over the base: clear them where we drew
        for other in OVERLAYS:
            opx = other.load()
            for y in range(self.h):
                for x in range(self.w):
                    if self.px[x, y][3] or (ol is not None and ol.getpixel((x, y))[3]):
                        opx[x, y] = (0, 0, 0, 0)


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


def beard(base, hb, color, length):
    f = Feature(base.size)
    x0, y0, x1, y1 = hb
    top = y1 - 1
    for dy in range(length):
        inset = max(0, dy - (length * 2) // 3)          # full, then tapering to a point
        for x in range(x0 - 1 + inset, x1 + 2 - inset):
            strand = (x - x0) % 2 == 0                      # vertical strands of hair
            f.dot(x, top + dy, shade(color, 1.15) if strand else color)
    for x in range(x0, x1 + 1):                          # moustache
        f.dot(x, top - 1, shade(color, 0.85))
    f.apply(base)


def tusks(base, hb, length, curl):
    f = Feature(base.size)
    x0, y0, x1, y1 = hb
    bone = (245, 240, 220)
    for fx, side in ((x1, 1), (x0 + 1, -1)):             # front tusk, back tusk
        for i in range(length):
            f.dot(fx + (side if curl and i == length - 1 else 0), y1 - i, bone)
    f.apply(base)


def horns(base, hb, color, style):
    f = Feature(base.size)
    x0, y0, x1, y1 = hb
    if style == "bull":       # wide, sweeping out then up
        shape = [(0, 0), (1, 0), (2, -1), (3, -2), (3, -3), (4, -4)]
    else:                     # draenei: sweeping back and down from the brow
        shape = [(0, 0), (1, 0), (2, 1), (2, 2)]
    for i, (dx, dy) in enumerate(shape):
        c = shade(color, 1.0 - 0.08 * i)
        f.dot(x1 + 1 + dx, y0 + dy, c)                    # front horn
        f.dot(x0 - 1 - dx, y0 + dy, shade(c, 0.85))       # back horn
    f.apply(base)


def ears(base, hb, skin, length, upward):
    f = Feature(base.size)
    x0, y0, x1, y1 = hb
    ey = y0 + (y1 - y0) // 2
    for i in range(1, length + 1):
        dy = -i if upward else -(i // 3)
        f.dot(x0 - i, ey + dy, skin)                      # back ear, fully visible
        if upward and i > 1:
            f.dot(x0 - i + 1, ey + dy, shade(skin, 0.85))  # give it some thickness
    for i in range(1, max(2, length // 2) + 1):          # front ear peeks out
        f.dot(x1 + i, ey - (i if upward else 0), skin)
    f.apply(base)


def topknot(base, hb, color, height, crest):
    """Hair on top of the head: an orc topknot or a tall troll crest."""
    f = Feature(base.size)
    x0, y0, x1, y1 = hb
    cx = (x0 + x1) // 2
    if crest:
        for i in range(height):
            for x in range(cx - 1, cx + 1):
                f.dot(x - i // 2, y0 - 1 - i, shade(color, 1.0 - 0.05 * i))
    else:
        for x in range(x0, x1 + 1):
            f.dot(x, y0 - 1, color)
        for i in range(height):
            f.dot(x0 - 1, y0 + i, color)                  # hair at the back
    f.apply(base)


def panda_face(base, hb):
    f = Feature(base.size)
    x0, y0, x1, y1 = hb
    white, black = (240, 238, 230), (28, 28, 30)
    for y in range(y0 - 1, y1 + 1):
        for x in range(x0 - 1, x1 + 2):
            corner = (y in (y0 - 1, y1)) and (x in (x0 - 1, x1 + 1))
            if not corner:
                f.dot(x, y, white)
    ey = y0 + (y1 - y0) // 2
    for dx, dy in ((0, 0), (-1, 0), (0, -1)):          # eye patch on the facing side
        f.dot(x1 - 1 + dx, ey + dy, black)
    f.dot(x1 + 1, ey + 1, black)                        # nose
    for ex in (x0 - 1, x0):                             # round ears
        f.dot(ex, y0 - 2, black)
    f.dot(x1, y0 - 2, black)
    f.apply(base)


def wolf_head(base, hb, fur):
    """A worgen head: furred, a long muzzle facing right and tall pointed ears."""
    f = Feature(base.size)
    x0, y0, x1, y1 = hb
    dark, light = shade(fur, 0.7), shade(fur, 1.25)
    for y in range(y0 - 1, y1 + 1):
        for x in range(x0 - 1, x1 + 1):
            f.dot(x, y, fur if (x + y) % 4 else dark)
    my = y1 - 1
    for i in range(1, 4):                               # muzzle
        f.dot(x1 + i, my, light)
        f.dot(x1 + i, my - 1, fur)
    f.dot(x1 + 4, my - 1, (20, 20, 20))                 # nose
    f.dot(x1, y0 + 1, (230, 200, 60))                   # eye
    for i in range(3):                                  # ears
        f.dot(x0, y0 - 2 - i, dark)
        f.dot(x0 + 2, y0 - 2 - i, fur)
    f.apply(base)


def defias_mask(base, hb):
    """A Defias bandit: red hood over the head and a red kerchief over mouth and nose,
    leaving a narrow band for the eyes."""
    f = Feature(base.size)
    x0, y0, x1, y1 = hb
    red, dark = (165, 32, 30), (110, 20, 22)
    for x in range(x0 - 1, x1 + 2):                        # hood
        f.dot(x, y0 - 1, red)
        f.dot(x, y0, dark if x == x0 - 1 else red)
    for y in range(y0, y1 + 1):
        f.dot(x0 - 1, y, dark)                             # hood falls at the back
    ey = y0 + max(1, (y1 - y0) // 3)
    for y in range(ey + 1, y1 + 2):                        # kerchief
        for x in range(x0, x1 + 2):
            f.dot(x, y, red if (x + y) % 3 else dark)
    f.dot(x1 + 1, y1 + 2, dark)                            # knot tail
    f.apply(base)


def gnoll_head(base, hb):
    """A gnoll: spotted hyena head with a short snout, rounded ears and a dark mane."""
    f = Feature(base.size)
    x0, y0, x1, y1 = hb
    fur, spot, mane = (180, 140, 80), (110, 75, 40), (60, 40, 25)
    for y in range(y0 - 1, y1 + 1):
        for x in range(x0 - 1, x1 + 1):
            f.dot(x, y, spot if (x * 3 + y * 5) % 7 == 0 else fur)
    my = y1 - 1
    for i in range(1, 3):                                  # snout
        f.dot(x1 + i, my, shade(fur, 1.15))
        f.dot(x1 + i, my - 1, fur)
    f.dot(x1 + 3, my - 1, (25, 20, 18))                   # nose
    f.dot(x1, y0 + 1, (200, 60, 40))                       # red eye
    for y in range(y0 - 2, y1 + 3):                       # mane down the back
        f.dot(x0 - 2, y, mane)
    for ex in (x0, x0 + 2):                                # round ears
        f.dot(ex, y0 - 2, spot)
        f.dot(ex, y0 - 3, fur)
    f.apply(base)


def murloc_head(base, hb):
    """A murloc: big round fish head, bulging eye, wide mouth and a fin crest."""
    f = Feature(base.size)
    x0, y0, x1, y1 = hb
    skin, belly, fin = (70, 150, 120), (170, 210, 160), (220, 110, 60)
    for y in range(y0 - 1, y1 + 2):
        for x in range(x0 - 1, x1 + 2):
            f.dot(x, y, belly if y >= y1 else skin)
    for x in range(x0 + 1, x1 + 2):                        # mouth
        f.dot(x, y1 - 1, (40, 30, 35))
    f.dot(x1 + 1, y0, (250, 240, 120))                     # bulging eye
    f.dot(x1 + 1, y0 - 1, (250, 240, 120))
    f.dot(x1 + 1, y0 + 1, (20, 20, 20))
    for i, h in enumerate((2, 3, 3, 2, 1)):                # fin crest along the head
        for k in range(h):
            f.dot(x0 - 1 + i, y0 - 2 - k, shade(fin, 1.0 - 0.12 * k))
    f.apply(base)


def est_head(base):
    """Guess the head of a figure whose face is hidden (helmets): the first solid run of
    pixels from the top, ignoring thin weapon shafts and plumes."""
    a = base.split()[3].load()
    x0, y0, x1, y1 = base.getbbox()
    for y in range(y0, y0 + (y1 - y0) // 2):
        runs, run = [], []
        for x in range(x0, x1):
            if a[x, y] > 128:
                run.append(x)
            elif run:
                runs.append(run); run = []
        if run:
            runs.append(run)
        wide = [r for r in runs if len(r) >= 5 and all(
            sum(a[x, y + k] > 128 for x in range(r[0], r[-1] + 1)) >= len(r) - 1 for k in (1, 2, 3))]
        if wide:
            r = max(wide, key=len)
            cx = (r[0] + r[-1]) // 2
            return (cx - 2, y + 1, cx + 2, y + 5)
    return None


BARBARIAN_RACES = {"Defias", "Gnolls", "Murlocs"}


# ------------------------------------------------------------------ races
def pick(seq, key):
    return seq[int(hashlib.md5(key.encode()).hexdigest(), 16) % len(seq)]


SKIN = {
    "Orcs": [ramp((40, 80, 30), (125, 170, 70), 5), ramp((90, 60, 30), (190, 120, 60), 5),
             ramp((95, 35, 25), (180, 80, 55), 5)],
    "Trolls": [ramp((30, 70, 110), (110, 170, 200), 5), ramp((25, 90, 80), (100, 180, 150), 5),
               ramp((70, 45, 100), (160, 120, 190), 5), ramp((40, 90, 50), (120, 170, 110), 5)],
    "Tauren": [ramp((60, 35, 20), (150, 100, 60), 5), ramp((40, 30, 25), (110, 90, 75), 5),
               ramp((120, 80, 45), (220, 180, 130), 5)],
    "Dwarves": [ramp((120, 75, 55), (215, 160, 125), 5)],
    "Gnomes": [ramp((140, 95, 75), (235, 190, 160), 5)],
    "Night Elves": [ramp((70, 50, 110), (175, 145, 215), 5), ramp((60, 70, 120), (150, 160, 215), 5)],
    "Blood Elves": [ramp((150, 110, 95), (250, 220, 195), 5)],
    "High Elves": [ramp((150, 115, 100), (250, 228, 205), 5)],
    "Forsaken": [ramp((70, 80, 65), (165, 175, 145), 5), ramp((80, 75, 85), (170, 160, 170), 5)],
    "Draenei": [ramp((70, 80, 140), (160, 180, 235), 5), ramp((100, 70, 140), (195, 160, 225), 5)],
    "Goblins": [ramp((60, 100, 30), (160, 200, 80), 5)],
    "Worgen": [ramp((55, 50, 45), (150, 140, 125), 5), ramp((70, 50, 35), (170, 130, 95), 5)],
    "Pandaren": [ramp((40, 40, 40), (120, 115, 110), 5)],
    # barbarian peoples (sprites for units owned by the Barbarians)
    "Defias": None,
    "Gnolls": [ramp((110, 80, 45), (190, 150, 95), 5)],
    "Murlocs": [ramp((40, 100, 85), (120, 190, 150), 5)],
}
HAIR = {
    "Dwarves": [(120, 60, 30), (170, 80, 40), (200, 160, 80), (90, 85, 80), (60, 40, 30)],
    "Gnomes": [(230, 110, 180), (90, 200, 200), (240, 240, 245), (240, 170, 60)],
    "Trolls": [(220, 60, 50), (60, 200, 220), (240, 200, 60), (200, 90, 220), (240, 240, 240)],
    "Night Elves": [(60, 160, 170), (40, 90, 160), (220, 220, 235)],
}
# (width, height) scale of the figure
BODY = {
    "Orcs": (1.15, 1.06), "Trolls": (0.92, 1.18), "Tauren": (1.3, 1.22), "Dwarves": (1.12, 0.80),
    "Gnomes": (0.80, 0.68), "Night Elves": (0.95, 1.10), "Blood Elves": (0.95, 1.04),
    "High Elves": (0.95, 1.04), "Forsaken": (0.90, 1.0), "Draenei": (1.0, 1.12),
    "Goblins": (0.85, 0.72), "Worgen": (1.18, 1.12), "Pandaren": (1.25, 0.95),
    "Defias": (1.0, 1.0), "Gnolls": (1.08, 1.1), "Murlocs": (1.0, 0.78),
}


def make(layers, race, unit, mode="full"):
    """mode: "full" (foot units), "mounted" (milder body change so the horse stays
    horse-sized) or "crew" (siege engines: recolour the crew only)."""
    base, l1, l2 = [l.copy() for l in layers]
    skin_mask = base.copy()                 # find the face on the original colours
    skin = pick(SKIN[race], unit) if SKIN[race] else ramp((150, 105, 80), (235, 190, 150), 5)
    if SKIN[race]:
        recolor_skin(base, skin)
    if mode == "crew":
        return [base, l1, l2]
    sx, sy = BODY[race]
    if mode == "mounted":
        sx, sy = 1 + (sx - 1) * 0.4, 1 + (sy - 1) * 0.4
    base, l1, l2, skin_mask = reshape([base, l1, l2, skin_mask], sx, sy)
    OVERLAYS[:] = [l1, l2]
    hb = head_box(skin_mask)
    if hb is None and race in BARBARIAN_RACES:
        hb = est_head(base)          # helmeted figure: put the barbarian head over the helm
    if hb:
        mid = skin[3]
        if race == "Dwarves":
            beard(base, hb, pick(HAIR["Dwarves"], unit), 7)
        elif race == "Gnomes":
            topknot(base, hb, pick(HAIR["Gnomes"], unit), 2, crest=False)
            ears(base, hb, mid, 2, False)
        elif race == "Orcs":
            topknot(base, hb, (25, 22, 20), 4, crest=True)
            tusks(base, hb, 2, curl=True)
        elif race == "Trolls":
            topknot(base, hb, pick(HAIR["Trolls"], unit), 4, crest=True)
            tusks(base, hb, 3, curl=True)
            ears(base, hb, mid, 3, True)
        elif race == "Tauren":
            horns(base, hb, (230, 222, 200), "bull")
        elif race == "Draenei":
            horns(base, hb, (70, 60, 80), "back")
        elif race in ("Night Elves", "Blood Elves", "High Elves"):
            ears(base, hb, mid, 5, True)
            if race == "Blood Elves":
                topknot(base, hb, (225, 180, 70), 2, crest=False)     # golden hair
            if race == "Night Elves":
                topknot(base, hb, pick(HAIR["Night Elves"], unit), 2, crest=False)
        elif race == "Goblins":
            ears(base, hb, mid, 5, False)
        elif race == "Worgen":
            wolf_head(base, hb, mid)
        elif race == "Pandaren":
            panda_face(base, hb)
        elif race == "Defias":
            defias_mask(base, hb)
        elif race == "Gnolls":
            gnoll_head(base, hb)
        elif race == "Murlocs":
            murloc_head(base, hb)
    return [base, l1, l2]


# ------------------------------------------------------------------ bulk generation
# Source sprite names (Unciv's originals). Ships keep shared sprites: their crews are
# only a few pixels tall.
FOOT = ["Worker", "Settler", "Scout", "Warrior", "Archer", "Spearman", "Composite Bowman",
        "Swordsman", "Pikeman", "Crossbowman", "Longswordsman", "Musketman", "Gatling Gun",
        "Rifleman", "Great War Infantry", "Infantry", "Machine Gun", "Marine", "Paratrooper",
        "Anti-Tank Gun", "Artillery", "Great Artist", "Great Scientist", "Great Merchant",
        "Great Engineer", "Great Prophet", "Great General", "Great Admiral", "Missionary",
        "Inquisitor"]
# mounted units: the race's own mount (mounts.py) carrying the race's foot soldier
MOUNTED = ["Chariot Archer", "Horseman", "Knight", "Lancer", "Cavalry"]
RIDER = {"Chariot Archer": "Archer", "Horseman": "Spearman", "Knight": "Swordsman",
         "Lancer": "Pikeman", "Cavalry": "Musketman"}
ARMORED = {"Knight", "Lancer"}
CREW = ["Catapult", "Trebuchet"]
RACES = ["Orcs", "Trolls", "Tauren", "Forsaken", "Blood Elves", "Goblins", "Dwarves", "Gnomes",
         "Night Elves", "Draenei", "Worgen", "High Elves", "Pandaren"]


def mounted(atlas, layers, race, src):
    """The race's mount with its rider, on a canvas as wide as the foot sprites' (so the
    rider keeps its size on the map) and with the original's proportions and footing."""
    import mounts
    w, h = layers[0].size
    rsrc = RIDER[src]
    rider_layers = make([atlas.crop(P + rsrc + s) for s in ("", "-1", "-2")], race, rsrc)
    cw = rider_layers[0].width
    canvas = (cw, round(h * cw / w))
    bb = layers[0].getbbox()
    ground = round(bb[3] / h * canvas[1])
    center = (bb[0] + bb[2]) / 2 / w * cw
    return mounts.compose(rider_layers, race, MOUNTED.index(src), src in ARMORED, canvas, ground, center)


def write_all(atlas, images_dir, renames, eras, races=RACES):
    """Write "<Unit>-<Race>" (and "<Unit>-<Race>-<Era>") layers for every person unit.
    `renames` maps Unciv names to this mod's names; `eras` maps era names."""
    count = 0
    for mode, units in (("full", FOOT), ("mounted", MOUNTED), ("crew", CREW)):
        for src in units:
            new = renames.get(src, src)
            # the plain sprite plus any era-specific variants (no civ-specific ones)
            variants = [""]
            for region in atlas.regions:
                if region.startswith(P + src + "-") and region.endswith(" era"):
                    suffix = region[len(P + src):]
                    if suffix.count("-") == 1:              # "-<Era>" only
                        variants.append(suffix)
            for variant in variants:
                import late_units
                layers = (late_units.source_layers(atlas, src) if not variant else
                          [atlas.crop(P + src + variant + s) for s in ("", "-1", "-2")])
                dressed = not variant and late_units.is_dressed(src)
                era = ""
                if variant:
                    old_era = variant[1:]
                    era = "-" + eras.get(old_era, old_era)
                for race in races:
                    if mode == "mounted":
                        out = mounted(atlas, layers, race, src)
                    elif dressed:
                        out = late_units.source_layers(atlas, src, lambda ls, b, race=race: make(ls, race, b, mode))
                    else:
                        out = make(layers, race, src, mode)
                    for s, im in zip(("", "-1", "-2"), out):
                        path = os.path.join(images_dir, P, f"{new}-{race}{era}{s}.png")
                        os.makedirs(os.path.dirname(path), exist_ok=True)
                        im.save(path)
                        count += 1
    return count


# ------------------------------------------------------------------ barbarians
# Units owned by the Barbarians are drawn as Azeroth's classic raiders: murloc packs and
# gnoll warbands in the early eras, the Defias Brotherhood once armies turn professional.
BARBARIANS = {
    "Warrior": "Murlocs", "Spearman": "Murlocs", "Archer": "Gnolls", "Composite Bowman": "Gnolls",
    "Swordsman": "Gnolls", "Pikeman": "Defias", "Crossbowman": "Defias", "Longswordsman": "Defias",
    "Musketman": "Defias", "Rifleman": "Defias", "Gatling Gun": "Defias",
    "Great War Infantry": "Defias", "Infantry": "Defias", "Machine Gun": "Defias",
    "Marine": "Defias", "Anti-Tank Gun": "Defias",
    "Horseman": "Defias", "Knight": "Defias", "Lancer": "Defias", "Cavalry": "Defias",
    "Chariot Archer": "Gnolls",
}


def write_barbarians(atlas, images_dir, renames):
    import late_units
    count = 0
    for src, race in BARBARIANS.items():
        new = renames.get(src, src)
        if src in MOUNTED:
            layers = [atlas.crop(P + src + s) for s in ("", "-1", "-2")]
            out = make(layers, race, src, "mounted")
        elif late_units.is_dressed(src):
            out = late_units.source_layers(atlas, src, lambda ls, b, race=race: make(ls, race, b, "full"))
        else:
            out = make(late_units.source_layers(atlas, src), race, src, "full")
        for s, im in zip(("", "-1", "-2"), out):
            path = os.path.join(images_dir, P, f"{new}-Barbarians{s}.png")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            im.save(path)
            count += 1
    return count
