"""Painted-style Human and Orc unit sprites (trial of the "closer to Warcraft" look).

Original designs drawn with paint.py, following the broad tenets of the Warcraft look
rather than any specific Blizzard artwork: chunky, exaggerated proportions (huge
shoulders, hands and weapons on short legs), bold saturated colours, rounded painted
shading and thick dark outlines that read from far away.

Each function draws one unit into a Canvas at feet position (fx, fy), facing right.
"""
import math
from paint import Canvas, grey, mix, S

# ------------------------------------------------------------------ palette
STEEL = (178, 188, 205)
DSTEEL = (120, 128, 145)
IRON = (112, 102, 96)
RUST = (130, 82, 50)
LEATHER = (125, 78, 42)
DLEATHER = (84, 52, 30)
WOOD = (150, 100, 55)
BONE = (238, 228, 196)
HSKIN = (238, 186, 146)
OSKIN = (98, 158, 58)
OHAIR = (34, 28, 24)
CLOTH_BROWN = (150, 112, 70)
CLOTH_TAN = (200, 170, 120)
GOLD = (240, 200, 90)
L_MAIN = grey(0.96)     # tinted-layer greys
L_DARK = grey(0.72)


class Fig:
    """Local coordinates: feet at (0, 0), y up is negative, about 1 px per unit at u=1."""
    def __init__(self, c, fx, fy, u=1.0, flip=False):
        self.c, self.fx, self.fy, self.u = c, fx, fy, u

    def p(self, x, y):
        return (self.fx + x * self.u, self.fy + y * self.u)

    def r(self, v):
        return v * self.u

    # shape shortcuts in local coordinates
    def poly(self, pts, m=None):
        return self.c.poly([self.p(*q) for q in pts], m)

    def ell(self, x, y, rx, ry, m=None, rot=0):
        X, Y = self.p(x, y)
        return self.c.ellipse(X, Y, self.r(rx), self.r(ry), m, rot)

    def cap(self, a, b, r1, r2=None, m=None):
        return self.c.capsule(self.p(*a), self.p(*b), self.r(r1), None if r2 is None else self.r(r2), m)

    def curve(self, pts, r1, r2=None, m=None):
        return self.c.curve([self.p(*q) for q in pts], self.r(r1), None if r2 is None else self.r(r2), m)

    def paint(self, m, color, **kw):
        self.c.paint(m, color, **kw)


# ================================================================== shared parts
def shadow(f, w=24):
    X, Y = f.p(0, 0)
    f.c.shadow(X, Y, f.r(w), f.r(w * 0.22))


def boot(f, x, y, color=DLEATHER, size=1.0, dark=1.0, mat="leather"):
    f.paint(f.poly([(x - 6 * size, y - 6 * size), (x + 3 * size, y - 6.5 * size), (x + 10 * size, y - 2.5 * size),
                    (x + 10 * size, y + 0.5), (x - 7 * size, y + 0.5)]), color, mat=mat, dark=dark)


# ----------------------------------------------------------------- orc body
def orc_legs(f, near=True, far=True, pants=DLEATHER, wraps=True, skin=OSKIN):
    if far:
        f.paint(f.cap((-6, -30), (-11, -15), 9, 7.5), pants, mat="leather", dark=0.78)
        f.paint(f.cap((-11, -15), (-11, -5), 7, 6.5), skin, mat="skin", dark=0.78)
        boot(f, -11, 0, DLEATHER, 1.0, dark=0.78)
    if near:
        f.paint(f.cap((5, -30), (9, -15), 10, 8), pants, mat="leather")
        f.paint(f.cap((9, -15), (10, -5), 7.5, 7), skin, mat="skin")
        if wraps:
            f.paint(f.poly([(3.5, -12), (16, -12), (16, -7), (3.5, -7)]), L_DARK, layer="l1", mat="cloth", outline=0.6)
        boot(f, 11, 0, DLEATHER, 1.1)


def orc_torso(f, skin=OSKIN, belt=True, loin=True):
    body = f.poly([(-17, -28), (15, -28), (22, -44), (25, -60), (17, -74), (-9, -76), (-23, -66), (-22, -46)])
    f.paint(body, skin, mat="skin")
    # chest and belly lines (dark painted strokes)
    f.paint(f.curve([(4, -64), (12, -58), (20, -60)], 0.9), mix(skin, (20, 40, 10), 0.6), mat="flat", outline=0)
    f.paint(f.curve([(8, -48), (14, -44), (19, -46)], 0.8), mix(skin, (20, 40, 10), 0.6), mat="flat", outline=0)
    if belt:
        f.paint(f.c.intersect(body, f.poly([(-30, -38), (30, -38), (30, -26), (-30, -26)])), LEATHER, mat="leather")
        f.paint(f.ell(10, -33, 4.5, 4.5), IRON, mat="metal")
        # bandolier strap across the chest
        f.paint(f.c.intersect(body, f.poly([(-20, -72), (-12, -74), (20, -36), (12, -34)])), LEATHER, mat="leather", outline=0.6)
    if loin:
        loincloth(f)


def loincloth(f, x=0):
    f.paint(f.poly([(x + 1, -32), (x + 17, -32), (x + 16, -13), (x + 12, -16), (x + 9, -10), (x + 6, -15), (x + 2, -12)]),
            L_MAIN, layer="l2", mat="cloth")


def orc_head(f, x=16, y=-73, skin=OSKIN, hair="topknot", helm=False, eye=(255, 70, 40)):
    # pointed ear, swept back
    f.paint(f.poly([(x - 6, y - 2), (x - 18, y - 8), (x - 5, y + 4)]), skin, mat="skin", dark=0.9)
    # skull
    f.paint(f.ell(x, y - 1, 10, 10), skin, mat="skin")
    # heavy jutting jaw
    f.paint(f.poly([(x - 2, y + 2), (x + 13, y + 1), (x + 14, y + 8), (x + 9, y + 11), (x - 1, y + 10)]), skin, mat="skin")
    # mouth line
    f.paint(f.curve([(x + 4, y + 6), (x + 9, y + 7), (x + 13, y + 5)], 0.7), (40, 30, 25), mat="flat", outline=0)
    # tusks
    f.paint(f.curve([(x + 11, y + 6), (x + 13.5, y + 2), (x + 12.5, y - 2)], 1.8, 0.6), BONE, mat="bone", outline=0.7)
    f.paint(f.curve([(x + 4, y + 6), (x + 5.5, y + 3), (x + 4.5, y + 0.5)], 1.4, 0.5), BONE, mat="bone", outline=0.6, dark=0.85)
    # brow ridge and glowing eye
    f.paint(f.poly([(x + 1, y - 6), (x + 12, y - 5), (x + 11, y - 2), (x + 2, y - 3)]), mix(skin, (0, 0, 0), 0.35), mat="skin", outline=0.5)
    e = f.ell(x + 8, y - 1.5, 1.8, 1.3)
    f.c.glow(e, eye, radius=1.5, strength=0.5)
    f.paint(e, eye, mat="glow", outline=0)
    if helm:
        f.paint(f.poly([(x - 9, y - 4), (x - 7, y - 11), (x + 2, y - 14), (x + 11, y - 9), (x + 12, y - 5), (x - 9, y - 2)]),
                IRON, mat="metal")
        for sx in (-4, 3):
            f.paint(f.poly([(x + sx - 2, y - 12), (x + sx - 5, y - 22), (x + sx + 2, y - 13)]), BONE, mat="bone", outline=0.7)
    elif hair == "topknot":
        f.paint(f.curve([(x + 2, y - 10), (x - 2, y - 18), (x - 10, y - 16), (x - 14, y - 8)], 3.2, 1.6), OHAIR, mat="fur")
        f.paint(f.ell(x + 1, y - 10, 4, 3), OHAIR, mat="fur", outline=0.6)
    elif hair == "mohawk":
        f.paint(f.curve([(x + 5, y - 10), (x, y - 16), (x - 8, y - 14)], 3.5, 2), OHAIR, mat="fur")


