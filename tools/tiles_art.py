"""Tile art for UncivWarcraft's terrain features and natural landmarks.

Pixel art in the style of Unciv's HexaRealm tileset (64 x 56 hexes), painted in code
from simple shapes with automatic shading and outlines (mounts.Paint). Features are
transparent overlays drawn over the base terrain, like HexaRealm's forests; landmarks
are whole tiles painted over a HexaRealm base terrain. FantasyHex gets 32 x 28
downscaled copies so players on either tileset see them.
"""
import math, os, random
from PIL import Image, ImageFilter, ImageChops
from mounts import Paint, shade

TW, TH = 64, 56
HR = "TileSets/HexaRealm/Tiles/"
FH = "TileSets/FantasyHex/Tiles/"


class Art:
    def __init__(self, atlas):
        self.a = atlas
        g = atlas.crop(HR + "Grassland")
        self.mask = g.split()[3].point(lambda v: 255 if v > 128 else 0)
        # the face: the hex without its darker bottom rim
        self.face = self.mask.copy()
        fp = self.face.load()
        for y in range(TH - 3, TH):
            for x in range(TW):
                fp[x, y] = 0

    def base(self, name, tint=None):
        im = self.a.crop(HR + name).convert("RGBA")
        if tint:
            px = im.load()
            for y in range(im.height):
                for x in range(im.width):
                    p = px[x, y]
                    if p[3]:
                        px[x, y] = tuple(int(p[i] * tint[i]) for i in range(3)) + (p[3],)
        return im

    def inside(self, x, y, margin=0):
        """Is (x, y) on the hex face, at least `margin` pixels in from its edge?"""
        for dx in range(-margin, margin + 1, max(1, margin)):
            for dy in range(-margin, margin + 1, max(1, margin)):
                X, Y = int(x + dx), int(y + dy)
                if not (0 <= X < TW and 0 <= Y < TH) or not self.face.getpixel((X, Y)):
                    return False
        return True

    def clip(self, im):
        out = im.copy()
        a = ImageChops.multiply(out.split()[3], self.mask)
        out.putalpha(a)
        return out


def layer(p, outline=None):
    return p.render(outline)[0]


def glow(im, color, radius=1.6, strength=1.3):
    """A soft coloured halo behind the opaque pixels of `im`."""
    m = im.split()[3].filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(radius))
    m = m.point(lambda v: min(255, int(v * strength)))
    g = Image.new("RGBA", im.size, tuple(color) + (0,))
    g.putalpha(m)
    out = Image.new("RGBA", im.size)
    out.alpha_composite(g)
    out.alpha_composite(im)
    return out


def stack(*layers):
    out = Image.new("RGBA", (TW, TH))
    for l in layers:
        if l is not None:
            out.alpha_composite(l)
    return out


def blob(p, cx, cy, r, col, part, rng, lumps=5):
    """An irregular ground patch made of overlapping ellipses."""
    p.ell(cx, cy, r, r * 0.62, col, part)
    for _ in range(lumps):
        a = rng.random() * math.tau
        d = r * (0.45 + rng.random() * 0.4)
        p.ell(cx + math.cos(a) * d, cy + math.sin(a) * d * 0.6, r * 0.55, r * 0.35, col, part)


def spots(art, rng, n, margin, min_d):
    """Scatter n points over the hex face, keeping them min_d apart; sorted back to front."""
    pts = []
    tries = 0
    while len(pts) < n and tries < 2000:
        tries += 1
        x, y = rng.uniform(4, TW - 4), rng.uniform(4, TH - 6)
        if art.inside(x, y, margin) and all(math.hypot(x - a, y - b) >= min_d for a, b in pts):
            pts.append((x, y))
    return sorted(pts, key=lambda q: q[1])


def crack(p, x, y, length, col, part, rng):
    for _ in range(length):
        p.dot(x, y, col, part)
        x += rng.choice((-1, 0, 1, 1))
        y += rng.choice((-1, 0, 1))


# ======================================================================= features
FEL, FEL_LIGHT = (110, 235, 60), (215, 255, 140)


def fel_scorched(art):
    rng = random.Random(11)
    ground = Paint(TW, TH)
    for i, (x, y) in enumerate(spots(art, rng, 5, 5, 13)):
        blob(ground, x, y, rng.uniform(6, 9), (52, 44, 40), "char%d" % i, rng)
    g = layer(ground)
    cr = Paint(TW, TH)
    gp = g.load()
    for _ in range(14):
        x, y = rng.uniform(6, TW - 6), rng.uniform(6, TH - 8)
        if gp[int(x), int(y)][3]:
            crack(cr, x, y, rng.randint(4, 8), FEL, "crack", rng)
    c = layer(cr)
    flames = Paint(TW, TH)
    for i, (x, y) in enumerate(spots(art, rng, 4, 6, 14)):
        flames.poly([(x - 1.5, y), (x + 1.5, y), (x + 0.5, y - 4), (x, y - 6), (x - 0.5, y - 3)], FEL, "fl%d" % i)
        flames.dot(x, y - 1, FEL_LIGHT, "fl%d" % i)
    f = layer(flames, outline=(30, 70, 20))
    return art.clip(stack(g, glow(c, FEL, 1.2, 1.1), glow(f, FEL, 1.5, 1.0)))


def plagued(art):
    rng = random.Random(12)
    ground = Paint(TW, TH)
    for i, (x, y) in enumerate(spots(art, rng, 5, 5, 13)):
        blob(ground, x, y, rng.uniform(6, 9), (112, 102, 118), "rot%d" % i, rng)
    g = layer(ground)
    things = Paint(TW, TH)
    for i, (x, y) in enumerate(spots(art, rng, 4, 7, 12)):
        kind = i % 3
        if kind == 0:                                   # slime pool
            things.ell(x, y, 3.5, 2, (110, 190, 60), "slime%d" % i)
            things.dot(x - 1, y - 1, (190, 240, 140), "slime%d" % i)
        elif kind == 1:                                 # skull and bones
            things.ell(x, y, 1.5, 1.3, (230, 225, 210), "skull%d" % i)
            things.dot(x - 0.5, y, (40, 35, 40), "skull%d" % i)
            things.line(x + 2, y + 1, x + 5, y + 2, 1, (220, 215, 200), "bone%d" % i)
        else:                                           # dead tree
            things.line(x, y, x, y - 7, 2, (70, 55, 50), "stump%d" % i)
            things.line(x, y - 5, x + 3, y - 8, 1, (70, 55, 50), "stump%d" % i)
            things.line(x, y - 4, x - 2, y - 6, 1, (70, 55, 50), "stump%d" % i)
    t = layer(things, outline=(40, 32, 45))
    return art.clip(stack(g, t))


