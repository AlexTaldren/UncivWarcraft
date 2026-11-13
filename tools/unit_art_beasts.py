"""Dedicated sprites for the roster's beasts, brutes, constructs, ships and flyers (replaces the interim art).

Parametric designs: one drawing routine per kind of thing, with a style per faction or per unit, so an
elven warship, a troll war canoe and a goblin steamer differ in hull, rig and prow, not only in colour.
All designs are original.
"""
import unit_art as UA
import unit_art_humans as UH
import unit_art_machines as UM
import unit_art_races as UR
from unit_art import lit, line, DARK, TINT, SKIN, HAIR, STEEL, LEATHER, TAN, WHITE, WOOD, GOLD, IRON, STONE, GLOW, FY, MID_X
from unit_art_humans import GREEN, ARCANE, AZER, CLOTHD, FUR, FLAME, RED, SMOKE
from unit_art_races import BONE, BLACK, beast

WY = 31
CX = 23
BRASS = UM.BRASS
TAR = UM.TAR
FEL = ((200, 255, 130), (130, 220, 70), (70, 140, 60))
FROST = ((226, 246, 255), (150, 210, 244), (84, 140, 200))
BEAR = ((170, 124, 86), (124, 86, 60), (80, 54, 46))
HOUND = ((150, 84, 70), (104, 54, 52), (66, 36, 44))
SHELL = ((150, 176, 110), (104, 132, 84), (68, 92, 72))
BARK = ((150, 116, 86), (108, 80, 62), (72, 52, 48))
LEAF = ((140, 200, 110), (90, 150, 84), (54, 100, 76))
ROCKY = ((190, 186, 178), (144, 140, 140), (96, 94, 108))
VIOLETW = ((170, 140, 190), (122, 96, 150), (80, 62, 108))
PALEW = ((250, 244, 226), (222, 208, 176), (160, 144, 130))


# ================================================================ beasts on four legs
def bear(orig, cv, cx, fy, ramp=None):
    def extra(cv, cx, back):
        m = cv.part(sep=False)
        cv.rows(m, [(back - 1, cx + 14, cx + 17), (back, cx + 15, cx + 17)], TAN[1])
        cv.put(m, cx + 17, back - 1, DARK)
    return beast(cv, cx, fy, BEAR, head_rows=[(-5, 9, 14), (-4, 8, 16), (-3, 7, 17), (-2, 6, 17), (-1, 5, 17), (0, 4, 17), (1, 5, 12)],
                 tail_rows=[(1, -11, -11)], ears=[(9, -6), (10, -6), (13, -6), (14, -6)], eye=(14, -3), extra=extra, leg_w=4)


def hound(orig, cv, cx, fy, ramp=None):
    """A two-headed hound of fire."""
    def extra(cv, cx, back):
        h2 = cv.part()                                                      # second head, higher
        cv.rows(h2, [(back - 9, cx + 6, cx + 10), (back - 8, cx + 5, cx + 13), (back - 7, cx + 5, cx + 14), (back - 6, cx + 5, cx + 9)], lit(HOUND, dark_from=cx + 12, light_to=cx + 8))
        g = cv.part(sep=False)
        cv.pix(g, [(cx + 10, back - 8), (cx + 12, back - 4), (cx + 14, back - 7), (cx + 17, back - 3)], FLAME[0])
        cv.pix(g, [(x, back + 1) for x in range(cx - 7, cx + 7, 3)] + [(x, back + 3) for x in range(cx - 6, cx + 8, 4)], FLAME[1])
    return beast(cv, cx, fy, HOUND, head_rows=[(-5, 9, 13), (-4, 8, 16), (-3, 7, 17), (-2, 6, 17), (-1, 5, 12), (0, 4, 10), (1, 5, 9)],
                 tail_rows=[(-1, -13, -11), (0, -12, -10), (1, -11, -10)], ears=[(9, -6), (12, -6)], extra=extra)


def turtle(orig, cv, cx, fy, ramp=None):
    """A dragon turtle: domed spiked shell, beaked head, stumpy legs."""
    back = fy - 13
    for x0 in (cx - 9, cx + 4):
        l = cv.part()
        cv.rect(l, x0, fy - 4, x0 + 4, fy - 1, lit(SHELL, dark_from=x0 + 3, light_to=x0))
        cv.rect(l, x0, fy, x0 + 5, fy, DARK)
    h = cv.part()
    cv.rows(h, [(back + 2, cx + 10, cx + 15), (back + 3, cx + 9, cx + 17), (back + 4, cx + 9, cx + 17), (back + 5, cx + 9, cx + 15), (back + 6, cx + 9, cx + 12)], lit(SHELL, dark_from=cx + 15, light_to=cx + 12))
    d = cv.part(sep=False)
    cv.put(d, cx + 14, back + 3, FLAME[0])
    cv.rect(d, cx + 15, back + 5, cx + 17, back + 5, SHELL[2])
    s = cv.part()
    rows = [(back, cx - 5, cx + 4), (back + 1, cx - 8, cx + 7), (back + 2, cx - 10, cx + 9)] + [(y, cx - 11, cx + 10) for y in range(back + 3, back + 8)] + [(back + 8, cx - 10, cx + 9)]
    cv.rows(s, rows, lit(BARK, dark_from=cx + 7, light_to=cx - 2, light_rows=back + 3))
    p = cv.part(sep=False)
    for x in (cx - 7, cx - 1, cx + 5):
        cv.pix(p, [(x, back + 3), (x + 1, back + 4), (x, back + 5), (x - 1, back + 6)], BARK[2])
    cv.rect(p, cx - 11, back + 7, cx + 10, back + 7, IRON[1])
    sp = cv.part()
    cv.pix(sp, [(cx - 6, back - 1), (cx, back - 1), (cx + 5, back)], BONE[0])
    return back


def big_lizard(body):
    return UR.strider(body, body, BONE, plume=0, crest=1, teeth=True)


BEASTS = {"kodo": UR.kodo, "bear": bear, "hound": hound, "turtle": turtle, "yak": UR.yak, "direhorn": UR.direhorn, "elekk": UR.elekk,
          "devilsaur": big_lizard(((176, 150, 110), (130, 104, 78), (86, 66, 58))), "wolf": UR.wolf}


