"""Warcraft-styled forests, jungles, hills and mountains for the HexaRealm and FantasyHex
tilesets.

Original pixel art painted in code with mounts.Paint (automatic shading and outlines),
like tiles_art.py. It keeps the stock image names and layering, so it drops straight in:
  - forests and jungles are transparent overlays (ForestG/ForestP/ForestT, their hill
    versions ForestGH/PH/TH, JungleG/JungleP) plus the Up/Low halves HexaRealm uses
    when a camp, ruin or resource sits among the trees;
  - hills are whole tiles (Grassland+Hill, Plains+Hill, Tundra+Hill, Snow+Hill,
    Desert+Hill and their "2" variants) built on the stock base terrain;
  - mountains are whole 64x64 tiles (Mountain, Mountain2, Mountain-1).
FantasyHex gets half-size copies under its own names.

The look follows broad Warcraft tenets (chunky, rounded, saturated, heavily outlined)
without copying any Blizzard asset: big lumpy-canopied oaks and tall pines for
Elwynn-like forests, gold and russet trees on the plains, snow-laden pines on the
tundra, palm-and-vine jungles, rounded hills with rocky crags (red sandstone in the
desert) and jagged dark peaks with heavy snow caps.
"""
import math
import os
import random

from PIL import Image
from mounts import Paint, shade
import tiles_art as T

TW, TH = 64, 56
HR, FH = T.HR, T.FH
OUT_TREE = (24, 30, 16)
OUT_ROCK = (30, 28, 32)


# ================================================================== trees
def oak(p, x, y, leaves, trunk, part, r=6.0):
    """A Warcraft-style tree: a stubby trunk under a big lumpy canopy."""
    p.line(x, y, x, y - r * 0.9, 2.4, trunk, part + "t")
    p.line(x, y - r * 0.6, x - r * 0.5, y - r * 1.1, 1.4, trunk, part + "t")
    cy = y - r * 1.55
    for dx, dy, k in ((-r * 0.55, r * 0.15, 0.62), (r * 0.6, r * 0.2, 0.6), (0, -r * 0.35, 0.72), (-r * 0.2, r * 0.3, 0.7),
                      (r * 0.25, -r * 0.05, 0.68)):
        p.ell(x + dx, cy + dy, r * k, r * k * 0.82, leaves, part)
    p.ell(x - r * 0.3, cy - r * 0.35, r * 0.28, r * 0.2, shade(leaves, 1.25), part + "h")      # sun-lit tuft


def pine(p, x, y, col, part, h=13, w=5.0, snow=None):
    """A tall layered pine; `snow` lays white along the top of each tier."""
    p.line(x, y, x, y - 3, 2, (90, 60, 40), part + "t")
    for k in range(3):
        top = y - 3 - h * (0.32 + 0.3 * k)
        base = y - 2 - h * 0.28 * k
        ww = w * (1.0 - 0.22 * k)
        p.poly([(x - ww, base), (x, top), (x + ww, base)], col, part + str(k))
        if snow:
            p.poly([(x - ww * 0.55, top + (base - top) * 0.5), (x, top), (x + ww * 0.5, top + (base - top) * 0.45),
                    (x + ww * 0.1, top + (base - top) * 0.6)], snow, part + "s" + str(k))


def palm(p, x, y, part, h=13, lean=3, col=(70, 160, 70)):
    p.line(x, y, x + lean * 0.5, y - h * 0.5, 2, (130, 95, 55), part + "t")
    p.line(x + lean * 0.5, y - h * 0.5, x + lean, y - h, 2, (120, 88, 50), part + "t")
    tx, ty = x + lean, y - h
    for ang, ln in ((-160, 7), (-120, 6), (-60, 6), (-20, 7), (20, 6), (160, 6)):
        a = math.radians(ang)
        ex, ey = tx + math.cos(a) * ln, ty + math.sin(a) * ln * 0.6 + 2
        p.line(tx, ty, ex, ey, 2, col, part + "f")
        p.dot(ex, ey + 1, shade(col, 0.8), part + "f")