def tree(p, x, y, trunk, leaves, part, h=6, r=5.0):
    p.line(x, y, x, y - h, 2, trunk, part + "t")
    for dx, dy, k in ((0, -h - 2, 1.0), (-r * 0.6, -h, 0.75), (r * 0.6, -h, 0.75)):
        p.ell(x + dx, y + dy, r * k, r * 0.8 * k, leaves, part)


def ancient_woods(art):
    rng = random.Random(13)
    p = Paint(TW, TH)
    cols = [(120, 80, 170), (90, 70, 150), (70, 130, 150), (140, 95, 185)]
    for i, (x, y) in enumerate(spots(art, rng, 8, 6, 11)):
        tree(p, x, y + 2, (75, 55, 70), cols[i % len(cols)], "tree%d" % i, h=rng.randint(5, 8),
             r=rng.uniform(4.0, 5.5))
    trees = layer(p, outline=(35, 25, 50))
    w = Paint(TW, TH)
    for i, (x, y) in enumerate(spots(art, rng, 3, 8, 16)):
        w.dot(x, y - 6, (220, 255, 255), "wisp%d" % i)
    return art.clip(stack(trees, glow(layer(w), (120, 230, 255), 1.4, 1.6)))


def bamboo(art):
    rng = random.Random(14)
    p = Paint(TW, TH)
    for i, (x, y) in enumerate(spots(art, rng, 7, 6, 11)):
        for j in range(3):
            sx = x + (j - 1) * 2.5 + rng.uniform(-0.5, 0.5)
            hgt = rng.randint(9, 14)
            col = (120, 175, 70) if j != 1 else (95, 150, 55)
            p.line(sx, y, sx, y - hgt, 1, col, "st%d%d" % (i, j))
            for k in range(3, hgt, 4):
                p.dot(sx, y - k, shade(col, 0.7), "st%d%d" % (i, j))
            p.line(sx, y - hgt, sx + 3, y - hgt - 1, 1, (70, 140, 50), "lf%d%d" % (i, j))
            p.line(sx, y - hgt + 2, sx - 3, y - hgt + 1, 1, (70, 140, 50), "lf%d%d" % (i, j))
    return art.clip(layer(p, outline=(35, 60, 25)))


def molten(art):
    rng = random.Random(15)
    ground = Paint(TW, TH)
    for i, (x, y) in enumerate(spots(art, rng, 5, 5, 12)):
        blob(ground, x, y, rng.uniform(6, 9), (42, 36, 36), "rock%d" % i, rng)
    g = layer(ground)
    lava = Paint(TW, TH)
    gp = g.load()
    for _ in range(40):
        x, y = rng.uniform(6, TW - 6), rng.uniform(6, TH - 8)
        if gp[int(x), int(y)][3]:
            for _ in range(rng.randint(5, 9)):
                if not gp[min(TW - 1, max(0, int(x))), min(TH - 1, max(0, int(y)))][3]:
                    break
                lava.dot(x, y, (255, 130, 30), "lava")
                lava.dot(x + 1, y, (255, 200, 70), "lava")
                x += rng.choice((1, 1, 0, -1)); y += rng.choice((0, 1, -1))
    lumps = Paint(TW, TH)
    for i, (x, y) in enumerate(spots(art, rng, 5, 6, 12)):
        lumps.ell(x, y, 2.5, 1.8, (70, 60, 58), "lump%d" % i)
    return art.clip(stack(g, glow(layer(lava), (255, 110, 30), 1.3, 1.2),
                          layer(lumps, outline=(25, 20, 20))))


def crystal(p, x, y, h, w, col, part):
    p.poly([(x, y - h), (x + w, y - h * 0.55), (x + w * 0.6, y), (x - w * 0.6, y), (x - w, y - h * 0.55)], col, part)
    p.line(x, y - h + 1, x - w * 0.5, y - h * 0.45, 1, shade(col, 1.25), part)


def crystal_grove(art):
    rng = random.Random(16)
    p = Paint(TW, TH)
    cols = [(170, 150, 255), (140, 215, 255), (200, 170, 255)]
    for i, (x, y) in enumerate(spots(art, rng, 7, 6, 11)):
        c = cols[i % 3]
        crystal(p, x, y, rng.randint(9, 13), 2.2, c, "c%da" % i)
        crystal(p, x - 3, y + 1, rng.randint(5, 7), 1.6, shade(c, 0.9), "c%db" % i)
        crystal(p, x + 3, y + 1, rng.randint(4, 6), 1.5, shade(c, 1.05), "c%dc" % i)
    c = layer(p, outline=(60, 50, 110))
    return art.clip(glow(c, (170, 200, 255), 1.6, 0.9))


STONE = (178, 172, 160)


