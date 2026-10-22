"""The previous city-center renderer, kept for the camps, forts, ships and race
improvements (race_works.py, race_improvements.py), which are drawn with its
house/tower/banner pieces and its STYLES. City centers themselves now come from
citycenters.py.

Original description: city-center tiles for every race, in its own architecture and colours.

Unciv looks for "City center-<civ>-<era>" first (falling back to earlier eras), so each
race gets three growth stages: a village (Age of Tribes), a town (Age of the Dark
Portal) and a walled city (Age of the Cataclysm). City-states borrow the style that
fits them (Gadgetzan is goblin, Cenarion Hold night elf, Dalaran violet), and the plain
"City center-<era>" images are replaced with a Warcraft-style stone town so no city
ever shows Unciv's modern skyscrapers.

Buildings are drawn as 3/4-view pixel art (front wall + roof) with mounts.Paint, each
outlined on its own layer and composited back to front, in HexaRealm's 64-px style.
"""
import math, os, random
from PIL import Image, ImageFilter
from mounts import Paint, shade

W, H = 64, 72                 # taller than a tile so towers can rise above it
OY = H - 56                   # the hex face starts this far down the canvas
STAGES = [("Age of Tribes", 0), ("Age of the Dark Portal", 1), ("Age of the Cataclysm", 2)]
ERA_STAGE = {"Age of Tribes": 0, "Age of Arathor": 0, "Age of the Dark Portal": 1, "Age of the Third War": 1,
             "Age of the Lich King": 1, "Age of the Cataclysm": 2, "Age of the Legion": 2,
             "Age of Azerite": 2, "Age of the Void": 2}


# ------------------------------------------------------------------ building blocks
def outlined(p, color=(30, 24, 22)):
    return p.render(color)[0]


def glow_of(im, color, radius=1.2, strength=1.2):
    m = im.split()[3].filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(radius))
    m = m.point(lambda v: min(255, int(v * strength)))
    g = Image.new("RGBA", im.size, tuple(color) + (0,))
    g.putalpha(m)
    return g


class Scene:
    """Collects drawable pieces with a depth (their base y) and composites them."""

    def __init__(self):
        self.items = []          # (depth, image)

    def add(self, depth, im):
        self.items.append((depth, im))

    def piece(self, depth, fn, outline=(30, 24, 22), glow=None):
        p = Paint(W, H)
        fn(p)
        im = outlined(p, outline) if outline else p.render(None)[0]
        if glow:
            g = Image.new("RGBA", (W, H))
            g.alpha_composite(glow_of(im, glow))
            g.alpha_composite(im)
            im = g
        self.add(depth, im)

    def render(self):
        out = Image.new("RGBA", (W, H))
        for _, im in sorted(self.items, key=lambda t: t[0]):
            out.alpha_composite(im)
        return out


def windows(p, x, y, w, h, col, every=3, part="win"):
    for wx in range(int(x + 2), int(x + w - 1), every):
        p.dot(wx, y - h * 0.55, col, part)


def door(p, x, y, w, col=(60, 40, 30)):
    cx = x + w / 2
    p.line(cx, y - 1, cx, y - 3, 2, col, "door")


