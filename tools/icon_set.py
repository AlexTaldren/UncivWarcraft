"""Warcraft icon set: technologies, buildings, wonders, units, resources, improvements,
policies and promotions.

Every icon is a flat silhouette (Unciv tints them), built from a library of Warcraft
motif glyphs drawn with icons.Icon primitives: swords, axes, hammers, runes, crystals,
gears, zeppelins, gryphons, moonwells, totems... An icon is one main glyph, optionally
with a smaller badge glyph in a corner, cut out with a thin gap so both stay readable.
"""
import math, os
from PIL import Image, ImageChops, ImageDraw, ImageFilter
from icons import Icon, SS, bez

N = 100 * SS


# ======================================================================= glyph library
def G():
    return Icon()


def g_sword(i=None, a=-45):
    i = i or G()
    i.poly([(47, 8), (53, 8), (54, 66), (50, 72), (46, 66)])
    i.rect(34, 66, 66, 72)
    i.rect(47, 72, 53, 88)
    i.circle(50, 91, 5)
    return i


def g_swords():
    i = G()
    for (x0, y0, x1, y1) in ((16, 84, 84, 10), (84, 84, 16, 10)):
        i.line([(x0, y0), (x1, y1)], 7)
        i.poly([(x1 - 4 * (1 if x1 > 50 else -1), y1), (x1 + 4 * (1 if x1 > 50 else -1), y1 - 6), (x1, y1 + 6)])
    i.line([(8, 68), (32, 92)], 6); i.line([(92, 68), (68, 92)], 6)
    i.circle(12, 90, 6); i.circle(88, 90, 6)
    return i


def g_shield():
    i = G()
    sh = [(18, 14), (82, 14), (82, 48), (50, 92), (18, 48)]
    i.poly(sh)
    i.poly([(28, 22), (72, 22), (72, 46), (50, 80), (28, 46)], 0)
    i.poly([(46, 26), (54, 26), (54, 70), (50, 75), (46, 70)])
    i.rect(32, 40, 68, 47)
    return i


def g_axe():
    i = G()
    i.line([(30, 92), (62, 18)], 7)
    i.poly([(56, 14), (90, 22), (94, 48), (78, 56), (66, 40)])
    i.poly([(56, 14), (40, 10), (34, 28), (48, 34)])
    return i


def g_hammer():
    i = G()
    i.rect(43, 34, 57, 94)
    i.rect(18, 8, 82, 38)
    i.rect(22, 19, 78, 22, 0); i.rect(22, 28, 78, 31, 0)
    i.circle(50, 6, 4)
    return i


def g_anvil():
    i = G()
    i.poly([(8, 34), (70, 34), (92, 26), (84, 46), (68, 50), (62, 62), (38, 62), (32, 50), (12, 46)])
    i.rect(30, 62, 70, 72)
    i.rect(18, 72, 82, 86)
    return i


def g_bow():
    i = G()
    i.arc(30, 50, 46, -70, 70, 6)
    i.line([(46, 8), (46, 92)], 2)
    i.line([(14, 50), (92, 50)], 3)
    i.poly([(92, 50), (80, 43), (80, 57)])
    i.poly([(14, 50), (6, 44), (10, 50), (6, 56)])
    return i


def g_spear():
    i = G()
    i.line([(14, 94), (78, 22)], 5)
    i.poly([(72, 18), (94, 4), (84, 28)])
    return i


def g_gun():
    """A long flintlock rifle with a curved wooden stock, as dwarven riflemen carry."""
    i = G()
    i.line([(6, 36), (66, 46)], 5)                       # long barrel
    i.poly([(56, 42), (70, 44), (94, 58), (92, 72), (80, 70), (62, 54)])   # stock
    i.poly([(56, 38), (62, 34), (66, 40), (60, 44)])     # flintlock hammer
    i.arc(58, 52, 6, 0, 180, 2)                         # trigger guard
    return i


def g_cannon():
    i = G()
    i.poly([(16, 40), (74, 26), (78, 40), (20, 54)])
    i.circle(16, 47, 8)
    i.circle(58, 66, 18); i.circle(58, 66, 12, 0); i.circle(58, 66, 4)
    for a in range(0, 360, 45):
        i.line([(58, 66), (58 + 12 * math.cos(math.radians(a)), 66 + 12 * math.sin(math.radians(a)))], 2)
    return i


def g_bomb():
    i = G()
    i.circle(46, 58, 30)
    i.rect(40, 22, 54, 32)
    i.bline((47, 22), (52, 10), (64, 6), (72, 12), 3)
    i.star(76, 12, 12, 4, 8)
    i.circle(36, 48, 6, 0)
    return i


def g_flame():
    i = G()
    i.poly([(50, 4), (66, 30), (80, 56), (72, 84), (50, 94), (28, 84), (20, 58), (34, 34), (40, 48)])
    i.poly([(50, 46), (60, 62), (60, 78), (50, 86), (40, 78), (40, 62)], 0)
    return i


def g_bolt():
    i = G()
    i.poly([(58, 4), (22, 54), (46, 54), (36, 96), (78, 40), (54, 40), (66, 4)])
    return i


def g_gear(i=None, cx=50, cy=50, r=30, teeth=10):
    i = i or G()
    i.circle(cx, cy, r)
    i.rays(cx, cy, r - 2, r + 12, teeth, 11 * r / 30)
    i.circle(cx, cy, r * 0.42, 0)
    return i


def g_gears():
    i = G()
    g_gear(i, 38, 58, 22, 9)
    g_gear(i, 72, 30, 15, 7)
    return i


def g_crystal():
    i = G()
    i.poly([(50, 4), (70, 34), (62, 94), (38, 94), (30, 34)])
    i.poly([(50, 4), (50, 94), (38, 94), (30, 34)], 0)
    i.poly([(50, 10), (49, 90), (39, 90), (33, 35)])
    i.line([(50, 8), (50, 92)], 2, 0)
    return i


def g_crystals():
    i = G()
    for x, top, w in ((30, 30, 13), (50, 6, 16), (72, 26, 13)):
        i.poly([(x, top), (x + w, top + 22), (x + w * 0.6, 94), (x - w * 0.6, 94), (x - w, top + 22)])
        i.line([(x, top + 4), (x, 90)], 2, 0)
    return i


def g_orb():
    i = G()
    i.circle(50, 46, 32)
    i.circle(40, 36, 9, 0)
    i.poly([(28, 80), (72, 80), (78, 94), (22, 94)])
    i.rays(50, 46, 36, 46, 8, 6)
    return i


def g_eye():
    i = G()
    i.poly([(4, 50), (26, 26), (50, 18), (74, 26), (96, 50), (74, 74), (50, 82), (26, 74)])
    i.circle(50, 50, 22, 0)
    i.circle(50, 50, 14)
    i.circle(44, 44, 4, 0)
    return i