def spiked_pauldron(f, x, y, size=1.0, color=IRON, dark=1.0, spikes=3, trim=False):
    if trim:
        f.paint(f.ell(x, y + 1.5 * size, 14.5 * size, 9 * size), L_DARK, layer="l1", mat="cloth", dark=dark)
    f.paint(f.ell(x, y, 13 * size, 10 * size), color, mat="metal", dark=dark)
    f.paint(f.poly([(x - 12 * size, y + 2 * size), (x + 12 * size, y + 2 * size), (x + 11 * size, y + 5 * size),
                    (x - 11 * size, y + 5 * size)]), mix(color, (0, 0, 0), 0.25), mat="metal", outline=0.5, dark=dark)
    for i in range(spikes):
        t = (i - (spikes - 1) / 2) * 7 * size
        bx, by = x + t, y - 7 * size + abs(t) * 0.25
        f.paint(f.poly([(bx - 3 * size, by + 1), (bx - 2.5 * size + t * 0.3, by - 11 * size), (bx + 3 * size, by + 1)]),
                BONE, mat="bone", outline=0.7, dark=dark)


def orc_arm(f, sh, el, hand, skin=OSKIN, bracer=LEATHER, dark=1.0, r=9):
    f.paint(f.cap(sh, el, r, r * 0.85), skin, mat="skin", dark=dark)
    f.paint(f.cap(el, hand, r * 0.8, r * 0.7), skin, mat="skin", dark=dark)
    ex, ey = el
    hx, hy = hand
    m = f.cap((ex + (hx - ex) * 0.45, ey + (hy - ey) * 0.45), hand, r * 0.78, r * 0.72)
    f.paint(m, bracer, mat="leather", dark=dark, outline=0.6)


def fist(f, x, y, skin=OSKIN, r=6.5, dark=1.0):
    f.paint(f.ell(x, y, r, r * 0.9), skin, mat="skin", dark=dark)


# ----------------------------------------------------------------- human body
def human_legs(f, armor="plate", far=True, near=True):
    col = STEEL if armor == "plate" else (LEATHER if armor == "leather" else CLOTH_BROWN)
    mat = "metal" if armor == "plate" else ("leather" if armor == "leather" else "cloth")
    if far:
        f.paint(f.cap((-5, -30), (-8, -15), 7, 6), col, mat=mat, dark=0.78)
        f.paint(f.cap((-8, -15), (-9, -5), 6, 5.5), col if armor == "plate" else DLEATHER, mat=mat if armor == "plate" else "leather", dark=0.78)
        boot(f, -9, 0, STEEL if armor == "plate" else DLEATHER, 0.95, dark=0.78, mat="metal" if armor == "plate" else "leather")
    if near:
        f.paint(f.cap((5, -30), (7, -15), 7.5, 6.5), col, mat=mat)
        f.paint(f.cap((7, -15), (8, -5), 6.5, 6), col if armor == "plate" else DLEATHER, mat=mat if armor == "plate" else "leather")
        if armor == "plate":
            f.paint(f.ell(7, -16, 5, 4.5), STEEL, mat="metal", outline=0.6)
        boot(f, 9, 0, STEEL if armor == "plate" else DLEATHER, 1.05, mat="metal" if armor == "plate" else "leather")


def human_torso(f, armor="plate", tabard=True, cloth=CLOTH_TAN):
    col = STEEL if armor == "plate" else (LEATHER if armor == "leather" else cloth)
    mat = "metal" if armor == "plate" else ("leather" if armor == "leather" else "cloth")
    body = f.poly([(-14, -28), (12, -28), (16, -46), (18, -62), (6, -68), (-12, -67), (-17, -48)])
    f.paint(body, col, mat=mat)
    f.paint(f.c.intersect(body, f.poly([(-30, -36), (30, -36), (30, -30), (-30, -30)])), LEATHER, mat="leather")
    if tabard:
        f.paint(f.poly([(-9, -60), (11, -60), (13, -30), (14, -13), (-8, -13), (-10, -30)]), L_MAIN, layer="l2", mat="cloth")
        f.paint(f.poly([(-8, -17), (14, -17), (14, -13), (-8, -13)]), L_MAIN, layer="l1", mat="gold", outline=0.6)
    else:
        f.paint(f.ell(9, -33, 3, 3), GOLD, mat="gold", outline=0.6)


def round_pauldron(f, x, y, size=1.0, dark=1.0, trim=True, color=STEEL):
    if trim:
        f.paint(f.ell(x, y + 0.8, 13.5 * size, 9.5 * size), L_MAIN, layer="l1", mat="gold", dark=dark)
        f.paint(f.ell(x, y - 1.2 * size, 11.5 * size, 7.8 * size), color, mat="metal", dark=dark, outline=0.5)
    else:
        f.paint(f.ell(x, y, 12.5 * size, 9 * size), color, mat="metal", dark=dark)
    f.paint(f.ell(x - 3 * size, y - 3 * size, 3 * size, 2 * size), (255, 255, 255), mat="flat", outline=0, dark=0.9)


def human_head(f, x=4, y=-74, hat=None, beard=None, skin=HSKIN, hood=False, hair=(110, 70, 35)):
    f.paint(f.ell(x, y, 8.5, 9), skin, mat="skin")
    f.paint(f.ell(x + 7.5, y + 1, 2.2, 2.6), skin, mat="skin", outline=0.5)            # nose
    f.paint(f.ell(x + 4, y - 1.5, 1.1, 1.4), (40, 30, 30), mat="flat", outline=0)     # eye
    f.paint(f.poly([(x + 2, y - 4.5), (x + 7, y - 4.5), (x + 7, y - 3.5), (x + 2, y - 3.5)]), (90, 60, 40), mat="flat", outline=0)
    if beard:
        f.paint(f.poly([(x - 6, y + 1), (x + 8, y + 3), (x + 6, y + 10), (x - 1, y + 11), (x - 6, y + 6)]), beard, mat="fur")
        f.paint(f.ell(x + 4, y - 1.5, 1.1, 1.4), (40, 30, 30), mat="flat", outline=0)
    if hood:
        f.paint(f.poly([(x - 11, y + 8), (x - 12, y - 4), (x - 4, y - 12), (x + 6, y - 12), (x + 11, y - 6), (x + 5, y - 6),
                        (x - 2, y - 2), (x - 3, y + 9)]), L_MAIN, layer="l2", mat="cloth")
    elif hat == "kettle":
        f.paint(f.ell(x, y - 6, 13, 3), DSTEEL, mat="metal")
        f.paint(f.ell(x, y - 8, 8.5, 6), STEEL, mat="metal")
    elif hat == "hair":
        f.paint(f.poly([(x - 9, y + 2), (x - 9, y - 6), (x - 2, y - 10), (x + 7, y - 8), (x + 8, y - 5), (x, y - 6), (x - 4, y + 3)]),
                hair, mat="fur")
    elif hat == "cap":
        f.paint(f.poly([(x - 10, y - 2), (x - 6, y - 11), (x + 5, y - 11), (x + 13, y - 5), (x + 8, y - 4), (x - 9, y + 1)]),
                L_MAIN, layer="l2", mat="cloth")