def house(p, x, y, w, h, wall, roof, kind="gable", rh=None, win=None, trim=None):
    """A building whose front wall spans x..x+w with its foot at y."""
    rh = rh if rh is not None else w * 0.55
    if kind not in ("cone", "tent"):
        p.poly([(x, y), (x + w, y), (x + w, y - h), (x, y - h)], wall, "wall")
        p.poly([(x + w * 0.62, y), (x + w, y), (x + w, y - h), (x + w * 0.62, y - h)], shade(wall, 0.82), "wallR")
    top = y - h
    if kind == "gable":
        p.poly([(x - 1.5, top), (x + w + 1.5, top), (x + w / 2, top - rh)], roof, "roof")
        p.poly([(x + w / 2, top - rh), (x + w + 1.5, top), (x + w / 2, top)], shade(roof, 0.8), "roofR")
    elif kind == "hip":
        p.poly([(x - 1.5, top), (x + w + 1.5, top), (x + w * 0.75, top - rh), (x + w * 0.25, top - rh)], roof, "roof")
        p.poly([(x + w * 0.75, top - rh), (x + w + 1.5, top), (x + w * 0.55, top)], shade(roof, 0.8), "roofR")
    elif kind == "spire":
        p.poly([(x - 1, top), (x + w + 1, top), (x + w / 2, top - rh * 2.2)], roof, "roof")
        p.poly([(x + w / 2, top - rh * 2.2), (x + w + 1, top), (x + w / 2, top)], shade(roof, 0.8), "roofR")
    elif kind == "dome":
        p.ell(x + w / 2, top, w / 2 + 0.5, rh * 0.8, roof, "roof")
        p.ell(x + w * 0.65, top - rh * 0.2, w * 0.18, rh * 0.45, shade(roof, 1.2), "roofH")
    elif kind == "flat":
        p.poly([(x - 1, top), (x + w + 1, top), (x + w + 1, top - 2), (x - 1, top - 2)], roof, "roof")
        for bx in range(int(x - 1), int(x + w + 1), 3):
            p.poly([(bx, top - 2), (bx + 1.5, top - 2), (bx + 1.5, top - 4), (bx, top - 4)], roof, "roof")
    elif kind == "cone":                                 # hut / tent: no wall
        p.poly([(x - 1, y), (x + w + 1, y), (x + w / 2, y - h - rh)], roof, "roof")
        p.poly([(x + w / 2, y - h - rh), (x + w + 1, y), (x + w / 2, y)], shade(roof, 0.8), "roofR")
    elif kind == "tent":                                 # tauren tent: painted band, crossed poles
        apex = y - h - rh
        p.poly([(x - 1, y), (x + w + 1, y), (x + w / 2, apex)], roof, "roof")
        p.poly([(x + w / 2, apex), (x + w + 1, y), (x + w / 2, y)], shade(roof, 0.8), "roofR")
        by = y - (h + rh) * 0.4
        half = (w / 2 + 1) * 0.6
        p.line(x + w / 2 - half, by, x + w / 2 + half, by, 1, (190, 60, 40), "band")
        p.line(x + w / 2 - half + 1, by + 1, x + w / 2 + half - 1, by + 1, 1, (60, 120, 170), "band")
        p.line(x + w / 2 - 1, apex, x + w / 2 - 3, apex - 3, 1, (110, 80, 50), "pole")
        p.line(x + w / 2 + 1, apex, x + w / 2 + 3, apex - 3, 1, (110, 80, 50), "pole")
        p.line(x + w / 2, y - 1, x + w / 2, y - 3, 2, (70, 45, 30), "door")
    elif kind == "thatch":                               # troll hut: low wall, tall shaggy cone
        p.poly([(x - 2.5, top + 1), (x + w + 2.5, top + 1), (x + w / 2, top - rh * 1.4)], roof, "roof")
        p.poly([(x + w / 2, top - rh * 1.4), (x + w + 2.5, top + 1), (x + w / 2, top + 1)], shade(roof, 0.8), "roofR")
        for k in range(int(x - 1), int(x + w + 2), 2):
            p.dot(k, top + 1, shade(roof, 0.7), "fringe")
        p.ell(x + w / 2, top - rh * 0.6, 1.2, 1, (240, 230, 210), "mask")
    elif kind == "pagoda":
        for k in range(3):
            ty = top - k * (rh * 0.55)
            ww = w + 4 - k * 3
            cx = x + w / 2
            p.poly([(cx - ww / 2 - 1, ty), (cx + ww / 2 + 1, ty), (cx + ww / 2 - 1, ty - 2), (cx - ww / 2 + 1, ty - 2)],
                   roof, "roof%d" % k)
            p.dot(cx - ww / 2 - 1, ty - 1, roof, "roof%d" % k)
            p.dot(cx + ww / 2 + 1, ty - 1, roof, "roof%d" % k)
            if k < 2:
                p.poly([(cx - ww / 2 + 2, ty - 2), (cx + ww / 2 - 2, ty - 2), (cx + ww / 2 - 2, ty - rh * 0.55),
                        (cx - ww / 2 + 2, ty - rh * 0.55)], wall, "pw%d" % k)
    elif kind == "spiky":
        p.poly([(x - 1.5, top), (x + w + 1.5, top), (x + w / 2, top - rh)], roof, "roof")
        p.poly([(x + w / 2, top - rh), (x + w + 1.5, top), (x + w / 2, top)], shade(roof, 0.8), "roofR")
        for sx in (x + 1, x + w / 2, x + w - 1):
            p.line(sx, top - (rh if sx == x + w / 2 else rh * 0.45), sx + (0 if sx == x + w / 2 else (sx - x - w / 2) * 0.4),
                   top - (rh if sx == x + w / 2 else rh * 0.45) - 3, 1, (55, 50, 50), "spike")
    elif kind == "leaf":                                  # night elf curved roof
        p.ell(x + w / 2, top - rh * 0.3, w / 2 + 2, rh * 0.6, roof, "roof")
        p.line(x - 2, top + 0.5, x + 1, top - rh * 0.4, 1, roof, "roof")
        p.line(x + w + 2, top + 0.5, x + w - 1, top - rh * 0.4, 1, roof, "roof")
        p.dot(x + w / 2, top - rh * 0.95, shade(roof, 1.3), "roof")
    if trim:
        p.line(x, top, x + w, top, 1, trim, "trim")
    if win:
        windows(p, x, y, w, h, win)
    if kind not in ("cone", "tent"):
        door(p, x, y, w)


def tower(p, x, y, w, h, wall, roof, kind="spire", rh=None, win=None, trim=None):
    house(p, x, y, w, h, wall, roof, kind=kind, rh=rh if rh is not None else w * 0.8, win=None, trim=trim)
    if win:
        for wy in range(int(y - h + 3), int(y - 3), 4):
            p.dot(x + w / 2, wy, win, "twin")