def jungle_tree(p, x, y, col, part, r=7.0, rng=None):
    oak(p, x, y, col, (95, 70, 45), part, r)
    for k in range(3):     # hanging vines
        vx = x - r * 0.6 + k * r * 0.6 + (rng.uniform(-1, 1) if rng else 0)
        top = y - r * 1.3
        p.line(vx, top, vx, top + 3 + k % 2 * 2, 1, shade(col, 0.75), part + "v")


def grass_tufts(p, rng, art, n, col):
    for i in range(n):
        x, y = rng.uniform(6, TW - 6), rng.uniform(8, TH - 8)
        if art.inside(x, y, 3):
            p.dot(x, y, col, "g%d" % i)
            p.dot(x + 1, y - 1, shade(col, 1.15), "g%d" % i)


# ================================================================== forest layouts
def layout(art, rng, n, margin, min_d, hill=False):
    pts = T.spots(art, rng, n * 3, margin, min_d)
    if hill:     # keep trees up on the hill's crown
        pts = [q for q in pts if math.hypot(q[0] - TW / 2, (q[1] - TH * 0.48) * 1.4) < 20] or pts
    return sorted(pts[:n], key=lambda q: q[1])


def forest_trees(kind, art, hill=False, seed=0):
    """[(y, draw(p, i))] for one forest overlay; sorted back to front."""
    rng = random.Random(100 + seed + (50 if hill else 0) + {"G": 0, "P": 7, "T": 13, "JG": 21, "JP": 29}[kind])
    out = []
    if kind == "G":       # Elwynn-like mixed forest: big oaks with a few dark pines
        greens = [(72, 152, 48), (56, 128, 46), (96, 168, 56), (60, 140, 70)]
        for i, (x, y) in enumerate(layout(art, rng, 4 if hill else 7, 7, 12, hill)):
            if i % 3 == 2:
                out.append((y, lambda p, i=i, x=x, y=y: pine(p, x, y + 2, (40, 100, 60), "tr%d" % i, h=rng.randint(12, 15))))
            else:
                c = greens[i % len(greens)]
                out.append((y, lambda p, i=i, x=x, y=y, c=c: oak(p, x, y + 3, c, (100, 70, 42), "tr%d" % i, rng.uniform(5.2, 6.6))))
    elif kind == "P":     # plains: gold, olive and russet trees
        cols = [(178, 150, 46), (140, 150, 50), (190, 112, 44), (160, 132, 52)]
        for i, (x, y) in enumerate(layout(art, rng, 4 if hill else 6, 7, 13, hill)):
            c = cols[i % len(cols)]
            out.append((y, lambda p, i=i, x=x, y=y, c=c: oak(p, x, y + 3, c, (110, 75, 45), "tr%d" % i, rng.uniform(5.0, 6.4))))
    elif kind == "T":     # tundra: snow-laden pines
        for i, (x, y) in enumerate(layout(art, rng, 5 if hill else 9, 6, 10, hill)):
            out.append((y, lambda p, i=i, x=x, y=y: pine(p, x, y + 2, (40, 92, 78), "tr%d" % i, h=rng.randint(13, 17), w=rng.uniform(4.5, 5.5),
                                                         snow=(236, 244, 250))))
    else:                 # jungle: heavy canopy, palms and vines
        cols = [(46, 150, 92), (34, 128, 84), (70, 168, 80), (40, 140, 110)] if kind == "JG" else \
               [(90, 150, 60), (70, 132, 56), (110, 160, 64), (60, 140, 80)]
        for i, (x, y) in enumerate(layout(art, rng, 7, 6, 11)):
            if i % 3 == 1:
                out.append((y, lambda p, i=i, x=x, y=y: palm(p, x, y + 3, "tr%d" % i, h=rng.randint(12, 15), lean=rng.choice((-3, 3)))))
            else:
                c = cols[i % len(cols)]
                out.append((y, lambda p, i=i, x=x, y=y, c=c: jungle_tree(p, x, y + 3, c, "tr%d" % i, rng.uniform(5.8, 7.2), rng)))
    return sorted(out, key=lambda t: t[0])


