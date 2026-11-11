"""Hand-placed pixel-art unit sprites (trial: six Human units).

Each sprite is drawn straight onto the art-pixel grid (47 x 40 art pixels, shown at
4 canvas pixels each, the same grid the other unit sprites end up on), instead of
being painted large and reduced. That keeps every pixel deliberate:

  * whole-pixel shapes only, with one consistent art-pixel size for every unit
    (rider and horse are the same scale as a footman);
  * chunky, readable proportions: big head and hands, wide shoulders, short legs,
    weapons and tools held clear of the head so their silhouette stays separate;
  * three-tone ramps per material, lit from the top left, with shadows shifted
    towards blue and lights towards yellow;
  * one 1-px dark silhouette line around the whole figure, added outside the shapes
    so it never eats into them; where one part overlaps another, the part behind
    gets a 1-px contact shadow in its own darkened colour instead of a black line;
  * nation colours on big simple areas (tabard, shield, mantle, caparison): layer 1
    takes the nation's inner colour, layer 2 its outer colour, as in Unciv.

The designs are original and follow only the broad principles of the Warcraft look.
"""
import os
from PIL import Image

GW, GH, BLOCK = 47, 40, 4
CANVAS = (190, 162)
INK = (14, 11, 10)
SHADOW = (40, 40, 40, 95)
FY = 31                       # feet row
CIV_X, MIL_X, MID_X = 10, 36, 23

# ---------------------------------------------------------------- ramps (light, mid, dark)
SKIN = ((246, 200, 154), (216, 152, 112), (158, 98, 84))
HAIR = ((150, 100, 54), (106, 66, 38), (70, 42, 34))
BLOND = ((250, 222, 130), (214, 168, 78), (156, 108, 56))
STEEL = ((232, 238, 244), (172, 184, 204), (104, 114, 148))
LEATHER = ((184, 126, 74), (136, 86, 52), (90, 54, 44))
TAN = ((232, 208, 160), (196, 164, 116), (142, 110, 90))
WHITE = ((250, 248, 240), (212, 212, 220), (150, 152, 182))
WOOD = ((196, 146, 88), (150, 102, 60), (102, 66, 48))
GOLD = ((255, 230, 120), (228, 172, 62), (160, 104, 44))
IRON = ((150, 150, 160), (104, 102, 116), (66, 62, 80))
HORSE = ((176, 116, 70), (132, 80, 48), (88, 50, 40))
STONE = ((200, 198, 190), (150, 148, 150), (100, 98, 112))
TINT = ((245, 245, 245), (188, 188, 188), (131, 131, 131))     # greys, multiplied by a nation colour
DARK = (46, 34, 34)
GLOW = ((255, 255, 220), (255, 236, 150), (250, 200, 90))


def shade(c, k):
    return tuple(max(0, min(255, int(round(v * k)))) for v in c)


