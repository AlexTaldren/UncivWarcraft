"""Race-styled tile improvements, drawn with the city-center renderer (citycenters.py).

Every faction's farmstead, mine, lumber mill, trading post, pasture, plantation,
quarry, fishing boats, hunting camp and fort are built from the same pieces, colours
and roof shapes as its city centers, so a race's land reads as one architecture:
Blood Elf onion domes, Goblin slab roofs, Scourge spires, Pandaren eaves and so on.

The same pixel rules apply as for the city centers: whole-pixel geometry, odd widths
under every peak, and one shared outline pass per layer, so lines are 1 px and
touching pieces share one line. Thin rigging (poles, rails, ropes, nets) is drawn as
1-px colour lines without an outline, the same way as banner poles in the towns.

Each scene can also hold finished images (a herd, crop rows, the stock resource)
at a depth; the drawn pieces behind and in front of it are rendered as separate
layers around it. All art is original.
"""
import math

from PIL import Image

import citycenters as CC
from citycenters import shade, odd, tri_rows, ell_rows, two_tone, wall_tone

TW, TH = 64, 56
OUT = CC.OUT


# ------------------------------------------------------------------ scene with image layers
class Scene:
    def __init__(self, w=TW, h=TH):
        self.w, self.h = w, h
        self.items = []

    def add(self, depth, item):
        """item: a function drawing onto a Canvas, or a finished RGBA image."""
        self.items.append((depth, len(self.items), item))

    def render(self):
        out = Image.new("RGBA", (self.w, self.h))
        batch = []
        def flush():
            if batch:
                cv = CC.Canvas(self.w, self.h)
                for fn in batch:
                    fn(cv)
                out.alpha_composite(cv.image())
                batch.clear()
        for _, _, item in sorted(self.items, key=lambda t: (t[0], t[1])):
            if isinstance(item, Image.Image):
                flush()
                out.alpha_composite(item)
            else:
                batch.append(item)
        flush()
        return out


# ------------------------------------------------------------------ raster helpers
def poly_rows(pts):
    """Scanline spans of an integer polygon (filled at pixel centres)."""
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


def line_px(x0, y0, x1, y1):
    """Bresenham line: one pixel per step, so diagonals stay a clean 1-px stair."""
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    out = []
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


def thin(cv, pts, col):
    """A 1-px colour line without an outline (poles, rails, ropes)."""
    s = cv.shape(outline=None)
    for x, y in pts:
        cv.put(s, x, y, col)


def vline(cv, x, y0, y1, col):
    thin(cv, [(x, y) for y in range(min(y0, y1), max(y0, y1) + 1)], col)


def hline(cv, x0, x1, y, col):
    thin(cv, [(x, y) for x in range(min(x0, x1), max(x0, x1) + 1)], col)


# ------------------------------------------------------------------ race styles
# Fort and fence material per race; the colours of walls, roofs and trim come from
# the race's city-center style.
MATERIAL = {
    "Humans": "stone", "Kul Tirans": "stone", "Blood Elves": "stone", "High Elves": "stone", "Worgen": "stone",
    "Forsaken": "stone", "Draenei": "stone", "Dwarves": "stone", "Dark Iron Dwarves": "stone",
    "Orcs": "palisade", "Tauren": "palisade", "Trolls": "palisade", "Zandalari Trolls": "palisade",
    "Night Elves": "thorn", "Gnomes": "metal", "Goblins": "metal", "Pandaren": "lacquer", "Scourge": "saronite",
}
FLAG = {
    "Humans": (40, 70, 160), "Kul Tirans": (30, 80, 110), "Orcs": (172, 32, 26), "Night Elves": (150, 210, 255),
    "Dwarves": (30, 70, 150), "Dark Iron Dwarves": (255, 120, 30), "Gnomes": (236, 160, 200), "Tauren": (190, 62, 42),
    "Trolls": (60, 140, 120), "Zandalari Trolls": (40, 130, 110), "Blood Elves": (172, 26, 36), "High Elves": (50, 100, 200),
    "Pandaren": (236, 196, 72), "Forsaken": (120, 60, 140), "Scourge": (130, 200, 246), "Draenei": (160, 210, 255),
    "Goblins": (236, 196, 60), "Worgen": (120, 40, 40),
}
LAMP = {"Forsaken": (150, 230, 90), "Scourge": (130, 205, 255), "Draenei": (170, 200, 255),
        "Dark Iron Dwarves": (255, 130, 50)}