def great_helm(f, x=4, y=-75, plume=True):
    if plume:
        f.paint(f.curve([(x - 1, y - 10), (x - 8, y - 18), (x - 18, y - 13), (x - 19, y - 2)], 3.6, 1.8), L_MAIN, layer="l2", mat="cloth")
    f.paint(f.poly([(x - 9, y + 8), (x - 10, y - 4), (x - 5, y - 11), (x + 5, y - 11), (x + 11, y - 5), (x + 12, y + 8)]), STEEL, mat="metal")
    f.paint(f.poly([(x - 9, y - 5), (x + 11, y - 5), (x + 11, y - 2), (x - 10, y - 2)]), L_MAIN, layer="l1", mat="gold", outline=0.5)
    f.paint(f.poly([(x + 3, y + 0.5), (x + 12, y + 0.5), (x + 12, y + 2.5), (x + 3, y + 2.5)]), (25, 22, 30), mat="flat", outline=0)
    f.paint(f.poly([(x + 6.5, y + 2.5), (x + 8.5, y + 2.5), (x + 8.5, y + 8), (x + 6.5, y + 8)]), DSTEEL, mat="metal", outline=0.4)


def kite_shield(f, x, y, size=1.0, emblem=True):
    s = size
    pts = [(x - 12 * s, y - 16 * s), (x + 12 * s, y - 16 * s), (x + 13 * s, y), (x, y + 22 * s), (x - 13 * s, y)]
    f.paint(f.poly(pts), L_MAIN, layer="l1", mat="gold")
    inner = [(x - 9.5 * s, y - 13.5 * s), (x + 9.5 * s, y - 13.5 * s), (x + 10.5 * s, y), (x, y + 18 * s), (x - 10.5 * s, y)]
    f.paint(f.poly(inner), L_MAIN, layer="l2", mat="cloth", outline=0.5, bevel=4)
    if emblem:   # a gold sun: disc with eight rays
        rays = []
        for i in range(16):
            a = i * math.pi / 8
            rr = (7.5 if i % 2 == 0 else 3.6) * s
            rays.append((x + math.cos(a) * rr, y - 2 * s + math.sin(a) * rr))
        f.paint(f.poly(rays), L_MAIN, layer="l1", mat="gold", outline=0.5)


def sword(f, hand, tip, width=2.6, guard=7):
    hx, hy = hand
    tx, ty = tip
    L = math.hypot(tx - hx, ty - hy)
    ux, uy = (tx - hx) / L, (ty - hy) / L
    nx, ny = -uy, ux
    gx, gy = hx + ux * 3, hy + uy * 3
    f.paint(f.poly([(gx + nx * width, gy + ny * width), (tx - ux * 5 + nx * width * 0.9, ty - uy * 5 + ny * width * 0.9), (tx, ty),
                    (tx - ux * 5 - nx * width * 0.9, ty - uy * 5 - ny * width * 0.9), (gx - nx * width, gy - ny * width)]), STEEL, mat="metal")
    f.paint(f.cap((gx + nx * guard, gy + ny * guard), (gx - nx * guard, gy - ny * guard), 1.6), GOLD, mat="gold", outline=0.6)
    f.paint(f.cap((hx - ux * 4, hy - uy * 4), (gx, gy), 1.6), DLEATHER, mat="leather", outline=0.5)
    f.paint(f.ell(hx - ux * 5, hy - uy * 5, 2.2, 2.2), GOLD, mat="gold", outline=0.5)


def frame(base, top):
    """Map (along, across) coordinates on a pole running base->top; across>0 is the
    pole's right-hand side when looking from base to top (the front for a right-facing figure)."""
    bx, by = base
    tx, ty = top
    L = math.hypot(tx - bx, ty - by)
    ux, uy = (tx - bx) / L, (ty - by) / L
    nx, ny = -uy, ux
    if nx < 0 or (nx == 0 and ny > 0):
        nx, ny = -nx, -ny
    return lambda a, c: (tx + ux * a + nx * c, ty + uy * a + ny * c)


def big_axe(f, hand_lo, top, blade=1.0, double=False):
    f.paint(f.cap(hand_lo, top, 2.3), WOOD, mat="wood")
    T = frame(hand_lo, top)
    b = blade
    def side(sg):
        return [T(1, 0), T(4 * b, 5 * b * sg), T(10 * b, 9 * b * sg), T(6 * b, 15 * b * sg), T(-4 * b, 18 * b * sg),
                T(-15 * b, 17 * b * sg), T(-24 * b, 12 * b * sg), T(-17 * b, 7 * b * sg), T(-13, 3 * sg), T(-12, 0)]
    f.paint(f.poly(side(1)), IRON, mat="metal", bevel=1.4)
    f.paint(f.poly([T(9 * b, 9.5 * b), T(6 * b, 15 * b), T(-4 * b, 18 * b), T(-15 * b, 17 * b), T(-24 * b, 12 * b),
                    T(-20 * b, 11.5 * b), T(-14 * b, 14 * b), T(-4 * b, 14.5 * b), T(4 * b, 12 * b), T(7 * b, 8.5 * b)]),
            STEEL, mat="metal", outline=0, bevel=1.0)
    # rivets
    for a in (-4, -9):
        f.paint(f.ell(*T(a * b, 5 * b), 1.0, 1.0), BONE, mat="metal", outline=0.4)
    if double:
        f.paint(f.poly(side(-1)), IRON, mat="metal", dark=0.85, bevel=1.4)
    else:
        f.paint(f.poly([T(-3, 0), T(-6, -9 * b), T(-10, 0)]), IRON, mat="metal", outline=0.7)
    f.paint(f.poly([T(8 * b, -1.6), T(1, 0), T(8 * b, 1.6)]), IRON, mat="metal", outline=0.7)
    f.paint(f.cap(T(-12, 0), T(-15, 0), 3), DLEATHER, mat="leather", outline=0.5)


# ================================================================== units
def grunt(c, fx, fy, u=1.0):
    f = Fig(c, fx, fy, u)
    shadow(f, 26)
    big_axe(f, (-23, -18), (-19, -100), 1.2)
    orc_legs(f, near=False)
    orc_arm(f, (-16, -62), (-25, -48), (-22, -36), dark=0.75)
    fist(f, -22, -33, dark=0.75)
    orc_torso(f, loin=False)
    orc_legs(f, far=False)
    loincloth(f)
    spiked_pauldron(f, -13, -70, 0.75, dark=0.8, spikes=2)
    spiked_pauldron(f, 0, -66, 1.0, spikes=3, trim=True)
    orc_arm(f, (6, -58), (12, -44), (22, -34))
    orc_head(f, 19, -66)
    fist(f, 25, -31)


def footman(c, fx, fy, u=1.0):
    f = Fig(c, fx, fy, u)
    shadow(f, 22)
    human_legs(f, near=False)
    # sword arm, raised behind the body
    f.paint(f.cap((-8, -62), (-19, -68), 6.5, 6), STEEL, mat="metal", dark=0.8)
    f.paint(f.cap((-19, -68), (-16, -80), 6, 5.5), STEEL, mat="metal", dark=0.8)
    sword(f, (-15, -83), (8, -106), 2.8, 6.5)
    f.paint(f.ell(-15, -82, 4.8, 4.8), DLEATHER, mat="leather", dark=0.85)
    human_torso(f)
    human_legs(f, far=False)
    round_pauldron(f, 1, -62, 1.0)
    great_helm(f, 4, -76)
    kite_shield(f, 15, -44, 1.0)


# ================================================================== more props
def pole(f, a, b, r=1.6, color=WOOD):
    f.paint(f.cap(a, b, r), color, mat="wood")


