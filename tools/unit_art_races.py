"""Race kits: the hand-placed unit sprites redrawn for each race (trial).

Every unit is a loadout (who carries what, drawn in unit_art*.py) worn by a body. A race
kit changes the body, not just its colours:
  * build     rows and columns are added to or taken out of the finished figure, so an
              orc is broader and shorter in the leg, an elf taller, a dwarf squat;
  * features  tusks, long ears, horns, a muzzle, a great beard, glowing eyes, drawn on
              top of whatever the unit wears on its head;
  * gear      the race's own helmets, shields, blades and shoulder pieces replace the
              Human ones wherever a loadout calls for them;
  * mount     riders sit on the race's own animal;
  * palette   skin, hair, metal, cloth and hide are the race's own materials.
All designs are original.
"""
import inspect

import unit_art as UA
import unit_art_humans as UH
import unit_art_machines as UM
from unit_art import (Canvas, lit, line, DARK, TINT, SKIN, HAIR, BLOND, STEEL, LEATHER, TAN, WHITE, WOOD, GOLD, IRON,
                      HORSE, STONE, GLOW, FY)
from unit_art_humans import GREEN, ARCANITE, ARCANE, AZER, GREYH, BLACKH, CLOTHD, FUR, FLAME, RED

BONE = ((246, 238, 212), (212, 198, 164), (152, 138, 122))

CUR = None                        # the race being drawn
HEADS = []                        # (cx, top) of every head drawn for the current sprite

MOUNTED = {"Knight", "Outrider", "Lancer", "War Rider", "Paladin", "Cavalry", "Mounted Archer", "Uther the Lightbringer"}
NO_BODY = {"Catapult", "Ballista", "Mortar Team", "Steam Tank"}     # machines keep their shape; crews are too small to rebuild


class Race:
    def __init__(self, name, cmap=None, rows=(), cols=(), hooks=None, finish=None, skin=SKIN):
        self.name = name
        self.cmap = {}
        for a, b in (cmap or {}).items():
            for i in range(3):
                self.cmap[tuple(a[i])] = tuple(b[i])
        self.rows = rows              # ("dup" | "del", offset from the feet row), applied top first
        self.cols = cols              # ("dup" | "del", offset from the centre column)
        self.hooks = hooks or {}
        self.finish = finish
        self.skin = skin
        self.special = {}


class RaceCanvas(Canvas):
    def __init__(self, race):
        super().__init__()
        self.race = race

    def put(self, s, x, y, c):
        if 0 <= x < self.gw and 0 <= y < self.gh:
            c = tuple(c(x, y) if callable(c) else c)
            self.lab[y][x] = s
            self.col[y][x] = self.race.cmap.get(c, c)


# ---------------------------------------------------------------- dispatch: the race's gear replaces the Human gear
HOOKABLE = ["head", "great_helm", "open_helm", "kettle", "hood", "hair", "beard", "brim_hat", "crest", "plume", "tall_plume",
            "feather", "goggles", "kite", "round_shield", "tower", "sword_up", "spear_head", "pauldron", "boots", "fist",
            "horse", "chanfron", "mantle", "cape", "bow", "quiver", "gun", "legs"]
_ORIG = {}


def _install():
    for name in HOOKABLE:
        orig = getattr(UH, name, None) or getattr(UA, name)
        _ORIG[name] = orig
        def disp(*a, _n=name, _o=orig, **k):
            if _n in ("head", "great_helm") and CUR is not None:
                HEADS.append((a[1], a[2]))
            h = CUR.hooks.get(_n) if CUR is not None else None
            return h(_o, *a, **k) if h else _o(*a, **k)
        for mod in (UA, UH, UM):
            if getattr(mod, name, None) is orig:
                setattr(mod, name, disp)


_install()


# ---------------------------------------------------------------- build: add or remove rows and columns
def _row_op(cv, op, y):
    lab, col = cv.lab, cv.col
    if not 0 < y < cv.gh:
        return
    if op == "del":
        for yy in range(y, 0, -1):
            lab[yy], col[yy] = lab[yy - 1][:], col[yy - 1][:]
        lab[0], col[0] = [-1] * cv.gw, [None] * cv.gw
    else:
        for yy in range(0, y):
            lab[yy], col[yy] = lab[yy + 1][:], col[yy + 1][:]


def _col_op(cv, op, x, right):
    for lab, col in zip(cv.lab, cv.col):
        for arr, empty in ((lab, -1), (col, None)):
            if op == "dup":
                if right:
                    arr[x + 1:] = arr[x:-1]
                else:
                    arr[:x] = arr[1:x + 1]
            else:
                if right:
                    arr[x:] = arr[x + 1:] + [empty]
                else:
                    arr[1:x + 1] = arr[:x]
                    arr[0] = empty


def _fit(cv):
    """Slide the figure back inside the frame if the build pushed it over an edge."""
    xs = [x for row in cv.lab for x, l in enumerate(row) if l >= 0]
    if not xs:
        return
    over = max(xs) - (cv.gw - 2)
    under = 1 - min(xs)
    shift = -over if over > 0 and min(xs) - over >= 1 else (under if under > 0 and max(xs) + under <= cv.gw - 2 else 0)
    if shift:
        for lab, col in zip(cv.lab, cv.col):
            for arr, empty in ((lab, -1), (col, None)):
                if shift < 0:
                    arr[:] = arr[-shift:] + [empty] * (-shift)
                else:
                    arr[:] = [empty] * shift + arr[:-shift]
        cv.shadows = [(cx + shift, cy, rx) for cx, cy, rx in cv.shadows]
    while any(l >= 0 for l in cv.lab[0]):                                  # keep one row free for the outline
        ys = [y for y, row in enumerate(cv.lab) if any(l >= 0 for l in row)]
        gap = next((y for y in range(2, min(ys) + 12) if all(cv.lab[y][x] == cv.lab[y + 1][x] for x in range(cv.gw))), None)
        if gap is None:
            break
        _row_op(cv, "del", gap)