def titan_ruins(art):
    rng = random.Random(17)
    p = Paint(TW, TH)
    pts = spots(art, rng, 6, 8, 13)
    for i, (x, y) in enumerate(pts):
        kind = i % 3
        if kind == 0:                                   # standing pillar, broken top
            p.poly([(x - 3, y), (x + 3, y), (x + 3, y - 13), (x + 0.5, y - 16), (x - 3, y - 14)], STONE, "pil%d" % i)
            p.poly([(x + 1, y), (x + 3, y), (x + 3, y - 13), (x + 1, y - 14)], shade(STONE, 0.8), "pil%dr" % i)
            p.line(x - 4, y, x + 4, y, 2, shade(STONE, 0.9), "pil%db" % i)
        elif kind == 1:                                 # arch
            p.line(x - 6, y, x - 6, y - 12, 3, STONE, "arch%d" % i)
            p.line(x + 6, y, x + 6, y - 12, 3, STONE, "arch%d" % i)
            p.line(x - 8, y - 13, x + 8, y - 13, 3, shade(STONE, 1.05), "arch%d" % i)
        else:                                           # fallen blocks
            p.poly([(x - 4, y), (x + 3, y), (x + 4, y - 3), (x - 3, y - 3)], STONE, "blk%d" % i)
            p.poly([(x + 3, y + 2), (x + 7, y + 2), (x + 7, y - 1), (x + 4, y - 1)], shade(STONE, 0.92), "blk%db" % i)
    s = layer(p, outline=(60, 58, 55))
    r = Paint(TW, TH)
    for i, (x, y) in enumerate(pts):
        for dy in (5, 8):
            r.dot(x - 1, y - dy, (110, 210, 255), "rune%d" % i)
            r.dot(x, y - dy - 1, (110, 210, 255), "rune%d" % i)
    return art.clip(stack(s, glow(layer(r), (90, 190, 255), 1.0, 1.4)))


FEATURES = {
    "Fel-Scorched Land": fel_scorched, "Plagued Land": plagued, "Ancient Woods": ancient_woods,
    "Bamboo Grove": bamboo, "Molten Fields": molten, "Crystal Grove": crystal_grove,
    "Titan Ruins": titan_ruins,
}


# ======================================================================= landmarks
def mountain(p, cx, base_y, w, h, col, part, snow=None, rng=None):
    """A shaded peak: lit left face, shadowed right face, optional snow cap."""
    top = (cx, base_y - h)
    p.poly([(cx - w, base_y), top, (cx + w, base_y)], col, part)
    p.poly([top, (cx + w, base_y), (cx + w * 0.15, base_y)], shade(col, 0.78), part + "r")
    if snow:
        p.poly([top, (cx - w * 0.3, base_y - h * 0.7), (cx - w * 0.05, base_y - h * 0.75),
                (cx + w * 0.3, base_y - h * 0.68)], snow, part + "s")


def maelstrom(art):
    im = art.base("Ocean")
    p = Paint(TW, TH)
    p.ell(32, 27, 24, 17, (30, 70, 120), "ring")
    p.ell(32, 27, 14, 10, (20, 45, 85), "inner")
    p.ell(32, 27, 5, 3.5, (8, 15, 35), "eye")
    swirl = Paint(TW, TH)
    for arm in range(3):
        for i in range(70):
            th = i * 0.11 + arm * math.tau / 3
            r = 3 + i * 0.32
            swirl.dot(32 + math.cos(th) * r, 27 + math.sin(th) * r * 0.68, (200, 230, 245), "foam")
    return art.clip(stack(im, layer(p), layer(swirl)))


def world_tree(p, cx, base_y, height, trunk, leaves, part, spread=1.0):
    p.poly([(cx - 4, base_y), (cx + 4, base_y), (cx + 2, base_y - height), (cx - 2, base_y - height)], trunk, part + "t")
    p.line(cx - 4, base_y, cx - 8, base_y + 2, 2, trunk, part + "r")
    p.line(cx + 4, base_y, cx + 8, base_y + 2, 2, trunk, part + "r")
    top = base_y - height
    for dx, dy, rx, ry in ((0, -4, 14, 7), (-11, 1, 9, 5), (11, 1, 9, 5), (-5, -9, 9, 5), (6, -9, 9, 5)):
        p.ell(cx + dx * spread, top + dy, rx * spread, ry, leaves, part + "l")
    for dx, dy, rx, ry in ((-4, -7, 5, 2.5), (7, -3, 4, 2)):
        p.ell(cx + dx * spread, top + dy, rx, ry, shade(leaves, 1.2), part + "h")


def hyjal(art):
    im = art.base("Grassland")
    p = Paint(TW, TH)
    mountain(p, 32, 50, 27, 24, (110, 125, 95), "mt")
    p.ell(32, 36, 13, 5, (85, 140, 65), "slope")
    world_tree(p, 32, 34, 14, (110, 85, 60), (70, 150, 90), "nord")
    return art.clip(stack(im, layer(p, outline=(40, 45, 35))))


def teldrassil(art):
    im = art.base("Coast")
    p = Paint(TW, TH)
    p.ell(32, 44, 20, 7, (100, 150, 70), "isle")
    world_tree(p, 32, 44, 22, (120, 95, 125), (95, 70, 140), "teld", spread=1.15)
    return art.clip(stack(im, layer(p, outline=(40, 30, 50))))


def moonglade(art):
    im = art.base("Grassland")
    p = Paint(TW, TH)
    rng = random.Random(21)
    for i, a in enumerate(range(200, 340, 28)):          # trees around the back
        x, y = 32 + math.cos(math.radians(a)) * 21, 30 + math.sin(math.radians(a)) * 14
        tree(p, x, y, (75, 55, 70), [(120, 80, 170), (70, 130, 150)][i % 2], "tb%d" % i, h=5, r=4.5)
    p.ell(32, 32, 11, 6, (150, 150, 160), "rim")
    p.ell(32, 32, 8.5, 4.3, (160, 200, 255), "well")
    for i, a in enumerate((20, 160)):                    # trees in front
        x, y = 32 + math.cos(math.radians(a)) * 22, 34 + math.sin(math.radians(a)) * 12
        tree(p, x, y, (75, 55, 70), (90, 70, 150), "tf%d" % i, h=5, r=4.5)
    l = layer(p, outline=(40, 35, 55))
    sh = Paint(TW, TH)
    sh.line(28, 31, 35, 31, 1, (240, 250, 255), "shine")
    return art.clip(stack(im, l, glow(layer(sh), (200, 230, 255), 2.0, 1.2)))


