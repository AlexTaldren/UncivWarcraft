"""Building icons (Nov 2026): pixel-art emblems in the same hand as the tech icons.

Each building gets a main motif drawn on the 32x32 grid, and where two buildings share a motif a small
corner mark (star, flame, skull, moon...) tells them apart. Icons are black with a mid tone, as the game
draws building icons untinted. All drawings are original.
"""
import math
import os

from PIL import Image

import tech_icons as TI
from tech_icons import B, M, C, N, Ic


# ---------------------------------------------------------------- structures
def hall(i):
    i.P([(1, 15), (16, 3), (31, 15)])
    i.R(5, 15, 27, 29)
    i.R(5, 15, 27, 16, M)
    i.R(13, 20, 18, 29, C).R(7, 19, 10, 22, C).R(21, 19, 24, 22, C)
    return i.R(15, 0, 16, 4)


def granary(i):
    i.R(12, 10, 26, 29)
    i.E(19, 10, 7, 6)
    i.R(12, 15, 26, 16, M).R(12, 22, 26, 23, M)
    i.R(17, 24, 20, 29, C)
    i.E(6, 25, 5, 5).P([(4, 20), (8, 20), (9, 17), (3, 17)])
    return i.R(4, 19, 8, 20, M)


def tower(i):
    i.tower(10, 21, 3, 29)
    i.R(14, 22, 17, 29, C).R(15, 11, 16, 15, C)
    return i.R(7, 29, 24, 30)


def spire(i):
    i.P([(16, 0), (22, 10), (10, 10)])
    i.R(12, 10, 20, 29)
    i.R(9, 16, 23, 17).R(9, 28, 23, 30)
    i.P([(9, 17), (12, 21), (12, 17)], M).P([(23, 17), (20, 21), (20, 17)], M)
    return i.R(15, 12, 16, 14, C).R(15, 21, 16, 25, C)


def castle(i):
    i.tower(2, 9, 5, 29).tower(22, 29, 5, 29)
    i.R(9, 15, 22, 29)
    for x in (10, 14, 18):
        i.R(x, 12, x + 2, 14)
    i.E(16, 23, 4, t=C).R(12, 23, 20, 29, C)
    return i.R(5, 12, 6, 16, C).R(25, 12, 26, 16, C)


def wall(i):
    i.R(1, 12, 30, 28)
    for x in range(1, 30, 6):
        i.R(x, 8, x + 3, 11)
    for y in (16, 21, 26):
        i.L([(1, y), (30, y)], 1, C)
    for x in (6, 16, 26):
        i.L([(x, 12), (x, 16)], 1, C).L([(x, 21), (x, 26)], 1, C)
    for x in (11, 21):
        i.L([(x, 16), (x, 21)], 1, C)
    return i.R(1, 29, 30, 30, M)


def fortress(i):
    i.tower(12, 19, 1, 29).tower(2, 8, 10, 29).tower(23, 29, 10, 29)
    i.R(8, 18, 23, 29)
    i.E(16, 24, 3, t=C).R(13, 24, 19, 29, C)
    return i.R(15, 8, 16, 12, C)


def keep(i):
    i.R(8, 11, 23, 29)
    i.tower(4, 9, 7, 29).tower(22, 27, 7, 29)
    i.R(15, 2, 15, 11).P([(16, 2), (23, 4), (16, 7)], M)
    i.E(16, 24, 3, t=C).R(13, 24, 19, 29, C)
    return i.R(11, 15, 12, 18, C).R(19, 15, 20, 18, C)


def temple(i):
    i.P([(16, 2), (30, 10), (2, 10)])
    i.R(3, 26, 28, 29)
    for x in (5, 11, 17, 23):
        i.R(x, 12, x + 3, 25, M)
    return i.R(4, 10, 27, 11)


def chapel(i):
    i.R(4, 17, 21, 29)
    i.P([(2, 17), (12, 8), (22, 17)])
    i.R(21, 9, 27, 29).P([(20, 9), (24, 1), (28, 9)])
    i.E(12, 20, 2, t=C).R(11, 24, 14, 29, C)
    return i.R(23, 12, 25, 15, C)


def cathedral(i):
    for x in (3, 21):
        i.R(x, 10, x + 7, 29).P([(x - 1, 10), (x + 3, 0), (x + 4, 0), (x + 8, 10)])
        i.R(x + 3, 13, x + 4, 17, C)
    i.R(10, 15, 21, 29).P([(10, 15), (15, 8), (16, 8), (21, 15)])
    i.E(15, 18, 3, t=C).E(15, 18, 1, t=M)
    return i.R(14, 24, 17, 29, C)


def pagoda(i):
    for w, y in ((13, 21), (10, 13), (7, 5)):
        i.P([(16 - w - 2, y + 4), (16 - w, y + 2), (16 - w + 2, y), (16 + w - 2, y), (16 + w, y + 2), (16 + w + 2, y + 4)])
        i.R(16 - w + 3, y + 5, 16 + w - 3, y + 7, M)
    i.R(4, 29, 28, 30)
    return i.R(15, 0, 16, 5).R(14, 26, 17, 28, C)


def ziggurat(i):
    for k in range(4):
        i.R(2 + 4 * k, 24 - 6 * k, 29 - 4 * k, 29 - 6 * k)
        i.R(2 + 4 * k, 24 - 6 * k, 29 - 4 * k, 24 - 6 * k, M)
    return i.R(14, 12, 17, 29, M).R(15, 7, 16, 10, C)


