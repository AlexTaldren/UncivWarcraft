"""Human city centers and tile improvements in the hand-placed pixel style (trial).

The same rules as the unit sprites (unit_art.py), at tile resolution: whole-pixel shapes,
three-tone ramps lit from the top left, one dark outline added outside the shapes, a
contact shadow where one piece stands in front of another instead of inner black lines.
Fences, ropes and rails are 1-px colour lines without an outline.

Human look: plastered walls on a stone footing with dark timber framing, steep blue slate
roofs, pale stone towers with blue caps and a gold finial. All designs are original.

Importing this module swaps the Human versions into improvement_art and citycenters, so
the rest of the build (snow variants, resource combinations, the 32-px tile set) is unchanged.
"""
import math

from PIL import Image

import unit_art as UA
from unit_art import line

TW, TH = 64, 56
OUT = (30, 24, 22)                # outline colour shared with the other tiles (race_works.snow looks for it)
SHADOW = (30, 34, 30, 90)

PLASTER = ((246, 240, 224), (224, 214, 194), (174, 162, 160))
TIMBER = ((150, 106, 68), (110, 76, 54), (72, 50, 46))
WOOD = ((196, 148, 92), (156, 110, 68), (108, 74, 56))
SLATE = ((98, 138, 218), (54, 90, 174), (34, 54, 120))
STONE = ((222, 220, 212), (184, 182, 180), (132, 130, 144))
ROCK = ((206, 202, 194), (166, 162, 160), (116, 114, 128))
THATCH = ((244, 218, 132), (212, 178, 94), (154, 120, 72))
CANVAS = ((250, 248, 240), (222, 220, 216), (168, 170, 188))
GOLD = ((255, 232, 140), (232, 186, 76), (166, 118, 56))
IRON = ((150, 150, 162), (104, 104, 120), (66, 64, 82))
SOIL = ((150, 108, 70), (118, 84, 52), (84, 58, 44))
PAVE = ((204, 196, 176), (178, 170, 152), (140, 132, 124))
HIDE = ((214, 160, 104), (176, 126, 80), (120, 84, 60))
FLAME = ((255, 244, 160), (255, 176, 64), (224, 96, 44))
WATER = ((232, 246, 252), (150, 206, 232), (104, 168, 210))
RED = ((232, 108, 88), (188, 62, 56), (124, 38, 52))
GLOW = (255, 228, 140)
DARK = (44, 32, 34)


class TC(UA.Canvas):
    """Tile canvas: unit_art's label map, plus 1-px line parts that get no outline."""

    def __init__(self, w=TW, h=TH):
        super().__init__(w, h)
        self.thin = set()
        self.flat = []

    cmap = {}                         # colour -> colour, set by tile_art_races for the other factions' materials

    def put(self, s, x, y, c):
        if 0 <= x < self.gw and 0 <= y < self.gh:
            c = tuple(c(x, y) if callable(c) else c)
            self.lab[y][x] = s
            self.col[y][x] = self.cmap.get(c, c)

    def lines(self):
        p = self.part(sep=False)
        self.thin.add(p)
        return p

    def ground(self, rows, col):
        """A patch painted on the ground under everything: no outline."""
        self.flat.append((rows, col))

    def image(self):
        gw, gh, lab, meta = self.gw, self.gh, self.lab, self.meta
        out = Image.new("RGBA", (gw, gh), (0, 0, 0, 0))
        px = out.load()
        N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
        for rows, col in self.flat:
            for y, a, b in rows:
                for x in range(a, b + 1):
                    if 0 <= x < gw and 0 <= y < gh:
                        c0 = tuple(col(x, y) if callable(col) else col)
                        px[x, y] = self.cmap.get(c0, c0) + (255,)
        solid = lambda l: l >= 0 and l not in self.thin
        for cx, cy, rx in self.shadows:
            for y in (cy, cy + 1):
                w = rx if y == cy else rx - 2
                for x in range(cx - w, cx + w + 1):
                    if 0 <= x < gw and 0 <= y < gh and lab[y][x] < 0:
                        px[x, y] = SHADOW if px[x, y][3] == 0 else tuple(int(v * 0.72) for v in px[x, y][:3]) + (255,)
        for y in range(gh):
            for x in range(gw):
                l = lab[y][x]
                if l < 0:
                    if any(0 <= x + dx < gw and 0 <= y + dy < gh and solid(lab[y + dy][x + dx]) for dx, dy in N4):
                        px[x, y] = OUT + (255,)
                    continue
                c = self.col[y][x]
                if meta[l][1]:
                    for dx, dy in N4:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < gw and 0 <= ny < gh and lab[ny][nx] > l and meta[lab[ny][nx]][1]:
                            c = tuple(int(v * 0.66) for v in c)
                            break
                px[x, y] = tuple(c) + (255,)
        return out