def g_book():
    i = G()
    i.poly([(8, 22), (48, 30), (48, 90), (8, 82)])
    i.poly([(92, 22), (52, 30), (52, 90), (92, 82)])
    for y in (40, 52, 64):
        i.line([(16, y - 6), (40, y)], 3, 0); i.line([(84, y - 6), (60, y)], 3, 0)
    return i


def g_scroll():
    i = G()
    i.rect(22, 18, 78, 82)
    i.circle(22, 18, 8); i.circle(78, 18, 8); i.circle(22, 82, 8); i.circle(78, 82, 8)
    i.rect(14, 10, 86, 18); i.rect(14, 82, 86, 90)
    for y in (32, 44, 56, 68):
        i.line([(32, y), (68, y)], 3, 0)
    return i


def g_quill():
    i = G()
    i.poly([(88, 6), (60, 22), (30, 62), (22, 80), (40, 70), (74, 34)])
    i.line([(22, 80), (12, 94)], 3)
    i.line([(80, 14), (34, 66)], 2, 0)
    return i


def g_rune():
    """A rune stone: a carved diamond with an angular titan rune."""
    i = G()
    i.poly([(50, 2), (92, 50), (50, 98), (8, 50)])
    i.poly([(50, 14), (80, 50), (50, 86), (20, 50)], 0)
    i.line([(50, 24), (50, 76)], 6)
    i.line([(50, 40), (66, 30)], 5)
    i.line([(50, 56), (34, 46)], 5)
    i.line([(50, 70), (64, 62)], 5)
    return i


def g_star():
    i = G()
    i.star(50, 52, 44, 18, 5)
    return i


def g_sparkle():
    i = G()
    i.star(50, 50, 44, 9, 4)
    i.star(82, 18, 12, 3, 4)
    i.star(18, 82, 10, 3, 4)
    return i


def g_moon():
    i = G()
    i.circle(46, 50, 40)
    i.circle(62, 40, 34, 0)
    i.star(76, 70, 10, 3, 4)
    return i


def g_sun():
    i = G()
    i.circle(50, 50, 22)
    i.rays(50, 50, 28, 46, 12, 9)
    return i


def g_tree(i=None):
    i = i or G()
    i.poly([(44, 94), (56, 94), (54, 56), (46, 56)])
    i.line([(44, 94), (32, 98)], 4); i.line([(56, 94), (68, 98)], 4)
    for cx, cy, r in ((50, 30, 24), (28, 46, 18), (72, 46, 18), (50, 52, 16)):
        i.circle(cx, cy, r)
    return i


def g_leaf():
    i = G()
    i.poly([(14, 86), (20, 44), (44, 18), (86, 12), (82, 54), (56, 80)])
    i.line([(14, 86), (70, 30)], 3, 0)
    for k in range(3):
        i.line([(32 + k * 12, 68 - k * 12), (32 + k * 12, 50 - k * 12)], 2, 0)
    return i


def g_mushroom():
    i = G()
    i.poly([(42, 50), (58, 50), (62, 92), (38, 92)])
    i.poly([(8, 52), (16, 28), (50, 10), (84, 28), (92, 52)])
    for cx, cy in ((32, 34), (56, 24), (70, 40)):
        i.circle(cx, cy, 5, 0)
    return i


def g_skull():
    i = G()
    i.circle(50, 40, 32)
    i.rect(32, 60, 68, 82)
    i.circle(37, 42, 9, 0); i.circle(63, 42, 9, 0)
    i.poly([(50, 54), (44, 64), (56, 64)], 0)
    for x in (40, 50, 60):
        i.rect(x - 1.5, 72, x + 1.5, 82, 0)
    return i


def g_crown():
    i = G()
    i.poly([(10, 78), (90, 78), (94, 26), (72, 52), (50, 16), (28, 52), (6, 26)])
    i.rect(10, 82, 90, 92)
    for x in (30, 50, 70):
        i.circle(x, 68, 4, 0)
    return i


def g_tower():
    i = G()
    i.poly([(32, 94), (68, 94), (62, 36), (38, 36)])
    for x in (34, 46, 58):
        i.rect(x, 26, x + 8, 36)
    i.rect(34, 30, 66, 38)
    i.poly([(40, 26), (60, 26), (50, 4)])
    i.rect(46, 52, 54, 64, 0)
    i.poly([(44, 94), (56, 94), (56, 80), (50, 74), (44, 80)], 0)
    return i


def g_castle():
    i = G()
    i.rect(14, 44, 86, 94)
    for x in (8, 70):
        i.rect(x, 24, x + 22, 94)
        for k in range(3):
            i.rect(x + k * 8, 16, x + k * 8 + 5, 24)
    for k in range(4):
        i.rect(34 + k * 9, 36, 39 + k * 9, 44)
    i.poly([(42, 94), (58, 94), (58, 72), (50, 64), (42, 72)], 0)
    return i


def g_temple():
    i = G()
    i.poly([(10, 36), (50, 10), (90, 36)])
    i.rect(14, 38, 86, 44)
    for x in (20, 36, 52, 68):
        i.rect(x, 46, x + 10, 84)
    i.rect(10, 84, 90, 94)
    return i


def g_dome():
    i = G()
    i.ellipse(50, 50, 32, 30)
    i.rect(14, 50, 86, 90)
    i.rect(8, 88, 92, 96)
    i.rect(48, 6, 52, 22)
    i.circle(50, 6, 4)
    i.poly([(42, 90), (58, 90), (58, 70), (50, 64), (42, 70)], 0)
    return i


def g_spire():
    i = G()
    for x, h in ((28, 46), (50, 10), (72, 46)):
        i.poly([(x - 9, 94), (x + 9, 94), (x + 7, h + 20), (x, h), (x - 7, h + 20)])
    i.rect(16, 74, 84, 94)
    i.poly([(44, 94), (56, 94), (56, 82), (50, 76), (44, 82)], 0)
    return i


def g_pagoda():
    i = G()
    for k, (w, y) in enumerate(((44, 78), (36, 56), (28, 36), (18, 18))):
        i.poly([(50 - w - 4, y), (50 + w + 4, y), (50 + w - 4, y - 8), (50 - w + 4, y - 8)])
        i.rect(50 - w + 8, y, 50 + w - 8, y + 12 if k else y + 16)
    i.rect(48, 2, 52, 12)
    return i


def g_tent():
    i = G()
    i.poly([(8, 92), (50, 14), (92, 92)])
    i.line([(50, 14), (38, 2)], 3); i.line([(50, 14), (62, 2)], 3)
    i.poly([(42, 92), (50, 62), (58, 92)], 0)
    i.line([(22, 70), (78, 70)], 4, 0)
    return i