def spear(f, base, top, r=1.5, feathers=False):
    pole(f, base, top, r)
    T = frame(base, top)
    f.paint(f.poly([T(9, 0), T(-1, 3.2), T(-5, 0), T(-1, -3.2)]), STEEL, mat="metal", bevel=1.2)
    if feathers:
        for k, c in ((0, (200, 60, 40)), (1, (230, 220, 200))):
            f.paint(f.curve([T(-7, 0), T(-10, 5 + k * 2), T(-16, 6 + k * 3)], 1.4, 0.6), c, mat="cloth", outline=0.5)
        f.paint(f.cap(T(-5, 0), T(-8, 0), 2.2), DLEATHER, mat="leather", outline=0.5)


def pickaxe(f, base, top, r=1.6):
    pole(f, base, top, r)
    T = frame(base, top)
    f.paint(f.curve([T(-2, -12), T(3, 0), T(-2, 12)], 2.4, 1.0), IRON, mat="metal", bevel=1.2)


def round_shield(f, x, y, r, rim=IRON, face_layer="l2", boss=True, dark=1.0, wood=False):
    f.paint(f.ell(x, y, r, r * 1.05), rim, mat="metal", dark=dark)
    if wood:
        f.paint(f.ell(x, y, r * 0.82, r * 0.87), WOOD, mat="wood", outline=0.5, dark=dark)
        f.paint(f.ell(x, y, r * 0.5, r * 0.53), L_MAIN, layer=face_layer, mat="cloth", outline=0.4, dark=dark)
    else:
        f.paint(f.ell(x, y, r * 0.82, r * 0.87), L_MAIN, layer=face_layer, mat="cloth", outline=0.5, dark=dark)
    if boss:
        f.paint(f.ell(x, y, r * 0.28, r * 0.3), STEEL if rim != IRON else IRON, mat="metal", outline=0.5, dark=dark)


def hide_shield(f, x, y, r, dark=1.0):
    """An orc shield: hide stretched on a wooden frame, painted with the clan colour."""
    f.paint(f.ell(x, y, r, r * 1.08), CLOTH_TAN, mat="leather", dark=dark)
    f.paint(f.poly([(x - r * 0.7, y - r * 0.15), (x + r * 0.7, y - r * 0.15), (x + r * 0.45, y + r * 0.35), (x - r * 0.45, y + r * 0.35)]),
            L_MAIN, layer="l2", mat="cloth", outline=0.4, dark=dark)
    for a in range(0, 360, 45):
        t = math.radians(a)
        f.paint(f.ell(x + math.cos(t) * r * 0.9, y + math.sin(t) * r * 0.95, 1.1, 1.1), DLEATHER, mat="leather", outline=0.3, dark=dark)
    f.paint(f.cap((x - r * 0.9, y + r * 0.2), (x + r * 0.9, y - r * 0.2), 1.4), WOOD, mat="wood", outline=0.4, dark=dark)


def bow(f, grip, top, bottom, string_to=None):
    f.paint(f.curve([top, (grip[0] + 9, grip[1] - 8), grip], 1.9, 2.3), WOOD, mat="wood")
    f.paint(f.curve([grip, (grip[0] + 9, grip[1] + 8), bottom], 2.3, 1.9), WOOD, mat="wood")
    sx, sy = string_to if string_to else ((top[0] + bottom[0]) / 2, (top[1] + bottom[1]) / 2)
    for end in (top, bottom):
        f.paint(f.cap(end, (sx, sy), 0.45), (235, 230, 215), mat="flat", outline=0)


def quiver(f, x, y, dark=0.85):
    for i, dx in enumerate((-2, 1, 4)):
        f.paint(f.cap((x + dx, y - 14), (x + dx - 1, y - 20), 1.3), (220, 70, 50) if i != 1 else (240, 235, 220), mat="cloth", outline=0.4, dark=dark)
    f.paint(f.cap((x, y), (x + 2, y - 14), 4.2, 4.4), LEATHER, mat="leather", dark=dark)


def staff_orb(f, base, top, glow_col, orb_col, r=1.8):
    pole(f, base, top, r)
    tx, ty = top
    f.paint(f.curve([(tx - 4, ty + 2), (tx - 5, ty - 6), (tx, ty - 9), (tx + 5, ty - 6), (tx + 4, ty + 2)], 1.4), WOOD, mat="wood", outline=0.6)
    orb = f.ell(tx, ty - 4, 3.6, 3.6)
    f.c.glow(orb, glow_col, radius=4, strength=0.7)
    f.paint(orb, orb_col, mat="skin", outline=0.5)
    f.paint(f.ell(tx - 1.2, ty - 5.4, 1.2, 1.0), (255, 255, 255), mat="flat", outline=0)


def bedroll_pack(f, x, y, dark=0.9):
    f.paint(f.poly([(x - 8, y - 2), (x + 6, y - 4), (x + 7, y + 16), (x - 9, y + 17)]), CLOTH_BROWN, mat="leather", dark=dark)
    f.paint(f.cap((x - 10, y - 5), (x + 8, y - 7), 4.2), L_MAIN, layer="l2", mat="cloth", dark=dark)
    f.paint(f.cap((x - 10, y + 2), (x + 8, y + 2), 1.0), DLEATHER, mat="leather", outline=0.3, dark=dark)


# ================================================================== humans
def human_arm(f, sh, el, hand, col=STEEL, mat="metal", glove=None, dark=1.0, r=6.5):
    f.paint(f.cap(sh, el, r, r * 0.9), col, mat=mat, dark=dark)
    f.paint(f.cap(el, hand, r * 0.9, r * 0.8), col, mat=mat, dark=dark)
    hx, hy = hand
    f.paint(f.ell(hx, hy, r * 0.85, r * 0.85), glove or (STEEL if mat == "metal" else HSKIN),
            mat="metal" if (glove is None and mat == "metal") else "skin", dark=dark)


def robe(f, col=L_MAIN, layer="l2", hem_layer="l1", hem_col=L_MAIN, hem_mat="gold", sash=True,
         sh=13, waist=10, flare=17, top=-66, waist_y=-40, hem_y=-1, folds=True, bulk=1.0):
    """A robe with shape: broad shoulders tapering to a cinched waist, then a skirt that
    flares out to a curved hem (longer at the front), with painted folds and feet peeking out."""
    sh, waist, flare = sh * bulk, waist * bulk, flare * bulk
    # feet under the hem
    boot(f, -8, 0, DLEATHER, 0.8, dark=0.8)
    boot(f, 7, 0, DLEATHER, 0.85)
    skirt_pts = [(-waist, waist_y), (waist + 2, waist_y), (flare * 0.75, -20), (flare + 2, hem_y - 2), (flare - 2, hem_y + 1),
                 (6, hem_y + 1.5), (-4, hem_y + 0.5), (-flare + 2, hem_y - 1.5), (-flare - 1, hem_y - 4), (-flare * 0.72, -22)]
    skirt = f.poly(skirt_pts)
    f.paint(skirt, col, layer=layer, mat="cloth")
    if folds:
        fold = mix(col, (0, 0, 0), 0.38) if layer == "base" else grey(0.55)
        for x0, x1 in ((-3, -9), (3, 3), (8, 13)):
            f.paint(f.c.intersect(skirt, f.curve([(x0, waist_y + 4), (x0 + (x1 - x0) * 0.4, -20), (x1, hem_y - 4)], 0.75, 1.1)),
                    fold, layer=layer, mat="flat", outline=0)
    if hem_layer:
        band = f.c.subtract(skirt, f.poly([(p[0], p[1] - 4.5) if p[1] > -10 else p for p in skirt_pts]))
        f.paint(band, hem_col, layer=hem_layer, mat=hem_mat, outline=0.5)
    chest = f.poly([(-sh, top), (sh + 2, top), (sh + 3, top + 10), (waist + 2, waist_y), (-waist, waist_y), (-sh - 1, top + 10)])
    f.paint(chest, col, layer=layer, mat="cloth")
    if sash:
        f.paint(f.poly([(-waist - 1, waist_y - 3), (waist + 3, waist_y - 3), (waist + 3.5, waist_y + 2.5), (-waist - 1.5, waist_y + 2.5)]),
                hem_col, layer=hem_layer or "base", mat=hem_mat if hem_layer else "leather", outline=0.6)
    return f.c.union(skirt, chest)