def war_beast(kind, gear="pack"):
    """A riderless war beast with its harness: a pack, war drums, a howdah or a siege frame."""
    def f(cv, cx=MID_X - 2, fy=FY):
        cv.shadow(cx + 1, 14)
        back = BEASTS[kind](None, cv, cx, fy)
        if kind != "turtle":
            UH.blanket(cv, cx, back)
        if gear == "drums":
            for x0 in (cx - 6, cx):
                d = cv.part()
                cv.rect(d, x0, back - 4, x0 + 4, back - 1, lit(WOOD, dark_from=x0 + 3, light_to=x0 + 1))
                t = cv.part(sep=False)
                cv.rect(t, x0, back - 4, x0 + 4, back - 4, TAN[0])
        elif gear == "howdah":
            p = cv.part()
            cv.rect(p, cx - 7, back - 2, cx + 4, back - 1, lit(WOOD, dark_from=cx + 3))
            c = cv.part(2)
            cv.rect(c, cx - 6, back - 7, cx + 3, back - 3, lit(TINT, dark_from=cx + 2, light_to=cx - 4, light_rows=back - 6))
            r = cv.part(1)
            cv.rows(r, [(back - 9, cx - 5, cx + 2), (back - 8, cx - 7, cx + 4)], lit(TINT, dark_from=cx + 2))
        elif gear == "siege":
            p = cv.part()
            cv.rect(p, cx - 7, back - 2, cx + 4, back - 1, lit(WOOD, dark_from=cx + 3))
            a = cv.part()
            cv.pix(a, [(cx - 6 + i, back - 3 - i) for i in range(9)] + [(cx - 5 + i, back - 3 - i) for i in range(9)], WOOD[1])
            s = cv.part()
            cv.rect(s, cx + 2, back - 14, cx + 5, back - 11, lit(STONE, dark_from=cx + 5, light_to=cx + 3))
        else:
            p = cv.part()
            cv.rect(p, cx - 5, back - 3, cx + 2, back - 1, lit(LEATHER, dark_from=cx + 1, light_to=cx - 3, light_rows=back - 3))
            d = cv.part(1, sep=False)
            cv.rect(d, cx - 5, back - 2, cx + 2, back - 2, TINT[1])
    return f


# ================================================================ brutes, trees and constructs
def brute(weapon="club", heads=1, stitched=False):
    """A hulking brute twice the size of a soldier: ogres, abominations, flesh giants."""
    def f(cv, cx=MID_X, fy=FY):
        cv.shadow(cx, 12)
        wx = cx - 12
        if weapon == "club":
            w = cv.part()
            cv.rect(w, wx, fy - 20, wx + 1, fy - 11, WOOD[1])
            cv.rows(w, [(fy - 30, wx - 1, wx + 2)] + [(y, wx - 2, wx + 3) for y in range(fy - 29, fy - 21)] + [(fy - 21, wx - 1, wx + 2)], lit(WOOD, dark_from=wx + 2, light_to=wx - 1))
            s = cv.part(sep=False)
            cv.pix(s, [(wx - 1, fy - 27), (wx + 2, fy - 25), (wx, fy - 23)], STEEL[0])
        else:
            w = cv.part()
            cv.rect(w, wx, fy - 20, wx + 1, fy - 11, WOOD[1])
            cv.rows(w, [(y, wx - 3, wx + 2) for y in range(fy - 30, fy - 21)] + [(fy - 21, wx - 2, wx + 1)], lit(STEEL, dark_from=wx + 1, light_to=wx - 2))
            cv.rect(w, wx - 3, fy - 30, wx - 3, fy - 22, STEEL[0])
        for x0 in (cx - 13, cx + 10):
            a = cv.part()
            cv.rect(a, x0, fy - 21, x0 + 3, fy - 12, lit(SKIN, dark_from=x0 + 3, light_to=x0))
        for x0 in (cx - 6, cx + 2):
            l = cv.part()
            cv.rect(l, x0, fy - 7, x0 + 4, fy - 2, lit(SKIN, dark_from=x0 + 4, light_to=x0))
            ft = cv.part()
            cv.rect(ft, x0 - 1, fy - 1, x0 + 5, fy, lit(SKIN, dark_from=x0 + 4))
            cv.rect(ft, x0 - 1, fy, x0 + 5, fy, SKIN[2])
        t = cv.part()
        rows = [(fy - 23, cx - 7, cx + 7)] + [(y, cx - 8, cx + 8) for y in range(fy - 22, fy - 16)] + [(y, cx - 9, cx + 9) for y in range(fy - 16, fy - 9)]
        cv.rows(t, rows, lit(SKIN, dark_from=cx + 7, light_to=cx - 5, light_rows=fy - 17))
        d = cv.part(sep=False)
        if stitched:
            cv.pix(d, line(cx - 5, fy - 21, cx + 4, fy - 12), DARK)
            cv.pix(d, [(cx - 3, fy - 21), (cx - 1, fy - 17), (cx + 1, fy - 17), (cx + 3, fy - 13), (cx + 5, fy - 13)], WHITE[0])
            cv.rect(d, cx + 2, fy - 15, cx + 6, fy - 12, RED[2])
        else:
            cv.rect(d, cx - 3, fy - 13, cx + 3, fy - 13, SKIN[2])
            cv.pix(d, line(cx - 8, fy - 22, cx + 6, fy - 10), LEATHER[1])
        lc = cv.part(2)
        cv.rows(lc, [(y, cx - 9, cx + 9) for y in range(fy - 10, fy - 6)] + [(fy - 6, cx - 8, cx - 2), (fy - 6, cx + 2, cx + 8)], lit(TINT, dark_from=cx + 7, light_to=cx - 6, light_rows=fy - 9))
        b = cv.part(1, sep=False)
        cv.rect(b, cx - 9, fy - 10, cx + 9, fy - 10, TINT[1])
        if heads == 2:
            UA.head(cv, cx - 4, fy - 30)
            UA.head(cv, cx + 4, fy - 30)
        else:
            UA.head(cv, cx, fy - 30)
        sp = UA.pauldron(cv, cx - 14, fy - 24, IRON, w=6)
        for x0 in (cx - 14, cx + 9):
            fs = cv.part()
            cv.rect(fs, x0, fy - 12, x0 + 4, fy - 8, lit(SKIN, dark_from=x0 + 4, light_to=x0 + 1, light_rows=fy - 11))
        if stitched:
            hk = cv.part()
            cv.pix(hk, [(cx + 12, fy - 7), (cx + 12, fy - 6), (cx + 13, fy - 5), (cx + 14, fy - 5), (cx + 15, fy - 6), (cx + 15, fy - 7)], STEEL[0])
    return f


