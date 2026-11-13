"""City centers and tile improvements for every other faction, in the hand-placed style.

The scenes are the ones drawn in tile_art_humans.py; a faction changes what they are built from and how
the buildings are shaped: its own wall, roof, stone and ground colours, its own roof form (spiked hall,
hide tent, thatch, leaf canopy, stone slab, dome, onion dome, spire, pagoda, scrap roof) and tower cap.
Colours and forms come from the faction styles in citycenters.STYLES. All designs are original.
"""
import contextlib

import citycenters as CC
import tile_art_humans as TH
from tile_art_humans import ell_rows

BONE = ((246, 238, 212), (212, 198, 164), (152, 138, 122))


def ramp(c, hi=1.2, lo=0.66):
    return (tuple(min(255, int(v * hi + 8)) for v in c), tuple(c), tuple(int(v * lo) for v in c))


def cmap_for(st):
    m = {}
    def put(src, dst):
        for a, b in zip(src, dst):
            m[tuple(a)] = tuple(b)
    put(TH.PLASTER, ramp(st["wall"]))
    put(TH.SLATE, ramp(st["roof"]))
    put(TH.STONE, ramp(st["stone"]))
    put(TH.PAVE, ramp(st["ground"], 1.1, 0.8))
    put(TH.TIMBER, ramp(st["trim"]) if st.get("trim") else ramp(tuple(int(v * 0.6) for v in st["wall"])))
    m[TH.GLOW] = tuple(st["win"])
    m[(226, 170, 84)] = tuple(int(v * 0.8) for v in st["win"])
    return m


_roof, _gable, _tower = TH.roof, TH.gable_roof, TH.tower
S = TH.SLATE


def _shade(x0, x1, top, eave):
    def f(xx, yy):
        if yy == eave or xx >= x1 - 1:
            return S[2]
        if yy == top or xx <= x0 + 1:
            return S[0]
        return S[2] if (xx + 2 * yy) % 5 == 0 else S[1]
    return f