def city_wall(s, st, stone, cap, stage, gate=(60, 40, 30)):
    """A wall across the front of the hex with a gate and end towers."""
    y = OY + 50
    def wall(p):
        p.poly([(8, y), (56, y), (56, y - 6), (8, y - 6)], stone, "cw")
        p.poly([(36, y), (56, y), (56, y - 6), (36, y - 6)], shade(stone, 0.85), "cwR")
        for bx in range(8, 56, 3):
            p.poly([(bx, y - 6), (bx + 1.5, y - 6), (bx + 1.5, y - 8), (bx, y - 8)], stone, "cren")
        p.poly([(29, y), (35, y), (35, y - 5), (32, y - 6.5), (29, y - 5)], gate, "gate")
    s.piece(y + 1, wall)
    for tx in (5, 52):
        s.piece(y + 2, lambda p, tx=tx: tower(p, tx, y + 1, 7, 12, stone, cap, kind=st.get("tower_roof", "spire"),
                                               rh=5, trim=st.get("trim")))


def plaza(s, col, rx=24, ry=13):
    def f(p):
        p.ell(32, OY + 30, rx, ry, col, "plaza")
        p.ell(32, OY + 30, rx - 3, ry - 2.5, shade(col, 1.08), "plaza2")
    s.piece(-100, f, outline=None)


def banner(p, x, y, pole, cloth, h=8):
    p.line(x, y, x, y - h, 1, pole, "pole")
    p.poly([(x + 1, y - h), (x + 5, y - h + 1), (x + 4, y - h + 3), (x + 5, y - h + 5), (x + 1, y - h + 4)], cloth, "flag")


# ------------------------------------------------------------------ styles
def S(**kw):
    base = dict(wall=(200, 195, 180), wall2=None, roof=(150, 60, 40), roof2=None, trim=None,
                win=(255, 220, 120), ground=(150, 140, 120), stone=(165, 160, 150), house="gable",
                big="hip", tower_roof="spire", banner=None, extras=None, landmark=None)
    base.update(kw)
    return base


# --- race extras and landmarks: small functions that add pieces to the scene
def e_orc(s, st, stage, rng):
    for x in (10, 52) if stage else (12,):
        s.piece(OY + 44, lambda p, x=x: [p.line(x + i * 2, OY + 46, x + i * 2, OY + 40, 1, (110, 80, 50), "stake")
                                          for i in range(4)])
    if stage >= 1:
        s.piece(OY + 22, lambda p: banner(p, 32, OY + 16, (60, 50, 45), (170, 30, 25), 12))


def lm_orc(s, st, rng):                                    # Grommash Hold: great spiked hall
    s.piece(OY + 26, lambda p: house(p, 18, OY + 26, 28, 12, (120, 75, 45), (70, 62, 60), kind="spiky", rh=12,
                                     win=(255, 140, 50)))


def e_human(s, st, stage, rng):
    if stage >= 1:
        s.piece(OY + 20, lambda p: banner(p, 46, OY + 16, (90, 80, 70), (30, 60, 150), 10))


def lm_human(s, st, rng):                                  # cathedral with tall spires
    def f(p):
        house(p, 22, OY + 24, 20, 12, (225, 222, 210), (40, 70, 160), kind="gable", rh=9, trim=(235, 195, 70))
        tower(p, 18, OY + 24, 6, 18, (230, 228, 218), (40, 70, 160), rh=6)
        tower(p, 40, OY + 24, 6, 18, (230, 228, 218), (40, 70, 160), rh=6)
        p.ell(32, OY + 15, 2, 2, (250, 220, 120), "rose")
    s.piece(OY + 24, f)


def e_nelf(s, st, stage, rng):
    def well(p):
        p.ell(32, OY + 38, 6, 3, (180, 180, 200), "rim")
        p.ell(32, OY + 38, 4.5, 2, (150, 210, 255), "water")
    s.piece(OY + 38, well, glow=(170, 220, 255))
    for x, y in ((10, OY + 30), (54, OY + 28)):
        def tr(p, x=x, y=y):
            p.line(x, y, x, y - 8, 2, (90, 70, 90), "trunk")
            p.ell(x, y - 11, 6, 4, (110, 80, 170), "leaf")
            p.ell(x - 2, y - 13, 3, 2, (140, 110, 200), "leafh")
        s.piece(y, tr, outline=(40, 30, 55))


def lm_nelf(s, st, rng):                                   # temple under a great tree
    def f(p):
        p.poly([(29, OY + 24), (35, OY + 24), (34, OY + 6), (30, OY + 6)], (110, 85, 110), "trunk")
        p.ell(32, OY + 4, 16, 6, (100, 75, 160), "canopy")
        p.ell(26, OY + 2, 6, 3, (135, 105, 190), "canopyh")
        house(p, 22, OY + 28, 20, 7, (215, 215, 235), (110, 80, 170), kind="leaf", rh=7)
    s.piece(OY + 28, f, outline=(40, 30, 55))