def elune_ara(art):
    im = art.base("Grassland")
    p = Paint(TW, TH)
    p.ell(32, 30, 22, 13, (70, 110, 170), "lake")
    p.ell(32, 30, 18, 10, (90, 135, 200), "lake2")
    for i, (x, y) in enumerate(((10, 18), (54, 18), (8, 38), (56, 40))):
        tree(p, x, y, (75, 55, 70), (120, 80, 170), "t%d" % i, h=4, r=4)
    l = layer(p, outline=(35, 40, 60))
    m = Paint(TW, TH)
    m.ell(32, 28, 4, 4, (245, 248, 255), "moon")
    m.ell(33.5, 27, 3.5, 3.5, (90, 135, 200), "moon2")       # crescent
    for x in range(22, 43, 3):
        m.dot(x, 34 + (x % 2), (230, 240, 255), "shim")
    return art.clip(stack(im, l, glow(layer(m), (220, 235, 255), 1.6, 1.1)))


def stonetalon(art):
    im = art.base("Plains")
    p = Paint(TW, TH)
    mountain(p, 20, 50, 14, 20, (125, 110, 95), "m1")
    mountain(p, 46, 50, 13, 18, (115, 100, 88), "m2")
    mountain(p, 32, 52, 15, 40, (140, 122, 104), "peak")
    tree(p, 32, 14, (90, 65, 45), (85, 140, 70), "tree", h=4, r=4.5)
    return art.clip(stack(im, layer(p, outline=(45, 38, 32))))


def red_rocks(art):
    im = art.base("Plains")
    p = Paint(TW, TH)
    rock = (190, 95, 55)
    for i, (x, w, h) in enumerate(((14, 6, 18), (26, 7, 26), (42, 8, 22), (52, 5, 14))):
        p.poly([(x - w, 46), (x - w + 1, 46 - h), (x + w - 1, 46 - h - 1), (x + w, 46)], rock, "rk%d" % i)
        p.poly([(x + 1, 46 - h), (x + w - 1, 46 - h - 1), (x + w, 46), (x + 1, 46)], shade(rock, 0.78), "rk%dr" % i)
        p.line(x - w + 1, 46 - h + 4, x + w - 1, 46 - h + 4, 1, shade(rock, 0.85), "rk%dl" % i)
    for k, c in enumerate(((200, 60, 40), (240, 200, 70), (60, 120, 170), (240, 240, 230))):  # totem
        p.poly([(33, 46 - k * 4), (37, 46 - k * 4), (37, 42 - k * 4), (33, 42 - k * 4)], c, "tot%d" % k)
    p.line(31, 33, 39, 33, 1, (240, 200, 70), "wings")
    return art.clip(stack(im, layer(p, outline=(60, 30, 20))))


def needles(art):
    im = art.base("Desert")
    p = Paint(TW, TH)
    rng = random.Random(22)
    for i, (x, y) in enumerate(spots(art, rng, 9, 6, 8)):
        h = rng.randint(14, 26)
        col = (175, 120, 75) if i % 2 else (160, 105, 65)
        p.poly([(x - 2.5, y), (x - 1, y - h), (x + 1, y - h + 1), (x + 2.5, y)], col, "n%d" % i)
        p.poly([(x + 0.5, y - h + 1), (x + 1, y - h + 1), (x + 2.5, y), (x + 0.5, y)], shade(col, 0.75), "n%dr" % i)
    return art.clip(stack(im, layer(p, outline=(70, 45, 30))))


def jungle_blobs(p, rng, cx, cy, rx, ry, n, part):
    for i in range(n):
        a, d = rng.random() * math.tau, rng.random() ** 0.5
        x, y = cx + math.cos(a) * rx * d, cy + math.sin(a) * ry * d
        p.ell(x, y, 3.5, 2.6, [(60, 130, 50), (80, 150, 55), (50, 110, 45)][i % 3], part + str(i))


def ungoro(art):
    im = art.base("Grassland")
    p = Paint(TW, TH)
    rng = random.Random(23)
    p.ell(32, 29, 27, 19, (140, 110, 80), "rim")
    p.ell(32, 30, 22, 14, (80, 120, 55), "floor")
    jungle_blobs(p, rng, 32, 32, 18, 10, 22, "j")
    mountain(p, 32, 34, 8, 13, (85, 60, 50), "volc")
    p.ell(32, 21.5, 3, 1.2, (255, 140, 40), "lava")
    l = layer(p, outline=(40, 35, 25))
    s = Paint(TW, TH)
    s.ell(30, 15, 2.5, 2, (170, 165, 160), "smoke")
    s.ell(27, 11, 3, 2.3, (195, 190, 185), "smoke2")
    return art.clip(stack(im, l, layer(s)))


def tar_pits(art):
    im = art.base("Grassland")
    p = Paint(TW, TH)
    rng = random.Random(24)
    jungle_blobs(p, rng, 32, 10, 24, 5, 10, "jb")
    for i, (x, y, rx) in enumerate(((22, 30, 10), (42, 26, 8), (36, 42, 9))):
        p.ell(x, y, rx, rx * 0.55, (28, 26, 30), "tar%d" % i)
        p.ell(x - rx * 0.3, y - 1, rx * 0.3, 1, (80, 80, 95), "gloss%d" % i)
        p.ell(x + rx * 0.4, y + 1, 1.2, 1, (60, 58, 66), "bub%d" % i)
    for k in range(4):                                     # ribs of a beast
        p.line(40 + k * 2, 25, 41 + k * 2, 20, 1, (235, 230, 215), "rib%d" % k)
    p.line(39, 25, 47, 25, 1, (225, 220, 205), "spine")
    return art.clip(stack(im, layer(p, outline=(30, 28, 25))))


