"""City-center tiles for every race, in its own architecture and colours.

Unciv looks for "City center-<civ>-<era>" first (falling back to earlier eras), so each
race gets three growth stages: a village (Age of Tribes), a town (Age of the Dark
Portal) and a walled city (Age of the Cataclysm). City-states borrow the style that
fits them (Gadgetzan is goblin, Cenarion Hold night elf, Dalaran violet), and the plain
"City center-<era>" images are replaced with a Warcraft-style stone town so no city
ever shows Unciv's modern skyscrapers.

Pixel rules (so the line work stays clean and aligned):
  * every coordinate is an integer pixel; nothing is placed at a fraction and rounded;
  * buildings with a roof peak have odd widths, so the peak sits on a whole column, and
    centred pieces sit on column 32, the canvas's centre line;
  * roof slopes are exact 1:1 or 1:2 staircases; merlons, windows and doors are laid
    out symmetrically from both ends of their wall;
  * every shape is drawn into one label map, back to front, and the outline is worked
    out once at the end: a pixel is outline when a 4-neighbour belongs to a shape
    drawn earlier (or to nothing). Two touching shapes therefore share a single 1-px
    line, never a doubled one;
  * the 32-px FantasyHex tile is made by reducing the label map, then outlining again
    at that size, so it also gets 1-px lines rather than blurred half-lines.
All designs are original; they use broad architectural cues only.
"""
import math, os
from PIL import Image

W, H = 64, 72                 # taller than a tile so towers can rise above it
OY = H - 56                   # the hex face starts this far down the canvas
CX = 32                       # centre column
OUT = (30, 24, 22)            # outline colour, shared with the unit sprites
SMALL = False                 # True while drawing the scene that is reduced for the 32-px tile set
STAGES = [("Age of Tribes", 0), ("Age of the Dark Portal", 1), ("Age of the Cataclysm", 2)]
ERA_STAGE = {"Age of Tribes": 0, "Age of Arathor": 0, "Age of the Dark Portal": 1, "Age of the Third War": 1,
             "Age of the Lich King": 1, "Age of the Cataclysm": 2, "Age of the Legion": 2,
             "Age of Azerite": 2, "Age of the Void": 2}


def shade(c, k):
    return tuple(max(0, min(255, int(round(v * k)))) for v in c)