def g_hut():
    i = G()
    i.poly([(6, 56), (50, 6), (94, 56)])
    i.rect(18, 56, 82, 92)
    i.rect(42, 70, 58, 92, 0)
    return i


def g_ziggurat():
    i = G()
    for k in range(4):
        w = 44 - k * 10
        i.rect(50 - w, 90 - k * 18, 50 + w, 92 - k * 18 - 14)
    i.rect(44, 6, 56, 20)
    i.rect(46, 30, 54, 92, 0)
    return i


def g_mountain():
    i = G()
    i.poly([(4, 92), (36, 28), (52, 52), (66, 18), (96, 92)])
    i.poly([(36, 28), (44, 44), (38, 40), (30, 44)], 0)
    i.poly([(66, 18), (76, 40), (68, 34), (60, 40)], 0)
    return i


def g_portal():
    i = G()
    i.rect(10, 20, 26, 94); i.rect(74, 20, 90, 94)
    i.poly([(4, 22), (96, 22), (90, 8), (10, 8)])
    i.poly([(2, 10), (10, 8), (4, 0)]); i.poly([(98, 10), (90, 8), (96, 0)])
    i.rect(30, 26, 70, 94)
    for k in range(4):
        i.arc(50, 60, 6 + k * 6, k * 70, k * 70 + 220, 3, 0)
    return i


def g_wave():
    i = G()
    for y in (40, 62, 84):
        pts = [(x, y + 8 * math.sin(x / 9)) for x in range(4, 97, 3)]
        i.line(pts, 7)
    return i


def g_ship():
    i = G()
    i.poly([(6, 70), (94, 70), (82, 90), (16, 90)])
    i.rect(48, 8, 52, 70)
    i.poly([(54, 12), (86, 30), (54, 62)])
    i.poly([(46, 18), (16, 40), (46, 62)])
    return i


def g_zeppelin():
    i = G()
    i.ellipse(54, 34, 40, 20)
    i.poly([(10, 20), (20, 34), (10, 48)])
    i.line([(18, 34), (92, 34)], 2, 0)
    i.line([(40, 52), (42, 66)], 3); i.line([(68, 52), (66, 66)], 3)
    i.poly([(30, 66), (80, 66), (74, 80), (36, 80)])
    i.ellipse(26, 72, 3, 10)
    return i


def g_gryphon():
    """A gryphon's head and raised wing."""
    i = G()
    i.poly([(30, 94), (36, 60), (30, 40), (40, 24), (58, 18), (74, 24), (90, 22), (80, 34), (72, 40), (64, 54), (60, 94)])
    i.poly([(74, 24), (96, 30), (80, 34)])
    i.circle(56, 30, 4, 0)
    for k in range(4):
        i.poly([(30, 50 - k * 2), (6 + k * 3, 30 - k * 9), (10 + k * 3, 44 - k * 8)])
    return i


def g_wing():
    i = G()
    for k in range(5):
        i.poly([(20, 80), (30 + k * 14, 10 + k * 4), (40 + k * 12, 22 + k * 6), (26, 86)])
    i.circle(20, 84, 8)
    return i


def g_wolf():
    i = G()
    i.poly([(18, 92), (26, 54), (20, 16), (40, 36), (60, 36), (80, 16), (74, 54), (82, 92), (64, 80), (50, 94), (36, 80)])
    i.poly([(32, 54), (44, 52), (40, 60)], 0); i.poly([(68, 54), (56, 52), (60, 60)], 0)
    i.poly([(44, 76), (56, 76), (50, 84)], 0)
    return i


def g_horse():
    i = G()
    i.poly([(30, 94), (34, 60), (24, 44), (20, 30), (36, 14), (50, 6), (60, 14), (78, 40), (88, 58), (82, 66), (64, 56), (60, 94)])
    i.circle(46, 22, 4, 0)
    return i


def g_dragon():
    i = G()
    i.poly([(14, 90), (24, 56), (20, 30), (34, 14), (60, 10), (90, 24), (70, 32), (88, 44), (60, 46), (48, 60), (50, 90)])
    i.poly([(34, 14), (24, 0), (44, 12)]); i.poly([(46, 12), (44, 0), (56, 10)])
    i.circle(46, 24, 4, 0)
    return i


def g_flask():
    i = G()
    i.rect(40, 6, 60, 14)
    i.poly([(42, 14), (58, 14), (58, 34), (86, 82), (80, 94), (20, 94), (14, 82), (42, 34)])
    i.poly([(26, 70), (74, 70), (82, 84), (18, 84)], 0)
    i.circle(40, 78, 5); i.circle(58, 76, 3)
    return i


def g_cauldron():
    i = G()
    i.ellipse(50, 60, 40, 28)
    i.rect(8, 34, 92, 42)
    i.line([(24, 84), (18, 96)], 5); i.line([(76, 84), (82, 96)], 5)
    for cx, cy, r in ((36, 24, 8), (56, 16, 6), (66, 28, 5)):
        i.circle(cx, cy, r)
    return i


def g_coin():
    i = G()
    i.circle(50, 50, 40)
    i.circle(50, 50, 32, 0)
    i.circle(50, 50, 26)
    i.star(50, 50, 16, 7, 6, v=0)
    return i


def g_coins():
    i = G()
    for k in range(4):
        i.ellipse(36, 86 - k * 12, 28, 9)
        i.line([(9, 86 - k * 12), (63, 86 - k * 12)], 2, 0)
    i.circle(72, 40, 22); i.circle(72, 40, 16, 0); i.circle(72, 40, 11)
    return i


def g_scales():
    i = G()
    i.rect(47, 14, 53, 86)
    i.rect(26, 86, 74, 94)
    i.line([(14, 26), (86, 26)], 5)
    for x in (18, 82):
        i.line([(x, 28), (x - 10, 56)], 2); i.line([(x, 28), (x + 10, 56)], 2)
        i.poly([(x - 14, 56), (x + 14, 56), (x + 8, 66), (x - 8, 66)])
    i.circle(50, 10, 6)
    return i


def g_banner():
    i = G()
    i.rect(14, 4, 20, 96)
    i.poly([(20, 10), (88, 10), (88, 62), (54, 50), (20, 62)])
    i.star(54, 30, 12, 5, 5, v=0)
    return i


def g_horn():
    i = G()
    i.poly([(8, 30), (22, 22), (60, 50), (86, 56), (92, 78), (70, 84), (50, 66)])
    i.ellipse(14, 26, 7, 12)
    i.line([(30, 40), (76, 70)], 2, 0)
    return i