def build_body(cv, race, cx, fy):
    for op, dy in sorted(race.rows, key=lambda t: t[1], reverse=True):     # offsets are "rows above the feet": top first
        _row_op(cv, op, fy - dy)
    right = sorted([c for c in race.cols if c[1] > 0], key=lambda t: -t[1])
    left = sorted([c for c in race.cols if c[1] < 0], key=lambda t: t[1])
    for op, dx in right:
        _col_op(cv, op, cx + dx, True)
    for op, dx in left:
        _col_op(cv, op, cx + dx, False)
    grow = sum(1 for op, _ in race.cols if op == "dup") - sum(1 for op, _ in race.cols if op == "del")
    cv.shadows = [(sx, sy, rx + grow // 2) for sx, sy, rx in cv.shadows]
    _fit(cv)


def base_name(stem):
    return stem[:-len("-Humans")] if stem.endswith("-Humans") else stem


def render(fn, race, stem=""):
    """Draw loadout `fn` on the body of `race`. Returns the three layer images."""
    global CUR
    fn = getattr(race, "special", {}).get(base_name(stem), fn)
    cv = RaceCanvas(race)
    CUR = race
    del HEADS[:]
    try:
        fn(cv)
        if race.finish:
            seen = []
            for h in HEADS:
                if h not in seen:
                    seen.append(h)
                    race.finish(cv, h[0], h[1])
        sig = inspect.signature(fn).parameters
        name = base_name(stem)
        if "cx" in sig and "fy" in sig and name not in MOUNTED and name not in NO_BODY:
            build_body(cv, race, sig["cx"].default, sig["fy"].default)
        else:
            _fit(cv)
    finally:
        CUR = None
    return cv.layers()


# ================================================================ shared pieces
def features(cv, pts, col, sep=False):
    p = cv.part(sep=sep)
    cv.pix(p, pts, col)
    return p


def beast(cv, cx, fy, ramp, head_rows, tail_rows, mane=None, ears=(), eye=None, extra=None, leg_w=3, dark_legs=True):
    """A four-legged mount in the warhorse's footprint (so saddles, cloths and riders fit). Returns the back row."""
    back = fy - 13
    for x0 in (cx - 8, cx + 5):
        s = cv.part()
        cv.rect(s, x0, fy - 7, x0 + leg_w - 2, fy - 1, ramp[2])
        cv.rect(s, x0, fy, x0 + leg_w - 1, fy, DARK)
    tl = cv.part()
    cv.rows(tl, [(back + dy, cx + a, cx + b) for dy, a, b in tail_rows], lit(mane or ramp, dark_from=cx - 11))
    b = cv.part()
    cv.rows(b, [(back, cx - 9, cx + 8)] + [(y, cx - 10, cx + 9) for y in range(back + 1, back + 6)] + [(back + 6, cx - 9, cx + 8)],
            lit(ramp, dark_from=cx + 8, light_to=cx + 7, light_rows=back + 1))
    cv.rows(b, [(back + 5, cx - 10, cx + 9), (back + 6, cx - 9, cx + 8)], ramp[2])
    for x0 in (cx - 10, cx + 6):
        s = cv.part()
        cv.rect(s, x0, fy - 7, x0 + leg_w - 1, fy - 1, lit(ramp, dark_from=x0 + leg_w - 1, light_to=x0))
        cv.rect(s, x0, fy, x0 + leg_w, fy, DARK)
    n = cv.part()
    cv.rows(n, [(back + dy, cx + a, cx + b) for dy, a, b in head_rows], lit(ramp, dark_from=cx + 15, light_to=cx + 12, light_rows=back - 4))
    if ears:
        e = cv.part()
        cv.pix(e, [(cx + a, back + dy) for a, dy in ears], ramp[1])
    d = cv.part(sep=False)
    if eye:
        cv.put(d, cx + eye[0], back + eye[1], eye[2] if len(eye) > 2 else DARK)
    if extra:
        extra(cv, cx, back)
    return back


# ================================================================ ORCS
ORC_SKIN = ((150, 192, 100), (108, 152, 76), (68, 104, 68))
ORC_IRON = ((182, 176, 180), (126, 120, 132), (78, 72, 92))
ORC_HIDE = ((214, 176, 130), (166, 126, 90), (110, 80, 68))
BLACK = ((92, 84, 96), (58, 52, 64), (36, 32, 44))
WOLF = ((176, 172, 180), (124, 120, 134), (78, 74, 94))


def orc_finish(cv, cx, top):
    features(cv, [(cx - 1, top + 2), (cx, top + 2), (cx + 1, top + 2), (cx + 2, top + 2), (cx + 3, top + 2)], ORC_SKIN[2])      # heavy brow
    features(cv, [(cx - 1, top + 5), (cx - 1, top + 4), (cx + 2, top + 5), (cx + 2, top + 4)], BONE[0])                           # tusks
    features(cv, [(cx - 4, top + 3), (cx - 5, top + 2)], ORC_SKIN[1], sep=True)                                                   # ear


def orc_great_helm(orig, cv, cx, top, ramp=STEEL):
    orig(cv, cx, top, ramp)
    j = cv.part(sep=False)                                                 # open jaw
    cv.rows(j, [(top + 4, cx - 2, cx + 3), (top + 5, cx - 2, cx + 3), (top + 6, cx - 2, cx + 2)], lit(ORC_SKIN, dark_from=cx + 3))
    h = cv.part()                                                          # horns
    cv.pix(h, [(cx - 4, top + 1), (cx - 5, top), (cx - 5, top - 1), (cx - 4, top - 2), (cx + 4, top + 1), (cx + 5, top), (cx + 5, top - 1), (cx + 4, top - 2)], BONE[1])
    cv.pix(h, [(cx - 4, top - 2), (cx + 4, top - 2)], BONE[0])


def orc_open_helm(orig, cv, cx, top, ramp=STEEL, skin=SKIN, nasal=False):
    orig(cv, cx, top, ramp, skin)
    s = cv.part()
    cv.pix(s, [(cx, top - 2), (cx, top - 3)], ramp[0])                     # spike


def orc_hair(orig, cv, cx, top, ramp=HAIR, long=False):
    k = cv.part()                                                          # topknot
    cv.rows(k, [(top - 3, cx - 2, cx - 1), (top - 2, cx - 2, cx), (top - 1, cx - 1, cx + 1)], lit(BLACK, dark_from=cx))
    t = cv.part()
    cv.rows(t, [(top - 3, cx - 4, cx - 3), (top - 2, cx - 5, cx - 4), (top - 1, cx - 5, cx - 5), (top, cx - 5, cx - 5)], BLACK[1])
    b = cv.part(1, sep=False)
    cv.put(b, cx - 3, top - 3, TINT[0])


def orc_beard(orig, cv, cx, top, ramp=HAIR, long=False):
    if long:                                                               # elders: a plaited chin beard
        b = cv.part()
        cv.rows(b, [(top + 7, cx, cx + 2), (top + 8, cx, cx + 2), (top + 9, cx + 1, cx + 2), (top + 10, cx + 1, cx + 1)], lit(WHITE, dark_from=cx + 2))


def orc_pauldron(orig, cv, x, y, ramp, layer=0, w=5):
    s = orig(cv, x, y, ramp, layer, w)
    sp = cv.part()
    cv.pix(sp, [(x + 1, y - 1), (x + 1, y - 2), (x + w - 2, y - 1)], BONE[0])
    return s


def orc_sword(orig, cv, x, tip, gy, ramp=STEEL, guard=1, guard_ramp=TINT):
    """Orcs carry axes: a haft with a broad bearded blade."""
    h = cv.part()
    cv.rect(h, x, tip + 1, x, gy + 4, WOOD[1])
    cv.rect(h, x, tip + 1, x, tip + 6, WOOD[0])
    b = cv.part()
    cv.rows(b, [(tip, x - 3, x - 2), (tip + 1, x - 4, x - 1), (tip + 2, x - 4, x + 1), (tip + 3, x - 4, x + 1), (tip + 4, x - 4, x - 1), (tip + 5, x - 4, x - 2),
                (tip + 6, x - 4, x - 3)], lit(ramp, dark_from=x - 1, light_to=x - 4, light_rows=tip + 6))
    g = cv.part(guard)
    cv.rect(g, x - 1, gy, x + 1, gy, lit(guard_ramp, dark_from=x + 1))


def orc_kite(orig, cv, x, top, w=9, h=12):
    """A round hide-and-plank shield with iron spikes, nation colours on the face."""
    UH.round_shield(cv, x, top + 1, rim=IRON)
    sp = cv.part()
    cv.pix(sp, [(x + 4, top), (x - 1, top + 5), (x + 9, top + 5), (x + 4, top + 10)], BONE[0])


def orc_tower(orig, cv, x, top, w=9, h=16, stud=1):
    orig(cv, x, top, w, h, stud)
    sp = cv.part()
    cv.pix(sp, [(x + w, top + 3), (x + w, top + 8), (x + w, top + 13), (x + 2, top - 1), (x + w - 3, top - 1)], BONE[0])


def wolf(orig, cv, cx, fy, ramp=HORSE):
    def extra(cv, cx, back):
        m = cv.part(sep=False)                                              # ruff
        cv.rows(m, [(back - 5, cx + 7, cx + 9), (back - 4, cx + 6, cx + 8), (back - 3, cx + 5, cx + 7), (back - 2, cx + 5, cx + 7), (back - 1, cx + 4, cx + 7),
                    (back, cx + 2, cx + 6)], WOLF[2])
        t = cv.part(sep=False)
        cv.pix(t, [(cx + 15, back - 1), (cx + 13, back - 1)], BONE[0])       # fangs
        cv.put(t, cx + 17, back - 3, DARK)
    return beast(cv, cx, fy, WOLF,
                 head_rows=[(-6, 8, 11), (-5, 7, 13), (-4, 6, 15), (-3, 6, 17), (-2, 5, 17), (-1, 5, 11), (0, 4, 10), (1, 5, 9)],
                 tail_rows=[(-2, -14, -12), (-1, -14, -11), (0, -13, -10), (1, -12, -10), (2, -11, -10)],
                 mane=WOLF, ears=[(8, -8), (8, -7), (11, -8), (11, -7)], eye=(12, -4, (236, 96, 60)), extra=extra)


def no_chanfron(orig, cv, cx, back, ramp=STEEL):
    c = cv.part()                                                          # a spiked collar instead of face plate
    cv.rows(c, [(back - 1, cx + 4, cx + 8), (back, cx + 4, cx + 8)], lit(ramp, dark_from=cx + 7))
    sp = cv.part()
    cv.pix(sp, [(cx + 5, back - 2), (cx + 7, back - 2)], BONE[0])


ORCS = Race("Orcs",
            cmap={SKIN: ORC_SKIN, HAIR: BLACK, BLOND: BLACK, STEEL: ORC_IRON, WHITE: ORC_HIDE, HORSE: WOLF, GREYH: WOLF, BLACKH: BLACK,
                  GOLD: BONE, ARCANITE: ((214, 120, 96), (160, 70, 62), (104, 44, 52)), GREEN: FUR},
            rows=(("del", 4),), cols=(("dup", 3), ("dup", -3)),
            hooks={"great_helm": orc_great_helm, "open_helm": orc_open_helm, "hair": orc_hair, "beard": orc_beard, "pauldron": orc_pauldron,
                   "sword_up": orc_sword, "kite": orc_kite, "tower": orc_tower, "horse": wolf, "chanfron": no_chanfron},
            finish=orc_finish)



# ================================================================ ELVES (shared pieces)
def elf_finish(skin, eye, up=False):
    def f(cv, cx, top):
        pts = [(cx - 4, top + 2), (cx - 5, top + 1), (cx - 5, top), (cx - 6, top - 1)] if up else \
              [(cx - 4, top + 3), (cx - 4, top + 2), (cx - 5, top + 2), (cx - 6, top + 1), (cx - 7, top)]
        features(cv, pts, skin[1], sep=True)
        features(cv, [(cx, top + 3), (cx + 2, top + 3)], eye)
    return f


def long_hair(orig, cv, cx, top, ramp=HAIR, long=False):
    orig(cv, cx, top, ramp, True)


def no_beard(orig, cv, cx, top, ramp=HAIR, long=False):
    pass


# ================================================================ NIGHT ELVES
NE_SKIN = ((216, 180, 234), (172, 132, 204), (116, 88, 158))
NE_HAIR = ((136, 224, 210), (72, 170, 172), (44, 110, 132))
SILVER = ((242, 246, 252), (198, 208, 226), (134, 146, 180))
MOONSTEEL = ((228, 242, 244), (162, 194, 206), (98, 122, 154))
SABER = ((156, 146, 182), (108, 100, 138), (68, 62, 98))


def glaive(orig, cv, x, tip, gy, ramp=STEEL, guard=1, guard_ramp=TINT):
    """A moon glaive: a short grip under a wide crescent blade."""
    h = cv.part()
    cv.rect(h, x, tip + 6, x, gy + 4, WOOD[1])
    b = cv.part()
    cv.rows(b, [(tip, x - 3, x - 2), (tip + 1, x - 4, x - 2), (tip + 2, x - 4, x - 3), (tip + 3, x - 4, x - 3), (tip + 4, x - 4, x - 2), (tip + 5, x - 3, x),
                (tip + 6, x - 2, x + 2), (tip + 5, x + 1, x + 3), (tip + 4, x + 3, x + 4), (tip + 3, x + 4, x + 4), (tip + 2, x + 4, x + 4)],
            lit(ramp, dark_from=x + 2, light_to=x - 3))
    g = cv.part(guard)
    cv.rect(g, x - 1, gy, x + 1, gy, lit(guard_ramp, dark_from=x + 1))


def ne_great_helm(orig, cv, cx, top, ramp=STEEL):
    orig(cv, cx, top, ramp)
    w = cv.part(1)                                                         # swept wings
    cv.pix(w, [(cx - 4, top + 1), (cx - 5, top), (cx - 5, top - 1), (cx - 6, top - 2), (cx - 6, top - 3), (cx - 4, top), (cx - 4, top - 1)], TINT[0])


def nightsaber(orig, cv, cx, fy, ramp=HORSE):
    def extra(cv, cx, back):
        st = cv.part(sep=False)                                             # stripes
        for x in (cx - 7, cx - 3, cx + 1, cx + 5):
            cv.pix(st, [(x, back + 1), (x + 1, back + 2), (x, back + 3)], SABER[2])
        t = cv.part()
        cv.pix(t, [(cx + 15, back - 1), (cx + 15, back)], BONE[0])           # sabre fang
    return beast(cv, cx, fy, SABER,
                 head_rows=[(-6, 9, 13), (-5, 8, 15), (-4, 7, 16), (-3, 6, 17), (-2, 6, 17), (-1, 5, 12), (0, 4, 10), (1, 5, 9)],
                 tail_rows=[(-5, -15, -14), (-4, -15, -14), (-3, -15, -13), (-2, -14, -12), (-1, -13, -11), (0, -12, -10), (1, -11, -10)],
                 ears=[(9, -7), (12, -7)], eye=(13, -4, (250, 236, 150)), extra=extra)


def wisp(cv, cx=UA.CIV_X + 2, fy=FY):
    """A wisp: a ball of pale light with a trailing tail, leaves of the nation's colour drifting round it."""
    cv.shadow(cx, 5)
    cy = fy - 14
    t = cv.part()
    cv.rows(t, [(cy + 5, cx - 2, cx + 1), (cy + 6, cx - 3, cx), (cy + 7, cx - 3, cx - 1), (cy + 8, cx - 4, cx - 2), (cy + 9, cx - 4, cx - 3), (cy + 10, cx - 5, cx - 4)],
            lit(NE_HAIR, dark_from=cx, light_to=cx - 2))
    b = cv.part()
    cv.rows(b, [(cy - 4, cx - 2, cx + 2), (cy - 3, cx - 3, cx + 3)] + [(y, cx - 4, cx + 4) for y in range(cy - 2, cy + 3)] + [(cy + 3, cx - 3, cx + 3), (cy + 4, cx - 2, cx + 2)],
            lit(NE_HAIR, dark_from=cx + 3, light_to=cx - 1, light_rows=cy))
    c = cv.part(sep=False)
    cv.rows(c, [(cy - 2, cx - 1, cx + 1), (cy - 1, cx - 2, cx + 2), (cy, cx - 2, cx + 2), (cy + 1, cx - 2, cx + 2), (cy + 2, cx - 1, cx + 1)], (236, 255, 250))
    cv.pix(c, [(cx - 1, cy), (cx + 1, cy)], NE_HAIR[2])
    for (x, y), layer in (((cx - 7, cy - 4), 2), ((cx + 7, cy - 1), 1), ((cx + 5, cy + 6), 2), ((cx - 8, cy + 3), 1)):
        l = cv.part(layer)
        cv.pix(l, [(x, y), (x + 1, y), (x, y + 1)], TINT[0])
    s = cv.part()
    cv.pix(s, [(cx - 6, cy - 7), (cx + 6, cy - 6), (cx + 8, cy + 3)], (236, 255, 250))


NIGHT_ELVES = Race("Night Elves",
                   cmap={SKIN: NE_SKIN, HAIR: NE_HAIR, BLOND: SILVER, GOLD: SILVER, STEEL: MOONSTEEL, HORSE: SABER, GREYH: SABER, BLACKH: SABER},
                   rows=(("dup", 4), ("dup", 10)),
                   hooks={"hair": long_hair, "beard": no_beard, "sword_up": glaive, "great_helm": ne_great_helm, "horse": nightsaber, "chanfron": no_chanfron},
                   finish=elf_finish(NE_SKIN, (255, 240, 170)))
NIGHT_ELVES.special = {"Peasant": wisp}


# ================================================================ BLOOD ELVES
BE_SKIN = ((252, 218, 184), (226, 174, 136), (172, 114, 100))
SUNGOLD = ((255, 236, 170), (230, 186, 96), (166, 116, 64))
STRIDER = ((255, 170, 150), (226, 104, 96), (150, 60, 78))


def be_great_helm(orig, cv, cx, top, ramp=STEEL):
    orig(cv, cx, top, ramp)
    w = cv.part()                                                          # a tall swept crest
    cv.pix(w, [(cx - 3, top - 1), (cx - 4, top - 2), (cx - 4, top - 3), (cx - 5, top - 4), (cx - 5, top - 5), (cx - 3, top - 2), (cx - 4, top - 4)], SUNGOLD[0])


def be_pauldron(orig, cv, x, y, ramp, layer=0, w=5):
    s = orig(cv, x, y, ramp, layer, w)
    sp = cv.part()
    cv.pix(sp, [(x, y - 1), (x, y - 2), (x - 1, y - 3), (x + 1, y - 1)], SUNGOLD[0])
    return s


def hawkstrider(orig, cv, cx, fy, ramp=HORSE):
    """A tall running bird: two long legs, a plumed tail, a long neck and a hooked beak."""
    back = fy - 13
    for x0 in (cx - 3, cx + 3):
        l = cv.part()
        cv.rect(l, x0, back + 7, x0 + 1, fy - 1, lit(SUNGOLD, dark_from=x0 + 1))
        cv.rect(l, x0, fy, x0 + 3, fy, SUNGOLD[2])
    tl = cv.part(2)                                                        # tail plumes: outer colour
    cv.rows(tl, [(back - 3, cx - 14, cx - 11), (back - 2, cx - 15, cx - 10), (back - 1, cx - 15, cx - 9), (back, cx - 14, cx - 9), (back + 1, cx - 13, cx - 9),
                 (back + 2, cx - 14, cx - 10), (back + 3, cx - 15, cx - 11)], lit(TINT, dark_from=cx - 10, light_to=cx - 13))
    b = cv.part()
    cv.rows(b, [(back, cx - 8, cx + 7)] + [(y, cx - 9, cx + 8) for y in range(back + 1, back + 5)] + [(back + 5, cx - 8, cx + 7), (back + 6, cx - 6, cx + 5)],
            lit(STRIDER, dark_from=cx + 7, light_to=cx + 5, light_rows=back + 1))
    cv.rows(b, [(back + 6, cx - 6, cx + 5)], STRIDER[2])
    n = cv.part()                                                          # neck and head
    cv.rows(n, [(back - 9, cx + 8, cx + 11), (back - 8, cx + 7, cx + 12), (back - 7, cx + 7, cx + 12), (back - 6, cx + 7, cx + 9), (back - 5, cx + 6, cx + 9),
                (back - 4, cx + 6, cx + 8), (back - 3, cx + 5, cx + 8), (back - 2, cx + 5, cx + 8), (back - 1, cx + 5, cx + 8), (back, cx + 4, cx + 8)],
            lit(STRIDER, dark_from=cx + 8, light_to=cx + 6))
    bk = cv.part()
    cv.rows(bk, [(back - 8, cx + 13, cx + 15), (back - 7, cx + 13, cx + 14)], SUNGOLD[1])
    d = cv.part(sep=False)
    cv.put(d, cx + 10, back - 8, DARK)
    cr = cv.part(1)                                                        # crest: inner colour
    cv.pix(cr, [(cx + 8, back - 10), (cx + 7, back - 11), (cx + 9, back - 11), (cx + 6, back - 12)], TINT[0])
    return back


def skip(orig, *a, **k):
    pass


BLOOD_ELVES = Race("Blood Elves",
                   cmap={SKIN: BE_SKIN, HAIR: BLOND, STEEL: SUNGOLD, GREEN: RED, ARCANITE: SUNGOLD, HORSE: STRIDER, GREYH: STRIDER, BLACKH: STRIDER,
                         FUR: RED},
                   rows=(("dup", 4),),
                   hooks={"hair": long_hair, "beard": no_beard, "great_helm": be_great_helm, "pauldron": be_pauldron, "horse": hawkstrider, "chanfron": skip},
                   finish=elf_finish(BE_SKIN, (140, 240, 110), up=True))


# ================================================================ DWARVES
DW_SKIN = ((248, 194, 154), (216, 142, 110), (158, 92, 86))
GINGER = ((238, 146, 74), (190, 100, 52), (124, 62, 48))
RAMC = ((232, 226, 212), (188, 180, 170), (128, 120, 126))


def dwarf_finish(cv, cx, top):
    b = cv.part()
    cv.rows(b, [(top + 5, cx - 3, cx + 3), (top + 6, cx - 3, cx + 3), (top + 7, cx - 3, cx + 3), (top + 8, cx - 3, cx + 3), (top + 9, cx - 2, cx + 2),
                (top + 10, cx - 1, cx + 1)], lit(GINGER, dark_from=cx + 2, light_to=cx - 1, light_rows=top + 6))
    cv.pix(b, [(cx - 3, top + 4)], GINGER[1])
    r = cv.part(sep=False)
    cv.rect(r, cx - 1, top + 9, cx + 1, top + 9, GOLD[1])                    # beard ring
    cv.put(r, cx + 3, top + 4, DW_SKIN[2])                                   # nose


def hammer(orig, cv, x, tip, gy, ramp=STEEL, guard=1, guard_ramp=TINT):
    h = cv.part()
    cv.rect(h, x, tip + 5, x, gy + 4, WOOD[1])
    hd = cv.part()
    cv.rect(hd, x - 3, tip, x + 3, tip + 4, lit(ramp, dark_from=x + 2, light_to=x - 2, light_rows=tip + 1))
    cv.rect(hd, x - 3, tip + 4, x + 3, tip + 4, ramp[2])
    g = cv.part(guard, sep=False)
    cv.rect(g, x - 3, tip + 2, x + 3, tip + 2, lit(guard_ramp, dark_from=x + 2))


def round_for_kite(rim):
    def f(orig, cv, x, top, w=9, h=12):
        UH.round_shield(cv, x, top + 1, rim=rim)
    return f


def ram(orig, cv, cx, fy, ramp=HORSE):
    def extra(cv, cx, back):
        hn = cv.part()                                                      # curled horn
        cv.rows(hn, [(back - 7, cx + 8, cx + 11), (back - 6, cx + 7, cx + 8), (back - 6, cx + 11, cx + 12), (back - 5, cx + 7, cx + 7), (back - 5, cx + 12, cx + 12),
                     (back - 4, cx + 7, cx + 8), (back - 4, cx + 11, cx + 12), (back - 3, cx + 8, cx + 11)], lit(BONE, dark_from=cx + 11))
        w = cv.part(sep=False)                                              # fleece
        cv.pix(w, [(x, back + 1 + (x % 2)) for x in range(cx - 8, cx + 8, 2)], RAMC[0])
    return beast(cv, cx, fy, RAMC,
                 head_rows=[(-5, 9, 14), (-4, 8, 16), (-3, 7, 17), (-2, 6, 17), (-1, 5, 14), (0, 4, 10), (1, 5, 9)],
                 tail_rows=[(1, -12, -11), (2, -12, -11)], eye=(14, -3), extra=extra)


DWARVES = Race("Dwarves",
               cmap={SKIN: DW_SKIN, HAIR: GINGER, BLOND: GINGER, HORSE: RAMC, GREYH: RAMC, BLACKH: ((150, 142, 140), (106, 98, 102), (68, 62, 74))},
               rows=(("del", 4), ("del", 5), ("del", 10)), cols=(("dup", 3), ("dup", -3)),
               hooks={"beard": no_beard, "sword_up": hammer, "kite": round_for_kite(IRON), "horse": ram, "chanfron": skip},
               finish=dwarf_finish)


# ================================================================ TAUREN
T_FUR = ((196, 152, 110), (150, 108, 76), (100, 68, 54))
T_MANE = ((112, 78, 58), (78, 52, 42), (50, 34, 34))
T_HIDE = ((226, 200, 156), (186, 154, 112), (132, 102, 84))
KODO = ((170, 164, 140), (124, 118, 102), (82, 76, 74))


def tauren_finish(cv, cx, top):
    m = cv.part()                                                          # muzzle
    cv.rows(m, [(top + 3, cx + 3, cx + 5), (top + 4, cx + 2, cx + 6), (top + 5, cx + 2, cx + 6), (top + 6, cx + 3, cx + 5)], lit(T_HIDE, dark_from=cx + 6, light_to=cx + 3, light_rows=top + 4))
    d = cv.part(sep=False)
    cv.put(d, cx + 6, top + 4, DARK)
    cv.put(d, cx + 5, top + 6, GOLD[1])                                      # nose ring
    h = cv.part()                                                          # horns
    cv.pix(h, [(cx - 4, top + 1), (cx - 5, top), (cx - 6, top - 1), (cx - 6, top - 2), (cx - 5, top - 3), (cx + 4, top), (cx + 5, top - 1), (cx + 5, top - 2), (cx + 4, top - 3)], BONE[1])
    cv.pix(h, [(cx - 5, top - 3), (cx + 4, top - 3)], BONE[0])
    features(cv, [(cx - 4, top + 3), (cx - 5, top + 3)], T_FUR[2], sep=True)


def hooves(orig, cv, cx, fy, ramp=LEATHER):
    for x0 in (cx - 5, cx + 1):
        s = cv.part()
        cv.rect(s, x0 + 1, fy - 2, x0 + 4, fy - 1, lit(SKIN, dark_from=x0 + 4, light_to=x0 + 1))
        cv.rect(s, x0, fy, x0 + 4, fy, T_MANE[2])
        cv.rect(s, x0, fy - 1, x0, fy - 1, T_MANE[1])


def headdress(orig, cv, cx, top, ramp=STEEL, *a, **k):
    """No iron helms: a leather browband with a fan of feathers in the nation's colour."""
    UH.head(cv, cx, top)
    b = cv.part(sep=False)
    cv.rect(b, cx - 3, top + 1, cx + 3, top + 1, LEATHER[1])
    cv.put(b, cx + 1, top + 1, AZER[1])
    f = cv.part(1)
    cv.pix(f, [(cx - 4, top), (cx - 5, top - 1), (cx - 5, top - 2), (cx - 4, top - 1), (cx - 3, top - 1), (cx - 3, top - 2), (cx - 4, top - 3), (cx - 6, top), (cx - 7, top - 1)], TINT[0])


def braids(orig, cv, cx, top, ramp=HAIR, long=False):
    b = cv.part()
    cv.rows(b, [(y, cx - 4, cx - 3) for y in range(top + 4, top + 10)], lit(T_MANE, dark_from=cx - 3))
    t = cv.part(1, sep=False)
    cv.rect(t, cx - 4, top + 8, cx - 3, top + 8, TINT[0])
    m = cv.part(sep=False)
    cv.rows(m, [(top, cx - 2, cx + 2), (top + 1, cx - 3, cx + 1)], T_MANE[1])


def maul(orig, cv, x, tip, gy, ramp=STEEL, guard=1, guard_ramp=TINT):
    """A totem maul: a log haft with a bound stone head and hanging feathers."""
    h = cv.part()
    cv.rect(h, x, tip + 5, x + 1, gy + 4, lit(WOOD, dark_from=x + 1))
    hd = cv.part()
    cv.rows(hd, [(tip, x - 2, x + 3), (tip + 1, x - 3, x + 4), (tip + 2, x - 3, x + 4), (tip + 3, x - 3, x + 4), (tip + 4, x - 2, x + 3)], lit(STONE, dark_from=x + 3, light_to=x - 1, light_rows=tip + 1))
    bd = cv.part(sep=False)
    cv.rect(bd, x, tip, x + 1, tip + 4, LEATHER[1])
    f = cv.part(guard)
    cv.pix(f, [(x - 1, tip + 6), (x - 2, tip + 7), (x - 2, tip + 8), (x + 2, tip + 6), (x + 3, tip + 7)], guard_ramp[0])


def hide_shield(orig, cv, x, top, w=9, h=12):
    UH.round_shield(cv, x, top + 1, rim=WOOD)
    f = cv.part(1)
    cv.pix(f, [(x + 2, top + 10), (x + 2, top + 11), (x + 6, top + 10), (x + 6, top + 11), (x + 6, top + 12)], TINT[0])


def kodo(orig, cv, cx, fy, ramp=HORSE):
    def extra(cv, cx, back):
        hn = cv.part()
        cv.pix(hn, [(cx + 16, back - 4), (cx + 17, back - 5), (cx + 17, back - 6), (cx + 12, back - 5), (cx + 12, back - 6)], BONE[0])
        pl = cv.part(sep=False)                                             # ridge of plates
        cv.pix(pl, [(x, back) for x in range(cx - 8, cx + 4, 3)] + [(x, back + 2) for x in range(cx - 7, cx + 8, 4)], KODO[2])
    return beast(cv, cx, fy, KODO,
                 head_rows=[(-4, 8, 14), (-3, 6, 17), (-2, 5, 18), (-1, 5, 18), (0, 4, 17), (1, 5, 14), (2, 6, 11)],
                 tail_rows=[(1, -13, -11), (2, -14, -11), (3, -14, -12), (4, -13, -12)], eye=(13, -2), extra=extra, leg_w=4)


TAUREN = Race("Tauren",
              cmap={SKIN: T_FUR, HAIR: T_MANE, BLOND: T_MANE, WHITE: T_HIDE, STEEL: ((220, 212, 196), (168, 158, 144), (110, 100, 98)),
                    HORSE: KODO, GREYH: KODO, BLACKH: KODO},
              rows=(("dup", 4), ("dup", 10), ("dup", 12)), cols=(("dup", 3), ("dup", -3)),
              hooks={"boots": hooves, "great_helm": headdress, "open_helm": headdress, "kettle": headdress, "hair": braids, "beard": no_beard,
                     "sword_up": maul, "kite": hide_shield, "horse": kodo, "chanfron": skip},
              finish=tauren_finish)



# ================================================================ two-legged mounts (birds, raptors, striders)
def strider(body, legs_r, beak, plume=2, crest=1, teeth=False, metal=False):
    def f(orig, cv, cx, fy, ramp=HORSE):
        back = fy - 13
        for x0 in (cx - 3, cx + 3):
            l = cv.part()
            cv.rect(l, x0, back + 7, x0 + 1, fy - 1, lit(legs_r, dark_from=x0 + 1))
            cv.rect(l, x0, fy, x0 + 3, fy, legs_r[2])
        tl = cv.part(plume) if plume else cv.part()
        tr = TINT if plume else body
        if teeth:                                                           # a heavy lizard tail
            cv.rows(tl, [(back + 1, cx - 13, cx - 9), (back + 2, cx - 15, cx - 9), (back + 3, cx - 16, cx - 10), (back + 4, cx - 16, cx - 13)], lit(tr, dark_from=cx - 10, light_to=cx - 14))
        else:
            cv.rows(tl, [(back - 3, cx - 14, cx - 11), (back - 2, cx - 15, cx - 10), (back - 1, cx - 15, cx - 9), (back, cx - 14, cx - 9), (back + 1, cx - 13, cx - 9),
                         (back + 2, cx - 14, cx - 10), (back + 3, cx - 15, cx - 11)], lit(tr, dark_from=cx - 10, light_to=cx - 13))
        b = cv.part()
        cv.rows(b, [(back, cx - 8, cx + 7)] + [(y, cx - 9, cx + 8) for y in range(back + 1, back + 5)] + [(back + 5, cx - 8, cx + 7), (back + 6, cx - 6, cx + 5)],
                lit(body, dark_from=cx + 7, light_to=cx + 5, light_rows=back + 1))
        cv.rows(b, [(back + 6, cx - 6, cx + 5)], body[2])
        if metal:
            rv = cv.part(sep=False)
            cv.pix(rv, [(cx - 6, back + 2), (cx - 2, back + 2), (cx + 2, back + 2), (cx + 6, back + 2)], body[2])
            cv.rect(rv, cx - 9, back + 4, cx + 8, back + 4, legs_r[1])
        n = cv.part()
        if teeth:
            cv.rows(n, [(back - 8, cx + 8, cx + 13), (back - 7, cx + 7, cx + 16), (back - 6, cx + 7, cx + 17), (back - 5, cx + 7, cx + 12), (back - 4, cx + 6, cx + 16),
                        (back - 3, cx + 6, cx + 9), (back - 2, cx + 5, cx + 8), (back - 1, cx + 5, cx + 8), (back, cx + 4, cx + 8)], lit(body, dark_from=cx + 14, light_to=cx + 9, light_rows=back - 6))
            t = cv.part(sep=False)
            cv.pix(t, [(cx + 13, back - 5), (cx + 15, back - 5), (cx + 14, back - 5)], BONE[0])
            cv.pix(t, [(cx + 13, back - 5)], DARK)
            cv.put(t, cx + 11, back - 7, (250, 220, 90))
        else:
            cv.rows(n, [(back - 9, cx + 8, cx + 11), (back - 8, cx + 7, cx + 12), (back - 7, cx + 7, cx + 12), (back - 6, cx + 7, cx + 9), (back - 5, cx + 6, cx + 9),
                        (back - 4, cx + 6, cx + 8), (back - 3, cx + 5, cx + 8), (back - 2, cx + 5, cx + 8), (back - 1, cx + 5, cx + 8), (back, cx + 4, cx + 8)],
                    lit(body, dark_from=cx + 8, light_to=cx + 6))
            bk = cv.part()
            cv.rows(bk, [(back - 8, cx + 13, cx + 15), (back - 7, cx + 13, cx + 14)], beak[1])
            d = cv.part(sep=False)
            cv.put(d, cx + 10, back - 8, AZER[0] if metal else DARK)
        if crest:
            cr = cv.part(crest)
            cv.pix(cr, [(cx + 8, back - 10), (cx + 7, back - 11), (cx + 9, back - 11), (cx + 6, back - 12)], TINT[0])
        return back
    return f


BLOOD_ELVES.hooks["horse"] = strider(STRIDER, SUNGOLD, SUNGOLD)


def recolor(race, name, cmap, **kw):
    """A sister race: the same kit with its own palette and a few of its own pieces."""
    r = Race(name, rows=kw.get("rows", race.rows), cols=kw.get("cols", race.cols), hooks=dict(race.hooks), finish=kw.get("finish", race.finish))
    r.cmap = dict(race.cmap)
    for a, b in cmap.items():
        for i in range(3):
            r.cmap[tuple(a[i])] = tuple(b[i])
    r.hooks.update(kw.get("hooks", {}))
    r.special = dict(kw.get("special", {}))
    return r


# ---------------------------------------------------------------- High Elves, Nightborne
HIGH_ELVES = recolor(BLOOD_ELVES, "High Elves", {STEEL: SILVER, GREEN: GREEN, ARCANITE: ARCANITE, FUR: FUR, HORSE: GREYH, GREYH: GREYH, BLACKH: GREYH},
                     finish=elf_finish(BE_SKIN, (130, 220, 255), up=True),
                     hooks={"horse": lambda orig, cv, cx, fy, ramp=HORSE: orig(cv, cx, fy, GREYH), "pauldron": lambda orig, *a, **k: orig(*a, **k),
                            "chanfron": lambda orig, *a, **k: orig(*a, **k)})
NB_SKIN = ((170, 160, 218), (122, 112, 178), (78, 70, 128))
MANA = ((236, 214, 255), (184, 140, 240), (118, 84, 190))
NIGHTBORNE = recolor(NIGHT_ELVES, "Nightborne", {SKIN: NB_SKIN, HAIR: WHITE, BLOND: WHITE, GOLD: GOLD, STEEL: ((226, 214, 244), (176, 158, 214), (112, 96, 160)),
                                                 HORSE: MANA, GREYH: MANA, BLACKH: MANA},
                     finish=elf_finish(NB_SKIN, (236, 200, 255)),
                     hooks={"sword_up": lambda orig, *a, **k: orig(*a, **k)})

# ---------------------------------------------------------------- Dark Iron Dwarves
DI_SKIN = ((178, 168, 170), (130, 120, 126), (86, 78, 90))
EMBER = ((255, 190, 90), (240, 120, 50), (170, 60, 44))


def dark_iron_finish(cv, cx, top):
    b = cv.part()
    cv.rows(b, [(top + 5, cx - 3, cx + 3), (top + 6, cx - 3, cx + 3), (top + 7, cx - 3, cx + 3), (top + 8, cx - 3, cx + 3), (top + 9, cx - 2, cx + 2), (top + 10, cx - 1, cx + 1)],
            lit(BLACK, dark_from=cx + 2, light_to=cx - 1, light_rows=top + 6))
    r = cv.part(sep=False)
    cv.rect(r, cx - 1, top + 9, cx + 1, top + 9, EMBER[1])
    cv.pix(r, [(cx, top + 3), (cx + 2, top + 3)], EMBER[0])


DARK_IRON = recolor(DWARVES, "Dark Iron Dwarves", {SKIN: DI_SKIN, HAIR: BLACK, BLOND: BLACK, STEEL: ((150, 144, 152), (102, 96, 108), (62, 58, 74)),
                                                   GOLD: EMBER, HORSE: BLACK, GREYH: BLACK, BLACKH: BLACK}, finish=dark_iron_finish)

# ---------------------------------------------------------------- Highmountain Tauren
HM_FUR = ((150, 122, 104), (108, 84, 72), (70, 52, 50))


def highmountain_finish(cv, cx, top):
    tauren_finish(cv, cx, top)
    a = cv.part()                                                          # antler tines on the horns
    cv.pix(a, [(cx - 7, top - 3), (cx - 7, top - 4), (cx - 5, top - 4), (cx - 5, top - 5), (cx + 6, top - 3), (cx + 6, top - 4), (cx + 4, top - 4), (cx + 4, top - 5)], BONE[0])


HIGHMOUNTAIN = recolor(TAUREN, "Highmountain Tauren", {SKIN: HM_FUR, HAIR: BLACK, BLOND: BLACK}, finish=highmountain_finish)

# ================================================================ TROLLS
TR_SKIN = ((140, 200, 210), (94, 154, 172), (58, 102, 130))
TR_HAIR = ((255, 150, 80), (224, 90, 50), (150, 50, 50))
RAPTOR = ((170, 200, 110), (120, 152, 80), (76, 104, 70))


def troll_finish(skin):
    def f(cv, cx, top):
        t = cv.part()                                                      # long tusks curving up
        cv.pix(t, [(cx + 3, top + 5), (cx + 4, top + 4), (cx + 4, top + 3), (cx, top + 5), (cx, top + 4)], BONE[0])
        features(cv, [(cx - 4, top + 3), (cx - 5, top + 2), (cx - 6, top + 2), (cx - 7, top + 1)], skin[1], sep=True)
        features(cv, [(cx + 4, top + 5)], skin[2], sep=True)                 # long nose / chin
    return f


def mohawk(orig, cv, cx, top, ramp=HAIR, long=False):
    m = cv.part()
    cv.rows(m, [(top - 4, cx - 1, cx + 1), (top - 3, cx - 2, cx + 2), (top - 2, cx - 3, cx + 2), (top - 1, cx - 3, cx + 1), (top, cx - 3, cx - 1), (top + 1, cx - 4, cx - 3),
                (top + 2, cx - 4, cx - 3)], lit(HAIR, dark_from=cx + 1, light_to=cx - 1, light_rows=top - 3))


def bare_feet(orig, cv, cx, fy, ramp=LEATHER):
    for x0 in (cx - 5, cx + 1):
        s = cv.part()
        cv.rect(s, x0 + 1, fy - 2, x0 + 3, fy - 1, lit(SKIN, dark_from=x0 + 3, light_to=x0 + 1))
        cv.rect(s, x0, fy, x0 + 4, fy, SKIN[2])
        cv.put(s, x0 + 2, fy, DARK)


def mask_shield(orig, cv, x, top, w=9, h=12):
    """A tall wooden shield painted as a mask in the nation's colours."""
    s = cv.part(2)
    rows = [(top, x + 2, x + w - 3)] + [(y, x + 1 if y < top + 2 else x, x + w - 2 if y < top + 2 else x + w - 1) for y in range(top + 1, top + h - 2)] + \
           [(top + h - 2, x + 1, x + w - 2), (top + h - 1, x + 3, x + w - 4)]
    cv.rows(s, rows, lit(TINT, dark_from=x + w - 3, light_to=x + 2, light_rows=top + h - 5))
    d = cv.part(1, sep=False)
    cv.rect(d, x + 1, top + 3, x + 3, top + 4, TINT[0])
    cv.rect(d, x + w - 4, top + 3, x + w - 2, top + 4, TINT[0])
    cv.rect(d, x + 2, top + 8, x + w - 3, top + 8, TINT[1])
    t = cv.part(sep=False)
    cv.pix(t, [(x + 2, top + 9), (x + 4, top + 9), (x + 6, top + 9)], BONE[0])
    f = cv.part()
    cv.pix(f, [(x + 3, top - 1), (x + 3, top - 2), (x + 5, top - 1), (x + 5, top - 2), (x + 5, top - 3)], TR_HAIR[1])


TROLLS = Race("Trolls",
              cmap={SKIN: TR_SKIN, HAIR: TR_HAIR, BLOND: TR_HAIR, STEEL: ((206, 200, 190), (152, 146, 140), (98, 92, 100)), WHITE: T_HIDE, GOLD: BONE,
                    HORSE: RAPTOR, GREYH: RAPTOR, BLACKH: RAPTOR},
              rows=(("dup", 4), ("dup", 5), ("dup", 11)),
              hooks={"hair": mohawk, "beard": no_beard, "boots": bare_feet, "kite": mask_shield, "horse": strider(RAPTOR, RAPTOR, BONE, plume=0, crest=1, teeth=True),
                     "chanfron": skip, "crest": lambda orig, cv, cx, top, layer=1: mohawk(None, cv, cx, top + 1)},
              finish=troll_finish(TR_SKIN))
ZA_SKIN = ((120, 196, 170), (78, 150, 132), (48, 100, 100))
HORN_BEAST = ((120, 170, 150), (84, 126, 116), (54, 84, 88))


def direhorn(orig, cv, cx, fy, ramp=HORSE):
    def extra(cv, cx, back):
        hn = cv.part()
        cv.pix(hn, [(cx + 16, back - 4), (cx + 17, back - 5), (cx + 17, back - 6), (cx + 12, back - 5), (cx + 12, back - 6), (cx + 13, back - 7), (cx + 9, back - 5), (cx + 9, back - 6)], BONE[0])
        fr = cv.part(1)                                                     # frill: inner colour
        cv.rows(fr, [(back - 6, cx + 5, cx + 7), (back - 5, cx + 4, cx + 7), (back - 4, cx + 4, cx + 6), (back - 3, cx + 4, cx + 5)], lit(TINT, dark_from=cx + 7))
    return beast(cv, cx, fy, HORN_BEAST,
                 head_rows=[(-4, 8, 14), (-3, 6, 17), (-2, 5, 18), (-1, 5, 18), (0, 4, 17), (1, 5, 14), (2, 6, 11)],
                 tail_rows=[(1, -13, -11), (2, -14, -11), (3, -15, -12), (4, -15, -13)], eye=(13, -2), extra=extra, leg_w=4)


ZANDALARI = recolor(TROLLS, "Zandalari Trolls", {SKIN: ZA_SKIN, HAIR: ((250, 250, 240), (212, 212, 220), (150, 152, 182)), BLOND: WHITE, STEEL: GOLD, GOLD: GOLD,
                                                HORSE: HORN_BEAST, GREYH: HORN_BEAST, BLACKH: HORN_BEAST},
                    rows=(("dup", 4), ("dup", 5), ("dup", 11), ("dup", 12)), finish=troll_finish(ZA_SKIN), hooks={"horse": direhorn})

# ================================================================ GNOMES AND GOBLINS
PINK = ((255, 170, 210), (232, 110, 170), (160, 70, 130))
BRASS = ((244, 214, 130), (204, 156, 76), (140, 98, 58))
GOB_SKIN = ((178, 214, 96), (130, 170, 70), (84, 116, 64))


def gnome_finish(cv, cx, top):
    g = cv.part(sep=False)                                                 # goggles on the brow
    cv.rect(g, cx - 3, top + 1, cx + 3, top + 1, LEATHER[2])
    cv.pix(g, [(cx, top + 1), (cx + 2, top + 1)], AZER[0])
    features(cv, [(cx - 4, top + 3), (cx - 4, top + 4)], SKIN[1], sep=True)


def tufts(orig, cv, cx, top, ramp=HAIR, long=False):
    h = cv.part()
    cv.rows(h, [(top - 2, cx - 3, cx - 2), (top - 2, cx + 1, cx + 2), (top - 1, cx - 4, cx + 3), (top, cx - 4, cx + 3), (top + 1, cx - 4, cx - 3), (top + 2, cx - 5, cx - 4)],
            lit(HAIR, dark_from=cx + 2, light_to=cx - 1))


GNOMES = Race("Gnomes",
              cmap={HAIR: PINK, BLOND: ((180, 240, 150), (120, 196, 96), (72, 130, 76)), GOLD: BRASS, HORSE: BRASS, GREYH: BRASS, BLACKH: BRASS},
              rows=(("del", 3), ("del", 4), ("del", 5), ("del", 10), ("del", 12)),
              hooks={"hair": tufts, "horse": strider(BRASS, IRON, IRON, plume=0, crest=0, metal=True), "chanfron": skip},
              finish=gnome_finish)


def goblin_finish(cv, cx, top):
    features(cv, [(cx - 4, top + 3), (cx - 5, top + 3), (cx - 6, top + 2), (cx - 7, top + 2), (cx - 8, top + 1), (cx - 4, top + 2)], GOB_SKIN[1], sep=True)   # long ear
    features(cv, [(cx + 4, top + 4), (cx + 5, top + 4)], GOB_SKIN[2], sep=True)                                                                           # long nose
    features(cv, [(cx + 1, top + 5), (cx + 3, top + 5)], BONE[0])                                                                                         # grin


GOBLINS = Race("Goblins",
               cmap={SKIN: GOB_SKIN, HAIR: BLACK, BLOND: RED, HORSE: RED, GREYH: RED, BLACKH: RED, STEEL: ((214, 206, 196), (160, 150, 144), (104, 96, 104))},
               rows=(("del", 3), ("del", 4), ("del", 10), ("del", 12)),
               hooks={"hair": skip, "beard": no_beard, "horse": strider(RED, IRON, IRON, plume=0, crest=0, metal=True), "chanfron": skip},
               finish=goblin_finish)

# ================================================================ UNDEAD: FORSAKEN AND SCOURGE
ROT = ((196, 206, 186), (148, 160, 146), (98, 108, 108))
RUST = ((196, 174, 152), (144, 118, 106), (94, 76, 78))
SHROUD = ((176, 166, 190), (128, 118, 146), (84, 76, 104))
SARONITE = ((150, 176, 184), (96, 122, 136), (56, 76, 96))


def bone_horse(orig, cv, cx, fy, ramp=HORSE):
    def extra(cv, cx, back):
        r = cv.part(sep=False)                                              # ribs
        for x in range(cx - 6, cx + 6, 3):
            cv.rect(r, x, back + 2, x, back + 5, DARK)
        cv.put(r, cx + 12, back - 5, (150, 240, 255))
    return beast(cv, cx, fy, BONE,
                 head_rows=[(-7, 8, 12), (-6, 7, 14), (-5, 8, 16), (-4, 9, 17), (-3, 9, 11), (-3, 14, 17), (-2, 8, 10), (-1, 7, 9), (0, 5, 9), (1, 5, 8)],
                 tail_rows=[(1, -12, -11), (2, -13, -12), (3, -13, -12), (4, -13, -13), (5, -13, -13)], extra=extra, leg_w=2)


def forsaken_finish(cv, cx, top):
    j = cv.part(sep=False)                                                 # bare jawbone
    cv.rows(j, [(top + 5, cx, cx + 3), (top + 6, cx, cx + 2)], BONE[1])
    cv.pix(j, [(cx + 1, top + 5), (cx + 3, top + 5)], DARK)
    cv.pix(j, [(cx, top + 3), (cx + 2, top + 3)], (255, 232, 110))


def ragged(orig, cv, cx, top, ramp=HAIR, long=False):
    h = cv.part(sep=False)
    cv.rows(h, [(top, cx - 2, cx + 1), (top + 1, cx - 3, cx - 1), (top + 2, cx - 3, cx - 3), (top + 4, cx - 3, cx - 3)], HAIR[1])


FORSAKEN = Race("Forsaken",
                cmap={SKIN: ROT, HAIR: ((150, 130, 170), (104, 88, 128), (68, 58, 92)), BLOND: SHROUD, STEEL: RUST, WHITE: SHROUD, TAN: SHROUD,
                      HORSE: BONE, GREYH: BONE, BLACKH: BONE, GOLD: ((200, 220, 150), (150, 176, 100), (96, 118, 76))},
                rows=(("del", 12),), cols=(("del", 4), ("del", -4)),
                hooks={"hair": ragged, "beard": no_beard, "horse": bone_horse, "chanfron": skip},
                finish=forsaken_finish)


def scourge_finish(cv, cx, top):
    s = cv.part(sep=False)                                                 # skull
    cv.rect(s, cx - 1, top + 2, cx + 3, top + 4, BONE[1])
    cv.rect(s, cx - 1, top + 3, cx, top + 4, DARK)
    cv.rect(s, cx + 2, top + 3, cx + 3, top + 4, DARK)
    cv.pix(s, [(cx, top + 3), (cx + 2, top + 3)], (140, 230, 255))
    cv.rows(s, [(top + 5, cx - 1, cx + 3)], BONE[0])
    cv.pix(s, [(cx, top + 5), (cx + 2, top + 5)], DARK)


SCOURGE = Race("Scourge",
               cmap={SKIN: BONE, HAIR: BONE, BLOND: BONE, STEEL: SARONITE, WHITE: SHROUD, TAN: ((170, 176, 186), (122, 130, 146), (80, 86, 106)),
                     HORSE: BONE, GREYH: BONE, BLACKH: BONE, GOLD: ((190, 236, 250), (110, 190, 230), (60, 120, 180)), LEATHER: ((140, 132, 140), (98, 90, 102), (62, 56, 70))},
               cols=(("del", 4), ("del", -4)),
               hooks={"hair": skip, "beard": no_beard, "horse": bone_horse, "chanfron": skip, "great_helm": orc_great_helm},
               finish=scourge_finish)

# ================================================================ DRAENEI
DR_SKIN = ((178, 198, 244), (126, 150, 214), (82, 100, 166))
CRYSTAL = ((240, 230, 252), (194, 174, 230), (126, 106, 174))
ELEKK = ((170, 170, 196), (122, 122, 152), (80, 78, 110))


def draenei_finish(cv, cx, top):
    h = cv.part()                                                          # horns swept back from the brow
    cv.pix(h, [(cx - 2, top - 1), (cx - 3, top - 1), (cx - 4, top), (cx - 5, top), (cx - 6, top + 1), (cx - 7, top + 1)], BONE[1])
    features(cv, [(cx, top + 7), (cx, top + 8), (cx + 2, top + 7), (cx + 2, top + 8)], DR_SKIN[1], sep=True)     # chin tendrils
    features(cv, [(cx, top + 3), (cx + 2, top + 3)], (220, 250, 255))


def elekk(orig, cv, cx, fy, ramp=HORSE):
    def extra(cv, cx, back):
        t = cv.part()                                                       # trunk and tusks
        cv.rows(t, [(back + 1, cx + 15, cx + 17), (back + 2, cx + 16, cx + 17), (back + 3, cx + 16, cx + 17), (back + 4, cx + 16, cx + 18), (back + 5, cx + 17, cx + 18)], lit(ELEKK, dark_from=cx + 17))
        k = cv.part()
        cv.pix(k, [(cx + 13, back + 1), (cx + 14, back + 2), (cx + 14, back + 3), (cx + 15, back + 3)], BONE[0])
        e = cv.part()
        cv.rows(e, [(back - 5, cx + 6, cx + 9), (back - 4, cx + 5, cx + 9), (back - 3, cx + 5, cx + 9), (back - 2, cx + 6, cx + 9), (back - 1, cx + 7, cx + 8)], lit(ELEKK, dark_from=cx + 9))
    return beast(cv, cx, fy, ELEKK,
                 head_rows=[(-6, 9, 15), (-5, 8, 17), (-4, 8, 18), (-3, 8, 18), (-2, 7, 18), (-1, 6, 18), (0, 4, 18)],
                 tail_rows=[(1, -12, -11), (2, -12, -11), (3, -12, -12)], eye=(15, -3), extra=extra, leg_w=4)


DRAENEI = Race("Draenei",
               cmap={SKIN: DR_SKIN, HAIR: BLACK, BLOND: WHITE, STEEL: CRYSTAL, HORSE: ELEKK, GREYH: ELEKK, BLACKH: ELEKK, ARCANITE: CRYSTAL},
               rows=(("dup", 4), ("dup", 10)),
               hooks={"boots": hooves, "horse": elekk, "chanfron": skip, "hair": long_hair},
               finish=draenei_finish)

# ================================================================ WORGEN
W_FUR = ((150, 140, 150), (104, 96, 110), (66, 60, 78))


def worgen_finish(cv, cx, top):
    m = cv.part()                                                          # snout
    cv.rows(m, [(top + 3, cx + 3, cx + 5), (top + 4, cx + 2, cx + 7), (top + 5, cx + 2, cx + 6)], lit(W_FUR, dark_from=cx + 6, light_to=cx + 3, light_rows=top + 3))
    d = cv.part(sep=False)
    cv.put(d, cx + 7, top + 4, DARK)
    cv.pix(d, [(cx + 3, top + 6), (cx + 5, top + 6)], BONE[0])
    cv.pix(d, [(cx, top + 3), (cx + 2, top + 3)], (255, 210, 90))
    e = cv.part()                                                          # tall ears
    cv.pix(e, [(cx - 3, top - 1), (cx - 3, top - 2), (cx - 4, top - 3), (cx - 2, top - 1), (cx + 2, top - 1), (cx + 2, top - 2), (cx + 3, top - 3), (cx + 1, top - 1)], W_FUR[1])


def paws(orig, cv, cx, fy, ramp=LEATHER):
    for x0 in (cx - 5, cx + 1):
        s = cv.part()
        cv.rect(s, x0 + 1, fy - 2, x0 + 4, fy - 1, lit(SKIN, dark_from=x0 + 4, light_to=x0 + 1))
        cv.rect(s, x0, fy, x0 + 5, fy, SKIN[2])
        cv.pix(s, [(x0 + 5, fy), (x0 + 3, fy)], BONE[0])


WORGEN = Race("Worgen",
              cmap={SKIN: W_FUR, HAIR: BLACK, BLOND: BLACK},
              rows=(("dup", 11),), cols=(("dup", 3), ("dup", -3)),
              hooks={"boots": paws, "hair": skip, "beard": no_beard},
              finish=worgen_finish)

# ================================================================ NAGA
NG_SKIN = ((150, 224, 200), (92, 176, 164), (52, 116, 128))
NG_BELLY = ((236, 232, 180), (200, 190, 130), (140, 130, 100))


def naga_finish(cv, cx, top):
    f = cv.part(1)                                                         # fin crest: inner colour
    cv.pix(f, [(cx - 2, top - 1), (cx - 3, top - 2), (cx - 3, top - 1), (cx - 4, top), (cx - 5, top - 1), (cx - 4, top + 1), (cx - 5, top + 2), (cx - 6, top + 1), (cx - 4, top + 3)], TINT[0])
    features(cv, [(cx, top + 3), (cx + 2, top + 3)], (255, 236, 120))


def no_legs(orig, cv, cx, fy, ramp=None):
    pass


def coils(orig, cv, cx, fy, ramp=LEATHER):
    """No legs: the body ends in a serpent's tail coiled on the ground."""
    c = cv.part()
    cv.rows(c, [(fy - 6, cx - 4, cx + 4), (fy - 5, cx - 5, cx + 4), (fy - 4, cx - 6, cx + 4), (fy - 3, cx - 7, cx + 5), (fy - 2, cx - 8, cx + 6), (fy - 1, cx - 8, cx + 6), (fy, cx - 7, cx + 5)],
            lit(NG_SKIN, dark_from=cx + 4, light_to=cx - 3, light_rows=fy - 3))
    b = cv.part(sep=False)
    cv.rows(b, [(fy - 5, cx, cx + 3), (fy - 4, cx, cx + 3), (fy - 3, cx + 1, cx + 4), (fy - 2, cx + 1, cx + 5)], NG_BELLY[1])
    cv.pix(b, [(cx - 5, fy - 2), (cx - 3, fy - 3), (cx - 6, fy - 1), (cx - 2, fy - 1)], NG_SKIN[2])
    t = cv.part()
    cv.rows(t, [(fy - 1, cx - 12, cx - 9), (fy, cx - 11, cx - 8), (fy - 2, cx - 13, cx - 12), (fy - 3, cx - 13, cx - 13)], lit(NG_SKIN, dark_from=cx - 9))


NAGA = Race("Naga",
            cmap={SKIN: NG_SKIN, HAIR: NG_SKIN, BLOND: NG_SKIN, STEEL: ((250, 236, 200), (220, 190, 140), (150, 120, 100)), HORSE: ((120, 190, 220), (70, 140, 180), (40, 90, 130)),
                  GREYH: ((120, 190, 220), (70, 140, 180), (40, 90, 130)), BLACKH: ((120, 190, 220), (70, 140, 180), (40, 90, 130)), LEATHER: ((120, 170, 160), (80, 126, 124), (50, 84, 92))},
            rows=(("dup", 11),),
            hooks={"boots": coils, "legs": no_legs, "hair": skip, "beard": no_beard, "horse": strider(((120, 190, 220), (70, 140, 180), (40, 90, 130)), NG_SKIN, BONE, plume=1, crest=1, teeth=True),
                   "chanfron": skip},
            finish=naga_finish)

# ================================================================ PANDAREN
P_FUR = ((250, 248, 240), (214, 212, 214), (156, 154, 172))
YAK = ((150, 112, 84), (108, 78, 60), (70, 50, 46))


def pandaren_finish(cv, cx, top):
    e = cv.part()                                                          # round ears
    cv.rows(e, [(top - 2, cx - 3, cx - 2), (top - 1, cx - 4, cx - 2), (top - 2, cx + 2, cx + 3), (top - 1, cx + 2, cx + 4)], BLACK[1])
    p = cv.part(sep=False)                                                 # eye patches
    cv.rect(p, cx - 1, top + 2, cx, top + 4, BLACK[1])
    cv.rect(p, cx + 2, top + 2, cx + 3, top + 4, BLACK[1])
    cv.pix(p, [(cx, top + 3), (cx + 2, top + 3)], (250, 248, 240))
    cv.put(p, cx + 1, top + 5, BLACK[2])


def black_paws(orig, cv, x, y, ramp=SKIN):
    orig(cv, x, y, BLACK if ramp is SKIN else ramp)


def straw_hat(orig, cv, cx, top, ramp=LEATHER, layer=0, crown=3, brim=6):
    h = cv.part(layer)
    r = TINT if layer else BLOND
    cv.rows(h, [(top - 2, cx - 1, cx + 1), (top - 1, cx - 3, cx + 3), (top, cx - 5, cx + 5), (top + 1, cx - 7, cx + 7)], lit(r, dark_from=cx + 3, light_to=cx - 1))
    return h


def yak(orig, cv, cx, fy, ramp=HORSE):
    def extra(cv, cx, back):
        hn = cv.part()
        cv.pix(hn, [(cx + 9, back - 6), (cx + 9, back - 7), (cx + 10, back - 8), (cx + 13, back - 6), (cx + 14, back - 7), (cx + 14, back - 8)], BONE[0])
        sh = cv.part(sep=False)                                             # shaggy coat
        cv.pix(sh, [(x, back + 6) for x in range(cx - 8, cx + 8, 2)] + [(x, back + 3) for x in range(cx - 7, cx + 8, 3)], YAK[2])
    return beast(cv, cx, fy, YAK,
                 head_rows=[(-5, 8, 14), (-4, 7, 16), (-3, 6, 17), (-2, 6, 17), (-1, 5, 16), (0, 4, 13), (1, 5, 10)],
                 tail_rows=[(1, -12, -11), (2, -12, -11), (3, -13, -11), (4, -13, -12)], eye=(14, -3), extra=extra, leg_w=4)


PANDAREN = Race("Pandaren",
                cmap={SKIN: P_FUR, HAIR: BLACK, BLOND: BLACK, HORSE: YAK, GREYH: YAK, BLACKH: YAK, STEEL: ((236, 226, 190), (196, 176, 130), (136, 114, 96))},
                rows=(("del", 4),), cols=(("dup", 3), ("dup", -3), ("dup", 2), ("dup", -2)),
                hooks={"fist": black_paws, "hair": skip, "beard": no_beard, "brim_hat": straw_hat, "horse": yak, "chanfron": skip,
                       "kettle": lambda orig, cv, cx, top, ramp=STEEL, skin=SKIN: (UH.head(cv, cx, top), straw_hat(None, cv, cx, top - 1))[0]},
                finish=pandaren_finish)

# ================================================================ KUL TIRANS
KUL_TIRANS = Race("Kul Tirans",
                  cmap={HAIR: ((170, 110, 70), (122, 74, 48), (80, 48, 40)), STEEL: ((214, 222, 226), (156, 170, 184), (96, 108, 136))},
                  rows=(("dup", 11),), cols=(("dup", 3), ("dup", -3)),
                  finish=lambda cv, cx, top: features(cv, [(cx - 3, top + 3), (cx - 3, top + 4), (cx - 3, top + 5), (cx - 2, top + 5), (cx - 2, top + 6), (cx - 1, top + 6), (cx, top + 6),
                                                           (cx + 1, top + 6), (cx + 2, top + 6), (cx + 3, top + 5)], (122, 74, 48)))

RACES = {r.name: r for r in (ORCS, NIGHT_ELVES, BLOOD_ELVES, HIGH_ELVES, NIGHTBORNE, DWARVES, DARK_IRON, TAUREN, HIGHMOUNTAIN, TROLLS, ZANDALARI,
                             GNOMES, GOBLINS, FORSAKEN, SCOURGE, DRAENEI, WORGEN, NAGA, PANDAREN, KUL_TIRANS)}


# ================================================================ loadouts the kits can dress
# The first six trial units draw their gear inline; these versions call the shared parts, so a kit can swap them.
def footman_r(cv, cx=UA.MIL_X - 1, fy=FY):
    cv.shadow(cx, 8)
    UH.sword_up(cv, cx - 9, fy - 28, fy - 13)
    UH.back_grip(cv, cx, fy, STEEL, IRON)
    UA.boots(cv, cx, fy, IRON)
    UA.legs(cv, cx, fy, STEEL)
    UH.tabard(cv, cx, fy, 2)
    UH.great_helm(cv, cx, fy - 23)
    UH.crest(cv, cx, fy - 23, 1)
    UA.pauldron(cv, cx - 8, fy - 17, STEEL)
    UA.kite(cv, cx + 1, fy - 15)


def knight_r(cv, cx=UA.MID_X - 2, fy=FY):
    cv.shadow(cx + 1, 14)
    back = UA.horse(cv, cx, fy)
    UH.caparison(cv, cx, back)
    lx = cx + 6
    UH.pole(cv, lx, 3, back - 1)
    UH.spear_head(cv, lx, 0)
    UH.pennant(cv, lx, 3, layer=2, n=7)
    ht = UH.rider(cv, cx, back)
    UH.rein_arm(cv, cx, back, STEEL)
    UH.great_helm(cv, cx, ht)
    UH.plume(cv, cx, ht, 1)
    UA.pauldron(cv, cx - 8, back - 9, STEEL)
    UA.pauldron(cv, cx + 3, back - 9, STEEL)
    UA.fist(cv, lx - 1, back - 5, IRON)


def peasant_r(cv, cx=UA.CIV_X - 1, fy=FY):
    cv.shadow(cx, 7)
    UH.hang(cv, cx - 6, fy, TAN)
    UH.base(cv, cx, fy, legs_r=LEATHER, torso_r=TAN, belt_r=IRON)
    a = cv.part()
    cv.rect(a, cx - 2, fy - 12, cx + 2, fy - 5, lit(LEATHER, dark_from=cx + 2, light_to=cx - 2, light_rows=fy - 10))
    UH.mantle(cv, cx, fy, 2)
    UA.head(cv, cx, fy - 23)
    UH.beard(cv, cx, fy - 23, HAIR)
    UH.hair(cv, cx, fy - 23, HAIR)
    tx = cx + 8
    UH.pole(cv, tx, fy - 20, fy - 1)
    p = cv.part()
    cv.rows(p, [(fy - 22, cx + 6, cx + 11), (fy - 21, cx + 5, cx + 12), (fy - 20, cx + 5, cx + 5), (fy - 20, cx + 12, cx + 13), (fy - 19, cx + 13, cx + 13)],
            lit(STEEL, dark_from=cx + 10, light_to=cx + 7, light_rows=fy - 22))
    UH.front_reach(cv, cx, fy, TAN, tx)


def archer_r(cv, cx=UA.MIL_X - 5, fy=FY):
    cv.shadow(cx + 1, 9)
    UH.quiver(cv, cx, fy)
    UH.cape(cv, cx, fy, 2)
    UH.base(cv, cx, fy, legs_r=TAN, torso_r=LEATHER)
    UH.hood(cv, cx, fy - 23, 2)
    UH.bow(cv, cx, fy - 13, sleeve=LEATHER)


def priest_r(cv, cx=UA.CIV_X + 1, fy=FY):
    cv.shadow(cx, 8)
    UH.robe(cv, cx, fy, WHITE)
    UH.robe_trim(cv, cx, fy, 1)
    UA.arm(cv, cx - 6, fy - 14, WHITE, length=5)
    UH.mantle(cv, cx, fy, 2, clasp=None)
    UA.head(cv, cx, fy - 23)
    UH.hair(cv, cx, fy - 23, BLOND)
    tx = cx + 9
    UH.pole(cv, tx, fy - 22, fy, GOLD)
    s = cv.part()
    cv.rows(s, [(fy - 27, tx - 1, tx + 1), (fy - 26, tx - 2, tx + 2), (fy - 25, tx - 2, tx + 2), (fy - 24, tx - 2, tx + 2), (fy - 23, tx - 1, tx + 1)], lit(GLOW, dark_from=tx + 2, light_to=tx))
    r = cv.part()
    cv.pix(r, [(tx, fy - 29), (tx - 4, fy - 25), (tx + 4, fy - 25), (tx - 3, fy - 28), (tx + 3, fy - 28)], GLOW[1])
    UH.front_reach(cv, cx, fy, WHITE, tx)


ALT = {"Footman": footman_r, "Knight": knight_r, "Peasant": peasant_r, "Archer": archer_r, "Priest": priest_r}
# Units with no Human-named sprite of their own: which loadout they wear.
EXTRA = {"Swordsman": footman_r, "Great Scientist": UH.archmage, "Missionary": UH.cleric, "Warlock": UH.magus, "Fel Initiate": UH.magus,
         "Demonologist": UH.magus, "Grand Warlock": UH.archmage, "Grand Champion": UH.man_at_arms}
# Kept as they are for the other races: ships, machines and airships (a recolour of the Human one would not be the race's own design).
KEEP = NO_BODY | {"Fishing Skiff", "Longboat", "Brigantine", "Buccaneer", "War Galley", "Frigate", "Ironclad", "Destroyer", "Dreadnought", "Juggernaught"}
_L = {"Swordsman": footman_r, "Vanguard": UH.vanguard, "Outrider": UH.outrider, "Hunter": UH.hunter, "Knight": knight_r, "Cavalry": UH.silver_hand,
      "Rifleman": UH.rifleman, "Mountaineer": UH.mountaineer, "Man-at-Arms": UH.man_at_arms, "Pikeman": UH.pikeman, "Ranger": UH.ranger,
      "Ranger Captain": UH.ranger_captain, "Cleric": UH.cleric, "Warbringer": UH.warbringer, "Champion": UM.lightbringer,
      "Marksman": UH.ranger_general, "Arcane": UH.archmage, "Heavy": UH.gladiator, "Archer": UH.hunter}
# Each race's own units that are people (monsters, machines and ships keep their art): (race, loadout of the unit they replace).
UNIQUES = {
    "Grunt": ("Orcs", "Swordsman"), "Wolf Rider": ("Orcs", "Outrider"), "Raider": ("Orcs", "Cavalry"), "Earthen Shaman": ("Orcs", "Cleric"),
    "Headhunter": ("Trolls", "Hunter"), "Troll Berserker": ("Trolls", "Man-at-Arms"), "Witch Doctor": ("Trolls", "Cleric"),
    "Tauren Warrior": ("Tauren", "Vanguard"), "Sunwalker": ("Tauren", "Cleric"),
    "Spellbreaker": ("Blood Elves", "Swordsman"), "Blood Knight": ("Blood Elves", "Knight"), "Sunfury Priest": ("Blood Elves", "Cleric"),
    "Ironforge Rifleman": ("Dwarves", "Rifleman"), "Ram Rider": ("Dwarves", "Knight"), "Dwarven Priest": ("Dwarves", "Cleric"),
    "Mechagnome Trooper": ("Gnomes", "Warbringer"), "Mechanostrider Rider": ("Gnomes", "Outrider"), "Decontaminator": ("Gnomes", "Cleric"),
    "Huntress": ("Night Elves", "Outrider"), "Cenarion Druid": ("Night Elves", "Cleric"),
    "Vindicator": ("Draenei", "Vanguard"), "Elekk Rider": ("Draenei", "Knight"), "Anchorite": ("Draenei", "Cleric"),
    "Worgen Stalker": ("Worgen", "Swordsman"), "Gilnean Rifleman": ("Worgen", "Mountaineer"), "Gilnean Hunter": ("Worgen", "Archer"),
    "Worgen Ravager": ("Worgen", "Heavy"), "Harvest Witch": ("Worgen", "Cleric"),
    "Farstrider": ("High Elves", "Hunter"), "Ranger-Lord": ("High Elves", "Ranger Captain"), "Lightwarden": ("High Elves", "Cleric"),
    "Brewmaster": ("Pandaren", "Vanguard"), "Shado-Pan Monk": ("Pandaren", "Pikeman"), "Mistweaver": ("Pandaren", "Cleric"),
    "Death Knight": ("Scourge", "Knight"), "Deathstalker": ("Forsaken", "Ranger Captain"),
    "Fireguard": ("Dark Iron Dwarves", "Pikeman"), "Flamekeeper": ("Dark Iron Dwarves", "Cleric"),
    "Admiralty Gunner": ("Kul Tirans", "Rifleman"), "Tidesage": ("Kul Tirans", "Cleric"),
    "Raptor Rider": ("Zandalari Trolls", "Outrider"), "Direhorn Rider": ("Zandalari Trolls", "Knight"), "Loa Speaker": ("Zandalari Trolls", "Cleric"),
    "Myrmidon": ("Naga", "Swordsman"), "Tidepriestess": ("Naga", "Cleric"),
    "Spellblade": ("Nightborne", "Vanguard"), "Duskwatch Sentinel": ("Nightborne", "Ranger"), "Shal'dorei Mender": ("Nightborne", "Cleric"),
    "Highmountain Warbrave": ("Highmountain Tauren", "Man-at-Arms"), "Thunderhoof Rider": ("Highmountain Tauren", "Knight"),
    "Spiritwalker": ("Highmountain Tauren", "Cleric"), "Hazmat Crew": ("Goblins", "Cleric"),
    # heroes: the race's champion, marksman or mage in its own kit (no likeness of the named character)
    "Grom Hellscream": ("Orcs", "Champion"), "Malfurion Stormrage": ("Night Elves", "Arcane"), "Muradin Bronzebeard": ("Dwarves", "Champion"),
    "Kelsey Steelspark": ("Gnomes", "Champion"), "Baine Bloodhoof": ("Tauren", "Champion"), "Rokhan": ("Trolls", "Marksman"),
    "Kael'thas Sunstrider": ("Blood Elves", "Arcane"), "Alleria Windrunner": ("High Elves", "Marksman"), "Chen Stormstout": ("Pandaren", "Champion"),
    "Nathanos Blightcaller": ("Forsaken", "Marksman"), "Maraad": ("Draenei", "Champion"), "Gazlowe": ("Goblins", "Champion"),
    "Darius Crowley": ("Worgen", "Champion"), "Dagran Thaurissan": ("Dark Iron Dwarves", "Champion"), "Daelin Proudmoore": ("Kul Tirans", "Champion"),
    "Rastakhan": ("Zandalari Trolls", "Arcane"), "Lady Vashj": ("Naga", "Arcane"), "Grand Magistrix Elisande": ("Nightborne", "Arcane"),
    "Huln Highmountain": ("Highmountain Tauren", "Champion"), "Kel'Thuzad": ("Scourge", "Arcane"),
    "Wisp": ("Night Elves", None),
}
MOUNTED |= {"Wolf Rider", "Raider", "Blood Knight", "Ram Rider", "Mechanostrider Rider", "Huntress", "Elekk Rider", "Death Knight", "Raptor Rider",
            "Direhorn Rider", "Thunderhoof Rider"} | {k for k, (r, l) in UNIQUES.items() if l == "Champion"}

for _b, _f in EXTRA.items():                                               # the Humans get these too
    UA.SPRITES.setdefault(_b + "-Humans", _f)


def jobs():
    """Every (file stem, loadout, race, name used for the build rules) the kits draw."""
    out = []
    for key, fn in list(UA.SPRITES.items()):
        if not key.endswith("-Humans"):
            continue
        b = key[:-7]
        if b in KEEP:
            continue
        for race in RACES.values():
            out.append(("%s-%s" % (b, race.name), ALT.get(b, fn), race, b))
    for stem, (rn, lo) in UNIQUES.items():
        fn = wisp if lo is None else _L[lo]
        out.append((stem, fn, RACES[rn], "Peasant" if lo is None else (stem if stem in MOUNTED else lo)))
    return out


def write_all(image_dirs, unit_dir="TileSets/AbsoluteUnits/Units/"):
    import os
    index = {}
    for d in image_dirs:
        folder = os.path.join(d, unit_dir)
        if not os.path.isdir(folder):
            continue
        for fname in os.listdir(folder):
            stem = fname[:-4]
            if stem.endswith("-1") or stem.endswith("-2"):
                continue
            base = stem.split("-Age of")[0]
            index.setdefault(base, []).append((folder, stem))
    count = 0
    for stem, fn, race, rule in jobs():
        if stem not in index:
            continue
        layers = render(fn, race, rule)
        for folder, s in index[stem]:
            for suf, im in zip(("", "-1", "-2"), layers):
                im.save(os.path.join(folder, s + suf + ".png"))
                count += 1
    return count


_human_write = UA.write_all


def _write_everything(image_dirs, unit_dir="TileSets/AbsoluteUnits/Units/"):
    """unit_art.write_all, then the same loadouts on every other race."""
    n = _human_write(image_dirs, unit_dir)
    m = write_all(image_dirs, unit_dir)
    print("race-kit unit sprites:", m)
    return n + m


UA.write_all = _write_everything
