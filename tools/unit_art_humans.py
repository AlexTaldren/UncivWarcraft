"""Hand-placed pixel sprites for the rest of the Human land units (trial).

Built on unit_art.py: the same grid, ramps, outline and layer rules. Every unit here is
an original design. What tells the units apart is silhouette first (headgear, weapon,
shield, mount), then where the nation's colours sit.
"""
from unit_art import *          # noqa: F401,F403  (Canvas, ramps and the figure parts)
import unit_art as UA

GREEN = ((126, 172, 92), (76, 124, 68), (46, 80, 64))
ARCANITE = ((206, 236, 250), (124, 172, 216), (68, 98, 162))
ARCANE = ((244, 226, 255), (200, 146, 250), (132, 86, 212))
AZER = ((206, 242, 255), (92, 192, 250), (42, 112, 212))
GREYH = ((232, 232, 226), (188, 188, 192), (130, 130, 150))
BLACKH = ((100, 92, 98), (68, 62, 70), (42, 38, 50))
CLOTHD = ((98, 90, 104), (66, 60, 76), (42, 38, 52))
FUR = ((170, 140, 104), (124, 96, 72), (82, 60, 52))
FLAME = ((255, 244, 160), (255, 176, 64), (224, 96, 44))
RED = ((236, 110, 90), (190, 60, 56), (126, 36, 52))
STRING = (238, 234, 222)
SMOKE = ((226, 226, 230), (186, 186, 196), (150, 150, 166))

T = 23                      # head top is fy - T


# ---------------------------------------------------------------- body
def base(cv, cx, fy, legs_r=LEATHER, torso_r=TAN, boots_r=LEATHER, layer=0, belt_r=LEATHER, neck=True):
    boots(cv, cx, fy, boots_r)
    legs(cv, cx, fy, legs_r)
    t = torso(cv, cx, fy, torso_r, layer, top=fy - 16 if neck else None)
    belt(cv, cx, fy, belt_r)
    return t


def tabard(cv, cx, fy, layer=2, split=False, top=None):
    """Tabard over the body; split = right half in the inner colour."""
    top = fy - 15 if top is None else top
    tb = cv.part(layer)
    cv.rect(tb, cx - 4, top, cx + 4, fy - 7, lit(TINT, dark_from=cx + 3, light_to=cx - 3, light_rows=fy - 12))
    cv.rows(tb, [(fy - 6, cx - 4, cx - 1), (fy - 6, cx + 1, cx + 4)], TINT[2])
    if split:
        h = cv.part(1, sep=False)
        cv.rect(h, cx + 1, top, cx + 4, fy - 7, lit(TINT, dark_from=cx + 3))
        cv.rows(h, [(fy - 6, cx + 1, cx + 4)], TINT[2])
    bt = cv.part(sep=False)
    cv.rect(bt, cx - 4, fy - 9, cx + 4, fy - 9, lit(LEATHER, dark_from=cx + 3))
    bk = cv.part(0 if split else 1, sep=False)
    cv.put(bk, cx, fy - 9, GOLD[0] if split else TINT[0])


def robe(cv, cx, fy, ramp=WHITE, layer=0, top=None):
    top = fy - 15 if top is None else top
    rb = cv.part(layer)
    rows = [(y, cx - 4, cx + 4) for y in range(top, fy - 7)] + [(y, cx - 5, cx + 5) for y in range(fy - 7, fy - 2)] + \
           [(fy - 2, cx - 6, cx + 6), (fy - 1, cx - 6, cx + 6), (fy, cx - 6, cx + 6)]
    cv.rows(rb, rows, lit(ramp, dark_from=cx + 3, light_to=cx - 3, light_rows=fy - 4))
    cv.rows(rb, [(fy, cx - 6, cx + 6)], ramp[2])
    return rb


def robe_trim(cv, cx, fy, layer=1, stole=True, hem=True):
    s = cv.part(layer, sep=False)
    if stole:
        cv.rect(s, cx - 1, fy - 13, cx + 1, fy - 3, lit(TINT, dark_from=cx + 1, light_to=cx - 1, light_rows=fy - 8))
    if hem:
        cv.rect(s, cx - 6, fy - 1, cx + 6, fy - 1, lit(TINT, dark_from=cx + 4))


def mantle(cv, cx, fy, layer=2, ramp=TINT, clasp=1):
    m = cv.part(layer)
    cv.rows(m, [(fy - 16, cx - 5, cx + 5), (fy - 15, cx - 6, cx + 6), (fy - 14, cx - 6, cx + 6), (fy - 13, cx - 5, cx + 5)],
            lit(ramp, dark_from=cx + 4, light_to=cx - 3, light_rows=fy - 15))
    if clasp is not None:
        t = cv.part(clasp, sep=False)
        cv.put(t, cx, fy - 14, TINT[0] if clasp else GOLD[0])


def cape(cv, cx, fy, layer=2, ramp=TINT, length=8):
    """A cape down the back. Draw it before the body."""
    cp = cv.part(layer)
    cv.rows(cp, [(y, cx - 6, cx - 3) for y in range(fy - 15, fy - 15 + length)] + [(fy - 15 + length, cx - 6, cx - 4)],
            lit(ramp, dark_from=cx - 4, light_to=cx - 6, light_rows=fy - 12))


def hang(cv, x, fy, ramp, layer=0, hand=SKIN):
    arm(cv, x, fy - 14, ramp, length=5, layer=layer, hand_ramp=hand)


def back_grip(cv, cx, fy, ramp, hand=SKIN, layer=0):
    """Back arm holding something upright at cx-9 (as the footman holds his sword)."""
    arm(cv, cx - 8, fy - 15, ramp, length=3, hand=False, layer=layer)
    fist(cv, cx - 10, fy - 12, hand)


def front_reach(cv, cx, fy, ramp, tx, hand=SKIN, fore=None, layer=0, low=False):
    """Front arm reaching out to a haft at column tx."""
    arm(cv, cx + 4, fy - 14, ramp, length=3, hand=False, layer=layer)
    f = cv.part()
    cv.rect(f, cx + 5, fy - 11, tx - 2, fy - 10, (fore or hand)[1])
    fist(cv, tx - 1, fy - 12, hand)
    if low:
        fist(cv, tx - 1, fy - 8, hand)


# ---------------------------------------------------------------- heads
def great_helm(cv, cx, top, ramp=STEEL):
    hm = cv.part()
    cv.rows(hm, [(top - 1, cx - 2, cx + 2)] + [(y, cx - 3, cx + 3) for y in range(top, top + 7)],
            lit(ramp, dark_from=cx + 2, light_to=cx - 2, light_rows=top + 1))
    v = cv.part(sep=False)
    cv.rect(v, cx - 1, top + 3, cx + 3, top + 3, DARK)
    cv.rect(v, cx + 1, top + 4, cx + 1, top + 6, ramp[2])


def crest(cv, cx, top, layer=1):
    cr = cv.part(layer)
    cv.rows(cr, [(top - 3, cx - 2, cx), (top - 2, cx - 3, cx + 1), (top - 1, cx - 4, cx - 3), (top, cx - 4, cx - 4)],
            lit(TINT, dark_from=cx, light_to=cx - 2, light_rows=top - 3))


def plume(cv, cx, top, layer=1):
    pl = cv.part(layer)
    cv.rows(pl, [(top - 3, cx - 3, cx - 1), (top - 2, cx - 5, cx), (top - 1, cx - 6, cx - 3), (top, cx - 6, cx - 4), (top + 1, cx - 6, cx - 5)],
            lit(TINT, dark_from=cx - 1, light_to=cx - 3, light_rows=top - 2))


def tall_plume(cv, cx, top, layer=1):
    pl = cv.part(layer)
    cv.rows(pl, [(top - 5, cx - 1, cx + 1), (top - 4, cx - 2, cx + 1), (top - 3, cx - 2, cx + 1), (top - 2, cx - 1, cx + 1)],
            lit(TINT, dark_from=cx + 1, light_to=cx - 1, light_rows=top - 4))


def open_helm(cv, cx, top, ramp=STEEL, skin=SKIN, nasal=False):
    head(cv, cx, top, skin)
    h = cv.part()
    cv.rows(h, [(top - 1, cx - 2, cx + 2), (top, cx - 3, cx + 3), (top + 1, cx - 3, cx + 3), (top + 2, cx - 3, cx - 1),
                (top + 3, cx - 3, cx - 2), (top + 4, cx - 3, cx - 2), (top + 5, cx - 3, cx - 3)],
            lit(ramp, dark_from=cx + 2, light_to=cx - 1, light_rows=top))
    if nasal:
        n = cv.part(sep=False)
        cv.rect(n, cx + 1, top + 2, cx + 1, top + 4, ramp[1])


def kettle(cv, cx, top, ramp=STEEL, skin=SKIN):
    head(cv, cx, top, skin)
    h = cv.part()
    cv.rows(h, [(top - 2, cx - 2, cx + 2), (top - 1, cx - 3, cx + 3), (top, cx - 3, cx + 3)],
            lit(ramp, dark_from=cx + 2, light_to=cx - 1, light_rows=top - 1))
    cv.rows(h, [(top + 1, cx - 5, cx + 5)], lit(ramp, dark_from=cx + 3, light_to=cx - 2))


def hood(cv, cx, top, layer=2, ramp=TINT, shoulders=True):
    hs = head(cv, cx, top)
    cv.rows(hs, [(y, cx - 1, cx + 2) for y in range(top + 2, top + 5)], SKIN[0])
    e = cv.part(sep=False)
    cv.pix(e, [(cx, top + 3), (cx + 2, top + 3)], DARK)
    hd = cv.part(layer)
    ht = top - 1
    rows = [(ht - 1, cx - 2, cx + 1), (ht, cx - 3, cx + 2), (ht + 1, cx - 4, cx + 3), (ht + 2, cx - 4, cx - 1), (ht + 3, cx - 4, cx - 2),
            (ht + 4, cx - 4, cx - 2), (ht + 5, cx - 4, cx - 2), (ht + 6, cx - 4, cx - 3)]
    if shoulders:
        rows += [(ht + 7, cx - 5, cx - 2), (ht + 8, cx - 5, cx + 4)]
    cv.rows(hd, rows, lit(ramp, dark_from=cx + 2, light_to=cx - 2, light_rows=ht + 1))


def hair(cv, cx, top, ramp=HAIR, long=False):
    hr = cv.part(sep=False)
    rows = [(top, cx - 2, cx + 2), (top + 1, cx - 3, cx + 2), (top + 2, cx - 3, cx - 2), (top + 3, cx - 3, cx - 3), (top + 4, cx - 3, cx - 3)]
    cv.rows(hr, rows, lit(ramp, dark_from=cx + 1, light_to=cx - 1, light_rows=top))
    if long:
        lg = cv.part()
        cv.rows(lg, [(y, cx - 4, cx - 3) for y in range(top + 2, top + 10)], lit(ramp, dark_from=cx - 3))


def beard(cv, cx, top, ramp=HAIR, long=False):
    b = cv.part(sep=False)
    cv.rows(b, [(top + 4, cx - 1, cx + 3), (top + 5, cx - 3, cx + 3), (top + 6, cx - 2, cx + 2)], lit(ramp, dark_from=cx + 2))
    cv.pix(b, [(cx - 3, top + 3), (cx - 3, top + 4)], ramp[1])
    if long:
        lb = cv.part()
        cv.rows(lb, [(top + 7, cx - 1, cx + 3), (top + 8, cx - 1, cx + 3), (top + 9, cx, cx + 3), (top + 10, cx, cx + 2), (top + 11, cx + 1, cx + 2)],
                lit(ramp, dark_from=cx + 3, light_to=cx))


def brim_hat(cv, cx, top, ramp=LEATHER, layer=0, crown=3, brim=6):
    h = cv.part(layer)
    cv.rows(h, [(top - crown + 1, cx - 2, cx + 2)] + [(y, cx - 3, cx + 3) for y in range(top - crown + 2, top + 1)],
            lit(ramp, dark_from=cx + 2, light_to=cx - 1, light_rows=top - crown + 2))
    cv.rows(h, [(top + 1, cx - brim, cx + brim)], lit(ramp, dark_from=cx + brim - 2, light_to=cx - 2))
    return h


def feather(cv, x, y, layer=1):
    f = cv.part(layer)
    cv.pix(f, [(x, y), (x - 1, y - 1), (x - 1, y - 2), (x - 2, y - 2), (x - 2, y - 3)], TINT[0])
    cv.pix(f, [(x, y - 1)], TINT[1])


def goggles(cv, cx, top):
    g = cv.part(sep=False)
    cv.rect(g, cx - 3, top + 1, cx + 3, top + 1, LEATHER[2])
    cv.pix(g, [(cx, top + 1), (cx + 2, top + 1)], AZER[0])