def e_dwarf(s, st, stage, rng):
    def forge(p):
        p.ell(49, OY + 40, 3, 2, (255, 150, 40), "fire")
        p.poly([(45, OY + 38), (53, OY + 38), (52, OY + 34), (46, OY + 34)], (90, 85, 85), "anvilbase")
    s.piece(OY + 40, forge, glow=(255, 130, 40))


def lm_dwarf(s, st, rng):                                  # the great forge gate in the mountain
    def f(p):
        p.poly([(10, OY + 28), (54, OY + 28), (44, OY + 2), (32, OY - 6), (20, OY + 2)], (120, 110, 105), "mtn")
        p.poly([(32, OY - 6), (44, OY + 2), (54, OY + 28), (32, OY + 28)], (95, 88, 85), "mtnR")
        p.poly([(24, OY + 28), (40, OY + 28), (40, OY + 14), (32, OY + 9), (24, OY + 14)], (170, 150, 120), "gateframe")
        p.poly([(27, OY + 28), (37, OY + 28), (37, OY + 16), (32, OY + 13), (27, OY + 16)], (255, 150, 50), "gatefire")
    s.piece(OY + 28, f, glow=None)


def e_gnome(s, st, stage, rng):
    def gear(p, x=50, y=OY + 34, r=4):
        p.ell(x, y, r, r, (200, 170, 80), "gear")
        p.ell(x, y, r * 0.4, r * 0.4, (90, 80, 70), "hub")
        for k in range(8):
            a = k * math.pi / 4
            p.dot(x + math.cos(a) * (r + 1), y + math.sin(a) * (r + 1), (200, 170, 80), "gear")
    s.piece(OY + 34, gear)
    def pipe(p):
        p.line(8, OY + 36, 20, OY + 36, 2, (150, 160, 170), "pipe")
        p.line(20, OY + 36, 20, OY + 26, 2, (150, 160, 170), "pipe")
    s.piece(OY + 37, pipe)


def lm_gnome(s, st, rng):                                  # great dome with a cog tower
    def f(p):
        house(p, 18, OY + 26, 28, 9, (150, 165, 175), (110, 190, 190), kind="dome", rh=12)
        p.line(45, OY + 26, 45, OY + 6, 3, (120, 130, 140), "stack")
        p.ell(45, OY + 4, 3, 2, (230, 230, 230), "steam")
        p.ell(42, OY + 1, 3, 2, (240, 240, 240), "steam2")
        p.ell(32, OY + 9, 3, 3, (250, 207, 231), "lamp")
    s.piece(OY + 26, f)


def e_tauren(s, st, stage, rng):
    for x in ((48,) if stage == 0 else (48, 14)):
        def totem(p, x=x):
            for k, c in enumerate(((200, 60, 40), (240, 200, 70), (60, 120, 170))):
                p.poly([(x - 1.5, OY + 40 - k * 3), (x + 1.5, OY + 40 - k * 3), (x + 1.5, OY + 37 - k * 3),
                        (x - 1.5, OY + 37 - k * 3)], c, "tot%d" % k)
            p.line(x - 3, OY + 31, x + 3, OY + 31, 1, (240, 200, 70), "wing")
        s.piece(OY + 40, totem)


def lm_tauren(s, st, rng):                                 # a mesa with a great tent and lift
    def f(p):
        p.poly([(8, OY + 30), (56, OY + 30), (52, OY + 14), (12, OY + 14)], (175, 115, 70), "mesa")
        p.poly([(32, OY + 14), (52, OY + 14), (56, OY + 30), (32, OY + 30)], (150, 95, 55), "mesaR")
        house(p, 22, OY + 14, 20, 3, (190, 140, 90), (200, 160, 110), kind="tent", rh=14)
    s.piece(OY + 30, f)


def e_troll(s, st, stage, rng):
    def torch(p, x):
        p.line(x, OY + 40, x, OY + 34, 1, (110, 80, 50), "pole")
        p.ell(x, OY + 33, 1.2, 1.5, (255, 170, 60), "flame")
    s.piece(OY + 40, lambda p: (torch(p, 14), torch(p, 50)), glow=(255, 150, 50))


def lm_troll(s, st, rng):                                  # stepped stone ziggurat
    def f(p):
        for k, (w, h) in enumerate(((30, 5), (23, 5), (16, 5), (9, 5))):
            y = OY + 30 - k * 5
            p.poly([(32 - w / 2, y), (32 + w / 2, y), (32 + w / 2 - 2, y - h), (32 - w / 2 + 2, y - h)],
                   shade((150, 160, 130), 1 - k * 0.05), "tier%d" % k)
        p.line(32, OY + 30, 32, OY + 12, 2, (100, 105, 90), "stairs")
        p.ell(32, OY + 8, 2.5, 2, (240, 230, 210), "mask")
        p.dot(31, OY + 8, (30, 30, 30), "mask"); p.dot(33, OY + 8, (30, 30, 30), "mask")
    s.piece(OY + 30, f)


def e_belf(s, st, stage, rng):
    if stage >= 1:
        s.piece(OY + 18, lambda p: banner(p, 14, OY + 18, (220, 180, 70), (170, 25, 35), 10))