def sleeve_arm(f, sh, el, hand, col=L_MAIN, layer="l2", skin=HSKIN, dark=1.0, r=6, cuff=(L_MAIN, "l1", "gold")):
    """A robed arm: a sleeve that widens into a bell at the wrist, with a bare hand."""
    f.paint(f.cap(sh, el, r, r * 0.95), col, layer=layer, mat="cloth", dark=dark)
    ex, ey = el
    hx, hy = hand
    L = math.hypot(hx - ex, hy - ey) or 1
    ux, uy = (hx - ex) / L, (hy - ey) / L
    nx, ny = -uy, ux
    wx, wy = hx - ux * 3.5, hy - uy * 3.5          # wrist
    bell = [(ex + nx * r * 0.9, ey + ny * r * 0.9), (wx + nx * r * 1.25, wy + ny * r * 1.25),
            (wx - nx * r * 1.25, wy - ny * r * 1.25), (ex - nx * r * 0.9, ey - ny * r * 0.9)]
    f.paint(f.poly(bell), col, layer=layer, mat="cloth", dark=dark)
    if cuff:
        c1, l1, m1 = cuff
        f.paint(f.poly([(wx + nx * r * 1.25, wy + ny * r * 1.25), (wx - nx * r * 1.25, wy - ny * r * 1.25),
                        (wx - nx * r * 1.2 - ux * 2, wy - ny * r * 1.2 - uy * 2), (wx + nx * r * 1.2 - ux * 2, wy + ny * r * 1.2 - uy * 2)]),
                c1, layer=l1, mat=m1, outline=0.5, dark=dark)
    f.paint(f.ell(hx, hy, r * 0.75, r * 0.75), skin, mat="skin", dark=dark)


def peasant(c, fx, fy, u=1.0):
    f = Fig(c, fx, fy, u)
    shadow(f, 18)
    human_legs(f, "cloth", near=False)
    human_arm(f, (-8, -60), (-14, -46), (-8, -38), CLOTH_TAN, "cloth", HSKIN, dark=0.8)
    # belted tunic that flares into a short skirt over the thighs
    tunic = f.poly([(-13, -66), (12, -66), (15, -56), (12, -40), (15, -24), (6, -22), (-6, -23), (-16, -26), (-12, -40), (-15, -56)])
    f.paint(tunic, CLOTH_TAN, mat="cloth")
    for x0, x1 in ((-4, -8), (5, 9)):
        f.paint(f.c.intersect(tunic, f.curve([(x0, -38), (x1, -24)], 0.6, 0.9)), mix(CLOTH_TAN, (0, 0, 0), 0.35), mat="flat", outline=0)
    f.paint(f.poly([(-13, -42), (13, -42), (13, -37), (-13, -37)]), LEATHER, mat="leather", outline=0.6)   # belt
    f.paint(f.poly([(-4, -66), (6, -66), (3, -58)]), mix(CLOTH_TAN, (0, 0, 0), 0.25), mat="cloth", outline=0.5)   # open collar
    human_legs(f, "cloth", far=False)
    human_head(f, 5, -75, hat="hair")
    pickaxe(f, (16, -24), (-4, -96))
    human_arm(f, (4, -60), (13, -50), (9, -50), CLOTH_TAN, "cloth", HSKIN)


def militia(c, fx, fy, u=1.0):
    f = Fig(c, fx, fy, u)
    shadow(f, 21)
    human_legs(f, "cloth", near=False)
    round_shield(f, -14, -50, 13, rim=IRON, wood=True, dark=0.8)
    human_torso(f, "cloth", tabard=True, cloth=CLOTH_TAN)
    # quilted gambeson lines
    for y in (-52, -44):
        f.paint(f.curve([(-12, y), (2, y + 1), (15, y)], 0.6), (150, 120, 80), mat="flat", outline=0)
    human_legs(f, "cloth", far=False)
    human_head(f, 5, -75, hat="kettle", beard=(120, 75, 40))
    human_arm(f, (4, -60), (10, -46), (20, -42), CLOTH_TAN, "cloth", HSKIN)
    # a stout mace
    pole(f, (17, -36), (26, -68), 1.8)
    f.paint(f.ell(26.5, -70, 5, 5.5), IRON, mat="metal")
    for dx, dy in ((5, 0), (-5, 0), (0, -6), (3.5, -4), (-3.5, -4)):
        f.paint(f.poly([(26.5 + dx * 0.7 - 1.3, -70 + dy * 0.7), (26.5 + dx * 1.45, -70 + dy * 1.45), (26.5 + dx * 0.7 + 1.3, -70 + dy * 0.7 - 1)]),
                IRON, mat="metal", outline=0.4)
    f.paint(f.ell(20, -42, 5.2, 5.2), HSKIN, mat="skin")


def archer(c, fx, fy, u=1.0):
    f = Fig(c, fx, fy, u)
    shadow(f, 20)
    quiver(f, -12, -46)
    human_legs(f, "leather", near=False)
    human_arm(f, (-6, -60), (6, -58), (16, -60), LEATHER, "leather", HSKIN, dark=0.8)   # draw arm
    human_torso(f, "leather", tabard=False)
    f.paint(f.poly([(-13, -64), (12, -64), (6, -54), (-4, -50), (-15, -54)]), L_MAIN, layer="l2", mat="cloth")   # short cape
    human_legs(f, "leather", far=False)
    human_head(f, 5, -75, hood=True)
    bow(f, (30, -60), (22, -92), (22, -28), string_to=(14, -60))
    human_arm(f, (4, -62), (18, -61), (30, -60), LEATHER, "leather", HSKIN)


def spearman(c, fx, fy, u=1.0):
    f = Fig(c, fx, fy, u)
    shadow(f, 21)
    human_legs(f, near=False)
    round_shield(f, -15, -50, 13, rim=STEEL, dark=0.8)
    human_torso(f)
    human_legs(f, far=False)
    round_pauldron(f, 1, -62, 0.9)
    human_head(f, 5, -75, hat="kettle")
    spear(f, (24, -4), (24, -104), 1.6)
    human_arm(f, (4, -58), (12, -46), (24, -50))


def fireball(f, x, y, r=5.0):
    core = f.ell(x, y, r, r)
    f.c.glow(core, (255, 130, 40), radius=r * 0.9, strength=0.85)
    # flame licks trailing upward
    for dx, h in ((-2.5, 1.6), (0, 2.2), (2.5, 1.5)):
        f.paint(f.poly([(x + dx - r * 0.45, y - r * 0.4), (x + dx * 1.3, y - r * h), (x + dx + r * 0.45, y - r * 0.4)]),
                (255, 150, 50), mat="glow", outline=0)
    f.paint(core, (255, 175, 60), mat="glow", outline=0)
    f.paint(f.ell(x - r * 0.15, y + r * 0.05, r * 0.62, r * 0.62), (255, 225, 120), mat="glow", outline=0)
    f.paint(f.ell(x - r * 0.25, y - r * 0.05, r * 0.3, r * 0.3), (255, 252, 225), mat="glow", outline=0)


