"""Raid boss map sprites (Nov 2026) in the hand-placed pixel style of the rest of the roster.

Each boss is drawn as a plain creature of its kind (a black dragon, a fire giant, a tentacled horror),
built from the roster's own flyer, golem and caster drawings plus two original horrors. No likenesses.
Bosses belong to no faction, so the nation-colour layers are flattened into fixed colours.
"""
import os

from PIL import Image, ImageChops

import unit_art as UA
import unit_art_humans as UH
import unit_art_machines   # noqa: F401  (loads the race and roster modules)
import unit_art_races as UR
import unit_art_roster as URO
import unit_art_beasts as UB
import roster_data as RD
from unit_art import lit, line

UNIT_DIR = "TileSets/AbsoluteUnits/Units"
OBSIDIAN = ((120, 110, 130), (74, 66, 86), (44, 38, 54))
MAGMA = ((120, 90, 84), (80, 56, 56), (50, 34, 40))
BLOOD = ((230, 120, 100), (180, 60, 60), (112, 34, 50))
VOID = ((170, 120, 190), (116, 74, 142), (70, 44, 96))
FEL = ((200, 255, 140), (130, 220, 80), (70, 150, 60))
EYE = ((255, 240, 150), (250, 190, 70), (200, 110, 40))

UB.FLYERS.update({
    "boss_black": dict(body=OBSIDIAN, wing="bat", wing_r=VOID, head="dragon", glow=UH.FLAME, big=True),
    "boss_lava": dict(body=MAGMA, wing="bat", wing_r=MAGMA, head="dragon", glow=UH.FLAME, big=True, long=True),
    "boss_frost": dict(body=UB.BONE, wing="bat", wing_r=UB.FROST, head="dragon", glow=UB.FROST, big=True),
    "boss_serpent": dict(body=BLOOD, wing="feather", wing_r=UH.FLAME, head="dragon", long=True, glow=UH.FLAME),
})