def tolvir(art):
    im = art.base("Desert")
    p = Paint(TW, TH)
    sand, gold = (215, 175, 110), (235, 195, 80)
    p.line(10, 40, 54, 40, 3, (90, 170, 190), "canal")
    for i, (x, y, w, h) in enumerate(((16, 34, 7, 8), (46, 34, 7, 8), (31, 30, 9, 11))):
        p.poly([(x - w, y), (x + w, y), (x + w, y - h), (x - w, y - h)], sand, "b%d" % i)
        p.poly([(x + w * 0.3, y), (x + w, y), (x + w, y - h), (x + w * 0.3, y - h)], shade(sand, 0.82), "b%dr" % i)
        p.ell(x, y - h, w * 0.7, w * 0.55, gold, "d%d" % i)
        p.line(x - 1, y, x - 1, y - 3, 2, (90, 60, 40), "door%d" % i)
    for i, x in enumerate((8, 24, 39, 56)):                 # obelisks
        p.poly([(x - 1.5, 47), (x + 1.5, 47), (x + 0.5, 34), (x - 0.5, 34)], sand, "ob%d" % i)
        p.dot(x, 33, gold, "ob%d" % i)
    return art.clip(stack(im, layer(p, outline=(80, 60, 35))))


def blackrock(art):
    im = art.base("Desert", tint=(0.85, 0.62, 0.5))
    p = Paint(TW, TH)
    mountain(p, 32, 52, 28, 42, (55, 48, 48), "mt")
    p.ell(32, 11, 4, 1.5, (255, 120, 30), "crater")
    l = layer(p, outline=(20, 15, 15))
    lava = Paint(TW, TH)
    rng = random.Random(25)
    for start, drift in ((31, -0.7), (33, 0.6), (32, -0.1), (32, 0.25)):
        x, y = start, 12
        stop = rng.randint(30, 47)
        while y < stop:
            lava.dot(x, y, (255, 120, 30), "lv")
            lava.dot(x, y + 1, (255, 190, 70), "lv")
            x += rng.choice((-1, 0, 0, 1)) + drift; y += 1.5
    return art.clip(stack(im, l, glow(layer(lava), (255, 90, 20), 1.4, 1.1)))


def stranglethorn(art):
    im = art.base("Coast")
    p = Paint(TW, TH)
    rng = random.Random(26)
    cliff = (110, 95, 70)
    p.poly([(0, 22), (12, 8), (30, 4), (52, 6), (64, 18), (64, 28), (50, 20), (34, 18), (18, 22), (8, 32), (0, 34)],
           cliff, "cliff")
    p.poly([(0, 34), (8, 32), (14, 44), (8, 54), (0, 54)], cliff, "cliffL")
    jungle_blobs(p, rng, 32, 9, 26, 5, 20, "jt")
    jungle_blobs(p, rng, 5, 42, 4, 8, 6, "jl")
    for i, x in enumerate((22, 30, 38)):                  # stilt houses of the bay
        p.poly([(x - 3, 28), (x + 3, 28), (x + 3, 24), (x - 3, 24)], (150, 100, 60), "h%d" % i)
        p.poly([(x - 4, 24), (x, 21), (x + 4, 24)], (180, 60, 45), "roof%d" % i)
        p.line(x - 2, 28, x - 2, 32, 1, (90, 60, 40), "stilt%d" % i)
        p.line(x + 2, 28, x + 2, 32, 1, (90, 60, 40), "stilt%d" % i)
    p.poly([(36, 44), (48, 44), (46, 47), (38, 47)], (120, 80, 50), "ship")
    p.line(42, 44, 42, 36, 1, (90, 60, 40), "mast")
    p.poly([(42, 37), (47, 40), (42, 42)], (235, 230, 220), "sail")
    return art.clip(stack(im, layer(p, outline=(35, 40, 25))))


def kelpthar(art):
    im = art.base("Ocean")
    p = Paint(TW, TH)
    rng = random.Random(27)
    for i, (x, y) in enumerate(spots(art, rng, 10, 5, 8)):
        h = rng.randint(10, 18)
        col = [(70, 140, 70), (100, 150, 60), (60, 120, 80)][i % 3]
        for k in range(h):
            p.dot(x + math.sin(k * 0.6 + i) * 1.3, y - k, col, "kelp%d" % i)
            if k % 4 == 2:
                p.dot(x + math.sin(k * 0.6 + i) * 1.3 + 1, y - k, shade(col, 1.3), "kelp%d" % i)
    for i, (x, y) in enumerate(spots(art, rng, 3, 7, 15)):
        p.ell(x, y, 2, 1.2, (230, 120, 90), "coral%d" % i)
    return art.clip(stack(im, layer(p, outline=(25, 55, 60))))


def dark_portal(art):
    im = art.base("Desert", tint=(0.95, 0.6, 0.5))
    p = Paint(TW, TH)
    stone = (120, 110, 100)
    p.poly([(12, 50), (52, 50), (48, 44), (16, 44)], shade(stone, 0.9), "steps")
    p.poly([(13, 45), (21, 45), (20, 12), (14, 12)], stone, "pl")
    p.poly([(43, 45), (51, 45), (50, 12), (44, 12)], stone, "pr")
    p.poly([(8, 13), (56, 13), (54, 6), (10, 6)], shade(stone, 1.08), "top")
    for x in (10, 54):                                     # horns
        p.poly([(x - 2, 7), (x + 2, 7), (x + (4 if x > 32 else -4), 0)], (90, 80, 75), "horn%d" % x)
    p.poly([(22, 44), (42, 44), (42, 14), (22, 14)], (60, 160, 50), "portal")
    l = layer(p, outline=(40, 30, 28))
    sw = Paint(TW, TH)
    for i in range(60):                                    # swirl inside the gate
        th, r = i * 0.25, 1 + i * 0.16
        sw.dot(32 + math.cos(th) * r, 29 + math.sin(th) * r * 1.4, (190, 255, 120), "sw")
    return art.clip(stack(im, l, glow(layer(sw), FEL, 1.5, 1.3)))


def nexus(art):
    im = art.base("Snow")
    p = Paint(TW, TH)
    p.ell(32, 44, 20, 5, (150, 165, 190), "base")
    crystal(p, 32, 42, 30, 5, (120, 140, 255), "spire")
    crystal(p, 22, 44, 16, 3.5, (150, 120, 240), "s2")
    crystal(p, 43, 44, 18, 3.5, (110, 180, 255), "s3")
    for i, (x, y) in enumerate(((12, 18), (52, 14), (18, 8), (46, 26))):   # floating shards
        crystal(p, x, y, 7, 2, (160, 150, 255), "f%d" % i)
    l = layer(p, outline=(45, 45, 100))
    r = Paint(TW, TH)
    for i in range(48):
        th = i / 48 * math.tau
        r.dot(32 + math.cos(th) * 18, 26 + math.sin(th) * 5, (200, 210, 255), "ring")
    return art.clip(glow(stack(im, l, layer(r)), (150, 170, 255), 1.2, 0.6))