def paint_trees(art, trees, keep=None):
    p = Paint(TW, TH + 8)     # a little headroom: tall trees may poke above the hex
    for y, draw in trees:
        if keep is None or keep(y):
            draw(_Shift(p, 8))
    im = p.render(OUT_TREE)[0]
    return im.crop((0, 8, TW, TH + 8)) if im.getbbox() else Image.new("RGBA", (TW, TH))


class _Shift:
    """Paint wrapper moving everything down by dy (so trees can grow above y = 0)."""
    def __init__(self, p, dy):
        self.p, self.dy = p, dy

    def dot(self, x, y, *a, **k):
        self.p.dot(x, y + self.dy, *a, **k)

    def ell(self, cx, cy, rx, ry, *a, **k):
        self.p.ell(cx, cy + self.dy, rx, ry, *a, **k)

    def poly(self, pts, *a, **k):
        self.p.poly([(x, y + self.dy) for x, y in pts], *a, **k)

    def line(self, x0, y0, x1, y1, *a, **k):
        self.p.line(x0, y0 + self.dy, x1, y1 + self.dy, *a, **k)


def forests(art):
    out = {}
    for kind, name in (("G", "ForestG"), ("P", "ForestP"), ("T", "ForestT"), ("JG", "JungleG"), ("JP", "JungleP")):
        trees = forest_trees(kind, art)
        out[name] = paint_trees(art, trees)
        out[name + "Up"] = paint_trees(art, trees, lambda y: y < 28)
        out[name + "Low"] = paint_trees(art, trees, lambda y: y >= 28)
        if kind in ("G", "P", "T"):
            h = forest_trees(kind, art, hill=True)
            out[name + "H"] = paint_trees(art, h)
            out[name + "HUp"] = paint_trees(art, h, lambda y: y < 28)
            out[name + "HLow"] = paint_trees(art, h, lambda y: y >= 28)
    return out


# ================================================================== hills
HILL = {   # base terrain -> (mound colour, rock colour, tuft colour)
    "Grassland": ((96, 160, 60), (128, 122, 112), (70, 132, 44)),
    "Plains": ((176, 166, 72), (140, 126, 100), (140, 140, 50)),
    "Tundra": ((150, 128, 96), (120, 116, 112), (120, 104, 70)),
    "Snow": ((226, 236, 246), (150, 160, 175), None),
    "Desert": ((212, 120, 72), (176, 86, 54), None),          # red sandstone, like Durotar and Thousand Needles
}


def dome(p, cx, cy, rx, ry, col, part):
    """A rounded hill: a tall dome, lit on its north-west crown, shaded on its south-east flank."""
    # one part name for the whole dome, so only its silhouette gets the edge shading
    p.ell(cx, cy, rx, ry, shade(col, 0.86), part)
    p.ell(cx - rx * 0.1, cy - ry * 0.12, rx * 0.8, ry * 0.74, col, part)
    p.ell(cx - rx * 0.28, cy - ry * 0.34, rx * 0.46, ry * 0.36, shade(col, 1.1), part)


def crag(p, x, y, col, part, s=1.0):
    p.poly([(x - 4 * s, y), (x - 3 * s, y - 4 * s), (x - 1 * s, y - 7 * s), (x + 2 * s, y - 6 * s), (x + 4 * s, y - 2 * s),
            (x + 4 * s, y)], col, part)
    p.poly([(x + 0.5 * s, y - 6.5 * s), (x + 2 * s, y - 6 * s), (x + 4 * s, y - 2 * s), (x + 4 * s, y), (x + 1 * s, y)],
           shade(col, 0.76), part + "r")