# ---------------------------------------------------------------- raster helpers
def ell_rows(cx, cy, rx, ry, top_only=False):
    out = []
    for y in range(cy - ry, cy + (0 if top_only else ry) + 1):
        t = (y - cy) / (ry + 0.5)
        hw = int(math.floor(rx * math.sqrt(max(0.0, 1 - t * t)) + 0.35))
        out.append((y, cx - hw, cx + hw))
    return out


def poly_rows(pts):
    ys = [p[1] for p in pts]
    rows = []
    for y in range(int(min(ys)), int(max(ys)) + 1):
        xs = []
        n = len(pts)
        for i in range(n):
            (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
            if (y0 <= y + .5 < y1) or (y1 <= y + .5 < y0):
                xs.append(x0 + (y + .5 - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for a, b in zip(xs[::2], xs[1::2]):
            a, b = int(math.floor(a + 0.5)), int(math.floor(b - 0.5))
            if b >= a:
                rows.append((y, a, b))
    return rows


def tone(ramp, x0, x1, top=None, lw=None):
    """Light on the left (and on the top row when given), dark on the right two columns."""
    lw = max(1, (x1 - x0 + 1) // 3) if lw is None else lw
    L, M, D = ramp
    def f(x, y):
        if x >= x1 - 1:
            return D
        if x < x0 + lw or (top is not None and y == top):
            return L
        return M
    return f


# ---------------------------------------------------------------- building parts
def roof(cv, x, eave, w, h, ramp=SLATE):
    """A slate roof seen from the side: ridge at the top, eave row `eave`, one pixel of overhang."""
    r = cv.part()
    rows = []
    for k in range(h):
        ins = h - 1 - k
        rows.append((eave - h + 1 + k, x - 1 + ins, x + w - ins))
    L, M, D = ramp
    def f(xx, yy):
        k = yy - (eave - h + 1)
        a, b = x - 1 + (h - 1 - k), x + w - (h - 1 - k)
        if yy == eave:
            return D
        if k == 0 or xx <= a + 1:
            return L
        if xx >= b - 1:
            return D
        return D if (xx + 2 * yy) % 4 == 0 and k % 2 == 0 else M
    cv.rows(r, rows, f)
    return eave - h + 1


def gable_roof(cv, x, eave, w, ramp=SLATE):
    """A steep roof seen end-on: the two slopes meet over the middle of the wall."""
    cx = x + w // 2
    r = cv.part()
    L, M, D = ramp
    rows = [(eave - (w // 2 + 1) + k, cx - k, cx + k) for k in range(w // 2 + 2)]
    cv.rows(r, rows, lambda xx, yy: D if yy == eave else (L if xx < cx else (M if xx < cx + (yy - rows[0][0]) - 1 else D)))
    return rows[0][0]


def walls(cv, x, foot, w, h, ramp=PLASTER, timber=True, door=True, windows=True, footing=True):
    b = cv.part()
    top = foot - h + 1
    cv.rect(b, x, top, x + w - 1, foot, tone(ramp, x, x + w - 1))
    d = cv.part(sep=False)
    if footing:
        cv.rect(d, x, foot, x + w - 1, foot, lambda xx, yy: STONE[2] if xx >= x + w - 2 else STONE[1])
    if timber:
        cv.rect(d, x, top, x, foot - 1, TIMBER[1])
        cv.rect(d, x + w - 1, top, x + w - 1, foot - 1, TIMBER[2])
        if h >= 6:
            cv.rect(d, x, top + h // 2 - 1, x + w - 1, top + h // 2 - 1, lambda xx, yy: TIMBER[2] if xx >= x + w - 2 else TIMBER[1])
    cx = x + w // 2
    if door:
        cv.rect(d, cx - 1, foot - min(3, h - 2), cx + 1, foot, TIMBER[2])
        cv.put(d, cx + 1, foot - 1, GOLD[1])
    if windows and w >= 9:
        wy = foot - min(3, h - 2)
        for wx in ((x + 2, x + w - 4) if w >= 13 else (x + w - 4,)):
            cv.rect(d, wx, wy, wx + 1, wy + 1, GLOW)
            cv.put(d, wx + 1, wy + 1, (226, 170, 84))
    return top


def chimney(cv, x, top, h=4):
    c = cv.part()
    cv.rect(c, x, top, x + 1, top + h - 1, lambda xx, yy: STONE[1] if xx == x else STONE[2])
    cv.rect(c, x, top, x + 1, top, STONE[0])


def house(cv, x, foot, w=13, wall=5, rh=5, ramp=SLATE, chim=True, **kw):
    """A side-on house. Returns the top row."""
    top = foot - wall - rh + 1
    if chim:
        chimney(cv, x + w - 4, top - 1, 4)
    walls(cv, x, foot, w, wall, **kw)
    return roof(cv, x, foot - wall, w, rh, ramp)


def barn(cv, x, foot, w=13, wall=5, ramp=SLATE, **kw):
    """An end-on building with a steep gable."""
    walls(cv, x, foot, w, wall, **kw)
    top = gable_roof(cv, x, foot - wall, w, ramp)
    d = cv.part(sep=False)
    cx = x + w // 2
    cv.put(d, cx, top + 3, GLOW)
    return top


def tower(cv, x, foot, w, h, cap="cone", ramp=STONE, slit=True, cone_ramp=SLATE):
    """A round stone tower. cap: 'cone' (blue cap, gold finial) or 'flat' (battlements). Returns the top row."""
    top = foot - h + 1
    b = cv.part()
    cv.rect(b, x, top, x + w - 1, foot, tone(ramp, x, x + w - 1, lw=max(1, w // 3)))
    d = cv.part(sep=False)
    cv.rect(d, x, foot, x + w - 1, foot, ramp[2])
    for yy in range(top + 3, foot - 1, 4):                               # stone courses
        cv.put(d, x + 1 + (yy // 4) % 2, yy, ramp[1])
        cv.put(d, x + w - 3, yy + 1, ramp[2])
    if slit:
        cv.rect(d, x + w // 2, top + 3, x + w // 2, top + 5, DARK)
    c = cv.part()
    cv.rect(c, x - 1, top - 1, x + w, top, tone(ramp, x - 1, x + w, top=top - 1))
    if cap == "flat":
        m = cv.part(sep=False)
        for xx in range(x - 1, x + w + 1, 2):
            cv.put(m, xx, top - 2, ramp[0] if xx < x + w - 2 else ramp[2])
        return top - 2
    cx = x + w // 2
    hw = w // 2 + 1
    r = cv.part()
    rows, y, k = [], top - 2, hw
    while k >= 0:                                                        # slope: two rows per column
        rows += [(y, cx - k, cx + k), (y - 1, cx - k, cx + k)] if k < hw else [(y, cx - k, cx + k)]
        y -= 2 if k < hw else 1
        k -= 1
    L, M, D = cone_ramp
    base_y = top - 2
    cv.rows(r, rows, lambda xx, yy: D if yy == base_y or xx > cx + 1 else (L if xx < cx else M))
    f = cv.part(sep=False)
    ty = min(r_[0] for r_ in rows)
    cv.put(f, cx, ty, GOLD[0])
    fn = cv.lines()
    cv.pix(fn, [(cx, ty - 1), (cx, ty - 2)], GOLD[1])
    return ty - 2


def curtain(cv, x0, x1, foot, h, gate=False, ramp=STONE):
    """A stretch of crenellated wall, with an arched gate when asked."""
    top = foot - h + 1
    b = cv.part()
    cv.rect(b, x0, top, x1, foot, lambda xx, yy: ramp[0] if yy == top else (ramp[2] if yy >= foot - 1 else ramp[1]))
    m = cv.part(sep=False)
    for xx in range(x0, x1 + 1):
        if (xx - x0) % 4 < 2:
            cv.put(m, xx, top - 1, ramp[0])
    mm = cv.part()
    cv.pix(mm, [(xx, top - 1) for xx in range(x0, x1 + 1) if (xx - x0) % 4 < 2], ramp[0])
    d = cv.part(sep=False)
    for yy in range(top + 2, foot - 1, 2):
        for xx in range(x0 + 2 + (yy % 4), x1 - 1, 6):
            cv.put(d, xx, yy, ramp[2])
    if gate:
        cx = (x0 + x1) // 2
        cv.rows(d, [(foot - 4, cx - 1, cx + 1)] + [(yy, cx - 2, cx + 2) for yy in range(foot - 3, foot + 1)], DARK)
        cv.pix(d, [(cx - 1, yy) for yy in range(foot - 3, foot + 1)] + [(cx + 1, yy) for yy in range(foot - 3, foot + 1)], TIMBER[1])


def flag(cv, x, foot, h=10, ramp=SLATE):
    p = cv.lines()
    cv.rect(p, x, foot - h, x, foot, TIMBER[1])
    f = cv.part()
    cv.rows(f, [(foot - h, x + 1, x + 5), (foot - h + 1, x + 1, x + 5), (foot - h + 2, x + 1, x + 4), (foot - h + 3, x + 1, x + 2)],
            lambda xx, yy: ramp[0] if xx < x + 3 else ramp[1])
    g = cv.part(sep=False)
    cv.put(g, x + 2, foot - h + 1, GOLD[1])


def barrel(cv, x, y):
    b = cv.part()
    cv.rows(b, [(y - 4, x, x + 2), (y - 3, x - 1, x + 3), (y - 2, x - 1, x + 3), (y - 1, x - 1, x + 3), (y, x, x + 2)], tone(WOOD, x - 1, x + 3))
    d = cv.part(sep=False)
    cv.rect(d, x - 1, y - 3, x + 3, y - 3, IRON[1])
    cv.rect(d, x - 1, y - 1, x + 3, y - 1, IRON[2])


def crate(cv, x, y, w=5, h=4):
    c = cv.part()
    cv.rect(c, x, y - h + 1, x + w - 1, y, tone(WOOD, x, x + w - 1, top=y - h + 1))
    d = cv.part(sep=False)
    cv.pix(d, line(x + 1, y - 1, x + w - 2, y - h + 2), WOOD[2])


def rick(cv, x, y, r=4):
    h = cv.part()
    rows = ell_rows(x, y - r + 1, r, r, top_only=True) + [(y - r + 2, x - r, x + r), (y, x - r, x + r)] + [(yy, x - r, x + r) for yy in range(y - r + 2, y)]
    cv.rows(h, rows, tone(THATCH, x - r, x + r))
    d = cv.part(sep=False)
    cv.pix(d, [(x - 1, y - 2), (x + 1, y - 4), (x - 2, y - 5)], THATCH[2])


def fence(cv, pts, posts=4):
    f = cv.lines()
    path = []
    for (a, b) in zip(pts, pts[1:]):
        path += line(a[0], a[1], b[0], b[1])
    cv.pix(f, [(x, y - 2) for x, y in path], WOOD[0])
    cv.pix(f, [(x, y - 4) for x, y in path], WOOD[1])
    for i, (x, y) in enumerate(path):
        if i % posts == 0:
            cv.rect(f, x, y - 5, x, y, TIMBER[1])
            cv.put(f, x, y - 5, WOOD[0])


def tent(cv, x, foot, w=15, ramp=CANVAS, trim=SLATE):
    cx = x + w // 2
    t = cv.part()
    rows = [(foot - (w // 2) + k, cx - k, cx + k) for k in range(w // 2 + 1)]
    cv.rows(t, rows, lambda xx, yy: ramp[0] if xx < cx else (ramp[1] if xx < cx + (yy - rows[0][0]) - 1 else ramp[2]))
    d = cv.part(sep=False)
    cv.rows(d, [(foot, cx - 1, cx + 1), (foot - 1, cx - 1, cx + 1), (foot - 2, cx, cx), (foot - 3, cx, cx)], DARK)
    for yy, a, b in rows[2:]:
        if (foot - yy) in (0, 1):
            cv.rect(d, a, yy, cx - 2, yy, trim[0])
            cv.rect(d, cx + 2, yy, b, yy, trim[1])
    p = cv.lines()
    cv.pix(p, [(cx, rows[0][0] - 1), (cx, rows[0][0] - 2)], TIMBER[1])
    f = cv.part()
    cv.rows(f, [(rows[0][0] - 3, cx, cx + 3), (rows[0][0] - 2, cx + 1, cx + 2)], trim[0])


def logs(cv, x, y, n=3):
    """A stack of sawn logs seen end-on."""
    spots = [(0, 0), (5, 0), (10, 0), (2, -4), (8, -4), (5, -8)][: {3: 3, 5: 5, 6: 6}.get(n, 3)]
    if n == 3:
        spots = [(0, 0), (5, 0), (2, -4)]
    for dx, dy in spots:
        l = cv.part()
        cx, cy = x + dx, y + dy - 2
        cv.rows(l, ell_rows(cx + 2, cy, 2, 2), tone(TIMBER, cx, cx + 4))
        d = cv.part(sep=False)
        cv.rect(d, cx + 1, cy - 1, cx + 3, cy + 1, WOOD[0])
        cv.put(d, cx + 2, cy, WOOD[2])


# ================================================================ improvements
def farmstead(race=None):
    cv = TC()
    cv.shadow(30, 15, 38)
    rick(cv, 46, 35, 4)
    house(cv, 19, 37, 17, wall=6, rh=6)
    barrel(cv, 13, 38)
    fence(cv, [(40, 41), (52, 41)])
    return cv.image()


def mine(race=None):
    cv = TC()
    m = cv.part()                                                          # spoil mound
    rows = ell_rows(30, 30, 19, 11) + ell_rows(26, 24, 12, 7)
    cv.rows(m, rows, lambda x, y: ROCK[0] if (x + y < 50 and y < 27) else (ROCK[2] if x > 40 or y > 37 else ROCK[1]))
    d = cv.part(sep=False)
    cv.pix(d, [(18, 30), (19, 31), (40, 26), (41, 27), (36, 37), (22, 36), (14, 33)], ROCK[2])
    cv.pix(d, [(22, 22), (23, 21), (30, 20)], ROCK[0])
    mo = cv.part(sep=False)                                                # tunnel mouth
    cv.rect(mo, 26, 26, 35, 35, DARK)
    cv.rect(mo, 30, 30, 31, 31, GLOW)
    for px in (24, 35):                                                    # timber frame
        p = cv.part()
        cv.rect(p, px, 25, px + 2, 36, tone(TIMBER, px, px + 2, lw=1))
    b = cv.part()
    cv.rect(b, 22, 22, 39, 24, lambda x, y: WOOD[0] if y == 22 else (WOOD[2] if x > 36 else WOOD[1]))
    r = cv.lines()                                                         # rails
    cv.pix(r, line(31, 37, 44, 45) + line(33, 37, 47, 45), IRON[1])
    c = cv.part()                                                          # ore cart
    cv.rows(c, poly_rows([(40, 38), (52, 38), (50, 44), (42, 44)]), tone(WOOD, 40, 52))
    o = cv.part()
    cv.rows(o, [(35, 43, 45), (36, 42, 50), (37, 41, 51)], lambda x, y: GOLD[1] if x in (44, 45, 49) else (ROCK[0] if x < 46 else ROCK[1]))
    for wx in (43, 49):
        w = cv.part()
        cv.rows(w, ell_rows(wx, 45, 1, 1), IRON[2])
    house(cv, 5, 44, 11, wall=4, rh=4, chim=False)
    flag(cv, 55, 34, 10)
    return cv.image()


def lumber_mill(race=None):
    cv = TC()
    house(cv, 39, 30, 13, wall=4, rh=5)
    for px in (7, 21):                                                     # saw shed: roof on posts
        p = cv.part()
        cv.rect(p, px, 34, px + 1, 43, tone(TIMBER, px, px + 1, lw=1))
    lg = cv.part()                                                         # log on the saw bench
    cv.rect(lg, 9, 39, 20, 41, lambda x, y: TIMBER[0] if y == 39 else (TIMBER[2] if y == 41 else TIMBER[1]))
    e = cv.part(sep=False)
    cv.rect(e, 19, 39, 20, 41, WOOD[0])
    sw = cv.lines()
    cv.pix(sw, line(11, 35, 17, 42), (212, 216, 226))
    roof(cv, 6, 34, 18, 5)
    logs(cv, 25, 48, 5)
    st = cv.part()                                                         # stump and axe
    cv.rows(st, [(42, 48, 52), (43, 47, 53), (44, 47, 53), (45, 47, 53)], lambda x, y: WOOD[0] if y == 42 else (TIMBER[2] if x > 51 else TIMBER[1]))
    ax = cv.lines()
    cv.pix(ax, line(51, 41, 55, 36), TIMBER[1])
    ah = cv.part()
    cv.rect(ah, 54, 34, 56, 36, lambda x, y: (220, 224, 232) if x < 56 else IRON[0])
    return cv.image()


def stall(cv, x, y, w=13, ramp=SLATE):
    p = cv.lines()
    cv.rect(p, x, y - 9, x, y, TIMBER[1])
    cv.rect(p, x + w - 1, y - 9, x + w - 1, y, TIMBER[2])
    c = cv.part()
    cv.rect(c, x, y - 4, x + w - 1, y - 1, tone(WOOD, x, x + w - 1, top=y - 4))
    g = cv.part(sep=False)
    for i, col in enumerate((RED[0], GOLD[1], (132, 190, 96), RED[1])):
        if x + 2 + i * 3 < x + w - 1:
            cv.rect(g, x + 2 + i * 3, y - 5, x + 3 + i * 3, y - 5, col)
    a = cv.part()
    rows = [(y - 13, x + 1, x + w - 2), (y - 12, x, x + w - 1), (y - 11, x - 1, x + w), (y - 10, x - 1, x + w)]
    cv.rows(a, rows, lambda xx, yy: (GOLD[0] if yy < y - 10 else GOLD[2]) if (xx - x) // 2 % 2 else (ramp[0] if yy == y - 13 else (ramp[2] if yy == y - 10 else ramp[1])))


def trading_post(race=None):
    cv = TC()
    house(cv, 38, 23, 13, wall=5, rh=5)
    stall(cv, 8, 29, 13)
    barrel(cv, 23, 30)
    stall(cv, 27, 46, 15)
    crate(cv, 46, 45, 6, 5)
    crate(cv, 48, 40, 5, 4)
    sk = cv.part()                                                         # sacks
    cv.rows(sk, [(42, 17, 19), (43, 16, 20), (44, 16, 20), (45, 16, 20)], tone(CANVAS, 16, 20))
    cv.rows(sk, [(43, 21, 23), (44, 20, 24), (45, 20, 24)], tone(THATCH, 20, 24))
    flag(cv, 55, 30, 10)
    return cv.image()


def pasture_parts():
    back = TC()
    barn(back, 23, 13, 15, wall=4, windows=False)
    house(back, 1, 30, 9, wall=3, rh=4, chim=False, windows=False)
    fence(back, [(51, 16), (57, 28), (53, 44)])
    front = TC()
    fence(front, [(6, 36), (12, 48), (26, 51)])
    t = front.part()                                                       # trough
    front.rect(t, 35, 48, 45, 51, tone(WOOD, 35, 45))
    w = front.part(sep=False)
    front.rect(w, 36, 48, 44, 48, WATER[1])
    front.pix(w, [(38, 48), (42, 48)], WATER[0])
    rick(front, 52, 52, 3)
    return back.image(), front.image()


PLOT = [(5, 36), (27, 50), (55, 34), (33, 22)]


def plantation_parts(bare=True):
    back = TC()
    for pts, c in (([(5, 36), (27, 50), (27, 53), (5, 39)], SOIL[2]), ([(27, 50), (55, 34), (55, 37), (27, 53)], (64, 44, 38))):
        p = back.part()
        back.rows(p, poly_rows(pts), c)
    p = back.part()
    back.rows(p, poly_rows(PLOT), lambda x, y: SOIL[0] if (x - 2 * y) % 9 == 0 and bare else SOIL[1])
    if bare:
        f = back.part(sep=False)
        for k in range(5):
            t = 0.18 + k * 0.16
            ax, ay = int(5 + 28 * t), int(36 - 14 * t)
            back.pix(f, line(ax, ay, ax + 22, ay + 14), SOIL[2])
    fence(back, [(6, 35), (33, 22), (54, 33)])
    front = TC()
    fence(front, [(27, 48), (54, 35)])
    house(front, 6, 49, 13, wall=4, rh=5)
    barrel(front, 22, 51)
    return back.image(), front.image()


def quarry_parts():
    cv = TC()
    for pts, c in (([(18, 24), (36, 14), (46, 20), (28, 30)], STONE[2]), ([(22, 26), (36, 18), (42, 22), (28, 30)], STONE[0]), ([(28, 30), (42, 22), (42, 27), (28, 35)], STONE[1])):
        p = cv.part()
        cv.rows(p, poly_rows(pts), c)
    d = cv.part(sep=False)
    cv.pix(d, line(26, 27, 34, 22) + line(31, 29, 39, 24), STONE[1])
    ft = cv.part()                                                         # hoist
    cv.rect(ft, 31, 27, 37, 30, tone(STONE, 31, 37, top=27))
    ps = cv.part()
    cv.rect(ps, 33, 9, 35, 26, tone(TIMBER, 33, 35, lw=1))
    jb = cv.part()
    cv.rect(jb, 33, 6, 49, 8, lambda x, y: WOOD[0] if y == 6 else (WOOD[2] if y == 8 else WOOD[1]))
    br = cv.lines()
    cv.pix(br, line(36, 17, 43, 9), TIMBER[1])
    cv.rect(br, 46, 9, 46, 15, (232, 226, 206))
    bk = cv.part()
    cv.rect(bk, 43, 16, 49, 20, tone(STONE, 43, 49, top=16))
    for bx, by in ((37, 41), (45, 41), (41, 36)):                           # dressed blocks
        b = cv.part()
        cv.rect(b, bx, by - 4, bx + 6, by, tone(STONE, bx, bx + 6, top=by - 4))
    house(cv, 12, 43, 11, wall=4, rh=4, chim=False)
    pk = cv.lines()                                                        # pick
    cv.pix(pk, line(28, 45, 32, 39), TIMBER[1])
    ph = cv.part()
    cv.rect(ph, 30, 38, 35, 38, IRON[0])
    flag(cv, 34, 5, 4)
    return cv.image()


def boat(cv, x, y, flip=False):
    d = -1 if flip else 1
    wk = cv.lines()                                                        # wake
    cv.rows(wk, ell_rows(x, y + 3, 10, 1), WATER[1])
    cv.rect(wk, x - 9, y + 3, x - 3, y + 3, WATER[0])
    m = cv.lines()
    cv.rect(m, x, y - 15, x, y - 3, TIMBER[1])
    cv.pix(m, line(x - 6 * d, y - 3, x - 10 * d, y - 7), (236, 232, 216))
    h = cv.part()
    cv.rows(h, [(y - 2, x - 8, x + 8), (y - 1, x - 8, x + 8), (y, x - 7, x + 7), (y + 1, x - 5, x + 5)],
            lambda xx, yy: WOOD[0] if yy == y - 2 else (WOOD[2] if yy == y + 1 else WOOD[1]))
    s = cv.part(sep=False)
    cv.rect(s, x - 7, y - 1, x + 7, y - 1, SLATE[1])
    sl = cv.part()
    rows = []
    for k in range(11):
        yy = y - 14 + k
        a, b = (x + 1, x + 1 + k * 2 // 3) if d > 0 else (x - 1 - k * 2 // 3, x - 1)
        rows.append((yy, a, b))
    cv.rows(sl, rows, lambda xx, yy: CANVAS[2] if yy == y - 4 else (CANVAS[0] if abs(xx - x) < 3 else CANVAS[1]))
    f = cv.part()
    cv.rows(f, [(y - 17, x, x + 2 * d if d > 0 else x), (y - 16, x, x + d if d > 0 else x)], SLATE[0])
    if d < 0:
        cv.rows(f, [(y - 17, x - 2, x), (y - 16, x - 1, x)], SLATE[0])


def fishing_boats(spots=((30, 26), (45, 40))):
    cv = TC()
    for k, (x, y) in enumerate(sorted(spots, key=lambda t: t[1])):
        boat(cv, int(x), int(y), flip=bool(k % 2))
    return cv.image()


def camp(race=None):
    cv = TC()
    cv.shadow(20, 9, 29)
    rk = cv.lines()                                                        # drying rack
    cv.rect(rk, 5, 22, 5, 33, TIMBER[1])
    cv.rect(rk, 13, 22, 13, 33, TIMBER[1])
    cv.rect(rk, 4, 22, 14, 22, WOOD[1])
    hd = cv.part()
    cv.rows(hd, [(23, 7, 11), (24, 6, 12), (25, 6, 12), (26, 6, 12), (27, 6, 12), (28, 7, 11), (29, 7, 8), (29, 10, 11)], tone(HIDE, 6, 12))
    tent(cv, 15, 29, 17)
    st = cv.part()                                                         # fire ring
    cv.rows(st, ell_rows(41, 30, 4, 2), lambda x, y: IRON[0] if x < 41 else IRON[1])
    a = cv.part(sep=False)
    cv.rows(a, ell_rows(41, 30, 2, 1), DARK)
    fl = cv.part()
    cv.rows(fl, [(25, 41, 41), (26, 41, 41), (27, 40, 42), (28, 40, 42), (29, 40, 42)], lambda x, y: FLAME[0] if (x == 41 and y > 26) else (FLAME[2] if y < 27 else FLAME[1]))
    flag(cv, 52, 29, 11)
    crate(cv, 46, 33, 5, 4)
    return cv.image()


def fort(race=None):
    cv = TC()
    x0, x1 = 9, 55
    curtain(cv, x0, x1, 18, 5)
    for tx in (x0 - 2, x1 - 2):
        tower(cv, tx, 19, 5, 9, slit=False)
    for sx in (x0, x1 - 3):                                                # side walls
        s = cv.part()
        cv.rect(s, sx, 14, sx + 3, 44, tone(STONE, sx, sx + 3, lw=1))
    g = cv.ground
    tower(cv, 28, 35, 9, 15)                                               # keep
    house(cv, 14, 39, 11, wall=4, rh=4, chim=False)
    flag(cv, 44, 38, 12)
    crate(cv, 40, 40, 4, 3)
    curtain(cv, x0, x1, 47, 6, gate=True)
    for tx in (x0 - 3, x1 - 3):
        tower(cv, tx, 48, 7, 11)
    return cv.image()


# ================================================================ city centers (64 x 72: towers rise above the hex)
CW, CH = 64, 72
OY = CH - 56
CX = 32


def plaza(cv, rx, ry):
    rows = ell_rows(CX, OY + 30, rx, ry)
    cv.ground(rows, PAVE[2])
    cv.ground(ell_rows(CX, OY + 30, rx - 1, ry - 1), lambda x, y: PAVE[0] if (x + 3 * y) % 7 == 0 else PAVE[1])


def well(cv, x, y):
    b = cv.part()
    cv.rows(b, [(y - 2, x - 2, x + 2), (y - 1, x - 3, x + 3), (y, x - 3, x + 3)], tone(STONE, x - 3, x + 3, top=y - 2))
    w = cv.part(sep=False)
    cv.rect(w, x - 1, y - 2, x + 1, y - 2, WATER[2])
    p = cv.lines()
    cv.rect(p, x - 3, y - 7, x - 3, y - 3, TIMBER[1])
    cv.rect(p, x + 3, y - 7, x + 3, y - 3, TIMBER[1])
    r = cv.part()
    cv.rows(r, [(y - 9, x - 2, x + 2), (y - 8, x - 4, x + 4)], lambda xx, yy: SLATE[0] if yy == y - 9 else SLATE[2])


def fountain(cv, x, y):
    b = cv.part()
    cv.rows(b, [(y - 2, x - 3, x + 3), (y - 1, x - 5, x + 5), (y, x - 5, x + 5), (y + 1, x - 3, x + 3)], tone(STONE, x - 5, x + 5, top=y - 2))
    w = cv.part(sep=False)
    cv.rows(w, [(y - 1, x - 3, x + 3), (y, x - 3, x + 3)], lambda xx, yy: WATER[0] if (xx + yy) % 3 == 0 else WATER[1])
    c = cv.part()
    cv.rect(c, x, y - 6, x, y - 2, STONE[0])
    cv.rect(c, x - 1, y - 5, x + 1, y - 5, STONE[1])
    s = cv.lines()
    cv.pix(s, [(x - 2, y - 6), (x + 2, y - 6), (x - 3, y - 4), (x + 3, y - 4), (x, y - 7)], WATER[0])


def keep(cv, stage):
    """The castle at the back of the town: hall between two capped towers, a taller donjon behind in the city."""
    e = 3 if stage == 2 else 0
    foot = OY + 26
    if stage == 2:
        tower(cv, CX - 4, foot - 6, 9, 22)
    top = house(cv, CX - 9, foot, 19, wall=8 + e, rh=6, chim=False, timber=False, ramp=SLATE, windows=False)
    d = cv.part(sep=False)
    for wx in (CX - 6, CX + 5):                                             # tall windows
        cv.rect(d, wx, foot - 6 - e, wx + 1, foot - 3 - e, GLOW)
        cv.put(d, wx + 1, foot - 3 - e, (226, 170, 84))
    cv.rows(d, [(foot - 4, CX - 1, CX + 1)] + [(yy, CX - 2, CX + 2) for yy in range(foot - 3, foot + 1)], DARK)   # gate
    cv.pix(d, [(CX, yy) for yy in range(foot - 3, foot + 1)], TIMBER[1])
    cv.rect(d, CX - 9, foot - 8 - e + 1, CX + 9, foot - 8 - e + 1, STONE[0])
    for tx in (CX - 15, CX + 9):
        tower(cv, tx, foot + 1, 7, 16 + e)
    if stage == 1:
        flag(cv, CX, top, 6)


def city_center(stage, small=False):
    cv = TC(CW, CH)
    plaza(cv, 24 + stage * 2, 11 + stage)
    if stage == 0:                                                         # village: hall, cottages, well
        top = barn(cv, CX - 8, OY + 27, 17, wall=6)
        b = cv.part()
        cv.rect(b, CX - 1, top - 4, CX + 1, top + 1, tone(STONE, CX - 1, CX + 1, lw=1))
        r = cv.part()
        cv.rows(r, [(top - 6, CX, CX), (top - 5, CX - 1, CX + 1), (top - 4, CX - 2, CX + 2)], lambda x, y: SLATE[0] if x < CX else SLATE[1])
        g = cv.part(sep=False)
        cv.put(g, CX, top - 2, GOLD[1])
        house(cv, 4, OY + 31, 13, wall=4, rh=5)
        house(cv, 47, OY + 31, 13, wall=4, rh=5)
        rick(cv, 21, OY + 34, 3)
        well(cv, CX, OY + 39)
        house(cv, 11, OY + 45, 13, wall=4, rh=5)
        house(cv, 40, OY + 45, 13, wall=4, rh=5)
        fence(cv, [(27, OY + 47), (37, OY + 47)])
    else:
        keep(cv, stage)
        e = 1 if stage == 2 else 0
        house(cv, 2, OY + 31, 11, wall=4 + e, rh=5)
        house(cv, 51, OY + 31, 11, wall=4 + e, rh=5)
        house(cv, 9, OY + 40, 13, wall=4 + e, rh=5)
        house(cv, 42, OY + 40, 13, wall=4 + e, rh=5)
        fountain(cv, CX, OY + 36)
        if stage == 1:
            house(cv, 15, OY + 49, 11, wall=4, rh=4)
            house(cv, 38, OY + 49, 11, wall=4, rh=4)
            barrel(cv, 30, OY + 48)
            crate(cv, 33, OY + 49, 4, 3)
        else:
            house(cv, 22, OY + 45, 9, wall=3, rh=4, chim=False)
            house(cv, 33, OY + 45, 9, wall=3, rh=4, chim=False)
            foot = OY + 51
            curtain(cv, 6, 58, foot, 7, gate=True)
            for tx in (2, 55):
                tower(cv, tx, foot + 1, 7, 12)
    return cv.image()


# ================================================================ hooks into the build
import contextlib

HANDLED = {"Humans"}              # styles drawn by this module; tile_art_races adds the rest


@contextlib.contextmanager
def CTX(race):                    # replaced by tile_art_races: sets the faction's materials and shapes while a scene is drawn
    yield


class _Img:
    """Stands in for a citycenters canvas: image() and half().image()."""

    def __init__(self, im):
        self.im = im

    def image(self):
        return self.im

    def half(self):
        import fh_improvements
        return _Img(fh_improvements.reduce(self.im))


def install():
    import improvement_art as IA
    import citycenters as CC
    if getattr(IA, "_human_trial", False):
        return
    IA._human_trial = True

    def swap(name, fn):
        old = getattr(IA, name)
        def wrapped(race, *a, **k):
            if race in HANDLED:
                with CTX(race):
                    return fn(race, *a, **k)
            return old(race, *a, **k)
        setattr(IA, name, wrapped)

    def scene(*layers):
        s = IA.Scene()
        for depth, im in layers:
            s.add(depth, im)
        return s

    swap("farmstead", farmstead)
    swap("mine", mine)
    swap("lumber_mill", lumber_mill)
    swap("trading_post", trading_post)
    swap("camp", camp)
    swap("fort", fort)

    def pasture(race):
        back, front = pasture_parts()
        return scene((13, back), (50, front))

    def plantation(race, crops=None):
        back, front = plantation_parts(bare=crops is None)
        s = scene((0, back), (52, front))
        if crops is not None:
            s.add(30, crops)
        return s

    swap("pasture_scene", pasture)
    swap("plantation_scene", plantation)
    swap("quarry_scene", lambda race: scene((22, quarry_parts())))
    swap("fishing_boats_scene", lambda race, spots=((30, 26), (45, 40)): scene((0, fishing_boats(spots))))

    old_cc = CC.city_center_canvas
    def cc(style_name, stage, small=False):
        if style_name in HANDLED:
            with CTX(style_name):
                return _Img(city_center(stage))
        return old_cc(style_name, stage, small)
    CC.city_center_canvas = cc


install()
import tile_art_races   # noqa: E402,F401  the other factions: their own materials, roof forms and tower caps on these scenes