# ---------------------------------------------------------------- gear
def pole(cv, x, y0, y1, ramp=WOOD):
    s = cv.part()
    cv.rect(s, x, y0, x, y1, ramp[1])
    cv.rect(s, x, y0, x, (y0 + y1) // 2, ramp[0])
    return s


def spear_head(cv, x, y, ramp=STEEL):
    """Leaf blade, tip at row y, four rows tall."""
    h = cv.part()
    cv.rows(h, [(y, x, x), (y + 1, x - 1, x + 1), (y + 2, x - 1, x + 1), (y + 3, x, x)], lit(ramp, dark_from=x + 1, light_to=x - 1))


def pennant(cv, x, y, layer=2, n=7):
    pn = cv.part(layer)
    cv.rows(pn, [(y, x + 1, x + n), (y + 1, x + 1, x + n - 1), (y + 2, x + 1, x + n), (y + 3, x + 1, x + n - 3)],
            lit(TINT, dark_from=x + n - 2, light_to=x + 3, light_rows=y + 1))
    pt = cv.part(3 - layer, sep=False)
    cv.rect(pt, x + 1, y, x + 1, y + 3, TINT[0])


def banner(cv, x0, y, w=8, h=10):
    """A hanging war banner: outer colour, inner band, swallow tail."""
    b = cv.part(2)
    rows = [(yy, x0, x0 + w - 1) for yy in range(y, y + h - 2)] + [(y + h - 2, x0, x0 + w // 2 - 2), (y + h - 2, x0 + w // 2 + 1, x0 + w - 1),
                                                                    (y + h - 1, x0, x0 + w // 2 - 3), (y + h - 1, x0 + w // 2 + 2, x0 + w - 1)]
    cv.rows(b, rows, lit(TINT, dark_from=x0 + w - 2, light_to=x0 + 1, light_rows=y + h - 4))
    t = cv.part(1, sep=False)
    cv.rect(t, x0, y + 1, x0 + w - 1, y + 2, lit(TINT, dark_from=x0 + w - 2))
    cv.rect(t, x0 + w // 2 - 1, y + 4, x0 + w // 2, y + 5, TINT[0])
    bar = cv.part()
    cv.rect(bar, x0 - 1, y - 1, x0 + w, y - 1, WOOD[1])


def sword_up(cv, x, tip, gy, ramp=STEEL, guard=1, guard_ramp=TINT):
    bl = cv.part()
    cv.rect(bl, x, tip + 1, x + 1, gy - 1, lit(ramp, dark_from=x + 1))
    cv.put(bl, x, tip, ramp[0])
    g = cv.part(guard)
    cv.rect(g, x - 2, gy, x + 3, gy, lit(guard_ramp, dark_from=x + 2))
    cv.rect(g, x, gy + 4, x + 1, gy + 4, guard_ramp[1])


def round_shield(cv, x, top, layer=2, rim=WOOD, boss=1):
    """A 9x9 round shield."""
    rows = [(top, x + 3, x + 5), (top + 1, x + 1, x + 7), (top + 2, x + 1, x + 7), (top + 3, x, x + 8), (top + 4, x, x + 8),
            (top + 5, x, x + 8), (top + 6, x + 1, x + 7), (top + 7, x + 1, x + 7), (top + 8, x + 3, x + 5)]
    r = cv.part()
    cv.rows(r, rows, lit(rim, dark_from=x + 6, light_to=x + 2, light_rows=top + 3))
    f = cv.part(layer, sep=False)
    cv.rows(f, [(top + 1, x + 3, x + 5), (top + 2, x + 2, x + 6), (top + 3, x + 1, x + 7), (top + 4, x + 1, x + 7), (top + 5, x + 1, x + 7),
                (top + 6, x + 2, x + 6), (top + 7, x + 3, x + 5)], lit(TINT, dark_from=x + 6, light_to=x + 2, light_rows=top + 3))
    b = cv.part(boss, sep=False)
    cv.rect(b, x + 3, top + 3, x + 5, top + 5, TINT[1] if boss else STEEL[1])
    cv.put(b, x + 4, top + 4, TINT[0] if boss else STEEL[0])


def tower(cv, x, top, w=9, h=16, stud=1):
    """A tall tower shield: outer colour, chief and stud in the inner colour, steel foot."""
    sh = cv.part(2)
    rows = [(top, x + 1, x + w - 2)] + [(y, x, x + w - 1) for y in range(top + 1, top + h - 1)] + [(top + h - 1, x + 1, x + w - 2)]
    cv.rows(sh, rows, lit(TINT, dark_from=x + w - 3, light_to=x + 2, light_rows=top + h - 5))
    ch = cv.part(1, sep=False)
    cv.rows(ch, [(top, x + 1, x + w - 2), (top + 1, x, x + w - 1), (top + 2, x, x + w - 1)], lit(TINT, dark_from=x + w - 3))
    if stud == 1:
        cv.rect(ch, x + w // 2 - 1, top + 6, x + w // 2 + 1, top + 8, TINT[0])
    ft = cv.part(sep=False)
    cv.rows(ft, [(top + h - 2, x, x + w - 1), (top + h - 1, x + 1, x + w - 2)], lit(STEEL, dark_from=x + w - 3))
    if stud == 0:
        cv.rect(ft, x + w // 2 - 1, top + 6, x + w // 2 + 1, top + 8, ARCANE[1])
        cv.put(ft, x + w // 2, top + 7, ARCANE[0])


def bow(cv, cx, by, sleeve=LEATHER, wood=WOOD, h=9, hand=SKIN, layer=0):
    """Bow held out in front, string drawn to the chest, arrow across (as the archer)."""
    bx = cx + 11
    sg = cv.part(sep=False)
    cv.pix(sg, line(bx - 2, by - h, cx + 3, by - 1) + line(cx + 3, by - 1, bx - 2, by + h), STRING)
    bw = cv.part()
    arc = [(bx - 2, by - h), (bx - 1, by - h + 1), (bx, by - h + 2), (bx, by - h + 3)] + [(bx + 1, y) for y in range(by - h + 4, by + h - 3)] + \
          [(bx, by + h - 3), (bx, by + h - 2), (bx - 1, by + h - 1), (bx - 2, by + h)]
    cv.pix(bw, arc, wood[1])
    cv.pix(bw, arc[:len(arc) // 2 - 2], wood[0])
    sl = cv.part(layer)
    cv.rect(sl, cx + 4, by, bx - 3, by + 1, lit(sleeve, dark_from=bx - 4, light_to=bx - 5, light_rows=by))
    ar = cv.part()
    cv.rect(ar, cx + 4, by - 1, bx + 1, by - 1, WOOD[0])
    cv.pix(ar, [(bx + 2, by - 1), (bx + 3, by - 1)], STEEL[0])
    fist(cv, bx - 2, by - 1, hand)
    fist(cv, cx + 1, by - 1, hand)


def quiver(cv, cx, fy, layer=1):
    q = cv.part()
    cv.rect(q, cx - 8, fy - 19, cx - 6, fy - 14, lit(LEATHER, dark_from=cx - 6, light_to=cx - 8))
    fl = cv.part(layer, sep=False)
    cv.rect(fl, cx - 8, fy - 20, cx - 6, fy - 20, lit(TINT, dark_from=cx - 6))
    ft = cv.part()
    cv.pix(ft, [(cx - 8, fy - 21), (cx - 6, fy - 21)], WHITE[0])


def gun(cv, x0, y, length=16, barrel=IRON, wood=WOOD, bayonet=False, bell=False, scope=False, glow=None):
    """A long gun pointing right: butt at x0, barrel along row y."""
    st = cv.part()
    cv.rows(st, [(y, x0, x0 + 3), (y + 1, x0, x0 + 3), (y + 2, x0, x0 + 1)], lit(wood, dark_from=x0 + 3, light_to=x0 + 1, light_rows=y))
    cv.rect(st, x0 + 4, y + 1, x0 + length - 5, y + 1, wood[1])
    br = cv.part()
    cv.rect(br, x0 + 4, y, x0 + length, y, barrel[0])
    cv.rect(br, x0 + length - 4, y + 1, x0 + length, y + 1, barrel[2])
    if bell:
        cv.rect(br, x0 + length - 1, y - 1, x0 + length, y + 2, barrel[1])
        cv.rect(br, x0 + length, y - 1, x0 + length, y + 2, barrel[0])
    if bayonet:
        b = cv.part()
        cv.rect(b, x0 + length + 1, y, x0 + length + 3, y, STEEL[0])
    if scope:
        s = cv.part()
        cv.rect(s, x0 + 5, y - 2, x0 + 10, y - 2, GOLD[1])
        cv.pix(s, [(x0 + 6, y - 1), (x0 + 9, y - 1)], GOLD[2])
        cv.put(s, x0 + 10, y - 2, AZER[0])
    if glow:
        g = cv.part(sep=False)
        cv.rect(g, x0 + 4, y, x0 + 6, y + 1, glow[1])
        cv.put(g, x0 + 5, y, glow[0])
        cv.put(g, x0 + length, y, glow[0])


def gun_arms(cv, cx, y, sleeve, hand=SKIN, layer=0):
    sl = cv.part(layer)
    cv.rect(sl, cx + 4, y + 2, cx + 6, y + 3, lit(sleeve, dark_from=cx + 6, light_to=cx + 4, light_rows=y + 2))
    fist(cv, cx + 7, y + 1, hand)
    fist(cv, cx, y + 1, hand)


def wheel(cv, wx, fy):
    """A 9-px spoked wheel with an iron tyre (as on the catapult)."""
    wh = cv.part()
    rows = [(fy - 8, wx - 2, wx + 2), (fy - 7, wx - 3, wx + 3)] + [(y, wx - 4, wx + 4) for y in range(fy - 6, fy - 1)] + \
           [(fy - 1, wx - 3, wx + 3), (fy, wx - 2, wx + 2)]
    cv.rows(wh, rows, IRON[1])
    cv.rows(wh, [(fy - 8, wx - 2, wx + 2), (fy - 7, wx - 3, wx - 2), (fy - 6, wx - 4, wx - 3)], IRON[0])
    cv.rows(wh, [(fy, wx - 2, wx + 2), (fy - 1, wx + 2, wx + 3), (fy - 2, wx + 4, wx + 4)], IRON[2])
    inn = cv.part(sep=False)
    cv.rows(inn, [(fy - 6, wx - 2, wx + 2), (fy - 5, wx - 3, wx + 3), (fy - 4, wx - 3, wx + 3), (fy - 3, wx - 3, wx + 3), (fy - 2, wx - 2, wx + 2)],
            lit(WOOD, dark_from=wx + 2, light_to=wx - 2, light_rows=fy - 5))
    cv.rect(inn, wx - 3, fy - 4, wx + 3, fy - 4, WOOD[2])
    cv.rect(inn, wx, fy - 6, wx, fy - 2, WOOD[2])
    cv.put(inn, wx, fy - 4, IRON[0])


def iron_wheel(cv, wx, fy):
    w = cv.part()
    cv.rows(w, [(fy - 6, wx - 1, wx + 1), (fy - 5, wx - 2, wx + 2), (fy - 4, wx - 3, wx + 3), (fy - 3, wx - 3, wx + 3), (fy - 2, wx - 3, wx + 3),
                (fy - 1, wx - 2, wx + 2), (fy, wx - 1, wx + 1)], lit(IRON, dark_from=wx + 2, light_to=wx - 2, light_rows=fy - 4))
    h = cv.part(sep=False)
    cv.rect(h, wx - 1, fy - 4, wx + 1, fy - 2, IRON[2])
    cv.put(h, wx, fy - 3, STEEL[0])


# ================================================================ civilians (left of the tile)
def settler(cv, cx=CIV_X + 1, fy=FY):
    """Pioneer: straw hat, heavy pack with a bedroll, a pole with the nation's pennant to plant."""
    cv.shadow(cx, 8)
    pk = cv.part()                                                                     # pack
    cv.rect(pk, cx - 9, fy - 16, cx - 5, fy - 8, lit(LEATHER, dark_from=cx - 6, light_to=cx - 8, light_rows=fy - 13))
    cv.rect(pk, cx - 9, fy - 12, cx - 5, fy - 12, LEATHER[2])
    br = cv.part(1)                                                                    # bedroll: inner colour
    cv.rect(br, cx - 10, fy - 19, cx - 5, fy - 17, lit(TINT, dark_from=cx - 6, light_to=cx - 9, light_rows=fy - 19))
    base(cv, cx, fy, legs_r=LEATHER, torso_r=TINT, layer=2)
    st = cv.part(sep=False)                                                            # pack strap
    cv.rect(st, cx - 3, fy - 16, cx - 3, fy - 9, LEATHER[2])
    head(cv, cx, fy - T)
    beard(cv, cx, fy - T, HAIR)
    brim_hat(cv, cx, fy - T - 1, BLOND, crown=3, brim=6)
    tx = cx + 8
    pole(cv, tx, fy - 28, fy)
    pennant(cv, tx, fy - 28, layer=2, n=6)
    front_reach(cv, cx, fy, TINT, tx, layer=2)


def great_artist(cv, cx=CIV_X, fy=FY):
    """Painter at an easel: beret, smock, brush on the canvas."""
    cv.shadow(cx + 3, 11)
    hang(cv, cx - 6, fy, WHITE)
    ex = cx + 9                                                                        # easel
    lg = cv.part()
    cv.pix(lg, line(ex + 1, fy - 10, ex, fy) + line(ex + 5, fy - 10, ex + 6, fy) + line(ex + 3, fy - 22, ex + 3, fy - 3), WOOD[2])
    cn = cv.part()
    cv.rect(cn, ex, fy - 21, ex + 6, fy - 11, WOOD[1])
    p = cv.part(sep=False)
    cv.rect(p, ex + 1, fy - 20, ex + 5, fy - 12, WHITE[0])
    cv.rect(p, ex + 1, fy - 15, ex + 5, fy - 12, WHITE[1])
    d2 = cv.part(2, sep=False)
    cv.rows(d2, [(fy - 16, ex + 2, ex + 4), (fy - 15, ex + 1, ex + 5), (fy - 14, ex + 1, ex + 5)], TINT[0])
    d1 = cv.part(1, sep=False)
    cv.rect(d1, ex + 3, fy - 19, ex + 4, fy - 18, TINT[0])
    base(cv, cx, fy, legs_r=CLOTHD, torso_r=WHITE)
    sc = cv.part(1, sep=False)                                                         # neckerchief
    cv.rows(sc, [(fy - 16, cx - 3, cx + 3), (fy - 15, cx - 1, cx + 2), (fy - 14, cx, cx + 1)], TINT[0])
    head(cv, cx, fy - T)
    hair(cv, cx, fy - T, HAIR)
    bt = cv.part(2)                                                                    # beret
    cv.rows(bt, [(fy - T - 2, cx - 3, cx + 1), (fy - T - 1, cx - 5, cx + 3), (fy - T, cx - 5, cx + 3)],
            lit(TINT, dark_from=cx + 2, light_to=cx - 2, light_rows=fy - T - 2))
    arm(cv, cx + 4, fy - 15, WHITE, length=3, hand=False)
    fist(cv, cx + 5, fy - 15)
    b = cv.part()                                                                      # brush
    cv.rect(b, cx + 8, fy - 15, cx + 9, fy - 15, WOOD[0])


def great_merchant(cv, cx=CIV_X, fy=FY):
    """Stout trader: plumed hat, long coat with a fur collar, purse in hand, strongbox at his feet."""
    cv.shadow(cx + 3, 11)
    hang(cv, cx - 7, fy, TINT, layer=2)
    bx = cx + 9                                                                        # strongbox
    ch = cv.part()
    cv.rect(ch, bx, fy - 6, bx + 7, fy, lit(WOOD, dark_from=bx + 6, light_to=bx + 1, light_rows=fy - 5))
    bd = cv.part(sep=False)
    cv.rect(bd, bx, fy - 4, bx + 7, fy - 4, GOLD[1])
    cv.rect(bd, bx + 3, fy - 4, bx + 4, fy - 3, GOLD[0])
    co = cv.part()
    cv.rows(co, [(fy - 8, bx + 2, bx + 5), (fy - 7, bx + 1, bx + 6)], lit(GOLD, dark_from=bx + 5, light_to=bx + 2))
    boots(cv, cx, fy)
    legs(cv, cx, fy, CLOTHD)
    ct = cv.part(2)                                                                    # coat
    cv.rows(ct, [(y, cx - 5, cx + 5) for y in range(fy - 15, fy - 3)], lit(TINT, dark_from=cx + 4, light_to=cx - 4, light_rows=fy - 10))
    cv.rows(ct, [(fy - 3, cx - 5, cx - 1), (fy - 3, cx + 1, cx + 5)], TINT[2])
    bn = cv.part(sep=False)
    cv.pix(bn, [(cx, fy - 12), (cx, fy - 10), (cx, fy - 8), (cx, fy - 6)], GOLD[0])
    cl = cv.part()                                                                     # fur collar
    cv.rows(cl, [(fy - 16, cx - 5, cx + 5), (fy - 15, cx - 6, cx + 6), (fy - 14, cx - 6, cx - 2), (fy - 14, cx + 2, cx + 6)],
            lit(WHITE, dark_from=cx + 4, light_to=cx - 3, light_rows=fy - 16))
    head(cv, cx, fy - T)
    beard(cv, cx, fy - T, HAIR)
    h = cv.part(2)                                                                     # flat cap
    cv.rows(h, [(fy - T - 2, cx - 3, cx + 2), (fy - T - 1, cx - 5, cx + 4), (fy - T, cx - 5, cx + 5)],
            lit(TINT, dark_from=cx + 3, light_to=cx - 2, light_rows=fy - T - 2))
    feather(cv, cx - 3, fy - T - 2)
    arm(cv, cx + 4, fy - 14, TINT, length=3, hand=False, layer=2)
    fist(cv, cx + 5, fy - 11)
    pr = cv.part()                                                                     # purse
    cv.rows(pr, [(fy - 9, cx + 6, cx + 7), (fy - 8, cx + 5, cx + 8), (fy - 7, cx + 5, cx + 8)], lit(TAN, dark_from=cx + 8, light_to=cx + 5))


def great_engineer(cv, cx=CIV_X + 1, fy=FY):
    """Engineer: goggles pushed up, leather apron, a wrench as tall as he is, plans under his arm."""
    cv.shadow(cx, 8)
    arm(cv, cx - 6, fy - 14, TINT, length=3, layer=2)
    pl = cv.part()                                                                     # rolled plans
    cv.rect(pl, cx - 10, fy - 10, cx - 4, fy - 9, lit(WHITE, dark_from=cx - 5, light_to=cx - 9, light_rows=fy - 10))
    cv.pix(pl, [(cx - 10, fy - 10), (cx - 10, fy - 9)], AZER[1])
    base(cv, cx, fy, legs_r=CLOTHD, torso_r=TINT, layer=2)
    a = cv.part()
    cv.rect(a, cx - 2, fy - 13, cx + 2, fy - 5, lit(LEATHER, dark_from=cx + 2, light_to=cx - 2, light_rows=fy - 10))
    pk = cv.part(1, sep=False)
    cv.rect(pk, cx - 1, fy - 10, cx + 1, fy - 9, TINT[1])
    head(cv, cx, fy - T)
    hair(cv, cx, fy - T, ((214, 130, 70), (170, 88, 50), (112, 56, 44)))
    goggles(cv, cx, fy - T)
    tx = cx + 8                                                                        # wrench
    w = cv.part()
    cv.rect(w, tx, fy - 21, tx, fy - 1, lit(STEEL, light_to=tx, light_rows=fy - 12))
    cv.rows(w, [(fy - 25, tx - 2, tx - 2), (fy - 25, tx + 2, tx + 2), (fy - 24, tx - 2, tx - 1), (fy - 24, tx + 1, tx + 2),
                (fy - 23, tx - 2, tx + 2), (fy - 22, tx - 1, tx + 1)], lit(STEEL, dark_from=tx + 2, light_to=tx - 1))
    front_reach(cv, cx, fy, TINT, tx, layer=2)


def great_prophet(cv, cx=CIV_X + 1, fy=FY):
    """Prophet: long robe in the nation's colour, beard to the belt, a halo, a shepherd's crook."""
    cv.shadow(cx, 8)
    robe(cv, cx, fy, TINT, layer=2)
    robe_trim(cv, cx, fy, 1, stole=False)
    arm(cv, cx - 6, fy - 14, TINT, length=5, layer=2)
    cf = cv.part(1, sep=False)
    cv.rect(cf, cx - 6, fy - 10, cx - 4, fy - 10, TINT[1])
    mantle(cv, cx, fy, layer=0, ramp=WHITE, clasp=None)
    head(cv, cx, fy - T)
    beard(cv, cx, fy - T, WHITE, long=True)
    hr = cv.part(sep=False)
    cv.pix(hr, [(cx - 3, fy - T + 1), (cx - 3, fy - T + 2), (cx - 2, fy - T)], WHITE[1])
    hl = cv.part()                                                                     # halo
    cv.rows(hl, [(fy - T - 3, cx - 2, cx + 2)], GLOW[1])
    cv.pix(hl, [(cx - 3, fy - T - 2), (cx + 3, fy - T - 2)], GLOW[2])
    tx = cx + 9                                                                        # crook
    pole(cv, tx, fy - 24, fy)
    ck = cv.part()
    cv.rows(ck, [(fy - 27, tx + 1, tx + 3), (fy - 26, tx, tx), (fy - 26, tx + 4, tx + 4), (fy - 25, tx, tx), (fy - 25, tx + 4, tx + 4),
                 (fy - 24, tx + 3, tx + 4)], lit(GOLD, dark_from=tx + 4, light_to=tx + 1))
    front_reach(cv, cx, fy, TINT, tx, layer=2)


def great_general(cv, cx=CIV_X + 1, fy=FY):
    """Commander: plate with gold shoulders, long cape, plumed helm, sword levelled at the enemy."""
    cv.shadow(cx + 1, 9)
    cape(cv, cx, fy, 2, length=12)
    boots(cv, cx, fy, IRON)
    legs(cv, cx, fy, STEEL)
    torso(cv, cx, fy, STEEL, top=fy - 16)
    s = cv.part(1, sep=False)                                                          # sash
    cv.pix(s, line(cx - 4, fy - 15, cx + 4, fy - 9) + line(cx - 4, fy - 14, cx + 4, fy - 8), TINT[0])
    belt(cv, cx, fy, LEATHER)
    open_helm(cv, cx, fy - T, STEEL)
    b = cv.part(sep=False)
    cv.rows(b, [(fy - T + 5, cx - 1, cx + 3)], HAIR[1])
    tall_plume(cv, cx - 1, fy - T, 1)
    pauldron(cv, cx - 8, fy - 17, GOLD)
    y = fy - 15                                                                        # sword arm, straight out
    bl = cv.part()
    cv.rect(bl, cx + 11, y, cx + 20, y + 1, lit(STEEL, light_to=cx + 20, light_rows=y))
    cv.put(bl, cx + 21, y, STEEL[0])
    g = cv.part(1)
    cv.rect(g, cx + 10, y - 2, cx + 10, y + 3, TINT[0])
    sl = cv.part()
    cv.rect(sl, cx + 3, y, cx + 6, y + 2, lit(STEEL, dark_from=cx + 6, light_to=cx + 4, light_rows=y))
    pauldron(cv, cx + 2, fy - 17, GOLD, w=4)
    fist(cv, cx + 7, y - 1, IRON)


def inquisitor(cv, cx=CIV_X + 1, fy=FY):
    """Witch-finder: tall buckled hat, dark coat, mantle in the nation's colour, book at the belt, burning torch."""
    cv.shadow(cx, 8)
    robe(cv, cx, fy, CLOTHD)
    arm(cv, cx - 6, fy - 14, CLOTHD, length=5)
    bk = cv.part(1)                                                                    # book at the hip
    cv.rect(bk, cx - 4, fy - 7, cx - 1, fy - 3, lit(TINT, dark_from=cx - 1, light_to=cx - 4, light_rows=fy - 6))
    pg = cv.part(sep=False)
    cv.rect(pg, cx - 1, fy - 6, cx - 1, fy - 4, WHITE[0])
    bl = cv.part(sep=False)
    cv.rect(bl, cx - 4, fy - 8, cx + 4, fy - 8, LEATHER[1])
    mantle(cv, cx, fy, 2, clasp=0)
    head(cv, cx, fy - T)
    hair(cv, cx, fy - T, CLOTHD)
    h = brim_hat(cv, cx, fy - T - 1, CLOTHD, crown=5, brim=6)
    bd = cv.part(sep=False)
    cv.rect(bd, cx - 3, fy - T - 1, cx + 3, fy - T - 1, CLOTHD[2])
    cv.rect(bd, cx, fy - T - 1, cx + 1, fy - T - 1, GOLD[0])
    tx = cx + 9                                                                        # torch
    pole(cv, tx, fy - 20, fy - 6)
    cup = cv.part()
    cv.rect(cup, tx - 1, fy - 21, tx + 1, fy - 20, IRON[1])
    fl = cv.part()
    cv.rows(fl, [(fy - 26, tx, tx), (fy - 25, tx - 1, tx), (fy - 24, tx - 1, tx + 1), (fy - 23, tx - 2, tx + 1), (fy - 22, tx - 1, tx + 1)], FLAME[1])
    cv.pix(fl, [(tx + 1, fy - 24), (tx - 2, fy - 23), (tx + 1, fy - 22), (tx, fy - 26)], FLAME[2])
    cv.pix(fl, [(tx, fy - 24), (tx - 1, fy - 23), (tx, fy - 23), (tx, fy - 22)], FLAME[0])
    front_reach(cv, cx, fy, CLOTHD, tx)


def archmage(cv, cx=CIV_X + 1, fy=FY):
    """Archmage: pointed hat and robe in the nation's colours, white beard, staff with a floating crystal."""
    cv.shadow(cx, 8)
    robe(cv, cx, fy, TINT, layer=2)
    robe_trim(cv, cx, fy, 1)
    arm(cv, cx - 6, fy - 14, TINT, length=5, layer=2)
    mantle(cv, cx, fy, 1, clasp=None)
    head(cv, cx, fy - T)
    beard(cv, cx, fy - T, WHITE, long=True)
    top = fy - T
    h = cv.part(2)                                                                     # hat: bent point
    cv.rows(h, [(top - 6, cx - 5, cx - 3), (top - 5, cx - 5, cx - 1), (top - 4, cx - 4, cx), (top - 3, cx - 3, cx + 1), (top - 2, cx - 3, cx + 2),
                (top - 1, cx - 3, cx + 3), (top, cx - 4, cx + 4), (top + 1, cx - 6, cx + 6)],
            lit(TINT, dark_from=cx + 2, light_to=cx - 2, light_rows=top - 2))
    bd = cv.part(1, sep=False)
    cv.rect(bd, cx - 4, top, cx + 4, top, lit(TINT, dark_from=cx + 3))
    tx = cx + 9
    pole(cv, tx, fy - 21, fy)
    cl = cv.part()                                                                     # claw holding the crystal
    cv.pix(cl, [(tx - 2, fy - 22), (tx + 2, fy - 22), (tx - 1, fy - 21), (tx + 1, fy - 21), (tx - 2, fy - 23), (tx + 2, fy - 23)], GOLD[1])
    cr = cv.part()
    cv.rows(cr, [(fy - 28, tx, tx), (fy - 27, tx - 1, tx + 1), (fy - 26, tx - 1, tx + 1), (fy - 25, tx - 1, tx + 1), (fy - 24, tx, tx)],
            lit(AZER, dark_from=tx + 1, light_to=tx - 1, light_rows=fy - 26))
    front_reach(cv, cx, fy, TINT, tx, layer=2)


def cleric(cv, cx=CIV_X + 1, fy=FY):
    """Abbey cleric: plain habit with a rope belt, cowl in the nation's colour, reading from an open book."""
    cv.shadow(cx, 8)
    robe(cv, cx, fy, TAN, top=fy - 16)
    rp = cv.part(sep=False)
    cv.rect(rp, cx - 4, fy - 8, cx + 4, fy - 8, WHITE[1])
    cv.rect(rp, cx - 2, fy - 7, cx - 2, fy - 4, WHITE[1])
    arm(cv, cx - 6, fy - 14, TAN, length=3, hand=False)
    hood(cv, cx, fy - T, 2)
    arm(cv, cx + 4, fy - 14, TAN, length=3, hand=False)
    bk = cv.part(1)                                                                    # book cover: inner colour
    cv.rect(bk, cx + 4, fy - 10, cx + 10, fy - 10, lit(TINT, dark_from=cx + 9))
    pg = cv.part()
    cv.rect(pg, cx + 4, fy - 12, cx + 10, fy - 11, WHITE[0])
    cv.rect(pg, cx + 7, fy - 12, cx + 7, fy - 11, WHITE[2])
    cv.pix(pg, [(cx + 5, fy - 11), (cx + 9, fy - 11)], WHITE[1])
    fist(cv, cx + 2, fy - 10)
    gl = cv.part()
    cv.pix(gl, [(cx + 7, fy - 15), (cx + 6, fy - 17), (cx + 9, fy - 16)], GLOW[1])


# ================================================================ foot soldiers (right of the tile)
def scout(cv, cx=MIL_X - 3, fy=FY):
    """Pathfinder: feathered cap, short cloak, satchel, walking stick."""
    cv.shadow(cx, 8)
    cape(cv, cx, fy, 2, length=9)
    hang(cv, cx - 6, fy, LEATHER)
    base(cv, cx, fy, legs_r=TAN, torso_r=LEATHER)
    st = cv.part(sep=False)
    cv.pix(st, line(cx - 4, fy - 16, cx + 3, fy - 9), TAN[0])
    sa = cv.part()
    cv.rect(sa, cx + 1, fy - 8, cx + 4, fy - 5, lit(TAN, dark_from=cx + 4, light_to=cx + 1, light_rows=fy - 8))
    cl = cv.part(1, sep=False)
    cv.put(cl, cx + 2, fy - 7, TINT[0])
    head(cv, cx, fy - T)
    hair(cv, cx, fy - T, HAIR)
    top = fy - T
    c = cv.part()
    cv.rows(c, [(top - 2, cx - 2, cx + 1), (top - 1, cx - 3, cx + 3), (top, cx - 4, cx + 5)], lit(GREEN, dark_from=cx + 3, light_to=cx - 1, light_rows=top - 1))
    feather(cv, cx - 2, top - 2)
    tx = cx + 8
    pole(cv, tx, fy - 22, fy)
    front_reach(cv, cx, fy, LEATHER, tx)


def militia(cv, cx=MIL_X - 1, fy=FY):
    """Levy: no armour, tunic in the nation's colour, headband, studded club."""
    cv.shadow(cx - 1, 8)
    wx = cx - 9
    cb = cv.part()
    cv.rect(cb, wx, fy - 18, wx, fy - 9, WOOD[1])
    cv.rows(cb, [(fy - 27, wx - 1, wx + 1)] + [(y, wx - 2, wx + 2) for y in range(fy - 26, fy - 20)] + [(fy - 20, wx - 1, wx + 1), (fy - 19, wx - 1, wx + 1)],
            lit(WOOD, dark_from=wx + 2, light_to=wx - 1, light_rows=fy - 22))
    sd = cv.part(sep=False)
    cv.pix(sd, [(wx - 1, fy - 25), (wx + 1, fy - 23), (wx - 1, fy - 22)], STEEL[0])
    back_grip(cv, cx, fy, SKIN)
    base(cv, cx, fy, legs_r=LEATHER, torso_r=TINT, layer=2, belt_r=TAN)
    head(cv, cx, fy - T)
    hair(cv, cx, fy - T, HAIR)
    hb = cv.part(1, sep=False)
    cv.rect(hb, cx - 3, fy - T + 1, cx + 3, fy - T + 1, TINT[0])
    hang(cv, cx + 4, fy, SKIN)


def spearman(cv, cx=MIL_X - 1, fy=FY):
    """Spearman: leather cap, quilted jack, spear grounded at his side, round shield."""
    cv.shadow(cx, 8)
    wx = cx - 9
    pole(cv, wx, fy - 25, fy)
    spear_head(cv, wx, fy - 29)
    back_grip(cv, cx, fy, TAN)
    base(cv, cx, fy, legs_r=LEATHER, torso_r=TAN, belt_r=LEATHER)
    q = cv.part(sep=False)                                                             # quilting
    cv.pix(q, [(cx - 2, y) for y in range(fy - 14, fy - 8)] + [(cx + 1, y) for y in range(fy - 14, fy - 8)], TAN[2])
    sc = cv.part(1, sep=False)
    cv.rect(sc, cx - 4, fy - 16, cx + 4, fy - 16, TINT[0])
    open_helm(cv, cx, fy - T, LEATHER)
    round_shield(cv, cx + 1, fy - 15)


def pikeman(cv, cx=MIL_X - 1, fy=FY):
    """Pikeman: kettle hat, tabard, a pike half again his height with a pennant."""
    cv.shadow(cx, 8)
    wx = cx - 9
    pole(cv, wx, fy - 26, fy)
    spear_head(cv, wx, fy - 30)
    pennant(cv, wx, fy - 27, layer=1, n=5)
    back_grip(cv, cx, fy, STEEL, IRON)
    boots(cv, cx, fy, LEATHER)
    legs(cv, cx, fy, IRON)
    tabard(cv, cx, fy, 2, top=fy - 16)
    kettle(cv, cx, fy - T)
    hang(cv, cx + 4, fy, STEEL, hand=IRON)
    pauldron(cv, cx + 3, fy - 17, STEEL, w=4)


def halberdier(cv, cx=MIL_X - 3, fy=FY):
    """Halberdier: breastplate, puffed sleeves and skirt in the nation's colours, halberd in front."""
    cv.shadow(cx + 1, 9)
    hang(cv, cx - 6, fy, TINT, layer=2, hand=IRON)
    boots(cv, cx, fy, LEATHER)
    legs(cv, cx, fy, TINT)
    for part_layer in (1,):
        lg = cv.part(part_layer, sep=False)
        cv.rect(lg, cx - 4, fy - 6, cx - 1, fy - 3, lit(TINT, dark_from=cx - 1, light_to=cx - 4))
    lg2 = cv.part(2, sep=False)
    cv.rect(lg2, cx + 1, fy - 6, cx + 4, fy - 3, lit(TINT, dark_from=cx + 4, light_to=cx + 1))
    torso(cv, cx, fy, STEEL, top=fy - 16)
    sk = cv.part(2)
    cv.rect(sk, cx - 4, fy - 9, cx + 4, fy - 7, lit(TINT, dark_from=cx + 3, light_to=cx - 3))
    sk1 = cv.part(1, sep=False)
    cv.pix(sk1, [(x, y) for x in (cx - 2, cx + 1) for y in (fy - 9, fy - 8, fy - 7)], TINT[1])
    open_helm(cv, cx, fy - T, STEEL)
    tl = cv.part()                                                                     # sallet tail and comb
    cv.rows(tl, [(fy - T + 3, cx - 5, cx - 4), (fy - T + 2, cx - 4, cx - 4), (fy - T - 2, cx - 1, cx + 1)], STEEL[1])
    tx = cx + 8
    pole(cv, tx, fy - 26, fy)
    hd = cv.part()
    cv.rows(hd, [(fy - 30, tx, tx), (fy - 29, tx, tx), (fy - 28, tx, tx + 2), (fy - 27, tx - 2, tx + 4), (fy - 26, tx + 1, tx + 4),
                 (fy - 25, tx + 1, tx + 4), (fy - 24, tx + 1, tx + 3), (fy - 23, tx + 1, tx + 1)], lit(STEEL, dark_from=tx + 3, light_to=tx + 1, light_rows=fy - 26))
    front_reach(cv, cx, fy, TINT, tx, hand=IRON, layer=2, low=True)


def vanguard(cv, cx=MIL_X - 1, fy=FY):
    """Vanguard: nasal helm, mail, short cape, sword and round shield."""
    cv.shadow(cx, 8)
    cape(cv, cx, fy, 2, length=7)
    sword_up(cv, cx - 9, fy - 27, fy - 13, guard=0, guard_ramp=GOLD)
    back_grip(cv, cx, fy, IRON, SKIN)
    base(cv, cx, fy, legs_r=LEATHER, torso_r=IRON, belt_r=LEATHER)
    ml = cv.part(sep=False)                                                            # mail texture
    cv.pix(ml, [(x, y) for y in range(fy - 15, fy - 8) for x in range(cx - 3, cx + 3) if (x + y) % 2 == 0], IRON[0])
    sc = cv.part(2, sep=False)
    cv.rect(sc, cx - 4, fy - 16, cx + 4, fy - 16, TINT[0])
    open_helm(cv, cx, fy - T, STEEL)
    round_shield(cv, cx + 1, fy - 15, rim=IRON)


def man_at_arms(cv, cx=MIL_X - 3, fy=FY):
    """Man-at-arms: open helm, halved tabard over mail and plate, greatsword held upright in both hands."""
    cv.shadow(cx + 1, 9)
    hang(cv, cx - 6, fy, STEEL, hand=IRON)
    boots(cv, cx, fy, IRON)
    legs(cv, cx, fy, STEEL)
    tabard(cv, cx, fy, 2, split=True, top=fy - 16)
    open_helm(cv, cx, fy - T, STEEL)
    pauldron(cv, cx - 8, fy - 17, STEEL)
    tx = cx + 8
    bl = cv.part()
    cv.rect(bl, tx - 1, fy - 28, tx + 1, fy - 14, lit(STEEL, dark_from=tx + 1, light_to=tx - 1))
    cv.rect(bl, tx, fy - 28, tx, fy - 14, STEEL[1])
    cv.put(bl, tx, fy - 29, STEEL[0])
    g = cv.part()
    cv.rect(g, tx - 3, fy - 13, tx + 3, fy - 13, lit(GOLD, dark_from=tx + 2))
    cv.rect(g, tx, fy - 6, tx, fy - 5, GOLD[1])
    front_reach(cv, cx, fy, STEEL, tx, hand=IRON, fore=STEEL, low=True)
    pauldron(cv, cx + 2, fy - 17, STEEL, w=4)


def royal_guard(cv, cx=MIL_X - 1, fy=FY):
    """Royal guard: polished plate with gold shoulders, tall plume, cape, sword and tower shield."""
    cv.shadow(cx, 9)
    cape(cv, cx, fy, 2, length=12)
    sword_up(cv, cx - 9, fy - 28, fy - 13, guard=0, guard_ramp=GOLD)
    back_grip(cv, cx, fy, STEEL, IRON)
    boots(cv, cx, fy, IRON)
    legs(cv, cx, fy, STEEL)
    torso(cv, cx, fy, STEEL)
    great_helm(cv, cx, fy - T)
    tall_plume(cv, cx, fy - T - 1, 1)
    pauldron(cv, cx - 8, fy - 17, GOLD)
    tower(cv, cx + 1, fy - 17, w=9, h=16)


def gladiator(cv, cx=MIL_X - 1, fy=FY):
    """Arena fighter: crested helm, bare chest under a harness, one big shoulder guard, axe and round shield."""
    cv.shadow(cx, 8)
    wx = cx - 9
    pole(cv, wx, fy - 28, fy - 9)
    ax = cv.part()
    cv.rows(ax, [(fy - 29, wx - 5, wx - 4), (fy - 28, wx - 5, wx - 3), (fy - 27, wx - 5, wx - 2), (fy - 26, wx - 5, wx + 1), (fy - 25, wx - 5, wx + 1),
                 (fy - 24, wx - 5, wx - 2), (fy - 23, wx - 5, wx - 3), (fy - 22, wx - 5, wx - 4)], lit(STEEL, dark_from=wx - 1, light_to=wx - 5, light_rows=fy - 22))
    back_grip(cv, cx, fy, SKIN)
    boots(cv, cx, fy, LEATHER)
    legs(cv, cx, fy, SKIN)
    torso(cv, cx, fy, SKIN, top=fy - 16)
    hs = cv.part(sep=False)
    cv.pix(hs, line(cx - 4, fy - 15, cx + 4, fy - 9) + line(cx - 4, fy - 14, cx + 3, fy - 9), LEATHER[1])
    sk = cv.part(2)                                                                    # war skirt
    cv.rect(sk, cx - 5, fy - 8, cx + 5, fy - 5, lit(TINT, dark_from=cx + 4, light_to=cx - 4, light_rows=fy - 7))
    cv.rows(sk, [(fy - 4, cx - 5, cx - 4), (fy - 4, cx - 2, cx - 1), (fy - 4, cx + 1, cx + 2), (fy - 4, cx + 4, cx + 5)], TINT[2])
    bl = cv.part(sep=False)
    cv.rect(bl, cx - 5, fy - 8, cx + 5, fy - 8, LEATHER[1])
    cv.put(bl, cx, fy - 8, GOLD[0])
    great_helm(cv, cx, fy - T, IRON)
    cr = cv.part(1)                                                                    # fore-and-aft crest
    cv.rows(cr, [(fy - T - 3, cx - 3, cx + 2), (fy - T - 2, cx - 4, cx + 3), (fy - T - 1, cx - 4, cx - 3), (fy - T, cx - 4, cx - 4), (fy - T + 1, cx - 4, cx - 4)],
            lit(TINT, dark_from=cx + 2, light_to=cx - 2, light_rows=fy - T - 3))
    pauldron(cv, cx - 9, fy - 17, STEEL, w=6)
    round_shield(cv, cx + 1, fy - 15, rim=IRON)


def vanquisher(cv, cx=MIL_X - 3, fy=FY):
    """Vanquisher: arcanite plate, winged helm, cape, a double-headed greataxe."""
    cv.shadow(cx + 1, 9)
    cape(cv, cx, fy, 2, length=12)
    hang(cv, cx - 6, fy, ARCANITE, hand=IRON)
    boots(cv, cx, fy, IRON)
    legs(cv, cx, fy, ARCANITE)
    torso(cv, cx, fy, ARCANITE)
    tb = cv.part(2)
    cv.rect(tb, cx - 2, fy - 12, cx + 2, fy - 5, lit(TINT, dark_from=cx + 2, light_to=cx - 2, light_rows=fy - 9))
    bt = cv.part(1, sep=False)
    cv.rect(bt, cx - 4, fy - 9, cx + 4, fy - 9, TINT[1])
    great_helm(cv, cx, fy - T, ARCANITE)
    wg = cv.part(1)                                                                    # wings on the helm
    cv.rows(wg, [(fy - T - 4, cx - 5, cx - 5), (fy - T - 3, cx - 5, cx - 4), (fy - T - 2, cx - 5, cx - 3), (fy - T - 1, cx - 4, cx - 3), (fy - T, cx - 4, cx - 4),
                 (fy - T - 4, cx + 3, cx + 3), (fy - T - 3, cx + 3, cx + 3)], TINT[0])
    pauldron(cv, cx - 9, fy - 18, ARCANITE, w=6)
    tx = cx + 8
    pole(cv, tx, fy - 28, fy, IRON)
    ax = cv.part()
    cv.rows(ax, [(fy - 28, tx - 3, tx - 2), (fy - 28, tx + 2, tx + 3), (fy - 27, tx - 4, tx - 1), (fy - 27, tx + 1, tx + 4), (fy - 26, tx - 4, tx + 4),
                 (fy - 25, tx - 4, tx + 4), (fy - 24, tx - 4, tx - 1), (fy - 24, tx + 1, tx + 4), (fy - 23, tx - 3, tx - 2), (fy - 23, tx + 2, tx + 3)],
            lit(ARCANITE, dark_from=tx + 3, light_to=tx - 2, light_rows=fy - 25))
    front_reach(cv, cx, fy, ARCANITE, tx, hand=IRON, fore=ARCANITE, low=True)
    pauldron(cv, cx + 2, fy - 18, ARCANITE, w=5)


def warbringer(cv, cx=MIL_X - 3, fy=FY):
    """Warbringer: gilded plate and crowned helm, the war banner on his back, sword raised in front."""
    cv.shadow(cx, 9)
    px = cx - 7
    pole(cv, px, fy - 30, fy - 12)
    banner(cv, px - 9, fy - 28, w=8, h=11)
    boots(cv, cx, fy, IRON)
    legs(cv, cx, fy, STEEL)
    hang(cv, cx - 6, fy, STEEL, hand=IRON)
    torso(cv, cx, fy, STEEL)
    tr = cv.part(sep=False)
    cv.rect(tr, cx - 4, fy - 12, cx + 4, fy - 12, GOLD[1])
    cv.pix(tr, [(cx - 2, fy - 14), (cx - 1, fy - 13), (cx + 1, fy - 13), (cx + 2, fy - 14), (cx - 3, fy - 15), (cx + 3, fy - 15)], GOLD[0])
    belt(cv, cx, fy, LEATHER)
    great_helm(cv, cx, fy - T)
    cw = cv.part()                                                                     # crown
    cv.rows(cw, [(fy - T - 1, cx - 3, cx + 3)], GOLD[1])
    cv.pix(cw, [(cx - 3, fy - T - 2), (cx - 1, fy - T - 2), (cx + 1, fy - T - 2), (cx + 3, fy - T - 2)], GOLD[0])
    pauldron(cv, cx - 9, fy - 18, GOLD, w=6)
    tx = cx + 8
    bl = cv.part()
    cv.rect(bl, tx, fy - 26, tx + 1, fy - 14, lit(STEEL, dark_from=tx + 1))
    cv.put(bl, tx, fy - 27, STEEL[0])
    g = cv.part(1)
    cv.rect(g, tx - 2, fy - 13, tx + 3, fy - 13, lit(TINT, dark_from=tx + 2))
    cv.rect(g, tx, fy - 8, tx + 1, fy - 8, TINT[1])
    front_reach(cv, cx, fy, STEEL, tx + 1, hand=IRON, fore=STEEL)
    pauldron(cv, cx + 2, fy - 18, GOLD, w=5)


def marine(cv, cx=MIL_X - 4, fy=FY):
    """Marine: tricorne, long sea coat in the nation's colour with white crossbelts, cutlass and pistol."""
    cv.shadow(cx, 9)
    wx = cx - 9
    bl = cv.part()                                                                     # cutlass: curved back
    cv.rows(bl, [(fy - 26, wx - 2, wx - 1), (fy - 25, wx - 2, wx), (fy - 24, wx - 1, wx + 1)] + [(y, wx, wx + 1) for y in range(fy - 23, fy - 13)],
            lit(STEEL, dark_from=wx + 1, light_to=wx - 1))
    g = cv.part()
    cv.rows(g, [(fy - 13, wx - 1, wx + 2), (fy - 12, wx - 2, wx - 2), (fy - 11, wx - 2, wx - 2), (fy - 10, wx - 2, wx - 1), (fy - 9, wx, wx + 1)], GOLD[1])
    back_grip(cv, cx, fy, TINT, layer=2)
    boots(cv, cx, fy, CLOTHD)
    legs(cv, cx, fy, WHITE)
    ct = cv.part(2)
    cv.rows(ct, [(y, cx - 4, cx + 4) for y in range(fy - 16, fy - 4)], lit(TINT, dark_from=cx + 3, light_to=cx - 3, light_rows=fy - 11))
    cv.rows(ct, [(fy - 4, cx - 4, cx - 1), (fy - 4, cx + 2, cx + 4)], TINT[2])
    xb = cv.part(sep=False)                                                            # crossbelts
    cv.pix(xb, line(cx - 4, fy - 15, cx + 3, fy - 9) + line(cx + 4, fy - 15, cx - 3, fy - 9), WHITE[0])
    bt = cv.part(sep=False)
    cv.rect(bt, cx - 4, fy - 8, cx + 4, fy - 8, LEATHER[2])
    cv.put(bt, cx, fy - 8, GOLD[0])
    head(cv, cx, fy - T)
    hair(cv, cx, fy - T, HAIR)
    top = fy - T
    h = cv.part()                                                                      # tricorne
    cv.rows(h, [(top - 3, cx - 2, cx + 2), (top - 2, cx - 4, cx + 4), (top - 1, cx - 6, cx + 6), (top, cx - 5, cx + 5)],
            lit(CLOTHD, dark_from=cx + 3, light_to=cx - 2, light_rows=top - 2))
    cv.pix(h, [(cx - 7, top - 2), (cx + 7, top - 2)], CLOTHD[1])
    tr = cv.part(1, sep=False)
    cv.rect(tr, cx - 5, top, cx + 5, top, TINT[0])
    y = fy - 14                                                                        # pistol arm
    sl = cv.part(2)
    cv.rect(sl, cx + 4, y, cx + 6, y + 2, lit(TINT, dark_from=cx + 6, light_to=cx + 4, light_rows=y))
    ps = cv.part()
    cv.rect(ps, cx + 8, y - 1, cx + 13, y - 1, IRON[0])
    cv.rect(ps, cx + 8, y, cx + 10, y, WOOD[1])
    cv.put(ps, cx + 13, y - 1, GOLD[0])
    fist(cv, cx + 7, y)


def skyguard(cv, cx=MIL_X - 2, fy=FY):
    """Airborne trooper: flying cap and goggles, scarf streaming back, harness and chute pack, sabre and buckler."""
    cv.shadow(cx, 8)
    pk = cv.part(2)                                                                    # chute pack
    cv.rect(pk, cx - 8, fy - 16, cx - 5, fy - 9, lit(TINT, dark_from=cx - 5, light_to=cx - 7, light_rows=fy - 13))
    sf = cv.part(1)                                                                    # scarf
    cv.rows(sf, [(fy - 17, cx - 11, cx - 4), (fy - 18, cx - 12, cx - 9), (fy - 16, cx - 9, cx - 7)], lit(TINT, dark_from=cx - 5, light_to=cx - 10))
    hang(cv, cx - 6, fy - 1, LEATHER)
    base(cv, cx, fy, legs_r=TAN, torso_r=LEATHER)
    hs = cv.part(sep=False)                                                            # harness
    cv.rect(hs, cx - 3, fy - 16, cx - 3, fy - 8, WHITE[0])
    cv.rect(hs, cx + 2, fy - 16, cx + 2, fy - 8, WHITE[1])
    cv.rect(hs, cx - 3, fy - 12, cx + 2, fy - 12, WHITE[1])
    sc = cv.part(1, sep=False)
    cv.rect(sc, cx - 4, fy - 16, cx + 4, fy - 16, TINT[0])
    open_helm(cv, cx, fy - T, LEATHER)
    fl = cv.part()
    cv.rect(fl, cx - 4, fy - T + 3, cx - 4, fy - T + 6, LEATHER[1])
    g = cv.part(sep=False)
    cv.rect(g, cx - 3, fy - T + 2, cx + 3, fy - T + 2, LEATHER[2])
    cv.rect(g, cx - 1, fy - T + 2, cx + 3, fy - T + 3, IRON[2])
    cv.pix(g, [(cx, fy - T + 3), (cx + 2, fy - T + 3)], AZER[0])
    tx = cx + 8                                                                        # sabre forward
    bl = cv.part()
    cv.rect(bl, tx, fy - 25, tx + 1, fy - 14, lit(STEEL, dark_from=tx + 1))
    cv.pix(bl, [(tx + 1, fy - 26), (tx + 2, fy - 26), (tx + 2, fy - 25)], STEEL[0])
    g2 = cv.part()
    cv.rect(g2, tx - 1, fy - 13, tx + 2, fy - 13, GOLD[1])
    front_reach(cv, cx, fy, LEATHER, tx + 1)


def siegebreaker(cv, cx=MIL_X - 1, fy=FY):
    """Siegebreaker: kettle hat, a rocket tube shouldered and loaded, tower shield."""
    cv.shadow(cx, 9)
    wx = cx - 11
    tb = cv.part()                                                                     # launch tube
    cv.rect(tb, wx, fy - 25, wx + 3, fy - 12, lit(IRON, dark_from=wx + 3, light_to=wx, light_rows=fy - 14))
    cv.rect(tb, wx - 1, fy - 26, wx + 4, fy - 25, IRON[0])
    bd = cv.part(1, sep=False)
    cv.rect(bd, wx, fy - 20, wx + 3, fy - 19, lit(TINT, dark_from=wx + 3))
    rk = cv.part()                                                                     # rocket nose
    cv.rows(rk, [(fy - 29, wx + 1, wx + 2), (fy - 28, wx, wx + 3), (fy - 27, wx, wx + 3)], lit(RED, dark_from=wx + 3, light_to=wx))
    arm(cv, cx - 8, fy - 15, STEEL, length=3, hand=False)
    fist(cv, cx - 9, fy - 12, IRON)
    boots(cv, cx, fy, IRON)
    legs(cv, cx, fy, STEEL)
    torso(cv, cx, fy, STEEL, top=fy - 16)
    kettle(cv, cx, fy - T, IRON)
    pauldron(cv, cx - 8, fy - 17, STEEL)
    tower(cv, cx + 1, fy - 17, w=9, h=16)


def phalanx(cv, cx=MIL_X - 1, fy=FY):
    """Phalanx: arcanite plate, a broad tower shield with a glowing rune, a runed pike."""
    cv.shadow(cx, 9)
    wx = cx - 9
    pole(cv, wx, fy - 24, fy, IRON)
    h = cv.part()
    cv.rows(h, [(fy - 30, wx, wx), (fy - 29, wx - 1, wx + 1), (fy - 28, wx - 1, wx + 1), (fy - 27, wx - 1, wx + 1), (fy - 26, wx - 1, wx + 1), (fy - 25, wx - 2, wx + 2)],
            lit(ARCANITE, dark_from=wx + 1, light_to=wx - 1))
    rn = cv.part(sep=False)
    cv.rect(rn, wx, fy - 28, wx, fy - 26, ARCANE[0])
    cv.pix(rn, [(wx, fy - 21), (wx, fy - 18)], ARCANE[1])
    back_grip(cv, cx, fy, ARCANITE, IRON)
    boots(cv, cx, fy, IRON)
    legs(cv, cx, fy, ARCANITE)
    torso(cv, cx, fy, ARCANITE)
    great_helm(cv, cx, fy - T, ARCANITE)
    cm = cv.part(1)                                                                    # flat comb
    cv.rows(cm, [(fy - T - 3, cx - 3, cx + 3), (fy - T - 2, cx - 3, cx + 3)], lit(TINT, dark_from=cx + 2, light_to=cx - 2, light_rows=fy - T - 3))
    pauldron(cv, cx - 8, fy - 17, ARCANITE)
    tower(cv, cx, fy - 18, w=10, h=18, stud=0)


# ================================================================ bows, magic and guns
def hunter(cv, cx=MIL_X - 5, fy=FY):
    """Woodsman: fur cap and fur mantle, tunic in the nation's colour, plain longbow."""
    cv.shadow(cx + 1, 9)
    quiver(cv, cx, fy)
    arm(cv, cx - 6, fy - 14, TINT, length=3, hand=False, layer=2)
    base(cv, cx, fy, legs_r=LEATHER, torso_r=TINT, layer=2, belt_r=LEATHER)
    mantle(cv, cx, fy, 0, ramp=FUR, clasp=None)
    head(cv, cx, fy - T)
    beard(cv, cx, fy - T, HAIR)
    top = fy - T
    fc = cv.part()
    cv.rows(fc, [(top - 2, cx - 2, cx + 2), (top - 1, cx - 3, cx + 3), (top, cx - 4, cx + 4), (top + 1, cx - 4, cx + 4), (top + 2, cx - 4, cx - 3),
                 (top + 3, cx - 4, cx - 3)], lit(FUR, dark_from=cx + 2, light_to=cx - 1, light_rows=top - 1))
    bow(cv, cx, fy - 13, sleeve=TINT, layer=2)


def ranger(cv, cx=MIL_X - 5, fy=FY):
    """Ranger: forest-green hood and long cloak, tunic in the nation's colour, longbow."""
    cv.shadow(cx + 1, 9)
    quiver(cv, cx, fy)
    cape(cv, cx, fy, 0, ramp=GREEN, length=12)
    base(cv, cx, fy, legs_r=LEATHER, torso_r=TINT, layer=2, belt_r=LEATHER)
    hood(cv, cx, fy - T, 0, ramp=GREEN)
    cl = cv.part(1, sep=False)
    cv.put(cl, cx + 2, fy - 16, TINT[0])
    bow(cv, cx, fy - 13, sleeve=GREEN)


def ranger_captain(cv, cx=MIL_X - 5, fy=FY):
    """Ranger captain: plumed hat, long fair hair, green cloak, leather shoulder guard, a bow with steel tips."""
    cv.shadow(cx + 1, 9)
    quiver(cv, cx, fy)
    cape(cv, cx, fy, 0, ramp=GREEN, length=12)
    base(cv, cx, fy, legs_r=LEATHER, torso_r=TINT, layer=2, belt_r=LEATHER)
    head(cv, cx, fy - T)
    hair(cv, cx, fy - T, BLOND, long=True)
    brim_hat(cv, cx, fy - T - 1, GREEN, crown=3, brim=5)
    feather(cv, cx - 2, fy - T - 3)
    pauldron(cv, cx - 8, fy - 17, LEATHER)
    bow(cv, cx, fy - 13, sleeve=LEATHER, h=10)
    tp = cv.part(sep=False)
    cv.pix(tp, [(cx + 9, fy - 23), (cx + 9, fy - 3)], STEEL[0])


def ranger_general(cv, cx=MIL_X - 6, fy=FY):
    """Ranger-general: circlet, fair hair, cape in the nation's colours, steel shoulder, a golden bow with a glowing arrow."""
    cv.shadow(cx + 1, 9)
    quiver(cv, cx, fy)
    cape(cv, cx, fy, 2, length=12)
    ct = cv.part(1, sep=False)
    cv.rect(ct, cx - 6, fy - 5, cx - 3, fy - 5, TINT[1])
    base(cv, cx, fy, legs_r=LEATHER, torso_r=GREEN, belt_r=LEATHER)
    tr = cv.part(1, sep=False)
    cv.rect(tr, cx, fy - 16, cx, fy - 8, TINT[0])
    head(cv, cx, fy - T)
    hair(cv, cx, fy - T, BLOND, long=True)
    ci = cv.part(sep=False)
    cv.rect(ci, cx - 3, fy - T + 1, cx + 3, fy - T + 1, GOLD[1])
    cv.put(ci, cx + 1, fy - T + 1, AZER[0])
    pauldron(cv, cx - 9, fy - 17, STEEL, w=6)
    ft = cv.part(1)
    cv.pix(ft, [(cx - 9, fy - 18), (cx - 8, fy - 19), (cx - 7, fy - 18), (cx - 10, fy - 19)], TINT[0])
    bow(cv, cx, fy - 13, sleeve=GREEN, wood=GOLD, h=10)
    gl = cv.part(sep=False)
    cv.pix(gl, [(cx + 13, fy - 14), (cx + 14, fy - 14)], GLOW[0])
    sp = cv.part()
    cv.pix(sp, [(cx + 15, fy - 16), (cx + 15, fy - 12)], GLOW[1])


def magus(cv, cx=MIL_X - 6, fy=FY):
    """Magus: hooded robe in the nation's colours, a wand in the back hand, an arcane bolt gathering in the other."""
    cv.shadow(cx, 8)
    robe(cv, cx, fy, TINT, layer=2)
    robe_trim(cv, cx, fy, 1)
    arm(cv, cx - 6, fy - 14, TINT, length=4, layer=2)
    wd = cv.part()                                                                     # wand
    cv.rect(wd, cx - 6, fy - 20, cx - 6, fy - 11, WOOD[1])
    cv.put(wd, cx - 6, fy - 21, ARCANE[0])
    hood(cv, cx, fy - T, 2)
    tr = cv.part(1, sep=False)
    cv.rect(tr, cx - 5, fy - 16, cx + 4, fy - 16, TINT[0])
    y = fy - 14
    sl = cv.part(2)
    cv.rect(sl, cx + 4, y, cx + 7, y + 2, lit(TINT, dark_from=cx + 7, light_to=cx + 5, light_rows=y))
    cf = cv.part(1, sep=False)
    cv.rect(cf, cx + 7, y, cx + 7, y + 2, TINT[1])
    fist(cv, cx + 8, y)
    ob = cv.part()                                                                     # arcane bolt
    ox, oy = cx + 13, y - 3
    cv.rows(ob, [(oy - 2, ox - 1, ox + 1), (oy - 1, ox - 2, ox + 2), (oy, ox - 2, ox + 2), (oy + 1, ox - 2, ox + 2), (oy + 2, ox - 1, ox + 1)],
            lit(ARCANE, dark_from=ox + 2, light_to=ox, light_rows=oy))
    sp = cv.part()
    cv.pix(sp, [(ox - 4, oy - 3), (ox + 4, oy - 2), (ox + 3, oy + 4), (ox - 4, oy + 3)], ARCANE[0])


def rifleman(cv, cx=MIL_X - 7, fy=FY):
    """Rifleman: slouch hat with a feather, coat in the nation's colour, long rifle with a bayonet at the shoulder."""
    cv.shadow(cx + 1, 9)
    arm(cv, cx - 6, fy - 15, TINT, length=3, hand=False, layer=2)
    base(cv, cx, fy, legs_r=TAN, torso_r=TINT, layer=2, belt_r=LEATHER)
    xb = cv.part(sep=False)
    cv.pix(xb, line(cx - 4, fy - 16, cx + 3, fy - 9), WHITE[0])
    pc = cv.part()
    cv.rect(pc, cx - 4, fy - 7, cx - 2, fy - 5, lit(LEATHER, dark_from=cx - 2))
    head(cv, cx, fy - T)
    beard(cv, cx, fy - T, HAIR)
    brim_hat(cv, cx, fy - T - 1, LEATHER, crown=3, brim=5)
    feather(cv, cx - 2, fy - T - 3)
    y = fy - 15
    gun(cv, cx - 3, y, length=16, bayonet=True)
    gun_arms(cv, cx, y, TINT, layer=2)


def mountaineer(cv, cx=MIL_X - 6, fy=FY):
    """Mountaineer: fur hat, big beard, fur mantle over the nation's colour, a short heavy gun with a bell mouth."""
    cv.shadow(cx + 1, 9)
    arm(cv, cx - 6, fy - 15, TINT, length=3, hand=False, layer=2)
    base(cv, cx, fy, legs_r=LEATHER, torso_r=TINT, layer=2, belt_r=LEATHER)
    mantle(cv, cx, fy, 0, ramp=FUR, clasp=None)
    head(cv, cx, fy - T)
    beard(cv, cx, fy - T, ((214, 130, 70), (170, 88, 50), (112, 56, 44)), long=True)
    top = fy - T
    fc = cv.part()
    cv.rows(fc, [(top - 3, cx - 2, cx + 2), (top - 2, cx - 3, cx + 3), (top - 1, cx - 4, cx + 4), (top, cx - 4, cx + 4), (top + 1, cx - 4, cx + 4), (top + 2, cx - 4, cx - 3),
                 (top + 3, cx - 4, cx - 3), (top + 4, cx - 4, cx - 3)], lit(FUR, dark_from=cx + 2, light_to=cx - 1, light_rows=top - 2))
    y = fy - 13
    gun(cv, cx - 2, y, length=13, bell=True, barrel=STEEL)
    gun_arms(cv, cx, y, TINT, layer=2)


def grenadier(cv, cx=MIL_X - 3, fy=FY):
    """Grenadier: tall mitre cap, coat in the nation's colour with white crossbelts, bomb bag, a lit bomb held high."""
    cv.shadow(cx, 8)
    hang(cv, cx - 6, fy, TINT, layer=2)
    base(cv, cx, fy, legs_r=WHITE, torso_r=TINT, layer=2, belt_r=LEATHER)
    xb = cv.part(sep=False)
    cv.pix(xb, line(cx - 4, fy - 15, cx + 3, fy - 9) + line(cx + 4, fy - 15, cx - 3, fy - 9), WHITE[0])
    bg = cv.part()
    cv.rect(bg, cx - 5, fy - 8, cx - 1, fy - 4, lit(LEATHER, dark_from=cx - 1, light_to=cx - 4, light_rows=fy - 7))
    bb = cv.part(sep=False)
    cv.pix(bb, [(cx - 4, fy - 9), (cx - 2, fy - 9)], IRON[2])
    head(cv, cx, fy - T)
    top = fy - T
    mt = cv.part(2)                                                                    # mitre cap
    cv.rows(mt, [(top - 5, cx - 1, cx + 1), (top - 4, cx - 2, cx + 2), (top - 3, cx - 2, cx + 2), (top - 2, cx - 3, cx + 3), (top - 1, cx - 3, cx + 3), (top, cx - 3, cx + 3),
                 (top + 1, cx - 3, cx + 3)], lit(TINT, dark_from=cx + 2, light_to=cx - 1, light_rows=top - 3))
    fp = cv.part(1, sep=False)
    cv.rows(fp, [(top - 3, cx + 1, cx + 2), (top - 2, cx, cx + 3), (top - 1, cx, cx + 3), (top, cx, cx + 3)], TINT[0])
    cv.rect(fp, cx - 3, top + 1, cx + 3, top + 1, TINT[1])
    ax = cx + 6                                                                        # raised arm
    sl = cv.part(2)
    cv.rect(sl, cx + 4, fy - 15, cx + 6, fy - 13, lit(TINT, dark_from=cx + 6))
    cv.rect(sl, ax, fy - 19, ax + 2, fy - 13, lit(TINT, dark_from=ax + 2, light_to=ax))
    fist(cv, ax, fy - 22)
    bm = cv.part()
    cv.rows(bm, [(fy - 27, ax, ax + 2), (fy - 26, ax - 1, ax + 3), (fy - 25, ax - 1, ax + 3), (fy - 24, ax - 1, ax + 3), (fy - 23, ax, ax + 2)],
            lit(BLACKH, dark_from=ax + 2, light_to=ax, light_rows=fy - 26))
    fz = cv.part()
    cv.pix(fz, [(ax + 2, fy - 28), (ax + 3, fy - 29)], TAN[1])
    sp = cv.part()
    cv.pix(sp, [(ax + 4, fy - 30), (ax + 3, fy - 30), (ax + 4, fy - 29)], FLAME[1])
    cv.put(sp, ax + 4, fy - 30, FLAME[0])


def sharpshooter(cv, cx=MIL_X - 8, fy=FY):
    """Sharpshooter: hooded cloak in the nation's colour, goggles, a very long scoped rifle with a glowing Azerite chamber."""
    cv.shadow(cx + 2, 10)
    cape(cv, cx, fy, 2, length=12)
    arm(cv, cx - 6, fy - 15, LEATHER, length=3, hand=False)
    base(cv, cx, fy, legs_r=CLOTHD, torso_r=LEATHER, belt_r=IRON)
    bd = cv.part(sep=False)
    cv.pix(bd, line(cx + 4, fy - 16, cx - 3, fy - 9), GOLD[1])
    hood(cv, cx, fy - T, 2)
    g = cv.part(sep=False)
    cv.rect(g, cx - 1, fy - T + 3, cx + 3, fy - T + 3, IRON[2])
    cv.pix(g, [(cx, fy - T + 3), (cx + 2, fy - T + 3)], AZER[0])
    y = fy - 15
    gun(cv, cx - 3, y, length=20, barrel=STEEL, scope=True, glow=AZER)
    gun_arms(cv, cx, y, LEATHER)
    sp = cv.part()
    cv.pix(sp, [(cx + 19, y - 1), (cx + 19, y + 1)], AZER[0])


# ================================================================ riders (centre of the tile)
def rider(cv, cx, back, leg_r=STEEL, boot_r=IRON, torso_r=TINT, layer=2, belt_layer=1):
    lg = cv.part()
    cv.rect(lg, cx - 2, back - 1, cx + 1, back + 4, lit(leg_r, dark_from=cx + 1, light_to=cx - 2))
    bt = cv.part()
    cv.rect(bt, cx - 2, back + 5, cx + 3, back + 6, lit(boot_r, dark_from=cx + 2))
    tb = cv.part(layer)
    cv.rect(tb, cx - 4, back - 8, cx + 4, back - 1, lit(torso_r, dark_from=cx + 3, light_to=cx - 3, light_rows=back - 5))
    if belt_layer is not None:
        bl = cv.part(belt_layer, sep=False)
        cv.rect(bl, cx - 4, back - 2, cx + 4, back - 2, lit(TINT if belt_layer else LEATHER, dark_from=cx + 3))
    return back - 15


def blanket(cv, cx, back, layer=2):
    b = cv.part(layer)
    cv.rows(b, [(back, cx - 5, cx + 3)] + [(y, cx - 6, cx + 4) for y in range(back + 1, back + 5)], lit(TINT, dark_from=cx + 3, light_to=cx - 4, light_rows=back + 1))
    t = cv.part(3 - layer, sep=False)
    cv.rect(t, cx - 6, back + 4, cx + 4, back + 4, lit(TINT, dark_from=cx + 3))


def caparison(cv, cx, back, layer=2):
    cp = cv.part(layer)
    cv.rows(cp, [(back, cx - 8, cx + 4)] + [(y, cx - 9, cx + 5) for y in range(back + 1, back + 8)] +
                [(back + 8, cx - 9, cx - 6), (back + 8, cx - 3, cx + 5), (back + 9, cx - 2, cx + 4)],
            lit(TINT, dark_from=cx + 4, light_to=cx - 6, light_rows=back + 2))
    tr = cv.part(3 - layer, sep=False)
    cv.rect(tr, cx - 9, back + 6, cx + 5, back + 6, lit(TINT, dark_from=cx + 4))


def chanfron(cv, cx, back, ramp=STEEL):
    """Plate on the horse's face and the crest of its neck."""
    c = cv.part()
    cv.rows(c, [(back - 7, cx + 9, cx + 12), (back - 6, cx + 9, cx + 14), (back - 5, cx + 10, cx + 16), (back - 4, cx + 12, cx + 17)],
            lit(ramp, dark_from=cx + 15, light_to=cx + 12, light_rows=back - 6))
    cv.rows(c, [(back - 4, cx + 6, cx + 8), (back - 3, cx + 6, cx + 8), (back - 2, cx + 5, cx + 8), (back - 1, cx + 5, cx + 8), (back, cx + 5, cx + 8)],
            lit(ramp, dark_from=cx + 8, light_to=cx + 6))
    e = cv.part(sep=False)
    cv.put(e, cx + 12, back - 5, DARK)


def rein_arm(cv, cx, back, ramp, hand=IRON, layer=0):
    arm(cv, cx - 7, back - 6, ramp, length=3, hand=False, layer=layer)
    fist(cv, cx - 6, back - 3, hand)


def outrider(cv, cx=MID_X - 2, fy=FY):
    """Outrider: unarmoured horse, rider in a cap with a cloak streaming behind, a light spear."""
    cv.shadow(cx + 1, 14)
    back = horse(cv, cx, fy)
    blanket(cv, cx, back)
    lx = cx + 6
    pole(cv, lx, 6, back - 1)
    spear_head(cv, lx, 2)
    ck = cv.part(2)                                                                    # cloak streaming back
    cv.rows(ck, [(back - 8, cx - 8, cx - 3), (back - 7, cx - 11, cx - 3), (back - 6, cx - 13, cx - 3), (back - 5, cx - 14, cx - 5), (back - 4, cx - 14, cx - 9)],
            lit(TINT, dark_from=cx - 5, light_to=cx - 10, light_rows=back - 7))
    ht = rider(cv, cx, back, leg_r=TAN, boot_r=LEATHER, torso_r=LEATHER, layer=0, belt_layer=None)
    sc = cv.part(1, sep=False)
    cv.rect(sc, cx - 4, back - 8, cx + 4, back - 8, TINT[0])
    head(cv, cx, ht)
    hair(cv, cx, ht, HAIR)
    c = cv.part()
    cv.rows(c, [(ht - 2, cx - 2, cx + 1), (ht - 1, cx - 3, cx + 3), (ht, cx - 4, cx + 5)], lit(GREEN, dark_from=cx + 3, light_to=cx - 1, light_rows=ht - 1))
    feather(cv, cx - 2, ht - 2)
    sl = cv.part()
    cv.rect(sl, cx + 3, back - 7, cx + 5, back - 5, lit(LEATHER, dark_from=cx + 5))
    fist(cv, lx - 1, back - 6)


def lancer(cv, cx=MID_X - 4, fy=FY):
    """Lancer: half-armoured rider in a kettle hat, long lance levelled forward with a pennant under the point."""
    cv.shadow(cx + 1, 14)
    back = horse(cv, cx, fy)
    blanket(cv, cx, back)
    ht = rider(cv, cx, back)
    kettle(cv, cx, ht)
    pauldron(cv, cx - 8, back - 9, STEEL)
    ln = cv.part()                                                                     # lance: rising one pixel every two columns
    pts = []
    for i in range(0, 32):
        x = cx - 9 + i
        y = back - 2 - i // 2
        pts += [(x, y)]
    cv.pix(ln, pts, WOOD[1])
    cv.pix(ln, pts[::2], WOOD[0])
    cv.pix(ln, pts[-4:], STEEL[0])
    tx, ty = pts[-6]
    pn = cv.part(2)
    cv.rows(pn, [(ty + 1, tx - 5, tx - 1), (ty + 2, tx - 6, tx - 1), (ty + 3, tx - 5, tx - 2), (ty + 4, tx - 6, tx - 4)], lit(TINT, dark_from=tx - 2, light_to=tx - 4))
    pt = cv.part(1, sep=False)
    cv.rect(pt, tx - 1, ty + 1, tx - 1, ty + 2, TINT[0])
    sl = cv.part()
    cv.rect(sl, cx + 2, back - 8, cx + 4, back - 5, lit(STEEL, dark_from=cx + 4, light_to=cx + 2))
    fist(cv, cx + 2, back - 5, IRON)


def war_rider(cv, cx=MID_X - 2, fy=FY):
    """War rider: black charger in plate and a caparison, rider in full plate with shield, lance and a great banner."""
    cv.shadow(cx + 1, 14)
    back = horse(cv, cx, fy, BLACKH)
    caparison(cv, cx, back, 1)
    chanfron(cv, cx, back)
    lx = cx + 6
    pole(cv, lx, 3, back - 1)
    h = cv.part()
    cv.pix(h, [(lx, 1), (lx, 2)], STEEL[0])
    bn = cv.part(2)                                                                    # banner flying forward
    cv.rows(bn, [(y, lx + 1, lx + 9) for y in range(3, 9)] + [(9, lx + 1, lx + 7), (10, lx + 1, lx + 4)], lit(TINT, dark_from=lx + 8, light_to=lx + 4, light_rows=5))
    bt = cv.part(1, sep=False)
    cv.rect(bt, lx + 1, 4, lx + 9, 5, lit(TINT, dark_from=lx + 8))
    cv.rect(bt, lx + 1, 3, lx + 1, 10, TINT[0])
    ht = rider(cv, cx, back)
    rein_arm(cv, cx, back, STEEL)
    great_helm(cv, cx, ht)
    crest(cv, cx, ht, 1)
    pauldron(cv, cx - 8, back - 9, STEEL)
    pauldron(cv, cx + 3, back - 9, STEEL)
    fist(cv, lx - 1, back - 5, IRON)
    kite(cv, cx - 3, back - 4, w=7, h=10)


def paladin(cv, cx=MID_X - 2, fy=FY):
    """Paladin: grey charger in a caparison, rider in plate with gold shoulders and a cape, warhammer raised and shining."""
    cv.shadow(cx + 1, 14)
    back = horse(cv, cx, fy, GREYH)
    caparison(cv, cx, back)
    cp = cv.part(2)                                                                    # cape
    cv.rows(cp, [(y, cx - 7, cx - 3) for y in range(back - 8, back)], lit(TINT, dark_from=cx - 4, light_to=cx - 6, light_rows=back - 5))
    lx = cx + 9
    pole(cv, lx, 6, back - 1)
    hm = cv.part()                                                                     # hammer head
    cv.rect(hm, lx - 3, 2, lx + 3, 6, lit(GOLD, dark_from=lx + 2, light_to=lx - 2, light_rows=3))
    cv.rect(hm, lx - 3, 6, lx + 3, 6, GOLD[2])
    gl = cv.part(sep=False)
    cv.rect(gl, lx - 1, 3, lx + 1, 5, GLOW[1])
    cv.put(gl, lx, 4, GLOW[0])
    ry = cv.part()
    cv.pix(ry, [(lx - 5, 1), (lx + 5, 1), (lx - 6, 4), (lx + 6, 4), (lx + 5, 8), (lx - 5, 8)], GLOW[1])
    ht = rider(cv, cx, back, torso_r=STEEL, layer=0, belt_layer=1)
    tb = cv.part(2, sep=False)
    cv.rect(tb, cx - 1, back - 8, cx + 1, back - 3, TINT[0])
    rein_arm(cv, cx, back, STEEL)
    open_helm(cv, cx, ht, STEEL)
    b = cv.part(sep=False)
    cv.rows(b, [(ht + 5, cx - 1, cx + 3)], BLOND[1])
    pauldron(cv, cx - 8, back - 9, GOLD)
    pauldron(cv, cx + 3, back - 9, GOLD)
    fist(cv, lx - 1, back - 5, IRON)


def silver_hand(cv, cx=MID_X - 2, fy=FY):
    """Order knight: barded grey charger, rider in a closed helm with a tall plume, shield and war hammer."""
    cv.shadow(cx + 1, 14)
    back = horse(cv, cx, fy, GREYH)
    caparison(cv, cx, back)
    chanfron(cv, cx, back)
    lx = cx + 9
    pole(cv, lx, 7, back - 1, IRON)
    hm = cv.part()
    cv.rows(hm, [(3, lx - 2, lx + 3), (4, lx - 3, lx + 3), (5, lx - 3, lx + 3), (6, lx - 2, lx + 3)], lit(STEEL, dark_from=lx + 2, light_to=lx - 1, light_rows=4))
    bd = cv.part(sep=False)
    cv.rect(bd, lx, 3, lx, 6, GOLD[1])
    ht = rider(cv, cx, back)
    rein_arm(cv, cx, back, STEEL)
    great_helm(cv, cx, ht)
    plume(cv, cx, ht, 1)
    pauldron(cv, cx - 8, back - 9, STEEL)
    pauldron(cv, cx + 3, back - 9, STEEL)
    tr = cv.part(sep=False)
    cv.rect(tr, cx - 8, back - 6, cx - 4, back - 6, GOLD[1])
    cv.rect(tr, cx + 3, back - 6, cx + 7, back - 6, GOLD[1])
    fist(cv, lx - 1, back - 5, IRON)


def mounted_archer(cv, cx=MID_X - 4, fy=FY):
    """Horse archer: hooded rider, quiver at the saddle, short bow drawn over the horse's neck."""
    cv.shadow(cx + 1, 14)
    back = horse(cv, cx, fy, BLACKH)
    blanket(cv, cx, back)
    q = cv.part()
    cv.rect(q, cx - 8, back - 4, cx - 6, back + 1, lit(LEATHER, dark_from=cx - 6, light_to=cx - 8))
    fl = cv.part(1, sep=False)
    cv.rect(fl, cx - 8, back - 5, cx - 6, back - 5, TINT[0])
    ht = rider(cv, cx, back, leg_r=TAN, boot_r=LEATHER, torso_r=TAN, layer=0, belt_layer=1)
    hood(cv, cx, ht, 2)
    bow(cv, cx, back - 10, sleeve=LEATHER, h=6)


# ================================================================ machines (centre of the tile)
def ballista(cv, cx=MID_X, fy=FY):
    """Ballista: a great crossbow on a wheeled frame, bolt loaded, raised to shoot."""
    cv.shadow(cx, 14)
    fr = cv.part()
    cv.rect(fr, cx - 11, fy - 9, cx + 11, fy - 8, WOOD[2])
    ps = cv.part()
    cv.rect(ps, cx + 3, fy - 16, cx + 5, fy - 9, lit(WOOD, dark_from=cx + 5, light_to=cx + 3))
    bx, by = cx + 7, fy - 19                                                            # bow arms
    sg = cv.part(sep=False)
    cv.pix(sg, line(bx - 3, by - 9, cx - 8, fy - 12) + line(bx - 3, by + 9, cx - 8, fy - 12), STRING)
    bw = cv.part()
    arc = [(bx - 3, by - 9), (bx - 2, by - 8), (bx - 1, by - 7), (bx, by - 6), (bx, by - 5)] + [(bx + 1, y) for y in range(by - 4, by + 5)] + \
          [(bx, by + 5), (bx, by + 6), (bx - 1, by + 7), (bx - 2, by + 8), (bx - 3, by + 9)]
    cv.pix(bw, arc + [(x + 1, y) for x, y in arc], WOOD[1])
    cv.pix(bw, arc[:9], WOOD[0])
    cv.pix(bw, [(bx - 3, by - 9), (bx - 2, by - 9), (bx - 3, by + 9), (bx - 2, by + 9)], STEEL[0])
    stk = cv.part()                                                                    # stock, rising to the right
    pts = []
    for i in range(0, 24):
        x = cx - 11 + i
        y = fy - 11 - i // 2
        pts += [(x, y), (x, y + 1)]
    cv.pix(stk, pts, WOOD[1])
    cv.pix(stk, pts[::2], WOOD[0])
    bl = cv.part()                                                                     # bolt
    bp = [(cx - 7 + i, fy - 14 - i // 2) for i in range(0, 24)]
    cv.pix(bl, bp, TAN[0])
    cv.pix(bl, bp[-4:], STEEL[0])
    fl = cv.part(1)
    cv.pix(fl, [(cx - 8, fy - 14), (cx - 8, fy - 15), (cx - 7, fy - 15)], TINT[0])
    bm = cv.part()
    cv.rect(bm, cx - 12, fy - 8, cx + 12, fy - 5, lit(WOOD, dark_from=cx + 11, light_to=cx + 10, light_rows=fy - 8))
    cv.rect(bm, cx - 12, fy - 5, cx + 12, fy - 5, WOOD[2])
    pl = cv.part(2)
    cv.rows(pl, [(fy - 12, cx - 3, cx + 2), (fy - 11, cx - 3, cx + 2), (fy - 10, cx - 3, cx + 2), (fy - 9, cx - 3, cx + 2), (fy - 8, cx - 2, cx + 1), (fy - 7, cx - 1, cx)],
            lit(TINT, dark_from=cx + 1, light_to=cx - 2, light_rows=fy - 11))
    bs = cv.part(1, sep=False)
    cv.rect(bs, cx - 3, fy - 12, cx + 2, fy - 11, lit(TINT, dark_from=cx + 1))
    wheel(cv, cx - 8, fy)
    wheel(cv, cx + 8, fy)


def mortar_team(cv, cx=MID_X, fy=FY):
    """Mortar crew: a squat iron mortar on a timber bed, gunner in a kettle hat with the next shell."""
    cv.shadow(cx, 15)
    gx = cx - 10                                                                       # gunner
    hang(cv, gx - 6, fy, TINT, layer=2)
    base(cv, gx, fy, legs_r=LEATHER, torso_r=TINT, layer=2, belt_r=LEATHER)
    ap = cv.part()
    cv.rect(ap, gx - 2, fy - 12, gx + 2, fy - 5, lit(LEATHER, dark_from=gx + 2, light_to=gx - 2, light_rows=fy - 10))
    kettle(cv, gx, fy - T)
    b = cv.part(sep=False)
    cv.rows(b, [(fy - T + 5, gx - 1, gx + 3), (fy - T + 6, gx - 1, gx + 2)], HAIR[1])
    arm(cv, gx + 4, fy - 14, TINT, length=3, hand=False, layer=2)
    sh = cv.part()                                                                     # shell in his hands
    cv.rows(sh, [(fy - 13, gx + 6, gx + 8), (fy - 12, gx + 5, gx + 9), (fy - 11, gx + 5, gx + 9), (fy - 10, gx + 5, gx + 9), (fy - 9, gx + 6, gx + 8)],
            lit(BLACKH, dark_from=gx + 8, light_to=gx + 6, light_rows=fy - 12))
    fist(cv, gx + 4, fy - 9)
    mx = cx + 8
    bed = cv.part()
    cv.rect(bed, mx - 8, fy - 4, mx + 8, fy, lit(WOOD, dark_from=mx + 7, light_to=mx + 6, light_rows=fy - 4))
    cv.rect(bed, mx - 8, fy, mx + 8, fy, WOOD[2])
    br = cv.part()                                                                     # barrel, leaning forward
    rows = [(fy - 5 - k, mx - 5 + (k + 1) // 2, mx + 2 + (k + 1) // 2) for k in range(0, 12)]
    cv.rows(br, rows, IRON[1])
    for (y, a, b2) in rows:
        cv.rect(br, a, y, a + 1, y, IRON[0])
        cv.rect(br, b2 - 1, y, b2, y, IRON[2])
    mz = cv.part()
    cv.rows(mz, [(fy - 17, mx, mx + 9), (fy - 18, mx + 1, mx + 10)], lit(IRON, dark_from=mx + 8, light_to=mx + 3))
    bd = cv.part(1, sep=False)
    y, a, b2 = rows[5]
    cv.rect(bd, a, y, b2, y, lit(TINT, dark_from=b2 - 1))
    y, a, b2 = rows[6]
    cv.rect(bd, a, y, b2, y, lit(TINT, dark_from=b2 - 1))
    pv = cv.part(sep=False)
    cv.rect(pv, mx - 1, fy - 6, mx + 1, fy - 5, STEEL[0])
    pl = cv.part(2)
    cv.rect(pl, mx - 6, fy - 3, mx + 6, fy - 2, lit(TINT, dark_from=mx + 5, light_to=mx - 4))


def steam_tank(cv, cx=MID_X + 1, fy=FY):
    """Steam tank: a riveted iron hull on three wheels, cabin and smoking stack, cannon forward, ram on the prow."""
    cv.shadow(cx, 16)
    top = fy - 15
    sm = cv.part()                                                                     # smoke
    cv.rows(sm, [(top - 12, cx - 14, cx - 11), (top - 11, cx - 15, cx - 10), (top - 10, cx - 14, cx - 10), (top - 9, cx - 12, cx - 9)],
            lit(SMOKE, dark_from=cx - 10, light_to=cx - 13, light_rows=top - 11))
    stk = cv.part()                                                                    # stack
    cv.rect(stk, cx - 12, top - 6, cx - 10, top - 1, lit(IRON, dark_from=cx - 10, light_to=cx - 12))
    cv.rect(stk, cx - 13, top - 7, cx - 9, top - 7, IRON[0])
    gn = cv.part()                                                                     # cannon
    cv.rect(gn, cx, top - 4, cx + 13, top - 3, IRON[1])
    cv.rect(gn, cx, top - 4, cx + 13, top - 4, IRON[0])
    cv.rect(gn, cx + 12, top - 5, cx + 13, top - 2, IRON[2])
    cb = cv.part()                                                                     # cabin
    cv.rows(cb, [(top - 6, cx - 7, cx + 1)] + [(y, cx - 8, cx + 2) for y in range(top - 5, top)], lit(STEEL, dark_from=cx + 1, light_to=cx - 6, light_rows=top - 5))
    sl = cv.part(sep=False)
    cv.rect(sl, cx - 2, top - 4, cx + 1, top - 4, DARK)
    rf = cv.part(1, sep=False)
    cv.rect(rf, cx - 7, top - 6, cx + 1, top - 6, lit(TINT, dark_from=cx))
    hl = cv.part()                                                                     # hull
    rows = [(top, cx - 13, cx + 8), (top + 1, cx - 13, cx + 9), (top + 2, cx - 13, cx + 10)] + [(y, cx - 13, cx + 11) for y in range(top + 3, fy - 5)] + \
           [(fy - 5, cx - 12, cx + 10), (fy - 4, cx - 11, cx + 9)]
    cv.rows(hl, rows, lit(STEEL, dark_from=cx + 9, light_to=cx + 7, light_rows=top + 1))
    cv.rows(hl, [(fy - 5, cx - 12, cx + 10), (fy - 4, cx - 11, cx + 9)], STEEL[2])
    sm2 = cv.part(sep=False)                                                           # plate seams and rivets
    cv.rect(sm2, cx - 6, top + 1, cx - 6, fy - 6, STEEL[2])
    cv.rect(sm2, cx + 5, top + 1, cx + 5, fy - 6, STEEL[2])
    cv.pix(sm2, [(cx - 11, top + 1), (cx - 8, top + 1), (cx + 7, top + 1), (cx - 11, fy - 7), (cx - 8, fy - 7), (cx + 7, fy - 7), (cx + 9, fy - 7)], IRON[2])
    pn = cv.part(2, sep=False)                                                         # colour panel
    cv.rect(pn, cx - 4, top + 2, cx + 3, fy - 7, lit(TINT, dark_from=cx + 2, light_to=cx - 2, light_rows=top + 4))
    ch = cv.part(1, sep=False)
    cv.rect(ch, cx - 4, top + 2, cx + 3, top + 3, lit(TINT, dark_from=cx + 2))
    rm = cv.part()                                                                     # ram
    cv.rows(rm, [(fy - 9, cx + 12, cx + 12), (fy - 8, cx + 12, cx + 14), (fy - 7, cx + 12, cx + 13), (fy - 6, cx + 12, cx + 12)], lit(IRON, dark_from=cx + 13))
    for wx in (cx - 9, cx - 1, cx + 7):
        iron_wheel(cv, wx, fy)


UA.SPRITES.update({
    "Settler-Humans": settler, "Great Artist-Humans": great_artist, "Great Merchant-Humans": great_merchant,
    "Great Engineer-Humans": great_engineer, "Great Prophet-Humans": great_prophet, "Great General-Humans": great_general,
    "Inquisitor-Humans": inquisitor, "Archmage": archmage, "Northshire Cleric": cleric,
    "Scout-Humans": scout, "Militia-Humans": militia, "Spearman-Humans": spearman, "Pikeman-Humans": pikeman,
    "Halberdier-Humans": halberdier, "Vanguard-Humans": vanguard, "Man-at-Arms-Humans": man_at_arms,
    "Royal Guard-Humans": royal_guard, "Gladiator-Humans": gladiator, "Vanquisher-Humans": vanquisher,
    "Warbringer-Humans": warbringer, "Kul Tiran Marine-Humans": marine, "Skyguard-Humans": skyguard,
    "Siegebreaker-Humans": siegebreaker, "Phalanx-Humans": phalanx,
    "Hunter-Humans": hunter, "Ranger-Humans": ranger, "Ranger Captain-Humans": ranger_captain,
    "Ranger-General-Humans": ranger_general, "Mounted Archer-Humans": mounted_archer, "Kirin Tor Magus": magus,
    "Rifleman-Humans": rifleman, "Mountaineer-Humans": mountaineer, "Grenadier-Humans": grenadier,
    "Azerite Sharpshooter-Humans": sharpshooter,
    "Outrider-Humans": outrider, "Lancer-Humans": lancer, "War Rider-Humans": war_rider, "Paladin": paladin,
    "Cavalry-Humans": silver_hand,
    "Ballista-Humans": ballista, "Mortar Team-Humans": mortar_team, "Steam Tank": steam_tank,
})
