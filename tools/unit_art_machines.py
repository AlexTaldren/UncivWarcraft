"""Hand-placed pixel sprites for ships, war machines and the two airborne units that
are drawn on the map (trial). Same grid, ramps, outline and layer rules as unit_art.py.
All designs are original.
"""
from unit_art import *            # noqa: F401,F403
from unit_art_humans import *     # noqa: F401,F403  (ramps and shared parts)
import unit_art as UA
import unit_art_humans as UH

WY = 31                          # waterline
CX = 23
FOAM = ((240, 248, 252), (196, 226, 242), (150, 196, 226))
TURT = ((176, 200, 124), (128, 158, 92), (86, 112, 78))
BRASS = ((244, 214, 130), (204, 156, 76), (140, 98, 58))
TAR = ((122, 92, 70), (86, 62, 52), (56, 40, 42))


# ---------------------------------------------------------------- ship parts (bow to the right)
def hull(cv, x0, x1, top, wy=WY, ramp=WOOD, rake=1):
    h = wy - top + 1
    s = cv.part()
    rows = []
    for k in range(h):
        left = x0 + max(0, k - (h - 3))
        right = x1 - (k * rake if rake >= 1 else k // 2)
        rows.append((top + k, left, right))
    cv.rows(s, rows, ramp[1])
    cv.rows(s, rows[:1], ramp[0])
    cv.rows(s, rows[-2:], ramp[2])
    return s


def foam(cv, x0, x1, wy=WY, bow=True):
    f = cv.part(sep=False)
    for x in range(x0, x1 + 1):
        cv.put(f, x, wy + 1, FOAM[1] if x % 3 else FOAM[0])
    if bow:
        cv.pix(f, [(x1 + 1, wy), (x1 + 1, wy + 1), (x1 + 2, wy + 1)], FOAM[0])
    cv.pix(f, [(x0 - 1, wy + 1), (x0 - 3, wy + 1)], FOAM[2])


def mast(cv, x, top, deck):
    m = cv.part()
    cv.rect(m, x, top, x, deck, TAR[1])


def sail(cv, xm, y0, w, h, layer=2, ramp=TINT, band=1):
    s = cv.part(layer)
    a, b = xm - w // 2, xm + w // 2
    rows = [(y0 + i, a, b + (1 if 0 < i < h - 1 else 0)) for i in range(h)]
    cv.rows(s, rows, lit(ramp, dark_from=b - 1, light_to=a + 2, light_rows=y0 + h - 3))
    if band is not None:
        t = cv.part(band, sep=False)
        cv.rect(t, a, y0 + 1, b + 1, y0 + 1, lit(TINT, dark_from=b - 1))
    return s


def flag(cv, x, y, layer=1, n=4):
    f = cv.part(layer)
    cv.rows(f, [(y, x + 1, x + n), (y + 1, x + 1, x + n - 1)], lit(TINT, dark_from=x + n - 1))


def funnel(cv, x, top, deck, w=3, band=1):
    f = cv.part()
    cv.rect(f, x, top, x + w - 1, deck, lit(IRON, dark_from=x + w - 1, light_to=x))
    cv.rect(f, x - 1, top, x + w, top, IRON[0])
    if band is not None:
        b = cv.part(band, sep=False)
        cv.rect(b, x, top + 2, x + w - 1, top + 3, lit(TINT, dark_from=x + w - 1))


def smoke(cv, x, y):
    s = cv.part()
    cv.rows(s, [(y - 3, x - 6, x - 3), (y - 2, x - 7, x - 2), (y - 1, x - 5, x - 1), (y, x - 2, x)],
            lit(SMOKE, dark_from=x - 2, light_to=x - 5, light_rows=y - 2))


def ports(cv, xs, y, c=DARK):
    p = cv.part(sep=False)
    cv.pix(p, [(x, y) for x in xs], c)


def stripe(cv, x0, x1, y0, y1, layer=2):
    s = cv.part(layer, sep=False)
    cv.rect(s, x0, y0, x1, y1, lit(TINT, dark_from=x1 - 2, light_to=x0 + 3, light_rows=y0))


def oars(cv, xs, y, n=4):
    o = cv.part()
    for x in xs:
        cv.pix(o, [(x - i // 2, y + i) for i in range(n)], WOOD[0])


# ================================================================ ships
def skiff(cv):
    """Fishing skiff: one small boat, a three-cornered sail, rod over the stern, the catch in a basket."""
    hull(cv, 13, 32, WY - 3)
    mast(cv, 21, 9, WY - 4)
    s = cv.part(2)
    cv.rows(s, [(11 + i, 22, 23 + (i * 2) // 3) for i in range(15)], lit(TINT, dark_from=30, light_to=24, light_rows=22))
    b = cv.part(1, sep=False)
    cv.rect(b, 22, 24, 32, 24, TINT[1])
    r = cv.part()
    cv.pix(r, line(15, WY - 4, 8, WY - 11), WOOD[0])
    st = cv.part()
    cv.rect(st, 8, WY - 10, 8, WY - 1, STRING)
    bk = cv.part()
    cv.rect(bk, 26, WY - 6, 30, WY - 4, lit(TAN, dark_from=30, light_to=27, light_rows=WY - 6))
    fs = cv.part(sep=False)
    cv.pix(fs, [(27, WY - 6), (29, WY - 6)], STEEL[0])
    foam(cv, 13, 31)


def longboat(cv):
    """Longboat: low hull with tall carved posts, shields along the rail, oars out, one striped sail."""
    for x, top in ((5, WY - 10), (39, WY - 11)):                                       # stern and stem posts
        p = cv.part()
        cv.rect(p, x, top, x + 1, WY - 3, lit(WOOD, dark_from=x + 1))
    hd = cv.part()
    cv.rows(hd, [(WY - 12, 40, 42), (WY - 11, 41, 43)], WOOD[0])
    cv.put(hd, 42, WY - 12, DARK)
    hull(cv, 5, 40, WY - 4)
    mast(cv, 22, 5, WY - 5)
    s = sail(cv, 22, 8, 17, 12, band=None)
    st = cv.part(1, sep=False)
    for x in (16, 17, 21, 22, 23, 27, 28):
        cv.rect(st, x, 8, x, 19, TINT[1 if x < 26 else 2])
    flag(cv, 22, 5, 1)
    for i, x in enumerate(range(9, 36, 5)):                                            # shields
        sh = cv.part(2 if i % 2 == 0 else 1)
        cv.rows(sh, [(WY - 6, x + 1, x + 1), (WY - 5, x, x + 2), (WY - 4, x, x + 2), (WY - 3, x + 1, x + 1)], lit(TINT, dark_from=x + 2))
        bs = cv.part(sep=False)
        cv.put(bs, x + 1, WY - 5, STEEL[0])
    foam(cv, 6, 38)
    oars(cv, range(11, 36, 5), WY - 1, n=5)


def brigantine(cv):
    """Brigantine: two masts, square sails in the nation's colours, long bowsprit with a jib."""
    cb = cv.part()                                                                     # stern cabin
    cv.rect(cb, 6, WY - 9, 13, WY - 6, lit(WOOD, dark_from=12, light_to=7, light_rows=WY - 9))
    ports(cv, [8, 10], WY - 8, GLOW[1])
    bs = cv.part()
    cv.pix(bs, line(35, WY - 7, 44, WY - 11), TAR[1])
    jb = cv.part(1)
    cv.rows(jb, [(y, 33 + (y - 8) // 2, 34 + (y - 8) * 2 // 3) for y in range(9, WY - 9)], lit(TINT, dark_from=40))
    hull(cv, 6, 37, WY - 6)
    stripe(cv, 7, 34, WY - 4, WY - 4)
    mast(cv, 17, 3, WY - 7)
    mast(cv, 28, 5, WY - 7)
    sail(cv, 17, 5, 9, 6)
    sail(cv, 17, 13, 11, 9)
    sail(cv, 28, 7, 7, 5)
    sail(cv, 28, 14, 9, 8)
    flag(cv, 17, 2, 1)
    foam(cv, 7, 35)


def buccaneer(cv):
    """Buccaneer: tarred hull, black sails with a pale skull, a big flag in the nation's colour."""
    cb = cv.part()
    cv.rect(cb, 7, WY - 10, 14, WY - 6, lit(TAR, dark_from=13, light_to=8, light_rows=WY - 10))
    ports(cv, [9, 11], WY - 8, FLAME[1])
    bs = cv.part()
    cv.pix(bs, line(34, WY - 7, 42, WY - 11), TAR[1])
    hull(cv, 7, 36, WY - 6, ramp=TAR)
    stripe(cv, 8, 33, WY - 5, WY - 5, layer=1)
    ports(cv, [14, 19, 24, 29], WY - 3)
    mast(cv, 13, 9, WY - 7)
    mast(cv, 24, 3, WY - 7)
    lt = cv.part()                                                                     # lateen on the mizzen
    cv.rows(lt, [(11 + i, 14, 15 + i // 2) for i in range(9)], lit(CLOTHD, dark_from=17, light_to=14))
    sail(cv, 24, 6, 9, 5, layer=0, ramp=CLOTHD, band=None)
    sail(cv, 24, 13, 13, 9, layer=0, ramp=CLOTHD, band=None)
    sk = cv.part(sep=False)
    cv.rows(sk, [(14, 23, 25), (15, 22, 26), (16, 22, 26), (17, 22, 26), (18, 23, 25)], WHITE[0])
    cv.pix(sk, [(23, 16), (25, 16), (24, 18)], DARK)
    f = cv.part(2)
    cv.rows(f, [(1, 25, 31), (2, 25, 32), (3, 25, 31), (4, 25, 29)], lit(TINT, dark_from=30, light_to=27))
    foam(cv, 8, 34)


def war_galley(cv):
    """War galley: long oared hull with a bronze ram, awning at the stern, a ballista on the foredeck, one sail."""
    aw = cv.part(1)                                                                    # stern awning
    cv.rows(aw, [(WY - 10, 6, 11), (WY - 9, 5, 12)], lit(TINT, dark_from=11))
    ps = cv.part()
    cv.pix(ps, [(5, WY - 8), (5, WY - 7), (5, WY - 6), (12, WY - 8), (12, WY - 7), (12, WY - 6)], WOOD[2])
    hull(cv, 4, 38, WY - 5)
    stripe(cv, 5, 35, WY - 4, WY - 4)
    rm = cv.part()                                                                     # ram
    cv.rows(rm, [(WY - 1, 37, 42), (WY, 36, 40)], lit(BRASS, dark_from=40))
    mast(cv, 20, 5, WY - 6)
    sail(cv, 20, 8, 13, 10)
    flag(cv, 20, 5, 1)
    bx = 31                                                                            # ballista
    b = cv.part()
    cv.pix(b, [(bx + 2, WY - 12), (bx + 3, WY - 11), (bx + 4, WY - 10), (bx + 4, WY - 9), (bx + 4, WY - 8), (bx + 3, WY - 7), (bx + 2, WY - 6)], WOOD[0])
    cv.rect(b, bx - 1, WY - 9, bx + 6, WY - 9, WOOD[1])
    cv.pix(b, [(bx + 7, WY - 9)], STEEL[0])
    foam(cv, 5, 35, bow=False)
    oars(cv, range(9, 36, 4), WY - 2, n=6)


def frigate(cv):
    """Frigate: three masts of white sail banded in the nation's colour, a gun deck along the side."""
    cb = cv.part()
    cv.rect(cb, 4, WY - 11, 10, WY - 8, lit(WOOD, dark_from=9, light_to=5, light_rows=WY - 11))
    ports(cv, [6, 8], WY - 10, GLOW[1])
    bs = cv.part()
    cv.pix(bs, line(36, WY - 9, 45, WY - 13), TAR[1])
    hull(cv, 4, 38, WY - 8)
    stripe(cv, 5, 34, WY - 6, WY - 5)
    ports(cv, range(8, 33, 4), WY - 5)
    mast(cv, 12, 5, WY - 9)
    mast(cv, 21, 2, WY - 9)
    mast(cv, 30, 5, WY - 9)
    for xm, tiers in ((12, ((7, 5, 4), (12, 7, 4), (17, 7, 5))), (21, ((4, 7, 4), (9, 9, 5), (15, 9, 7))), (30, ((7, 5, 4), (12, 7, 4), (17, 7, 5)))):
        for y0, w, h in tiers:
            sail(cv, xm, y0, w, h, layer=0, ramp=WHITE, band=2)
    flag(cv, 21, 1, 1)
    foam(cv, 5, 35)


def ironclad(cv):
    """Ironclad: low iron hull with a ram, a sloped armoured casemate with gun ports, one funnel, one short mast."""
    smoke(cv, 20, WY - 18)
    mast(cv, 31, WY - 18, WY - 10)
    flag(cv, 31, WY - 18, 2)
    funnel(cv, 19, WY - 16, WY - 10)
    c = cv.part()                                                                      # casemate
    rows = [(WY - 9 + k, 12 - k, 31 + k) for k in range(5)]
    cv.rows(c, rows, lit(STEEL, dark_from=30, light_to=27, light_rows=WY - 8))
    cv.rows(c, rows[-1:], STEEL[2])
    stripe(cv, 12, 31, WY - 9, WY - 8)
    ports(cv, [13, 14, 20, 21, 27, 28], WY - 6)
    ports(cv, [10, 17, 24, 31, 34], WY - 5, IRON[2])
    hull(cv, 4, 40, WY - 4, ramp=IRON)
    rm = cv.part()
    cv.rows(rm, [(WY - 1, 38, 43), (WY, 37, 41)], lit(STEEL, dark_from=41))
    foam(cv, 5, 36, bow=False)


def destroyer(cv):
    """Destroyer: a long lean steel hull, bridge amidships, two raked funnels, a gun on the foredeck."""
    smoke(cv, 13, WY - 13)
    funnel(cv, 12, WY - 11, WY - 5)
    funnel(cv, 17, WY - 11, WY - 5)
    mast(cv, 25, WY - 18, WY - 10)
    flag(cv, 25, WY - 18, 2)
    br = cv.part()                                                                     # bridge
    cv.rect(br, 22, WY - 9, 29, WY - 5, lit(WHITE, dark_from=28, light_to=23, light_rows=WY - 8))
    ports(cv, [24, 26, 28], WY - 8, AZER[1])
    gn = cv.part()
    cv.rect(gn, 32, WY - 6, 35, WY - 5, lit(STEEL, dark_from=35))
    cv.rect(gn, 36, WY - 6, 39, WY - 6, IRON[1])
    hull(cv, 3, 42, WY - 4, ramp=STEEL)
    stripe(cv, 4, 38, WY - 2, WY - 2)
    ports(cv, [8, 12, 16, 20], WY - 3, IRON[2])
    foam(cv, 4, 38)


def dreadnought(cv):
    """Dreadnought: a high steel hull, stepped bridge and tall mast, two funnels, a big gun turret at each end."""
    smoke(cv, 12, WY - 17)
    smoke(cv, 28, WY - 17)
    funnel(cv, 11, WY - 15, WY - 7, w=4)
    funnel(cv, 27, WY - 15, WY - 7, w=4)
    mast(cv, 21, WY - 24, WY - 15)
    nest = cv.part()
    cv.rect(nest, 20, WY - 20, 22, WY - 19, IRON[1])
    flag(cv, 21, WY - 24, 2)
    t1 = cv.part()
    cv.rect(t1, 16, WY - 11, 25, WY - 7, lit(STEEL, dark_from=24, light_to=17, light_rows=WY - 10))
    t2 = cv.part()
    cv.rect(t2, 18, WY - 15, 23, WY - 12, lit(WHITE, dark_from=23, light_to=19, light_rows=WY - 14))
    ports(cv, [19, 21, 23], WY - 14, AZER[1])
    for x0, d in ((33, 1), (5, -1)):                                                   # turrets
        t = cv.part()
        cv.rect(t, x0, WY - 10, x0 + 4, WY - 7, lit(STEEL, dark_from=x0 + 4, light_to=x0 + 1, light_rows=WY - 9))
        b = cv.part()
        if d > 0:
            cv.rect(b, x0 + 5, WY - 10, x0 + 10, WY - 9, lit(IRON, light_to=x0 + 10, light_rows=WY - 10))
        else:
            cv.rect(b, x0 - 4, WY - 10, x0 - 1, WY - 9, lit(IRON, light_to=x0 - 1, light_rows=WY - 10))
    hull(cv, 2, 44, WY - 6, ramp=STEEL)
    stripe(cv, 3, 38, WY - 5, WY - 4)
    ports(cv, range(6, 36, 3), WY - 3, IRON[2])
    bt = cv.part(sep=False)
    cv.rect(bt, 4, WY - 1, 39, WY - 1, RED[2])
    foam(cv, 4, 39)


def juggernaught(cv):
    """Juggernaught: a towering iron-banded hull with castles fore and aft, heavy guns in the side, two great sails."""
    ac = cv.part()                                                                     # aft castle
    cv.rect(ac, 3, WY - 16, 11, WY - 11, lit(WOOD, dark_from=10, light_to=4, light_rows=WY - 15))
    ports(cv, [5, 7, 9], WY - 14, GLOW[1])
    rl = cv.part(sep=False)
    cv.rect(rl, 3, WY - 16, 11, WY - 16, IRON[0])
    fc = cv.part()                                                                     # fore castle
    cv.rect(fc, 31, WY - 14, 38, WY - 11, lit(WOOD, dark_from=37, light_to=32, light_rows=WY - 13))
    gn = cv.part()                                                                     # bow chaser
    cv.rect(gn, 37, WY - 16, 44, WY - 15, lit(IRON, light_to=44, light_rows=WY - 16))
    hull(cv, 3, 41, WY - 10, rake=0)
    bd = cv.part(sep=False)                                                            # iron bands
    for x in (8, 15, 22, 29, 35):
        cv.rect(bd, x, WY - 10, x, WY - 2, IRON[1])
    cv.rect(bd, 3, WY - 10, 41, WY - 10, IRON[0])
    stripe(cv, 4, 38, WY - 8, WY - 8)
    gp = cv.part(sep=False)
    for x in (11, 18, 25, 32):
        cv.rect(gp, x, WY - 6, x + 1, WY - 5, DARK)
        cv.rect(gp, x + 2, WY - 6, x + 2, WY - 6, IRON[0])
    sp = cv.part()                                                                     # prow spikes
    cv.pix(sp, [(42, WY - 9), (43, WY - 9), (41, WY - 6), (42, WY - 6)], STEEL[0])
    mast(cv, 15, 2, WY - 11)
    mast(cv, 26, 4, WY - 11)
    sail(cv, 15, 4, 9, 6)
    sail(cv, 15, 12, 9, 7)
    sail(cv, 26, 6, 7, 5)
    sail(cv, 26, 13, 9, 6)
    flag(cv, 15, 1, 1)
    foam(cv, 4, 39)


def admiral(cv, cx=CIV_X + 3):
    """Admiral: cocked hat, coat in the nation's colour with gold shoulders, spyglass to his eye, standing in his gig."""
    fy = WY - 3
    hang(cv, cx - 6, fy, TINT, layer=2)
    legs(cv, cx, fy, WHITE)
    ct = cv.part(2)
    cv.rows(ct, [(y, cx - 4, cx + 4) for y in range(fy - 16, fy - 4)], lit(TINT, dark_from=cx + 3, light_to=cx - 3, light_rows=fy - 11))
    bn = cv.part(sep=False)
    cv.pix(bn, [(cx + 1, fy - 13), (cx + 1, fy - 11), (cx + 1, fy - 9), (cx + 1, fy - 7)], GOLD[0])
    cv.rect(bn, cx - 4, fy - 8, cx + 4, fy - 8, WHITE[1])
    head(cv, cx, fy - T)
    hair(cv, cx, fy - T, WHITE)
    top = fy - T
    h = cv.part()                                                                      # cocked hat
    cv.rows(h, [(top - 3, cx - 1, cx + 2), (top - 2, cx - 3, cx + 4), (top - 1, cx - 5, cx + 6), (top, cx - 6, cx + 7)],
            lit(CLOTHD, dark_from=cx + 4, light_to=cx - 1, light_rows=top - 2))
    tr = cv.part(sep=False)
    cv.rect(tr, cx - 6, top, cx + 7, top, GOLD[1])
    ck = cv.part(1)
    cv.rect(ck, cx, top - 2, cx + 1, top - 1, TINT[0])
    pauldron(cv, cx - 7, fy - 17, GOLD, w=4)
    sg = cv.part()                                                                     # spyglass
    cv.rect(sg, cx + 4, top + 3, cx + 11, top + 3, BRASS[1])
    cv.rect(sg, cx + 9, top + 2, cx + 11, top + 4, BRASS[0])
    cv.put(sg, cx + 11, top + 3, AZER[0])
    sl = cv.part(2)
    cv.rect(sl, cx + 4, fy - 15, cx + 6, fy - 13, lit(TINT, dark_from=cx + 6))
    cv.rect(sl, cx + 5, fy - 18, cx + 7, fy - 15, lit(TINT, dark_from=cx + 7, light_to=cx + 5))
    fist(cv, cx + 5, top + 3)
    pauldron(cv, cx + 3, fy - 17, GOLD, w=4)
    hull(cv, cx - 9, cx + 11, WY - 3)
    stripe(cv, cx - 8, cx + 8, WY - 2, WY - 2, layer=1)
    foam(cv, cx - 8, cx + 9)


def giant_turtle(cv):
    """War turtle: a huge sea turtle with an iron-rimmed shell, a small gun platform strapped on top."""
    cx = 21
    fl = cv.part()                                                                     # far flippers
    cv.rows(fl, [(WY - 1, 6, 11), (WY, 5, 9)], TURT[2])
    hd = cv.part()                                                                     # head and neck
    cv.rows(hd, [(WY - 9, 36, 40), (WY - 8, 34, 42), (WY - 7, 33, 43), (WY - 6, 33, 43), (WY - 5, 33, 41), (WY - 4, 33, 37)],
            lit(TURT, dark_from=41, light_to=38, light_rows=WY - 8))
    e = cv.part(sep=False)
    cv.put(e, 40, WY - 7, DARK)
    cv.rect(e, 40, WY - 5, 42, WY - 5, TURT[2])
    pf = cv.part()                                                                     # platform
    cv.rect(pf, cx - 6, WY - 19, cx + 5, WY - 18, lit(WOOD, dark_from=cx + 4))
    cl = cv.part(2)
    cv.rect(cl, cx - 5, WY - 17, cx + 4, WY - 14, lit(TINT, dark_from=cx + 3, light_to=cx - 3, light_rows=WY - 16))
    tr = cv.part(1, sep=False)
    cv.rect(tr, cx - 5, WY - 14, cx + 4, WY - 14, TINT[1])
    gn = cv.part()
    cv.rect(gn, cx - 1, WY - 22, cx + 9, WY - 21, lit(IRON, light_to=cx + 9, light_rows=WY - 22))
    cv.rect(gn, cx - 3, WY - 23, cx, WY - 20, IRON[1])
    mast(cv, cx - 5, WY - 27, WY - 20)
    flag(cv, cx - 5, WY - 27, 1)
    sh = cv.part()                                                                     # shell
    rows = [(WY - 14, cx - 6, cx + 6), (WY - 13, cx - 9, cx + 9), (WY - 12, cx - 11, cx + 11), (WY - 11, cx - 12, cx + 12)] + \
           [(y, cx - 13, cx + 13) for y in range(WY - 10, WY - 5)] + [(WY - 5, cx - 14, cx + 14), (WY - 4, cx - 14, cx + 14)]
    cv.rows(sh, rows, lit(GREEN, dark_from=cx + 10, light_to=cx - 2, light_rows=WY - 11))
    sm = cv.part(sep=False)                                                            # plates
    for x in (cx - 8, cx - 2, cx + 4, cx + 10):
        cv.pix(sm, [(x, WY - 12), (x - 1, WY - 11), (x - 1, WY - 10), (x, WY - 9), (x + 1, WY - 8), (x + 1, WY - 7), (x, WY - 6)], GREEN[2])
    cv.rect(sm, cx - 14, WY - 5, cx + 14, WY - 4, IRON[1])
    cv.pix(sm, [(x, WY - 5) for x in range(cx - 12, cx + 13, 4)], STEEL[0])
    bl = cv.part()                                                                     # belly and near flippers
    cv.rows(bl, [(WY - 3, cx - 13, cx + 13), (WY - 2, cx - 12, cx + 12)], TAN[1])
    f2 = cv.part()
    cv.rows(f2, [(WY - 2, 26, 33), (WY - 1, 27, 35), (WY, 29, 36)], lit(TURT, dark_from=34, light_to=30))
    cv.rows(f2, [(WY - 2, 9, 14), (WY - 1, 8, 13), (WY, 7, 11)], TURT[1])
    foam(cv, 8, 34, bow=False)


# ================================================================ war machines
def demolisher(cv, cx=CX - 1, fy=FY):
    """Demolisher: an armoured stone-thrower with a spiked iron plough, its shot already burning."""
    UA.catapult(cv, cx, fy)
    sh = cv.part()                                                                     # burning shot over the stone
    cv.rows(sh, [(fy - 29, cx - 16, cx - 14), (fy - 28, cx - 17, cx - 13), (fy - 27, cx - 17, cx - 13), (fy - 26, cx - 16, cx - 14)], FLAME[1])
    cv.pix(sh, [(cx - 16, fy - 28), (cx - 15, fy - 28), (cx - 15, fy - 27)], FLAME[0])
    cv.pix(sh, [(cx - 13, fy - 27), (cx - 14, fy - 26), (cx - 13, fy - 28)], FLAME[2])
    fl = cv.part()
    cv.pix(fl, [(cx - 15, fy - 30), (cx - 14, fy - 30), (cx - 17, fy - 30), (cx - 12, fy - 29)], FLAME[1])
    pl = cv.part()                                                                     # plough
    cv.rows(pl, [(fy - 14, cx + 11, cx + 12), (fy - 13, cx + 11, cx + 13), (fy - 12, cx + 11, cx + 14)] + [(y, cx + 12, cx + 15) for y in range(fy - 11, fy - 3)] +
                [(fy - 3, cx + 12, cx + 14)], lit(IRON, dark_from=cx + 15, light_to=cx + 12, light_rows=fy - 8))
    sp = cv.part()
    cv.pix(sp, [(cx + 16, fy - 10), (cx + 17, fy - 10), (cx + 16, fy - 7), (cx + 17, fy - 7), (cx + 16, fy - 4), (cx + 17, fy - 4)], STEEL[0])
    bd = cv.part(sep=False)                                                            # iron straps on the beam
    for x in (cx - 11, cx - 1, cx + 9):
        cv.rect(bd, x, fy - 8, x, fy - 5, IRON[1])


def war_golem(cv, cx=CX, fy=FY):
    """War golem: a squat iron giant with a furnace in its chest, a stack on its back and fists like anvils."""
    cv.shadow(cx, 12)
    stk = cv.part()
    cv.rect(stk, cx - 10, fy - 29, cx - 8, fy - 23, lit(IRON, dark_from=cx - 8, light_to=cx - 10))
    for x0 in (cx - 12, cx + 9):                                                       # arms
        a = cv.part()
        cv.rect(a, x0, fy - 19, x0 + 3, fy - 10, lit(IRON, dark_from=x0 + 3, light_to=x0))
    for x0 in (cx - 6, cx + 2):                                                        # legs
        l = cv.part()
        cv.rect(l, x0, fy - 9, x0 + 4, fy - 2, lit(IRON, dark_from=x0 + 4, light_to=x0))
        f = cv.part()
        cv.rect(f, x0 - 1, fy - 2, x0 + 5, fy, lit(STEEL, dark_from=x0 + 4, light_to=x0, light_rows=fy - 2))
        cv.rect(f, x0 - 1, fy, x0 + 5, fy, IRON[2])
    pv = cv.part()
    cv.rect(pv, cx - 6, fy - 12, cx + 6, fy - 10, lit(STEEL, dark_from=cx + 5, light_to=cx - 4))
    tr = cv.part()                                                                     # boiler body
    cv.rows(tr, [(fy - 23, cx - 7, cx + 7)] + [(y, cx - 8, cx + 8) for y in range(fy - 22, fy - 13)] + [(fy - 13, cx - 7, cx + 7)],
            lit(STEEL, dark_from=cx + 6, light_to=cx - 5, light_rows=fy - 19))
    rv = cv.part(sep=False)
    cv.pix(rv, [(cx - 7, fy - 21), (cx + 7, fy - 21), (cx - 7, fy - 15), (cx + 7, fy - 15)], IRON[2])
    cv.rect(rv, cx - 4, fy - 20, cx + 4, fy - 15, IRON[2])
    fr = cv.part(sep=False)                                                            # furnace
    cv.rect(fr, cx - 3, fy - 19, cx + 3, fy - 16, FLAME[1])
    cv.rect(fr, cx - 2, fy - 17, cx + 2, fy - 16, FLAME[0])
    cv.pix(fr, [(cx - 1, y) for y in range(fy - 19, fy - 15)] + [(cx + 1, y) for y in range(fy - 19, fy - 15)], IRON[2])
    hd = cv.part()
    cv.rect(hd, cx - 3, fy - 28, cx + 3, fy - 24, lit(IRON, dark_from=cx + 3, light_to=cx - 2, light_rows=fy - 27))
    ey = cv.part(sep=False)
    cv.rect(ey, cx - 1, fy - 26, cx + 3, fy - 26, FLAME[0])
    for x0 in (cx - 13, cx + 8):                                                       # shoulders: outer colour
        p = cv.part(2)
        cv.rows(p, [(fy - 25, x0 + 1, x0 + 4), (fy - 24, x0, x0 + 5), (fy - 23, x0, x0 + 5), (fy - 22, x0, x0 + 5), (fy - 21, x0, x0 + 5)],
                lit(TINT, dark_from=x0 + 4, light_to=x0 + 1, light_rows=fy - 23))
        t = cv.part(1, sep=False)
        cv.rect(t, x0, fy - 21, x0 + 5, fy - 21, TINT[1])
    for x0 in (cx - 13, cx + 8):                                                       # fists
        f = cv.part()
        cv.rect(f, x0, fy - 10, x0 + 5, fy - 5, lit(STEEL, dark_from=x0 + 4, light_to=x0 + 1, light_rows=fy - 8))
        cv.rect(f, x0, fy - 5, x0 + 5, fy - 5, IRON[2])


def siege_engine(cv, cx=CX - 1, fy=FY):
    """Siege engine: a long brass-bound steam wagon with one huge driving wheel, a bombard on top and a ram out front."""
    cv.shadow(cx, 17)
    smoke(cv, cx - 12, fy - 24)
    for x in (cx - 15, cx - 11):                                                       # twin stacks
        funnel(cv, x, fy - 22, fy - 15, w=2, band=None)
    bm = cv.part()                                                                     # bombard
    rows = [(fy - 15 - k, cx - 3 + k, cx + 3 + k) for k in range(0, 7)]
    cv.rows(bm, rows, IRON[1])
    for (y, a, b) in rows:
        cv.put(bm, a, y, IRON[0])
        cv.put(bm, b, y, IRON[2])
    cv.rows(bm, [(fy - 22, cx + 3, cx + 11)], IRON[0])
    rm = cv.part()                                                                     # ram
    cv.rect(rm, cx + 9, fy - 10, cx + 17, fy - 9, lit(WOOD, light_to=cx + 17, light_rows=fy - 10))
    rh = cv.part()
    cv.rows(rh, [(fy - 12, cx + 17, cx + 18), (fy - 11, cx + 17, cx + 20), (fy - 10, cx + 17, cx + 21), (fy - 9, cx + 17, cx + 21), (fy - 8, cx + 17, cx + 20), (fy - 7, cx + 17, cx + 18)],
            lit(STEEL, dark_from=cx + 20, light_to=cx + 18, light_rows=fy - 10))
    hl = cv.part()                                                                     # hull
    rows = [(fy - 15, cx - 16, cx + 6)] + [(y, cx - 17, cx + 8 + min(2, y - (fy - 14))) for y in range(fy - 14, fy - 5)] + [(fy - 5, cx - 16, cx + 9)]
    cv.rows(hl, rows, lit(IRON, dark_from=cx + 8, light_to=cx - 14, light_rows=fy - 13))
    bd = cv.part(sep=False)                                                            # brass bands
    cv.rect(bd, cx - 17, fy - 14, cx + 8, fy - 14, BRASS[1])
    cv.rect(bd, cx - 17, fy - 6, cx + 10, fy - 6, BRASS[2])
    for x in (cx - 12, cx - 4, cx + 4):
        cv.rect(bd, x, fy - 13, x, fy - 7, BRASS[1])
    pn = cv.part(2, sep=False)
    cv.rect(pn, cx - 3, fy - 12, cx + 3, fy - 8, lit(TINT, dark_from=cx + 2, light_to=cx - 1, light_rows=fy - 11))
    ch = cv.part(1, sep=False)
    cv.rect(ch, cx - 3, fy - 12, cx + 3, fy - 11, lit(TINT, dark_from=cx + 2))
    wx = cx - 9                                                                        # driving wheel: 11 px
    w = cv.part()
    rows = [(fy - 10, wx - 2, wx + 2), (fy - 9, wx - 4, wx + 4)] + [(y, wx - 5, wx + 5) for y in range(fy - 8, fy - 1)] + [(fy - 1, wx - 4, wx + 4), (fy, wx - 2, wx + 2)]
    cv.rows(w, rows, lit(IRON, dark_from=wx + 4, light_to=wx - 3, light_rows=fy - 7))
    sp = cv.part(sep=False)
    cv.rows(sp, [(y, wx - 3, wx + 3) for y in range(fy - 8, fy - 1)], IRON[2])
    cv.rect(sp, wx - 3, fy - 5, wx + 3, fy - 5, BRASS[1])
    cv.rect(sp, wx, fy - 8, wx, fy - 2, BRASS[1])
    cv.put(sp, wx, fy - 5, BRASS[0])
    iron_wheel(cv, cx + 5, fy)


def mechano_tank(cv, cx=CX - 1, fy=FY):
    """Mechano-tank: wide treads, a low riveted hull, a domed turret with a long gun and a sparking aerial."""
    cv.shadow(cx, 16)
    an = cv.part()
    cv.rect(an, cx - 5, fy - 26, cx - 5, fy - 19, IRON[0])
    sp = cv.part()
    cv.pix(sp, [(cx - 5, fy - 27), (cx - 7, fy - 28), (cx - 3, fy - 28)], AZER[0])
    gn = cv.part()                                                                     # gun
    cv.rect(gn, cx + 5, fy - 18, cx + 17, fy - 17, lit(IRON, light_to=cx + 17, light_rows=fy - 18))
    cv.rect(gn, cx + 16, fy - 19, cx + 17, fy - 16, IRON[2])
    dm = cv.part()                                                                     # dome
    cv.rows(dm, [(fy - 21, cx - 3, cx + 3), (fy - 20, cx - 5, cx + 5), (fy - 19, cx - 6, cx + 6), (fy - 18, cx - 7, cx + 7), (fy - 17, cx - 7, cx + 7),
                 (fy - 16, cx - 7, cx + 7), (fy - 15, cx - 7, cx + 7)], lit(STEEL, dark_from=cx + 5, light_to=cx - 2, light_rows=fy - 19))
    bd = cv.part(1, sep=False)
    cv.rect(bd, cx - 7, fy - 15, cx + 7, fy - 15, lit(TINT, dark_from=cx + 5))
    pw = cv.part(sep=False)
    cv.rect(pw, cx, fy - 19, cx + 2, fy - 17, AZER[1])
    cv.put(pw, cx, fy - 19, AZER[0])
    hl = cv.part()                                                                     # hull
    cv.rows(hl, [(fy - 14, cx - 11, cx + 11), (fy - 13, cx - 12, cx + 13), (fy - 12, cx - 12, cx + 14), (fy - 11, cx - 12, cx + 14), (fy - 10, cx - 12, cx + 13),
                 (fy - 9, cx - 12, cx + 12), (fy - 8, cx - 12, cx + 12)], lit(STEEL, dark_from=cx + 11, light_to=cx + 9, light_rows=fy - 13))
    pn = cv.part(2, sep=False)
    cv.rect(pn, cx - 9, fy - 13, cx + 2, fy - 9, lit(TINT, dark_from=cx + 1, light_to=cx - 6, light_rows=fy - 12))
    cg = cv.part(sep=False)                                                            # brass cog
    cv.rows(cg, [(fy - 13, cx + 6, cx + 6), (fy - 12, cx + 5, cx + 7), (fy - 11, cx + 4, cx + 8), (fy - 10, cx + 5, cx + 7), (fy - 9, cx + 6, cx + 6)], BRASS[1])
    cv.put(cg, cx + 6, fy - 11, IRON[2])
    tk = cv.part()                                                                     # tread
    cv.rows(tk, [(fy - 7, cx - 12, cx + 12), (fy - 6, cx - 14, cx + 14)] + [(y, cx - 15, cx + 15) for y in range(fy - 5, fy - 1)] + [(fy - 1, cx - 14, cx + 14), (fy, cx - 12, cx + 12)], BLACKH[1])
    cv.rows(tk, [(fy - 7, cx - 12, cx + 12)], BLACKH[0])
    tt = cv.part(sep=False)
    cv.pix(tt, [(x, fy) for x in range(cx - 11, cx + 12, 3)] + [(x, fy - 7) for x in range(cx - 10, cx + 12, 3)], IRON[0])
    for wx in (cx - 10, cx - 3, cx + 4, cx + 11):
        cv.rows(tt, [(fy - 5, wx - 1, wx + 1), (fy - 4, wx - 2, wx + 2), (fy - 3, wx - 2, wx + 2), (fy - 2, wx - 1, wx + 1)], IRON[1])
        cv.put(tt, wx, fy - 4, STEEL[0])


def iron_colossus(cv, cx=CX, fy=FY + 4):
    """Iron colossus: a towering figure of dark metal trimmed in gold, an arcane core burning in its chest."""
    cv.shadow(cx, 12, fy)
    for x0 in (cx - 13, cx + 10):                                                      # arms
        a = cv.part()
        cv.rect(a, x0, fy - 25, x0 + 3, fy - 13, lit(IRON, dark_from=x0 + 3, light_to=x0))
        br = cv.part(sep=False)
        cv.rect(br, x0, fy - 17, x0 + 3, fy - 15, lit(GOLD, dark_from=x0 + 3))
    for x0 in (cx - 6, cx + 2):                                                        # legs
        l = cv.part()
        cv.rect(l, x0, fy - 12, x0 + 4, fy - 2, lit(IRON, dark_from=x0 + 4, light_to=x0))
        k = cv.part(sep=False)
        cv.rect(k, x0, fy - 8, x0 + 4, fy - 7, lit(GOLD, dark_from=x0 + 4))
        f = cv.part()
        cv.rect(f, x0 - 1, fy - 2, x0 + 5, fy, lit(IRON, dark_from=x0 + 4, light_to=x0 + 1, light_rows=fy - 2))
        cv.rect(f, x0 - 1, fy, x0 + 5, fy, IRON[2])
    lc = cv.part(2)                                                                    # hanging cloth
    cv.rows(lc, [(y, cx - 3, cx + 3) for y in range(fy - 14, fy - 7)] + [(fy - 7, cx - 2, cx + 2), (fy - 6, cx - 1, cx + 1)], lit(TINT, dark_from=cx + 2, light_to=cx - 2, light_rows=fy - 10))
    lt = cv.part(1, sep=False)
    cv.rect(lt, cx - 3, fy - 9, cx + 3, fy - 9, TINT[1])
    tr = cv.part()                                                                     # torso, tapering to the waist
    rows = [(fy - 28 + k, cx - 9 + k // 4, cx + 9 - k // 4) for k in range(0, 14)]
    cv.rows(tr, rows, lit(IRON, dark_from=cx + 6, light_to=cx - 6, light_rows=fy - 22))
    gt = cv.part(sep=False)
    cv.rect(gt, cx - 6, fy - 15, cx + 6, fy - 15, GOLD[1])
    cv.pix(gt, line(cx - 8, fy - 27, cx - 1, fy - 20) + line(cx + 8, fy - 27, cx + 1, fy - 20), GOLD[1])
    co = cv.part(sep=False)                                                            # core
    cv.rows(co, [(fy - 23, cx, cx), (fy - 22, cx - 1, cx + 1), (fy - 21, cx - 2, cx + 2), (fy - 20, cx - 1, cx + 1), (fy - 19, cx, cx)], ARCANE[1])
    cv.put(co, cx, fy - 21, ARCANE[0])
    hd = cv.part()
    cv.rows(hd, [(fy - 34, cx - 2, cx + 2)] + [(y, cx - 3, cx + 3) for y in range(fy - 33, fy - 29)], lit(IRON, dark_from=cx + 3, light_to=cx - 2, light_rows=fy - 32))
    ey = cv.part(sep=False)
    cv.rect(ey, cx - 1, fy - 32, cx + 3, fy - 32, ARCANE[0])
    cv.rect(ey, cx - 3, fy - 30, cx + 3, fy - 30, GOLD[1])
    for x0 in (cx - 14, cx + 8):                                                       # shoulders
        p = cv.part(2)
        cv.rows(p, [(fy - 31, x0 + 1, x0 + 5), (fy - 30, x0, x0 + 6), (fy - 29, x0, x0 + 6), (fy - 28, x0, x0 + 6), (fy - 27, x0, x0 + 6), (fy - 26, x0, x0 + 6)],
                lit(TINT, dark_from=x0 + 5, light_to=x0 + 1, light_rows=fy - 29))
        t = cv.part(1, sep=False)
        cv.rect(t, x0, fy - 26, x0 + 6, fy - 26, TINT[1])
    for x0 in (cx - 14, cx + 9):                                                       # fists
        f = cv.part()
        cv.rect(f, x0, fy - 13, x0 + 5, fy - 8, lit(IRON, dark_from=x0 + 4, light_to=x0 + 1, light_rows=fy - 11))
        cv.rect(f, x0, fy - 8, x0 + 5, fy - 8, IRON[2])


# ================================================================ in the air
def airship_tender(cv, cx=CX, fy=FY):
    """Airship tender: a long gas bag in the nation's colours over a wooden hull with a landing deck and a stern screw."""
    cv.shadow(cx, 11, fy + 3)
    fn = cv.part(1)                                                                    # tail fins
    cv.rows(fn, [(4, 3, 6), (5, 2, 7), (6, 2, 8), (10, 2, 8), (11, 2, 7), (12, 3, 6)], lit(TINT, dark_from=6, light_to=3))
    rp = cv.part()                                                                     # rigging
    cv.pix(rp, line(13, 14, 15, 19) + line(22, 15, 22, 19) + line(32, 14, 30, 19), TAR[1])
    bag = cv.part(2)
    rows = [(2, 13, 31), (3, 9, 36), (4, 7, 39), (5, 5, 41), (6, 4, 42), (7, 4, 43), (8, 4, 43), (9, 4, 42), (10, 5, 41), (11, 7, 39), (12, 9, 36), (13, 13, 31)]
    cv.rows(bag, rows, lit(TINT, dark_from=37, light_to=30, light_rows=6))
    cv.rows(bag, rows[-3:], TINT[2])
    bd = cv.part(1, sep=False)
    for x in (15, 16, 27, 28):
        cv.rect(bd, x, 3, x, 12, TINT[1])
    ns = cv.part(sep=False)
    cv.rows(ns, [(6, 41, 42), (7, 41, 43), (8, 41, 43), (9, 41, 42)], IRON[1])
    dk = cv.part()                                                                     # landing deck
    cv.rect(dk, 9, 20, 35, 20, WOOD[0])
    hl = cv.part()
    cv.rows(hl, [(21, 11, 34), (22, 11, 33), (23, 12, 32), (24, 13, 30), (25, 15, 28)], lit(WOOD, dark_from=30, light_to=27, light_rows=21))
    cv.rows(hl, [(25, 15, 28)], WOOD[2])
    ports(cv, [16, 20, 24, 28], 22, GLOW[1])
    pr = cv.part()                                                                     # screw
    cv.rect(pr, 9, 20, 9, 26, STEEL[0])
    cv.rect(pr, 10, 23, 10, 23, IRON[1])
    fm = cv.part()                                                                     # a flyer on the deck
    cv.rows(fm, [(18, 28, 31), (19, 27, 32)], BRASS[1])
    cv.rect(fm, 26, 17, 33, 17, STEEL[0])


def flying_machine(cv, cx=CX, fy=FY):
    """Flying machine: a brass pod under a whirling rotor, pilot in goggles, guns under the nose, a tail with a fin."""
    cv.shadow(cx, 8, fy + 2)
    rt = cv.part()                                                                     # rotor
    cv.rect(rt, cx - 13, 7, cx + 13, 7, STEEL[0])
    cv.pix(rt, [(cx - 14, 7), (cx + 14, 7), (cx - 8, 7), (cx + 8, 7)], STEEL[1])
    cv.rect(rt, cx, 8, cx, 11, IRON[1])
    tl = cv.part()                                                                     # tail boom
    cv.rows(tl, [(15, cx - 16, cx - 7), (16, cx - 14, cx - 7)], lit(BRASS, dark_from=cx - 8, light_to=cx - 14, light_rows=15))
    fn = cv.part(1)
    cv.rows(fn, [(10, cx - 17, cx - 16), (11, cx - 17, cx - 15), (12, cx - 17, cx - 14), (13, cx - 17, cx - 14), (14, cx - 17, cx - 14)], lit(TINT, dark_from=cx - 14))
    pd = cv.part()                                                                     # pod
    rows = [(12, cx - 5, cx + 4), (13, cx - 7, cx + 6), (14, cx - 8, cx + 8), (15, cx - 8, cx + 9), (16, cx - 8, cx + 9), (17, cx - 8, cx + 9), (18, cx - 7, cx + 8), (19, cx - 6, cx + 6), (20, cx - 4, cx + 4)]
    cv.rows(pd, rows, lit(BRASS, dark_from=cx + 7, light_to=cx - 4, light_rows=14))
    cv.rows(pd, rows[-2:], BRASS[2])
    pn = cv.part(2, sep=False)
    cv.rect(pn, cx - 7, 16, cx, 18, lit(TINT, dark_from=cx - 1, light_to=cx - 5, light_rows=16))
    wn = cv.part(sep=False)                                                            # open cockpit
    cv.rect(wn, cx + 1, 13, cx + 6, 15, AZER[1])
    cv.rect(wn, cx + 1, 13, cx + 6, 13, AZER[0])
    pl = cv.part(sep=False)
    cv.rect(pl, cx + 2, 13, cx + 4, 15, SKIN[1])
    cv.rect(pl, cx + 2, 13, cx + 4, 13, LEATHER[1])
    cv.pix(pl, [(cx + 3, 14), (cx + 4, 14)], DARK)
    gn = cv.part()                                                                     # guns
    cv.rect(gn, cx + 7, 19, cx + 14, 19, IRON[0])
    cv.rect(gn, cx + 6, 20, cx + 12, 20, IRON[2])
    sk = cv.part()                                                                     # skids
    cv.pix(sk, [(cx - 4, 21), (cx + 3, 21)], IRON[1])
    cv.rect(sk, cx - 7, 22, cx + 6, 22, IRON[0])


# ================================================================ hero
def lightbringer(cv, cx=MID_X - 2, fy=FY):
    """Paladin hero: the Paladin on a barded charger, with a long cape, a crowned helm and a great shining hammer."""
    cv.shadow(cx + 1, 14)
    back = horse(cv, cx, fy, GREYH)
    caparison(cv, cx, back)
    chanfron(cv, cx, back, GOLD)
    cp = cv.part(2)
    cv.rows(cp, [(back - 8, cx - 7, cx - 3), (back - 7, cx - 8, cx - 3)] + [(y, cx - 9, cx - 3) for y in range(back - 6, back + 1)] + [(back + 1, cx - 10, cx - 5)],
            lit(TINT, dark_from=cx - 4, light_to=cx - 7, light_rows=back - 4))
    ct = cv.part(1, sep=False)
    cv.rect(ct, cx - 10, back + 1, cx - 5, back + 1, TINT[1])
    lx = cx + 9
    pole(cv, lx, 8, back - 1, GOLD)
    hm = cv.part()
    cv.rect(hm, lx - 4, 2, lx + 4, 7, lit(GOLD, dark_from=lx + 3, light_to=lx - 3, light_rows=4))
    cv.rect(hm, lx - 4, 7, lx + 4, 7, GOLD[2])
    gl = cv.part(sep=False)
    cv.rect(gl, lx - 2, 3, lx + 2, 6, GLOW[1])
    cv.rect(gl, lx - 1, 4, lx + 1, 5, GLOW[0])
    ry = cv.part()
    cv.pix(ry, [(lx - 6, 1), (lx + 6, 1), (lx - 7, 5), (lx + 7, 5), (lx + 6, 9), (lx - 6, 9)], GLOW[1])
    ht = rider(cv, cx, back, torso_r=STEEL, layer=0, belt_layer=1)
    tb = cv.part(2, sep=False)
    cv.rect(tb, cx - 1, back - 8, cx + 1, back - 3, TINT[0])
    rein_arm(cv, cx, back, STEEL)
    great_helm(cv, cx, ht)
    cw = cv.part()
    cv.rows(cw, [(ht - 1, cx - 3, cx + 3)], GOLD[1])
    cv.pix(cw, [(cx - 3, ht - 2), (cx - 1, ht - 2), (cx + 1, ht - 2), (cx + 3, ht - 2)], GOLD[0])
    pauldron(cv, cx - 9, back - 10, GOLD, w=6)
    pauldron(cv, cx + 3, back - 10, GOLD, w=6)
    fist(cv, lx - 1, back - 5, IRON)


UA.SPRITES.update({
    "Fishing Skiff-Humans": skiff, "Longboat-Humans": longboat, "Brigantine-Humans": brigantine, "Buccaneer-Humans": buccaneer,
    "War Galley-Humans": war_galley, "Frigate-Humans": frigate, "Ironclad-Humans": ironclad, "Destroyer-Humans": destroyer,
    "Dreadnought-Humans": dreadnought, "Juggernaught-Humans": juggernaught, "Great Admiral-Humans": admiral, "Giant Turtle": giant_turtle,
    "Demolisher": demolisher, "War Golem": war_golem, "Siege Engine": siege_engine, "Mechano-Tank": mechano_tank, "Iron Colossus": iron_colossus,
    "Airship Tender": airship_tender, "Flying Machine": flying_machine,
    "Uther the Lightbringer": lightbringer,
})
