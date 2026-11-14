"""Tech tree icons (Nov 2026): bold pixel-art emblems, one per technology.

Each icon is drawn on a 32x32 grid in three tones (bright, mid, cut-out) and scaled up without smoothing,
so it reads at the size of a tech-tree button. The motifs are the stuff of the setting: war mounts,
hammers and anvils, runes, crystals, gears, powder kegs, airships. All drawings are original.
"""
import os

from PIL import Image, ImageDraw

N = 32
B, M, C = 255, 165, 0                     # bright, mid, cut-out


class Ic:
    def __init__(self):
        self.im = Image.new("L", (N, N), 0)
        self.d = ImageDraw.Draw(self.im)

    def R(self, x0, y0, x1, y1, t=B):
        self.d.rectangle([x0, y0, x1, y1], fill=t)
        return self

    def E(self, cx, cy, rx, ry=None, t=B):
        ry = rx if ry is None else ry
        self.d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=t)
        return self

    def L(self, pts, w=2, t=B):
        self.d.line(pts, fill=t, width=w)
        return self

    def P(self, pts, t=B):
        self.d.polygon(pts, fill=t)
        return self

    def ring(self, cx, cy, r, w=2, t=B):
        self.E(cx, cy, r, t=t)
        return self.E(cx, cy, r - w, t=C)

    def gear(self, cx, cy, r, teeth=8, hole=True):
        import math
        for k in range(teeth):
            a = k * 2 * math.pi / teeth
            x, y = cx + (r + 1) * math.cos(a), cy + (r + 1) * math.sin(a)
            self.R(int(round(x - 1.5)), int(round(y - 1.5)), int(round(x + 1.5)), int(round(y + 1.5)))
        self.E(cx, cy, r)
        self.E(cx, cy, r - 3, t=M)
        if hole:
            self.E(cx, cy, max(1, r // 3), t=C)
        return self

    def star(self, cx, cy, r, t=B):
        return self.P([(cx, cy - r), (cx + r // 3, cy - r // 3), (cx + r, cy), (cx + r // 3, cy + r // 3), (cx, cy + r), (cx - r // 3, cy + r // 3), (cx - r, cy), (cx - r // 3, cy - r // 3)], t)

    def sword(self, x, top=2, bottom=29, t=B):
        self.P([(x, top), (x + 2, top + 3), (x + 2, bottom - 8), (x - 1, bottom - 8), (x - 1, top + 3)], t)
        self.R(x - 5, bottom - 8, x + 6, bottom - 6, t)
        self.R(x - 1, bottom - 5, x + 2, bottom - 2, M)
        return self.R(x - 2, bottom - 1, x + 3, bottom, t)

    def hammer(self, x, top=3, bottom=29, w=8, t=B):
        self.R(x - 1, top + 6, x + 1, bottom, M)
        self.R(x - w, top, x + w, top + 8, t)
        self.R(x - w, top + 3, x + w, top + 4, M)
        return self

    def crystal(self, cx, top, bottom, w=5, t=B):
        mid = top + (bottom - top) // 3
        self.P([(cx, top), (cx + w, mid), (cx + w // 2, bottom), (cx - w // 2, bottom), (cx - w, mid)], t)
        return self.P([(cx, top), (cx + w, mid), (cx + w // 2, bottom), (cx, bottom)], M)

    def flask(self, cx, cy, r=8):
        self.R(cx - 2, cy - r - 7, cx + 2, cy - r + 2)
        self.R(cx - 4, cy - r - 8, cx + 4, cy - r - 6)
        self.E(cx, cy, r)
        self.d.pieslice([cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2], 0, 180, fill=M)
        return self.E(cx - 3, cy - 3, 1, t=B)

    def tower(self, x0, x1, top, bottom):
        self.R(x0, top + 3, x1, bottom)
        for x in range(x0 - 1, x1 + 1, 4):
            self.R(x, top, x + 1, top + 2)
        self.R(x0 - 1, top + 3, x1 + 1, top + 4)
        return self

    def ship(self, y=24):
        self.P([(3, y - 4), (29, y - 4), (25, y + 2), (7, y + 2)])
        self.R(15, 4, 16, y - 5, M)
        self.P([(17, 6), (26, 16), (17, 18)])
        self.P([(14, 8), (14, 18), (6, 18)], M)
        return self.L([(2, y + 4), (8, y + 5), (14, y + 4), (20, y + 5), (29, y + 4)], 1, M)

    def bolt(self, x, top, bottom, t=B):
        h = bottom - top
        return self.P([(x + 3, top), (x - 4, top + h // 2 + 1), (x, top + h // 2 + 1), (x - 3, bottom), (x + 5, top + h // 2 - 2), (x + 1, top + h // 2 - 2)], t)

    def flame(self, cx, bottom, h=14, t=B):
        self.P([(cx, bottom - h), (cx + 5, bottom - h // 2), (cx + 6, bottom - 3), (cx + 3, bottom), (cx - 3, bottom), (cx - 6, bottom - 3), (cx - 4, bottom - h // 2 - 1), (cx - 1, bottom - h // 2 + 2)], t)
        return self.P([(cx, bottom - h // 2), (cx + 3, bottom - 3), (cx + 1, bottom), (cx - 2, bottom), (cx - 3, bottom - 3)], M)

    def book(self, cx=16, cy=17):
        self.P([(cx - 12, cy - 6), (cx - 1, cy - 4), (cx - 1, cy + 8), (cx - 12, cy + 6)])
        self.P([(cx + 12, cy - 6), (cx + 1, cy - 4), (cx + 1, cy + 8), (cx + 12, cy + 6)], M)
        for k in (0, 3, 6):
            self.L([(cx - 10, cy - 3 + k), (cx - 3, cy - 2 + k)], 1, C)
            self.L([(cx + 10, cy - 3 + k), (cx + 3, cy - 2 + k)], 1, C)
        return self

    def keg(self, cx, cy, rx=7, ry=9):
        self.E(cx, cy, rx, ry)
        self.R(cx - rx, cy - 4, cx + rx, cy - 3, M)
        self.R(cx - rx, cy + 3, cx + rx, cy + 4, M)
        return self


def _horse(i):
    i.P([(8, 30), (8, 19), (10, 12), (14, 7), (16, 2), (18, 7), (22, 9), (28, 15), (28, 19), (24, 20), (20, 17), (19, 21), (21, 30)])
    i.P([(8, 19), (10, 12), (14, 7), (12, 6), (8, 10), (5, 17), (5, 24), (8, 24)], M)
    i.E(20, 11, 1, t=C)
    i.R(26, 16, 27, 17, C)
    return i.L([(18, 18), (25, 13)], 1, C)


def _wolf(i):
    # a wolf's face, head on: tall ears, slanted eyes, narrow muzzle
    i.P([(4, 1), (11, 8), (21, 8), (28, 1), (28, 13), (31, 19), (24, 22), (20, 30), (12, 30), (8, 22), (1, 19), (4, 13)])
    i.P([(6, 5), (10, 9), (7, 12)], M).P([(26, 5), (22, 9), (25, 12)], M)
    i.P([(12, 20), (20, 20), (19, 29), (13, 29)], M)
    i.P([(7, 14), (13, 17), (9, 18)], C).P([(25, 14), (19, 17), (23, 18)], C)
    i.R(14, 25, 18, 27, C)
    return i.P([(13, 30), (14, 27), (15, 30)], B).P([(17, 30), (18, 27), (19, 30)], B)


def _anvil(i, y=12):
    i.P([(3, y), (26, y), (26, y + 4), (20, y + 5), (19, y + 9), (23, y + 13), (23, y + 16), (8, y + 16), (8, y + 13), (12, y + 9), (11, y + 5), (3, y + 4)])
    i.P([(26, y), (30, y + 1), (26, y + 4)], M)
    return i.R(8, y + 14, 23, y + 16, M)


def _bow(i):
    i.L([(9, 4), (16, 8), (20, 16), (16, 24), (9, 28)], 3)
    i.L([(9, 4), (9, 28)], 1, M)
    i.L([(5, 16), (27, 16)], 2, M)
    return i.P([(27, 12), (31, 16), (27, 20)])


def _wheel(i, cx=16, cy=16, r=13):
    i.ring(cx, cy, r, 3)
    for a, b in (((cx - r, cy), (cx + r, cy)), ((cx, cy - r), (cx, cy + r)), ((cx - 9, cy - 9), (cx + 9, cy + 9)), ((cx - 9, cy + 9), (cx + 9, cy - 9))):
        i.L([a, b], 2, M)
    return i.E(cx, cy, 3)


def _pick(i):
    i.L([(7, 28), (22, 9)], 3, M)
    i.P([(10, 5), (20, 4), (28, 10), (29, 18), (25, 12), (19, 9), (12, 9)])
    return i


def _pot(i):
    i.E(16, 19, 10, 9)
    i.R(10, 6, 22, 11)
    i.R(8, 5, 24, 7)
    i.L([(7, 17), (25, 17)], 2, M)
    return i.L([(8, 21), (11, 19), (14, 21), (17, 19), (20, 21), (23, 19)], 1, C)


def _wheat(i):
    i.L([(16, 30), (16, 8)], 2, M)
    for y in (6, 11, 16, 21):
        i.P([(16, y + 4), (9, y), (10, y - 4)])
        i.P([(16, y + 4), (23, y), (22, y - 4)])
    return i.P([(16, 8), (13, 3), (16, 0), (19, 3)])


def _paw(i):
    i.E(16, 21, 7, 6)
    for x, y in ((7, 13), (13, 8), (20, 8), (26, 13)):
        i.E(x, y, 3, 4)
    return i


def _leaf(i, cx=16):
    i.P([(cx, 2), (cx + 9, 10), (cx + 9, 19), (cx, 27), (cx - 9, 19), (cx - 9, 10)])
    i.P([(cx, 2), (cx + 9, 10), (cx + 9, 19), (cx, 27)], M)
    i.L([(cx, 5), (cx, 30)], 1, C)
    return i.L([(cx, 14), (cx + 6, 9)], 1, C).L([(cx, 19), (cx - 6, 14)], 1, C)


def _rune(i):
    i.P([(9, 30), (7, 8), (12, 2), (20, 2), (25, 8), (23, 30)])
    i.P([(16, 2), (20, 2), (25, 8), (23, 30), (16, 30)], M)
    i.L([(16, 8), (16, 24)], 2, C)
    return i.L([(16, 10), (21, 14), (16, 18)], 2, C).L([(16, 16), (11, 20)], 2, C)


def _hide(i):
    i.P([(6, 3), (12, 6), (20, 6), (26, 3), (24, 11), (28, 15), (23, 17), (25, 28), (19, 24), (13, 24), (7, 28), (9, 17), (4, 15), (8, 11)])
    return i.L([(16, 8), (16, 22)], 1, M)


def _scope(i):
    # a brass spyglass, three draws, with a glint at the lens
    i.P([(2, 25), (10, 17), (14, 21), (6, 29)])
    i.P([(10, 15), (17, 8), (23, 14), (16, 21)], M)
    i.P([(17, 6), (23, 0), (31, 8), (25, 14)])
    i.L([(10, 16), (15, 21)], 1, C).L([(17, 7), (24, 14)], 1, C)
    return i.star(6, 7, 5)


def _lyre(i):
    i.L([(9, 5), (7, 16), (11, 25), (21, 25), (25, 16), (23, 5)], 3)
    i.R(8, 7, 24, 8, M)
    for x in (12, 15, 18, 21):
        i.L([(x, 9), (x, 24)], 1, M)
    return i.R(10, 25, 22, 28)


def _coins(i):
    for y in (26, 21, 16):
        i.E(13, y, 9, 3)
        i.E(13, y - 1, 9, 3, t=M)
    i.E(23, 10, 6)
    i.E(23, 10, 4, t=M)
    return i.R(22, 7, 23, 13, C)


def _scroll(i):
    i.R(7, 6, 25, 26)
    i.E(7, 6, 3, t=M).E(25, 6, 3, t=M).E(7, 26, 3, t=M).E(25, 26, 3, t=M)
    for y in (11, 15, 19):
        i.L([(11, y), (21, y)], 1, C)
    return i


def _scales(i):
    i.R(15, 5, 16, 26)
    i.R(10, 26, 21, 28)
    i.L([(5, 9), (26, 9)], 2)
    for x in (6, 25):
        i.L([(x, 9), (x - 4, 18)], 1, M).L([(x, 9), (x + 4, 18)], 1, M)
        i.d.pieslice([x - 5, 14, x + 5, 22], 0, 180, fill=B)
    return i.E(15, 5, 2)


def _cart(i):
    i.P([(4, 10), (26, 10), (24, 21), (6, 21)])
    i.R(4, 10, 26, 12, M)
    i.E(10, 24, 4).E(10, 24, 1, t=C).E(21, 24, 4).E(21, 24, 1, t=C)
    return i.R(9, 4, 20, 9, M)


def _cannon(i):
    i.P([(5, 12), (27, 9), (27, 16), (5, 19)])
    i.R(26, 8, 29, 17, M)
    i.E(5, 15, 3)
    i.E(13, 23, 6).E(13, 23, 2, t=C)
    return i.L([(13, 23), (3, 28)], 2, M)


def _rifle(i):
    i.P([(2, 20), (9, 15), (30, 9), (30, 12), (12, 18), (10, 22), (5, 26)])
    i.P([(2, 20), (9, 15), (12, 18), (10, 22), (5, 26)], M)
    return i.L([(13, 18), (15, 22), (18, 20)], 1)


def _compass(i):
    i.ring(16, 16, 13, 2)
    i.P([(16, 4), (19, 16), (16, 28), (13, 16)])
    i.P([(16, 16), (19, 16), (16, 28)], M)
    return i.E(16, 16, 1, t=C)


def _arch(i):
    i.R(5, 8, 27, 28)
    i.E(16, 18, 6, t=C).R(10, 18, 22, 28, C)
    i.R(3, 5, 29, 8)
    i.R(3, 27, 9, 29).R(23, 27, 29, 29)
    return i.R(14, 6, 18, 11, M)


def _gavel(i):
    i.L([(6, 26), (19, 13)], 3, M)
    i.P([(14, 5), (24, 15), (20, 19), (10, 9)])
    i.L([(12, 7), (22, 17)], 1, C)
    return i.R(18, 25, 29, 28)


def _shovel_urn(i):
    i.L([(5, 5), (17, 17)], 2, M)
    i.P([(15, 15), (21, 17), (23, 23), (17, 21)])
    i.E(22, 12, 5, 6).R(19, 4, 25, 7)
    return i.L([(18, 12), (26, 12)], 1, C)


def _boiler(i):
    i.R(6, 12, 22, 27)
    i.E(14, 12, 8, 3)
    i.R(6, 17, 22, 18, M)
    i.R(23, 8, 26, 27, M)
    i.R(22, 6, 27, 8)
    i.E(9, 5, 3, t=M).E(15, 3, 2, t=M)
    return i.E(14, 22, 2, t=C)


def _banner(i, x=16):
    i.R(x - 9, 3, x + 9, 4, M)
    i.P([(x - 8, 5), (x + 8, 5), (x + 8, 24), (x, 19), (x - 8, 24)])
    i.R(x - 8, 8, x + 8, 9, M)
    return i


def _sprout(i):
    i.P([(2, 28), (30, 28), (26, 23), (6, 23)], M)
    i.L([(16, 23), (16, 10)], 2)
    i.P([(16, 13), (8, 11), (6, 4), (13, 6)])
    i.P([(16, 15), (24, 12), (26, 5), (19, 8)])
    return i


def _bomb(i):
    i.E(14, 19, 10)
    i.E(10, 15, 2, t=M)
    i.R(17, 6, 21, 10)
    i.L([(20, 6), (24, 3), (27, 5)], 1, M)
    return i.star(28, 5, 3)


def _snow(i):
    for a, b in (((16, 2), (16, 30)), ((3, 9), (29, 23)), ((3, 23), (29, 9))):
        i.L([a, b], 2)
    for x, y in ((16, 6), (16, 26), (7, 11), (25, 21), (7, 21), (25, 11)):
        i.E(x, y, 2, t=M)
    return i.E(16, 16, 3)


def _rotor(i):
    i.L([(3, 5), (29, 5)], 2)
    i.R(15, 6, 16, 10, M)
    i.E(15, 17, 9, 6)
    i.E(19, 15, 3, 2, t=C)
    i.P([(6, 17), (0, 12), (0, 20)], M)
    return i.L([(9, 26), (22, 26)], 1).L([(12, 23), (12, 26)], 1, M).L([(19, 23), (19, 26)], 1, M)


def _rail(i):
    i.P([(5, 9), (27, 9), (24, 20), (8, 20)])
    i.P([(9, 4), (23, 4), (27, 9), (5, 9)], M)
    i.E(11, 23, 3).E(21, 23, 3)
    return i.L([(1, 28), (31, 28)], 2).L([(5, 30), (5, 28)], 1, M).L([(16, 30), (16, 28)], 1, M).L([(27, 30), (27, 28)], 1, M)


def _ingot(i):
    i.P([(8, 12), (26, 12), (30, 22), (4, 22)])
    i.P([(8, 12), (26, 12), (24, 8), (10, 8)], M)
    return i.star(25, 6, 4)


def _burst(i):
    for a in ((16, 16, 16, 1), (16, 16, 30, 6), (16, 16, 31, 20), (16, 16, 22, 30), (16, 16, 8, 30), (16, 16, 1, 20), (16, 16, 2, 6)):
        i.L([(a[0], a[1]), (a[2], a[3])], 1, M)
    i.star(16, 16, 8)
    for x, y in ((27, 8), (28, 22), (20, 28), (9, 27), (4, 19), (5, 7), (16, 3)):
        i.P([(x, y - 2), (x + 2, y + 1), (x - 2, y + 1)])
    return i


def _orb(i, cx=16, cy=13, r=9):
    i.E(cx, cy, r)
    i.E(cx + 2, cy + 2, r - 3, t=M)
    i.E(cx - 3, cy - 4, 2)
    i.P([(cx - 8, cy + r), (cx + 8, cy + r), (cx + 10, 30), (cx - 10, 30)])
    return i.R(cx - 8, cy + r, cx + 8, cy + r + 1, M)


def _shields(i):
    for x, t in ((9, M), (23, M), (16, B)):
        y = 6 if t == B else 4
        i.P([(x - 6, y), (x + 6, y), (x + 6, y + 12), (x, y + 19), (x - 6, y + 12)], t)
    return i.R(11, 9, 21, 11, M)


def _flower(i):
    for x, y in ((16, 7), (24, 13), (21, 22), (11, 22), (8, 13)):
        i.E(x, y, 5)
    i.E(16, 15, 4, t=M)
    return i.L([(16, 21), (16, 31)], 2, M)


def _dynamite(i):
    for x in (9, 14, 19):
        i.R(x, 10, x + 3, 28)
    i.R(7, 15, 24, 17, M).R(7, 22, 24, 24, M)
    i.L([(16, 10), (16, 5), (21, 3)], 1, M)
    return i.star(24, 4, 3)


def _keystone(i):
    i.P([(16, 2), (30, 28), (2, 28)])
    i.P([(16, 9), (24, 25), (8, 25)], M)
    i.E(16, 20, 3, t=B)
    return i.E(16, 20, 1, t=C)


def _portal(i):
    i.E(16, 16, 11, 14)
    i.E(16, 16, 8, 11, t=C)
    i.L([(16, 8), (20, 12), (19, 18), (14, 20), (12, 15), (15, 12), (17, 15)], 2, M)
    return i.R(4, 29, 28, 30)


def _drum(i):
    i.R(6, 12, 26, 26)
    i.E(16, 12, 10, 4, t=M)
    i.E(16, 26, 10, 3)
    i.L([(6, 14), (11, 25), (16, 16), (21, 25), (26, 14)], 1, C)
    return i.L([(3, 2), (13, 10)], 2).L([(29, 2), (19, 10)], 2)


def _barrage(i):
    # burning stones falling on a breached wall
    for x, y in ((8, 9), (19, 6), (25, 15)):
        i.P([(x - 2, y - 2), (x - 8, y - 9), (x + 1, y - 4)], M)
        i.E(x, y, 3)
    i.R(1, 22, 12, 30).R(20, 22, 31, 30)
    for x in (1, 6, 11, 20, 25, 30):
        i.R(x, 19, x + 1, 21)
    i.P([(12, 30), (12, 26), (15, 28), (17, 25), (20, 27), (20, 30)], M)
    return i


def _eye(i):
    i.P([(1, 16), (9, 8), (16, 6), (23, 8), (31, 16), (23, 24), (16, 26), (9, 24)])
    i.E(16, 16, 7, t=M)
    i.E(16, 16, 3, t=C)
    return i.E(18, 14, 1)


def _robot(i):
    i.R(7, 8, 25, 26)
    i.R(14, 3, 17, 7, M).E(15, 3, 2)
    i.R(3, 13, 6, 20, M).R(26, 13, 29, 20, M)
    i.E(12, 15, 3, t=C).E(20, 15, 3, t=C).E(12, 15, 1).E(20, 15, 1)
    return i.R(11, 21, 21, 22, C)


def _lens(i):
    i.E(10, 16, 7, 10)
    i.E(10, 16, 4, 7, t=M)
    i.P([(16, 14), (30, 15), (30, 17), (16, 18)])
    return i.star(27, 16, 4)


def _rings(i):
    i.ring(11, 16, 9, 3)
    i.ring(21, 16, 9, 3, t=M)
    i.d.arc([2, 7, 20, 25], 300, 60, fill=B, width=3)
    return i


def _cluster(i):
    i.crystal(16, 2, 28, 6)
    i.crystal(7, 12, 28, 4)
    i.crystal(25, 10, 28, 4)
    return i.R(3, 28, 29, 30, M)


def _ghost(i):
    # a cloaked figure seen only as a broken outline
    i.P([(16, 1), (8, 7), (7, 16), (3, 30), (29, 30), (25, 16), (24, 7)])
    i.P([(16, 4), (10, 8), (9, 17), (6, 28), (26, 28), (23, 17), (22, 8)], C)
    for a, b in (((16, 16), (2, 2)), ((16, 16), (30, 2)), ((16, 16), (0, 20)), ((16, 16), (32, 20)), ((16, 20), (10, 32)), ((16, 20), (22, 32)), ((16, 10), (16, 0))):
        i.L([a, b], 3, C)
    i.E(13, 13, 1, t=M).E(19, 13, 1, t=M)
    return i.star(27, 5, 3, M)


def _ether(i):
    # a wrapped being of energy: bandaged head with burning eyes
    i.E(16, 14, 11, 13)
    for y in (4, 11, 19):
        i.L([(4, y + 5), (28, y)], 2, C)
    i.E(11, 13, 2, t=M).E(21, 11, 2, t=M)
    i.P([(11, 27), (21, 27), (25, 31), (7, 31)], M)
    return i.star(28, 26, 3, M).star(4, 3, 2, M)


def _axe(i):
    # a double-bladed war axe
    i.R(15, 2, 16, 30, M)
    i.P([(14, 5), (8, 2), (2, 8), (2, 16), (8, 22), (14, 19)])
    i.P([(18, 5), (24, 2), (30, 8), (30, 16), (24, 22), (18, 19)])
    i.L([(5, 8), (5, 16)], 1, M).L([(27, 8), (27, 16)], 1, M)
    return i.R(13, 10, 19, 14).P([(14, 2), (16, 0), (18, 2)])


def _maths(i):
    # dividers over a measured arc
    i.L([(16, 3), (6, 27)], 3).L([(16, 3), (26, 27)], 3)
    i.E(16, 4, 3)
    i.d.arc([4, 14, 28, 34], 200, 340, fill=M, width=2)
    return i.R(10, 14, 22, 15, M)


def _commcrystal(i):
    i.crystal(16, 6, 29, 5)
    for r in (9, 14):
        i.d.arc([16 - r, 12 - r, 16 + r, 12 + r], 205, 245, fill=M, width=2)
        i.d.arc([16 - r, 12 - r, 16 + r, 12 + r], 295, 335, fill=M, width=2)
    return i


def _void(i):
    import math
    for k in range(8):
        a = k * math.pi / 4 + 0.3
        x1, y1 = 16 + 9 * math.cos(a), 16 + 9 * math.sin(a)
        x2, y2 = 16 + 15 * math.cos(a + 0.5), 16 + 15 * math.sin(a + 0.5)
        i.L([(x1, y1), (x2, y2)], 2, M)
    i.E(16, 16, 9)
    i.E(16, 16, 6, t=C)
    return i.E(16, 16, 2, t=M)


ICONS = {
    "Farming": _wheat, "Pottery": _pot, "Beast Taming": _paw, "Archery": _bow, "Mining": _pick,
    "Sailing": lambda i: i.ship(), "Herbalism": _leaf, "Runic Script": _rune, "Skinning": _hide, "The Wheel": _wheel,
    "Masonry": lambda i: i.tower(8, 23, 4, 29).R(13, 20, 18, 29, C).R(10, 12, 12, 16, C).R(19, 12, 21, 16, C),
    "Bronze Working": _axe,
    "Optics": _scope, "Riding": _horse,
    "Mathematics": _maths,
    "Construction": lambda i: i.hammer(11, 3, 29, 7).P([(20, 6), (30, 10), (27, 14), (24, 12), (20, 28), (17, 27), (21, 11), (18, 9)], M),
    "Philosophy": lambda i: _scroll(i).P([(22, 2), (29, 0), (26, 9), (20, 16), (19, 13)], B),
    "Bardic Lore": _lyre, "Coinage": _coins,
    "Engineering": lambda i: i.gear(13, 18, 8).gear(24, 8, 4, 6),
    "Iron Forged Swords": lambda i: i.sword(15),
    "Priesthood": lambda i: i.flame(16, 20, 17).P([(8, 21), (24, 21), (21, 30), (11, 30)]).R(7, 20, 25, 22, M),
    "Arathi Law": _scales, "Trade Guilds": _cart,
    "Blacksmithing": lambda i: _anvil(i, 14).R(14, 2, 24, 7).R(18, 7, 19, 12, M),
    "Seafaring": lambda i: i.ring(16, 11, 5, 2).R(15, 15, 16, 28).R(10, 18, 21, 19).d.arc([4, 12, 28, 30], 20, 160, fill=B, width=3) or i.P([(3, 20), (7, 19), (6, 25)]).P([(29, 20), (25, 19), (26, 25)]),
    "Scholarship": lambda i: i.book(),
    "Animal War Training": _wolf,
    "Clockwork": lambda i: i.ring(16, 16, 14, 3).L([(16, 16), (16, 6)], 2).L([(16, 16), (23, 19)], 2, M).E(16, 16, 2),
    "Siege Engineering": lambda i: i.L([(4, 6), (22, 20)], 2).E(5, 6, 3).R(17, 10, 19, 22, M).R(6, 21, 27, 23).E(11, 26, 4).E(11, 26, 1, t=C).E(23, 26, 4).E(23, 26, 1, t=C),
    "Steel Forged Swords": lambda i: i.L([(5, 4), (25, 24)], 3).L([(27, 4), (7, 24)], 3).L([(19, 24), (27, 16)], 2, M).L([(13, 24), (5, 16)], 2, M).E(26, 27, 2).E(6, 27, 2),
    "Astronomy": lambda i: i.E(13, 16, 11).E(18, 13, 10, t=C).star(23, 9, 5).star(25, 23, 3, M),
    "Choral Hymns": lambda i: i.E(9, 24, 4, 3).E(22, 21, 4, 3).R(12, 7, 13, 24).R(25, 4, 26, 21).P([(12, 7), (26, 4), (26, 9), (12, 12)], M),
    "Banking": lambda i: i.P([(16, 2), (30, 10), (2, 10)]).R(4, 25, 28, 29).R(6, 12, 9, 24, M).R(12, 12, 15, 24, M).R(18, 12, 21, 24, M).R(24, 12, 27, 24, M),
    "Inscription": lambda i: i.P([(27, 1), (30, 5), (14, 22), (9, 25), (10, 19)]).P([(27, 1), (30, 5), (22, 10), (20, 7)], M).L([(3, 29), (20, 29)], 2).L([(9, 25), (6, 28)], 1),
    "Blackpowder": lambda i: i.keg(14, 19, 9, 10).L([(14, 9), (17, 4), (22, 4)], 1, M).star(25, 4, 4),
    "Navigation": _compass, "Architecture": _arch, "Auctioneering": _gavel,
    "Mithril Forged Swords": lambda i: i.sword(15, 1, 30).star(25, 6, 5).star(6, 12, 3, M),
    "Alchemy": lambda i: i.flask(16, 20, 9).E(22, 6, 2, t=M).E(26, 2, 1, t=M),
    "Archaeology": _shovel_urn,
    "Arcane Science": lambda i: i.ring(16, 16, 14, 2).star(16, 16, 10).E(16, 16, 3, t=C),
    "Steamworks": _boiler, "Long Rifles": _rifle,
    "War Doctrine": lambda i: _banner(i, 16).P([(16, 8), (19, 12), (16, 16), (13, 12)], C).R(15, 24, 16, 30, M),
    "Soil Enrichment": _sprout,
    "Natural Lore": lambda i: _leaf(i, 11).E(24, 22, 4, 3).E(20, 16, 2).E(24, 14, 2).E(28, 16, 2),
    "Storm Hammers": lambda i: i.hammer(12, 3, 29, 7).bolt(25, 3, 24),
    "Steam Power": lambda i: i.gear(16, 19, 9).E(8, 6, 3, t=M).E(15, 3, 3, t=M).E(22, 6, 3, t=M),
    "Seaforium": _bomb, "Frost Enchantment": _snow,
    "Communication Crystals": _commcrystal,
    "Gnomish Gearworks": lambda i: i.gear(11, 11, 6).gear(22, 14, 5, 6).gear(13, 24, 4, 6),
    "Gnomish Flight": _rotor, "Tramways": _rail, "Arcanite Alloys": _ingot,
    "Arcane Conduits": lambda i: i.R(11, 2, 21, 5).R(11, 27, 21, 30).R(13, 6, 19, 26, M).bolt(15, 7, 25),
    "Fragmentation Shards": _burst,
    "Liquid Fire": lambda i: i.P([(16, 1), (25, 15), (25, 22), (20, 29), (12, 29), (7, 22), (7, 15)]).flame(16, 27, 14, C),
    "Elixir Mastery": lambda i: i.flask(10, 21, 7).flask(23, 19, 6),
    "Mana Theory": lambda i: i.P([(16, 1), (25, 16), (24, 23), (16, 30), (8, 23), (7, 16)]).star(16, 19, 6, M).E(16, 19, 1, t=C),
    "Scrying": _orb, "Battle Formations": _shields, "Nature's Blessing": _flower,
    "Unstable Mana": lambda i: i.E(16, 17, 11).L([(13, 6), (17, 14), (13, 19), (19, 28)], 2, C).star(27, 5, 4).star(4, 9, 3, M).star(28, 26, 3, M),
    "Demolition": _dynamite, "Titan Logic": _keystone, "Portal Networks": _portal, "War Drums": _drum, "Siege Barrage": _barrage,
    "Eye of Kilrogg": _eye, "Mechagnomics": _robot, "Focused Arcana": _lens, "Azerothian Unity": _rings, "Azerite Refinement": _cluster,
    "Titanforging": lambda i: _anvil(i, 15).star(16, 7, 7),
    "Ethereal Technology": _ether,
    "Invisibility": _ghost, "Secrets of the Void": _void,
}


def render(name):
    i = Ic()
    ICONS[name](i)
    a = i.im.resize((N * 3, N * 3), Image.NEAREST)
    out = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    white = Image.new("RGBA", a.size, (255, 255, 255, 255))
    white.putalpha(a)
    out.alpha_composite(white, (2, 2))
    return out


def write_all(folder):
    n = 0
    if not os.path.isdir(folder):
        return 0
    for name in ICONS:
        render(name).save(os.path.join(folder, name + ".png"))
        n += 1
    return n