def mage(c, fx, fy, u=1.0):
    """Battle mage hurling fire from both hands: no staff, long beard."""
    f = Fig(c, fx, fy, u)
    shadow(f, 20)
    # far arm flung back and up, a fireball in that hand
    sleeve_arm(f, (-6, -61), (-16, -66), (-22, -78), dark=0.8)
    fireball(f, -23, -84, 4.6)
    robe(f)
    # mantle over the shoulders
    f.paint(f.poly([(-15, -67), (15, -67), (19, -58), (12, -54), (0, -55), (-12, -53), (-17, -58)]), L_MAIN, layer="l2", mat="cloth", dark=0.88)
    f.paint(f.poly([(-15, -69), (14, -69), (15, -65), (-16, -65)]), L_MAIN, layer="l1", mat="gold", outline=0.5)   # gold collar
    human_head(f, 5, -76, hat="hair", hair=(205, 205, 212))
    # near arm thrust forward (behind the beard), the second fireball
    sleeve_arm(f, (6, -58), (15, -48), (25, -52))
    # long forked white beard over the chest
    beard = (232, 232, 238)
    f.paint(f.poly([(-3, -74), (12, -73), (12, -66), (9, -56), (7, -50), (5, -55), (3, -49), (0, -57), (-3, -66)]), beard, mat="fur")
    f.paint(f.poly([(4, -72), (12, -72), (12, -70), (4, -70)]), mix(beard, (0, 0, 0), 0.15), mat="fur", outline=0.4)   # moustache
    f.paint(f.ell(9, -77.5, 1.1, 1.4), (40, 30, 30), mat="flat", outline=0)
    f.paint(f.poly([(6, -81), (12, -81), (12, -80), (6, -79.5)]), (230, 230, 235), mat="flat", outline=0)   # white brow
    fireball(f, 29, -56, 5.4)


def priest(c, fx, fy, u=1.0):
    f = Fig(c, fx, fy, u)
    shadow(f, 19)
    white = (240, 235, 222)
    sleeve_arm(f, (-6, -60), (-12, -48), (-8, -40), white, "base", dark=0.8)
    m = robe(f, col=white, layer="base", hem_layer="l1")
    # stole hanging from the neck in the faction colour
    f.paint(f.c.intersect(m, f.poly([(1, -66), (8, -66), (10, -6), (3, -6)])), L_MAIN, layer="l2", mat="cloth", outline=0.4)
    f.paint(f.poly([(-14, -68), (14, -68), (16, -61), (-15, -60)]), L_MAIN, layer="l1", mat="gold", outline=0.5)   # gold collar
    human_head(f, 5, -76, hat="hair")
    # book held to the chest
    f.paint(f.poly([(5, -54), (16, -56), (17, -44), (6, -42)]), (125, 40, 35), mat="leather")
    f.paint(f.poly([(8, -52), (14, -53), (14.5, -49), (8.5, -48)]), GOLD, mat="gold", outline=0.3)
    # raised hand with the Light
    sleeve_arm(f, (5, -61), (15, -58), (22, -68), white, "base")
    light = f.ell(23, -74, 4, 4)
    f.c.glow(light, (255, 225, 120), radius=5, strength=0.85)
    f.paint(light, (255, 245, 190), mat="glow", outline=0)


def settler_h(c, fx, fy, u=1.0):
    f = Fig(c, fx, fy, u)
    shadow(f, 19)
    bedroll_pack(f, -12, -64)
    human_legs(f, "cloth", near=False)
    human_torso(f, "cloth", tabard=False, cloth=CLOTH_BROWN)
    f.paint(f.poly([(-13, -66), (12, -66), (14, -24), (-15, -26)]), L_MAIN, layer="l2", mat="cloth")   # travel cloak
    human_legs(f, "cloth", far=False)
    human_head(f, 5, -75, hat="hair", beard=(110, 70, 35))
    pole(f, (22, 0), (20, -84), 1.8)
    human_arm(f, (4, -60), (12, -48), (21, -50), CLOTH_BROWN, "cloth", HSKIN)


# ----------------------------------------------------------------- horse & paladin
def horse(f, coat=(235, 232, 225), barding=True):
    # far legs
    for (a, b, c2) in (((16, -32), (14, -16), (16, -3)), ((-20, -32), (-25, -17), (-23, -3))):
        f.paint(f.cap(a, b, 5.5, 4.2), coat, mat="skin", dark=0.75)
        f.paint(f.cap(b, c2, 4.2, 3.6), coat, mat="skin", dark=0.75)
        f.paint(f.ell(c2[0] + 1, -1.5, 4, 2.5), (60, 50, 45), mat="leather", dark=0.75)
    f.paint(f.curve([(-31, -44), (-42, -40), (-42, -18)], 4, 2.5), (200, 195, 185), mat="fur")    # tail
    f.paint(f.ell(-18, -40, 15, 13), coat, mat="skin")
    f.paint(f.ell(0, -40, 24, 12), coat, mat="skin")
    f.paint(f.ell(19, -42, 13, 13), coat, mat="skin")
    f.paint(f.poly([(10, -46), (24, -78), (36, -78), (31, -46)]), coat, mat="skin")      # neck
    f.paint(f.poly([(24, -82), (34, -86), (50, -68), (48, -62), (40, -62), (27, -72)]), coat, mat="skin")   # head
    f.paint(f.poly([(27, -84), (29, -93), (32, -84)]), coat, mat="skin", outline=0.6)   # ear
    f.paint(f.curve([(26, -84), (14, -66), (10, -50)], 3.5, 2.5), (200, 195, 185), mat="fur")   # mane
    for (a, b, c2) in (((22, -32), (24, -16), (24, -3)), ((-16, -32), (-20, -17), (-17, -3))):
        f.paint(f.cap(a, b, 6, 4.5), coat, mat="skin")
        f.paint(f.cap(b, c2, 4.5, 3.8), coat, mat="skin")
        f.paint(f.ell(c2[0] + 1, -1.5, 4.3, 2.7), (60, 50, 45), mat="leather")
    if barding:
        cap_m = f.poly([(-32, -50), (24, -52), (30, -40), (28, -22), (-32, -22), (-34, -40)])
        f.paint(cap_m, L_MAIN, layer="l2", mat="cloth")
        f.paint(f.c.intersect(cap_m, f.poly([(-40, -27), (40, -27), (40, -20), (-40, -20)])), L_MAIN, layer="l1", mat="gold", outline=0.5)
        # chanfron plate on the head
        f.paint(f.poly([(27, -82), (33, -85), (47, -68), (43, -66), (30, -74)]), STEEL, mat="metal", outline=0.6)
        f.paint(f.poly([(14, -74), (28, -78), (34, -50), (18, -48)]), STEEL, mat="metal", outline=0.6)   # crinet
    f.paint(f.ell(37, -75, 1.3, 1.3), (25, 20, 20), mat="flat", outline=0)


def paladin(c, fx, fy, u=1.0):
    f = Fig(c, fx - 4, fy, u * 1.06)
    shadow(f, 34)
    horse(f)
    # rider seated at (-2, -52)
    r = Fig(c, *f.p(-4, -22), u * 0.88)   # rider's hips (y=-30 in rider coordinates) sit on the saddle
    # hammer arm, raised behind
    r.paint(r.cap((-8, -62 + 20), (-18, -70 + 20), 6.5, 6), STEEL, mat="metal", dark=0.8)
    r.paint(r.cap((-18, -50), (-14, -62), 6, 5.5), STEEL, mat="metal", dark=0.8)
    pole(r, (-12, -58), (4, -90), 2.0)
    hh = r.poly([(-6, -96), (6, -82), (15, -90), (3, -104)])
    r.c.glow(hh, (255, 230, 140), radius=4, strength=0.7)
    r.paint(hh, (245, 240, 225), mat="metal", bevel=2, outline=0.9)
    r.paint(r.poly([(-2, -93), (7, -83), (9, -85), (0, -95)]), GOLD, mat="gold", outline=0.4)
    r.paint(r.ell(-13, -61, 4.8, 4.8), STEEL, mat="metal", dark=0.85)
    human_torso(r)
    # near leg, seated: thigh forward, shin down
    r.paint(r.cap((2, -30), (14, -26), 7.5, 7), STEEL, mat="metal")
    r.paint(r.cap((14, -26), (13, -12), 6.5, 6), STEEL, mat="metal")
    boot(r, 13, -6, STEEL, 0.95, mat="metal")
    round_pauldron(r, 1, -62, 1.05)
    great_helm(r, 4, -76, plume=True)
    kite_shield(r, 16, -44, 0.95)