FIRE = {"Forsaken": (140, 240, 90), "Scourge": (120, 200, 255), "Draenei": (170, 150, 255),
        "Dark Iron Dwarves": (255, 120, 40)}
DEAD = ("Scourge", "Forsaken")


def style(race):
    st = dict(CC.STYLES[race])
    st["race"] = race
    st["mat"] = MATERIAL[race]
    st["fcol"] = st["stone"]
    st["flag"] = FLAG[race]
    st["lamp"] = LAMP.get(race)
    st["small_roof"] = {"pagoda": "hip", "tent": "tent", "cone": "cone"}.get(st["house"], st["house"])
    return st


def house(cv, st, x, foot, w, h, kind=None, roof=None, door=True):
    k = kind or st["house"]
    CC.building(cv, x, foot, odd(w), h, st["wall"], roof or st["roof"], kind=k,
                trim=st["trim"] if k != "flat" else None, win=st["win"], door=door)


# ------------------------------------------------------------------ props
def cc_prop(fn, cv, x, y):
    old = CC.EX_Y
    CC.EX_Y = y
    try:
        fn(cv, x)
    finally:
        CC.EX_Y = old


def p_barrel(cv, x, y):
    b = cv.shape()
    cv.rows(b, ell_rows(x, y - 3, 2, 3), lambda xx, yy: (112, 116, 122) if xx <= x else (90, 94, 100))
    t = cv.shape(outline=None)
    hline(cv, x - 1, x + 1, y - 3, (190, 90, 40))
    cv.put(t, x, y - 7, (240, 210, 60))


def prop(cv, st, x, y):
    """The race's small prop, standing with its foot at (x, y)."""
    r = st["race"]
    if r in ("Humans", "Kul Tirans", "High Elves", "Blood Elves"):
        pole = (220, 180, 70) if r == "Blood Elves" else (200, 200, 210) if r == "High Elves" else (100, 80, 60)
        CC.banner(cv, x, y, 9, pole, st["flag"])
    elif r == "Orcs":
        cc_prop(CC.p_stakes, cv, x, y)
    elif r == "Night Elves":
        cc_prop(CC.p_tree, cv, x, y)
    elif r == "Dwarves":
        cc_prop(CC.p_forge((255, 150, 40)), cv, x, y)
    elif r == "Dark Iron Dwarves":
        cc_prop(CC.p_forge((255, 110, 30)), cv, x, y)
    elif r == "Gnomes":
        cc_prop(CC.p_gear, cv, x, y)
    elif r == "Tauren":
        cc_prop(CC.p_totem, cv, x, y)
    elif r in ("Trolls", "Zandalari Trolls"):
        cc_prop(CC.p_torch, cv, x, y)
    elif r == "Pandaren":
        cc_prop(CC.p_lantern, cv, x, y)
    elif r == "Forsaken":
        cc_prop(CC.p_cauldron, cv, x, y)
    elif r == "Scourge":
        cc_prop(CC.p_obelisk, cv, x, y)
    elif r == "Draenei":
        cc_prop(CC.p_crystal, cv, x, y)
    elif r == "Goblins":
        p_barrel(cv, x, y)
    elif r == "Worgen":
        cc_prop(CC.p_lamp, cv, x, y)