def lm_belf(s, st, rng):                                   # Sunfury spire with floating gold rings
    def f(p):
        tower(p, 28, OY + 28, 8, 22, (240, 230, 215), (180, 30, 40), rh=8, trim=(240, 200, 70))
        tower(p, 18, OY + 28, 5, 13, (240, 230, 215), (180, 30, 40), rh=5)
        tower(p, 41, OY + 28, 5, 13, (240, 230, 215), (180, 30, 40), rh=5)
        p.dot(32, OY - 12, (250, 220, 90), "orb")
    s.piece(OY + 28, f, glow=None)
    def rings(p):
        for k in range(16):
            a = k / 16 * math.tau
            p.dot(32 + math.cos(a) * 7, OY + 2 + math.sin(a) * 2, (250, 215, 90), "ring")
    s.piece(OY + 29, rings, outline=None, glow=(255, 220, 120))


def e_helf(s, st, stage, rng):
    if stage >= 1:
        s.piece(OY + 18, lambda p: banner(p, 50, OY + 18, (200, 200, 210), (40, 90, 190), 10))


def lm_helf(s, st, rng):                                   # white spires with blue caps, a sunwell font
    def f(p):
        for x, h in ((20, 14), (28, 22), (37, 18), (45, 12)):
            tower(p, x, OY + 28, 6, h, (240, 240, 245), (50, 100, 200), rh=6, trim=(220, 200, 120))
    s.piece(OY + 28, f)
    def font(p):
        p.ell(32, OY + 34, 4, 2, (250, 230, 130), "font")
    s.piece(OY + 34, font, outline=None, glow=(255, 240, 150))


def e_panda(s, st, stage, rng):
    def lantern(p, x, y):
        p.line(x, y, x, y - 5, 1, (90, 60, 40), "post")
        p.ell(x, y - 6, 1.5, 1.5, (240, 80, 50), "lantern")
    s.piece(OY + 42, lambda p: (lantern(p, 12, OY + 42), lantern(p, 52, OY + 42)), glow=(255, 150, 80))


def lm_panda(s, st, rng):                                  # a tall pagoda
    def f(p):
        cx, y = 32, OY + 30
        for k in range(4):
            w = 22 - k * 4
            p.poly([(cx - w / 2 + 2, y - k * 6), (cx + w / 2 - 2, y - k * 6), (cx + w / 2 - 2, y - k * 6 - 4),
                    (cx - w / 2 + 2, y - k * 6 - 4)], (180, 50, 40), "floor%d" % k)
            p.poly([(cx - w / 2 - 1, y - k * 6 - 4), (cx + w / 2 + 1, y - k * 6 - 4), (cx + w / 2 - 1, y - k * 6 - 6.5),
                    (cx - w / 2 + 1, y - k * 6 - 6.5)], (40, 130, 110), "eave%d" % k)
            p.dot(cx - w / 2 - 2, y - k * 6 - 5, (40, 130, 110), "eave%d" % k)
            p.dot(cx + w / 2 + 2, y - k * 6 - 5, (40, 130, 110), "eave%d" % k)
        p.line(cx, y - 24, cx, y - 30, 1, (230, 190, 70), "finial")
    s.piece(OY + 30, f)


def e_forsaken(s, st, stage, rng):
    def cauldron(p):
        p.ell(48, OY + 40, 3.5, 2.5, (60, 60, 65), "pot")
        p.ell(48, OY + 38, 2.5, 1, (140, 230, 80), "brew")
    s.piece(OY + 40, cauldron, glow=(140, 230, 80))
    if stage >= 1:
        s.piece(OY + 18, lambda p: banner(p, 14, OY + 18, (70, 65, 70), (90, 40, 110), 10))


def lm_forsaken(s, st, rng):                               # the ruined royal keep of Lordaeron
    def f(p):
        stone = (95, 95, 105)
        p.poly([(18, OY + 28), (46, OY + 28), (46, OY + 12), (18, OY + 12)], stone, "keep")
        p.poly([(36, OY + 28), (46, OY + 28), (46, OY + 12), (36, OY + 12)], shade(stone, 0.8), "keepR")
        p.poly([(14, OY + 28), (21, OY + 28), (21, OY + 2), (17, OY - 1), (14, OY + 3)], stone, "tl")   # broken top
        p.poly([(43, OY + 28), (50, OY + 28), (50, OY + 6), (43, OY + 4)], stone, "tr")
        for bx in range(18, 46, 3):
            p.poly([(bx, OY + 12), (bx + 1.5, OY + 12), (bx + 1.5, OY + 10), (bx, OY + 10)], stone, "cren")
        for wx, wy in ((24, OY + 18), (30, OY + 18), (40, OY + 18), (17, OY + 10), (46, OY + 14)):
            p.dot(wx, wy, (150, 230, 90), "win")
    s.piece(OY + 28, f)