# ================================================================== orcs
def peon(c, fx, fy, u=1.0):
    f = Fig(c, fx, fy, u * 0.88)
    shadow(f, 20)
    orc_legs(f, near=False, pants=CLOTH_BROWN)
    orc_arm(f, (-16, -62), (-22, -48), (-15, -40), dark=0.75)
    fist(f, -15, -38, dark=0.75)
    orc_torso(f, loin=False, belt=False)
    # rope belt and a ragged sackcloth wrap over one shoulder
    f.paint(f.poly([(-18, -64), (-8, -74), (10, -40), (0, -38)]), CLOTH_TAN, mat="cloth", outline=0.6)
    f.paint(f.poly([(-18, -38), (17, -38), (18, -33), (-18, -33)]), (170, 140, 90), mat="cloth", outline=0.6)
    orc_legs(f, far=False, pants=CLOTH_BROWN, wraps=False)
    loincloth(f)
    pickaxe(f, (28, -22), (6, -96))
    orc_arm(f, (4, -55), (12, -42), (21, -48))
    orc_head(f, 18, -67, hair="mohawk", eye=(255, 200, 60))
    fist(f, 21, -48)


def militia_o(c, fx, fy, u=1.0):
    f = Fig(c, fx, fy, u * 0.95)
    shadow(f, 24)
    orc_legs(f, near=False)
    orc_arm(f, (-16, -62), (-24, -48), (-20, -36), dark=0.75)
    fist(f, -20, -34, dark=0.75)
    orc_torso(f, loin=False)
    # hide vest
    f.paint(f.poly([(-20, -66), (-6, -74), (6, -60), (2, -40), (-20, -42)]), (140, 105, 70), mat="fur", outline=0.6)
    orc_legs(f, far=False)
    loincloth(f)
    f.paint(f.ell(-10, -70, 11, 7), (140, 105, 70), mat="fur")   # fur mantle
    # spiked club
    f.paint(f.cap((22, -32), (32, -78), 2.6, 5.5), WOOD, mat="wood")
    for t in (0.55, 0.7, 0.85):
        x, y = 22 + 10 * t, -32 - 46 * t
        f.paint(f.poly([(x + 3, y - 1), (x + 9, y - 3), (x + 3, y + 2)]), IRON, mat="metal", outline=0.5)
        f.paint(f.poly([(x - 3, y), (x - 8, y - 4), (x - 2, y + 3)]), IRON, mat="metal", outline=0.5)
    orc_arm(f, (4, -55), (12, -46), (22, -38))
    orc_head(f, 18, -67, hair="topknot")
    fist(f, 23, -36)


def archer_o(c, fx, fy, u=1.0):
    f = Fig(c, fx, fy, u * 0.95)
    shadow(f, 23)
    quiver(f, -16, -48)
    orc_legs(f, near=False)
    orc_arm(f, (-14, -64), (2, -62), (12, -64), dark=0.75)
    orc_torso(f, loin=False)
    orc_legs(f, far=False)
    loincloth(f)
    spiked_pauldron(f, -2, -68, 0.7, spikes=0, color=LEATHER)
    f.paint(f.poly([(9, -78), (27, -77), (27, -74), (9, -75)]), L_MAIN, layer="l2", mat="cloth", outline=0.5)   # headband
    bow(f, (34, -62), (26, -98), (26, -26), string_to=(12, -64))
    orc_arm(f, (4, -55), (20, -63), (32, -62))
    orc_head(f, 18, -68, hair="topknot")
    fist(f, 33, -62, r=5.5)


def spearman_o(c, fx, fy, u=1.0):
    f = Fig(c, fx, fy, u * 0.95)
    shadow(f, 24)
    orc_legs(f, near=False)
    hide_shield(f, -18, -50, 14, dark=0.8)
    orc_torso(f, loin=False)
    orc_legs(f, far=False)
    loincloth(f)
    spiked_pauldron(f, -1, -67, 0.85, spikes=2)
    spear(f, (28, -2), (28, -108), 1.7, feathers=True)
    orc_arm(f, (4, -55), (14, -46), (27, -48))
    orc_head(f, 18, -67, hair="topknot")
    fist(f, 28, -48)


def shaman(c, fx, fy, u=1.0):
    f = Fig(c, fx, fy, u * 0.92)
    shadow(f, 21)
    # far arm, crackling with lightning
    sleeve_arm(f, (-14, -62), (-22, -50), (-18, -40), skin=OSKIN, dark=0.75, r=7.5, cuff=(L_DARK, "l1", "cloth"))
    bolt = f.curve([(-20, -38), (-26, -46), (-21, -52), (-28, -60)], 1.2, 0.5)
    f.c.glow(bolt, (120, 220, 255), radius=3, strength=0.8)
    f.paint(bolt, (220, 245, 255), mat="glow", outline=0)
    robe(f, hem_layer="l1", hem_col=L_DARK, hem_mat="cloth", bulk=1.25, top=-68, waist_y=-38, sash=False)
    f.paint(f.poly([(-14, -41), (16, -41), (17, -35), (-14, -35)]), LEATHER, mat="leather", outline=0.6)   # leather belt
    f.paint(f.ell(9, -38, 3.2, 3.2), BONE, mat="bone", outline=0.5)                                       # bone buckle
    # wolf-pelt mantle with ragged edge
    pelt = (122, 92, 62)
    f.paint(f.ell(-4, -64, 17, 8), pelt, mat="fur")
    for x in (-17, -11, -5, 1, 7):
        f.paint(f.poly([(x - 3, -59), (x, -51), (x + 3, -59)]), pelt, mat="fur", outline=0.5, dark=0.9)
    # totem staff in the near hand: horned skull and feathers
    pole(f, (30, -2), (28, -100), 2.0)
    for k, col in enumerate(((220, 70, 50), (240, 235, 220), (220, 70, 50))):
        f.paint(f.curve([(28, -88 + k * 4), (36, -84 + k * 4), (39, -76 + k * 4)], 1.5, 0.6), col, mat="cloth", outline=0.4)
    f.paint(f.ell(28, -100, 5, 5.5), BONE, mat="bone")
    f.paint(f.poly([(25, -97), (31, -97), (30, -92), (26, -92)]), BONE, mat="bone", outline=0.5)
    for ex in (26, 30):
        f.paint(f.ell(ex, -100, 1.2, 1.4), (30, 20, 20), mat="flat", outline=0)
    for sg in (-1, 1):
        f.paint(f.curve([(28 + 4 * sg, -103), (28 + 10 * sg, -106), (28 + 11 * sg, -112)], 1.6, 0.6), BONE, mat="bone", outline=0.5)
    sleeve_arm(f, (4, -57), (14, -46), (27, -48), skin=OSKIN, r=7.5, cuff=(L_DARK, "l1", "cloth"))
    orc_head(f, 17, -68, hair=None, eye=(120, 230, 255))
    for k, col in enumerate(((240, 235, 220), (200, 60, 40), (240, 235, 220))):
        f.paint(f.curve([(12 - k * 2, -78), (8 - k * 3, -84), (3 - k * 3, -85)], 1.4, 0.6), col, mat="cloth", outline=0.5)
    f.paint(f.poly([(7, -81), (24, -80), (24, -77), (7, -77)]), BONE, mat="bone", outline=0.5)
    fist(f, 28, -48, r=6)