def galakrond(art):
    im = art.base("Snow")
    p = Paint(TW, TH)
    bone = (232, 226, 205)
    pts = [(10, 30), (18, 26), (28, 25), (38, 27), (48, 30), (56, 36)]
    for a, b in zip(pts, pts[1:]):
        p.line(*a, *b, 2, bone, "spine")
    for i, (x, y) in enumerate(pts[1:5]):                 # ribs
        for side in (-1, 1):
            p.line(x, y, x + side * 2, y + 9, 1, shade(bone, 0.92 if side > 0 else 1.0), "rib%d%d" % (i, side))
            p.line(x + side * 2, y + 9, x + side * 1, y + 14, 1, shade(bone, 0.85), "rib%d%d" % (i, side))
    p.poly([(2, 30), (10, 26), (13, 30), (9, 34), (3, 34)], bone, "skull")
    p.dot(8, 29, (40, 35, 40), "eye")
    p.line(10, 26, 14, 20, 1, bone, "horn")
    p.line(56, 36, 62, 44, 1, bone, "tail")
    for i, (x, y) in enumerate(((22, 14), (40, 12))):   # a wing bone
        p.line(28 if i == 0 else 38, 25, x, y, 1, bone, "wing%d" % i)
        p.line(x, y, x + (8 if i else -8), y + 6, 1, bone, "wing%d" % i)
    return art.clip(stack(im, layer(p, outline=(85, 90, 105))))


def sunken_temple(art):
    im = art.base("Grassland")
    p = Paint(TW, TH)
    rng = random.Random(28)
    p.ell(32, 30, 26, 17, (70, 100, 70), "swamp")
    jungle_blobs(p, rng, 32, 30, 24, 15, 10, "reeds")
    p.ell(32, 32, 20, 11, (65, 105, 95), "water")
    stone = (120, 135, 110)
    for k, (w, h) in enumerate(((16, 5), (12, 5), (8, 5), (4, 4))):
        y = 34 - k * 5
        p.poly([(32 - w, y), (32 + w, y), (32 + w - 2, y - h), (32 - w + 2, y - h)], shade(stone, 1 - k * 0.04), "tier%d" % k)
    p.line(32, 34, 32, 30, 2, (35, 40, 35), "door")
    p.line(26, 30, 24, 34, 1, (70, 120, 50), "vine")
    p.line(39, 25, 40, 29, 1, (70, 120, 50), "vine")
    return art.clip(stack(im, layer(p, outline=(35, 45, 35))))


def maraudon(art):
    im = art.base("Desert", tint=(0.85, 0.82, 0.8))
    p = Paint(TW, TH)
    mountain(p, 32, 50, 30, 30, (130, 105, 90), "hill")
    p.ell(32, 40, 10, 8, (30, 22, 28), "cave")
    p.ell(32, 44, 8, 3, (55, 42, 55), "floor")
    for i, (x, y, c) in enumerate(((19, 44, (170, 100, 220)), (45, 43, (170, 100, 220)), (24, 34, (230, 140, 60)),
                                   (41, 33, (230, 140, 60)))):
        crystal(p, x, y, 8, 2, c, "cr%d" % i)
    p.line(14, 22, 12, 34, 2, (90, 170, 90), "falls")
    return art.clip(stack(im, layer(p, outline=(45, 32, 30))))


def lifeblood(art):
    im = art.base("Grassland")
    p = Paint(TW, TH)
    rng = random.Random(29)
    jungle_blobs(p, rng, 32, 42, 26, 8, 22, "jb")
    p.poly([(26, 46), (38, 46), (37, 6), (27, 6)], STONE, "pillar")
    p.poly([(33, 46), (38, 46), (37, 6), (33, 6)], shade(STONE, 0.8), "pillarR")
    p.poly([(24, 8), (40, 8), (38, 3), (26, 3)], shade(STONE, 1.1), "cap")
    l = layer(p, outline=(55, 55, 50))
    w = Paint(TW, TH)
    for x in (25, 39):                                      # life-giving water pouring down
        w.line(x, 8, x + (-2 if x < 32 else 2), 44, 2, (110, 230, 170), "water")
    for y in (14, 24, 34):
        w.dot(32, y, (110, 210, 255), "rune")
    return art.clip(stack(im, l, glow(layer(w), (120, 255, 180), 1.4, 0.9)))


WONDERS = {
    "The Maelstrom": maelstrom, "Mount Hyjal": hyjal, "Teldrassil": teldrassil, "Moonglade": moonglade,
    "Lake Elune'ara": elune_ara, "Stonetalon Peak": stonetalon, "Red Rocks of Mulgore": red_rocks,
    "Thousand Needles": needles, "Un'Goro Crater": ungoro, "Lakkari Tar Pits": tar_pits,
    "Lost City of the Tol'vir": tolvir, "Blackrock Mountain": blackrock,
    "Cape of Stranglethorn": stranglethorn, "Kelp'thar Forest": kelpthar,
    "The Dark Portal": dark_portal, "The Nexus": nexus, "Galakrond's Rest": galakrond,
    "Sunken Temple": sunken_temple, "Maraudon": maraudon, "The Lifeblood Pillar": lifeblood,
}


def render_all(atlas):
    art = Art(atlas)
    out = {}
    for n, f in {**FEATURES, **WONDERS, **RESOURCES, **CAMPS}.items():
        out[n] = f(art)
    return out


def write_all(atlas, images_dir):
    """Write every tile into the HexaRealm and FantasyHex folders of `images_dir`."""
    tiles = render_all(atlas)
    for name, im in tiles.items():
        for folder, size in ((HR, None), (FH, (32, 28))):
            path = os.path.join(images_dir, folder, name + ".png")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            (im.resize(size, Image.BOX) if size else im).save(path)
    return len(tiles)


