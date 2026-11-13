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


install()