def e_scourge(s, st, stage, rng):
    def obelisk(p, x):
        p.poly([(x - 2, OY + 40), (x + 2, OY + 40), (x + 1, OY + 31), (x, OY + 28), (x - 1, OY + 31)], (55, 65, 85), "ob%d" % x)
        p.dot(x, OY + 33, (150, 220, 255), "obg%d" % x)
    s.piece(OY + 40, lambda p: (obelisk(p, 13), obelisk(p, 51)), glow=(120, 200, 255))
    if stage >= 1:
        s.piece(OY + 18, lambda p: banner(p, 14, OY + 18, (40, 50, 70), (130, 200, 245), 10))


def lm_scourge(s, st, rng):                                # a saronite spire and ziggurat
    def f(p):
        dark = (50, 58, 75)
        for k, (w, h) in enumerate(((26, 4), (20, 4), (14, 4))):
            y = OY + 30 - k * 4
            p.poly([(32 - w / 2, y), (32 + w / 2, y), (32 + w / 2 - 2, y - h), (32 - w / 2 + 2, y - h)],
                   shade(dark, 1 - k * 0.06), "zig%d" % k)
        p.poly([(28, OY + 18), (36, OY + 18), (34, OY + 2), (32, OY - 6), (30, OY + 2)], (65, 75, 95), "spire")
        for dx in (-5, 5):
            p.poly([(32 + dx - 1, OY + 18), (32 + dx + 1, OY + 18), (32 + dx * 1.6, OY + 6)], (75, 85, 105), "spur%d" % dx)
        p.dot(32, OY + 6, (160, 230, 255), "throne")
        p.dot(32, OY + 7, (160, 230, 255), "throne")
    s.piece(OY + 30, f, glow=(120, 200, 255))


def e_draenei(s, st, stage, rng):
    def crystal(p, x, y, h):
        p.poly([(x, y - h), (x + 2, y - h * 0.5), (x + 1.2, y), (x - 1.2, y), (x - 2, y - h * 0.5)], (150, 200, 255), "cr")
    s.piece(OY + 40, lambda p: (crystal(p, 12, OY + 40, 8), crystal(p, 52, OY + 40, 7)), glow=(150, 200, 255))


def lm_draenei(s, st, rng):                                # crystal-crowned spire of the Exodar
    def f(p):
        p.poly([(22, OY + 28), (42, OY + 28), (38, OY + 10), (32, OY + 4), (26, OY + 10)], (150, 135, 190), "hull")
        p.poly([(32, OY + 4), (38, OY + 10), (42, OY + 28), (32, OY + 28)], (120, 105, 160), "hullR")
        for x, h in ((26, 14), (32, 22), (38, 14)):
            p.poly([(x, OY + 4 - h), (x + 2.5, OY + 4 - h * 0.45), (x + 1.5, OY + 6), (x - 1.5, OY + 6),
                    (x - 2.5, OY + 4 - h * 0.45)], (160, 210, 255), "crys%d" % x)
    s.piece(OY + 28, f, glow=(160, 200, 255))


def e_goblin(s, st, stage, rng):
    def crane(p):
        p.line(50, OY + 42, 50, OY + 22, 1, (200, 150, 40), "crane")
        p.line(50, OY + 22, 40, OY + 24, 1, (200, 150, 40), "boom")
        p.line(41, OY + 24, 41, OY + 30, 1, (80, 80, 80), "hook")
    s.piece(OY + 42, crane)


def lm_goblin(s, st, rng):                                 # a trade-prince's bank with a gold sign
    def f(p):
        house(p, 18, OY + 26, 28, 14, (150, 110, 70), (190, 90, 40), kind="flat", win=(255, 220, 110))
        p.line(22, OY + 12, 22, OY + 2, 2, (110, 110, 110), "stack")
        p.line(40, OY + 12, 40, OY + 4, 2, (110, 110, 110), "stack")
        p.ell(22, OY, 2.5, 2, (180, 180, 180), "smoke")
        p.ell(32, OY + 7, 4, 4, (250, 210, 40), "coin")
        p.ell(32, OY + 7, 2, 2, (220, 170, 20), "coin2")
    s.piece(OY + 26, f)


def e_worgen(s, st, stage, rng):
    def lamp(p, x):
        p.line(x, OY + 42, x, OY + 33, 1, (40, 40, 45), "post")
        p.ell(x, OY + 32, 1.3, 1.3, (255, 220, 120), "lamp")
    s.piece(OY + 42, lambda p: (lamp(p, 13), lamp(p, 51)), glow=(255, 210, 120))


def lm_worgen(s, st, rng):                                 # Greymane manor with a clock tower
    def f(p):
        house(p, 16, OY + 26, 24, 12, (130, 125, 120), (55, 60, 70), kind="gable", rh=9, win=(255, 210, 120))
        tower(p, 40, OY + 26, 8, 22, (120, 115, 112), (55, 60, 70), rh=7)
        p.ell(44, OY + 10, 2, 2, (240, 230, 200), "clock")
        p.line(22, OY + 10, 22, OY + 4, 2, (80, 70, 65), "chimney")
    s.piece(OY + 26, f)


def e_cs(s, st, stage, rng):
    pass