# ======================================================================= resources & drills (v0.8)
def _cluster(p, x, y, cols, n=3, h=6, w=1.6, part="c"):
    for k in range(n):
        dx = (k - (n - 1) / 2) * 2.6
        crystal(p, x + dx, y + abs(dx) * 0.3, h - abs(dx) * 0.6, w, cols[k % len(cols)], "%s%d" % (part, k))


def _rock_bed(p, x, y, r, col, part):
    p.ell(x, y, r, r * 0.55, col, part)
    p.ell(x - r * 0.4, y - r * 0.2, r * 0.45, r * 0.3, shade(col, 1.12), part + "h")


def res_azerite(art):
    """Azerite: golden crystal shards shot through with blue light, bursting from the ground."""
    rng = random.Random(41)
    p = Paint(TW, TH)
    for i, (x, y) in enumerate(((22, 30), (40, 26), (33, 40))):
        _rock_bed(p, x, y + 1, 6, (95, 80, 70), "bed%d" % i)
        _cluster(p, x, y, [(250, 200, 80), (255, 225, 120), (235, 175, 60)], n=3, h=rng.randint(8, 11), part="az%d" % i)
    l = layer(p, outline=(80, 55, 20))
    sp = Paint(TW, TH)
    for x, y in ((21, 24), (41, 20), (33, 33), (26, 29), (38, 25)):
        sp.dot(x, y, (140, 220, 255), "spark")
    return art.clip(stack(glow(l, (255, 200, 90), 1.6, 0.9), glow(layer(sp), (110, 200, 255), 1.0, 1.4)))


def res_arcane(art):
    p = Paint(TW, TH)
    for i, (x, y) in enumerate(((20, 28), (42, 30), (31, 40))):
        _rock_bed(p, x, y + 1, 6, (110, 105, 120), "bed%d" % i)
        _cluster(p, x, y, [(190, 120, 255), (230, 160, 255), (150, 110, 240)], n=3, h=9, part="ar%d" % i)
    return art.clip(glow(layer(p, outline=(60, 35, 100)), (200, 140, 255), 1.6, 1.0))


def res_ore(art, vein, bright, seed, rock=(105, 100, 98)):
    rng = random.Random(seed)
    p = Paint(TW, TH)
    for i, (x, y) in enumerate(((20, 28), (42, 26), (31, 39), (47, 38))):
        r = 7 if i < 3 else 4.5
        _rock_bed(p, x, y, r, rock, "rock%d" % i)
        for k in range(4 if i < 3 else 2):
            vx, vy = x + rng.uniform(-r * 0.6, r * 0.6), y + rng.uniform(-r * 0.3, r * 0.3)
            p.line(vx, vy, vx + rng.choice((-2, 2)), vy + rng.choice((-1, 1)), 1, vein, "vein%d%d" % (i, k))
            p.dot(vx, vy, bright, "vein%d%d" % (i, k))
    return art.clip(layer(p, outline=(45, 42, 40)))


def res_honeycomb(art, with_farm=False):
    p = Paint(TW, TH)
    for i, (x, y) in enumerate(((20, 32), (34, 27), (44, 38))):
        for k in range(3):                               # straw skep hive: stacked rings
            p.ell(x, y - k * 2.6, 5 - k * 1.3, 2.2, (215, 170, 80) if k % 2 == 0 else (190, 145, 60), "skep%d%d" % (i, k))
        p.ell(x, y + 1, 1.2, 0.9, (60, 40, 20), "door%d" % i)
    for i, (x, y) in enumerate(((27, 40), (39, 20))):  # spilled honeycomb
        for dx, dy in ((0, 0), (2, 0), (1, 1.6)):
            p.ell(x + dx, y + dy, 1, 0.8, (250, 200, 60), "comb%d" % i)
    l = layer(p, outline=(90, 60, 25))
    b = Paint(TW, TH)
    for x, y in ((24, 22), (31, 18), (47, 30), (16, 26), (40, 31)):
        b.dot(x, y, (30, 25, 15), "bee")
        b.dot(x + 1, y, (250, 210, 60), "bee")
    return art.clip(stack(l, layer(b)))


def res_glowcap(art):
    p = Paint(TW, TH)
    for i, (x, y, s) in enumerate(((20, 32, 1.0), (27, 36, 0.7), (40, 28, 1.1), (46, 33, 0.7), (33, 42, 0.9))):
        p.line(x, y, x, y - 5 * s, 2 if s > 0.8 else 1, (210, 220, 200), "stem%d" % i)
        p.ell(x, y - 5 * s - 1, 4 * s + 0.5, 2.3 * s + 0.4, (90, 210, 200), "cap%d" % i)
        p.dot(x - 1, y - 5 * s - 2, (200, 255, 245), "cap%d" % i)
    return art.clip(glow(layer(p, outline=(25, 70, 70)), (110, 240, 220), 1.6, 1.0))


def drill(art, sea=False, pillaged=False):
    """A goblin drilling rig: timber-and-brass derrick, gears and a glow of Azerite."""
    p = Paint(TW, TH)
    if sea:
        p.poly([(14, 40), (50, 40), (46, 46), (18, 46)], (120, 90, 60), "deck")
        for x in (18, 30, 44):
            p.line(x, 46, x, 52, 2, (90, 65, 45), "pile")
    else:
        p.ell(32, 42, 12, 4, (100, 80, 60), "pad")
        p.ell(32, 42, 4, 1.5, (250, 200, 80), "pool")
    wood, brass = (150, 100, 60), (210, 170, 70)
    top = 8 if not pillaged else 18
    p.line(24, 41, 31 if not pillaged else 26, top, 2, wood, "legL")
    p.line(40, 41, 33 if not pillaged else 36, top + (0 if not pillaged else 6), 2, wood, "legR")
    for y in range(top + 6, 40, 7):
        p.line(26, y, 38, y, 1, shade(wood, 0.85), "brace%d" % y)
    if not pillaged:
        p.line(32, top, 32, top - 3, 1, (90, 90, 95), "crown")
        p.ell(22, 36, 4, 4, brass, "gear")
        p.ell(22, 36, 1.5, 1.5, (110, 85, 40), "hub")
        p.poly([(38, 40), (46, 40), (46, 33), (38, 33)], (180, 70, 45), "engine")
        p.line(44, 33, 44, 26, 2, (90, 90, 95), "stack")
    l = layer(p, outline=(50, 35, 25))
    s = Paint(TW, TH)
    if not pillaged:
        s.ell(45, 23, 2.5, 2, (170, 170, 170), "smoke")
        s.ell(48, 19, 3, 2.3, (200, 200, 200), "smoke2")
    else:
        s.ell(33, 40, 3, 2, (60, 55, 50), "wreck")
    return art.clip(stack(glow(l, (255, 200, 90), 1.2, 0.5) if not pillaged else l, layer(s)))