def hill_tile(art, base, variant=0):
    mcol, rcol, tuft = HILL[base]
    rng = random.Random(300 + variant * 17 + len(base))
    im = art.base(base)
    p = Paint(TW, TH)
    rocks = Paint(TW, TH)
    if base == "Desert":       # flat-topped red sandstone mesas
        mesas = [(24, 40, 18, 22), (46, 44, 12, 14)] if variant == 0 else [(32, 42, 20, 24), (13, 44, 8, 10)]
        for i, (x, y, w, h) in enumerate(mesas):
            p.poly([(x - w, y), (x - w * 0.85, y - h * 0.5), (x - w * 0.7, y - h), (x + w * 0.75, y - h), (x + w * 0.9, y - h * 0.45),
                    (x + w, y)], mcol, "m%d" % i)
            p.poly([(x - w * 0.7, y - h), (x + w * 0.75, y - h), (x + w * 0.65, y - h + 3), (x - w * 0.62, y - h + 3)],
                   shade(mcol, 1.18), "t%d" % i)
            p.poly([(x + w * 0.3, y - h + 3), (x + w * 0.75, y - h), (x + w * 0.9, y - h * 0.45), (x + w, y), (x + w * 0.35, y)],
                   rcol, "s%d" % i)
            for k in range(2):
                yy = y - h * (0.35 + 0.3 * k)
                p.line(x - w * 0.8, yy, x + w * 0.25, yy, 1, shade(mcol, 0.8), "b%d%d" % (i, k))
        over = p.render(shade(rcol, 0.45))[0]
    else:
        domes = [(24, 30, 17, 15), (44, 35, 13, 12)] if variant == 0 else [(32, 28, 18, 15), (16, 40, 10, 9), (48, 40, 10, 9)]
        for i, (x, y, rx, ry) in enumerate(sorted(domes, key=lambda m: m[1])):
            dome(p, x, y, rx, ry, mcol, "m%d" % i)
        over = p.render(shade(mcol, 0.66))[0]
        for i, (x, y) in enumerate(((30, 22), (50, 30)) if variant == 0 else ((38, 20), (14, 38))):
            crag(rocks, x, y, rcol, "c%d" % i, 0.9 + 0.15 * i)
        if tuft:
            grass_tufts(rocks, rng, art, 5, tuft)
        over.alpha_composite(rocks.render((50, 44, 40))[0])
    out = im.copy()
    out.alpha_composite(art.clip(over))
    return out


def hill_overlay(art):
    """The bare 'Hill' overlay (used over other base terrains): grassy domes."""
    p = Paint(TW, TH)
    for i, (x, y, rx, ry) in enumerate(((24, 30, 18, 14), (44, 34, 14, 11))):
        dome(p, x, y, rx, ry, (110, 150, 70), "m%d" % i)
    over = p.render(shade((110, 150, 70), 0.55))[0]
    r = Paint(TW, TH)
    crag(r, 30, 22, (128, 122, 112), "c", 0.9)
    over.alpha_composite(r.render((50, 44, 40))[0])
    return art.clip(over)


# ================================================================== mountains
def peak(p, cx, base_y, w, h, col, part, snow, lean=0, rng=None):
    """A jagged peak: ragged ridgelines, lit west face, shadowed east face, a deep snow cap."""
    r = rng or random.Random(1)
    top = (cx + lean, base_y - h)
    west = [(cx - w, base_y), (cx - w * 0.78, base_y - h * 0.32 + r.uniform(-2, 2)), (cx - w * 0.5, base_y - h * 0.5),
            (cx - w * 0.3, base_y - h * 0.74 + r.uniform(-2, 1)), top]
    east = [top, (cx + w * 0.22, base_y - h * 0.72), (cx + w * 0.4, base_y - h * 0.62 + r.uniform(-2, 1)),
            (cx + w * 0.62, base_y - h * 0.38), (cx + w, base_y)]
    p.poly(west + east[1:], col, part)
    p.poly([top] + east[1:] + [(cx + w * 0.05, base_y), (cx + lean * 0.3, base_y - h * 0.55)], shade(col, 0.7), part + "r")
    for k in range(2):     # gullies on the lit face
        gx = cx - w * (0.25 + 0.3 * k)
        p.line(gx + w * 0.15, base_y - h * (0.55 - 0.15 * k), gx - w * 0.05, base_y - h * 0.12, 1, shade(col, 0.8), part + "g%d" % k)
    cap = [top, (cx - w * 0.3, base_y - h * 0.74), (cx - w * 0.36, base_y - h * 0.6), (cx - w * 0.18, base_y - h * 0.66),
           (cx - w * 0.06, base_y - h * 0.55), (cx + w * 0.1, base_y - h * 0.64), (cx + w * 0.26, base_y - h * 0.58),
           (cx + w * 0.22, base_y - h * 0.72)]
    p.poly(cap, snow, part + "s")
    p.poly([top, (cx + w * 0.22, base_y - h * 0.72), (cx + w * 0.26, base_y - h * 0.58), (cx + w * 0.08, base_y - h * 0.64),
            (cx + lean * 0.4, base_y - h * 0.78)], shade(snow, 0.84), part + "ss")