def g_drum():
    i = G()
    i.ellipse(50, 30, 38, 12)
    i.rect(12, 30, 88, 78)
    i.ellipse(50, 78, 38, 12)
    i.ellipse(50, 30, 32, 8, 0)
    for x in range(20, 82, 12):
        i.line([(x, 42), (x + 10, 70)], 2, 0)
    i.line([(70, 6), (40, 22)], 4); i.circle(70, 6, 5)
    return i


def g_totem():
    i = G()
    i.rect(36, 16, 64, 96)
    i.poly([(4, 22), (36, 18), (36, 30)]); i.poly([(96, 22), (64, 18), (64, 30)])
    for y in (30, 58, 80):
        i.rect(40, y, 46, y + 5, 0); i.rect(54, y, 60, y + 5, 0)
        i.rect(42, y + 10, 58, y + 13, 0)
    i.poly([(36, 16), (64, 16), (50, 2)])
    return i


def g_mask():
    i = G()
    i.poly([(18, 10), (82, 10), (90, 50), (70, 90), (50, 96), (30, 90), (10, 50)])
    i.poly([(26, 34), (44, 38), (40, 48), (26, 46)], 0); i.poly([(74, 34), (56, 38), (60, 48), (74, 46)], 0)
    i.rect(38, 66, 62, 74, 0)
    for x in (42, 50, 58):
        i.rect(x - 1.5, 66, x + 1.5, 74)
    i.poly([(2, 0), (18, 10), (12, 24)]); i.poly([(98, 0), (82, 10), (88, 24)])
    return i


def g_hand_light():
    i = G()
    i.poly([(30, 94), (26, 60), (18, 44), (24, 40), (32, 52), (32, 24), (38, 24), (40, 46), (42, 18), (48, 18),
            (50, 46), (52, 22), (58, 22), (60, 48), (62, 30), (68, 30), (68, 66), (60, 94)])
    i.rays(46, 8, 6, 14, 8, 4)
    return i


def g_chalice():
    i = G()
    i.poly([(18, 10), (82, 10), (76, 38), (58, 50), (54, 76), (70, 90), (30, 90), (46, 76), (42, 50), (24, 38)])
    i.rect(22, 16, 78, 20, 0)
    return i


def g_key():
    i = G()
    i.ring(30, 30, 20, 9)
    i.line([(44, 44), (90, 90)], 9)
    i.line([(70, 70), (80, 60)], 7); i.line([(80, 80), (90, 70)], 7)
    return i


def g_hourglass():
    i = G()
    i.rect(18, 6, 82, 14); i.rect(18, 86, 82, 94)
    i.poly([(24, 14), (76, 14), (54, 50), (76, 86), (24, 86), (46, 50)])
    i.poly([(32, 20), (68, 20), (52, 46), (48, 46)], 0)
    i.poly([(50, 62), (70, 82), (30, 82)], 0)
    return i


def g_world():
    i = G()
    i.circle(50, 50, 44)
    i.circle(50, 50, 38, 0)
    i.poly([(18, 34), (34, 22), (44, 30), (40, 52), (28, 62), (20, 52)])          # Kalimdor-ish
    i.poly([(58, 20), (74, 26), (80, 44), (70, 56), (62, 44)])                    # Eastern Kingdoms-ish
    i.poly([(44, 64), (60, 64), (58, 74), (46, 74)])
    return i


def g_golem():
    i = G()
    i.rect(30, 6, 70, 34)
    i.rect(36, 16, 46, 22, 0); i.rect(54, 16, 64, 22, 0)
    i.rect(16, 36, 84, 72)
    i.rect(6, 36, 16, 66); i.rect(84, 36, 94, 66)
    i.rect(24, 72, 42, 96); i.rect(58, 72, 76, 96)
    i.circle(50, 54, 8, 0)
    return i


def g_turtle():
    i = G()
    i.ellipse(48, 56, 38, 26)
    i.ellipse(86, 54, 10, 8)
    for x, y in ((24, 80), (68, 82), (20, 34), (66, 32)):
        i.ellipse(x, y, 9, 6)
    for x, y in ((34, 50), (52, 44), (50, 64)):
        i.circle(x, y, 7, 0)
    return i


def g_anchor():
    i = G()
    i.ring(50, 14, 9, 5)
    i.rect(46, 22, 54, 86)
    i.rect(28, 32, 72, 38)
    i.arc(50, 58, 34, 20, 160, 7)
    i.poly([(12, 64), (22, 56), (24, 70)]); i.poly([(88, 64), (78, 56), (76, 70)])
    return i


def g_wheel():
    i = G()
    i.ring(50, 50, 40, 8)
    i.circle(50, 50, 9)
    i.rays(50, 50, 8, 40, 8, 5)
    return i


def g_pick():
    i = G()
    i.line([(26, 94), (62, 22)], 7)
    i.bline((10, 30), (36, 6), (76, 6), (94, 34), 7)
    return i


def g_saw():
    i = G()
    g_gear(i, 50, 50, 34, 18)
    i.circle(50, 50, 10)
    return i


def g_compass():
    i = G()
    i.ring(50, 50, 40, 6)
    i.poly([(50, 14), (58, 50), (50, 86), (42, 50)])
    i.poly([(50, 14), (58, 50), (42, 50)], 0)
    i.poly([(50, 22), (55, 48), (45, 48)])
    return i


def g_scope():
    i = G()
    i.poly([(8, 46), (70, 18), (76, 30), (14, 58)])
    i.rect(70, 14, 86, 34)
    i.line([(44, 40), (30, 92)], 4); i.line([(44, 40), (58, 92)], 4)
    return i


def g_lute():
    i = G()
    i.ellipse(36, 64, 26, 28)
    i.circle(36, 64, 7, 0)
    i.line([(52, 44), (88, 8)], 7)
    i.rect(80, 2, 94, 14)
    return i


def g_void():
    i = G()
    for k in range(5):
        i.arc(50, 50, 10 + k * 8, k * 50, k * 50 + 250, 5)
    i.circle(50, 50, 7)
    return i


def g_tentacle_eye():
    i = G()
    i.circle(50, 40, 26)
    i.circle(50, 40, 14, 0)
    i.circle(50, 40, 7)
    for x, c in ((26, -1), (50, 0), (74, 1)):
        i.bline((x, 60), (x + 10 * c, 74), (x - 10 * c, 86), (x + 6 * c, 98), 7)
    return i


def g_rocket():
    i = G()
    i.poly([(50, 4), (64, 24), (64, 70), (36, 70), (36, 24)])
    i.poly([(36, 50), (20, 76), (36, 72)]); i.poly([(64, 50), (80, 76), (64, 72)])
    i.circle(50, 34, 7, 0)
    i.poly([(40, 72), (60, 72), (50, 98)])
    return i