class Canvas:
    """A label map: each art pixel remembers the part drawn on it last and its colour."""

    def __init__(self, gw=GW, gh=GH):
        self.gw, self.gh = gw, gh
        self.lab = [[-1] * gw for _ in range(gh)]
        self.col = [[None] * gw for _ in range(gh)]
        self.meta = []
        self.shadows = []

    def part(self, layer=0, sep=True):
        """Start a part. layer 0 = fixed colours, 1 = inner nation colour, 2 = outer.
        sep=False marks a detail drawn onto a part (an eye, a rivet): no contact shadow."""
        self.meta.append((layer, sep))
        return len(self.meta) - 1

    def put(self, s, x, y, c):
        if 0 <= x < self.gw and 0 <= y < self.gh:
            self.lab[y][x] = s
            self.col[y][x] = tuple(c(x, y) if callable(c) else c)

    def rect(self, s, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.put(s, x, y, c)

    def rows(self, s, rows, c):
        for y, a, b in rows:
            for x in range(a, b + 1):
                self.put(s, x, y, c)

    def pix(self, s, pts, c):
        for x, y in pts:
            self.put(s, x, y, c)

    def shadow(self, cx, rx, y=FY):
        self.shadows.append((cx, y, rx))

    # ------------------------------------------------------------ output
    def grids(self):
        gw, gh, lab, meta = self.gw, self.gh, self.lab, self.meta
        out = [Image.new("RGBA", (gw, gh), (0, 0, 0, 0)) for _ in range(3)]
        px = [o.load() for o in out]
        N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
        for y in range(gh):
            for x in range(gw):
                l = lab[y][x]
                if l < 0:
                    continue
                c = self.col[y][x]
                if meta[l][1]:
                    for dx, dy in N4:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < gw and 0 <= ny < gh and lab[ny][nx] > l and meta[lab[ny][nx]][1]:
                            c = shade(c, 0.62)             # contact shadow under the part in front
                            break
                px[meta[l][0]][x, y] = tuple(c) + (255,)
        ring = set()
        for y in range(gh):
            for x in range(gw):
                if lab[y][x] < 0 and any(0 <= x + dx < gw and 0 <= y + dy < gh and lab[y + dy][x + dx] >= 0
                                         for dx, dy in N4):
                    ring.add((x, y))
        for cx, cy, rx in self.shadows:
            for y in (cy, cy + 1):
                w = rx if y == cy else rx - 2
                for x in range(cx - w, cx + w + 1):
                    if 0 <= x < gw and 0 <= y < gh and lab[y][x] < 0 and (x, y) not in ring:
                        px[0][x, y] = SHADOW
        for x, y in ring:
            px[0][x, y] = INK + (255,)
        return out

    def layers(self):
        res = []
        for g in self.grids():
            big = g.resize((self.gw * BLOCK, self.gh * BLOCK), Image.NEAREST)
            c = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
            c.paste(big, (0, 0))
            res.append(c)
        return res


# ---------------------------------------------------------------- shading helpers
def line(x0, y0, x1, y1):
    """Bresenham line: one pixel per step."""
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err, out = dx + dy, []
    while True:
        out.append((x0, y0))
        if x0 == x1 and y0 == y1:
            return out
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def lit(ramp, dark_from=None, light_to=None, light_rows=None):
    """Mid tone; dark from column `dark_from` rightwards; light up to column `light_to`
    (only on rows up to `light_rows` when given)."""
    L, M, D = ramp
    def f(x, y):
        if dark_from is not None and x >= dark_from:
            return D
        if light_to is not None and x <= light_to and (light_rows is None or y <= light_rows):
            return L
        return M
    return f


# ---------------------------------------------------------------- figure parts (facing right)
def boots(cv, cx, fy, ramp=LEATHER):
    for x0 in (cx - 5, cx + 1):
        s = cv.part()
        cv.rect(s, x0, fy - 2, x0 + 4, fy, lit(ramp, dark_from=x0 + 3, light_to=x0 + 1, light_rows=fy - 2))
        cv.rect(s, x0, fy, x0 + 4, fy, ramp[2])                 # sole


def legs(cv, cx, fy, ramp):
    for x0 in (cx - 4, cx + 1):
        s = cv.part()
        cv.rect(s, x0, fy - 6, x0 + 3, fy - 3, lit(ramp, dark_from=x0 + 3, light_to=x0))


def torso(cv, cx, fy, ramp, layer=0, w=4, top=None):
    top = fy - 15 if top is None else top
    s = cv.part(layer)
    cv.rect(s, cx - w, top, cx + w, fy - 8, lit(ramp, dark_from=cx + w - 1, light_to=cx - w + 1, light_rows=top + 3))
    return s


def belt(cv, cx, fy, ramp=LEATHER, buckle=GOLD, w=4, layer=0):
    s = cv.part(sep=False)
    cv.rect(s, cx - w, fy - 7, cx + w, fy - 7, lit(ramp, dark_from=cx + w - 1))
    b = cv.part(layer, sep=False)
    cv.put(b, cx, fy - 7, buckle[0] if layer == 0 else TINT[0])


def arm(cv, x, top, ramp, length=6, layer=0, hand=True, hand_ramp=SKIN):
    """A 3-px arm hanging from row `top`, with a 3x3 fist under it."""
    s = cv.part(layer)
    cv.rect(s, x, top, x + 2, top + length - 1, lit(ramp, dark_from=x + 2, light_to=x, light_rows=top + 1))
    if hand:
        fist(cv, x, top + length, hand_ramp)


def fist(cv, x, y, ramp=SKIN):
    h = cv.part()
    cv.rect(h, x, y, x + 2, y + 2, lit(ramp, dark_from=x + 2, light_to=x, light_rows=y))
    cv.put(h, x + 2, y + 2, ramp[2])


def head(cv, cx, top, skin=SKIN):
    """A 7x7 head with rounded corners, eyes looking right."""
    s = cv.part()
    rows = [(top, cx - 2, cx + 2)] + [(y, cx - 3, cx + 3) for y in range(top + 1, top + 6)] + [(top + 6, cx - 2, cx + 2)]
    cv.rows(s, rows, lit(skin, dark_from=cx + 3, light_to=cx - 1, light_rows=top + 3))
    cv.rows(s, [(top + 6, cx - 2, cx + 2)], skin[2])
    cv.rows(s, [(top + 5, cx - 3, cx + 3)], lit(skin, dark_from=cx + 2))
    e = cv.part(sep=False)
    cv.pix(e, [(cx, top + 3), (cx + 2, top + 3)], DARK)
    return s


def pauldron(cv, x, y, ramp, layer=0, w=5):
    s = cv.part(layer)
    cv.rows(s, [(y, x + 1, x + w - 2), (y + 1, x, x + w - 1), (y + 2, x, x + w - 1), (y + 3, x, x + w - 1)],
            lit(ramp, dark_from=x + w - 1, light_to=x + 1, light_rows=y + 1))
    cv.rows(s, [(y + 3, x, x + w - 1)], ramp[2])
    return s


# ---------------------------------------------------------------- units
def peasant(cv, cx=CIV_X - 1, fy=FY):
    """Village labourer: cap, short beard, rolled sleeves, nation-colour mantle, pickaxe
    held out in front so its head stays clear of his own."""
    cv.shadow(cx, 7)
    arm(cv, cx - 6, fy - 14, TAN, length=5)                     # back arm (sleeve), fist at the hip
    boots(cv, cx, fy)
    legs(cv, cx, fy, LEATHER)
    torso(cv, cx, fy, TAN)
    belt(cv, cx, fy, ramp=IRON)
    a = cv.part()                                                 # leather work apron
    cv.rect(a, cx - 2, fy - 12, cx + 2, fy - 5, lit(LEATHER, dark_from=cx + 2, light_to=cx - 2, light_rows=fy - 10))
    m = cv.part(2)                                                # mantle over the shoulders: outer colour
    cv.rows(m, [(fy - 16, cx - 5, cx + 5), (fy - 15, cx - 6, cx + 6), (fy - 14, cx - 6, cx + 6), (fy - 13, cx - 5, cx + 5)],
            lit(TINT, dark_from=cx + 4, light_to=cx - 3, light_rows=fy - 15))
    t = cv.part(1, sep=False)                                     # clasp: inner colour
    cv.put(t, cx, fy - 14, TINT[0])
    head(cv, cx, fy - 23)
    b = cv.part(sep=False)                                        # short beard and moustache
    cv.rows(b, [(fy - 19, cx - 1, cx + 3), (fy - 18, cx - 3, cx + 3), (fy - 17, cx - 2, cx + 2)], lit(HAIR, dark_from=cx + 2))
    cv.pix(b, [(cx - 3, fy - 20), (cx - 3, fy - 19)], HAIR[1])
    c = cv.part()                                                 # cloth cap
    cv.rows(c, [(fy - 25, cx - 2, cx + 1), (fy - 24, cx - 3, cx + 3), (fy - 23, cx - 4, cx + 3), (fy - 22, cx - 4, cx - 2)],
            lit(LEATHER, dark_from=cx + 2, light_to=cx - 1, light_rows=fy - 24))
    # pickaxe: haft upright in the front fist, head pointing away from him
    h = cv.part()
    cv.rect(h, cx + 8, fy - 20, cx + 8, fy - 1, WOOD[1])
    cv.rect(h, cx + 8, fy - 20, cx + 8, fy - 14, WOOD[0])
    p = cv.part()
    cv.rows(p, [(fy - 22, cx + 6, cx + 11), (fy - 21, cx + 5, cx + 12), (fy - 20, cx + 5, cx + 5), (fy - 20, cx + 12, cx + 13),
                (fy - 19, cx + 13, cx + 13)], lit(STEEL, dark_from=cx + 10, light_to=cx + 7, light_rows=fy - 22))
    arm(cv, cx + 4, fy - 14, TAN, length=3, hand=False)           # front arm reaching to the haft
    f = cv.part()
    cv.rect(f, cx + 5, fy - 11, cx + 6, fy - 10, SKIN[1])
    fist(cv, cx + 7, fy - 12)


def kite(cv, x, top, w=9, h=12):
    """A kite shield in the outer colour with a chief (top band) and stud in the inner colour."""
    sh = cv.part(2)
    rows = [(top, x + 1, x + w - 2)] + [(y, x, x + w - 1) for y in range(top + 1, top + h - 4)]
    k = 1
    for y in range(top + h - 4, top + h):
        rows.append((y, x + k, x + w - 1 - k))
        k += 1
    cv.rows(sh, rows, lit(TINT, dark_from=x + w - 3, light_to=x + 2, light_rows=top + h - 6))
    ch = cv.part(1, sep=False)
    cv.rows(ch, [(top, x + 1, x + w - 2), (top + 1, x, x + w - 1), (top + 2, x, x + w - 1)], lit(TINT, dark_from=x + w - 3))
    cv.rect(ch, x + w // 2, top + 5, x + w // 2, top + 6, TINT[0])
    cv.rect(ch, x + w // 2 - 1, top + 5, x + w // 2 + 1, top + 5, TINT[0])


def footman(cv, cx=MIL_X - 1, fy=FY):
    """Heavy infantry: full helm with a crest, big pauldrons, tabard and kite shield in
    the nation's colours, sword held upright at his side."""
    cv.shadow(cx, 8)
    bl = cv.part()                                                                     # sword, clear of the helm
    cv.rect(bl, cx - 9, fy - 27, cx - 8, fy - 14, lit(STEEL, dark_from=cx - 8))
    cv.put(bl, cx - 9, fy - 28, STEEL[0])
    g = cv.part(1)
    cv.rect(g, cx - 11, fy - 13, cx - 6, fy - 13, lit(TINT, dark_from=cx - 7))        # crossguard: inner colour
    cv.rect(g, cx - 9, fy - 9, cx - 8, fy - 9, TINT[1])                                # pommel
    arm(cv, cx - 8, fy - 15, STEEL, length=3, hand=False)
    fist(cv, cx - 10, fy - 12, IRON)                                                   # gauntlet on the grip
    boots(cv, cx, fy, IRON)
    legs(cv, cx, fy, STEEL)
    tb = cv.part(2)                                                                    # tabard: outer colour
    cv.rect(tb, cx - 4, fy - 15, cx + 4, fy - 7, lit(TINT, dark_from=cx + 3, light_to=cx - 3, light_rows=fy - 12))
    cv.rows(tb, [(fy - 6, cx - 4, cx - 1), (fy - 6, cx + 1, cx + 4)], TINT[2])
    bt = cv.part(sep=False)
    cv.rect(bt, cx - 4, fy - 9, cx + 4, fy - 9, lit(LEATHER, dark_from=cx + 3))
    bk = cv.part(1, sep=False)
    cv.put(bk, cx, fy - 9, TINT[0])
    head_top = fy - 23
    hm = cv.part()                                                                     # great helm
    cv.rows(hm, [(head_top - 1, cx - 2, cx + 2)] + [(y, cx - 3, cx + 3) for y in range(head_top, head_top + 7)],
            lit(STEEL, dark_from=cx + 2, light_to=cx - 2, light_rows=head_top + 1))
    v = cv.part(sep=False)
    cv.rect(v, cx - 1, head_top + 3, cx + 3, head_top + 3, DARK)                       # eye slit
    cv.rect(v, cx + 1, head_top + 4, cx + 1, head_top + 6, STEEL[2])
    cr = cv.part(1)                                                                    # crest: inner colour
    cv.rows(cr, [(head_top - 3, cx - 2, cx), (head_top - 2, cx - 3, cx + 1), (head_top - 1, cx - 4, cx - 3), (head_top, cx - 4, cx - 4)],
            lit(TINT, dark_from=cx, light_to=cx - 2, light_rows=head_top - 3))
    pauldron(cv, cx - 8, fy - 17, STEEL)
    pauldron(cv, cx + 3, fy - 17, STEEL)
    kite(cv, cx + 2, fy - 15)


def archer(cv, cx=MIL_X - 4, fy=FY):
    """Bowman: hood and short cape in the nation's colour, leather jerkin, longbow held
    out in front with an arrow drawn, quiver on the back."""
    cv.shadow(cx + 1, 9)
    q = cv.part()                                                                      # quiver behind the shoulder
    cv.rect(q, cx - 8, fy - 19, cx - 6, fy - 14, lit(LEATHER, dark_from=cx - 6, light_to=cx - 8))
    fl = cv.part(1, sep=False)                                                         # fletchings: inner colour
    cv.rect(fl, cx - 8, fy - 20, cx - 6, fy - 20, lit(TINT, dark_from=cx - 6))
    ft = cv.part()
    cv.pix(ft, [(cx - 8, fy - 21), (cx - 6, fy - 21)], WHITE[0])
    cp = cv.part(2)                                                                    # cape down the back
    cv.rows(cp, [(y, cx - 6, cx - 3) for y in range(fy - 15, fy - 7)] + [(fy - 7, cx - 6, cx - 4)],
            lit(TINT, dark_from=cx - 4, light_to=cx - 6, light_rows=fy - 12))
    boots(cv, cx, fy)
    legs(cv, cx, fy, TAN)
    torso(cv, cx, fy, LEATHER)
    belt(cv, cx, fy, ramp=IRON)
    hs = head(cv, cx, fy - 23)
    cv.rows(hs, [(y, cx - 1, cx + 2) for y in range(fy - 21, fy - 18)], SKIN[0])        # face lit under the hood
    e = cv.part(sep=False)
    cv.pix(e, [(cx, fy - 20), (cx + 2, fy - 20)], DARK)
    hd = cv.part(2)                                                                    # hood: outer colour
    ht = fy - 24
    cv.rows(hd, [(ht - 1, cx - 2, cx + 1), (ht, cx - 3, cx + 2), (ht + 1, cx - 4, cx + 3), (ht + 2, cx - 4, cx - 1), (ht + 3, cx - 4, cx - 2),
                 (ht + 4, cx - 4, cx - 2), (ht + 5, cx - 4, cx - 2), (ht + 6, cx - 4, cx - 3), (ht + 7, cx - 5, cx - 2), (ht + 8, cx - 5, cx + 4)],
            lit(TINT, dark_from=cx + 2, light_to=cx - 2, light_rows=ht + 1))
    # bow: a tall arc held out in front, string drawn back to the chest, arrow across
    bx, by = cx + 11, fy - 13
    sg = cv.part(sep=False)                                                            # string
    cv.pix(sg, line(bx - 2, by - 9, cx + 3, by - 1) + line(cx + 3, by - 1, bx - 2, by + 9), (238, 234, 222))
    bw = cv.part()
    arc = [(bx - 2, by - 9), (bx - 1, by - 8), (bx, by - 7), (bx, by - 6), (bx + 1, by - 5), (bx + 1, by - 4), (bx + 1, by - 3), (bx + 1, by - 2),
           (bx + 1, by - 1), (bx + 1, by), (bx + 1, by + 1), (bx + 1, by + 2), (bx + 1, by + 3), (bx + 1, by + 4), (bx + 1, by + 5),
           (bx, by + 6), (bx, by + 7), (bx - 1, by + 8), (bx - 2, by + 9)]
    cv.pix(bw, arc, WOOD[1])
    cv.pix(bw, arc[:7], WOOD[0])
    sl = cv.part()                                                                     # bow arm: sleeve straight out
    cv.rect(sl, cx + 4, by, bx - 3, by + 1, lit(LEATHER, dark_from=bx - 4, light_to=bx - 5, light_rows=by))
    ar = cv.part()                                                                     # arrow lying along the arm
    cv.rect(ar, cx + 4, by - 1, bx + 1, by - 1, WOOD[0])
    cv.pix(ar, [(bx + 2, by - 1), (bx + 3, by - 1)], STEEL[0])
    fist(cv, bx - 2, by - 1)
    fist(cv, cx + 1, by - 1)                                                           # drawing hand at the chest


def priest(cv, cx=CIV_X + 1, fy=FY):
    """Cleric: long white robe, mantle and stole in the nation's colours, staff with a
    glowing sunburst held upright in front."""
    cv.shadow(cx, 7)
    rb = cv.part()                                                                     # robe, flaring to the hem
    rows = [(y, cx - 4, cx + 4) for y in range(fy - 15, fy - 7)] + [(y, cx - 5, cx + 5) for y in range(fy - 7, fy - 2)] + \
           [(fy - 2, cx - 6, cx + 6), (fy - 1, cx - 6, cx + 6), (fy, cx - 6, cx + 6)]
    cv.rows(rb, rows, lit(WHITE, dark_from=cx + 3, light_to=cx - 3, light_rows=fy - 4))
    cv.rows(rb, [(fy, cx - 6, cx + 6)], WHITE[2])
    stl = cv.part(1, sep=False)                                                        # stole down the front: inner colour
    cv.rect(stl, cx - 1, fy - 13, cx + 1, fy - 3, lit(TINT, dark_from=cx + 1, light_to=cx - 1, light_rows=fy - 8))
    cv.rect(stl, cx - 6, fy - 1, cx + 6, fy - 1, lit(TINT, dark_from=cx + 4))          # hem band
    arm(cv, cx - 6, fy - 14, WHITE, length=5)                                          # back arm at the side
    mt = cv.part(2)                                                                    # mantle: outer colour
    cv.rows(mt, [(fy - 16, cx - 5, cx + 5), (fy - 15, cx - 6, cx + 6), (fy - 14, cx - 6, cx + 6), (fy - 13, cx - 6, cx - 2), (fy - 13, cx + 2, cx + 6)],
            lit(TINT, dark_from=cx + 4, light_to=cx - 3, light_rows=fy - 15))
    head(cv, cx, fy - 23)
    hr = cv.part(sep=False)                                                            # tonsured blond hair
    cv.rows(hr, [(fy - 23, cx - 2, cx + 2), (fy - 22, cx - 3, cx + 2), (fy - 21, cx - 3, cx - 2), (fy - 20, cx - 3, cx - 3), (fy - 19, cx - 3, cx - 3)],
            lit(BLOND, dark_from=cx + 1, light_to=cx - 1, light_rows=fy - 23))
    # staff
    sx = cx + 9
    stf = cv.part()
    cv.rect(stf, sx, fy - 21, sx, fy, lit(WOOD, light_to=sx, light_rows=fy - 12))
    sun = cv.part()
    cv.rows(sun, [(fy - 26, sx - 1, sx + 1), (fy - 25, sx - 2, sx + 2), (fy - 24, sx - 2, sx + 2), (fy - 23, sx - 2, sx + 2), (fy - 22, sx - 1, sx + 1)],
            lit(GOLD, dark_from=sx + 2, light_to=sx - 1, light_rows=fy - 25))
    gl = cv.part(sep=False)
    cv.rows(gl, [(fy - 25, sx - 1, sx + 1), (fy - 24, sx - 1, sx + 1), (fy - 23, sx - 1, sx + 1)], GLOW[1])
    cv.put(gl, sx, fy - 24, GLOW[0])
    ry = cv.part(sep=False)                                                            # rays
    cv.pix(ry, [(sx, fy - 28), (sx - 4, fy - 24), (sx + 4, fy - 24), (sx - 3, fy - 27), (sx + 3, fy - 27)], GLOW[1])
    arm(cv, cx + 4, fy - 14, WHITE, length=3, hand=False)                              # front arm to the staff
    f = cv.part()
    cv.rect(f, cx + 5, fy - 11, cx + 7, fy - 10, WHITE[1])
    fist(cv, sx - 1, fy - 12)


def horse(cv, cx, fy, ramp=HORSE):
    """A stocky warhorse facing right, body centred on cx. Returns the row of its back."""
    back = fy - 13
    for x0 in (cx - 8, cx + 5):                                                        # far legs
        s = cv.part()
        cv.rect(s, x0, fy - 7, x0 + 1, fy - 1, ramp[2])
        cv.rect(s, x0, fy, x0 + 2, fy, DARK)
    tl = cv.part()                                                                     # tail
    cv.rows(tl, [(back + 1, cx - 12, cx - 10), (back + 2, cx - 13, cx - 11), (back + 3, cx - 13, cx - 11), (back + 4, cx - 13, cx - 12),
                 (back + 5, cx - 13, cx - 12), (back + 6, cx - 13, cx - 12), (back + 7, cx - 12, cx - 12)], lit(HAIR, dark_from=cx - 11))
    b = cv.part()                                                                      # barrel
    cv.rows(b, [(back, cx - 9, cx + 8)] + [(y, cx - 10, cx + 9) for y in range(back + 1, back + 6)] + [(back + 6, cx - 9, cx + 8)],
            lit(ramp, dark_from=cx + 8, light_to=cx + 7, light_rows=back + 1))
    cv.rows(b, [(back + 5, cx - 10, cx + 9), (back + 6, cx - 9, cx + 8)], ramp[2])
    for x0 in (cx - 10, cx + 6):                                                       # near legs
        s = cv.part()
        cv.rect(s, x0, fy - 7, x0 + 2, fy - 1, lit(ramp, dark_from=x0 + 2, light_to=x0))
        cv.rect(s, x0, fy, x0 + 3, fy, DARK)
    n = cv.part()                                                                      # neck and head
    cv.rows(n, [(back - 7, cx + 8, cx + 12), (back - 6, cx + 7, cx + 14), (back - 5, cx + 7, cx + 16), (back - 4, cx + 6, cx + 17),
                (back - 3, cx + 6, cx + 11), (back - 3, cx + 14, cx + 17), (back - 2, cx + 5, cx + 10), (back - 2, cx + 15, cx + 17),
                (back - 1, cx + 5, cx + 10), (back, cx + 4, cx + 10), (back + 1, cx + 5, cx + 9)],
            lit(ramp, dark_from=cx + 15, light_to=cx + 12, light_rows=back - 5))
    cv.rows(n, [(back - 3, cx + 14, cx + 17), (back - 2, cx + 15, cx + 17)], ramp[2])
    er = cv.part()
    cv.pix(er, [(cx + 9, back - 8), (cx + 11, back - 8)], ramp[1])                     # ears
    d = cv.part(sep=False)
    cv.put(d, cx + 12, back - 5, DARK)                                                 # eye
    cv.put(d, cx + 17, back - 3, DARK)                                                 # nostril
    mn = cv.part(sep=False)                                                            # mane down the back of the neck
    cv.rows(mn, [(back - 7, cx + 8, cx + 8), (back - 6, cx + 7, cx + 8), (back - 5, cx + 7, cx + 8), (back - 4, cx + 6, cx + 7),
                 (back - 3, cx + 6, cx + 7), (back - 2, cx + 5, cx + 6), (back - 1, cx + 5, cx + 6)], HAIR[2])
    return back


def knight(cv, cx=MID_X - 2, fy=FY):
    """Mounted knight: warhorse in a caparison of the nation's colours, rider in plate
    with a plume, lance held upright with a pennant."""
    cv.shadow(cx + 1, 14)
    back = horse(cv, cx, fy)
    cp = cv.part(2)                                                                    # caparison: outer colour
    cv.rows(cp, [(back, cx - 8, cx + 4)] + [(y, cx - 9, cx + 5) for y in range(back + 1, back + 8)] +
                [(back + 8, cx - 9, cx - 6), (back + 8, cx - 3, cx + 5), (back + 9, cx - 2, cx + 4)],
            lit(TINT, dark_from=cx + 4, light_to=cx - 6, light_rows=back + 2))
    tr = cv.part(1, sep=False)                                                         # trim band: inner colour
    cv.rect(tr, cx - 9, back + 6, cx + 5, back + 6, lit(TINT, dark_from=cx + 4))
    # lance: upright in the forward hand, pennant streaming over the horse's head
    lx = cx + 6
    ln = cv.part()
    cv.rect(ln, lx, 3, lx, back - 1, lit(WOOD, light_to=lx, light_rows=back - 8))
    cv.rect(ln, lx, 1, lx, 2, STEEL[0])
    pn = cv.part(2)                                                                    # pennant: outer colour
    cv.rows(pn, [(3, lx + 1, lx + 7), (4, lx + 1, lx + 6), (5, lx + 1, lx + 7), (6, lx + 1, lx + 4)],
            lit(TINT, dark_from=lx + 5, light_to=lx + 3, light_rows=4))
    pt = cv.part(1, sep=False)
    cv.rect(pt, lx + 1, 3, lx + 1, 6, TINT[0])                                         # hoist edge: inner colour
    lg = cv.part()                                                                     # rider's leg and boot
    cv.rect(lg, cx - 2, back - 1, cx + 1, back + 4, lit(STEEL, dark_from=cx + 1, light_to=cx - 2))
    bt = cv.part()
    cv.rect(bt, cx - 2, back + 5, cx + 3, back + 6, lit(IRON, dark_from=cx + 2))
    arm(cv, cx - 7, back - 6, STEEL, length=3, hand=False)                             # rein arm
    fist(cv, cx - 6, back - 3, IRON)
    tb = cv.part(2)                                                                    # surcoat: outer colour
    cv.rect(tb, cx - 4, back - 8, cx + 4, back - 1, lit(TINT, dark_from=cx + 3, light_to=cx - 3, light_rows=back - 5))
    bl = cv.part(1, sep=False)
    cv.rect(bl, cx - 4, back - 2, cx + 4, back - 2, lit(TINT, dark_from=cx + 3))
    ht = back - 15
    hm = cv.part()                                                                     # great helm
    cv.rows(hm, [(ht - 1, cx - 2, cx + 2)] + [(y, cx - 3, cx + 3) for y in range(ht, ht + 7)],
            lit(STEEL, dark_from=cx + 2, light_to=cx - 2, light_rows=ht + 1))
    v = cv.part(sep=False)
    cv.rect(v, cx - 1, ht + 3, cx + 3, ht + 3, DARK)
    cv.rect(v, cx + 1, ht + 4, cx + 1, ht + 6, STEEL[2])
    pl = cv.part(1)                                                                    # plume: inner colour
    cv.rows(pl, [(ht - 3, cx - 3, cx - 1), (ht - 2, cx - 5, cx), (ht - 1, cx - 6, cx - 3), (ht, cx - 6, cx - 4), (ht + 1, cx - 6, cx - 5)],
            lit(TINT, dark_from=cx - 1, light_to=cx - 3, light_rows=ht - 2))
    pauldron(cv, cx - 8, back - 9, STEEL)
    pauldron(cv, cx + 3, back - 9, STEEL)
    fist(cv, lx - 1, back - 5, IRON)                                                   # gauntlet on the lance


def catapult(cv, cx=MID_X, fy=FY):
    """Siege catapult: timber frame on two iron-shod wheels, throwing arm cocked back
    with a stone in the cup, a shield plate in the nation's colours on the frame."""
    cv.shadow(cx, 14)
    fr = cv.part()                                                                     # far side beam
    cv.rect(fr, cx - 11, fy - 9, cx + 11, fy - 8, WOOD[2])
    # throwing arm, cocked back to the left: a 2-px beam climbing one pixel every two columns
    am = cv.part()
    pts = []
    for i in range(0, 20):
        x = cx + 6 - i
        y = fy - 10 - i * 3 // 4
        pts += [(x, y), (x, y + 1)]
    cv.pix(am, pts, WOOD[1])
    cv.pix(am, [p for k, p in enumerate(pts) if k % 2 == 0], WOOD[0])
    cup = cv.part()
    cv.rows(cup, [(fy - 25, cx - 17, cx - 12), (fy - 24, cx - 16, cx - 13)], lit(IRON, dark_from=cx - 13))
    stn = cv.part()
    cv.rows(stn, [(fy - 29, cx - 16, cx - 14), (fy - 28, cx - 17, cx - 13), (fy - 27, cx - 17, cx - 13), (fy - 26, cx - 16, cx - 14)],
            lit(STONE, dark_from=cx - 14, light_to=cx - 16, light_rows=fy - 28))
    for x0 in (cx - 3, cx + 5):                                                        # A-frame uprights
        up = cv.part()
        cv.rect(up, x0, fy - 20, x0 + 2, fy - 9, lit(WOOD, dark_from=x0 + 2, light_to=x0))
    xb = cv.part()                                                                     # crossbar the arm strikes
    cv.rect(xb, cx - 4, fy - 21, cx + 8, fy - 20, lit(WOOD, dark_from=cx + 7, light_to=cx + 6, light_rows=fy - 21))
    bm = cv.part()                                                                     # near side beam
    cv.rect(bm, cx - 12, fy - 8, cx + 12, fy - 5, lit(WOOD, dark_from=cx + 11, light_to=cx + 10, light_rows=fy - 8))
    cv.rect(bm, cx - 12, fy - 5, cx + 12, fy - 5, WOOD[2])
    pl = cv.part(2)                                                                    # shield plate: outer colour
    cv.rows(pl, [(fy - 13, cx - 2, cx + 4), (fy - 12, cx - 2, cx + 4), (fy - 11, cx - 2, cx + 4), (fy - 10, cx - 2, cx + 4), (fy - 9, cx - 1, cx + 3), (fy - 8, cx, cx + 2), (fy - 7, cx + 1, cx + 1)],
            lit(TINT, dark_from=cx + 3, light_to=cx - 1, light_rows=fy - 12))
    bs = cv.part(1, sep=False)                                                         # chief: inner colour
    cv.rect(bs, cx - 2, fy - 13, cx + 4, fy - 12, lit(TINT, dark_from=cx + 3))
    for wx in (cx - 8, cx + 8):                                                        # wheels: 9 px across
        wh = cv.part()
        rows = [(fy - 8, wx - 2, wx + 2), (fy - 7, wx - 3, wx + 3)] + [(y, wx - 4, wx + 4) for y in range(fy - 6, fy - 1)] + \
               [(fy - 1, wx - 3, wx + 3), (fy, wx - 2, wx + 2)]
        cv.rows(wh, rows, IRON[1])
        cv.rows(wh, [(fy - 8, wx - 2, wx + 2), (fy - 7, wx - 3, wx - 2), (fy - 6, wx - 4, wx - 3)], IRON[0])
        cv.rows(wh, [(fy, wx - 2, wx + 2), (fy - 1, wx + 2, wx + 3), (fy - 2, wx + 4, wx + 4)], IRON[2])
        inn = cv.part(sep=False)
        cv.rows(inn, [(fy - 6, wx - 2, wx + 2), (fy - 5, wx - 3, wx + 3), (fy - 4, wx - 3, wx + 3), (fy - 3, wx - 3, wx + 3), (fy - 2, wx - 2, wx + 2)],
                lit(WOOD, dark_from=wx + 2, light_to=wx - 2, light_rows=fy - 5))
        cv.rect(inn, wx - 3, fy - 4, wx + 3, fy - 4, WOOD[2])                          # spokes
        cv.rect(inn, wx, fy - 6, wx, fy - 2, WOOD[2])
        cv.put(inn, wx, fy - 4, IRON[0])                                               # hub


# name -> (function, the stems it replaces)
SPRITES = {
    "Peasant-Humans": peasant, "Footman": footman, "Archer-Humans": archer,
    "Knight-Humans": knight, "Priest": priest, "Catapult-Humans": catapult,
}


def render(name):
    cv = Canvas()
    SPRITES[name](cv)
    return cv.layers()


def write_all(image_dirs, unit_dir="TileSets/AbsoluteUnits/Units/"):
    """Overwrite the trial units' sprites (and their era variants) wherever they exist."""
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
        for folder, stem in targets:
            for suf, im in zip(("", "-1", "-2"), layers):
                im.save(os.path.join(folder, stem + suf + ".png"))
                count += 1
    return count