def settler_o(c, fx, fy, u=1.0):
    f = Fig(c, fx, fy, u * 0.9)
    shadow(f, 21)
    bedroll_pack(f, -18, -66)
    orc_legs(f, near=False)
    orc_torso(f, loin=False)
    f.paint(f.poly([(-20, -68), (16, -72), (22, -50), (18, -26), (-22, -28)]), L_MAIN, layer="l2", mat="cloth")   # travel cloak
    orc_legs(f, far=False)
    pole(f, (30, 0), (27, -92), 2.0)
    orc_arm(f, (4, -55), (14, -48), (27, -52))
    orc_head(f, 18, -68, hair="topknot")
    fist(f, 27, -52)


# ----------------------------------------------------------------- wolf & wolf rider
def wolf(f, fur=(92, 84, 78), belly=(150, 140, 128)):
    dark = mix(fur, (0, 0, 0), 0.3)
    for (a, b, c2) in (((18, -26), (18, -12), (20, -3)), ((-20, -26), (-26, -14), (-22, -3))):
        f.paint(f.cap(a, b, 6, 4.5), fur, mat="fur", dark=0.72)
        f.paint(f.cap(b, c2, 4.5, 4), fur, mat="fur", dark=0.72)
        f.paint(f.ell(c2[0] + 2, -2, 5, 2.8), dark, mat="fur", dark=0.72)
    f.paint(f.curve([(-28, -36), (-44, -38), (-50, -24)], 6, 2.5), fur, mat="fur")    # bushy tail
    f.paint(f.ell(-16, -32, 15, 12), fur, mat="fur")
    f.paint(f.ell(2, -34, 22, 12), fur, mat="fur")
    f.paint(f.ell(18, -40, 16, 15), fur, mat="fur")             # big shaggy shoulders
    # ruff of fur on the neck
    f.paint(f.poly([(14, -56), (36, -52), (38, -32), (26, -24), (14, -30)]), mix(fur, belly, 0.4), mat="fur")
    # head: skull, long snout, open jaws
    f.paint(f.ell(36, -48, 10, 9), fur, mat="fur")
    f.paint(f.poly([(38, -54), (54, -46), (54, -41), (40, -40)]), fur, mat="fur")          # upper snout
    f.paint(f.poly([(38, -40), (51, -38), (50, -34), (38, -34)]), dark, mat="fur")         # lower jaw
    for x in (42, 45.5, 49):
        f.paint(f.poly([(x, -41), (x + 1, -38), (x + 2, -41)]), BONE, mat="bone", outline=0.3)
    f.paint(f.ell(54, -45, 2, 1.8), (25, 20, 20), mat="skin", outline=0.3)                  # nose
    for ex in (28, 33):
        f.paint(f.poly([(ex, -54), (ex - 2, -66), (ex + 5, -56)]), fur, mat="fur", outline=0.6, dark=0.9)
    e = f.ell(41, -50, 1.6, 1.1)
    f.c.glow(e, (255, 210, 60), radius=1.5, strength=0.5)
    f.paint(e, (255, 220, 80), mat="glow", outline=0)
    for (a, b, c2) in (((24, -26), (25, -12), (27, -3)), ((-14, -26), (-19, -14), (-15, -3))):
        f.paint(f.cap(a, b, 6.5, 5), fur, mat="fur")
        f.paint(f.cap(b, c2, 5, 4.2), fur, mat="fur")
        f.paint(f.ell(c2[0] + 2, -2, 5.5, 3), dark, mat="fur")
    # saddle blanket in the clan colour
    sm = f.poly([(-14, -46), (14, -48), (16, -30), (-14, -28)])
    f.paint(sm, L_MAIN, layer="l2", mat="cloth")
    f.paint(f.c.intersect(sm, f.poly([(-30, -33), (30, -33), (30, -26), (-30, -26)])), L_DARK, layer="l1", mat="cloth", outline=0.4)


def wolf_rider(c, fx, fy, u=1.0):
    f = Fig(c, fx, fy, u * 1.08)
    shadow(f, 36)
    wolf(f)
    r = Fig(c, *f.p(-2, -16), u * 0.84)    # rider seat ~ y=-30 in rider coords
    big_axe(r, (-20, -26), (-18, -96), 1.05)
    orc_arm(r, (-16, -62), (-24, -48), (-20, -36), dark=0.75)
    fist(r, -20, -33, dark=0.75)
    orc_torso(r, loin=False)
    r.paint(r.cap((2, -30), (16, -24), 9, 8), DLEATHER, mat="leather")
    r.paint(r.cap((16, -24), (15, -10), 7, 6.5), OSKIN, mat="skin")
    boot(r, 15, -4, DLEATHER, 1.0)
    spiked_pauldron(r, -12, -70, 0.7, dark=0.8, spikes=2)
    spiked_pauldron(r, 0, -66, 0.95, spikes=3, trim=True)
    orc_arm(r, (6, -58), (12, -44), (22, -36))
    orc_head(r, 19, -66)
    fist(r, 24, -34)




# ================================================================== output
# sprite name -> (draw function, slot). Slots follow AbsoluteUnits' layout (at 2x):
# civilians stand on the left of the tile, military units on the right.
SPRITES = {
    "Peasant-Humans": (peasant, "civilian"), "Settler-Humans": (settler_h, "civilian"),
    "Priest": (priest, "civilian"),
    "Militia-Humans": (militia, "military"), "Archer-Humans": (archer, "military"),
    "Spearman-Humans": (spearman, "military"), "Footman": (footman, "military"),
    "Mage": (mage, "military"), "Paladin": (paladin, "mounted"),
    "Peasant-Orcs": (peon, "civilian"), "Settler-Orcs": (settler_o, "civilian"),
    "Missionary-Orcs": (shaman, "civilian"),
    "Militia-Orcs": (militia_o, "military"), "Archer-Orcs": (archer_o, "military"),
    "Spearman-Orcs": (spearman_o, "military"), "Grunt": (grunt, "military"),
    "Wolf Rider": (wolf_rider, "mounted"),
}
SLOTS = {"civilian": ((190, 162), 40, 124), "military": ((190, 162), 145, 124), "mounted": ((190, 172), 122, 164)}
X_SHIFT = {"Grunt": -7, "Mage": -6}


def render(name):
    from paint import Canvas
    fn, slot = SPRITES[name]
    (w, h), fx, fy = SLOTS[slot]
    c = Canvas(w, h)
    fn(c, fx + X_SHIFT.get(name, 0), fy)
    return c.finish()


def write_all(image_dirs, unit_dir="TileSets/AbsoluteUnits/Units/"):
    """Overwrite the trial units' sprites, including any era-specific variants that the
    other generators wrote ("Settler-Orcs-Age of Tribes"), so the new look shows in every era."""
    import os
    count = 0
    for name in SPRITES:
        layers = render(name)
        targets = set()
        for d in image_dirs:
            folder = os.path.join(d, unit_dir)
            if not os.path.isdir(folder):
                continue
            for fname in os.listdir(folder):
                stem = fname[:-4]
                for suf in ("-1", "-2"):
                    if stem.endswith(suf):
                        stem = stem[:-2]
                        break
                if stem == name or (stem.startswith(name + "-") and stem[len(name) + 1:].startswith("Age of")):
                    targets.add((folder, stem))
        if not targets:
            targets.add((os.path.join(image_dirs[0], unit_dir), name))
        for folder, stem in targets:
            os.makedirs(folder, exist_ok=True)
            for suf, im in zip(("", "-1", "-2"), layers):
                im.save(os.path.join(folder, stem + suf + ".png"))
                count += 1
    return count