def mountain_tile(art, variant=0):
    from PIL import ImageChops
    rng = random.Random(500 + variant)
    out = Image.new("RGBA", (TW, 64))
    out.alpha_composite(art.base("Snow", tint=(0.5, 0.5, 0.56)), (0, 8))     # grey stony ground
    p = Paint(TW, 64)
    rock = [(112, 108, 120), (104, 100, 112), (116, 106, 104)][variant % 3]
    snow = (240, 246, 252)
    p.poly([(2, 58), (6, 40), (16, 30), (30, 26), (46, 28), (58, 38), (62, 58)], shade(rock, 0.84), "ridge")    # the massif behind
    layouts = [
        [(14, 58, 16, 34, -1), (50, 58, 16, 38, 2), (32, 62, 22, 58, 0)],
        [(20, 60, 20, 50, 1), (46, 58, 17, 36, -2), (34, 63, 16, 28, 0)],
        [(12, 60, 14, 32, 0), (34, 62, 23, 60, -1), (54, 62, 13, 30, 1)],
    ][variant % 3]
    for i, (x, y, w, h, lean) in enumerate(sorted(layouts, key=lambda q: q[1])):
        peak(p, x, y, w, h, rock, "p%d" % i, snow, lean, rng)
    peaks = p.render(OUT_ROCK)[0]
    mask = Image.new("L", (TW, 64), 0)
    mask.paste(art.mask, (0, 8))
    top = Image.new("L", (TW, 64), 0)
    top.paste(255, (0, 0, TW, 30))
    keep = ImageChops.lighter(mask, top)
    peaks.putalpha(ImageChops.multiply(peaks.split()[3], keep))
    out.alpha_composite(peaks)
    return out


# ================================================================== output
FH_MAP = {"Forest": "ForestG", "GrasslandForest": "ForestG", "PlainsForest": "ForestP", "TundraForest": "ForestT",
          "Jungle": "JungleG", "PlainsJungle": "JungleP", "Hill": "Hill", "Mountain": "Mountain"}


def render_all(atlas):
    art = T.Art(atlas)
    tiles = forests(art)
    for base in HILL:
        tiles[base + "+Hill"] = hill_tile(art, base, 0)
        tiles[base + "+Hill2"] = hill_tile(art, base, 1)
    tiles["Hill"] = hill_overlay(art)
    tiles["Mountain"] = mountain_tile(art, 0)
    tiles["Mountain2"] = mountain_tile(art, 1)
    tiles["Mountain-1"] = mountain_tile(art, 2)
    return tiles


def fh_version(im, name):
    """Half size, on FantasyHex's canvas (32 wide; overlays sit on a 28-high hex at the bottom)."""
    small = im.resize((im.width // 2, im.height // 2), Image.BOX)
    h = {"Mountain": 36}.get(name, 32)
    out = Image.new("RGBA", (32, h))
    out.alpha_composite(small, (0, h - small.height))
    return out


def write_all(atlas, images_dir):
    tiles = render_all(atlas)
    for name, im in tiles.items():
        path = os.path.join(images_dir, HR, name + ".png")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        im.save(path)
    for fh_name, src in FH_MAP.items():
        path = os.path.join(images_dir, FH, fh_name + ".png")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        fh_version(tiles[src], fh_name).save(path)
    return len(tiles) + len(FH_MAP)