def treant(stone=False, thrower=False):
    """A walking ancient: trunk body, branch arms, a crown of leaves (or a moss-backed stone giant)."""
    body = ROCKY if stone else BARK
    def f(cv, cx=MID_X, fy=FY):
        cv.shadow(cx, 12)
        for x0 in (cx - 6, cx + 2):
            l = cv.part()
            cv.rect(l, x0, fy - 8, x0 + 4, fy - 1, lit(body, dark_from=x0 + 4, light_to=x0))
            cv.rows(l, [(fy, x0 - 1, x0 + 5)], body[2])
        for x0, up in ((cx - 12, thrower), (cx + 9, False)):
            a = cv.part()
            if up:
                cv.rect(a, x0, fy - 30, x0 + 3, fy - 18, lit(body, dark_from=x0 + 3, light_to=x0))
                r = cv.part()
                cv.rows(r, [(fy - 35 + 4, x0 - 1, x0 + 4), (fy - 30, x0 - 2, x0 + 5), (fy - 29, x0 - 2, x0 + 5), (fy - 28, x0 - 1, x0 + 4)], lit(STONE, dark_from=x0 + 4, light_to=x0))
            else:
                cv.rect(a, x0, fy - 21, x0 + 3, fy - 9, lit(body, dark_from=x0 + 3, light_to=x0))
                cv.rows(a, [(fy - 8, x0 - 1, x0 + 4), (fy - 7, x0 - 1, x0 + 4)], body[2])
        t = cv.part()
        cv.rows(t, [(y, cx - 8, cx + 8) for y in range(fy - 24, fy - 8)], lit(body, dark_from=cx + 6, light_to=cx - 5, light_rows=fy - 18))
        d = cv.part(sep=False)
        cv.pix(d, [(cx - 5, y) for y in range(fy - 22, fy - 10, 3)] + [(cx + 3, y) for y in range(fy - 21, fy - 10, 3)], body[2])
        cv.pix(d, [(cx - 1, fy - 19), (cx + 3, fy - 19)], GLOW[1] if not stone else AZER[0])
        cv.rect(d, cx - 1, fy - 16, cx + 3, fy - 16, DARK)
        s = cv.part(2)                                                      # sash in the faction's colour
        cv.rect(s, cx - 8, fy - 12, cx + 8, fy - 10, lit(TINT, dark_from=cx + 6, light_to=cx - 5))
        c = cv.part()
        rows = [(fy - 31, cx - 5, cx + 4), (fy - 30, cx - 8, cx + 7), (fy - 29, cx - 10, cx + 9), (fy - 28, cx - 11, cx + 10), (fy - 27, cx - 11, cx + 10), (fy - 26, cx - 10, cx + 9), (fy - 25, cx - 9, cx + 8)]
        if stone:
            rows = rows[2:]
        cv.rows(c, rows, lit(LEAF, dark_from=cx + 6, light_to=cx - 4, light_rows=fy - 29))
        m = cv.part(sep=False)
        cv.pix(m, [(cx - 6, fy - 28), (cx + 2, fy - 29), (cx + 6, fy - 27), (cx - 2, fy - 26)], LEAF[2])
    return f


def golem(core=FLAME, arm="fist", head="box", ramp=STEEL, crown=False):
    """A walking construct: boiler or crystal body, changeable arms and head."""
    def f(cv, cx=MID_X, fy=FY):
        cv.shadow(cx, 12)
        for x0 in (cx - 12, cx + 9):
            a = cv.part()
            cv.rect(a, x0, fy - 20, x0 + 3, fy - 11, lit(ramp, dark_from=x0 + 3, light_to=x0))
        for x0 in (cx - 6, cx + 2):
            l = cv.part()
            cv.rect(l, x0, fy - 9, x0 + 4, fy - 2, lit(ramp, dark_from=x0 + 4, light_to=x0))
            ft = cv.part()
            cv.rect(ft, x0 - 1, fy - 2, x0 + 5, fy, lit(ramp, dark_from=x0 + 4, light_to=x0, light_rows=fy - 2))
            cv.rect(ft, x0 - 1, fy, x0 + 5, fy, ramp[2])
        pv = cv.part()
        cv.rect(pv, cx - 6, fy - 12, cx + 6, fy - 10, lit(ramp, dark_from=cx + 5, light_to=cx - 4))
        t = cv.part()
        cv.rows(t, [(fy - 24, cx - 7, cx + 7)] + [(y, cx - 8, cx + 8) for y in range(fy - 23, fy - 13)] + [(fy - 13, cx - 7, cx + 7)], lit(ramp, dark_from=cx + 6, light_to=cx - 5, light_rows=fy - 20))
        d = cv.part(sep=False)
        cv.rect(d, cx - 4, fy - 21, cx + 4, fy - 15, ramp[2])
        if head == "crystal" or arm == "crystal":
            cv.rows(d, [(fy - 21, cx, cx), (fy - 20, cx - 1, cx + 1), (fy - 19, cx - 2, cx + 2), (fy - 18, cx - 3, cx + 3), (fy - 17, cx - 2, cx + 2), (fy - 16, cx - 1, cx + 1), (fy - 15, cx, cx)], core[1])
            cv.pix(d, [(cx, fy - 18), (cx - 1, fy - 19)], core[0])
        else:
            cv.rect(d, cx - 3, fy - 20, cx + 3, fy - 16, core[1])
            cv.rect(d, cx - 2, fy - 18, cx + 2, fy - 16, core[0])
            cv.pix(d, [(cx - 1, y) for y in range(fy - 20, fy - 15)] + [(cx + 1, y) for y in range(fy - 20, fy - 15)], ramp[2])
        if head == "pumpkin":
            h = cv.part()
            cv.rows(h, [(fy - 31, cx - 2, cx + 2)] + [(y, cx - 4, cx + 4) for y in range(fy - 30, fy - 25)] + [(fy - 25, cx - 3, cx + 3)], lit(((255, 180, 90), (232, 130, 50), (160, 80, 44)), dark_from=cx + 3, light_to=cx - 2))
            e = cv.part(sep=False)
            cv.pix(e, [(cx - 2, fy - 29), (cx + 2, fy - 29), (cx - 2, fy - 27), (cx - 1, fy - 26), (cx, fy - 27), (cx + 1, fy - 26), (cx + 2, fy - 27)], GLOW[0])
            st = cv.part()
            cv.pix(st, [(cx, fy - 32), (cx + 1, fy - 33)], LEAF[2])
        elif head == "crystal":
            h = cv.part()
            cv.rows(h, [(fy - 32, cx, cx), (fy - 31, cx - 1, cx + 1), (fy - 30, cx - 2, cx + 2), (fy - 29, cx - 2, cx + 2), (fy - 28, cx - 2, cx + 2), (fy - 27, cx - 1, cx + 1), (fy - 26, cx - 1, cx + 1)], lit(core, dark_from=cx + 2, light_to=cx - 1))
        else:
            h = cv.part()
            cv.rect(h, cx - 3, fy - 29, cx + 3, fy - 25, lit(ramp, dark_from=cx + 3, light_to=cx - 2, light_rows=fy - 28))
            e = cv.part(sep=False)
            cv.rect(e, cx - 1, fy - 27, cx + 3, fy - 27, core[0])
            if crown:
                c = cv.part()
                cv.pix(c, [(cx - 3, fy - 30), (cx - 3, fy - 31), (cx, fy - 30), (cx, fy - 31), (cx + 3, fy - 30), (cx + 3, fy - 31)], GOLD[0])
        for x0 in (cx - 13, cx + 8):
            p = cv.part(2)
            cv.rows(p, [(fy - 26, x0 + 1, x0 + 4), (fy - 25, x0, x0 + 5), (fy - 24, x0, x0 + 5), (fy - 23, x0, x0 + 5), (fy - 22, x0, x0 + 5)], lit(TINT, dark_from=x0 + 4, light_to=x0 + 1, light_rows=fy - 24))
            tr = cv.part(1, sep=False)
            cv.rect(tr, x0, fy - 22, x0 + 5, fy - 22, TINT[1])
        for x0 in (cx - 13, cx + 8):
            hd = cv.part()
            if arm == "saw":
                cv.rows(hd, [(fy - 12, x0 + 1, x0 + 4), (fy - 11, x0, x0 + 5), (fy - 10, x0 - 1, x0 + 6), (fy - 9, x0 - 1, x0 + 6), (fy - 8, x0 - 1, x0 + 6), (fy - 7, x0, x0 + 5), (fy - 6, x0 + 1, x0 + 4)], lit(STEEL, dark_from=x0 + 5, light_to=x0 + 1))
                tt = cv.part()
                cv.pix(tt, [(x0 + 2, fy - 13), (x0 - 2, fy - 9), (x0 + 7, fy - 9), (x0 + 3, fy - 5)], STEEL[0])
                hb = cv.part(sep=False)
                cv.put(hb, x0 + 2, fy - 9, DARK)
            elif arm == "blade":
                cv.rows(hd, [(fy - 11, x0, x0 + 3)] + [(y, x0 + 1, x0 + 2) for y in range(fy - 10, fy - 3)] + [(fy - 3, x0 + 3, x0 + 5), (fy - 4, x0 + 3, x0 + 4)], lit(STEEL, dark_from=x0 + 2))
            else:
                cv.rect(hd, x0, fy - 11, x0 + 5, fy - 6, lit(ramp, dark_from=x0 + 4, light_to=x0 + 1, light_rows=fy - 9))
                cv.rect(hd, x0, fy - 6, x0 + 5, fy - 6, ramp[2])
    return f