# ------------------------------------------------------------------ canvas
class Canvas:
    """A label map: each pixel remembers which shape drew it last and its colour."""

    def __init__(self, w=W, h=H):
        self.w, self.h = w, h
        self.lab = [[-1] * w for _ in range(h)]
        self.col = [[None] * w for _ in range(h)]
        self.meta = []

    def shape(self, outline=OUT, glow=None):
        self.meta.append({"outline": outline, "glow": glow})
        return len(self.meta) - 1

    def put(self, s, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.lab[y][x] = s
            self.col[y][x] = tuple(c)

    def rows(self, s, rows, fn):
        """rows: (y, x0, x1) inclusive spans; fn(x, y) gives the colour."""
        for y, a, b in rows:
            for x in range(a, b + 1):
                self.put(s, x, y, fn(x, y))

    def rect(self, s, x0, y0, x1, y1, fn):
        self.rows(s, [(y, x0, x1) for y in range(y0, y1 + 1)], fn)

    def image(self):
        im = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        px = im.load()
        lab, meta = self.lab, self.meta
        line = self.lines()
        for y in range(self.h):
            for x in range(self.w):
                if lab[y][x] >= 0:
                    px[x, y] = (meta[lab[y][x]]["outline"] if line[y][x] else self.col[y][x]) + (255,)
        # hard-pixel glow halo on empty pixels around glowing shapes
        halo = {}
        for y in range(self.h):
            for x in range(self.w):
                l = lab[y][x]
                if l >= 0 and meta[l]["glow"]:
                    for dy in (-2, -1, 0, 1, 2):
                        for dx in (-2, -1, 0, 1, 2):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.w and 0 <= ny < self.h and lab[ny][nx] < 0:
                                a = 130 if max(abs(dx), abs(dy)) == 1 else 60
                                if a > halo.get((nx, ny), (None, 0))[1]:
                                    halo[(nx, ny)] = (meta[l]["glow"], a)
        for (x, y), (g, a) in halo.items():
            px[x, y] = tuple(g) + (a,)
        return im

    def lines(self):
        """Which pixels show as outline. A pixel of a shape is outline where a 4-neighbour
        belongs to an earlier shape or to nothing, unless that neighbour already shows a
        line of the same colour, in which case the two edges share that one line.
        Shapes are settled back to front so a front shape only leans on final lines."""
        lab, meta = self.lab, self.meta
        line = [[False] * self.w for _ in range(self.h)]
        order = sorted(((lab[y][x], y, x) for y in range(self.h) for x in range(self.w) if lab[y][x] >= 0))
        for l, y, x in order:
            out = meta[l]["outline"]
            if out is None:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                nl = lab[ny][nx] if 0 <= nx < self.w and 0 <= ny < self.h else -1
                if nl < l and not (nl >= 0 and line[ny][nx] and meta[nl]["outline"] == out):
                    line[y][x] = True
                    break
        # thinning: no solid 2x2 block of line; the front-most pixel in it shows its fill
        changed = True
        while changed:
            changed = False
            for y in range(self.h - 1):
                for x in range(self.w - 1):
                    blk = [(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)]
                    if all(line[by][bx] for bx, by in blk):
                        bx, by = max(blk, key=lambda p: (lab[p[1]][p[0]], p[1], p[0]))
                        line[by][bx] = False
                        changed = True
        return line

    def half(self):
        """Reduce to half size. Column 32 (the mirror axis) becomes its own output column
        and columns pair up outwards from it, so mirrored art stays mirrored. In each
        block the shape covering most pixels wins, ties going to the shape in front.
        Outlines are then recomputed at the new size, so the lines stay 1 px."""
        c = Canvas(self.w // 2, self.h // 2)
        c.meta = [dict(m) for m in self.meta]
        half_w = c.w // 2
        def cols(k):
            if k < half_w:
                return (2 * k, 2 * k + 1)
            if k == half_w:
                return (CX,)
            return (2 * k - 1, 2 * k)
        for y in range(c.h):
            for x in range(c.w):
                cnt, first = {}, {}
                for sy in (2 * y, 2 * y + 1):
                    for sx in cols(x):
                        l = self.lab[sy][sx]
                        cnt[l] = cnt.get(l, 0) + 1
                        first.setdefault(l, self.col[sy][sx])
                best = max(cnt, key=lambda l: (cnt[l], l))
                if best >= 0:
                    c.lab[y][x] = best
                    c.col[y][x] = first[best]
        return c


# ------------------------------------------------------------------ geometry helpers
def tri_rows(cx, base_y, hw0, rate=1, top_hw=0):
    """A symmetric stepped triangle: half-width hw0 at base_y, narrowing by one pixel
    on each side every `rate` rows until it reaches top_hw."""
    out, k, hw = [], 0, hw0
    while hw >= top_hw:
        out.append((base_y - k, cx - hw, cx + hw))
        k += 1
        if k % rate == 0:
            hw -= 1
    return out


def ell_rows(cx, cy, rx, ry, top_only=False):
    out = []
    for y in range(cy - ry, cy + (0 if top_only else ry) + 1):
        t = (y - cy) / (ry + 0.5)
        hw = int(math.floor(rx * math.sqrt(max(0.0, 1 - t * t)) + 0.35))
        out.append((y, cx - hw, cx + hw))
    return out


def two_tone(base, cx, k=0.78):
    """Lit on the left (and the centre column), shaded on the right."""
    dark = shade(base, k)
    return lambda x, y: base if x <= cx else dark


def wall_tone(base, x0, w, top):
    dark = shade(base, 0.8)
    eave = shade(base, 0.82)
    split = x0 + w - min(max(2, w // 3), 4)
    def f(x, y):
        c = base if x < split else dark
        return eave if y == top + 1 and x < split else (shade(dark, 0.9) if y == top + 1 else c)
    return f


def odd(w):
    return w if w % 2 else w + 1


# ------------------------------------------------------------------ roofs
def roof(cv, kind, x, top, w, col, trim=None, accent=None):
    """Draw a roof over a wall whose top row is `top`, spanning x..x+w-1 (w odd)."""
    cx = x + (w - 1) // 2
    hw = (w - 1) // 2
    s = cv.shape()
    if kind == "gable":
        cv.rows(s, tri_rows(cx, top, hw + 1, 1), two_tone(col, cx))
    elif kind == "hip":
        cv.rows(s, tri_rows(cx, top, hw + 1, 1, top_hw=max(1, hw // 2)), two_tone(col, cx))
    elif kind == "spire":
        rows = tri_rows(cx, top, hw + 1, 2)
        cv.rows(s, rows, two_tone(col, cx))
        finial(cv, cx, rows[-1][0] - 1, trim or shade(col, 1.3))
    elif kind == "cone":
        cv.rows(s, tri_rows(cx, top, hw + 1, 1), two_tone(col, cx))
    elif kind == "spiky":
        rows = tri_rows(cx, top, hw + 1, 1, top_hw=max(1, hw // 3))
        cv.rows(s, rows, two_tone(col, cx))
        spikes(cv, cx, rows, accent or (225, 214, 190))
    elif kind == "dome":
        R = hw + 1
        rh = max(2, (R * 3 + 2) // 4)
        rows = [(y, a, b) for (y, a, b) in ell_rows(cx, top, R, rh, top_only=True)]
        hi = shade(col, 1.22)
        dark = shade(col, 0.78)
        def f(xx, yy):
            if xx > cx + R // 3:
                return dark
            if xx in (cx - R // 2, cx - R // 2 + 1) and yy == top - rh + max(1, rh // 3):
                return hi
            return col
        cv.rows(s, rows, f)
        finial(cv, cx, top - rh - 1, trim or shade(col, 1.3))
    elif kind == "onion":
        R = hw + 1
        prof = [R, R + 1, R + 1, R, R - 1] + list(range(R - 2, 0, -1)) + [0, 0]
        rows = [(top - k, cx - h, cx + h) for k, h in enumerate(prof)]
        cv.rows(s, rows, two_tone(col, cx))
        finial(cv, cx, rows[-1][0] - 1, trim or (240, 200, 70), 2)
    elif kind == "leaf":
        R = hw + 2
        rh = max(2, R // 2)
        rows = ell_rows(cx, top, R, rh, top_only=True)
        rows.append((top - 1, cx - R - 1, cx - R - 1))
        rows.append((top - 2, cx - R - 1, cx - R - 1))
        rows.append((top - 1, cx + R + 1, cx + R + 1))
        rows.append((top - 2, cx + R + 1, cx + R + 1))
        cv.rows(s, rows, two_tone(col, cx))
    elif kind == "flat":                          # crenellated stone roof
        cv.rows(s, [(top, x - 1, x + w)], lambda xx, yy: col)
        span = w + 2
        rows = []
        for o in range(span):
            m = min(o, span - 1 - o)
            if SMALL:                             # 2-px rhythm on the 32-px reduction grid
                ax = x - 1 + o
                ax = ax if ax <= CX else 2 * CX - ax
                on = (ax // 2) % 2 == 0
            else:
                on = m % 6 < 4                    # 4-px merlons, 2-px gaps
            if on:
                for k in (1, 2, 3):
                    rows.append((top - k, x - 1 + o, x - 1 + o))
        cv.rows(s, rows, two_tone(col, cx))
    elif kind == "slab":                          # plain flat roof with a lip
        cv.rows(s, [(top, x - 1, x + w), (top - 1, x - 1, x + w), (top - 2, x - 1, x + w)], two_tone(col, cx))
    elif kind == "thatch":
        rows = tri_rows(cx, top + 1, hw + 2, 1)
        fr = shade(col, 0.7)
        base = two_tone(col, cx)
        cv.rows(s, rows, lambda xx, yy: fr if yy == top + 1 and (xx - cx) % 2 == 0 else base(xx, yy))
        d = cv.shape(outline=None)
        cv.put(d, cx, top - hw // 2, (240, 230, 210))
    elif kind == "pagoda":
        eave(cv, cx, top, hw + 2, col)
        c = cv.shape()
        cv.rows(c, tri_rows(cx, top - 3, max(1, hw - 1), 1, top_hw=max(1, hw // 2)), two_tone(col, cx))
    if trim and kind in ("gable", "hip", "spire", "slab"):
        t = cv.shape(outline=None)
        cv.rows(t, [(top + 1, x, x + w - 1)], lambda xx, yy: trim)


def finial(cv, cx, y, col, h=2):
    s = cv.shape(outline=None)
    for k in range(h):
        cv.put(s, cx, y - k, col)


def spikes(cv, cx, rows, col):
    s = cv.shape(outline=None)
    base_y, a, b = rows[0]
    for k in (1, 2):                              # a tusk at each eave end, rising outwards
        cv.put(s, a - k, base_y - k, col)
        cv.put(s, b + k, base_y - k, col)


def eave(cv, cx, y, hw, col):
    """A pagoda eave: three rows with upturned tips, centred on cx."""
    s = cv.shape()
    rows = [(y, cx - hw, cx + hw), (y - 1, cx - hw, cx + hw), (y - 2, cx - hw + 1, cx + hw - 1),
            (y - 2, cx - hw - 1, cx - hw - 1), (y - 2, cx + hw + 1, cx + hw + 1)]
    cv.rows(s, rows, two_tone(col, cx))


# ------------------------------------------------------------------ buildings
NO_WALL = ("cone", "tent")


def building(cv, x, foot, w, h, wall, roofcol, kind="gable", trim=None, win=None, door=True, accent=None):
    """A building whose front wall spans x..x+w-1 (w odd) with its bottom row at foot."""
    w = odd(w)
    cx = x + (w - 1) // 2
    top = foot - h + 1
    if kind == "tent":
        tent(cv, cx, foot, (w - 1) // 2, roofcol)
        return
    if kind == "cone":
        s = cv.shape()
        cv.rows(s, tri_rows(cx, foot, (w - 1) // 2, 1), two_tone(roofcol, cx))
        d = cv.shape(outline=None)
        cv.put(d, cx, foot - 1, (60, 40, 30))
        return
    s = cv.shape()
    cv.rect(s, x, top, x + w - 1, foot, wall_tone(wall, x, w, top))
    d = cv.shape(outline=None)
    if win and h >= 5:
        wy = top + (h - 1) // 2 + (1 if kind != "flat" else 0)
        for wx in sorted({x + 2, x + w - 3}):
            if x + 1 < wx < x + w - 2 and wx != cx:
                cv.put(d, wx, wy, win)
    if door:
        dh = 2 if h < 9 else 3
        dw = 1 if w < 13 else 3
        for yy in range(foot - dh, foot):
            for xx in range(cx - dw // 2, cx + dw // 2 + 1):
                cv.put(d, xx, yy, (62, 42, 32))
    if kind == "pagoda":
        roof(cv, "pagoda", x, top, w, roofcol)
    else:
        roof(cv, kind, x, top, w, roofcol, trim=trim, accent=accent)


def tower(cv, x, foot, w, h, wall, roofcol, kind="spire", trim=None, win=None, stripes=None):
    w = odd(w)
    cx = x + (w - 1) // 2
    top = foot - h + 1
    s = cv.shape()
    base = wall_tone(wall, x, w, top)
    if stripes:
        cv.rect(s, x, top, x + w - 1, foot,
                lambda xx, yy: shade(stripes, 1 if xx < x + w - min(max(2, w // 3), 4) else 0.8) if (foot - yy) // 3 % 2 else base(xx, yy))
    else:
        cv.rect(s, x, top, x + w - 1, foot, base)
    if win:
        d = cv.shape(outline=None)
        for wy in range(top + 3, foot - 2, 4):
            cv.put(d, cx, wy, win)
    if trim:
        t = cv.shape(outline=None)
        cv.rows(t, [(top + 1, x, x + w - 1)], lambda xx, yy: trim)
    roof(cv, kind, x, top, w, roofcol, trim=trim)


def tent(cv, cx, foot, hw, col):
    s = cv.shape()
    rows = tri_rows(cx, foot, hw, 2)
    base = two_tone(col, cx)
    red, blue = (190, 62, 42), (58, 112, 165)
    by = foot - len(rows) * 2 // 5
    cv.rows(s, rows, lambda x, y: red if y == by else blue if y == by - 1 else base(x, y))
    d = cv.shape(outline=None)
    cv.put(d, cx, foot - 1, (60, 40, 30))
    cv.put(d, cx, foot - 2, (60, 40, 30))
    apex = rows[-1][0]
    for k in (1, 2):
        cv.put(d, cx - k, apex - k, (110, 80, 50))
        cv.put(d, cx + k, apex - k, (110, 80, 50))


def banner(cv, x, foot, h, pole, cloth):
    p = cv.shape(outline=None)
    for y in range(foot - h, foot + 1):
        cv.put(p, x, y, pole)
    s = cv.shape()
    rows = [(y, x + 1, x + 5) for y in range(foot - h, foot - h + 4)] + [(foot - h + 4, x + 1, x + 2), (foot - h + 4, x + 4, x + 5)]
    cv.rows(s, rows, lambda xx, yy: cloth)


def mirror_x(x, w):
    """Left edge of the mirror image (about column 32) of a piece spanning x..x+w-1."""
    return 2 * CX + 1 - x - w


# ------------------------------------------------------------------ scene
class Scene:
    """Pieces with a depth (their foot row); drawn back to front onto one canvas."""

    def __init__(self):
        self.items = []

    def add(self, depth, fn):
        self.items.append((depth, len(self.items), fn))

    def canvas(self):
        cv = Canvas()
        for _, _, fn in sorted(self.items, key=lambda t: (t[0], t[1])):
            fn(cv)
        return cv


def plaza(s, col, rx, ry):
    def f(cv):
        a = cv.shape(outline=shade(col, 0.72))
        cv.rows(a, ell_rows(CX, OY + 30, rx, ry), lambda x, y: col)
        b = cv.shape(outline=None)
        cv.rows(b, ell_rows(CX, OY + 30, rx - 3, ry - 2), lambda x, y: shade(col, 1.07))
    s.add(-1000, f)


def city_wall(s, st):
    foot = OY + 50
    x0, w = 6, 53
    stone, cap = st["stone"], st["cap"]
    def f(cv):
        building(cv, x0, foot, w, 7, stone, stone, kind="flat", door=False)
        d = cv.shape(outline=None)
        for yy in range(foot - 3, foot):
            for xx in range(CX - 2, CX + 3):
                if not (yy == foot - 3 and xx in (CX - 2, CX + 2)):
                    cv.put(d, xx, yy, (62, 42, 32))
    s.add(foot, f)
    tk = st["tower_roof"]
    for tx in (3, mirror_x(3, 7)):
        s.add(foot + 1, lambda cv, tx=tx: tower(cv, tx, foot + 1, 7, 12, stone, cap, kind=tk, trim=st["trim"]))


# ------------------------------------------------------------------ landmarks (stage 1 = town, 2 = city)
FY = OY + 26                       # landmark foot row


def lm_castle(s, st, stage, lighthouse=False):
    e = 3 if stage == 2 else 0
    def f(cv):
        if lighthouse:
            tower(cv, CX - 3, FY - 2, 7, 22 + e, (236, 232, 222), (190, 60, 50), kind="dome",
                  stripes=(190, 60, 50))
            g = cv.shape(outline=None, glow=(255, 230, 140))
            top = FY - 2 - (22 + e) + 1
            cv.rect(g, CX - 1, top + 2, CX + 1, top + 3, lambda x, y: (255, 236, 150))
        building(cv, CX - 8, FY, 17, 9 + e, st["wall"], st["roof"], kind="hip" if lighthouse else "gable",
                 trim=st["trim"], win=st["win"])
        for tx in (CX - 14, mirror_x(CX - 14, 7)):
            tower(cv, tx, FY + 1, 7, 15 + e, st["wall"], st["roof"], kind="spire", trim=st["trim"], win=st["win"])
        if not lighthouse:
            d = cv.shape(outline=None)
            ry = FY - (9 + e) - 3
            for xx, yy in ((CX, ry - 1), (CX - 1, ry), (CX, ry), (CX + 1, ry), (CX, ry + 1)):
                cv.put(d, xx, yy, (250, 220, 120))
    s.add(FY, f)


def lm_orc(s, st, stage):
    e = 2 if stage == 2 else 0
    def f(cv):
        building(cv, CX - 10, FY, 21, 7 + e, (120, 76, 46), (150, 50, 35), kind="spiky", win=(255, 140, 50))
        top = FY - (7 + e) + 1 - 8
        banner(cv, CX, top - 1, 9, (60, 50, 45), (175, 32, 26))
    s.add(FY, f)


def lm_nelf(s, st, stage):
    e = 3 if stage == 2 else 0
    def f(cv):
        t = cv.shape(outline=(40, 30, 55))
        trunk = [(y, CX - 2, CX + 2) for y in range(FY - 18 - e, FY - 3)]
        trunk += [(FY - 4, CX - 4, CX + 4), (FY - 3, CX - 5, CX + 5)]          # flared roots
        cv.rows(t, trunk, lambda x, y: (112, 86, 112) if x <= CX else (90, 68, 92))
        c = cv.shape(outline=(40, 30, 55))
        cy = FY - 22 - e
        rows = ell_rows(CX, cy, 10, 4) + ell_rows(CX - 9, cy + 3, 6, 3) + ell_rows(CX + 9, cy + 3, 6, 3) + ell_rows(CX, cy - 3, 6, 3)
        hi, mid, lo = (142, 114, 198), (106, 80, 166), (84, 62, 136)
        cv.rows(c, rows, lambda x, y: hi if (x < CX - 2 and y < cy) else (mid if x <= CX + 5 else lo))
        building(cv, CX - 7, FY, 15, 6, st["wall"], st["roof"], kind="leaf", win=st["win"])
    s.add(FY, f)


def lm_mountain(s, st, stage, dark=False):
    e = 3 if stage == 2 else 0
    rock = (78, 70, 68) if dark else (124, 114, 108)
    snow = (120, 60, 40) if dark else (232, 234, 240)
    glow = (255, 120, 40) if dark else (255, 160, 60)
    def f(cv):
        m = cv.shape()
        rows = tri_rows(CX, FY, 20 + e, 1, top_hw=1)
        peak = rows[-1][0]
        cv.rows(m, rows, lambda x, y: snow if y < peak + 4 else (rock if x <= CX else shade(rock, 0.8)))
        fr = cv.shape()
        frame = (176, 156, 124) if not dark else (110, 96, 90)
        gate_rows = [(y, CX - 5, CX + 5) for y in range(FY - 8, FY + 1)] + tri_rows(CX, FY - 9, 4, 1)
        cv.rows(fr, gate_rows, lambda x, y: frame)
        g = cv.shape(glow=glow)
        inner = [(y, CX - 3, CX + 3) for y in range(FY - 7, FY + 1)] + tri_rows(CX, FY - 8, 2, 1)
        cv.rows(g, inner, lambda x, y: (255, 200, 90) if abs(x - CX) <= 1 else glow)
        if dark:
            for cx_ in (CX - 12, CX + 12):
                c = cv.shape()
                cv.rect(c, cx_ - 1, FY - 16 - e, cx_ + 1, FY - 6, lambda x, y: (60, 54, 54))
                fl = cv.shape(outline=None, glow=(255, 120, 40))
                cv.put(fl, cx_, FY - 17 - e, (255, 170, 60))
    s.add(FY, f)


def lm_gnome(s, st, stage):
    e = 2 if stage == 2 else 0
    def f(cv):
        stack_x = CX + 7
        c = cv.shape()
        cv.rect(c, stack_x - 1, FY - 20 - e, stack_x + 1, FY - 6, lambda x, y: (128, 138, 148) if x <= stack_x else (104, 112, 122))
        puff = cv.shape(outline=None)
        for xx, yy in ((stack_x, FY - 22 - e), (stack_x - 1, FY - 23 - e), (stack_x + 1, FY - 23 - e), (stack_x - 2, FY - 25 - e),
                       (stack_x - 1, FY - 25 - e)):
            cv.put(puff, xx, yy, (236, 236, 240))
        building(cv, CX - 10, FY, 21, 6 + e, (156, 168, 178), (108, 188, 188), kind="dome", win=(250, 207, 231))
        g = cv.shape()
        gy = FY - (6 + e) - 4
        cv.rows(g, ell_rows(CX, gy, 2, 2), lambda x, y: (214, 182, 84))
        h = cv.shape(outline=None)
        cv.put(h, CX, gy, (90, 80, 70))
    s.add(FY, f)


def lm_tauren(s, st, stage):
    e = 2 if stage == 2 else 0
    def f(cv):
        m = cv.shape()
        mesa_top = FY - 11 - e
        rows = [(y, CX - 20 + (FY - y) // 2, CX + 20 - (FY - y) // 2) for y in range(mesa_top, FY + 1)]
        rock, rock_d = (182, 112, 70), (150, 90, 54)
        band = (160, 96, 58)
        cv.rows(m, rows, lambda x, y: (band if (FY - y) % 4 == 2 else rock) if x <= CX + 8 else rock_d)
        tent(cv, CX, mesa_top, 6, (196, 152, 104))
    s.add(FY, f)


def lm_ziggurat(s, st, stage, gold=False):
    tiers = 5 if stage == 2 else 4
    stone = (206, 182, 110) if gold else (150, 160, 128)
    def f(cv):
        for k in range(tiers):
            t = cv.shape()
            hw = 16 - k * 3
            y1 = FY - k * 4
            cv.rect(t, CX - hw, y1 - 3, CX + hw, y1, lambda x, y, k=k: shade(stone, 1 - k * 0.04) if x <= CX + hw // 2 else shade(stone, 0.8 - k * 0.04))
        st_ = cv.shape(outline=None)
        for y in range(FY - tiers * 4 + 1, FY + 1):
            cv.rows(st_, [(y, CX - 1, CX + 1)], lambda x, yy: shade(stone, 0.7))
        top = FY - tiers * 4
        if gold:
            building(cv, CX - 3, top, 7, 4, (230, 196, 80), (40, 120, 100), kind="hip", door=True)
        else:
            mk = cv.shape()
            cv.rect(mk, CX - 2, top - 3, CX + 2, top, lambda x, y: (238, 228, 206))
            d = cv.shape(outline=None)
            cv.put(d, CX - 1, top - 2, (30, 30, 30)); cv.put(d, CX + 1, top - 2, (30, 30, 30))
    s.add(FY, f)


def lm_belf(s, st, stage):
    e = 3 if stage == 2 else 0
    def f(cv):
        for tx in (CX - 14, mirror_x(CX - 14, 7)):
            tower(cv, tx, FY - 1, 7, 13 + e, st["wall"], st["roof"], kind="onion", trim=st["trim"], win=st["win"])
        tower(cv, CX - 4, FY, 9, 20 + e, st["wall"], st["roof"], kind="onion", trim=st["trim"], win=st["win"])
        r = cv.shape(outline=None, glow=(255, 220, 120))
        ry = FY - (20 + e) - 14
        cv.rows(r, [(ry, CX - 5, CX - 3), (ry, CX + 3, CX + 5), (ry - 1, CX - 6, CX - 6), (ry - 1, CX + 6, CX + 6),
                    (ry + 1, CX - 6, CX - 6), (ry + 1, CX + 6, CX + 6), (ry - 2, CX - 5, CX + 5), (ry + 2, CX - 5, CX + 5)],
                lambda x, y: (250, 214, 92))
    s.add(FY, f)


def lm_spires(s, st, stage, font=(250, 230, 130)):
    e = 3 if stage == 2 else 0
    def f(cv):
        for tx, w, h in ((CX - 15, 5, 11 + e), (CX - 10, 7, 16 + e)):
            tower(cv, tx, FY - 1, w, h, st["wall"], st["roof"], kind="spire", trim=st["trim"], win=st["win"])
            tower(cv, mirror_x(tx, w), FY - 1, w, h, st["wall"], st["roof"], kind="spire", trim=st["trim"], win=st["win"])
        tower(cv, CX - 3, FY, 7, 22 + e, st["wall"], st["roof"], kind="spire", trim=st["trim"], win=st["win"])
        if font:
            g = cv.shape(glow=font)
            cv.rows(g, ell_rows(CX, FY + 5, 3, 1), lambda x, y: font)
    s.add(FY, f)


def lm_pagoda(s, st, stage):
    tiers = 4 if stage == 2 else 3
    def f(cv):
        y = FY
        w = 19
        for k in range(tiers):
            hgt = 4 if k < tiers - 1 else 3
            building(cv, CX - (w - 1) // 2, y, w, hgt, (180, 50, 40), (40, 130, 110), kind="pagoda",
                     door=(k == 0), win=None)
            y = y - hgt - 1
            w -= 4
        finial(cv, CX, y - 1, (230, 190, 70), 3)
    s.add(FY, f)


def lm_ruin(s, st, stage):
    """Lordaeron's ruined keep: a parapet with missing merlons and a broken tower."""
    e = 3 if stage == 2 else 0
    stone = (96, 96, 106)
    win = (150, 230, 90)
    def keep(cv, x, foot, w, h, gaps=(), broken=False):
        top = foot - h + 1
        k = cv.shape()
        rows = [(y, x, x + w - 1) for y in range(top, foot + 1)]
        if broken:                                   # a stepped break down the right side
            rows = [(y, x, x + w - 1 - max(0, min(w - 3, (top + 5 - y)))) if y < top + 5 else (y, x, x + w - 1)
                    for y in range(top, foot + 1)]
        else:
            span = w + 2
            for o in range(span):
                m = min(o, span - 1 - o)
                if m % 5 < 3 and (m // 5) not in gaps:
                    for kk in (1, 2, 3):
                        rows.append((top - kk, x - 1 + o, x - 1 + o))
            rows.append((top, x - 1, x + w))
        cv.rows(k, rows, wall_tone(stone, x, w, top))
        d = cv.shape(outline=None)
        for wy in range(top + 3, foot - 1, 4):
            for wx in ((x + 2, x + w - 3) if w > 7 else (x + (w - 1) // 2,)):
                if cv.lab[wy][wx] == k:
                    cv.put(d, wx, wy, win)
        return top
    def f(cv):
        top = keep(cv, CX - 10, FY, 21, 11 + e, gaps=(1,))
        d = cv.shape(outline=None)
        for yy in range(FY - 2, FY):
            cv.put(d, CX, yy, (62, 42, 32))
        keep(cv, CX - 15, FY + 1, 7, 18 + e, broken=True)
        keep(cv, mirror_x(CX - 15, 7), FY + 1, 7, 15 + e)
    s.add(FY, f)


def lm_scourge(s, st, stage):
    e = 3 if stage == 2 else 0
    dark = (52, 60, 78)
    def f(cv):
        for k in range(3):
            t = cv.shape()
            hw = 14 - k * 3
            y1 = FY - k * 4
            cv.rect(t, CX - hw, y1 - 3, CX + hw, y1, lambda x, y, k=k, hw=hw: shade(dark, 1 - k * 0.05) if x <= CX + hw // 2 else shade(dark, 0.8))
        base = FY - 12
        for d in (-6, 6):                             # two lesser spires on the top tier
            sp = cv.shape()
            cv.rows(sp, tri_rows(CX + d, base, 1, 3), two_tone((70, 80, 102), CX + d))
        sp = cv.shape()
        cv.rows(sp, tri_rows(CX, base, 3, 4 + e // 3), two_tone((70, 80, 102), CX))
        g = cv.shape(outline=None, glow=(130, 205, 255))
        cv.rect(g, CX, base - 5, CX, base - 4, lambda x, y: (170, 232, 255))
    s.add(FY, f)


def lm_draenei(s, st, stage):
    e = 2 if stage == 2 else 0
    def f(cv):
        h = cv.shape()
        rows = tri_rows(CX, FY, 11, 2, top_hw=3)
        cv.rows(h, rows, two_tone((152, 136, 192), CX))
        d = cv.shape(outline=None)
        for wy in range(FY - 4, rows[-1][0] + 2, -4):
            cv.put(d, CX - 3, wy, (180, 225, 255)); cv.put(d, CX + 3, wy, (180, 225, 255))
        top = rows[-1][0]
        for cx_, ht in ((CX - 4, 7 + e), (CX + 4, 7 + e), (CX, 12 + e)):
            c = cv.shape(glow=(160, 205, 255))
            hw = 2 if cx_ == CX else 1
            body = [(y, cx_ - hw, cx_ + hw) for y in range(top - ht + hw + 1, top + 1)] + tri_rows(cx_, top - ht + hw, hw, 1)
            cv.rows(c, body, lambda x, y, cx_=cx_: (176, 222, 255) if x <= cx_ else (130, 180, 240))
    s.add(FY, f)


def lm_goblin(s, st, stage):
    e = 3 if stage == 2 else 0
    def f(cv):
        for sx in (CX - 6, CX + 6):
            c = cv.shape()
            cv.rect(c, sx - 1, FY - 20 - e, sx + 1, FY - 8, lambda x, y, sx=sx: (118, 118, 118) if x <= sx else (94, 94, 94))
            p = cv.shape(outline=None)
            for xx, yy in ((sx, FY - 22 - e), (sx - 1, FY - 23 - e), (sx, FY - 23 - e), (sx - 2, FY - 25 - e)):
                cv.put(p, xx, yy, (190, 190, 190))
        building(cv, CX - 9, FY, 19, 9 + e, (150, 110, 70), (190, 90, 40), kind="slab", win=(255, 220, 110))
        coin = cv.shape()
        cy = FY - (9 + e) - 4
        cv.rows(coin, ell_rows(CX, cy, 3, 3), lambda x, y: (250, 210, 40) if x <= CX else (222, 172, 22))
        d = cv.shape(outline=None)
        cv.rect(d, CX, cy - 1, CX, cy + 1, lambda x, y: (200, 150, 20))
    s.add(FY, f)


def lm_worgen(s, st, stage):
    e = 3 if stage == 2 else 0
    def f(cv):
        c = cv.shape()
        cv.rect(c, CX - 7, FY - 18 - e, CX - 5, FY - 6, lambda x, y: (84, 72, 66))
        building(cv, CX - 12, FY, 17, 8 + e, (130, 125, 120), (56, 60, 72), kind="gable", trim=(120, 40, 40), win=(255, 210, 120))
        tower(cv, CX + 5, FY + 1, 7, 21 + e, (120, 115, 112), (56, 60, 72), kind="spire")
        k = cv.shape()
        ky = FY + 1 - (21 + e) + 6
        cv.rows(k, ell_rows(CX + 8, ky, 2, 2), lambda x, y: (240, 230, 200))
        h = cv.shape(outline=None)
        cv.put(h, CX + 8, ky, (40, 30, 30)); cv.put(h, CX + 8, ky - 1, (40, 30, 30))
    s.add(FY, f)


def lm_keep(s, st, stage):
    e = 3 if stage == 2 else 0
    def f(cv):
        tower(cv, CX - 3, FY - 9 - e + 3, 7, 11 + e, st["stone"], st["roof"], kind="spire", trim=st["trim"])
        building(cv, CX - 8, FY, 17, 9 + e, st["wall"], st["stone"], kind="flat", win=st["win"])
    s.add(FY, f)


# ------------------------------------------------------------------ extras (small props)
EX_L, EX_R = CX - 5, CX + 5       # prop pair flanking the main street, mirrored about column 32
EX_C = CX                         # a single prop stands in the middle of the street
PROP_Y = {0: OY + 46, 1: OY + 47, 2: OY + 42}   # street foot row per stage (in front of the wall at stage 2)
EX_Y = PROP_Y[1]                  # set per scene in city_center_canvas


def pair(fn):
    """Run a prop function at both prop spots."""
    def e(s, st, stage):
        s.add(PROP_Y[stage] + 2, lambda cv: (fn(cv, EX_L), fn(cv, EX_R)))
    return e


def one(fn):
    def e(s, st, stage):
        s.add(PROP_Y[stage] + 2, lambda cv: fn(cv, EX_C))
    return e


def p_stakes(cv, x):
    p = cv.shape()
    for i in (-2, 0, 2):
        cv.rect(p, x + i, EX_Y - 6, x + i, EX_Y, lambda xx, y: (112, 82, 52))
    t = cv.shape(outline=None)
    for i in (-2, 0, 2):
        cv.put(t, x + i, EX_Y - 7, (225, 214, 190))


def p_fountain(cv, x):
    b = cv.shape()
    cv.rows(b, ell_rows(x, EX_Y - 1, 4, 2), lambda xx, y: (196, 194, 188) if xx <= x else (168, 166, 160))
    w = cv.shape(outline=None)
    cv.rows(w, ell_rows(x, EX_Y - 1, 2, 1), lambda xx, y: (120, 180, 230))
    j = cv.shape(outline=None)
    for y in range(EX_Y - 5, EX_Y - 2):
        cv.put(j, x, y, (190, 225, 250))


def p_moonwell(cv, x):
    r = cv.shape()
    cv.rows(r, ell_rows(x, EX_Y - 1, 4, 2), lambda xx, y: (186, 186, 206))
    w = cv.shape(outline=None, glow=(150, 212, 255))
    cv.rows(w, ell_rows(x, EX_Y - 1, 2, 1), lambda xx, y: (150, 212, 255))


def p_tree(cv, x):
    t = cv.shape(outline=(40, 30, 55))
    cv.rect(t, x - 1, EX_Y - 4, x + 1, EX_Y, lambda xx, y: (92, 72, 92))
    c = cv.shape(outline=(40, 30, 55))
    cy = EX_Y - 6
    cv.rows(c, ell_rows(x, cy, 3, 2), lambda xx, y: (140, 112, 196) if xx < x and y < cy else (110, 82, 170))


def p_forge(fire):
    def f(cv, x):
        a = cv.shape()
        cv.rect(a, x - 3, EX_Y - 3, x + 3, EX_Y, lambda xx, y: (96, 90, 90) if xx <= x else (78, 72, 72))
        g = cv.shape(outline=None, glow=fire)
        cv.rows(g, [(EX_Y - 4, x - 1, x + 1), (EX_Y - 5, x, x)], lambda xx, y: fire)
    return f


def p_gear(cv, x):
    cy = EX_Y - 4
    g = cv.shape()
    cv.rows(g, ell_rows(x, cy, 3, 3), lambda xx, y: (204, 172, 82))
    for dx, dy in ((0, -4), (0, 4), (-4, 0), (4, 0)):
        cv.put(g, x + dx, cy + dy, (204, 172, 82))
    h = cv.shape(outline=None)
    cv.put(h, x, cy, (90, 80, 70))


def p_totem(cv, x):
    t = cv.shape()
    for k, c in enumerate(((200, 62, 42), (240, 200, 72), (60, 120, 170))):
        cv.rect(t, x - 1, EX_Y - 2 - k * 3, x + 1, EX_Y - k * 3, lambda xx, y, c=c: c)
    cv.rows(t, [(EX_Y - 10, x - 3, x + 3), (EX_Y - 9, x - 1, x + 1)], lambda xx, y: (240, 200, 72))


def p_torch(cv, x):
    p = cv.shape(outline=None)
    for y in range(EX_Y - 5, EX_Y + 1):
        cv.put(p, x, y, (112, 82, 52))
    g = cv.shape(outline=None, glow=(255, 150, 50))
    cv.rows(g, [(EX_Y - 6, x, x), (EX_Y - 7, x, x)], lambda xx, y: (255, 176, 64))


def p_lantern(cv, x):
    p = cv.shape(outline=None)
    for y in range(EX_Y - 4, EX_Y + 1):
        cv.put(p, x, y, (90, 60, 40))
    g = cv.shape(glow=(255, 150, 80))
    cv.rect(g, x - 1, EX_Y - 7, x + 1, EX_Y - 5, lambda xx, y: (236, 78, 50))


def p_cauldron(cv, x):
    p = cv.shape()
    cv.rows(p, ell_rows(x, EX_Y - 2, 3, 2), lambda xx, y: (62, 62, 68))
    g = cv.shape(outline=None, glow=(140, 230, 80))
    cv.rows(g, [(EX_Y - 4, x - 2, x + 2)], lambda xx, y: (140, 230, 80))


def p_obelisk(cv, x):
    o = cv.shape()
    cv.rows(o, [(y, x - 1, x + 1) for y in range(EX_Y - 7, EX_Y + 1)] + [(EX_Y - 8, x, x), (EX_Y - 9, x, x)],
            lambda xx, y: (56, 66, 86) if xx <= x else (44, 52, 70))
    g = cv.shape(outline=None, glow=(120, 200, 255))
    cv.put(g, x, EX_Y - 5, (160, 225, 255))


def p_crystal(cv, x):
    c = cv.shape(glow=(150, 200, 255))
    cv.rows(c, [(y, x - 1, x + 1) for y in range(EX_Y - 5, EX_Y + 1)] + [(EX_Y - 6, x, x)],
            lambda xx, y: (176, 222, 255) if xx <= x else (130, 180, 240))


def p_crane(cv, x):
    c = cv.shape(outline=None)
    for y in range(EX_Y - 12, EX_Y + 1):
        cv.put(c, x + 2, y, (204, 152, 42))
    for xx in range(x - 3, x + 3):
        cv.put(c, xx, EX_Y - 12, (204, 152, 42))
    for y in range(EX_Y - 11, EX_Y - 7):
        cv.put(c, x - 3, y, (80, 80, 80))
    b = cv.shape()
    cv.rect(b, x - 4, EX_Y - 7, x - 2, EX_Y - 5, lambda xx, y: (150, 110, 70))


def p_lamp(cv, x):
    p = cv.shape(outline=None)
    for y in range(EX_Y - 5, EX_Y + 1):
        cv.put(p, x, y, (40, 40, 46))
    g = cv.shape(glow=(255, 210, 120))
    cv.rect(g, x - 1, EX_Y - 8, x + 1, EX_Y - 6, lambda xx, y: (255, 222, 124))


e_orc = pair(p_stakes)
e_fountain = one(p_fountain)
e_gnome = one(p_gear)
e_tauren = pair(p_totem)
e_torches = pair(p_torch)
e_lanterns = pair(p_lantern)
e_obelisks = pair(p_obelisk)
e_crystals = pair(p_crystal)
e_crane = one(p_crane)
e_lamps = pair(p_lamp)


def e_forge(fire=(255, 150, 40)):
    return one(p_forge(fire))


def e_nelf(s, st, stage):
    s.add(PROP_Y[stage] + 2, lambda cv: (p_tree(cv, EX_L - 2), p_tree(cv, EX_R + 2), p_moonwell(cv, EX_C)))


def e_cauldron(s, st, stage):
    s.add(PROP_Y[stage] + 2, lambda cv: p_cauldron(cv, EX_C))


def e_none(s, st, stage):
    pass


# ------------------------------------------------------------------ styles
def S(**kw):
    base = dict(wall=(200, 195, 180), roof=(150, 60, 40), roof2=None, trim=None, win=(255, 220, 120),
                ground=(150, 140, 120), stone=(165, 160, 150), cap=None, house="gable", big="hip",
                tower_roof="spire", extras=e_none, landmark=lm_keep)
    base.update(kw)
    if base["cap"] is None:
        base["cap"] = base["stone"] if base["tower_roof"] in ("flat", "slab") else base["roof"]
    return base


STYLES = {
    "Humans": S(wall=(226, 221, 206), roof=(40, 70, 160), trim=(236, 196, 72), ground=(172, 166, 150),
                stone=(202, 198, 190), house="gable", big="hip", extras=e_fountain,
                landmark=lm_castle),
    "Kul Tirans": S(wall=(216, 210, 196), roof=(30, 70, 96), trim=(230, 220, 190), ground=(166, 160, 146),
                    stone=(186, 182, 172), house="gable", big="hip", win=(255, 226, 140), extras=e_fountain,
                    landmark=lambda s, st, stage: lm_castle(s, st, stage, lighthouse=True)),
    "Orcs": S(wall=(124, 80, 50), roof=(150, 50, 35), roof2=(72, 64, 62), ground=(150, 102, 70), stone=(112, 76, 50),
              house="spiky", big="spiky", tower_roof="spiky", win=(255, 140, 50), extras=e_orc, landmark=lm_orc),
    "Night Elves": S(wall=(216, 216, 236), roof=(112, 80, 172), roof2=(70, 130, 150), ground=(122, 150, 112),
                     stone=(192, 190, 216), house="leaf", big="leaf", tower_roof="leaf", win=(170, 230, 255),
                     extras=e_nelf, landmark=lm_nelf),
    "Dwarves": S(wall=(152, 142, 132), roof=(104, 98, 94), trim=(200, 150, 60), ground=(142, 132, 122),
                 stone=(132, 124, 116), house="flat", big="flat", tower_roof="flat", win=(255, 160, 60),
                 extras=e_forge(), landmark=lm_mountain),
    "Dark Iron Dwarves": S(wall=(74, 66, 66), roof=(50, 44, 46), trim=(255, 120, 30), ground=(96, 82, 76),
                           stone=(78, 70, 70), house="flat", big="flat", tower_roof="flat", win=(255, 120, 40),
                           extras=e_forge((255, 110, 30)),
                           landmark=lambda s, st, stage: lm_mountain(s, st, stage, dark=True)),
    "Gnomes": S(wall=(160, 170, 180), roof=(60, 150, 150), roof2=(236, 160, 200), ground=(142, 146, 152),
                stone=(150, 156, 166), house="dome", big="dome", tower_roof="dome", win=(250, 207, 231),
                extras=e_gnome, landmark=lm_gnome),
    "Tauren": S(wall=(190, 140, 90), roof=(186, 140, 96), roof2=(204, 162, 112), ground=(172, 132, 86),
                stone=(162, 112, 72), house="tent", big="tent", tower_roof="cone", extras=e_tauren, landmark=lm_tauren),
    "Trolls": S(wall=(152, 122, 82), roof=(190, 166, 92), roof2=(152, 132, 72), ground=(152, 132, 92),
                stone=(150, 160, 130), house="thatch", big="thatch", tower_roof="cone", extras=e_torches,
                landmark=lm_ziggurat),
    "Zandalari Trolls": S(wall=(192, 170, 120), roof=(240, 196, 62), roof2=(40, 120, 100), ground=(162, 142, 96),
                          stone=(206, 186, 132), house="thatch", big="thatch", tower_roof="cone", win=(255, 220, 110),
                          extras=e_torches, landmark=lambda s, st, stage: lm_ziggurat(s, st, stage, gold=True)),
    "Blood Elves": S(wall=(242, 232, 216), roof=(178, 32, 42), trim=(240, 200, 70), ground=(202, 172, 122),
                     stone=(232, 222, 202), house="onion", big="onion", tower_roof="onion",
                     extras=e_none, landmark=lm_belf),
    "High Elves": S(wall=(242, 242, 246), roof=(50, 100, 200), trim=(222, 202, 122), ground=(172, 182, 172),
                    stone=(226, 226, 232), house="spire", big="spire", extras=e_none,
                    landmark=lm_spires),
    "Pandaren": S(wall=(180, 52, 42), roof=(40, 130, 110), ground=(162, 152, 122), stone=(172, 162, 142),
                  house="pagoda", big="pagoda", tower_roof="hip", extras=e_lanterns, landmark=lm_pagoda),
    "Forsaken": S(wall=(102, 102, 110), roof=(62, 56, 72), trim=(120, 60, 140), ground=(106, 102, 106),
                  stone=(96, 96, 106), house="gable", big="spire", win=(150, 230, 90), extras=e_cauldron, landmark=lm_ruin),
    "Scourge": S(wall=(82, 92, 112), roof=(46, 56, 76), trim=(130, 200, 246), ground=(186, 196, 210),
                 stone=(82, 92, 106), house="spire", big="spire", win=(150, 220, 255),
                 extras=e_obelisks, landmark=lm_scourge),
    "Draenei": S(wall=(162, 146, 202), roof=(110, 90, 172), trim=(160, 210, 255), ground=(152, 146, 176),
                 stone=(152, 142, 186), house="dome", big="dome", tower_roof="spire", win=(170, 220, 255),
                 extras=e_crystals, landmark=lm_draenei),
    "Goblins": S(wall=(150, 110, 70), roof=(190, 90, 40), roof2=(130, 136, 140), ground=(142, 122, 90),
                 stone=(132, 110, 80), house="slab", big="slab", tower_roof="slab", win=(255, 220, 110),
                 extras=e_crane, landmark=lm_goblin),
    "Worgen": S(wall=(130, 125, 120), roof=(56, 60, 72), trim=(120, 40, 40), ground=(122, 118, 116),
                stone=(116, 112, 110), house="gable", big="gable", win=(255, 210, 120), extras=e_lamps, landmark=lm_worgen),
    "_cs": S(wall=(202, 192, 172), roof=(150, 70, 45), ground=(152, 142, 122), stone=(166, 160, 150),
             house="gable", big="hip", landmark=lm_keep),
}
STYLES["_dalaran"] = S(wall=(228, 222, 238), roof=(122, 72, 192), trim=(232, 202, 92), ground=(172, 166, 160),
                       stone=(206, 200, 214), house="spire", big="spire",
                       landmark=lambda s, st, stage: lm_spires(s, st, stage, font=(200, 150, 255)))

CITY_STATE_STYLE = {
    "Dalaran": "_dalaran", "Theramore": "Humans", "Stromgarde": "Humans", "Gadgetzan": "Goblins",
    "Booty Bay": "Goblins", "Ratchet": "Goblins", "Everlook": "Goblins", "Steamwheedle Port": "Goblins",
    "Light's Hope Chapel": "Humans", "Cenarion Hold": "Night Elves", "Argent Vanguard": "Humans",
    "Feathermoon Stronghold": "Night Elves", "The Earthen Ring": "Tauren", "Knights of the Ebon Blade": "Scourge",
    "Explorers' League": "Dwarves", "Thorium Brotherhood": "Dwarves",
}

# house slots per stage, left half only: (x, foot row on the hex face, width, wall height).
# Each one is mirrored about column 32, so every town is laid out on the same axis.
SLOTS = {
    0: [(7, 30, 11, 6), (17, 40, 11, 6)],
    1: [(3, 31, 11, 6), (9, 40, 11, 6), (17, 45, 9, 5)],
    2: [(2, 31, 11, 6), (8, 39, 11, 6), (17, 42, 9, 5)],
}


def city_center_canvas(style_name, stage, small=False):
    global EX_Y, SMALL
    EX_Y = PROP_Y[stage]
    SMALL = small
    st = STYLES[style_name]
    s = Scene()
    plaza(s, st["ground"], 24 + stage * 2, 11 + stage)
    roofs = [st["roof"]] + ([st["roof2"]] if st.get("roof2") else [])
    slots = SLOTS[stage]
    if small and len(slots) > 2:                  # the 32-px tile keeps the back and front rows only
        slots = [slots[0], slots[-1]]
    for i, (x, y, w, h) in enumerate(slots):
        roof_c = roofs[i % len(roofs)]
        for xx in (x, mirror_x(x, w)):
            s.add(OY + y, lambda cv, xx=xx, y=y, w=w, h=h, roof_c=roof_c:
                  building(cv, xx, OY + y, w, h + (1 if stage == 2 else 0), st["wall"], roof_c, kind=st["house"],
                           trim=st["trim"] if st["house"] != "flat" else None, win=st["win"]))
    if stage == 0:
        s.add(OY + 26, lambda cv: building(cv, CX - 6, OY + 26, 13, 7, st["wall"], st["roof"], kind=st["big"],
                                           trim=st["trim"], win=st["win"]))
    else:
        st["landmark"](s, st, stage)
    st["extras"](s, st, stage)
    if stage == 2:
        city_wall(s, st)
    return s.canvas()


def city_center(style_name, stage, seed=0):
    return city_center_canvas(style_name, stage).image()


def write_all(images_dir, eras, nations, city_states):
    """Write race city centers, city-state ones, and the generic era replacements into
    the HexaRealm (64 px) and FantasyHex (32 px) tile folders."""
    out = {}
    cache = {}
    def get(style, stage):
        if (style, stage) not in cache:
            big = city_center_canvas(style, stage).image()
            small = city_center_canvas(style, stage, small=True).half().image()
            cache[(style, stage)] = (big, small)
        return cache[(style, stage)]
    for n in nations:
        if n not in STYLES:
            continue
        for era, stage in STAGES:
            out["City center-%s-%s" % (n, era)] = get(n, stage)
    for cs in city_states:
        style = CITY_STATE_STYLE.get(cs, "_cs")
        for era, stage in STAGES:
            out["City center-%s-%s" % (cs, era)] = get(style, stage)
    for era, stage in ERA_STAGE.items():
        out["City center-%s" % era] = get("_cs", stage)
    out["City center"] = get("_cs", 0)
    for name, (big, small) in out.items():
        for folder, im in (("TileSets/HexaRealm/Tiles/", big), ("TileSets/FantasyHex/Tiles/", small)):
            path = os.path.join(images_dir, folder, name + ".png")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            im.save(path)
    return len(out)