def g_plow():
    i = G()
    i.line([(10, 30), (60, 60)], 6)
    i.poly([(56, 54), (92, 62), (84, 84), (60, 80)])
    i.line([(30, 42), (24, 80)], 5)
    i.line([(10, 30), (4, 20)], 6)
    return i


def g_wheat():
    i = G()
    i.line([(50, 96), (50, 20)], 4)
    for k in range(4):
        y = 22 + k * 14
        i.ellipse(40, y + 4, 8, 5); i.ellipse(60, y + 4, 8, 5)
    i.ellipse(50, 14, 5, 9)
    return i


def g_fish():
    i = G()
    i.ellipse(42, 50, 34, 18)
    i.poly([(72, 50), (96, 30), (96, 70)])
    i.circle(24, 46, 4, 0)
    return i


def g_bee():
    i = G()
    for k in range(3):
        i.ellipse(50, 30 + k * 22, 30 - k * 6, 12)
        i.line([(26 + k * 6, 40 + k * 22), (74 - k * 6, 40 + k * 22)], 3, 0)
    i.rect(44, 84, 56, 94, 0)
    return i


def g_tusk():
    i = G()
    i.bline((20, 92), (10, 40), (40, 10), (80, 8), 12)
    i.bline((50, 92), (44, 60), (60, 40), (90, 34), 8)
    return i


def g_ink():
    i = G()
    i.poly([(26, 46), (74, 46), (82, 90), (18, 90)])
    i.rect(36, 34, 64, 46)
    i.poly([(60, 34), (92, 2), (96, 6), (66, 38)])
    return i


def g_hex_cells():
    i = G()
    for cx, cy in ((34, 34), (66, 34), (50, 62), (18, 62), (82, 62), (34, 88), (66, 88)):
        pts = [(cx + 15 * math.cos(math.radians(a)), cy + 15 * math.sin(math.radians(a))) for a in range(30, 390, 60)]
        i.poly(pts)
        pts = [(cx + 9 * math.cos(math.radians(a)), cy + 9 * math.sin(math.radians(a))) for a in range(30, 390, 60)]
        i.poly(pts, 0)
    return i


def g_gem():
    i = G()
    i.poly([(20, 34), (34, 16), (66, 16), (80, 34), (50, 88)])
    i.line([(20, 34), (80, 34)], 3, 0)
    i.line([(34, 16), (44, 34), (50, 88)], 2, 0); i.line([(66, 16), (56, 34), (50, 88)], 2, 0)
    return i


def g_feather_plume():
    i = G()
    i.bline((20, 94), (30, 50), (60, 20), (90, 6), 10)
    for k in range(6):
        i.line([(30 + k * 9, 70 - k * 10), (16 + k * 9, 56 - k * 10)], 3)
    return i


def g_heart():
    i = G()
    i.circle(34, 38, 22); i.circle(66, 38, 22)
    i.poly([(13, 46), (87, 46), (50, 90)])
    return i


def g_eye_kilrogg():
    i = g_eye()
    i.line([(50, 82), (50, 96)], 3)
    i.line([(20, 70), (10, 84)], 3); i.line([(80, 70), (90, 84)], 3)
    return i


def g_paw():
    i = G()
    i.ellipse(50, 66, 24, 20)
    for x, y in ((22, 38), (40, 22), (60, 22), (78, 38)):
        i.ellipse(x, y, 9, 11)
    return i


def g_ram_head():
    i = G()
    i.poly([(36, 30), (64, 30), (62, 72), (50, 92), (38, 72)])
    i.ring(26, 34, 16, 8); i.ring(74, 34, 16, 8)
    i.circle(42, 50, 4, 0); i.circle(58, 50, 4, 0)
    return i


def g_bandage():
    i = G()
    i.rect(38, 10, 62, 90)
    i.rect(10, 38, 90, 62)
    return i


def g_feet():
    i = G()
    for x, y in ((30, 70), (66, 40)):
        i.ellipse(x, y, 13, 18)
        for k in range(4):
            i.circle(x - 9 + k * 6, y - 22, 3)
    return i


def g_chains():
    i = G()
    for k in range(4):
        i.ring(22 + k * 19, 30 + k * 13, 11, 5)
    return i


def g_shovel():
    i = G()
    i.line([(80, 10), (40, 60)], 5)
    i.poly([(34, 52), (50, 66), (32, 94), (14, 80)])
    return i


def g_lantern():
    i = G()
    i.ring(50, 12, 8, 4)
    i.poly([(30, 22), (70, 22), (78, 34), (22, 34)])
    i.rect(28, 34, 72, 80)
    i.rect(36, 40, 64, 74, 0)
    i.ellipse(50, 60, 8, 10)
    i.rect(24, 80, 76, 90)
    return i


def g_pumpkin():
    i = G()
    i.ellipse(50, 60, 40, 32)
    for x in (34, 50, 66):
        i.line([(x, 34), (x, 88)], 2, 0)
    i.rect(46, 14, 54, 30)
    return i


def g_fruit():
    i = G()
    i.circle(50, 60, 34)
    i.line([(50, 26), (54, 8)], 4)
    i.poly([(56, 18), (80, 6), (78, 22)])
    i.circle(38, 48, 7, 0)
    return i


def g_banana():
    i = G()
    for k in range(3):
        i.bline((14, 30 + k * 12), (30, 84 + k * 4), (70, 86 + k * 2), (90, 54 + k * 8), 9)
    i.rect(10, 22, 20, 34)
    return i


def g_salt():
    i = G()
    i.poly([(14, 92), (32, 40), (50, 60), (68, 30), (88, 92)])
    for x, y in ((32, 50), (66, 42)):
        i.poly([(x - 6, y + 6), (x, y - 4), (x + 6, y + 6)], 0)
    return i


def g_jade():
    i = G()
    i.poly([(34, 92), (66, 92), (62, 70), (72, 52), (64, 22), (50, 8), (36, 22), (28, 52), (38, 70)])
    i.circle(50, 40, 10, 0)
    i.rect(30, 86, 70, 96)
    return i


def g_naaru():
    i = G()
    i.circle(50, 50, 14)
    for k in range(8):
        a = math.radians(k * 45 + 22)
        cx, cy = 50 + 32 * math.cos(a), 50 + 32 * math.sin(a)
        i.poly([(cx, cy - 10), (cx + 6, cy), (cx, cy + 10), (cx - 6, cy)])
    return i


def g_ghost():
    i = G()
    i.poly([(20, 92), (20, 40), (30, 16), (50, 8), (70, 16), (80, 40), (80, 92), (70, 82), (60, 92), (50, 82), (40, 92), (30, 82)])
    i.circle(38, 38, 7, 0); i.circle(62, 38, 7, 0)
    return i