def spider_tank(cv, cx=MID_X, fy=FY):
    """A walking tank: a riveted pod with a gun, carried on four jointed legs."""
    cv.shadow(cx, 14)
    for x0, d in ((cx - 9, -1), (cx - 4, -1), (cx + 4, 1), (cx + 9, 1)):
        l = cv.part()
        cv.pix(l, line(x0, fy - 9, x0 + 3 * d, fy - 13) + line(x0 + 3 * d, fy - 13, x0 + 5 * d, fy - 1) + line(x0 + 1, fy - 9, x0 + 3 * d + 1, fy - 13) + line(x0 + 3 * d + 1, fy - 13, x0 + 5 * d + 1, fy - 1), IRON[1])
        cv.rect(l, x0 + 5 * d - 1, fy, x0 + 5 * d + 2, fy, IRON[2])
    g = cv.part()
    cv.rect(g, cx + 6, fy - 15, cx + 17, fy - 14, lit(IRON, light_to=cx + 17, light_rows=fy - 15))
    b = cv.part()
    cv.rows(b, [(fy - 19, cx - 5, cx + 5), (fy - 18, cx - 7, cx + 7)] + [(y, cx - 8, cx + 8) for y in range(fy - 17, fy - 10)] + [(fy - 10, cx - 7, cx + 7), (fy - 9, cx - 5, cx + 5)], lit(BRASS, dark_from=cx + 6, light_to=cx - 4, light_rows=fy - 16))
    p = cv.part(2, sep=False)
    cv.rect(p, cx - 6, fy - 15, cx + 1, fy - 12, lit(TINT, dark_from=cx, light_to=cx - 4, light_rows=fy - 15))
    w = cv.part(sep=False)
    cv.rect(w, cx + 3, fy - 17, cx + 6, fy - 15, AZER[1])
    cv.put(w, cx + 3, fy - 17, AZER[0])
    cv.pix(w, [(cx - 7, fy - 17), (cx + 7, fy - 11), (cx - 7, fy - 11)], BRASS[2])
    s = cv.part()
    cv.rect(s, cx - 3, fy - 23, cx - 2, fy - 20, IRON[1])
    UM.smoke(cv, cx - 2, fy - 24)


# ================================================================ ships (bow to the right)
SHIPS = {
    "horde": dict(hull=TAR, sail="square", prow="tusk", shields=True),
    "nightelf": dict(hull=VIOLETW, sail="crescent", prow="curl", lantern=AZER),
    "elf": dict(hull=PALEW, sail="lateen", prow="curl", trim=GOLD),
    "navy": dict(hull=WOOD, sail="square", prow="plain", guns=True, white=True),
    "troll": dict(hull=BARK, sail="bat", prow="tiki", outrigger=True),
    "zandalari": dict(hull=BARK, sail="bat", prow="tiki", trim=GOLD, guns=True),
    "goblin": dict(hull=RED, sail="none", prow="ram", funnels=True),
    "pandaren": dict(hull=WOOD, sail="junk", prow="curl"),
    "ghost": dict(hull=BONE, sail="bat", prow="tusk", lantern=FROST, grey=True),
}