def lm_cs(s, st, rng):                                     # a stone keep
    def f(p):
        house(p, 20, OY + 26, 24, 14, (170, 165, 155), (150, 70, 45), kind="flat")
        tower(p, 28, OY + 14, 8, 10, (175, 170, 160), (150, 70, 45), rh=6)
    s.piece(OY + 26, f)


def lm_dalaran(s, st, rng):                                # the Violet Citadel
    def f(p):
        for x, h in ((18, 12), (27, 24), (38, 18), (46, 10)):
            tower(p, x, OY + 28, 7 if x == 27 else 6, h, (225, 220, 235), (120, 70, 190), rh=6, trim=(230, 200, 90))
    s.piece(OY + 28, f, glow=None)


STYLES = {
    "Humans": S(wall=(225, 220, 205), roof=(40, 70, 160), trim=(235, 195, 70), ground=(170, 165, 150),
                stone=(200, 198, 190), house="gable", big="hip", extras=e_human, landmark=lm_human),
    "Orcs": S(wall=(125, 80, 50), roof=(150, 50, 35), roof2=(70, 62, 60), ground=(150, 100, 70), stone=(110, 75, 50),
              house="spiky", big="spiky", tower_roof="spiky", win=(255, 140, 50), extras=e_orc, landmark=lm_orc),
    "Night Elves": S(wall=(215, 215, 235), roof=(110, 80, 170), roof2=(70, 130, 150), ground=(120, 150, 110),
                     stone=(190, 190, 215), house="leaf", big="leaf", tower_roof="leaf", win=(170, 230, 255),
                     extras=e_nelf, landmark=lm_nelf),
    "Dwarves": S(wall=(150, 140, 130), roof=(100, 95, 92), trim=(200, 150, 60), ground=(140, 130, 120),
                 stone=(130, 122, 115), house="flat", big="flat", tower_roof="flat", win=(255, 160, 60),
                 extras=e_dwarf, landmark=lm_dwarf),
    "Gnomes": S(wall=(160, 170, 180), roof=(60, 150, 150), roof2=(240, 160, 200), ground=(140, 145, 150),
                stone=(150, 155, 165), house="dome", big="dome", tower_roof="dome", win=(250, 207, 231),
                extras=e_gnome, landmark=lm_gnome),
    "Tauren": S(wall=(190, 140, 90), roof=(185, 140, 95), roof2=(200, 160, 110), ground=(170, 130, 85),
                stone=(160, 110, 70), house="tent", big="tent", tower_roof="tent", extras=e_tauren, landmark=lm_tauren),
    "Trolls": S(wall=(150, 120, 80), roof=(190, 165, 90), roof2=(150, 130, 70), ground=(150, 130, 90),
                stone=(150, 160, 130), house="thatch", big="thatch", tower_roof="thatch", extras=e_troll, landmark=lm_troll),
    "Blood Elves": S(wall=(240, 230, 215), roof=(180, 30, 40), trim=(240, 200, 70), ground=(200, 170, 120),
                     stone=(230, 220, 200), house="spire", big="hip", win=(255, 220, 120), extras=e_belf, landmark=lm_belf),
    "High Elves": S(wall=(240, 240, 245), roof=(50, 100, 200), trim=(220, 200, 120), ground=(170, 180, 170),
                    stone=(225, 225, 230), house="spire", big="hip", extras=e_helf, landmark=lm_helf),
    "Pandaren": S(wall=(180, 50, 40), roof=(40, 130, 110), ground=(160, 150, 120), stone=(170, 160, 140),
                  house="pagoda", big="pagoda", tower_roof="pagoda", extras=e_panda, landmark=lm_panda),
    "Forsaken": S(wall=(100, 100, 108), roof=(60, 55, 70), trim=(120, 60, 140), ground=(105, 100, 105),
                  stone=(95, 95, 105), house="gable", big="spire", win=(150, 230, 90), extras=e_forsaken, landmark=lm_forsaken),
    "Scourge": S(wall=(80, 90, 110), roof=(45, 55, 75), trim=(130, 200, 245), ground=(185, 195, 210),
                 stone=(80, 90, 105), house="spiky", big="spire", win=(150, 220, 255), extras=e_scourge, landmark=lm_scourge),
    "Draenei": S(wall=(160, 145, 200), roof=(110, 90, 170), trim=(160, 210, 255), ground=(150, 145, 175),
                 stone=(150, 140, 185), house="dome", big="spire", win=(170, 220, 255), extras=e_draenei, landmark=lm_draenei),
    "Goblins": S(wall=(150, 110, 70), roof=(190, 90, 40), roof2=(130, 135, 140), ground=(140, 120, 90),
                 stone=(130, 110, 80), house="flat", big="gable", tower_roof="flat", win=(255, 220, 110),
                 extras=e_goblin, landmark=lm_goblin),
    "Worgen": S(wall=(130, 125, 120), roof=(55, 60, 70), trim=(120, 40, 40), ground=(120, 118, 115),
                stone=(115, 112, 110), house="gable", big="gable", win=(255, 210, 120), extras=e_worgen, landmark=lm_worgen),
    "Dark Iron Dwarves": S(wall=(70, 62, 62), roof=(45, 40, 42), trim=(255, 120, 30), ground=(95, 80, 75),
                           stone=(75, 66, 66), house="flat", big="flat", tower_roof="flat", win=(255, 120, 40),
                           extras=e_dwarf, landmark=lm_dwarf),
    "Kul Tirans": S(wall=(215, 210, 195), roof=(30, 70, 95), trim=(230, 220, 190), ground=(165, 160, 145),
                    stone=(185, 182, 172), house="gable", big="hip", win=(255, 225, 140), extras=e_human, landmark=lm_human),
    "Zandalari Trolls": S(wall=(190, 170, 120), roof=(240, 195, 60), roof2=(40, 120, 100), ground=(160, 140, 95),
                          stone=(205, 185, 130), house="thatch", big="thatch", tower_roof="thatch", win=(255, 220, 110),
                          extras=e_troll, landmark=lm_troll),
    "_cs": S(wall=(200, 190, 170), roof=(150, 70, 45), ground=(150, 140, 120), stone=(165, 160, 150),
             house="gable", big="hip", extras=e_cs, landmark=lm_cs),
}
STYLES["_dalaran"] = dict(STYLES["Humans"], roof=(120, 70, 190), landmark=lm_dalaran, extras=e_cs)