def g_coffin():
    i = G()
    i.poly([(30, 4), (70, 4), (82, 28), (70, 96), (30, 96), (18, 28)])
    i.poly([(50, 24), (60, 40), (50, 56), (40, 40)], 0)
    i.circle(50, 40, 4)
    return i


def g_fist():
    i = G()
    i.poly([(20, 40), (80, 40), (84, 70), (70, 90), (30, 90), (16, 66)])
    for x in (28, 42, 56, 70):
        i.rect(x - 6, 22, x + 6, 44)
    i.poly([(14, 52), (34, 58), (30, 70), (16, 66)])
    return i


def g_helm():
    i = G()
    i.poly([(18, 92), (18, 40), (30, 16), (50, 8), (70, 16), (82, 40), (82, 92), (62, 92), (62, 60), (38, 60), (38, 92)])
    i.rect(26, 40, 74, 48, 0)
    i.poly([(46, 8), (54, 8), (52, -2), (48, -2)])
    return i


def g_boot():
    i = G()
    i.poly([(30, 6), (58, 6), (58, 64), (90, 74), (90, 92), (24, 92)])
    i.rect(28, 20, 60, 26, 0)
    return i


def g_target():
    i = G()
    i.ring(50, 50, 40, 7); i.ring(50, 50, 22, 7); i.circle(50, 50, 7)
    i.line([(76, 24), (96, 4)], 4); i.poly([(70, 30), (66, 16), (84, 34)])
    return i


def g_net():
    i = G()
    for k in range(5):
        i.line([(10 + k * 20, 10), (10 + k * 20, 90)], 3)
        i.line([(10, 10 + k * 20), (90, 10 + k * 20)], 3)
    return i


def g_ladder():
    i = G()
    i.rect(24, 4, 32, 96); i.rect(68, 4, 76, 96)
    for y in range(14, 96, 16):
        i.rect(32, y, 68, y + 5)
    return i


def g_arrows_up():
    i = G()
    for x in (28, 50, 72):
        i.line([(x, 94), (x, 24)], 5)
        i.poly([(x - 9, 30), (x, 10), (x + 9, 30)])
    return i


GLYPHS = {k[2:]: v for k, v in dict(globals()).items() if k.startswith("g_") and callable(v)}
_cache = {}


def glyph(name):
    if name not in _cache:
        _cache[name] = GLYPHS[name]().im
    return _cache[name]


# ======================================================================= composition
def compose(main, badge=None, corner="br"):
    """main glyph full size; badge 45% size in a corner, with a cut-out gap."""
    img = glyph(main).copy()
    if badge:
        b = glyph(badge).resize((int(N * 0.46), int(N * 0.46)), Image.LANCZOS)
        bx = N - b.width if corner[1] == "r" else 0
        by = N - b.height if corner[0] == "b" else 0
        gap = b.filter(ImageFilter.GaussianBlur(SS * 3)).point(lambda v: 255 if v > 8 else 0)
        hole = Image.new("L", (N, N), 0)
        hole.paste(gap, (bx, by))
        img = ImageChops.subtract(img, hole)
        img.paste(255, (bx, by), b)
    return img


def save(img, path, color=(255, 255, 255)):
    mask = img.resize((100, 100), Image.LANCZOS)
    out = Image.new("RGBA", (100, 100), color + (0,))
    out.putalpha(mask)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out.save(path)


# ======================================================================= recipes
# name -> "glyph" or ("glyph", "badge")
TECHS = {
    "Farming": "wheat", "Pottery": "cauldron", "Beast Taming": "paw", "Archery": "bow", "Mining": "pick",
    "Sailing": "ship", "Herbalism": "leaf", "Runic Script": "rune", "Skinning": ("paw", "sword"),
    "The Wheel": "wheel", "Masonry": "castle", "Bronze Working": "anvil", "Optics": "scope", "Riding": "horse",
    "Mathematics": ("scroll", "rune"), "Construction": "ladder", "Philosophy": ("book", "star"),
    "Bardic Lore": "lute", "Coinage": "coin", "Engineering": "gears", "Iron Forged Swords": "sword",
    "Priesthood": "hand_light", "Arathi Law": ("scroll", "crown"), "Trade Guilds": ("scales", "hammer"),
    "Blacksmithing": ("anvil", "flame"), "Seafaring": "compass", "Scholarship": ("book", "quill"),
    "Animal War Training": ("horse", "shield"), "Clockwork": "gear", "Siege Engineering": ("cannon", "gear"),
    "Steel Forged Swords": ("sword", "star"), "Astronomy": ("moon", "scope"), "Choral Hymns": ("hand_light", "lute"),
    "Banking": "coins", "Inscription": "quill", "Blackpowder": "bomb", "Navigation": ("compass", "star"),
    "Architecture": "spire", "Auctioneering": ("scales", "coin"), "Mithril Forged Swords": ("sword", "sparkle"),
    "Alchemy": "flask", "Archaeology": ("shovel", "skull"), "Arcane Science": ("orb", "book"),
    "Steamworks": ("gears", "flame"), "Long Rifles": "gun", "War Doctrine": ("banner", "swords"),
    "Soil Enrichment": ("wheat", "flask"), "Natural Lore": ("tree", "leaf"), "Storm Hammers": ("hammer", "bolt"),
    "Steam Power": ("wheel", "flame"), "Seaforium": ("bomb", "sparkle"), "Frost Enchantment": ("crystal", "sparkle"),
    "Communication Crystals": ("crystal", "eye"), "Gnomish Gearworks": ("gears", "hammer"),
    "Gnomish Flight": ("wing", "gear"), "Tramways": ("wheel", "gears"), "Arcanite Alloys": ("anvil", "crystal"),
    "Arcane Conduits": ("bolt", "crystal"), "Fragmentation Shards": ("bomb", "crystals"),
    "Liquid Fire": ("flask", "flame"), "Elixir Mastery": ("flask", "heart"), "Mana Theory": "orb",
    "Scrying": ("orb", "eye"), "Battle Formations": "swords", "Nature's Blessing": ("leaf", "sun"),
    "Unstable Mana": ("orb", "bolt"), "Demolition": "rocket", "Titan Logic": ("golem", "rune"),
    "Portal Networks": "portal", "War Drums": "drum", "Siege Barrage": ("cannon", "flame"),
    "Eye of Kilrogg": "eye_kilrogg", "Mechagnomics": ("golem", "gear"), "Focused Arcana": ("crystal", "bolt"),
    "Azerothian Unity": "world", "Azerite Refinement": ("crystals", "flame"), "Titanforging": ("anvil", "rune"),
    "Ethereal Technology": ("naaru", "gear"), "Invisibility": "ghost", "Secrets of the Void": "tentacle_eye",
}