# ------------------------------------------------------------------ walls and fences
def wall(cv, st, x, foot, w, h, gate=False):
    """A straight wall in the race's material, its face spanning x..x+w-1 (w odd)."""
    w = odd(w)
    mat, col = st["mat"], st["fcol"]
    top = foot - h + 1
    cx = x + (w - 1) // 2
    if mat == "stone":
        CC.building(cv, x, foot, w, h, col, col, kind="flat", door=False)
        if st.get("trim"):
            t = cv.shape(outline=None)
            for xx in range(x + 2, x + w - 2, 4):
                cv.put(t, xx, top + 2, st["trim"])
    elif mat == "palisade":
        s = cv.shape()
        rows = [(y, x, x + w - 1) for y in range(top, foot + 1)]
        for xx in range(x, x + w):
            if (xx - x) % 3 == 1:
                rows += [(top - 1, xx, xx), (top - 2, xx, xx)]
        dark = shade(col, 0.82)
        cv.rows(s, rows, lambda xx, yy: dark if (xx - x) % 3 == 2 else col)
    elif mat == "thorn":
        s = cv.shape()
        cv.rect(s, x, top, x + w - 1, foot, wall_tone(col, x, w, top))
        for lx in range(x + 2, x + w - 2, 6):
            l = cv.shape()
            cv.rows(l, ell_rows(lx, top - 1, 2, 1), lambda xx, yy: (90, 160, 100) if xx <= lx else (70, 130, 84))
    elif mat == "metal":
        s = cv.shape()
        cv.rows(s, [(y, x, x + w - 1) for y in range(top, foot + 1)] + [(top - 1, x - 1, x + w)],
                lambda xx, yy: shade(col, 1.1) if yy == top - 1 else wall_tone(col, x, w, top)(xx, yy))
        r = cv.shape(outline=None)
        rivet = (190, 90, 40) if st["race"] == "Goblins" else shade(col, 1.35)
        for xx in range(x + 2, x + w - 2, 4):
            cv.put(r, xx, top + (h - 1) // 2, rivet)
    elif mat == "lacquer":
        s = cv.shape()
        cv.rect(s, x, top, x + w - 1, foot, wall_tone(st["wall"], x, w, top))
        c = cv.shape()
        cv.rows(c, [(top, x - 1, x + w), (top - 1, x - 1, x + w), (top - 2, x - 2, x - 2), (top - 2, x + w + 1, x + w + 1)],
                two_tone(st["roof"], cx))
    elif mat == "saronite":
        s = cv.shape()
        cv.rows(s, [(y, x, x + w - 1) for y in range(top, foot + 1)] + [(top - 1, x - 1, x + w)],
                lambda xx, yy: shade(col, 1.1) if yy == top - 1 else wall_tone(col, x, w, top)(xx, yy))
        b = cv.shape(outline=None)
        for xx in range(x + 1, x + w - 1, 4):
            cv.put(b, xx, top - 2, (225, 222, 205))
            cv.put(b, xx, top - 3, (225, 222, 205))
        g = cv.shape(outline=None, glow=None)
        for xx in range(x + 3, x + w - 3, 8):
            cv.put(g, xx, top + (h - 1) // 2, (130, 205, 255))
    if gate:
        d = cv.shape(outline=None)
        for yy in range(foot - 3, foot):
            for xx in range(cx - 2, cx + 3):
                if not (yy == foot - 3 and xx in (cx - 2, cx + 2)):
                    cv.put(d, xx, yy, (62, 42, 32))


def side_wall(cv, st, x, y_back, y_front, h):
    """A wall running from the back to the front, seen end-on: a 5-px band."""
    col = shade(st["fcol"] if st["mat"] != "lacquer" else st["wall"], 0.86)
    s = cv.shape()
    cv.rect(s, x, y_back - h + 1, x + 4, y_front, lambda xx, yy: col if xx < x + 3 else shade(col, 0.85))


def fence(cv, st, pts):
    """A field fence along a polyline, in the race's material."""
    mat = st["mat"]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        base = line_px(x0, y0, x1, y1)
        if mat == "stone":                       # a low dry-stone wall, two pixels high
            s = cv.shape()
            for x, y in base:
                cv.put(s, x, y, st["fcol"])
                cv.put(s, x, y - 1, st["fcol"])
                cv.put(s, x, y - 2, st["fcol"])
        elif mat == "thorn":                     # a hedge with blossoms
            s = cv.shape()
            for x, y in base:
                for k in (0, 1, 2):
                    cv.put(s, x, y - k, (74, 120, 86))
            b = cv.shape(outline=None)
            for i, (x, y) in enumerate(base):
                if i % 6 == 3:
                    cv.put(b, x, y - 1, st["roof"])
        else:                                    # posts and two rails
            rail = {"palisade": (124, 86, 52), "metal": shade(st["fcol"], 0.95), "lacquer": st["wall"],
                    "saronite": (225, 222, 205)}[mat]
            post = shade(rail, 0.7)
            thin(cv, [(x, y - 1) for x, y in base] + [(x, y - 3) for x, y in base], rail)
            thin(cv, [(x, y - k) for i, (x, y) in enumerate(base) if i % 4 == 0 for k in range(0, 5)], post)


# ------------------------------------------------------------------ improvements
def farmstead(race):
    st = style(race)
    s = Scene()
    s.add(34, lambda cv: house(cv, st, 25, 34, 13, 7))
    if race not in DEAD:
        def rick(cv):                           # a hay rick
            h = cv.shape()
            cv.rows(h, ell_rows(42, 31, 3, 3) + ell_rows(42, 28, 2, 2),
                    lambda x, y: (232, 204, 110) if x <= 42 and y < 31 else (206, 176, 86))
        s.add(32, rick)
    else:
        def crates(cv):                         # sacks of grain under a tarp
            c = cv.shape()
            cv.rect(c, 39, 29, 45, 32, lambda x, y: (120, 112, 104) if x <= 42 else (98, 92, 86))
        s.add(32, crates)
    s.add(35, lambda cv: prop(cv, st, 19, 35))
    return s.render()


def portal(cv, st, x, foot, w=13, h=10):
    """The pit-head frame over the tunnel mouth, in the race's wall material."""
    mat, col = st["mat"], st["fcol"]
    top = foot - h + 1
    cx = x + (w - 1) // 2
    if mat in ("stone", "saronite", "lacquer"):
        pc = st["wall"] if mat == "lacquer" else shade(col, 1.05)
        for px in (x, x + w - 3):
            p = cv.shape()
            cv.rect(p, px, top, px + 2, foot, lambda xx, yy, px=px: pc if xx < px + 2 else shade(pc, 0.82))
        l = cv.shape()
        cv.rect(l, x - 1, top - 2, x + w, top, lambda xx, yy: shade(pc, 1.05) if xx <= cx else shade(pc, 0.85))
        if mat == "lacquer":
            CC.eave(cv, cx, top - 3, (w + 1) // 2 + 1, st["roof"])
        if mat == "saronite":
            b = cv.shape(outline=None)
            for xx in (x, cx, x + w - 1):
                vline(cv, xx, top - 5, top - 3, (225, 222, 205))
        if st.get("trim"):
            t = cv.shape(outline=None)
            cv.put(t, cx, top - 1, st["trim"])
    elif mat == "metal":
        for px in (x, x + w - 3):
            p = cv.shape()
            cv.rect(p, px, top, px + 2, foot, lambda xx, yy: shade(col, 1.0))
        b = cv.shape()
        cv.rect(b, x - 1, top - 2, x + w, top, lambda xx, yy: shade(col, 1.1))
        g = cv.shape()
        cv.rows(g, ell_rows(cx, top - 5, 3, 3), lambda xx, yy: (204, 172, 82) if xx <= cx else (176, 146, 66))
        hb = cv.shape(outline=None)
        cv.put(hb, cx, top - 5, (90, 80, 70))
    elif mat == "thorn":
        for px in (x, x + w - 3):
            p = cv.shape(outline=(40, 30, 55))
            cv.rect(p, px, top, px + 2, foot, lambda xx, yy: (110, 86, 112))
        a = cv.shape(outline=(40, 30, 55))
        cv.rows(a, ell_rows(cx, top - 1, (w + 3) // 2, 3), lambda xx, yy: st["roof"] if xx <= cx else shade(st["roof"], 0.8))
    else:                                       # timber with tusks: orcs, tauren, trolls
        wood = col
        for px in (x, x + w - 3):
            p = cv.shape()
            cv.rect(p, px, top, px + 2, foot, lambda xx, yy: wood if xx % 2 else shade(wood, 0.85))
        b = cv.shape()
        cv.rect(b, x - 2, top - 2, x + w + 1, top, lambda xx, yy: shade(wood, 1.05))
        thin(cv, [(x - 3, top - 3), (x - 4, top - 4), (x + w + 2, top - 3), (x + w + 3, top - 4)], (235, 225, 200))


def mine(race):
    st = style(race)
    s = Scene()
    rock = st["stone"]
    def mound(cv):
        m = cv.shape()
        cv.rows(m, ell_rows(30, 30, 19, 11) + ell_rows(26, 24, 12, 7),
                lambda x, y: shade(rock, 1.05) if (x < 26 and y < 26) else (rock if x <= 38 else shade(rock, 0.82)))
        mo = cv.shape(outline=None)
        cv.rows(mo, ell_rows(30, 31, 4, 4), lambda x, y: (28, 22, 22))
    s.add(24, mound)
    s.add(34, lambda cv: portal(cv, st, 24, 34))
    if st["lamp"] or st["win"]:
        lamp = st["lamp"] or st["win"]
        def l(cv):
            g = cv.shape(outline=None, glow=lamp)
            cv.rect(g, 30, 29, 30, 30, lambda x, y: lamp)
        s.add(35, l)
    def cart(cv):
        c = cv.shape()
        cv.rows(c, poly_rows([(41, 38), (51, 38), (49, 43), (43, 43)]), lambda x, y: (128, 90, 54) if x <= 46 else (104, 72, 44))
        o = cv.shape()
        ore2 = st["trim"] or (206, 176, 92)
        cv.rows(o, ell_rows(44, 37, 2, 1) + ell_rows(48, 37, 2, 1), lambda x, y: (152, 146, 140) if x < 46 else ore2)
        for wx in (43, 49):
            wh = cv.shape()
            cv.rows(wh, ell_rows(wx, 44, 1, 1), lambda x, y: (62, 56, 50))
    s.add(44, cart)
    s.add(42, lambda cv: house(cv, st, 7, 42, 11, 6))
    s.add(33, lambda cv: prop(cv, st, 54, 33))
    return s.render()


def logs(cv, x, y, col):
    for dx, dy in ((0, 0), (5, 0), (2, -3)):
        l = cv.shape()
        cv.rows(l, ell_rows(x + dx, y + dy, 2, 2), lambda xx, yy: col)
        r = cv.shape(outline=None)
        cv.put(r, x + dx, y + dy, shade(col, 1.4))


def lumber_mill(race):
    st = style(race)
    s = Scene()
    s.add(42, lambda cv: house(cv, st, 7, 42, 15, 7))
    s.add(30, lambda cv: house(cv, st, 40, 30, 11, 6))
    wood = (122, 96, 132) if race == "Night Elves" else (132, 92, 56)      # night elves take only deadwood
    s.add(46, lambda cv: logs(cv, 26, 46, wood))
    def stump(cv):
        t = cv.shape()
        cv.rows(t, ell_rows(50, 44, 3, 1), lambda x, y: (124, 88, 52))
        vline(cv, 52, 38, 43, (110, 80, 50))
        a = cv.shape()
        cv.rect(a, 53, 38, 54, 39, lambda x, y: (178, 182, 192))
    s.add(44, stump)
    s.add(35, lambda cv: prop(cv, st, 31, 35))
    return s.render()


def stall(cv, st, x, y, w=11):
    """A market stall: two posts, a striped awning and a counter with goods."""
    w = odd(w)
    cloth = st.get("roof2") or st["roof"]
    stripe = st.get("trim") or shade(cloth, 1.45)
    vline(cv, x, y - 8, y, (100, 75, 50))
    vline(cv, x + w - 1, y - 8, y, (100, 75, 50))
    c = cv.shape()
    cv.rect(c, x, y - 4, x + w - 1, y - 1, lambda xx, yy: (152, 112, 72) if xx < x + w - 3 else (124, 90, 58))
    g = cv.shape(outline=None)
    cv.put(g, x + 3, y - 5, (222, 82, 62))
    cv.put(g, x + 6, y - 5, (242, 202, 72))
    a = cv.shape()
    cv.rows(a, [(y - 11, x, x + w - 1), (y - 10, x - 1, x + w), (y - 9, x - 1, x + w)],
            lambda xx, yy: stripe if (xx - x) // 2 % 2 else cloth)


def trading_post(race):
    st = style(race)
    s = Scene()
    s.add(22, lambda cv: house(cv, st, 38, 22, 13, 7))
    s.add(26, lambda cv: stall(cv, st, 9, 26))
    s.add(44, lambda cv: stall(cv, st, 29, 44, 13))
    def crates(cv):
        c = cv.shape()
        cv.rect(c, 47, 40, 52, 44, lambda x, y: (150, 110, 70) if x < 51 else (124, 90, 58))
        c2 = cv.shape()
        cv.rect(c2, 49, 36, 53, 39, lambda x, y: (166, 122, 76) if x < 52 else (136, 100, 62))
    s.add(45, crates)
    s.add(44, lambda cv: prop(cv, st, 18, 44))
    return s.render()


def pasture_scene(race):
    """Barn, fences and trough, kept clear of the middle where the herd stands
    (the stock animals of Sheep/Kodo/Horses sit inside x 12..50, y 14..44)."""
    st = style(race)
    s = Scene()
    s.add(13, lambda cv: house(cv, st, 23, 13, 15, 7))
    s.add(30, lambda cv: fence(cv, st, [(51, 16), (57, 28), (53, 44)]))
    s.add(50, lambda cv: fence(cv, st, [(6, 36), (12, 48), (26, 51)]))
    def trough(cv):
        t = cv.shape()
        cv.rect(t, 36, 48, 44, 51, lambda x, y: (122, 86, 52) if x < 42 else (100, 70, 44))
        w = cv.shape(outline=None)
        hline(cv, 37, 43, 48, (110, 160, 210))
    s.add(51, trough)
    s.add(30, lambda cv: house(cv, st, 2, 30, 9, 5))
    s.add(52, lambda cv: prop(cv, st, 50, 52))
    return s


PLOT = [(5, 36), (27, 50), (55, 34), (33, 22)]       # the raised field, as in the stock plantation


def plantation_scene(race, crops=None):
    """A raised, fenced field with the faction's farmhouse at its front corner.
    `crops` (the resource's crop rows cut from the stock combined image) grow on it."""
    st = style(race)
    s = Scene()
    soil = (118, 84, 52) if race not in DEAD else (92, 84, 80)
    def plot(cv):
        bl = cv.shape()
        cv.rows(bl, poly_rows([(5, 36), (27, 50), (27, 53), (5, 39)]), lambda x, y: shade(soil, 0.75))
        br = cv.shape()
        cv.rows(br, poly_rows([(27, 50), (55, 34), (55, 37), (27, 53)]), lambda x, y: shade(soil, 0.6))
        p = cv.shape()
        cv.rows(p, poly_rows(PLOT), lambda x, y: soil)
        if crops is None:
            for k in range(5):
                t = 0.18 + k * 0.16
                ax, ay = 5 + 28 * t, 36 - 14 * t
                thin(cv, line_px(ax, ay, ax + 22, ay + 14), shade(soil, 0.8))
    s.add(0, plot)
    s.add(1, lambda cv: fence(cv, st, [(6, 35), (33, 22), (54, 33)]))
    if crops is not None:
        s.add(30, crops)
    s.add(52, lambda cv: fence(cv, st, [(6, 37), (27, 48), (54, 35)]))
    s.add(53, lambda cv: house(cv, st, 13, 48, 13, 6))
    return s


def quarry_scene(race):
    """Dressed blocks, a hoist in the race's material and a mason's hut,
    laid over the stock rock (Stone, Marble...) that sits under it."""
    st = style(race)
    s = Scene()
    stone = shade(st["stone"], 1.08)
    def cut(cv):
        f = cv.shape()
        cv.rows(f, poly_rows([(18, 24), (36, 14), (46, 20), (28, 30)]), lambda x, y: shade(stone, 0.75))
        t = cv.shape()
        cv.rows(t, poly_rows([(22, 26), (36, 18), (42, 22), (28, 30)]), lambda x, y: stone)
        r = cv.shape()
        cv.rows(r, poly_rows([(28, 30), (42, 22), (42, 26), (28, 34)]), lambda x, y: shade(stone, 0.6))
    s.add(22, cut)
    def hoist(cv):
        mat = st["mat"]
        wood = st["fcol"] if mat in ("palisade", "metal") else (126, 90, 56)
        if mat in ("stone", "saronite", "lacquer"):
            ft = cv.shape()
            cv.rect(ft, 31, 27, 37, 30, lambda x, y: shade(st["fcol"], 1.05) if x < 35 else shade(st["fcol"], 0.85))
        p = cv.shape()
        cv.rect(p, 33, 9, 35, 27, lambda x, y: wood if x < 35 else shade(wood, 0.82))
        b = cv.shape()
        cv.rect(b, 33, 7, 48, 9, lambda x, y: shade(wood, 0.95))
        thin(cv, line_px(36, 16, 42, 10), shade(wood, 0.8))
        vline(cv, 46, 10, 16, (92, 76, 60))
        bk = cv.shape()
        cv.rect(bk, 44, 17, 48, 20, lambda x, y: stone if x < 47 else shade(stone, 0.8))
        CC.banner(cv, 34, 6, 3, wood, st["flag"])
    s.add(27, hoist)
    def blocks(cv):
        for bx, by, k in ((38, 40, 0), (44, 40, 1), (41, 36, 2)):
            b = cv.shape()
            cv.rect(b, bx, by - 3, bx + 5, by, lambda x, y, bx=bx, k=k: shade(stone, 1 - 0.06 * k) if x < bx + 4 else shade(stone, 0.8))
    s.add(40, blocks)
    s.add(42, lambda cv: house(cv, st, 15, 42, 11, 6))
    def tools(cv):
        thin(cv, line_px(30, 43, 33, 38), (110, 80, 50))
        p = cv.shape()
        cv.rect(p, 32, 37, 35, 37, lambda x, y: (176, 180, 190))
    s.add(43, tools)
    return s


def boat(cv, ss, x, y, flip=False):
    """A small race fishing boat whose hull sits on the water at (x, y)."""
    x, y = int(x), int(y)
    d = -1 if flip else 1
    hull, sail, acc = ss["hull"], ss["sail"], ss["acc"]
    h = cv.shape()
    cv.rows(h, [(y - 2, x - 7, x + 7), (y - 1, x - 7, x + 7), (y, x - 6, x + 6), (y + 1, x - 5, x + 5)],
            lambda xx, yy: acc if yy == y - 2 else (hull if yy < y + 1 else shade(hull, 0.8)))
    vline(cv, x, y - 14, y - 3, (96, 70, 46))
    sl = cv.shape()
    rows = []
    for k in range(9):                                   # a triangular sail on the leeward side
        yy = y - 12 + k
        a, b = (x + 1, x + 1 + k * 2 // 3) if d > 0 else (x - 1 - k * 2 // 3, x - 1)
        rows.append((yy, a, b))
    cv.rows(sl, rows, lambda xx, yy: sail)
    thin(cv, line_px(x - 6 * d, y - 3, x - 9 * d, y - 6), (200, 200, 190))
    if ss.get("glow"):
        g = cv.shape(outline=None, glow=ss["glow"])
        cv.put(g, x - 4 * d, y - 4, ss["glow"])


def fishing_boats_scene(race, spots=((30, 26), (45, 40))):
    import race_works as RW
    ss = RW.SHIP_STYLE[race]
    s = Scene()
    for k, (x, y) in enumerate(spots):
        x, y = int(x), int(y)
        def wake(cv, x=x, y=y):
            w = cv.shape(outline=None)
            cv.rows(w, ell_rows(x, y + 3, 9, 1), lambda xx, yy: (122, 190, 216))
            hline(cv, x - 8, x - 3, y + 3, (230, 245, 250))
        s.add(y - 1, wake)
        s.add(y, lambda cv, x=x, y=y, k=k: boat(cv, ss, x, y, flip=bool(k % 2)))
    return s


# ------------------------------------------------------------------ hunting camp
CAMP_SHELTER = {"Humans": "canvas", "Kul Tirans": "canvas", "High Elves": "canvas", "Blood Elves": "canvas",
                "Forsaken": "canvas", "Tauren": "tent"}


def shelter(cv, st, x, foot, w=13, h=6):
    kind = CAMP_SHELTER.get(st["race"], st["small_roof"])
    w = odd(w)
    cx = x + (w - 1) // 2
    if kind == "canvas":                          # a pitched canvas or silk tent
        cloth = {"Blood Elves": st["roof"], "Forsaken": (96, 92, 102)}.get(st["race"], (236, 232, 218))
        t = cv.shape()
        cv.rows(t, tri_rows(cx, foot, (w - 1) // 2, 1), two_tone(cloth, cx))
        d = cv.shape(outline=None)
        cv.rows(d, [(foot - 1, cx - 1, cx + 1), (foot - 2, cx, cx), (foot - 3, cx, cx)], lambda xx, yy: (62, 46, 36))
        trim = st["trim"] if st["race"] != "Forsaken" else None
        if trim:
            rows = tri_rows(cx, foot, (w - 1) // 2, 1)
            for yy, a, b in rows[1:-1]:
                cv.put(d, a + 1, yy, trim)
                cv.put(d, b - 1, yy, trim)
    elif kind == "tent":
        CC.tent(cv, cx, foot, (w - 1) // 2, st["roof"])
    else:
        house(cv, st, x, foot, w, h, kind=kind)


def camp(race):
    st = style(race)
    s = Scene()
    s.add(28, lambda cv: shelter(cv, st, 13, 28))
    hide = (110, 90, 70) if race in DEAD else (176, 126, 80)
    def rack(cv):
        vline(cv, 12, 25, 33, (100, 70, 45))
        h = cv.shape()
        cv.rows(h, ell_rows(9, 27, 4, 5), lambda x, y: (112, 80, 50))
        i = cv.shape(outline=None)
        cv.rows(i, ell_rows(9, 27, 2, 3), lambda x, y: hide if x >= 9 else shade(hide, 1.12))
    s.add(33, rack)
    fire = FIRE.get(race, (255, 150, 50))
    def campfire(cv):
        r = cv.shape()
        cv.rows(r, ell_rows(39, 29, 4, 2), lambda x, y: (122, 116, 110))
        a = cv.shape(outline=None)
        cv.rows(a, ell_rows(39, 29, 2, 1), lambda x, y: (62, 46, 36))
        f = cv.shape(outline=None, glow=fire)
        cv.rows(f, [(28, 38, 40), (27, 38, 40), (26, 39, 39), (25, 39, 39)], lambda x, y: fire)
        cv.put(f, 39, 28, (255, 245, 200))
    s.add(30, campfire)
    s.add(28, lambda cv: prop(cv, st, 50, 28))
    return s.render()


# ------------------------------------------------------------------ fort
def fort(race):
    """A walled outpost: back wall, side walls, keep and barracks, front wall with a
    gate and corner towers, in the race's wall material and roof shapes."""
    st = style(race)
    s = Scene()
    heavy = race in ("Dwarves", "Dark Iron Dwarves")
    h = 7 if heavy else 6
    x0, w = 9, 47                                  # walls span x 9..55, centred on column 32
    tower_kind = st["tower_roof"] if st["tower_roof"] != "pagoda" else "hip"
    tcol = st["fcol"] if st["mat"] != "lacquer" else st["wall"]
    s.add(18, lambda cv: wall(cv, st, x0, 18, w, h - 1))
    for tx in (x0 - 2, CC.mirror_x(x0 - 2, 5)):    # back corner towers
        s.add(19, lambda cv, tx=tx: CC.tower(cv, tx, 19, 5, 10, tcol, st["roof"], kind=tower_kind, trim=st["trim"]))
    s.add(20, lambda cv: (side_wall(cv, st, x0, 18, 46, h - 1), side_wall(cv, st, x0 + w - 5, 18, 46, h - 1)))
    s.add(34, lambda cv: CC.tower(cv, 28, 34, 9, 14, st["wall"], st["roof"], kind=tower_kind, trim=st["trim"], win=st["win"]))
    s.add(38, lambda cv: house(cv, st, 14, 38, 11, 5, kind=st["small_roof"]))
    s.add(37, lambda cv: CC.banner(cv, 44, 37, 12, (80, 70, 60), st["flag"]))
    if st["lamp"]:
        def l(cv):
            g = cv.shape(outline=None, glow=st["lamp"])
            cv.put(g, 40, 35, st["lamp"])
        s.add(39, l)
    s.add(47, lambda cv: wall(cv, st, x0, 47, w, h, gate=True))
    for tx in (x0 - 3, CC.mirror_x(x0 - 3, 7)):    # front corner towers
        s.add(48, lambda cv, tx=tx: CC.tower(cv, tx, 48, 7, 12, tcol, st["roof"], kind=tower_kind, trim=st["trim"]))
    return s.render()