def horror(ramp, eyes=1, maw=False):
    """A mound of flesh and tentacles risen from the ground."""
    def f(cv, cx=UA.MID_X, fy=UA.FY):
        cv.shadow(cx, 15)
        for k, (x0, top, lean) in enumerate(((cx - 15, fy - 16, -1), (cx - 9, fy - 24, -1), (cx + 8, fy - 25, 1), (cx + 14, fy - 15, 1))):
            t = cv.part()
            pts = []
            for i in range(fy - top):
                y = fy - i
                x = x0 + (lean * (i * i) // 60 if k in (1, 2) else lean * i // 5)
                w = 2 if i < (fy - top) * 2 // 3 else 1
                pts += [(x + d, y) for d in range(w)]
            cv.pix(t, pts, lit(ramp, dark_from=x0 + 1))
            cv.pix(t, [(pts[-1][0] + lean, top), (pts[-1][0] + 2 * lean, top + 1)], ramp[1])
            s = cv.part(sep=False)
            cv.pix(s, [(x0, fy - 3 - 4 * j) for j in range(1, (fy - top) // 5)], ramp[0])
        b = cv.part()
        rows = [(fy - 17, cx - 3, cx + 3), (fy - 16, cx - 5, cx + 5), (fy - 15, cx - 6, cx + 6)]
        rows += [(y, cx - 7 - (y - (fy - 14)) // 3, cx + 7 + (y - (fy - 14)) // 3) for y in range(fy - 14, fy + 1)]
        cv.rows(b, rows, lit(ramp, dark_from=cx + 6, light_to=cx - 5, light_rows=fy - 12))
        d = cv.part(sep=False)
        cv.pix(d, [(cx - 6, fy - 4), (cx + 4, fy - 6), (cx - 2, fy - 2), (cx + 8, fy - 2), (cx - 9, fy - 1)], ramp[2])
        e = cv.part(sep=False)
        if eyes == 1:
            cv.rows(e, [(fy - 13, cx - 2, cx + 2), (fy - 12, cx - 3, cx + 3), (fy - 11, cx - 3, cx + 3), (fy - 10, cx - 2, cx + 2)], EYE[1])
            cv.rect(e, cx - 1, fy - 12, cx + 1, fy - 11, EYE[0])
            cv.rect(e, cx, fy - 12, cx, fy - 11, UA.DARK)
        else:
            for ex, ey in ((cx - 4, fy - 13), (cx + 2, fy - 14), (cx - 1, fy - 9), (cx + 5, fy - 9), (cx - 6, fy - 7), (cx + 1, fy - 5)):
                cv.rect(e, ex, ey, ex + 1, ey, EYE[1])
                cv.put(e, ex + 1, ey, UA.DARK)
        if maw:
            m = cv.part(sep=False)
            cv.rect(m, cx - 4, fy - 5, cx + 4, fy - 3, UA.DARK)
            cv.pix(m, [(x, fy - 5) for x in range(cx - 3, cx + 4, 2)] + [(x, fy - 3) for x in range(cx - 4, cx + 5, 2)], UB.BONE[0])
    return f


def demon(skin=BLOOD, wing=MAGMA):
    """A towering horned demon with bat wings and burning eyes."""
    def f(cv, cx=UA.MID_X, fy=UA.FY):
        cv.shadow(cx, 13)
        g = fy + 3                                                         # everything above the legs sits three rows lower
        for sgn in (-1, 1):                                                # wings, spread behind
            w = cv.part()
            rows = []
            for i in range(13):
                y = g - 31 + i
                inner = cx + sgn * 5
                outer = cx + sgn * (17 - max(0, i - 6) * 2 + (1 if i in (8, 10) else 0))
                rows.append((y, min(inner, outer), max(inner, outer)))
            cv.rows(w, rows, lit(wing, dark_from=cx + 9, light_to=cx - 12, light_rows=g - 26))
            b = cv.part(sep=False)
            cv.pix(b, [(cx + sgn * (6 + j), g - 31 + j // 2) for j in range(0, 11)], wing[2])
        t = cv.part()                                                      # tail
        cv.pix(t, line(cx + 5, g - 6, cx + 13, g - 2) + [(cx + 14, g - 3), (cx + 15, g - 4)], skin[2])
        for x0 in (cx - 6, cx + 2):                                        # legs and hooves
            l = cv.part()
            cv.rect(l, x0, g - 9, x0 + 4, fy - 1, lit(skin, dark_from=x0 + 4, light_to=x0))
            h = cv.part()
            cv.rect(h, x0 - 1, fy - 1, x0 + 5, fy, UA.DARK)
        for x0 in (cx - 12, cx + 9):                                       # arms and claws
            a = cv.part()
            cv.rect(a, x0, g - 22, x0 + 3, g - 11, lit(skin, dark_from=x0 + 3, light_to=x0))
            c = cv.part(sep=False)
            cv.pix(c, [(x0, g - 10), (x0 + 2, g - 10), (x0 + 3, g - 10)], UB.BONE[0])
        b = cv.part()                                                      # torso
        cv.rows(b, [(g - 23, cx - 8, cx + 8)] + [(y, cx - 9, cx + 9) for y in range(g - 22, g - 16)] +
                [(y, cx - 7, cx + 7) for y in range(g - 16, g - 9)], lit(skin, dark_from=cx + 6, light_to=cx - 5, light_rows=g - 18))
        r = cv.part(sep=False)                                             # burning sigil
        cv.pix(r, [(cx, g - 20), (cx - 1, g - 19), (cx + 1, g - 19), (cx, g - 18), (cx - 2, g - 17), (cx + 2, g - 17), (cx, g - 16)], FEL[1])
        k = cv.part()                                                      # loincloth
        cv.rows(k, [(g - 10, cx - 7, cx + 7), (g - 9, cx - 3, cx + 3), (g - 8, cx - 2, cx + 2), (g - 7, cx - 1, cx + 1)], UA.DARK)
        hd = cv.part()                                                     # head
        cv.rows(hd, [(g - 30, cx - 2, cx + 2)] + [(y, cx - 3, cx + 3) for y in range(g - 29, g - 24)] + [(g - 24, cx - 2, cx + 2)], lit(skin, dark_from=cx + 2, light_to=cx - 2))
        e = cv.part(sep=False)
        cv.pix(e, [(cx - 2, g - 27), (cx + 1, g - 27)], FEL[0])
        cv.rect(e, cx - 1, g - 25, cx + 1, g - 25, UA.DARK)
        for sgn in (-1, 1):                                                # horns
            hn = cv.part()
            cv.pix(hn, [(cx + sgn * 4, g - 29), (cx + sgn * 5, g - 30), (cx + sgn * 6, g - 31), (cx + sgn * 6, g - 32), (cx + sgn * 5, g - 33)], UB.BONE[0])
    return f


def _humans():
    return UR.RACES.get("Humans", URO.HUMANS)


def _air(kind):
    return lambda: UR.render(UB.flyer(kind), _humans(), "Catapult")


def _machine(fn):
    return lambda: UR.render(fn, _humans(), "Catapult")


def _unit(name, nation):
    def f():
        b, t, _ = RD.slots()[name]
        return URO.render(name, b, t, nation)
    return f


# name -> (layers function, inner colour, outer colour)
BOSSES = {
    "Onyxia": (_air("boss_black"), (90, 60, 110), (60, 40, 80)),
    "Deathwing the Destroyer": (_air("boss_lava"), (240, 120, 40), (90, 50, 50)),
    "Sapphiron": (_air("boss_frost"), (150, 200, 240), (110, 160, 220)),
    "Hakkar the Soulflayer": (_air("boss_serpent"), (230, 150, 60), (200, 70, 60)),
    "Ragnaros the Firelord": (_machine(UB.golem(core=UH.FLAME, ramp=MAGMA, crown=True)), (250, 150, 50), (230, 90, 40)),
    "Kil'jaeden the Deceiver": (_machine(demon()), (120, 220, 80), (150, 40, 50)),
    "Gul'dan the Destroyer": (_unit("Warlock", "Orcs"), (110, 200, 80), (70, 60, 90)),
    "Kel'Thuzad": (_unit("Lich", "Scourge"), (150, 210, 250), (90, 80, 140)),
    "C'Thun": (_machine(horror(VOID, eyes=1)), (150, 100, 180), (110, 70, 140)),
    "N'Zoth the Corruptor": (_machine(horror(((120, 130, 170), (76, 84, 130), (46, 50, 90)), eyes=6, maw=True)), (100, 110, 160), (70, 80, 130)),
}


def render(name):
    make, inner, outer = BOSSES[name]
    base, l1, l2 = make()
    out = base.copy()
    for layer, rgb in ((l1, inner), (l2, outer)):
        tint = Image.new("RGBA", layer.size, rgb + (255,))
        out.alpha_composite(ImageChops.multiply(layer, tint))
    return out


def write_all(images_dir):
    folder = os.path.join(images_dir, UNIT_DIR)
    if not os.path.isdir(folder):
        return 0
    for name in BOSSES:
        for suf in ("-1", "-2"):
            p = os.path.join(folder, name + suf + ".png")
            if os.path.exists(p):
                os.remove(p)
        render(name).save(os.path.join(folder, name + ".png"))
    return len(BOSSES)