UNITS = {
    "Settler": "banner", "Scout": "eye", "Mounted Archer": ("horse", "bow"),
    "Spearman": "spear", "Catapult": ("cannon", "skull"), "Ranger": ("bow", "leaf"), "Swordsman": "sword",
    "Knight": "helm", "Lancer": ("horse", "spear"), "Cannon": "cannon", "Mountaineer": ("gun", "mountain"),
    "Rifleman": "gun", "Musketeer": ("gun", "bomb"), "Cavalry": ("horse", "gun"), "Ironclad": ("ship", "gear"),
    "Mortar Team": ("cannon", "mountain"), "Gnomish Submarine": ("fish", "gear"), "Fusilier": ("gun", "sword"),
    "Gyrocopter": ("wing", "gear"), "Bomber Zeppelin": ("zeppelin", "bomb"), "Shock Trooper": ("helm", "gun"),
    "Airship Tender": ("zeppelin", "wing"), "Dreadnought": ("ship", "cannon"), "Grenadier": "bomb",
    "Flak Cannon": ("cannon", "wing"), "War Golem": "golem", "Destroyer": ("ship", "bolt"),
    "Kul Tiran Marine": ("anchor", "gun"), "Gryphon Rider": "gryphon", "War Zeppelin": "zeppelin",
    "Skyguard": ("wing", "gun"), "Siege Engine": ("wheel", "hammer"), "Siegebreaker": ("rocket", "shield"),
    "Mana Bomb": ("orb", "bomb"), "Demolisher": ("cannon", "flame"), "Flak Wagon": ("rocket", "wheel"),
    "Arcane Missile": ("crystal", "bolt"), "Arcane Annihilator": ("orb", "skull"), "Flying Machine": ("gear", "wing"),
    "Giant Turtle": "turtle", "Mechagnome Trooper": ("golem", "gun"), "Juggernaught": ("ship", "skull"),
    "Mechano-Tank": ("golem", "wheel"), "Sky Golem": ("golem", "wing"), "Iron Colossus": ("golem", "rune"),
    "Void Bomber": ("zeppelin", "void"), "Great Artist": "lute", "Great Merchant": "coins",
    "Great Engineer": ("gears", "hammer"), "Great Prophet": "hand_light", "Great General": "banner",
    "Great Admiral": "anchor", "Missionary": ("book", "hand_light"), "Inquisitor": ("flame", "book"),
    "Arcane Thruster": ("rocket", "rune"), "Navigation Crystal": ("crystal", "compass"),
    "Titan Engine": ("gear", "rune"), "Stasis Vault": ("coffin", "crystal"), "Great Scientist": ("orb", "book"),
    "Militia": "axe", "Fishing Skiff": ("ship", "fish"), "Longboat": "ship", "War Galley": ("ship", "bow"),
    "Brigantine": ("ship", "compass"), "Buccaneer": ("ship", "skull"), "Frigate": ("ship", "cannon"),
    "Ballista": ("spear", "wheel"), "Outrider": "horse", "Pikeman": ("spear", "shield"),
    "Crossbowman": ("bow", "gear"), "Vanguard": ("sword", "shield"), "Archer": "bow",
}

RESOURCES = {
    "Azerite": "crystals", "Arcane Crystals": "crystal", "Elementium": ("gem", "bolt"), "Thorium": ("pick", "gem"),
    "Tel'Abim Bananas": "banana", "Sunfruit": "fruit", "Honeycomb": "hex_cells", "Mammoth Ivory": "tusk",
    "Moonglow Ink": "ink", "Glowcap": "mushroom", "Leviathans": "fish", "Deeprock Salt": "salt",
    "Jeweled Trinkets": "gem", "Jade Carvings": "jade", "Truesilver": ("pick", "sparkle"), "Mageweave": "scroll",
    "Ale": "chalice", "Rugged Leather": ("paw", "sword"), "Peacebloom": "leaf", "Mageroyal": ("leaf", "sparkle"),
}

IMPROVEMENTS = {
    "Azerite Drill": ("crystals", "gear"), "Tidal Drill": ("crystals", "wave"), "Great Workshop": ("gears", "hammer"),
    "Academy": ("book", "orb"), "Customs house": ("coins", "anchor"), "Citadel": "castle", "Landmark": "star",
    "Holy site": "hand_light", "Trading post": "scales", "Plantation": "fruit", "Lumber mill": "saw",
    "Fort": "shield", "Railroad": "wheel",
}

BUILDINGS = {   # wonders and buildings with real-world pictures (black icons)
    "Palace": "crown", "Temple of Elune": "moon", "Circle of Binding": "rune", "The Violet Citadel": ("spire", "orb"),
    "Halls of Origination": ("ziggurat", "rune"), "Uther's Tomb": ("coffin", "hand_light"),
    "Valley of Heroes": ("sword", "crown"), "Westfall Lighthouse": "tower", "Grand Coliseum": "swords",
    "Vale of Eternal Blossoms": ("pagoda", "leaf"), "Mogu'shan Vaults": ("golem", "key"), "Grand Library": "book",
    "Sanctum of the Oracles": ("orb", "eye"), "Hall of Legends": ("lute", "book"), "Caverns of Time": "hourglass",
    "The Greymane Wall": ("castle", "wolf"), "Hall of Champions": ("banner", "sword"),
    "Admiralty of Boralus": ("anchor", "crown"), "Cathedral of Light": ("spire", "hand_light"),
    "Shrine of Seven Stars": ("pagoda", "star"), "High Temple": "temple", "Zul'Gurub": ("ziggurat", "mask"),
    "Royal Vault": ("key", "coins"), "Thunder Totem": "totem", "College of Magi": ("book", "orb"),
    "Temple of the White Tiger": ("pagoda", "paw"), "Sunfury Spire": ("spire", "sun"),
    "Great Foundry": ("anvil", "flame"), "Northshire Abbey": ("temple", "hand_light"), "Karazhan": ("tower", "eye"),
    "Mogu'shan Palace": ("pagoda", "crown"), "Tower of Azora": ("tower", "sparkle"), "Grim Batol": ("mountain", "dragon"),
    "Royal Gallery": ("crown", "lute"), "Sunwell Plateau": "sun", "Ulduar": ("golem", "crown"),
    "Icecrown Citadel": ("spire", "skull"), "Hall of Explorers": ("shovel", "book"),
    "Undermine Exchange": ("coins", "gear"), "Gates of Ahn'Qiraj": ("portal", "tentacle_eye"),
    "Wyrmrest Temple": ("tower", "dragon"), "Spymaster's Guild": ("eye", "key"), "Lion's Rest": ("sword", "star"),
    "Shadowfang Keep": ("castle", "wolf"), "Seat of the Naaru": "naaru", "Mana Bomb Project": ("orb", "bomb"),
    "Grommash Hold": ("axe", "banner"), "The Nighthold": ("moon", "orb"), "Titan Ascension Project": ("rocket", "rune"),
    "Great Arcane Ward": ("shield", "orb"), "Mechagon Spire": ("tower", "gear"), "Celestial Planetarium": ("world", "star"),
    "Grand Council of Azeroth": "world", "Well of Eternity": ("orb", "moon"),
    # ordinary buildings with real-world or modern pictures
    "Monument": "rune", "Shrine": "totem", "Stone Works": ("pick", "castle"), "Temple": "temple", "Market": "scales",
    "Mint": "coin", "Aqueduct": "wave", "Garden": "leaf", "Bank": ("key", "coins"), "Museum": ("skull", "book"),
    "Amphitheater": "lute", "Arsenal": ("swords", "shield"), "Foundry": ("anvil", "gear"), "Port": ("anchor", "coins"),
    "Training Grounds": ("swords", "banner"), "House of Healing": "bandage", "Auction House": ("scales", "coins"),
    "Tidal Works": ("wave", "gear"), "Guard Tower": "tower", "Grand Arena": ("swords", "crown"),
    "Arcane Beacon": ("crystal", "eye"), "Fortress": ("castle", "banner"), "Arcane Laboratory": ("flask", "orb"),
    "Alchemy Lab": "flask", "Sun Crystal Array": ("crystal", "sun"), "Salvage Yard": ("gears", "wheel"),
    "Mana Reactor": ("orb", "bolt"), "Burrow": ("mountain", "gear"), "Skyship Foundry": ("zeppelin", "anvil"),
    "City Watch": ("lantern", "shield"), "Magistrate's Hall": ("scales", "scroll"), "Arena": "swords",
    "Bardic Hall": "lute", "Beastiary": "paw", "Mage Tower": ("tower", "orb"), "Arcane Sanctum": ("book", "orb"),
    "Cathedral": ("spire", "hand_light"), "Monastery": ("temple", "book"), "Sanctuary": ("dome", "hand_light"),
    "Pagoda": "pagoda", "Windmill": ("wheel", "wheat"), "Water Mill": ("wheel", "wave"), "Observatory": ("scope", "star"),
    "Keep": "castle", "Walls": ("castle", "shield"),
}