CITY_STATE_STYLE = {
    "Dalaran": "_dalaran", "Theramore": "Humans", "Stromgarde": "Humans", "Gadgetzan": "Goblins",
    "Booty Bay": "Goblins", "Ratchet": "Goblins", "Everlook": "Goblins", "Steamwheedle Port": "Goblins",
    "Light's Hope Chapel": "Humans", "Cenarion Hold": "Night Elves", "Argent Vanguard": "Humans",
    "Feathermoon Stronghold": "Night Elves", "The Earthen Ring": "Tauren", "Knights of the Ebon Blade": "Scourge",
    "Explorers' League": "Dwarves", "Thorium Brotherhood": "Dwarves",
}

# house slots per stage: (x, foot y, width, height) on the hex face, back to front
SLOTS = {
    0: [(14, 30, 9, 6), (36, 26, 10, 7), (24, 38, 10, 6), (42, 40, 9, 6)],
    1: [(10, 28, 9, 6), (44, 26, 9, 7), (8, 40, 9, 6), (22, 42, 10, 7), (36, 42, 10, 6), (48, 38, 8, 6)],
    2: [(6, 30, 8, 6), (50, 30, 8, 6), (10, 42, 10, 7), (24, 42, 8, 6), (34, 42, 9, 7), (46, 42, 9, 6)],
}


def city_center(style_name, stage, seed=0):
    st = STYLES[style_name]
    rng = random.Random(hash((style_name, stage, seed)) & 0xffff)
    s = Scene()
    plaza(s, st["ground"], 22 + stage * 2, 12 + stage)
    roofs = [st["roof"]] + ([st["roof2"]] if st.get("roof2") else [])
    for i, (x, y, w, h) in enumerate(SLOTS[stage]):
        kind = st["house"]
        roof = roofs[i % len(roofs)]
        hh = h + (2 if stage == 2 else 0)
        s.piece(OY + y, lambda p, x=x, y=y, w=w, hh=hh, roof=roof, kind=kind:
                house(p, x, OY + y, w, hh, st["wall"], roof, kind=kind,
                      rh=(w * 0.9 if kind in ("cone", "tent") else w * 0.5 if kind == "thatch" else None), win=st["win"] if stage else None, trim=st["trim"]))
    if stage == 0:
        s.piece(OY + 24, lambda p: house(p, 22, OY + 24, 14, 8, st["wall"], st["roof"], kind=st["big"],
                                          rh=(12 if st["big"] in ("cone", "tent") else None), trim=st["trim"]))
    else:
        st["landmark"](s, st, rng)
    if st["extras"]:
        st["extras"](s, st, stage, rng)
    if stage == 2:
        city_wall(s, st, st["stone"], st["roof"] if st["tower_roof"] != "flat" else st["stone"], stage)
    return s.render()


def write_all(images_dir, eras, nations, city_states):
    """Write race city centers, city-state ones, and the generic era replacements into
    the HexaRealm (64 px) and FantasyHex (32 px, downscaled) tile folders."""
    out = {}
    for n in nations:
        for era, stage in STAGES:
            out["City center-%s-%s" % (n, era)] = city_center(n, stage)
    for cs in city_states:
        style = CITY_STATE_STYLE.get(cs, "_cs")
        for era, stage in STAGES:
            out["City center-%s-%s" % (cs, era)] = city_center(style, stage, seed=1)
    for era, stage in ERA_STAGE.items():
        out["City center-%s" % era] = city_center("_cs", stage)
    out["City center"] = city_center("_cs", 0)
    for name, im in out.items():
        for folder, scale in (("TileSets/HexaRealm/Tiles/", 1), ("TileSets/FantasyHex/Tiles/", 2)):
            path = os.path.join(images_dir, folder, name + ".png")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            (im if scale == 1 else im.resize((W // 2, H // 2), Image.BOX)).save(path)
    return len(out)