def pyramid(i):
    i.P([(16, 2), (31, 29), (1, 29)])
    i.P([(16, 2), (31, 29), (16, 29)], M)
    for y in (11, 17, 23):
        i.L([(16 - (y - 2) // 2, y), (16, y)], 1, C)
    return i.P([(13, 29), (16, 23), (19, 29)], C)


def totem(i):
    i.R(12, 5, 19, 30)
    i.P([(12, 8), (2, 3), (4, 12), (12, 14)]).P([(19, 8), (29, 3), (27, 12), (19, 14)])
    i.P([(12, 5), (16, 1), (19, 5)])
    i.R(13, 8, 14, 9, C).R(17, 8, 18, 9, C).P([(15, 10), (16, 14), (17, 10)], M)
    i.R(12, 17, 19, 18, M)
    return i.R(13, 21, 14, 22, C).R(17, 21, 18, 22, C).R(13, 25, 18, 26, C)


def tent(i):
    i.P([(16, 4), (29, 29), (3, 29)])
    i.L([(16, 5), (12, 0)], 1).L([(16, 5), (20, 0)], 1)
    i.P([(16, 15), (21, 29), (11, 29)], C)
    return i.L([(10, 15), (22, 15)], 1, M).L([(8, 21), (12, 21)], 2, M).L([(20, 21), (24, 21)], 2, M)


def burrow(i):
    i.E(16, 23, 13, 12)
    i.R(0, 29, 31, 31, C)
    for x, y, d in ((6, 13, -3), (12, 9, -1), (20, 9, 1), (26, 13, 3)):
        i.P([(x - 2, y + 3), (x + d, y - 8), (x + 2, y + 3)])
    i.E(16, 26, 4, 5, t=C)
    return i.R(2, 28, 29, 29).L([(6, 19), (26, 19)], 1, M)


def lighthouse(i):
    i.P([(12, 11), (19, 11), (22, 28), (9, 28)])
    i.R(10, 17, 21, 19, M)
    i.R(10, 6, 21, 10).P([(11, 6), (15, 1), (16, 1), (20, 6)])
    i.R(13, 7, 18, 9, C)
    i.P([(22, 8), (31, 4), (31, 12)], M).P([(9, 8), (0, 4), (0, 12)], M)
    return i.R(5, 28, 26, 30).R(14, 23, 17, 28, C)


def windmill(i):
    i.P([(12, 14), (20, 14), (23, 30), (9, 30)])
    for x, y in ((3, 1), (29, 1), (3, 25), (29, 25)):
        i.L([(16, 13), (x, y)], 3, M)
    i.E(16, 13, 3)
    return i.R(14, 24, 17, 30, C)


def watermill(i):
    i.R(15, 12, 30, 28).P([(13, 12), (22, 4), (31, 12)])
    i.R(21, 17, 24, 21, C)
    i.E(10, 20, 10, t=C)
    i.ring(10, 20, 9, 2)
    for a in range(0, 180, 45):
        dx, dy = 9 * math.cos(math.radians(a)), 9 * math.sin(math.radians(a))
        i.L([(10 - dx, 20 - dy), (10 + dx, 20 + dy)], 1, M)
    i.E(10, 20, 2)
    return i.L([(0, 30), (5, 29), (10, 30), (15, 29), (20, 30), (25, 29), (31, 30)], 1, M)


def anvil(i):
    return TI._anvil(i, 13)


def smithy(i):
    TI._anvil(i, 14)
    return i.R(13, 2, 23, 7).R(17, 7, 18, 12, M)


def furnace(i):
    i.R(4, 13, 27, 29)
    i.R(19, 3, 25, 13).R(18, 3, 26, 4)
    i.E(13, 24, 6, t=C).R(7, 24, 19, 29, C)
    i.flame(13, 29, 9)
    i.E(13, 2, 2, t=M).E(8, 5, 2, t=M)
    return i.R(4, 13, 27, 14, M)


def arena(i):
    i.E(16, 17, 15, 10)
    i.E(16, 14, 11, 5, t=C)
    i.E(16, 14, 8, 3, t=M)
    for x in (5, 10, 15, 20, 25):
        i.R(x, 21 if x in (5, 25) else 22, x + 1, 24 if x in (5, 25) else 25, C)
    return i


def swords(i):
    return TI.ICONS["Steel Forged Swords"](i)


def pit(i):
    i.ring(16, 16, 14, 2, t=M)
    i.L([(8, 6), (24, 24)], 3).L([(24, 6), (8, 24)], 3)
    return i.L([(19, 24), (25, 18)], 2).L([(13, 24), (7, 18)], 2)


def dock(i):
    i.R(1, 13, 24, 15)
    for x in (3, 11, 19):
        i.R(x, 15, x + 2, 26)
    i.R(20, 6, 22, 13).R(19, 5, 23, 6)
    i.P([(24, 20), (31, 20), (29, 24), (26, 24)]).R(27, 14, 27, 20).P([(28, 14), (31, 19), (28, 19)], M)
    return i.L([(0, 28), (5, 27), (10, 28), (15, 27), (20, 28), (25, 27), (31, 28)], 2, M)


def shipyard(i):
    i.P([(2, 12), (30, 12), (25, 23), (7, 23)])
    for x in (9, 14, 19, 24):
        i.L([(x, 14), (x, 21)], 1, C)
    i.R(15, 2, 16, 12).L([(16, 3), (23, 11)], 1, M)
    i.L([(7, 23), (4, 29)], 2, M).L([(25, 23), (28, 29)], 2, M).L([(16, 23), (16, 29)], 2, M)
    return i.R(1, 29, 30, 30)


def stall(i):
    i.P([(3, 6), (29, 6), (31, 14), (1, 14)])
    for x in (7, 15, 23):
        i.P([(x, 6), (x + 3, 6), (x + 3, 14), (x - 1, 14)], M)
    i.R(3, 14, 4, 29).R(28, 14, 29, 29)
    i.R(3, 22, 29, 25)
    return i.E(10, 19, 3).E(17, 20, 2, t=M).E(23, 19, 3)


def coins(i):
    return TI._coins(i)


def vault(i):
    i.E(16, 16, 14)
    i.E(16, 16, 11, t=M)
    i.E(16, 16, 8)
    for a in range(0, 180, 45):
        dx, dy = 6 * math.cos(math.radians(a)), 6 * math.sin(math.radians(a))
        i.L([(16 - dx, 16 - dy), (16 + dx, 16 + dy)], 1, C)
    i.E(16, 16, 2, t=C)
    return i.R(0, 9, 3, 13).R(0, 19, 3, 23)


def chest(i):
    i.d.pieslice([3, 4, 28, 26], 180, 360, fill=B)
    i.R(3, 15, 28, 28)
    i.R(3, 15, 28, 16, C)
    i.R(8, 7, 10, 28, M).R(21, 7, 23, 28, M)
    return i.R(14, 14, 17, 19).R(15, 16, 16, 17, C)


def observatory(i):
    i.d.pieslice([4, 8, 27, 32], 180, 360, fill=B)
    i.R(4, 20, 27, 29)
    i.P([(14, 9), (18, 9), (20, 20), (15, 20)], C)
    i.L([(17, 15), (27, 4)], 3, M)
    i.R(4, 20, 27, 21, M)
    return i.star(6, 5, 4)


def cauldron(i):
    i.E(16, 20, 12, 9)
    i.R(3, 12, 28, 15)
    i.R(7, 27, 9, 31).R(22, 27, 24, 31)
    i.E(10, 7, 2, t=M).E(17, 4, 3, t=M).E(23, 8, 2, t=M)
    return i.d.arc([8, 14, 24, 26], 20, 160, fill=M, width=1) or i


def well(i, top="moon"):
    i.P([(2, 19), (29, 19), (25, 29), (6, 29)])
    i.E(15, 19, 13, 3, t=M)
    i.E(15, 19, 10, 2, t=C)
    if top == "moon":
        i.E(15, 8, 7).E(19, 6, 6, t=C)
    elif top == "sun":
        _sunburst(i, 15, 8, 4, 8)
    else:
        i.star(15, 8, 8)
    return i


def _sunburst(i, cx, cy, r, R):
    for k in range(8):
        a = k * math.pi / 4
        i.P([(cx + R * math.cos(a), cy + R * math.sin(a)), (cx + r * math.cos(a - 0.35), cy + r * math.sin(a - 0.35)), (cx + r * math.cos(a + 0.35), cy + r * math.sin(a + 0.35))])
    return i.E(cx, cy, r)


def sun(i):
    return _sunburst(i, 16, 16, 8, 15).E(16, 16, 5, t=M)


def moon(i):
    i.E(14, 16, 13)
    i.E(20, 13, 11, t=C)
    return i.star(23, 12, 5, M)


def tree(i):
    i.R(14, 16, 18, 28)
    i.P([(14, 26), (8, 31), (24, 31), (18, 26)])
    i.L([(15, 20), (9, 15)], 2).L([(17, 20), (23, 15)], 2)
    i.E(16, 8, 9, 8).E(7, 13, 7, 6).E(25, 13, 7, 6)
    return i.E(12, 7, 2, t=M).E(22, 12, 2, t=M).E(7, 13, 1, t=M)


def horseshoe(i):
    i.E(16, 14, 13, 13)
    i.R(3, 14, 29, 28)
    i.E(16, 14, 7, 7, t=C).R(9, 14, 23, 31, C)
    i.R(0, 29, 31, 31, C)
    for x, y in ((6, 12), (26, 12), (5, 20), (27, 20), (10, 5), (22, 5)):
        i.R(x - 1, y, x, y + 1, C)
    return i


def aqueduct(i):
    i.R(0, 8, 31, 30)
    for cx in (6, 16, 26):
        i.E(cx, 19, 3, 5, t=C).R(cx - 3, 19, cx + 3, 30, C)
    i.R(0, 8, 31, 9, M)
    return i.L([(0, 5), (5, 4), (10, 5), (15, 4), (20, 5), (25, 4), (31, 5)], 2, M)


def wave(i):
    for k, y in enumerate((8, 16, 24)):
        i.L([(1, y + 2), (6, y - 2), (11, y + 2), (16, y - 2), (21, y + 2), (26, y - 2), (31, y + 2)], 3, B if k != 1 else M)
    return i


def gear(i):
    return i.gear(16, 16, 10)


def gears(i):
    return TI.ICONS["Gnomish Gearworks"](i)


def airship(i):
    i.E(15, 10, 14, 8)
    i.R(1, 9, 29, 10, M)
    i.P([(27, 5), (31, 2), (31, 18), (27, 15)], M)
    i.L([(8, 17), (10, 22)], 1).L([(22, 17), (20, 22)], 1)
    i.P([(7, 22), (23, 22), (20, 28), (10, 28)])
    return i.R(12, 24, 13, 25, C).R(17, 24, 18, 25, C)


def crown(i):
    i.P([(2, 25), (2, 8), (9, 16), (16, 4), (23, 16), (30, 8), (30, 25)])
    i.R(2, 25, 30, 29, M)
    i.E(2, 7, 2).E(16, 3, 2).E(30, 7, 2)
    return i.E(16, 20, 2, t=C).E(8, 21, 1, t=C).E(24, 21, 1, t=C)


def throne(i):
    i.P([(9, 7), (12, 3), (16, 0), (20, 3), (23, 7), (23, 20), (9, 20)])
    i.R(12, 8, 20, 17, C)
    i.R(14, 10, 18, 15, M)
    i.R(4, 14, 8, 24).R(24, 14, 28, 24)
    i.R(4, 20, 28, 24)
    return i.R(4, 24, 8, 31).R(24, 24, 28, 31)


def banner(i):
    TI._banner(i, 16)
    return i.star(16, 14, 5, C).R(15, 24, 16, 31, M)


def shield(i):
    i.P([(3, 3), (29, 3), (29, 15), (16, 30), (3, 15)])
    i.P([(16, 3), (29, 3), (29, 15), (16, 30)], M)
    return i.P([(16, 8), (22, 14), (16, 22), (10, 14)], C)


def armory(i):
    i.L([(3, 2), (29, 28)], 2, M).L([(29, 2), (3, 28)], 2, M)
    i.P([(7, 6), (25, 6), (25, 16), (16, 27), (7, 16)])
    return i.R(15, 6, 16, 26, C).P([(16, 6), (25, 6), (25, 16), (17, 26)], M)


def helm(i):
    i.E(16, 13, 11, 11)
    i.R(5, 13, 27, 26)
    i.R(8, 14, 24, 16, C).R(15, 16, 16, 26, C)
    return i.P([(14, 2), (18, 2), (22, 0), (18, 6), (14, 6)], M)


def skull(i):
    i.E(16, 12, 11, 11)
    i.R(10, 18, 22, 27)
    i.E(11, 13, 3, t=C).E(21, 13, 3, t=C)
    i.P([(16, 16), (18, 20), (14, 20)], C)
    for x in (13, 16, 19):
        i.L([(x, 23), (x, 27)], 1, C)
    return i


def tomb(i):
    i.P([(2, 12), (16, 3), (30, 12)])
    i.R(5, 12, 26, 29)
    i.R(5, 12, 7, 29, M).R(24, 12, 26, 29, M)
    i.E(15, 22, 4, t=C).R(11, 22, 19, 29, C)
    return i.R(2, 29, 29, 30)


def coffin(i):
    i.P([(11, 1), (21, 1), (26, 10), (21, 30), (11, 30), (6, 10)])
    i.P([(13, 4), (19, 4), (22, 10), (19, 27), (13, 27), (10, 10)], M)
    return i.E(16, 12, 3)


def mask(i):
    i.P([(1, 8), (10, 6), (16, 9), (22, 6), (31, 8), (29, 19), (21, 22), (16, 17), (11, 22), (3, 19)])
    i.E(9, 13, 4, 3, t=C).E(23, 13, 4, 3, t=C)
    return i.P([(14, 22), (18, 22), (16, 31)], M)


def tiki(i):
    i.P([(8, 2), (24, 2), (27, 10), (23, 29), (9, 29), (5, 10)])
    i.P([(8, 9), (14, 11), (9, 13)], C).P([(24, 9), (18, 11), (23, 13)], C)
    i.R(11, 20, 21, 22, C)
    i.P([(11, 22), (12, 17), (14, 22)]).P([(21, 22), (20, 17), (18, 22)])
    i.P([(15, 12), (17, 12), (18, 18), (14, 18)], M)
    return i.P([(8, 2), (10, -1), (13, 2)]).P([(14, 2), (16, -2), (18, 2)]).P([(19, 2), (22, -1), (24, 2)])


def hourglass(i):
    i.R(5, 1, 26, 4).R(5, 27, 26, 30)
    i.P([(7, 5), (24, 5), (16, 16)])
    i.P([(16, 15), (24, 26), (7, 26)], M)
    i.P([(11, 26), (16, 20), (20, 26)])
    return i.R(15, 14, 16, 19, M)


def ringtemple(i):
    i.P([(16, 0), (19, 5), (13, 5)])
    i.R(9, 5, 22, 7)
    for x in (10, 14, 18):
        i.R(x, 8, x + 2, 12, M)
    i.R(6, 13, 25, 15)
    for x in (7, 12, 17, 22):
        i.R(x, 16, x + 2, 22, M)
    i.R(2, 23, 29, 25)
    for x in (3, 8, 13, 18, 23, 27):
        i.R(x, 26, x + 1, 29, M)
    return i.R(0, 30, 31, 31)


def gate(i):
    i.R(2, 6, 9, 30).R(22, 6, 29, 30)
    i.R(1, 2, 30, 7)
    i.R(10, 8, 21, 30, M)
    i.L([(15, 8), (15, 30)], 2, C)
    return i.E(15, 17, 4).E(15, 17, 1, t=C)


def bars(i):
    i.R(3, 3, 28, 6).R(3, 26, 28, 29)
    for x in (5, 10, 15, 20, 25):
        i.R(x, 6, x + 1, 26)
    return i.R(3, 15, 28, 16, M)


def mountain(i):
    i.P([(0, 30), (10, 9), (15, 17), (21, 3), (31, 30)])
    i.P([(21, 3), (31, 30), (20, 30), (23, 18)], M)
    i.P([(21, 3), (24, 10), (21, 9), (19, 11), (18, 9)], C)
    return i.E(13, 27, 3, 4, t=C).R(10, 27, 16, 30, C)


def serpent(i):
    i.L([(22, 5), (10, 6), (7, 11), (11, 15), (22, 16), (25, 21), (21, 26), (8, 27)], 4)
    i.P([(20, 2), (30, 3), (31, 7), (22, 9)])
    i.E(26, 5, 1, t=C)
    i.P([(8, 25), (2, 23), (8, 29)])
    return i.L([(31, 6), (31, 10)], 1, M)


def brewery(i):
    i.keg(11, 17, 9, 11)
    i.R(21, 15, 28, 28)
    i.E(24, 14, 4, 2, t=M)
    i.d.arc([26, 17, 32, 26], 270, 90, fill=B, width=2)
    return i.R(23, 19, 24, 25, C)


def pig(i):
    i.E(14, 17, 12, 8)
    i.E(25, 15, 5)
    i.R(28, 14, 31, 18, M)
    i.P([(22, 11), (23, 6), (26, 10)])
    i.R(6, 23, 8, 29).R(11, 24, 13, 29).R(18, 24, 20, 29).R(22, 23, 24, 29)
    i.E(25, 13, 1, t=C)
    return i.L([(2, 15), (0, 12), (2, 10)], 1)


def saw(i):
    for k in range(12):
        a = k * math.pi / 6
        i.P([(16 + 14 * math.cos(a + 0.3), 14 + 14 * math.sin(a + 0.3)), (16 + 9 * math.cos(a - 0.3), 14 + 9 * math.sin(a - 0.3)), (16 + 9 * math.cos(a + 0.4), 14 + 9 * math.sin(a + 0.4))])
    i.E(16, 14, 10)
    i.E(16, 14, 6, t=M)
    i.E(16, 14, 2, t=C)
    i.R(0, 22, 31, 31, C)
    return i.R(1, 23, 30, 29).E(30, 26, 2, 3, t=M).L([(4, 26), (24, 26)], 1, C)


def cup(i):
    i.P([(8, 2), (24, 2), (22, 13), (16, 18), (10, 13)])
    i.d.arc([2, 3, 12, 13], 90, 270, fill=B, width=2)
    i.d.arc([20, 3, 30, 13], 270, 90, fill=B, width=2)
    i.R(15, 18, 16, 24).R(9, 24, 22, 28)
    return i.R(11, 4, 12, 10, M).R(9, 28, 22, 29, M)


def frame(i):
    i.R(2, 4, 29, 28)
    i.R(5, 7, 26, 25, C)
    i.P([(5, 25), (12, 14), (17, 21), (21, 16), (26, 25)], M)
    return i.E(21, 11, 2)


def heart(i):
    i.E(10, 11, 7).E(22, 11, 7)
    i.P([(3, 13), (29, 13), (16, 29)])
    return i.E(8, 9, 2, t=M)


def planet(i):
    i.E(16, 16, 9)
    i.d.arc([0, 9, 31, 23], 0, 360, fill=M, width=2)
    i.d.pieslice([7, 7, 25, 25], 180, 360, fill=B)
    return i.star(27, 4, 3).star(4, 27, 2, M)


def blocks(i):
    i.R(9, 4, 22, 12)
    i.R(1, 14, 14, 22).R(17, 14, 30, 22)
    i.R(1, 24, 9, 30).R(11, 24, 20, 30).R(22, 24, 30, 30)
    return i.R(9, 4, 22, 5, M).R(1, 14, 14, 15, M).R(17, 14, 30, 15, M)


def target(i):
    i.ring(14, 17, 13, 3)
    i.ring(14, 17, 7, 2, t=M)
    i.E(14, 17, 2)
    i.L([(15, 16), (28, 3)], 2)
    return i.P([(24, 1), (31, 0), (30, 7)])


def campfire(i):
    i.flame(16, 23, 20)
    i.L([(4, 24), (27, 30)], 3, M).L([(28, 24), (5, 30)], 3, M)
    return i


def brazier(i):
    return TI.ICONS["Priesthood"](i)


def altar(i):
    i.R(2, 12, 29, 16)
    i.R(5, 16, 9, 28).R(22, 16, 26, 28)
    i.R(1, 28, 30, 30)
    i.R(11, 18, 20, 28, M)
    return i.flame(16, 12, 11)


def stones(i):
    for x, h in ((3, 12), (11, 18), (19, 16), (26, 11)):
        i.P([(x, 28), (x + 1, 28 - h), (x + 4, 28 - h - 1), (x + 5, 28)])
        i.R(x + 3, 28 - h + 2, x + 4, 27, M)
    i.R(9, 8, 25, 10)
    return i.R(0, 28, 31, 30)


def sevenstars(i):
    for x, y, r in ((16, 6, 5), (6, 12, 3), (26, 12, 3), (9, 22, 3), (23, 22, 3), (16, 16, 3), (16, 27, 3)):
        i.star(x, y, r, B if r == 5 else M)
    return i


def naaru(i):
    i.star(16, 16, 15)
    i.P([(16, 6), (26, 16), (16, 26), (6, 16)], M)
    i.star(16, 16, 6)
    return i.E(16, 16, 1, t=C)


def anchor(i):
    return TI.ICONS["Seafaring"](i)


def trident(i):
    i.R(15, 6, 16, 31, M)
    i.P([(16, 0), (18, 6), (17, 14), (14, 14), (13, 6)])
    i.L([(5, 3), (6, 13), (15, 16)], 3).L([(26, 3), (25, 13), (16, 16)], 3)
    i.P([(5, 0), (8, 5), (3, 5)]).P([(26, 0), (29, 5), (24, 5)])
    return i.R(12, 17, 19, 18)


def coral(i):
    i.L([(16, 30), (16, 12)], 3)
    i.L([(16, 22), (8, 16), (7, 7)], 3).L([(16, 18), (24, 13), (25, 4)], 3)
    i.L([(8, 14), (3, 11)], 2, M).L([(24, 12), (29, 9)], 2, M).L([(16, 12), (13, 4)], 2).L([(16, 13), (19, 6)], 2, M)
    for x, y in ((7, 6), (25, 3), (13, 3), (19, 5), (2, 10), (30, 8)):
        i.E(x, y, 1)
    return i.R(8, 30, 24, 31, M)


def cleaver(i):
    i.P([(3, 4), (22, 4), (25, 8), (25, 18), (3, 18)])
    i.R(3, 15, 25, 18, M)
    i.E(7, 8, 1, t=C)
    return i.P([(20, 18), (25, 18), (29, 30), (25, 31)])


def hammer_gear(i):
    i.gear(20, 20, 8)
    i.L([(4, 26), (15, 12)], 3, M)
    return i.P([(9, 6), (17, 2), (22, 10), (14, 14)])


def wrench(i):
    i.gear(21, 21, 7)
    i.L([(6, 6), (20, 20)], 4)
    i.E(6, 6, 5).P([(1, 1), (7, 3), (3, 7)], C)
    return i


def reactor(i):
    i.R(8, 2, 23, 5).R(8, 27, 23, 30)
    i.R(10, 6, 21, 26, M)
    i.bolt(15, 7, 25)
    return i.R(4, 12, 7, 20).R(24, 12, 27, 20)


def beacon(i):
    i.P([(11, 14), (20, 14), (23, 30), (8, 30)])
    i.R(9, 12, 22, 14)
    i.star(15, 6, 6)
    for a, b in (((5, 3), (1, 0)), ((26, 3), (30, 0)), ((4, 8), (0, 9)), ((27, 8), (31, 9))):
        i.L([a, b], 1, M)
    return i.R(14, 24, 17, 30, C)


def crystal(i):
    return i.crystal(16, 1, 30, 8)


def from_tech(name):
    return lambda i: TI.ICONS[name](i)


# ---------------------------------------------------------------- corner marks
def _halo(i, x, y, r=7):
    i.E(x, y, r, t=C)


def b_star(i, x, y): i.star(x, y, 5)
def b_flame(i, x, y): i.P([(x, y - 6), (x + 4, y), (x + 3, y + 4), (x - 3, y + 4), (x - 4, y), (x - 1, y - 1)]).P([(x, y), (x + 1, y + 4), (x - 1, y + 4)], C)
def b_skull(i, x, y): i.E(x, y - 1, 4, 4).R(x - 2, y + 2, x + 2, y + 5).R(x - 3, y - 2, x - 2, y - 1, C).R(x + 2, y - 2, x + 3, y - 1, C).R(x, y + 3, x, y + 5, C)
def b_moon(i, x, y): i.E(x - 1, y, 5).E(x + 2, y - 2, 4, t=C)
def b_sun(i, x, y): _sunburst(i, x, y, 3, 6)
def b_leaf(i, x, y): i.P([(x - 5, y + 5), (x - 4, y - 2), (x + 2, y - 5), (x + 5, y - 5), (x + 5, y - 2), (x + 2, y + 4)]).L([(x - 5, y + 5), (x + 3, y - 3)], 1, C)
def b_coin(i, x, y): i.E(x, y, 5).E(x, y, 3, t=M).R(x, y - 2, x, y + 2, C)
def b_gear(i, x, y): i.gear(x, y, 4, 6)
def b_bolt(i, x, y): i.bolt(x, y - 6, y + 6)
def b_crown(i, x, y): i.P([(x - 5, y + 4), (x - 5, y - 4), (x - 2, y), (x, y - 5), (x + 2, y), (x + 5, y - 4), (x + 5, y + 4)])
def b_paw(i, x, y): i.E(x, y + 2, 3, 3).E(x - 4, y - 2, 1).E(x - 1, y - 4, 1).E(x + 2, y - 4, 1).E(x + 5, y - 2, 1)
def b_anchor(i, x, y): i.R(x, y - 5, x, y + 4).R(x - 2, y - 3, x + 2, y - 3).E(x, y - 5, 1); i.d.arc([x - 5, y - 3, x + 5, y + 5], 10, 170, fill=B, width=2)
def b_sword(i, x, y): i.P([(x, y - 6), (x + 1, y - 4), (x + 1, y + 2), (x - 1, y + 2), (x - 1, y - 4)]).R(x - 3, y + 2, x + 3, y + 3).R(x, y + 4, x, y + 6)
def b_eye(i, x, y): i.P([(x - 6, y), (x - 2, y - 4), (x + 2, y - 4), (x + 6, y), (x + 2, y + 4), (x - 2, y + 4)]).R(x - 1, y - 1, x + 1, y + 1, C)
def b_key(i, x, y): i.ring(x - 2, y - 3, 3, 1).L([(x, y - 1), (x + 4, y + 5)], 2).L([(x + 2, y + 3), (x + 4, y + 1)], 1)
def b_drop(i, x, y): i.E(x, y + 2, 4).P([(x, y - 6), (x + 4, y + 1), (x - 4, y + 1)])
def b_gem(i, x, y): i.P([(x, y - 6), (x + 4, y - 1), (x + 2, y + 5), (x - 2, y + 5), (x - 4, y - 1)]).P([(x, y - 6), (x + 4, y - 1), (x + 2, y + 5), (x, y + 5)], M)
def b_book(i, x, y): i.P([(x - 6, y - 3), (x - 1, y - 2), (x - 1, y + 4), (x - 6, y + 3)]).P([(x + 6, y - 3), (x + 1, y - 2), (x + 1, y + 4), (x + 6, y + 3)], M)
def b_hammer(i, x, y): i.R(x - 4, y - 5, x + 4, y - 1).R(x, y, x, y + 6)
def b_heart(i, x, y): i.E(x - 2, y - 2, 3).E(x + 2, y - 2, 3).P([(x - 5, y - 1), (x + 5, y - 1), (x, y + 5)])


MARKS = {k[2:]: v for k, v in list(globals().items()) if k.startswith("b_")}

T = from_tech
ICONS = {
    # everyday buildings
    "Town Hall": hall, "Granary": granary, "Shrine": brazier, "Stone Works": blocks, "Library": lambda i: i.book(),
    "Fighting Pit": pit, "Water Mill": watermill, "Walls": wall, "Barracks": helm, "Lighthouse": lighthouse,
    "Stable": horseshoe, "Magistrate's Hall": T("Arathi Law"), "Arena": arena, "Temple": temple,
    "Storyteller's Circle": campfire, "Market": stall, "Coin Forge": (coins, "hammer"), "Waterworks": aqueduct,
    "Herb Garden": T("Nature's Blessing"), "Workshop": hammer_gear, "Blacksmith": smithy, "Shipyard": shipyard,
    "Arcane Sanctum": T("Scrying"), "Keep": keep, "Armory": armory, "Observatory": observatory, "Bardic Hall": T("Bardic Lore"),
    "Bank": vault, "City Watch": (shield, "eye"), "Beastiary": T("Beast Taming"), "Docks": dock, "Windmill": windmill,
    "Siege Workshop": T("Siege Engineering"), "Hall of Relics": (chest, "star"), "Mage Tower": (spire, "star"),
    "Foundry": furnace, "Training Grounds": target, "House of Healing": (heart, "leaf"), "Auction House": T("Auctioneering"),
    "Tidal Works": (wave, "gear"), "Guard Tower": tower, "Grand Arena": (arena, "crown"), "Arcane Beacon": beacon,
    "Fortress": fortress, "Arcane Laboratory": (T("Alchemy"), "star"), "Alchemy Lab": T("Elixir Mastery"),
    "Sun Crystal Array": (crystal, "sun"), "Salvage Yard": wrench, "Mana Reactor": reactor, "Burrow": burrow,
    "Skyship Foundry": airship, "Cathedral": cathedral, "Monastery": (chapel, "book"), "Sanctuary": (temple, "heart"),
    "Pagoda": pagoda,
    # faction buildings
    "Chapel of the Light": (chapel, "sun"), "Royal Barracks": (helm, "crown"), "Lumber Mill": saw, "Castle": castle,
    "Cathedral of Light": (cathedral, "sun"), "Altar of Kings": (altar, "crown"), "Necropolis": (tomb, "skull"),
    "Crypt": coffin, "Ziggurat": (ziggurat, "skull"), "Altar of Storms": (altar, "bolt"), "Pig Farm": pig,
    "Voodoo Lounge": tiki, "Great Totem": totem, "Apothecarium": (T("Alchemy"), "skull"), "Magisters' Sanctum": (T("Scrying"), "sun"),
    "Goblin Bazaar": (stall, "coin"), "Dwarven Forge": (smithy, "flame"), "Tinker's Workshop": (gears, "bolt"),
    "Moonwell": well, "Crystal Sanctum": (T("Azerite Refinement"), "star"), "Gilnean Bulwark": (wall, "paw"),
    "Runestone": T("Runic Script"), "Brewery": brewery, "War Mill": (saw, "sword"), "Great Forge": (furnace, "hammer"),
    "Gnomeregan Laboratory": (T("Alchemy"), "gear"), "Tree of Life": tree, "Crystal Hall": (lambda i: i.book(), "gem"),
    "Greymane Watchtower": (tower, "paw"), "Elven Spire": (spire, "sun"), "Loa Shrine": (tiki, "flame"),
    "Spirit Lodge": (tent, "leaf"), "Plague Cauldron": (cauldron, "skull"), "Mana Forge": (furnace, "star"),
    "Trade Prince's Bank": (vault, "crown"), "Jade Pagoda": (pagoda, "leaf"), "Slaughterhouse": (cleaver, "skull"),
    "Shadowforge Furnace": (furnace, "skull"), "Admiralty Drydock": (shipyard, "anchor"), "Golden Pyramid": (pyramid, "coin"),
    "Coral Spawning Pool": coral, "Arcway": (T("Architecture"), "star"), "Ironhorn Lodge": (hammer_gear, "paw"),
    "Tushui Monastery": (pagoda, "moon"), "Huojin Training Hall": (pagoda, "flame"),
    # capitals
    "Stormwind Throne Room": (throne, "crown"), "Ring of Valor": (arena, "flame"), "Temple of the Moon": (temple, "moon"),
    "High Seat of Ironforge": (throne, "hammer"), "Tinkertown Workshops": (gears, "crown"), "Spirit Rise": (tent, "star"),
    "Darkspear Voodoo Hall": (tiki, "skull"), "Court of the Sun": (sun, "crown"), "Sunstrider Spire": (spire, "crown"),
    "Temple of the Jade Serpent": serpent, "Royal Apothecary Society": (cauldron, "crown"), "Vault of Lights": (T("Azerite Refinement"), "sun"),
    "Steamwheedle Exchange": (T("Arathi Law"), "coin"), "Greymane Court": (castle, "paw"), "Throne of the Damned": (throne, "skull"),
    "Black Anvil": (anvil, "flame"), "Proudmoore Admiralty": (anchor, "crown"), "Great Seal of Dazar'alor": (pyramid, "crown"),
    "Palace of Nazjatar": trident, "Shal'Aran Sanctum": (tree, "star"), "Huln's Totem": (totem, "paw"),
    # national wonders
    "Palace": crown, "Grand Coliseum": (arena, "star"), "Grand Library": (lambda i: i.book(), "crown"),
    "Hall of Legends": banner, "Hall of Champions": (cup, "sword"), "High Temple": (temple, "sun"), "Royal Vault": (chest, "crown"),
    "College of Magi": (lambda i: i.book(), "star"), "Great Foundry": (furnace, "gear"), "Royal Gallery": frame,
    "Spymaster's Guild": (mask, "eye"), "The Violet Hold": bars, "Titan Ascension Project": T("Titan Logic"),
    "Well of Eternity": lambda i: well(i, "star"), "Trophy Hall": cup,
    # wonders
    "Temple of Elune": moon, "Circle of Binding": stones, "The Violet Citadel": (spire, "eye"), "Halls of Origination": (pyramid, "sun"),
    "Uther's Tomb": (tomb, "sun"), "Valley of Heroes": T("Mithril Forged Swords"), "Westfall Lighthouse": (lighthouse, "star"),
    "Vale of Eternal Blossoms": (T("Nature's Blessing"), "sun"), "Mogu'shan Vaults": (vault, "bolt"), "Sanctum of the Oracles": (T("Scrying"), "eye"),
    "Caverns of Time": hourglass, "The Greymane Wall": (gate, "paw"), "Admiralty of Boralus": (anchor, "star"),
    "Shrine of Seven Stars": sevenstars, "Zul'Gurub": (ziggurat, "leaf"), "Thunder Totem": (totem, "bolt"),
    "Temple of the White Tiger": (pagoda, "paw"), "Sunfury Spire": (spire, "flame"), "Northshire Abbey": (chapel, "leaf"),
    "Karazhan": (spire, "moon"), "Mogu'shan Palace": (pagoda, "crown"), "Tower of Azora": (tower, "eye"), "Grim Batol": (mountain, "flame"),
    "Sunwell Plateau": lambda i: well(i, "sun"), "Ulduar": (gate, "star"), "Icecrown Citadel": (fortress, "skull"),
    "Hall of Explorers": T("Navigation"), "Undermine Exchange": (coins, "gear"), "Gates of Ahn'Qiraj": (gate, "sun"),
    "Wyrmrest Temple": ringtemple, "Lion's Rest": (tomb, "crown"), "Shadowfang Keep": (keep, "moon"), "Seat of the Naaru": naaru,
    "Grommash Hold": (burrow, "crown"), "The Nighthold": (castle, "moon"), "Great Arcane Ward": (shield, "star"),
    "Mechagon Spire": T("Mechagnomics"), "Celestial Planetarium": planet, "Grand Council of Azeroth": T("Azerothian Unity"),
    "Ravenholdt": (mask, "key"),
}


class _Scaled:
    """Draws through to an ImageDraw with every coordinate scaled, so a motif can be drawn smaller but crisp."""

    def __init__(self, d, k):
        self.d, self.k = d, k

    def _xy(self, xy):
        if xy and isinstance(xy[0], (tuple, list)):
            return [(int(round(x * self.k)), int(round(y * self.k))) for x, y in xy]
        return [int(round(v * self.k)) for v in xy]

    def rectangle(self, xy, **kw): self.d.rectangle(self._xy(xy), **kw)
    def ellipse(self, xy, **kw): self.d.ellipse(self._xy(xy), **kw)
    def polygon(self, xy, **kw): self.d.polygon(self._xy(xy), **kw)
    def line(self, xy, **kw): self.d.line(self._xy(xy), **kw)
    def arc(self, xy, a, b, **kw): self.d.arc(self._xy(xy), a, b, **kw)
    def pieslice(self, xy, a, b, **kw): self.d.pieslice(self._xy(xy), a, b, **kw)


def render(name):
    spec = ICONS[name]
    main, mark = spec if isinstance(spec, tuple) else (spec, None)
    i = Ic()
    if mark:   # draw the motif at four fifths size toward the top-left, leaving the corner for the mark
        real = i.d
        i.d = _Scaled(real, 0.8)
        main(i)
        i.d = real
        _halo(i, 26, 26, 6)
        MARKS[mark](i, 26, 26)
    else:
        main(i)
    a = i.im.resize((N * 3, N * 3), Image.NEAREST)
    out = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    ink = Image.new("RGBA", a.size, (0, 0, 0, 255))
    ink.putalpha(a)
    out.alpha_composite(ink, (2, 2))
    return out


def write_all(folder):
    if not os.path.isdir(folder):
        return 0
    for name in ICONS:
        render(name).save(os.path.join(folder, name + ".png"))
    return len(ICONS)