POLICIES = {
    "Aristocracy": "crown", "Legalism": "scroll", "Oligarchy": ("crown", "coins"), "Landed Elite": ("wheat", "crown"),
    "Monarchy": "crown", "Republic": ("scales", "banner"), "Citizenship": ("hut", "shield"),
    "Collective Rule": ("hut", "hammer"), "Representation": ("scroll", "quill"), "Meritocracy": ("star", "book"),
    "Warrior Code": "axe", "Discipline": "shield", "Military Tradition": "swords", "Military Caste": ("helm", "crown"),
    "Professional Army": ("helm", "sword"), "Organized Religion": "temple", "Divine Mandate": ("hand_light", "crown"),
    "Theocracy": ("spire", "crown"), "Spiritual Renewal": "sun", "Free Religion": ("moon", "sun"),
    "Philantropy": ("coins", "heart"), "Aesthetics": "lute", "Scholasticism": ("book", "quill"),
    "Cultural Diplomacy": ("scroll", "lute"), "Educated Elite": ("book", "star"), "Naval Tradition": "anchor",
    "Merchant Guilds": ("scales", "hammer"), "Merchant Navy": ("ship", "coins"), "Mercantilism": ("coins", "scales"),
    "Protectionism": ("shield", "coins"), "Secular Scholarship": "book", "Humanism": ("heart", "book"),
    "Free Thought": ("orb", "quill"), "Sovereignty": ("crown", "orb"), "Arcane Revolution": ("orb", "sparkle"),
    "Charter of Kings": ("scroll", "crown"), "Common Voice": "horn", "Civic Guilds": ("hammer", "scales"),
    "Open Council": ("scroll", "star"), "House of Nobles": ("castle", "crown"), "Rallying Cry": "horn",
    "Militarism": ("banner", "sword"), "Iron Will": "fist", "Inquisition": ("flame", "hand_light"),
    "Total War": ("swords", "skull"), "United Front": ("shield", "swords"), "Grand Stewardship": ("key", "wheat"),
    "Ancestral Pride": ("totem", "banner"), "Common Granaries": "wheat", "Collective Labor": ("hammer", "pick"),
}

BRANCHES = {     # policy branch icons (new names)
    "Old Kingdoms": "crown", "Frontier": ("banner", "hut"), "Blood and Thunder": ("axe", "bolt"),
    "Devotion": "hand_light", "Diplomacy": ("scroll", "scales"), "Trade Princes": ("coins", "anchor"),
    "Arcane Inquiry": "orb", "Free Peoples": ("hut", "banner"), "Dominion": "fist", "Unity": ("shield", "swords"),
}

PROMOTIONS = {   # base names (icons are keyed by the base name, levels share them)
    "Morale": "banner", "Sortie": ("wing", "bolt"), "Wolfpack": ("fish", "skull"), "Aerial Combat": ("gryphon", "sword"),
    "Interception": ("wing", "target"), "Bombardment": ("bomb", "target"), "Aerial Targeting": ("wing", "target"),
    "Aerie Deck": ("gryphon", "anchor"), "Iron Plating": ("shield", "anvil"), "Armor Piercing": ("spear", "shield"),
    "Long Flight": ("wing", "compass"), "Field Repairs": ("hammer", "gear"), "Extended Range": "target",
    "Coastal Raider": ("ship", "flame"), "Boarding Party": ("anchor", "sword"), "Targeting": "target",
    "Supply": ("wheat", "anchor"), "Volley": ("bow", "star"),
}


def write_all(images_dir):
    groups = (("TechIcons", TECHS, (255, 255, 255)), ("UnitIcons", UNITS, (255, 255, 255)),
              ("ResourceIcons", RESOURCES, (255, 255, 255)), ("ImprovementIcons", IMPROVEMENTS, (255, 255, 255)),
              ("BuildingIcons", BUILDINGS, (0, 0, 0)), ("PolicyIcons", POLICIES, (255, 255, 255)),
              ("UnitPromotionIcons", PROMOTIONS, (255, 255, 255)), ("PolicyBranchIcons", BRANCHES, (255, 255, 255)))
    import wc_renames as R
    n = 0
    for folder, table, color in groups:
        for name, recipe in table.items():
            name = {"Secular Scholarship": "Apprentice Mages"}.get(name, R.ALL.get(name, name))
            main, badge = (recipe, None) if isinstance(recipe, str) else recipe
            save(compose(main, badge), os.path.join(images_dir, folder, name + ".png"), color)
            n += 1
    return n