def ship(style, tier):
    st = SHIPS[style]
    x0, x1, top = [(12, 33, WY - 3), (7, 37, WY - 5), (4, 40, WY - 8)][tier]
    masts = [[22], [16, 28], [12, 22, 32]][tier]
    def f(cv):
        hull_r = st["hull"]
        if tier == 2:                                                       # castles
            for a, b, h in ((x0, x0 + 7, 4), (x1 - 8, x1 - 2, 3)):
                c = cv.part()
                cv.rect(c, a, top - h, b, top - 1, lit(hull_r, dark_from=b - 1, light_to=a + 1, light_rows=top - h))
                UM.ports(cv, [a + 2, a + 4], top - h + 1, (st.get("lantern") or GLOW)[1])
        px, py = x1, top - 1                                                # prow ornament
        o = cv.part()
        if st["prow"] == "tusk":
            cv.pix(o, [(px, py), (px + 1, py - 1), (px + 2, py - 2), (px + 2, py - 3), (px + 1, py + 2), (px + 2, py + 2)], BONE[0])
        elif st["prow"] == "curl":
            cv.pix(o, [(px, py), (px + 1, py - 1), (px + 1, py - 2), (px + 1, py - 3), (px + 2, py - 4), (px + 3, py - 4), (px + 3, py - 3)], (st.get("trim") or hull_r)[0])
        elif st["prow"] == "tiki":
            cv.rect(o, px, py - 5, px + 2, py, lit(hull_r, dark_from=px + 2))
            e = cv.part(1, sep=False)
            cv.pix(e, [(px, py - 4), (px + 2, py - 4), (px + 1, py - 2)], TINT[0])
        elif st["prow"] == "ram":
            cv.rows(o, [(WY - 1, px, px + 4), (WY, px - 1, px + 2)], lit(STEEL, dark_from=px + 3))
        UM.hull(cv, x0, x1, top, ramp=hull_r, rake=1 if tier < 2 else 0)
        UM.stripe(cv, x0 + 1, x1 - 3 - (WY - top) // 2, top + 1, top + 1, layer=2 if not st.get("white") else 2)
        if st.get("trim"):
            t = cv.part(sep=False)
            cv.rect(t, x0, top, x1, top, st["trim"][1])
        if st.get("guns") or tier == 2:
            UM.ports(cv, range(x0 + 4, x1 - 5, 4), top + 3 if tier == 2 else top + 2)
        if st.get("shields"):
            for i, x in enumerate(range(x0 + 3, x1 - 4, 5)):
                s = cv.part(2 if i % 2 == 0 else 1)
                cv.rows(s, [(top - 1, x + 1, x + 1), (top, x, x + 2), (top + 1, x, x + 2), (top + 2, x + 1, x + 1)], lit(TINT, dark_from=x + 2))
        if st.get("funnels"):
            for i, x in enumerate(masts):
                UM.smoke(cv, x + 1, top - 9 - i % 2)
                UM.funnel(cv, x, top - 7 - i % 2, top - 1)
            cab = cv.part()
            cv.rect(cab, x1 - 12, top - 4, x1 - 6, top - 1, lit(STEEL, dark_from=x1 - 7, light_to=x1 - 11, light_rows=top - 4))
            UM.ports(cv, [x1 - 10, x1 - 8], top - 3, AZER[1])
            fl = masts[0]
            UM.flag(cv, x1 - 9, top - 7, 2)
        else:
            for i, x in enumerate(masts):
                mt = [8, 5, 2][tier] + (2 if i != len(masts) // 2 else 0)
                UM.mast(cv, x, mt, top - 1)
                w = [9, 9, 7][tier] if len(masts) > 1 else 11
                h_total = top - 2 - (mt + 2)
                kind = st["sail"]
                layer, ramp = (0, CLOTHD) if st.get("grey") else ((0, WHITE) if st.get("white") else (2, TINT))
                if kind == "square":
                    if h_total > 12:
                        UM.sail(cv, x, mt + 2, w - 2, h_total // 2 - 1, layer=layer, ramp=ramp, band=2 if st.get("white") else 1)
                        UM.sail(cv, x, mt + 2 + h_total // 2, w, h_total - h_total // 2, layer=layer, ramp=ramp, band=2 if st.get("white") else 1)
                    else:
                        UM.sail(cv, x, mt + 2, w, h_total, layer=layer, ramp=ramp, band=2 if st.get("white") else 1)
                elif kind == "junk":
                    s = UM.sail(cv, x, mt + 2, w, h_total, layer=layer, ramp=ramp, band=None)
                    b = cv.part(sep=False)
                    for yy in range(mt + 4, mt + 2 + h_total, 3):
                        cv.rect(b, x - w // 2, yy, x + w // 2, yy, WOOD[2])
                else:
                    s = cv.part(layer)
                    rows = []
                    for k in range(h_total):
                        if kind == "lateen":
                            rows.append((mt + 2 + k, x + 1, x + 1 + (k * w) // h_total))
                        elif kind == "crescent":
                            rows.append((mt + 2 + k, x + 1 + min(k, h_total - 1 - k) // 3, x + 2 + min(k * 2, (h_total - k) * 2, w)))
                        else:                                               # bat: ragged lower edge
                            a, b2 = x - w // 2 + (k // 3), x + w // 2 - (k // 4)
                            if k == h_total - 1:
                                rows += [(mt + 2 + k, xx, xx) for xx in range(a, b2 + 1, 2)]
                            else:
                                rows.append((mt + 2 + k, a, b2))
                    cv.rows(s, rows, lit(ramp, dark_from=x + w // 2 - 1, light_to=x - 1, light_rows=mt + 2 + h_total - 3))
                    if not st.get("grey"):
                        t = cv.part(1, sep=False)
                        y = mt + 2 + h_total // 2
                        cv.pix(t, [(xx, yy) for (yy, a, b2) in rows if yy == y for xx in range(a, b2 + 1)], TINT[1])
            UM.flag(cv, masts[len(masts) // 2], [8, 5, 2][tier] - 1 if tier < 2 else 1, 1)
        if st.get("lantern"):
            g = cv.part()
            cv.pix(g, [(x0 + 1, top - 2), (x1 - 2, top - 3)], st["lantern"][0])
        UM.foam(cv, x0 + 1, x1 - 2 - (WY - top) // (1 if tier < 2 else 99))
        if st.get("outrigger") or (st.get("shields") and tier == 0):
            UM.oars(cv, range(x0 + 4, x1 - 4, 5), WY - 1, n=5)
    return f


# ================================================================ flyers
FLYERS = {
    "gryphon": dict(body=TAN, wing="feather", wing_r=WHITE, head="beak", rider=True),
    "wyvern": dict(body=TAN, wing="bat", wing_r=LEATHER, head="snout", tail="sting", rider=True),
    "hippogryph": dict(body=((120, 200, 196), (70, 150, 160), (44, 100, 124)), wing="feather", wing_layer=2, head="beak", antlers=True, rider=True),
    "bat": dict(body=CLOTHD, wing="bat", wing_r=CLOTHD, head="bat", rider=True),
    "dragonhawk": dict(body=RED, wing="feather", wing_layer=2, head="beak", long=True, rider=True),
    "pterrordax": dict(body=((150, 190, 150), (100, 144, 110), (64, 98, 86)), wing="bat", wing_layer=2, head="crest", rider=True),
    "eagle": dict(body=FUR, wing="feather", wing_r=FUR, head="beak", white_head=True, rider=True),
    "ray": dict(body=((190, 150, 230), (140, 100, 190), (90, 62, 140)), wing="ray", head="none", glow=ARCANE, rider=True),
    "serpent": dict(body=((130, 220, 180), (80, 170, 140), (50, 110, 110)), wing="none", head="dragon", long=True, mane=2, rider=True),
    "couatl": dict(body=((130, 210, 220), (80, 160, 180), (50, 104, 130)), wing="feather", wing_layer=1, head="dragon", long=True),
    "gargoyle": dict(body=ROCKY, wing="bat", wing_r=ROCKY, head="bat", glow=FROST),
    "wyrm": dict(body=BONE, wing="bat", wing_r=FROST, head="dragon", glow=FROST, big=True),
    "phoenix": dict(body=FLAME, wing="feather", wing_r=FLAME, head="beak", glow=FLAME, tail="plume"),
    "chimaera": dict(body=LEAF, wing="bat", wing_r=VIOLETW, head="two", big=True),
    "thunder": dict(body=((150, 170, 220), (100, 122, 180), (64, 80, 130)), wing="bat", wing_layer=1, head="snout", tail="sting", rider=True, glow=AZER),
}


def flyer(kind):
    st = FLYERS[kind]
    def f(cv, cx=CX - 1):
        by = 19 if not st.get("big") else 20
        body = st["body"]
        cv.shadow(cx, 9, FY + 2)
        wl = st.get("wing_layer", 0)
        wr = TINT if wl else st.get("wing_r", body)
        w = cv.part(wl)                                                     # far wing, raised
        if st["wing"] == "feather":
            rows = [(by - 14, cx - 10, cx - 7), (by - 13, cx - 11, cx - 5), (by - 12, cx - 12, cx - 3), (by - 11, cx - 12, cx - 1), (by - 10, cx - 12, cx + 1), (by - 9, cx - 11, cx + 2),
                    (by - 8, cx - 10, cx + 3), (by - 7, cx - 8, cx + 3), (by - 6, cx - 6, cx + 3), (by - 5, cx - 4, cx + 3), (by - 4, cx - 2, cx + 3)]
        elif st["wing"] == "bat":
            rows = [(by - 15, cx - 6, cx - 4), (by - 14, cx - 9, cx - 3), (by - 13, cx - 12, cx - 2), (by - 12, cx - 13, cx - 1), (by - 11, cx - 13, cx), (by - 10, cx - 13, cx + 1),
                    (by - 9, cx - 13, cx - 10), (by - 9, cx - 8, cx - 5), (by - 9, cx - 3, cx + 2), (by - 8, cx - 13, cx - 12), (by - 8, cx - 7, cx - 6), (by - 8, cx - 2, cx + 3),
                    (by - 7, cx - 1, cx + 3), (by - 6, cx, cx + 3), (by - 5, cx, cx + 3), (by - 4, cx + 1, cx + 3)]
        elif st["wing"] == "ray":
            rows = [(by - 4, cx - 6, cx + 6), (by - 3, cx - 10, cx + 9), (by - 2, cx - 13, cx + 11), (by - 1, cx - 14, cx + 12)]
        else:
            rows = []
        cv.rows(w, rows, lit(wr, dark_from=cx + 1, light_to=cx - 8, light_rows=by - 10))
        if st.get("tail") == "sting":
            t = cv.part()
            cv.pix(t, [(cx - 10, by + 1), (cx - 11, by), (cx - 12, by - 1), (cx - 13, by - 2), (cx - 13, by - 3), (cx - 12, by - 4)], body[1])
            cv.pix(t, [(cx - 11, by - 5), (cx - 12, by - 4)], BONE[0])
        elif st.get("tail") == "plume" or st["wing"] == "feather":
            t = cv.part(wl if st.get("tail") != "plume" else 0)
            cv.rows(t, [(by, cx - 13, cx - 9), (by + 1, cx - 14, cx - 9), (by + 2, cx - 13, cx - 10)], lit(wr, dark_from=cx - 10))
        elif st.get("long"):
            t = cv.part()
            cv.rows(t, [(by + 1, cx - 14, cx - 9), (by + 2, cx - 16, cx - 12), (by + 3, cx - 17, cx - 15), (by + 2, cx - 18, cx - 18)], lit(body, dark_from=cx - 10))
        else:
            t = cv.part()
            cv.rows(t, [(by, cx - 12, cx - 9), (by + 1, cx - 13, cx - 10)], body[1])
        b = cv.part()                                                       # body
        if st["wing"] == "ray":
            cv.rows(b, [(by, cx - 12, cx + 12), (by + 1, cx - 9, cx + 13), (by + 2, cx - 5, cx + 10)], lit(body, dark_from=cx + 9, light_to=cx - 4, light_rows=by))
            tl = cv.part()
            cv.pix(tl, line(cx - 12, by + 1, cx - 18, by + 4), body[2])
        elif st.get("long"):
            cv.rows(b, [(by - 1, cx - 8, cx + 8), (by, cx - 9, cx + 9), (by + 1, cx - 9, cx + 9), (by + 2, cx - 7, cx + 7)], lit(body, dark_from=cx + 7, light_to=cx - 3, light_rows=by - 1))
            bl = cv.part(sep=False)
            cv.rect(bl, cx - 6, by + 2, cx + 6, by + 2, TAN[0])
        else:
            cv.rows(b, [(by - 2, cx - 6, cx + 6), (by - 1, cx - 8, cx + 8)] + [(y, cx - 9, cx + 9) for y in range(by, by + 3)] + [(by + 3, cx - 8, cx + 7), (by + 4, cx - 6, cx + 5)],
                    lit(body, dark_from=cx + 7, light_to=cx - 3, light_rows=by - 1))
            for x0 in (cx - 6, cx + 3):                                     # legs tucked under
                l = cv.part()
                cv.rect(l, x0, by + 5, x0 + 1, by + 7, body[2])
                cv.pix(l, [(x0 + 2, by + 7)], BONE[0])
        hx, hy = cx + 9, by - 3                                             # head
        h = cv.part()
        hd = st["head"]
        hr = WHITE if st.get("white_head") else body
        if hd == "beak":
            cv.rows(h, [(hy - 3, hx, hx + 3), (hy - 2, hx - 1, hx + 4), (hy - 1, hx - 1, hx + 4), (hy, hx - 1, hx + 3), (hy + 1, hx - 2, hx + 2), (hy + 2, hx - 2, hx + 1)], lit(hr, dark_from=hx + 3, light_to=hx))
            k = cv.part()
            cv.rows(k, [(hy - 1, hx + 5, hx + 7), (hy, hx + 4, hx + 6)], GOLD[1])
        elif hd == "bat":
            cv.rows(h, [(hy - 2, hx, hx + 3), (hy - 1, hx - 1, hx + 4), (hy, hx - 1, hx + 5), (hy + 1, hx - 2, hx + 3), (hy + 2, hx - 2, hx + 1)], lit(hr, dark_from=hx + 3, light_to=hx))
            e = cv.part()
            cv.pix(e, [(hx, hy - 3), (hx, hy - 4), (hx + 3, hy - 3), (hx + 3, hy - 4)], hr[1])
        elif hd == "crest":
            cv.rows(h, [(hy - 2, hx, hx + 3), (hy - 1, hx - 1, hx + 7), (hy, hx - 1, hx + 9), (hy + 1, hx - 2, hx + 3), (hy + 2, hx - 2, hx + 1)], lit(hr, dark_from=hx + 5, light_to=hx))
            c = cv.part(1)
            cv.pix(c, [(hx - 1, hy - 3), (hx - 2, hy - 4), (hx - 3, hy - 5), (hx - 2, hy - 3)], TINT[0])
        elif hd in ("dragon", "snout", "two"):
            for dy in ((0, -6) if hd == "two" else (0,)):
                hh = cv.part()
                cv.rows(hh, [(hy - 3 + dy, hx, hx + 3), (hy - 2 + dy, hx - 1, hx + 6), (hy - 1 + dy, hx - 1, hx + 8), (hy + dy, hx - 1, hx + 5), (hy + 1 + dy, hx - 2, hx + 7), (hy + 2 + dy, hx - 2, hx + 1)],
                        lit(hr, dark_from=hx + 5, light_to=hx))
                e = cv.part(sep=False)
                cv.put(e, hx + 3, hy - 2 + dy, (st.get("glow") or GLOW)[0] if st.get("glow") else DARK)
                cv.pix(e, [(hx + 6, hy + dy), (hx + 4, hy + dy)], BONE[0])
                if hd == "dragon":
                    hn = cv.part()
                    cv.pix(hn, [(hx - 1, hy - 4 + dy), (hx - 2, hy - 5 + dy), (hx + 1, hy - 4 + dy)], BONE[1])
        if hd in ("beak", "bat", "crest"):
            e = cv.part(sep=False)
            cv.put(e, hx + 2, hy - 1, (st.get("glow") or GLOW)[0] if st.get("glow") else DARK)
        if st.get("antlers"):
            a = cv.part()
            cv.pix(a, [(hx, hy - 4), (hx - 1, hy - 5), (hx - 1, hy - 6), (hx + 1, hy - 5), (hx - 3, hy - 6)], BONE[0])
        if st.get("mane"):
            m = cv.part(st["mane"])
            cv.pix(m, [(x, by - 2) for x in range(cx - 7, cx + 8, 2)] + [(x, by - 3) for x in range(cx - 6, cx + 8, 4)], TINT[0])
        if st.get("glow") and st["wing"] != "ray":
            g = cv.part(sep=False)
            cv.pix(g, [(cx - 5, by), (cx - 1, by + 1), (cx + 3, by)], st["glow"][1])
        if st["wing"] == "ray":
            g = cv.part(sep=False)
            cv.pix(g, [(cx + 10, by), (cx - 6, by - 2), (cx + 4, by - 2), (cx - 1, by - 3)], st["glow"][0])
        if st.get("rider"):
            ry = by - 2 if st["wing"] != "ray" else by - 4
            tb = cv.part(2)
            cv.rect(tb, cx - 3, ry - 6, cx + 2, ry - 1, lit(TINT, dark_from=cx + 1, light_to=cx - 2, light_rows=ry - 4))
            UA.head(cv, cx, ry - 13)
            lg = cv.part()
            cv.rect(lg, cx - 1, ry, cx + 1, ry + 3, LEATHER[1])
            ar = cv.part()
            cv.rect(ar, cx + 2, ry - 5, cx + 5, ry - 4, LEATHER[1])
    return f


def skiff(glow=ARCANE, hull_r=PALEW):
    """A small flying boat: a hull held up by a glowing crystal, a swept sail in the faction's colour."""
    def f(cv, cx=CX):
        cv.shadow(cx, 9, FY + 2)
        s = cv.part(2)
        cv.rows(s, [(6 + k, cx - 6 - k // 2, cx - 5 + k) for k in range(10)], lit(TINT, dark_from=cx + 1, light_to=cx - 5))
        UM.mast(cv, cx - 6, 5, 18)
        h = cv.part()
        cv.rows(h, [(19, cx - 11, cx + 12), (20, cx - 10, cx + 11), (21, cx - 9, cx + 9), (22, cx - 7, cx + 7)], lit(hull_r, dark_from=cx + 9, light_to=cx - 6, light_rows=19))
        t = cv.part(1, sep=False)
        cv.rect(t, cx - 10, 20, cx + 10, 20, TINT[1])
        c = cv.part()
        cv.rows(c, [(23, cx - 1, cx + 1), (24, cx - 2, cx + 2), (25, cx - 1, cx + 1), (26, cx, cx)], lit(glow, dark_from=cx + 1, light_to=cx - 1))
        g = cv.part()
        cv.pix(g, [(cx - 4, 26), (cx + 4, 25), (cx, 28)], glow[0])
    return f


def kite(cv, cx=CX):
    """A scout slung under a great paper kite in the faction's colours."""
    cv.shadow(cx, 7, FY + 2)
    k = cv.part(2)
    cv.rows(k, [(4, cx - 1, cx + 1), (5, cx - 4, cx + 4), (6, cx - 8, cx + 8), (7, cx - 12, cx + 12), (8, cx - 9, cx + 9), (9, cx - 5, cx + 5), (10, cx - 2, cx + 2)], lit(TINT, dark_from=cx + 6, light_to=cx - 4))
    t = cv.part(1, sep=False)
    cv.rect(t, cx, 4, cx, 10, TINT[0])
    cv.rect(t, cx - 12, 7, cx + 12, 7, TINT[1])
    r = cv.part(sep=False)
    r2 = cv.part()
    cv.pix(r2, line(cx - 6, 9, cx - 2, 15) + line(cx + 6, 9, cx + 2, 15), WOOD[2])
    UA.head(cv, cx, 13)
    b = cv.part()
    cv.rect(b, cx - 3, 20, cx + 3, 25, lit(LEATHER, dark_from=cx + 2, light_to=cx - 2))
    l = cv.part()
    cv.rect(l, cx - 3, 26, cx - 1, 29, TAN[1])
    cv.rect(l, cx + 1, 26, cx + 3, 28, TAN[2])


def zeppelin(bomb=False, spikes=False):
    def f(cv, cx=CX, fy=FY):
        UM.airship_tender(cv, cx, fy)
        if spikes:
            s = cv.part()
            cv.pix(s, [(44, 6), (45, 6), (44, 9), (45, 9), (20, 1), (30, 1)], BONE[0])
        if bomb:
            b = cv.part()
            cv.rows(b, [(27, 21, 23), (28, 20, 24), (29, 20, 24), (30, 21, 23)], lit(BLACK, dark_from=24, light_to=21))
            cv.pix(b, [(22, 26)], FLAME[0])
    return f


# ================================================================ which design each roster unit uses
SPECIAL = {
    # heavy
    "Kodo Beast": (war_beast("kodo", "drums"), "mount"), "War Kodo": (war_beast("kodo", "howdah"), "mount"),
    "War Bear": (war_beast("bear", "pack"), "mount"), "Thornspeaker Bear": (war_beast("bear", "pack"), "mount"),
    "Druid of the Claw": (war_beast("bear", "pack"), "mount"), "Brutosaur": (war_beast("direhorn", "howdah"), "mount"),
    "Mushan Beast": (war_beast("yak", "howdah"), "mount"), "Dragon Turtle": (war_beast("turtle", "pack"), "mount"),
    "Devilsaur Siege Beast": (war_beast("devilsaur", "siege"), "mount"),
    "Ogre Brute": (brute("club"), "machine"), "Ogre Mauler": (brute("club", heads=2), "machine"),
    "Abomination": (brute("cleaver", stitched=True), "machine"), "Flesh Giant": (brute("cleaver", stitched=True), "machine"),
    "Flesh Titan": (brute("cleaver", heads=2, stitched=True), "machine"),
    "Ancient of War": (treant(), "machine"), "Ancient Stone Thrower": (treant(thrower=True), "machine"), "Mountain Giant": (treant(stone=True), "machine"),
    "Steam Armor": (golem(FLAME), "machine"), "Dark Iron Golem": (golem(FLAME, ramp=IRON), "machine"),
    "Molten Colossus": (golem(FLAME, ramp=IRON, crown=True), "machine"), "Crystal Golem": (golem(ARCANE, head="crystal"), "machine"),
    "Lightforged Warframe": (golem(GLOW, head="crystal", crown=True), "machine"), "Harvest Golem": (golem(GLOW, arm="blade", head="pumpkin", ramp=WOOD), "machine"),
    "Arcane Golem": (golem(ARCANE, head="crystal"), "machine"), "Arcane Construct": (golem(ARCANE, head="crystal"), "machine"),
    "Fel Reaver": (golem(FEL, arm="blade", crown=True), "machine"), "Felbound Construct": (golem(FEL, head="crystal"), "machine"),
    "Iron Lumberjack": (golem(FLAME, arm="saw"), "machine"), "Iron Shredder": (golem(FLAME, arm="saw", crown=True), "machine"),
    "Jade Serpent Guardian": (golem(((190, 250, 200), (110, 210, 150), (60, 140, 110)), head="crystal", ramp=LEAF), "machine"),
    "Tidal Guardian": (golem(AZER, head="crystal", ramp=AZER), "machine"), "Obsidian Statue": (golem(FROST, head="box", ramp=CLOTHD), "machine"),
    "Spider Tank": (spider_tank, "machine"), "Azerite War Machine": (UM.siege_engine, "machine"),
    # aerial
    "Gryphon Rider": (flyer("gryphon"), "air"), "Stormhammer Rider": (flyer("gryphon"), "air"), "Wind Rider": (flyer("wyvern"), "air"),
    "Thunder Wyvern": (flyer("thunder"), "air"), "Hippogryph Rider": (flyer("hippogryph"), "air"), "Silver Covenant Hippogryph": (flyer("hippogryph"), "air"),
    "Chimaera": (flyer("chimaera"), "air"), "Batrider": (flyer("bat"), "air"), "Bat Lord": (flyer("bat"), "air"), "Bat Rider": (flyer("bat"), "air"),
    "Plague Bat Bomber": (flyer("bat"), "air"), "Dragonhawk Scout": (flyer("dragonhawk"), "air"), "Dragonhawk Rider": (flyer("dragonhawk"), "air"),
    "Phoenix": (flyer("phoenix"), "air"), "Pterrordax Rider": (flyer("pterrordax"), "air"), "Pa'ku's Windrider": (flyer("pterrordax"), "air"),
    "Skyhorn Eagle Rider": (flyer("eagle"), "air"), "Great Eagle Warrior": (flyer("eagle"), "air"), "Nether Ray Rider": (flyer("ray"), "air"),
    "Manaray Rider": (flyer("ray"), "air"), "Cloud Serpent Rider": (flyer("serpent"), "air"), "Couatl": (flyer("couatl"), "air"),
    "Storm Couatl": (flyer("couatl"), "air"), "Gargoyle": (flyer("gargoyle"), "air"), "Frost Wyrm": (flyer("wyrm"), "air"),
    "Gyrocopter": (UM.flying_machine, "air"), "Flying Machine": (UM.flying_machine, "air"), "Gnomish Bomber": (UM.flying_machine, "air"),
    "Gunship": (zeppelin(), "air"), "Zeppelin": (zeppelin(spikes=True), "air"), "Goblin Zeppelin": (zeppelin(bomb=True), "air"),
    "Rocket Bomber": (zeppelin(bomb=True, spikes=True), "air"), "Vindicaar Skiff": (skiff(GLOW), "air"), "Arcane Skiff": (skiff(ARCANE, VIOLETW), "air"),
    "Kite Scout": (kite, "air"),
}
SHIP_STYLE = {"Night Elves": "nightelf", "High Elves": "elf", "Blood Elves": "elf", "Kul Tirans": "navy", "Trolls": "troll", "Zandalari Trolls": "zandalari",
              "Goblins": "goblin", "Pandaren": "pandaren", "Scourge": "ghost"}
HORDE_SHIPS = ("Raider Longboat", "Destroyer", "Juggernaught")


def icon(layers):
    """A white unit icon cut from a sprite: brighter parts of the drawing are more opaque."""
    from PIL import Image
    g = [im.crop((0, 0, 188, 160)).resize((47, 40), Image.NEAREST) for im in layers]
    flat = g[0].copy()
    for extra, col in ((g[1], (200, 200, 200)), (g[2], (150, 150, 150))):
        px = extra.load()
        for y in range(40):
            for x in range(47):
                if px[x, y][3]:
                    v = px[x, y][0] * col[0] // 255
                    flat.putpixel((x, y), (v, v, v, 255))
    src = flat.load()
    out = Image.new("RGBA", (47, 40), (0, 0, 0, 0))
    o = out.load()
    for y in range(40):
        for x in range(47):
            r, gg, b, a = src[x, y]
            if a < 200 or (r, gg, b) == UA.INK:
                continue
            o[x, y] = (255, 255, 255, 175 + (r * 3 + gg * 6 + b) * 80 // 2550)
    box = out.getbbox()
    if not box:
        return None
    crop = out.crop(box)
    k = max(1, min(92 // crop.width, 92 // crop.height))
    crop = crop.resize((crop.width * k, crop.height * k), Image.NEAREST)
    canvas = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    canvas.alpha_composite(crop, ((100 - crop.width) // 2, (100 - crop.height) // 2))
    return canvas
