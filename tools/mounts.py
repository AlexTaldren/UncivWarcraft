"""Race mounts for the mounted units, drawn as pixel art in code.

Each race rides its own beast (wolves for orcs, rams for dwarves, mechanical striders
for gnomes, ...). A mount is painted from simple shapes (ellipses, polygons, thick
lines) into a part map; shading and a dark outline are then added automatically so it
sits with Unciv's pixel art. The rider is the race's own foot sprite, cut at the hip
and seated in the saddle; the saddle blanket goes on the faction-colour layer.
The designs follow broad fantasy archetypes, not Blizzard's artwork.
"""
import math
from PIL import Image

OUTLINE = (30, 24, 22)


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


class Paint:
    """A small canvas of (colour, part) cells. Later strokes cover earlier ones."""

    def __init__(self, w, h, scale=1.0):
        self.s = scale
        self.w, self.h = int(w * scale), int(h * scale)
        self.c = {}          # (x, y) -> (rgb, part, layer)   layer: 0 base, 1 inner tint, 2 outer tint

    def dot(self, x, y, col, part, layer=0):
        self._set(x * self.s, y * self.s, col, part, layer)

    def _set(self, x, y, col, part, layer=0):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h:
            self.c[(x, y)] = (tuple(col), part, layer)

    def ell(self, cx, cy, rx, ry, col, part, layer=0):
        k = self.s
        self._ell(cx * k, cy * k, rx * k, ry * k, col, part, layer)

    def _ell(self, cx, cy, rx, ry, col, part, layer=0):
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                if ((x - cx) / max(rx, .5)) ** 2 + ((y - cy) / max(ry, .5)) ** 2 <= 1.0:
                    self._set(x, y, col, part, layer)

    def poly(self, pts, col, part, layer=0):
        pts = [(x * self.s, y * self.s) for x, y in pts]
        ys = [p[1] for p in pts]
        for y in range(int(min(ys)), int(max(ys)) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
                if (y0 <= y + .5 < y1) or (y1 <= y + .5 < y0):
                    xs.append(x0 + (y + .5 - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2]):
                for x in range(int(round(a)), int(round(b)) + 1):
                    self._set(x, y, col, part, layer)

    def line(self, x0, y0, x1, y1, wd, col, part, layer=0):
        k = self.s
        x0, y0, x1, y1 = x0 * k, y0 * k, x1 * k, y1 * k
        wd = wd * k if wd > 1 else 1
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        for i in range(n + 1):
            t = i / n
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            if wd <= 1.3:
                self._set(x, y, col, part, layer)
            else:
                self._ell(x, y, wd / 2 - .25, wd / 2 - .25, col, part, layer)

    def leg(self, x, top, length, wd, col, part, bend=0, hoof=None):
        """A leg from its top to the ground; `bend` shifts the lower half (knee)."""
        mid = top + length * .5
        self.line(x, top, x + bend, mid, wd, col, part)
        self.line(x + bend, mid, x + bend * .3, top + length, max(1, wd - 1), col, part)
        if hoof:
            for dx in range(-1, max(1, wd - 1)):
                self.dot(x + bend * .3 + dx, top + length, hoof, part + "h")

    def render(self):
        """Return (base, inner, outer) RGBA images: auto-shaded and outlined."""
        base = Image.new("RGBA", (self.w, self.h))
        l1, l2 = Image.new("RGBA", (self.w, self.h)), Image.new("RGBA", (self.w, self.h))
        bp, p1, p2 = base.load(), l1.load(), l2.load()
        for (x, y), (col, part, layer) in self.c.items():
            up, dn = self.c.get((x, y - 1)), self.c.get((x, y + 1))
            k = 1.0
            if up is None or up[1] != part:
                k = 1.18
            elif dn is None or dn[1] != part:
                k = 0.78
            lt = self.c.get((x - 1, y))
            if k == 1.0 and (lt is None or lt[1] != part):
                k = 1.08
            if layer == 0:
                bp[x, y] = shade(col, k) + (255,)
            else:
                g = int(max(0, min(255, 225 * k)))
                (p1 if layer == 1 else p2)[x, y] = (g, g, g, 255)
                bp[x, y] = (g, g, g, 255)
        for y in range(self.h):
            for x in range(self.w):
                if (x, y) in self.c:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if (x + dx, y + dy) in self.c:
                        bp[x, y] = OUTLINE + (255,)
                        break
        return base, l1, l2


# --------------------------------------------------------------------- mount designs
# Canvas: 56 x 44, facing left, ground line at y = GY. Each design returns the saddle
# point (x, y) where the rider sits. `armored` adds barding for heavy cavalry.
W, H, GY = 56, 44, 42

METAL, METAL_D, GOLD, BONE = (165, 172, 185), (105, 110, 125), (220, 180, 70), (222, 214, 186)


def blanket(p, x, y, wd, ht):
    """Saddle cloth in the faction colour (inner tint layer), with a leather saddle."""
    p.poly([(x - wd / 2, y), (x + wd / 2, y), (x + wd / 2 - 1, y + ht), (x - wd / 2 + 1, y + ht)],
           (225, 225, 225), "blanket", layer=1)
    p.line(x - 3, y - 1, x + 3, y - 1, 2, (110, 70, 40), "saddle")


def barding(p, x0, x1, y, ht):
    """Armour plates over the body for knights and lancers (outer tint layer trim)."""
    p.poly([(x0, y), (x1, y), (x1 - 1, y + ht), (x0 + 1, y + ht)], METAL, "bard")
    p.line(x0 + 1, y + ht, x1 - 1, y + ht, 1, (225, 225, 225), "trim", layer=2)


def quad_body(p, cx, cy, ln, ht, col, belly=None):
    p.ell(cx, cy, ln / 2, ht / 2, col, "body")
    if belly:
        p.ell(cx, cy + ht * .28, ln / 2 - 3, ht / 4, belly, "body")


def wolf(p, v, armored):
    furs = [(92, 84, 78), (60, 55, 52), (120, 92, 66), (150, 145, 138)]
    fur = furs[v % len(furs)]
    dark, light = shade(fur, .7), shade(fur, 1.25)
    # far legs, bushy tail, long low body, near legs, ruff and head
    p.leg(19, 26, 15, 3, dark, "far", bend=-1)
    p.leg(38, 26, 15, 3, dark, "far", bend=1)
    for (x0, y0), (x1, y1), wd in (((42, 21), (48, 25), 5), ((48, 25), (51, 31), 4), ((51, 31), (50, 34), 2)):
        p.line(x0, y0, x1, y1, wd, fur, "tail")
    p.dot(50, 34, light, "tail")
    quad_body(p, 30, 23, 27, 9, fur, light)
    p.ell(21, 21, 6, 6, shade(fur, 1.05), "ruff")       # shaggy shoulders
    for x in range(16, 26, 2):
        p.dot(x, 15 + (x % 4) // 2, dark, "ruff")
    p.leg(22, 26, 15, 3, fur, "near", bend=-2)
    p.leg(41, 26, 15, 3, fur, "near", bend=2)
    p.ell(12, 18, 5, 4, fur, "head")
    p.poly([(9, 17), (2, 19), (3, 21), (10, 22)], light, "snout")
    p.dot(2, 19, (20, 20, 20), "nose")
    p.dot(10, 17, (230, 70, 40), "eye")
    for ex in (11, 14):
        p.poly([(ex, 15), (ex + 3, 15), (ex + 2, 10)], dark, "ear")
    p.line(4, 22, 8, 22, 1, (240, 235, 220), "fang")
    if armored:
        barding(p, 22, 39, 18, 7)
        p.line(10, 14, 16, 14, 1, METAL, "helm")
    blanket(p, 31, 16, 10, 6)
    for sx in (27, 35):                              # spikes on the saddle
        p.line(sx, 15, sx, 12, 1, METAL, "spike")
    return 31, 16


def ram(p, v, armored):
    wools = [(150, 120, 90), (205, 195, 175), (110, 85, 65), (175, 170, 160)]
    wool = wools[v % len(wools)]
    p.leg(20, 27, 13, 4, shade(wool, .65), "far", hoof=(50, 40, 30))
    p.leg(38, 27, 13, 4, shade(wool, .65), "far", hoof=(50, 40, 30))
    p.ell(44, 21, 3, 3, wool, "tail")
    quad_body(p, 30, 23, 28, 14, wool)
    for x in range(18, 43, 3):                        # curly fleece
        p.dot(x, 18 + (x % 2), shade(wool, 1.2), "body")
        p.dot(x + 1, 25 + (x % 2), shade(wool, .85), "body")
    p.leg(23, 28, 12, 4, shade(wool, .8), "near", hoof=(50, 40, 30))
    p.leg(41, 28, 12, 4, shade(wool, .8), "near", hoof=(50, 40, 30))
    p.line(19, 21, 14, 16, 7, wool, "neck")
    p.ell(11, 16, 5, 4, shade(wool, .9), "head")
    p.poly([(8, 16), (4, 18), (5, 21), (9, 20)], shade(wool, .8), "snout")
    p.dot(9, 15, (25, 20, 20), "eye")
    horn = (225, 210, 170)                            # big curled horn
    for a in range(0, 300, 30):
        r = 4 - a / 120
        p.dot(14 + r * math.cos(math.radians(a - 90)), 15 + r * math.sin(math.radians(a - 90)) - 1,
              horn, "horn")
        p.dot(14 + r * math.cos(math.radians(a - 90)) + 1, 15 + r * math.sin(math.radians(a - 90)) - 1,
              shade(horn, .85), "horn")
    p.line(5, 21, 8, 23, 2, shade(wool, 1.15), "beard")
    if armored:
        barding(p, 21, 40, 19, 8)
    blanket(p, 30, 16, 11, 6)
    return 30, 16


def mechanostrider(p, v, armored):
    metals = [METAL, (200, 120, 90), (120, 170, 190), (200, 190, 120)]
    m = metals[v % len(metals)]
    dk = shade(m, .6)
    for x, b in ((24, -3), (32, 3)):                  # two jointed legs (far one darker)
        col = dk if x == 24 else shade(m, .85)
        p.line(x, 24, x + b, 32, 2, col, "leg" + str(x))
        p.line(x + b, 32, x, GY - 1, 2, col, "leg" + str(x))
        p.dot(x + b, 32, GOLD, "knee" + str(x))
        p.line(x - 2, GY, x + 2, GY, 1, dk, "foot" + str(x))
    p.ell(28, 20, 9, 6, m, "body")
    p.line(19, 19, 12, 12, 3, dk, "neck")
    p.ell(10, 10, 4, 3, m, "head")
    p.poly([(7, 9), (2, 11), (7, 12)], GOLD, "beak")
    p.ell(10, 9, 1, 1, (255, 235, 120), "lamp")
    p.line(37, 18, 42, 14, 2, dk, "tail")
    p.dot(42, 13, (90, 220, 255), "tail")
    for x in (24, 28, 32):
        p.dot(x, 22, GOLD, "rivet")
    if armored:
        p.line(21, 15, 35, 15, 2, METAL_D, "plate")
    blanket(p, 28, 14, 9, 4)
    return 28, 14


def nightsaber(p, v, armored):
    furs = [(95, 75, 140), (60, 55, 95), (180, 175, 195), (70, 90, 120)]
    fur = furs[v % len(furs)]
    stripe = shade(fur, .6)
    p.leg(19, 26, 16, 3, shade(fur, .7), "far", bend=-1)
    p.leg(39, 26, 16, 3, shade(fur, .7), "far", bend=1)
    pts = [(44, 23), (49, 26), (52, 22), (53, 16)]    # long curling tail
    for a, b in zip(pts, pts[1:]):
        p.line(*a, *b, 3, fur, "tail")
    quad_body(p, 31, 23, 28, 10, fur, shade(fur, 1.2))
    for x in range(22, 42, 4):
        p.line(x, 19, x + 1, 24, 1, stripe, "body")
    p.leg(22, 26, 16, 3, fur, "near", bend=-2)
    p.leg(42, 26, 16, 3, fur, "near", bend=2)
    p.line(20, 21, 15, 16, 6, fur, "neck")
    p.ell(12, 15, 5, 4, fur, "head")
    p.poly([(8, 15), (5, 17), (9, 19)], shade(fur, 1.15), "snout")
    p.dot(10, 14, (120, 255, 200), "eye")
    for ex in (11, 15):
        p.poly([(ex, 12), (ex + 2, 12), (ex + 1, 9)], stripe, "ear")
    if armored:
        barding(p, 22, 40, 18, 7)
        p.line(9, 12, 14, 12, 1, (210, 210, 230), "circlet")
    blanket(p, 31, 16, 10, 6)
    return 31, 16


def kodo(p, v, armored):
    hides = [(130, 115, 95), (100, 90, 80), (150, 125, 95)]
    hide = hides[v % len(hides)]
    dk = shade(hide, .7)
    p.leg(17, 28, 13, 6, dk, "far", hoof=(55, 45, 35))
    p.leg(41, 28, 13, 6, dk, "far", hoof=(55, 45, 35))
    p.line(49, 22, 52, 28, 2, dk, "tail")
    quad_body(p, 30, 24, 36, 18, hide, shade(hide, 1.15))
    for x in range(16, 46, 5):                        # leathery wrinkles
        p.line(x, 17, x + 1, 21, 1, dk, "body")
    p.leg(21, 29, 12, 6, hide, "near", hoof=(55, 45, 35))
    p.leg(45, 29, 12, 6, hide, "near", hoof=(55, 45, 35))
    p.ell(10, 22, 7, 6, hide, "head")               # big low head
    p.poly([(9, 14), (16, 13), (17, 22), (12, 18)], shade(hide, 1.2), "frill")
    p.line(6, 18, 2, 12, 2, BONE, "horn")
    p.line(4, 24, 2, 28, 2, BONE, "tusk")
    p.dot(7, 20, (30, 25, 20), "eye")
    if armored:
        barding(p, 18, 42, 18, 9)
    p.line(23, 11, 37, 11, 1, (120, 80, 50), "rail")   # a howdah frame
    blanket(p, 30, 13, 14, 6)
    return 30, 13


def raptor(p, v, armored):
    scales = [(70, 130, 70), (180, 100, 50), (60, 110, 150), (160, 70, 140)]
    sc = scales[v % len(scales)]
    belly, stripe = shade(sc, 1.3), shade(sc, .6)
    p.line(33, 24, 37, 33, 3, shade(sc, .7), "farleg")
    p.line(37, 33, 34, GY, 2, shade(sc, .7), "farleg")
    pts = [(38, 20), (46, 19), (53, 15)]               # long stiff tail
    for a, b in zip(pts, pts[1:]):
        p.line(*a, *b, 4 if a[0] == 38 else 2, sc, "tail")
    p.ell(30, 21, 10, 6, sc, "body")
    p.ell(30, 24, 7, 3, belly, "body")
    for x in range(24, 38, 4):
        p.line(x, 16, x - 1, 20, 1, stripe, "body")
    p.line(29, 24, 32, 33, 4, sc, "leg")
    p.line(32, 33, 29, GY, 2, sc, "leg")
    p.line(26, GY, 31, GY, 1, (230, 220, 200), "claw")
    p.line(21, 19, 15, 12, 4, sc, "neck")
    p.poly([(16, 8), (5, 10), (4, 13), (15, 14)], sc, "head")
    p.line(5, 13, 13, 14, 1, belly, "jaw")
    p.dot(13, 10, (250, 200, 40), "eye")
    p.line(19, 22, 17, 25, 1, stripe, "arm")
    for x in (14, 17, 20):                             # crest quills
        p.line(x, 8, x + 1, 5, 1, (220, 60, 50), "quill")
    if armored:
        p.line(23, 16, 37, 16, 2, METAL, "bard")
    blanket(p, 30, 14, 9, 5)
    return 30, 14


def hawkstrider(p, v, armored):
    plumes = [(190, 50, 40), (220, 170, 60), (200, 90, 50), (240, 230, 210)]
    pl = plumes[v % len(plumes)]
    leg = (230, 180, 60)
    p.line(31, 25, 34, 33, 2, shade(leg, .7), "farleg")
    p.line(34, 33, 31, GY, 1, shade(leg, .7), "farleg")
    p.ell(29, 21, 9, 7, pl, "body")
    p.poly([(36, 17), (46, 13), (47, 18), (38, 24)], shade(pl, .8), "tailf")
    p.poly([(37, 19), (49, 20), (39, 25)], shade(GOLD, 1.0), "tailf2")
    p.line(27, 26, 30, 33, 2, leg, "leg")
    p.line(30, 33, 27, GY, 1, leg, "leg")
    p.line(24, GY, 29, GY, 1, leg, "toe")
    p.line(22, 18, 17, 9, 3, pl, "neck")
    p.ell(16, 7, 3, 3, pl, "head")
    p.poly([(13, 6), (8, 8), (13, 9)], GOLD, "beak")
    p.dot(15, 6, (30, 25, 20), "eye")
    p.line(18, 5, 22, 1, 1, GOLD, "crest")
    p.line(19, 5, 24, 3, 1, pl, "crest2")
    if armored:
        p.line(22, 15, 35, 15, 2, GOLD, "bard")
    blanket(p, 29, 14, 9, 5)
    return 29, 14


def horse(p, v, armored, coat, mane, skeletal=False):
    dk = shade(coat, .7)
    hoof = (50, 45, 40)
    p.leg(19, 26, 16, 3, dk, "far", bend=-1, hoof=hoof)
    p.leg(38, 26, 16, 3, dk, "far", bend=1, hoof=hoof)
    p.line(44, 20, 48, 30, 3, mane, "tail")
    quad_body(p, 30, 22, 28, 11, coat)
    if skeletal:                                       # ribs: dark gaps through the body
        for x in range(21, 38, 3):
            p.line(x, 19, x, 26, 1, (40, 45, 35), "body")
        p.ell(30, 23, 3, 2, (90, 200, 90), "body")      # unholy glow inside
    p.leg(22, 26, 16, 3, coat, "near", bend=-2, hoof=hoof)
    p.leg(41, 26, 16, 3, coat, "near", bend=2, hoof=hoof)
    p.line(19, 20, 14, 11, 6, coat, "neck")
    p.line(17, 11, 20, 18, 2, mane, "mane")
    p.poly([(15, 8), (7, 12), (6, 15), (9, 16), (16, 13)], coat, "head")
    p.dot(13, 10, (130, 255, 130) if skeletal else (25, 20, 20), "eye")
    p.poly([(14, 8), (15, 4), (17, 8)], dk, "ear")
    if armored:
        barding(p, 21, 39, 18, 7)
        p.poly([(15, 9), (8, 12), (9, 14), (15, 12)], METAL, "chanfron")
    blanket(p, 30, 15, 10, 6)
    return 30, 15


def elekk(p, v, armored):
    hides = [(135, 125, 160), (110, 110, 135), (160, 140, 170)]
    hide = hides[v % len(hides)]
    dk = shade(hide, .7)
    p.leg(18, 29, 12, 6, dk, "far")
    p.leg(40, 29, 12, 6, dk, "far")
    quad_body(p, 30, 24, 34, 17, hide)
    p.leg(22, 29, 12, 6, hide, "near")
    p.leg(44, 29, 12, 6, hide, "near")
    p.ell(11, 20, 7, 7, hide, "head")
    p.ell(16, 19, 4, 6, shade(hide, .85), "ear")
    p.line(6, 23, 4, 30, 3, hide, "trunk")
    p.line(4, 30, 6, 33, 2, hide, "trunk")
    p.line(8, 26, 3, 25, 2, BONE, "tusk")
    p.line(3, 25, 2, 22, 1, BONE, "tusk")
    p.dot(9, 18, (40, 30, 30), "eye")
    for x in range(20, 42, 6):                         # ornaments on the flank
        p.dot(x, 28, GOLD, "body")
    if armored:
        barding(p, 19, 41, 18, 8)
    blanket(p, 30, 13, 13, 7)
    return 30, 13


def dragon_turtle(p, v, armored):
    shells = [(60, 120, 70), (50, 100, 110), (90, 120, 60)]
    sh = shells[v % len(shells)]
    skin = (200, 90, 60) if v % 2 else (220, 170, 70)
    p.leg(21, 30, 11, 5, shade(skin, .7), "far")
    p.leg(39, 30, 11, 5, shade(skin, .7), "far")
    p.line(46, 30, 51, 32, 2, skin, "tail")
    p.ell(30, 26, 18, 10, sh, "shell")
    p.line(14, 31, 46, 31, 2, (220, 200, 140), "rim")
    for cx in (22, 30, 38):                            # shell plates
        p.ell(cx, 23, 3, 3, shade(sh, 1.2), "plate" + str(cx))
    p.leg(24, 31, 10, 5, skin, "near")
    p.leg(42, 31, 10, 5, skin, "near")
    p.line(15, 28, 9, 22, 5, skin, "neck")
    p.ell(7, 20, 5, 4, skin, "head")
    p.line(3, 17, 1, 13, 1, (240, 230, 200), "whisker")
    p.line(8, 16, 11, 12, 1, GOLD, "horn")
    p.dot(6, 19, (25, 20, 20), "eye")
    if armored:
        p.line(18, 17, 42, 17, 2, GOLD, "bard")
    blanket(p, 30, 15, 12, 4)
    return 30, 15


def trike(p, v, armored):
    frames = [(180, 60, 40), (90, 100, 110), (200, 150, 50)]
    fr = frames[v % len(frames)]
    tire = (40, 38, 36)
    p.ell(38, 34, 8, 8, tire, "wheelfar")
    p.ell(38, 34, 3, 3, METAL, "hubfar")
    p.poly([(14, 28), (40, 22), (42, 30), (16, 33)], fr, "frame")
    p.line(14, 26, 10, 17, 2, METAL_D, "fork")
    p.line(8, 16, 14, 16, 1, METAL, "bars")
    p.ell(12, 34, 6, 6, tire, "wheel")
    p.ell(12, 34, 2, 2, METAL, "hub")
    p.ell(40, 35, 7, 7, shade(tire, 1.2), "wheelnear")
    p.ell(40, 35, 2, 2, GOLD, "hubnear")
    p.line(44, 26, 50, 20, 2, METAL_D, "exhaust")
    p.ell(51, 17, 2, 2, (150, 150, 150), "smoke")
    p.ell(53, 13, 2, 2, (180, 180, 180), "smoke2")
    if armored:
        p.poly([(16, 22), (26, 20), (26, 26), (17, 27)], METAL, "plow")
    blanket(p, 30, 20, 9, 4)
    return 30, 20


RACE_MOUNT = {
    "Orcs": wolf, "Dwarves": ram, "Gnomes": mechanostrider, "Night Elves": nightsaber,
    "Tauren": kodo, "Trolls": raptor, "Blood Elves": hawkstrider, "Draenei": elekk,
    "Pandaren": dragon_turtle, "Goblins": trike,
    "Forsaken": lambda p, v, a: horse(p, v, a, BONE, (70, 90, 60), skeletal=True),
    "High Elves": lambda p, v, a: horse(p, v, a, (235, 232, 222), (225, 190, 90)),
    "Worgen": lambda p, v, a: horse(p, v, a, [(60, 45, 35), (40, 38, 36), (95, 80, 65)][v % 3],
                                    (25, 22, 20)),
}
MOUNT_NAME = {
    "Orcs": "wolf", "Dwarves": "ram", "Gnomes": "mechanostrider", "Night Elves": "nightsaber",
    "Tauren": "kodo", "Trolls": "raptor", "Blood Elves": "hawkstrider", "Draenei": "elekk",
    "Pandaren": "dragon turtle", "Goblins": "trike", "Forsaken": "skeletal horse",
    "High Elves": "white steed", "Worgen": "Gilnean horse",
}


SCALE = {"Tauren": 1.35, "Draenei": 1.3, "Pandaren": 1.25, "Trolls": 1.2, "Gnomes": 1.05,
         "Goblins": 1.1, "Dwarves": 1.15}


def draw_mount(race, variant, armored, legc=None):
    """Paint the mount; if `legc` is given, also the rider's near leg down its flank."""
    p = Paint(W, H, SCALE.get(race, 1.2))
    sx, sy = RACE_MOUNT[race](p, variant, armored)
    if legc:
        p.line(sx - 1, sy + 1, sx - 3, sy + 6, 3, legc, "rleg")
        p.line(sx - 3, sy + 6, sx - 2, sy + 8, 2, legc, "rleg")
        p.line(sx - 5, sy + 9, sx - 2, sy + 9, 2, (45, 35, 30), "boot")
    return p.render(), (int(sx * p.s), int(sy * p.s)), int(GY * p.s)


# --------------------------------------------------------------------- composing
def rider(layers, cut=0.56):
    """Upper body of a foot sprite: everything above the hip, on every layer."""
    boxes = [l.getbbox() for l in layers if l.getbbox()]
    x0, y0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
    x1, y1 = max(b[2] for b in boxes), max(b[3] for b in boxes)
    hip = y0 + int((y1 - y0) * cut)
    out = [l.crop((x0, y0, x1, hip)) for l in layers]
    # where the torso is: the median column of opaque pixels in the bottom rows
    px = out[0].load()
    cols = [x for y in range(max(0, out[0].height - 4), out[0].height)
            for x in range(out[0].width) if px[x, y][3] > 200]
    cx = sorted(cols)[len(cols) // 2] if cols else out[0].width // 2
    # leg colour: the pixel just below the hip in the middle of the body
    lp = layers[0].load()
    legc = None
    for dy in range(1, 6):
        c = lp[x0 + cx, min(layers[0].height - 1, hip + dy)]
        if c[3] > 200 and sum(c[:3]) > 90:
            legc = c[:3]
            break
    return out, cx, legc or (80, 70, 60)


def compose(rider_layers, race, variant, armored, canvas, ground, center_x):
    """Mount + seated rider on an output canvas of size `canvas`, with the mount's
    feet on `ground` and centred at `center_x`. Returns [base, -1, -2]."""
    up, rcx, legc = rider(rider_layers)
    (mb, m1, m2), (sx, sy), gy = draw_mount(race, variant, armored, legc)
    mbox = mb.getbbox()
    ox = int(center_x - (mbox[0] + mbox[2]) / 2)
    ox = max(1 - mbox[0], min(ox, canvas[0] - 1 - mbox[2]))      # keep it on the canvas
    oy = ground - gy
    out = [Image.new("RGBA", canvas) for _ in range(3)]
    for im, m in zip(out, (mb, m1, m2)):
        im.alpha_composite(m, (ox, oy))
    # rider: hip on the saddle, torso over the seat
    rx, ry = ox + sx - rcx, max(0, oy + sy - up[0].height + 2)
    for im, r in zip(out, up):
        im.alpha_composite(r, (rx, ry))
    # the mount's tint layers must not show through the rider
    rp = up[0].load()
    own = [r.load() for r in up[1:]]
    for im in out[1:]:
        px = im.load()
        for y in range(up[0].height):
            for x in range(up[0].width):
                X, Y = rx + x, ry + y
                if rp[x, y][3] > 0 and 0 <= X < canvas[0] and 0 <= Y < canvas[1] \
                        and not any(o[x, y][3] for o in own):
                    px[X, Y] = (0, 0, 0, 0)
    return out