def roof_kind(kind):
    def roof(cv, x, eave, w, h, ramp=None):
        cx = x + w // 2
        if kind in ("gable", "hip"):
            return _roof(cv, x, eave, w, h)
        if kind == "spiky":                                               # pitched hall with tusks at both ends
            top = _roof(cv, x, eave, w, h)
            t = cv.part()
            cv.pix(t, [(x + h - 2, top - 1), (x + h - 3, top - 2), (x + h - 3, top - 3), (x + w - h + 1, top - 1), (x + w - h + 2, top - 2), (x + w - h + 2, top - 3)], BONE[0])
            cv.pix(t, [(cx, top - 1)], BONE[1])
            return top - 3
        if kind in ("dome", "leaf", "onion"):
            r = cv.part()
            hh = h + (2 if kind != "dome" else 1)
            rows = ell_rows(cx, eave, w // 2 + 1, hh, top_only=True)
            cv.rows(r, rows, _shade(x - 1, x + w, eave - hh, eave))
            d = cv.part(sep=False)
            top = eave - hh
            if kind == "leaf":
                cv.pix(d, [(x + 2 + i * 3, eave - 2 - (i % 2)) for i in range((w - 2) // 3)], S[0])
                e = cv.part()
                cv.pix(e, [(x - 2, eave - 1), (x - 3, eave - 2), (x + w + 1, eave - 1), (x + w + 2, eave - 2)], S[1])
            if kind == "onion":
                o = cv.part()
                cv.pix(o, [(cx, top - 1), (cx, top - 2), (cx, top - 3)], TH.GOLD[0])
                cv.rect(o, cx - 1, top - 1, cx + 1, top - 1, S[0])
                top -= 3
            else:
                cv.put(d, cx, top, TH.GOLD[0])
            return top
        if kind == "tent":                                                # hide tent: cone with crossed poles
            r = cv.part()
            hh = max(h + 2, w // 2)
            rows = [(eave - hh + 1 + k, cx - (k * (w // 2 + 1)) // (hh - 1), cx + (k * (w // 2 + 1)) // (hh - 1)) for k in range(hh)]
            cv.rows(r, rows, lambda xx, yy: S[2] if yy == eave else (S[0] if xx < cx else (S[1] if xx < cx + 3 else S[2])))
            b = cv.part(sep=False)
            y = eave - hh // 2
            cv.pix(b, [(xx, y) for (yy, a, c) in rows if yy == y for xx in range(a, c + 1)], TH.RED[1])
            p = cv.lines()
            top = eave - hh + 1
            cv.pix(p, [(cx - 1, top - 1), (cx - 2, top - 2), (cx + 1, top - 1), (cx + 2, top - 2)], TH.WOOD[2])
            return top - 2
        if kind == "thatch":                                              # steep thatch with a ragged eave
            top = _roof(cv, x, eave, w, h + 1)
            g = cv.part()
            cv.pix(g, [(xx, eave + 1) for xx in range(x - 1, x + w + 1, 2)], S[2])
            return top
        if kind == "flat":                                                # stone slab with blocks along the top
            r = cv.part()
            top = eave - max(2, h - 2)
            cv.rect(r, x - 1, top, x + w, eave, lambda xx, yy: S[0] if yy == top else (S[2] if yy == eave or xx >= x + w - 1 else S[1]))
            m = cv.part()
            cv.pix(m, [(xx, top - 1) for xx in range(x - 1, x + w + 1) if (xx - x) % 4 < 2], S[0])
            t = cv.part(sep=False)
            cv.rect(t, x, eave - 1, x + w - 1, eave - 1, TH.GOLD[1])
            return top - 1
        if kind == "spire":                                               # tall narrow roof
            r = cv.part()
            hh = h + 4
            rows = [(eave - hh + 1 + k, cx - (k * (w // 2 + 1)) // (hh - 1), cx + (k * (w // 2 + 1)) // (hh - 1)) for k in range(hh)]
            cv.rows(r, rows, lambda xx, yy: S[2] if yy == eave else (S[0] if xx < cx else (S[1] if xx < cx + 2 else S[2])))
            f = cv.lines()
            cv.pix(f, [(cx, eave - hh), (cx, eave - hh - 1)], TH.GOLD[0])
            return eave - hh - 1
        if kind == "pagoda":                                              # two tiers, eaves turned up
            top = _roof(cv, x, eave, w, max(3, h - 1))
            u = cv.part()
            cv.pix(u, [(x - 2, eave - 1), (x - 3, eave - 2), (x + w + 1, eave - 1), (x + w + 2, eave - 2)], S[0])
            r2 = cv.part()
            cv.rows(r2, [(top - 3, cx - 1, cx + 1), (top - 2, cx - 3, cx + 3), (top - 1, cx - 5, cx + 5)], lambda xx, yy: S[2] if yy == top - 1 else (S[0] if xx < cx else S[1]))
            cv.pix(r2, [(cx - 6, top - 2), (cx + 6, top - 2)], S[0])
            return top - 3
        if kind == "slab":                                                # scrap roof, one slope, with a stove pipe
            r = cv.part()
            rows = [(eave - k, x - 1, x + w - k * 2) for k in range(h)]
            cv.rows(r, rows, lambda xx, yy: S[2] if yy == eave else (S[0] if (xx - x) % 6 < 3 else S[1]))
            d = cv.part(sep=False)
            cv.pix(d, [(x + 1 + i * 4, eave - 1) for i in range(w // 4)], TH.IRON[2])
            p = cv.part()
            cv.rect(p, x + 2, eave - h - 3, x + 3, eave - h + 1, TH.IRON[1])
            return eave - h - 3
        return _roof(cv, x, eave, w, h)
    return roof


def tower_kind(kind):
    def tower(cv, x, foot, w, h, cap="cone", ramp=TH.STONE, slit=True, cone_ramp=TH.SLATE):
        if kind in ("flat", "slab"):
            return _tower(cv, x, foot, w, h, cap="flat", slit=slit)
        top = _tower(cv, x, foot, w, h, cap=cap, slit=slit)
        if kind == "spiky" and cap == "cone":
            t = cv.part()
            cv.pix(t, [(x - 2, foot - h - 1), (x - 3, foot - h - 2), (x + w + 1, foot - h - 1), (x + w + 2, foot - h - 2)], BONE[0])
        return top
    return tower


@contextlib.contextmanager
def ctx(race):
    st = CC.STYLES[race]
    saved = (TH.TC.cmap, TH.roof, TH.gable_roof, TH.tower)
    TH.TC.cmap = cmap_for(st)
    kind = st["house"]
    TH.roof = roof_kind(kind)
    if kind not in ("gable", "hip"):
        big = st["big"]
        TH.gable_roof = lambda cv, x, eave, w, ramp=None: roof_kind(big)(cv, x, eave, w, min(7, w // 2))
    TH.tower = tower_kind(st["tower_roof"])
    try:
        yield
    finally:
        TH.TC.cmap, TH.roof, TH.gable_roof, TH.tower = saved


def install():
    TH.HANDLED |= {k for k in CC.STYLES if k != "Humans"}
    human = TH.CTX
    TH.CTX = lambda race: human(race) if race == "Humans" else ctx(race)



# ================================================================ faction landmarks (the heart of each city center)
OY, CXC = TH.OY, TH.CX
F = OY + 26                                  # ground row of the landmark
LEAFY = ((150, 210, 120), (96, 160, 90), (58, 108, 80))
BARKY = ((160, 124, 92), (116, 86, 66), (76, 56, 50))
VIOLET = ((236, 214, 255), (190, 146, 244), (124, 88, 196))
AQUA = ((214, 250, 255), (120, 214, 236), (60, 140, 190))
LAVA = ((255, 236, 150), (255, 150, 50), (210, 70, 40))
FELG = ((210, 255, 140), (140, 226, 80), (76, 146, 66))
ICE = ((236, 248, 255), (170, 214, 244), (100, 150, 206))
SUN = ((255, 248, 190), (255, 214, 96), (226, 150, 60))
GOLDR = TH.GOLD
ST, RF, WL = TH.STONE, TH.SLATE, TH.PLASTER


def _block(cv, x0, y0, x1, y1, r=ST, sep=True):
    p = cv.part(sep=sep) if sep else cv.part(sep=False)
    cv.rect(p, x0, y0, x1, y1, TH.tone(r, x0, x1, top=y0))
    return p


def _glow(cv, pts, c):
    g = cv.part(sep=False)
    cv.pix(g, pts, c)


def great_hall(cv, stage):
    """Orcs: a long spiked hall between two great tusks, watchtowers at its ends."""
    e = stage - 1
    for x, d in ((CXC - 15, 1), (CXC + 15, -1)):
        t = cv.part()
        cv.pix(t, [(x, F), (x, F - 1), (x, F - 2), (x + d, F - 3), (x + d, F - 4), (x + d, F - 5), (x + 2 * d, F - 6), (x + 2 * d, F - 7), (x + 3 * d, F - 8), (x + 4 * d, F - 9)], BONE[1])
        cv.pix(t, [(x + 1 if d > 0 else x - 1, F), (x + 1 if d > 0 else x - 1, F - 1), (x + 2 * d, F - 4), (x + 3 * d, F - 7)], BONE[0])
    if stage == 2:
        TH.tower(cv, CXC - 3, F - 6, 7, 20)
    top = TH.house(cv, CXC - 10, F, 21, wall=6 + e, rh=7, chim=False, windows=False)
    _glow(cv, [(CXC - 6, F - 3), (CXC - 5, F - 3), (CXC + 5, F - 3), (CXC + 6, F - 3)], LAVA[1])
    TH.flag(cv, CXC, top + 1, 6, ramp=TH.RED)


def totem_rise(cv, stage):
    """Tauren: a great lodge under a tall carved totem with spread wings."""
    e = stage - 1
    TH.barn(cv, CXC - 10, F, 15, wall=5 + e, windows=False)
    x = CXC + 9
    h = 20 + 4 * e
    for k in range(h // 5):
        y1 = F - k * 5
        _block(cv, x - 2, y1 - 4, x + 2, y1, BARKY)
        _glow(cv, [(x - 1, y1 - 3), (x + 1, y1 - 3)], (40, 30, 30))
        _glow(cv, [(x - 1, y1 - 1), (x, y1 - 1), (x + 1, y1 - 1)], TH.RED[1] if k % 2 else AQUA[1])
    top = F - (h // 5) * 5
    w = cv.part()
    cv.rows(w, [(top + 2, x - 8, x - 3), (top + 3, x - 6, x - 3), (top + 2, x + 3, x + 8), (top + 3, x + 3, x + 6)], TH.tone(BARKY, x - 8, x + 8))
    hd = cv.part()
    cv.pix(hd, [(x - 2, top), (x - 3, top - 1), (x + 2, top), (x + 3, top - 1)], BONE[0])
    if stage == 2:
        TH.barn(cv, CXC - 1, F + 1, 9, wall=3, windows=False)


def ziggurat(gold=False):
    """Trolls: a stepped temple with a stair up the front and torches at the top."""
    def f(cv, stage):
        steps = 3 + (stage - 1)
        w = 24 + 4 * (stage - 1)
        y = F
        for k in range(steps):
            x0 = CXC - w // 2 + k * 3
            x1 = CXC + w // 2 - k * 3
            _block(cv, x0, y - 4, x1, y)
            y -= 5
        st = cv.part(sep=False)
        cv.rect(st, CXC - 1, y + 1, CXC + 1, F, ST[2])
        cv.pix(st, [(CXC, yy) for yy in range(y + 2, F, 2)], ST[0])
        sh = TH.house(cv, CXC - 4, y, 9, wall=3, rh=4, chim=False, windows=False)
        if gold:
            g = cv.part(sep=False)
            cv.rect(g, CXC - 4, y, CXC + 4, y, GOLDR[1])
        for x in (CXC - 7, CXC + 7):
            p = cv.lines()
            cv.rect(p, x, y - 3, x, y, TH.TIMBER[1])
            fl = cv.part()
            cv.pix(fl, [(x, y - 4), (x, y - 5)], LAVA[1])
    return f


def world_tree(cv, stage):
    """Night Elves: a great tree with halls among its roots and a moonwell at its foot."""
    e = stage - 1
    h = 20 + 5 * e
    tr = cv.part()
    cv.rows(tr, [(F - k, CXC - 3 - (1 if k < 3 else 0), CXC + 3 + (1 if k < 3 else 0)) for k in range(h)], TH.tone(BARKY, CXC - 3, CXC + 3))
    d = cv.part(sep=False)
    cv.rows(d, [(F - 4, CXC - 1, CXC + 1), (F - 3, CXC - 1, CXC + 1), (F - 2, CXC - 1, CXC + 1), (F - 1, CXC - 1, CXC + 1)], (40, 30, 44))
    cv.pix(d, [(CXC, F - 8), (CXC, F - 12)], AQUA[0])
    top = F - h
    r = 12 + 2 * e
    c = cv.part()
    rows = ell_rows(CXC, top + 2, r, 7 + e)
    cv.rows(c, rows, lambda x, y: RF[0] if (x - CXC) + 2 * (y - top) < -6 else (RF[2] if x > CXC + r - 4 or y > top + 5 else RF[1]))
    m = cv.part(sep=False)
    cv.pix(m, [(CXC - 7 + i * 4, top + (i % 3)) for i in range(5)], RF[0])
    cv.pix(m, [(CXC - 5 + i * 5, top + 5) for i in range(3)], AQUA[0])
    w = cv.part()
    cv.rows(w, ell_rows(CXC - 11, F, 3, 1), TH.tone(ST, CXC - 14, CXC - 8))
    _glow(cv, [(CXC - 12, F), (CXC - 11, F), (CXC - 10, F)], AQUA[0])
    TH.house(cv, CXC + 6, F, 9, wall=3, rh=3, chim=False)


def high_spire(orb, domes=False):
    """Elven kingdoms: a soaring central spire with a floating orb, lesser spires beside it."""
    def f(cv, stage):
        e = stage - 1
        for x in (CXC - 13, CXC + 7):
            TH.tower(cv, x, F + 1, 7, 13 + 2 * e)
        top = TH.tower(cv, CXC - 4, F, 9, 22 + 4 * e)
        o = cv.part()
        cv.rows(o, [(top - 4, CXC - 1, CXC + 1), (top - 3, CXC - 1, CXC + 1), (top - 2, CXC - 1, CXC + 1)], lambda x, y: orb[0] if x <= CXC else orb[1])
        _glow(cv, [(CXC - 4, top - 5), (CXC + 4, top - 2)], orb[0])
        d = cv.part(sep=False)
        cv.rows(d, [(F - 4, CXC - 1, CXC + 1)] + [(yy, CXC - 2, CXC + 2) for yy in range(F - 3, F + 1)], (44, 32, 40))
        cv.rect(d, CXC - 4, F - 12, CXC + 4, F - 12, GOLDR[1])
        if domes:
            TH.house(cv, CXC - 12, F + 3, 9, wall=3, rh=4, chim=False)
    return f


def mountain_gate(fire):
    """Dwarves: a gate cut into a mountain face, a forge burning inside, an anvil before it."""
    def f(cv, stage):
        e = stage - 1
        mt = cv.part()
        rows = [(F - k, CXC - 15 + k // 2, CXC + 15 - k // 2) for k in range(20 + 4 * e)]
        cv.rows(mt, rows, lambda x, y: TH.ROCK[0] if (x - CXC) * 2 + (y - F) < -30 else (TH.ROCK[2] if x > CXC + 6 else TH.ROCK[1]))
        sn = cv.part(sep=False)
        ty = F - (20 + 4 * e) + 1
        cv.rows(sn, [(ty, CXC - 15 + (F - ty) // 2, CXC + 15 - (F - ty) // 2), (ty + 1, CXC - 3, CXC + 2)], (240, 244, 250))
        _block(cv, CXC - 8, F - 13 - e, CXC + 8, F)
        g = cv.part(sep=False)
        cv.rows(g, [(F - 9, CXC - 2, CXC + 2)] + [(yy, CXC - 3, CXC + 3) for yy in range(F - 8, F + 1)], (40, 30, 36))
        cv.rect(g, CXC - 1, F - 4, CXC + 1, F - 1, fire[1])
        cv.rect(g, CXC, F - 3, CXC, F - 2, fire[0])
        cv.rect(g, CXC - 8, F - 12 - e, CXC + 8, F - 12 - e, GOLDR[1])
        for x in (CXC - 7, CXC + 5):
            cv.rect(g, x, F - 9, x + 2, F, ST[2])
            cv.rect(g, x, F - 9, x + 2, F - 9, ST[0])
        a = cv.part()
        cv.rows(a, [(F + 3, CXC - 13, CXC - 9), (F + 4, CXC - 12, CXC - 10), (F + 5, CXC - 13, CXC - 9)], TH.tone(TH.IRON, CXC - 13, CXC - 9))
    return f


def gear_tower(cv, stage):
    """Gnomes: a riveted tower crowned by a turning cog, pipes venting steam."""
    e = stage - 1
    top = TH.tower(cv, CXC - 4, F, 9, 18 + 4 * e, cap="flat")
    cy = top - 5
    c = cv.part()
    cv.rows(c, ell_rows(CXC, cy, 5, 5), lambda x, y: GOLDR[0] if x < CXC - 1 else (GOLDR[2] if x > CXC + 2 else GOLDR[1]))
    t = cv.part()
    cv.pix(t, [(CXC, cy - 6), (CXC, cy + 6), (CXC - 6, cy), (CXC + 6, cy), (CXC - 4, cy - 4), (CXC + 4, cy - 4), (CXC - 4, cy + 4), (CXC + 4, cy + 4)], GOLDR[1])
    _glow(cv, [(CXC - 1, cy), (CXC, cy), (CXC + 1, cy), (CXC, cy - 1), (CXC, cy + 1)], (60, 50, 60))
    TH.house(cv, CXC - 14, F + 1, 9, wall=3, rh=4, chim=False)
    p = cv.part()
    cv.rect(p, CXC + 8, F - 12, CXC + 9, F, TH.tone(TH.IRON, CXC + 8, CXC + 9, lw=1))
    s = cv.part()
    cv.rows(s, [(F - 16, CXC + 9, CXC + 12), (F - 15, CXC + 8, CXC + 12), (F - 14, CXC + 8, CXC + 10)], (232, 234, 240))


def derrick(cv, stage):
    """Goblins: a pumping derrick, a smoking stack and a big gaudy sign."""
    e = stage - 1
    h = 20 + 4 * e
    d = cv.lines()
    for k in range(0, h, 4):
        y = F - k
        w = 5 - k * 4 // h
        cv.pix(d, TH.line(CXC - w, y, CXC + w, y - 4) + TH.line(CXC + w, y, CXC - w, y - 4), TH.IRON[1])
    lg = cv.part()
    cv.pix(lg, TH.line(CXC - 6, F, CXC - 1, F - h) + TH.line(CXC + 6, F, CXC + 1, F - h), TH.IRON[0])
    _block(cv, CXC - 2, F - h - 3, CXC + 2, F - h, TH.IRON)
    stx = CXC + 10
    s = cv.part()
    cv.rect(s, stx, F - 16 - 2 * e, stx + 3, F, TH.tone(RF, stx, stx + 3, lw=1))
    sm = cv.part()
    cv.rows(sm, [(F - 21 - 2 * e, stx + 2, stx + 6), (F - 20 - 2 * e, stx + 1, stx + 6), (F - 19 - 2 * e, stx + 1, stx + 4), (F - 18 - 2 * e, stx + 1, stx + 3)], (200, 200, 208))
    TH.house(cv, CXC - 16, F + 1, 11, wall=4, rh=4, chim=False)
    sg = cv.part()
    cv.rect(sg, CXC - 15, F - 13, CXC - 7, F - 9, TH.tone(GOLDR, CXC - 15, CXC - 7))
    _glow(cv, [(CXC - 13, F - 11), (CXC - 11, F - 11), (CXC - 9, F - 11)], TH.RED[1])


def crystal_spire(col, dome=True):
    """Draenei / Naga: a great crystal (or coral spire) on a dais, domed halls beside it."""
    def f(cv, stage):
        e = stage - 1
        _block(cv, CXC - 9, F - 3, CXC + 9, F)
        h = 20 + 5 * e
        c = cv.part()
        rows = []
        for k in range(h):
            y = F - 4 - k
            hw = min(4, k // 2 + 1, (h - k + 1) // 2)
            rows.append((y, CXC - hw, CXC + hw))
        cv.rows(c, rows, lambda x, y: col[0] if x < CXC - 1 else (col[2] if x > CXC + 1 else col[1]))
        _glow(cv, [(CXC - 1, F - 8), (CXC - 1, F - 9), (CXC, F - 14), (CXC - 6, F - 12), (CXC + 6, F - 16), (CXC + 5, F - 8)], col[0])
        for x, hh in ((CXC - 13, 9), (CXC + 9, 7 + 2 * e)):
            s = cv.part()
            cv.rows(s, [(F + 1 - k, x + 2 - min(2, k // 2, (hh - k) // 2), x + 2 + min(2, k // 2, (hh - k) // 2)) for k in range(hh)], lambda xx, yy: col[0] if xx <= x + 1 else col[2])
        if dome:
            TH.house(cv, CXC - 16, F + 4, 9, wall=3, rh=4, chim=False)
    return f


def ruined_cathedral(glow):
    """Forsaken / Worgen: a tall cathedral tower; the Forsaken one is broken and glows from below."""
    def f(cv, stage):
        e = stage - 1
        top = TH.house(cv, CXC - 12, F, 15, wall=7 + e, rh=6, chim=False, timber=False, windows=False)
        _glow(cv, [(CXC - 9, F - 4), (CXC - 9, F - 5), (CXC - 5, F - 4), (CXC - 5, F - 5), (CXC - 1, F - 4), (CXC - 1, F - 5)], glow[1])
        t = TH.tower(cv, CXC + 3, F, 9, 22 + 4 * e)
        c = cv.part(sep=False)                                              # clock or rose window
        cv.rows(c, ell_rows(CXC + 7, F - 15 - 2 * e, 2, 2), glow[0])
        cv.pix(c, [(CXC + 7, F - 15 - 2 * e), (CXC + 7, F - 16 - 2 * e), (CXC + 8, F - 15 - 2 * e)], (50, 40, 50))
        cv.rows(c, [(F - 4, CXC + 6, CXC + 8)] + [(yy, CXC + 5, CXC + 9) for yy in range(F - 3, F + 1)], (44, 34, 44))
        if glow is FELG:
            g = cv.part()
            cv.rows(g, ell_rows(CXC - 14, F + 5, 3, 1), FELG[1])
            _glow(cv, [(CXC - 15, F + 5), (CXC - 13, F + 5)], FELG[0])
    return f


def ice_citadel(cv, stage):
    """Scourge: a jagged citadel of dark metal and ice, lit cold blue."""
    e = stage - 1
    for x, h in ((CXC - 13, 14), (CXC + 8, 16), (CXC - 6, 22 + 3 * e), (CXC + 2, 26 + 4 * e)):
        s = cv.part()
        rows = [(F - k, x + min(2, k * 3 // h), x + 5 - min(2, k * 3 // h) - (1 if k > h - 4 else 0)) for k in range(h)]
        cv.rows(s, rows, lambda xx, yy, x=x: ST[0] if xx <= x + 1 else (ST[2] if xx >= x + 4 else ST[1]))
        ic = cv.part()
        cv.pix(ic, [(x + 2, F - h), (x + 2, F - h - 1), (x + 3, F - h)], ICE[0])
        _glow(cv, [(x + 2, F - h // 2), (x + 2, F - h // 2 - 1), (x + 3, F - 3)], AQUA[1])
    _block(cv, CXC - 9, F - 6, CXC + 9, F)
    d = cv.part(sep=False)
    cv.rows(d, [(F - 4, CXC - 1, CXC + 1)] + [(yy, CXC - 2, CXC + 2) for yy in range(F - 3, F + 1)], (30, 34, 50))
    cv.pix(d, [(CXC, F - 2), (CXC, F - 1)], AQUA[0])
    ch = cv.lines()
    cv.pix(ch, TH.line(CXC - 9, F - 14, CXC - 4, F - 10) + TH.line(CXC + 9, F - 15, CXC + 5, F - 11), TH.IRON[0])


def lighthouse(cv, stage):
    """Kul Tirans: a harbour lighthouse over the admiralty hall, a crane on the quay."""
    e = stage - 1
    TH.house(cv, CXC - 13, F, 15, wall=6 + e, rh=5, chim=True)
    top = TH.tower(cv, CXC + 4, F, 7, 20 + 4 * e, cap="flat")
    l = cv.part()
    cv.rect(l, CXC + 5, top - 4, CXC + 9, top - 1, lambda x, y: SUN[0] if x < CXC + 8 else SUN[1])
    r = cv.part()
    cv.rows(r, [(top - 7, CXC + 7, CXC + 7), (top - 6, CXC + 6, CXC + 8), (top - 5, CXC + 4, CXC + 10)], lambda x, y: RF[0] if x < CXC + 7 else RF[2])
    b = cv.lines()
    cv.pix(b, [(CXC + 11, top - 3), (CXC + 12, top - 3), (CXC + 13, top - 4), (CXC + 3, top - 3), (CXC + 2, top - 4)], SUN[0])
    st = cv.part(sep=False)
    for yy in range(F - 4, top + 2, -6):
        cv.rect(st, CXC + 4, yy - 1, CXC + 10, yy, TH.RED[1])


def pagoda_temple(cv, stage):
    """Pandaren: a temple of stacked roofs, lanterns at its door."""
    tiers = 2 + stage
    y = F
    w = 19
    for k in range(tiers):
        x = CXC - w // 2
        TH.walls(cv, x + 1, y, w - 2, 4, timber=False, door=(k == 0), windows=False, footing=(k == 0))
        TH.roof(cv, x, y - 4, w, 3)
        y -= 7
        w -= 4
    f = cv.lines()
    cv.pix(f, [(CXC, y + 2), (CXC, y + 1), (CXC, y)], GOLDR[0])
    for x in (CXC - 12, CXC + 12):
        p = cv.lines()
        cv.rect(p, x, F - 5, x, F, TH.TIMBER[1])
        l = cv.part()
        cv.rect(l, x - 1, F - 8, x + 1, F - 6, lambda xx, yy: SUN[1] if xx <= x else TH.RED[1])


LANDMARK = {
    "Orcs": great_hall, "Tauren": totem_rise, "Highmountain Tauren": totem_rise, "Trolls": ziggurat(), "Zandalari Trolls": ziggurat(gold=True),
    "Night Elves": world_tree, "High Elves": high_spire(AQUA), "Blood Elves": high_spire(SUN), "Nightborne": high_spire(VIOLET, domes=True),
    "_dalaran": high_spire(VIOLET), "Dwarves": mountain_gate(LAVA), "Dark Iron Dwarves": mountain_gate(LAVA), "Gnomes": gear_tower, "Goblins": derrick,
    "Draenei": crystal_spire(VIOLET), "Naga": crystal_spire(((255, 190, 200), (236, 120, 150), (160, 70, 110)), dome=False),
    "Forsaken": ruined_cathedral(FELG), "Worgen": ruined_cathedral(SUN), "Scourge": ice_citadel, "Kul Tirans": lighthouse, "Pandaren": pagoda_temple,
}
_keep = TH.keep
_ctx_plain = ctx


@contextlib.contextmanager
def ctx(race):                                # as above, plus the faction's landmark in place of the keep
    with _ctx_plain(race):
        saved = TH.keep
        if race in LANDMARK:
            TH.keep = LANDMARK[race]
        try:
            yield
        finally:
            TH.keep = saved


install()