def with_base(art, name, over):
    """Combine a stock improvement image (camp, plantation) with our resource art."""
    im = art.a.crop(HR + name) if (HR + name) in art.a.regions else Image.new("RGBA", (TW, TH))
    out = Image.new("RGBA", (TW, TH))
    out.alpha_composite(over(art))
    out.alpha_composite(im, (0, TH - im.height) if im.height <= TH else (0, 0))
    return out


RESOURCES = {
    "Azerite": res_azerite, "OilS": res_azerite, "Arcane Crystals": res_arcane,
    "Elementium": lambda art: res_ore(art, (90, 200, 220), (200, 250, 255), 42),
    "Thorium": lambda art: res_ore(art, (140, 190, 110), (220, 245, 190), 43, rock=(80, 78, 80)),
    "Honeycomb": res_honeycomb, "Glowcap": res_glowcap,
    "Glowcap+Camp": lambda art: with_base(art, "Camp", res_glowcap),
    "Glowcap+CampT": lambda art: with_base(art, "CampT" if (HR + "CampT") in art.a.regions else "Camp", res_glowcap),
    "Honeycomb+Plantation": lambda art: with_base(art, "Plantation", res_honeycomb),
    "Azerite Drill": lambda art: drill(art), "Azerite Drill-Pillaged": lambda art: drill(art, pillaged=True),
    "Azerite+Azerite Drill": lambda art: stack(res_azerite(art), drill(art)),
    "Azerite+Azerite Drill-Pillaged": lambda art: stack(res_azerite(art), drill(art, pillaged=True)),
    "Oil WellC": lambda art: drill(art, sea=True),
    "Tidal Drill": lambda art: drill(art, sea=True), "Azerite+Tidal Drill": lambda art: drill(art, sea=True),
}


# ======================================================================= barbarian camp (v0.10)
def encampment(art, snow=False):
    """A Defias hideout: a timbered mine mouth dug into a rocky mound, red-and-black
    tents, a sharpened palisade, a campfire and the Brotherhood's red kerchief banner."""
    p = Paint(TW, TH)
    ground = (185, 190, 200) if snow else (150, 118, 70)
    p.ell(32, 33, 23, 13, ground, "yard")
    p.ell(30, 31, 17, 9, shade(ground, 1.08), "yard2")
    # rocky mound with the mine entrance (back of the camp)
    rock = (118, 108, 98)
    p.ell(36, 20, 13, 9, rock, "mound")
    p.ell(31, 17, 7, 5, shade(rock, 1.1), "mound2")
    p.poly([(31, 26), (31, 18), (35, 15), (39, 18), (39, 26)], (22, 18, 18), "shaft")
    wood = (120, 80, 45)
    p.line(30, 26, 30, 17, 2, wood, "beamL")
    p.line(40, 26, 40, 17, 2, wood, "beamR")
    p.line(29, 16, 41, 16, 2, shade(wood, 1.1), "lintel")
    p.line(33, 26, 37, 22, 1, (150, 150, 160), "rail")          # mine-cart rail
    p.poly([(36, 27), (41, 27), (40, 24), (37, 24)], (95, 90, 95), "cart")
    # tents in the Brotherhood's red
    red, black = (160, 35, 30), (45, 35, 35)
    for i, (x, y) in enumerate(((17, 30), (47, 33))):
        p.poly([(x - 6, y + 4), (x + 6, y + 4), (x, y - 5)], red, "tent%d" % i)
        p.poly([(x, y - 5), (x + 6, y + 4), (x + 2, y + 4)], shade(red, 0.75), "tent%ds" % i)
        p.poly([(x - 1, y + 4), (x + 1, y + 4), (x, y)], black, "tent%dd" % i)
    # palisade of sharpened stakes around the front
    for i in range(13):
        a = math.pi * (0.08 + 0.84 * i / 12)
        x, y = 32 - math.cos(a) * 22, 35 + math.sin(a) * 9
        p.line(x, y, x, y - 5, 1, shade(wood, 0.9 + 0.1 * (i % 2)), "stake%d" % i)
        p.dot(x, y - 6, shade(wood, 1.25), "tip%d" % i)
    # banner: a red kerchief on a pole
    p.line(12, 31, 12, 14, 1, (90, 60, 35), "pole")
    p.poly([(13, 14), (20, 15), (18, 17), (20, 19), (13, 19)], red, "flag")
    p.dot(15, 16, black, "flagmark")
    p.dot(16, 16, black, "flagmark")
    # campfire
    for dx in (-2, 0, 2):
        p.line(32 + dx, 36, 32 - dx, 34, 1, (80, 50, 30), "logs")
    s = layer(p, outline=(40, 30, 25))
    f = Paint(TW, TH)
    f.dot(32, 33, (255, 200, 60), "fire")
    f.dot(31, 33, (255, 140, 40), "fire")
    f.dot(33, 33, (255, 140, 40), "fire")
    f.dot(32, 32, (255, 230, 120), "fire")
    return art.clip(stack(s, glow(layer(f), (255, 150, 50), 1.4, 1.3)))


CAMPS = {"Barbarian encampment": encampment,
         "Barbarian encampmentT": lambda art: encampment(art, snow=True)}
