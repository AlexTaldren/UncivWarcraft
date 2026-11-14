"""Resource and tile-improvement icons (Nov 2026): coloured pixel art with a dark outline.

The game draws these untinted on a coloured disc, so unlike the tech, building, policy and promotion
icons they carry their own colours: two tones per icon over an ink outline. All drawings are original.
"""
import math
import os

from PIL import Image, ImageChops, ImageFilter

import building_icons as BI
import misc_icons as MI
import tech_icons as TI
from tech_icons import B, M, C, N, Ic

T = BI.from_tech
INK = (34, 26, 24)


# ---------------------------------------------------------------- shapes
def beast(i):
    i.E(14, 17, 12, 8)
    i.P([(22, 12), (30, 14), (31, 20), (25, 24), (20, 20)])
    i.P([(27, 12), (31, 6), (30, 13)], M)
    i.R(4, 22, 8, 30).R(18, 22, 22, 30)
    i.R(9, 23, 12, 29, M).R(13, 23, 16, 29, M)
    i.E(27, 16, 1, t=C)
    return i.L([(4, 12), (10, 9), (18, 9)], 2, M)


def sheep(i):
    for x, y in ((8, 13), (14, 10), (20, 11), (24, 15), (20, 20), (13, 20), (8, 18)):
        i.E(x, y, 5)
    i.E(27, 12, 4, 3, t=M)
    i.P([(23, 9), (25, 7), (26, 10)], M)
    i.R(9, 23, 11, 30, M).R(19, 23, 21, 30, M)
    return i.R(28, 11, 28, 12, C)


def strider(i):
    i.E(13, 15, 9, 7)
    i.P([(18, 12), (22, 3), (25, 3), (23, 14)])
    i.E(24, 4, 3)
    i.P([(26, 3), (31, 5), (26, 6)], M)
    i.P([(4, 12), (0, 7), (1, 16), (6, 18)], M)
    i.L([(11, 21), (9, 30)], 2, M).L([(16, 21), (18, 30)], 2, M)
    i.L([(6, 30), (11, 30)], 1, M).L([(16, 30), (21, 30)], 1, M)
    return i.R(24, 3, 24, 3, C)


def banana(i):
    i.d.pieslice([0, -8, 30, 28], 20, 150, fill=B)
    i.d.pieslice([2, -12, 28, 20], 15, 165, fill=C)
    i.d.pieslice([2, -2, 32, 32], 30, 140, fill=M)
    i.d.pieslice([4, -6, 30, 25], 25, 155, fill=C)
    return i.R(27, 12, 29, 15).R(2, 13, 4, 16, M)


def fish(i):
    i.E(14, 16, 12, 8)
    i.P([(22, 16), (31, 7), (31, 25)])
    i.P([(10, 9), (18, 3), (19, 10)], M).P([(11, 23), (16, 28), (18, 23)], M)
    i.E(7, 14, 1, t=C)
    return i.L([(13, 12), (11, 16), (13, 20)], 1, M)


def ore(i):
    i.P([(2, 28), (4, 15), (11, 7), (20, 5), (28, 13), (30, 28)])
    i.P([(20, 5), (28, 13), (30, 28), (18, 28), (21, 16)], M)
    for x, y in ((8, 16), (13, 22), (15, 11), (24, 20)):
        i.P([(x, y - 2), (x + 2, y), (x, y + 2), (x - 2, y)], C)
    return i


def nuggets(i):
    for x, y, r in ((10, 22, 7), (22, 21, 8), (16, 10, 7)):
        i.P([(x - r, y + r - 2), (x - r + 1, y - r + 3), (x - 1, y - r), (x + r - 1, y - r + 2), (x + r, y + r - 2), (x, y + r)])
        i.P([(x + r - 1, y - r + 2), (x + r, y + r - 2), (x, y + r), (x + 1, y)], M)
    return i


def ingot(i):
    i.P([(7, 9), (25, 9), (30, 23), (2, 23)])
    i.P([(7, 9), (25, 9), (23, 5), (9, 5)], M)
    return i.R(2, 23, 30, 26, M)


def gem(i):
    i.P([(8, 4), (24, 4), (31, 12), (16, 30), (1, 12)])
    i.P([(16, 12), (31, 12), (16, 30)], M)
    i.P([(8, 4), (16, 12), (1, 12)], M)
    return i.L([(1, 12), (31, 12)], 1, C).L([(11, 6), (14, 9)], 1, C)


def ink(i):
    i.P([(5, 14), (21, 14), (24, 29), (2, 29)])
    i.R(8, 9, 18, 14, M)
    i.R(6, 20, 20, 23, M)
    i.P([(30, 0), (31, 4), (18, 14), (15, 14)])
    return i.P([(30, 0), (26, 1), (22, 7), (25, 7)], M)


def herb(i):
    i.L([(16, 31), (16, 12)], 2, M)
    i.P([(16, 24), (7, 22), (4, 15), (12, 17)], M).P([(16, 20), (25, 18), (28, 11), (20, 13)], M)
    for x, y in ((16, 4), (11, 8), (21, 8), (16, 11)):
        i.E(x, y, 4)
    return i.E(16, 8, 2, t=C)


def tusk(i):
    i.d.pieslice([-14, -6, 28, 36], 300, 60, fill=B)
    i.d.pieslice([-20, -6, 20, 36], 290, 70, fill=C)
    i.P([(10, 0), (16, 2), (14, 6), (8, 5)], M)
    i.P([(9, 26), (15, 26), (13, 31), (8, 31)], M)
    return i


def cloth(i):
    i.R(4, 6, 27, 25)
    i.E(4, 15, 3, 9, t=M).E(27, 15, 3, 9)
    i.E(27, 15, 1, 5, t=C)
    for x in (10, 16, 22):
        i.L([(x, 7), (x, 24)], 1, M)
    return i.P([(4, 25), (12, 25), (10, 31), (2, 30)], M)


def pepper(i):
    i.P([(9, 8), (16, 6), (22, 10), (24, 18), (20, 27), (14, 31), (16, 24), (13, 16), (8, 12)])
    i.P([(16, 6), (22, 10), (24, 18), (20, 27), (19, 18), (17, 11)], M)
    i.P([(10, 8), (16, 6), (15, 3), (19, 0), (14, 0), (11, 4)], M)
    return i


def mug(i):
    i.R(5, 10, 21, 30)
    i.d.arc([17, 13, 31, 27], 270, 90, fill=B, width=3)
    for x, y in ((7, 8), (12, 6), (18, 8), (22, 10)):
        i.E(x, y, 4, t=M)
    return i.R(9, 15, 10, 27, C).R(15, 15, 16, 27, C)


def honey(i):
    def hexa(cx, cy, t):
        i.P([(cx - 5, cy), (cx - 3, cy - 5), (cx + 3, cy - 5), (cx + 5, cy), (cx + 3, cy + 5), (cx - 3, cy + 5)], t)
    for cx, cy, t in ((9, 8, B), (20, 8, M), (4, 18, M), (15, 18, B), (26, 18, B), (9, 27, B), (20, 27, M)):
        hexa(cx, cy, t)
        i.E(cx, cy, 1, t=C)
    return i


def column(i):
    i.R(4, 2, 27, 6).R(6, 6, 25, 8, M)
    i.R(9, 8, 22, 25)
    for x in (12, 16, 20):
        i.L([(x, 9), (x, 24)], 1, M)
    return i.R(6, 25, 25, 27, M).R(4, 27, 27, 30)


def tail(i):
    i.P([(13, 31), (13, 18), (2, 4), (10, 6), (16, 13), (22, 6), (30, 4), (19, 18), (19, 31)])
    i.P([(16, 13), (22, 6), (30, 4), (19, 18), (19, 31), (16, 31)], M)
    return i.L([(0, 30), (5, 28), (10, 30)], 2, M).L([(22, 30), (27, 28), (31, 30)], 2, M)


def pearl(i):
    i.E(13, 15, 11)
    i.E(9, 11, 2, t=C)
    i.d.arc([4, 6, 24, 26], 20, 100, fill=M, width=2)
    i.E(25, 25, 5, t=M)
    return i.E(23, 23, 1, t=C)


def ringjewel(i):
    i.ring(16, 20, 10, 3)
    i.P([(11, 9), (21, 9), (24, 4), (16, 0), (8, 4)], M)
    i.L([(12, 4), (20, 4)], 1, C)
    return i


def fruit(i):
    i.E(16, 19, 11, 11)
    i.d.arc([7, 10, 25, 28], 10, 110, fill=C, width=1)
    i.R(15, 4, 16, 9)
    i.P([(17, 6), (24, 1), (27, 5), (21, 9)], M)
    return i.E(11, 14, 2, t=C)


def crab(i):
    i.E(16, 19, 10, 7)
    i.ring(5, 8, 4, 2).ring(27, 8, 4, 2)
    i.P([(3, 4), (7, 4), (5, 8)], C).P([(25, 4), (29, 4), (27, 8)], C)
    i.L([(7, 16), (5, 11)], 2).L([(25, 16), (27, 11)], 2)
    for y in (20, 24):
        i.L([(7, y), (1, y + 4)], 2, M).L([(25, y), (31, y + 4)], 2, M)
    return i.R(12, 13, 13, 16).R(19, 13, 20, 16).R(12, 12, 12, 12, C).R(19, 12, 19, 12, C)


def pile(i):
    i.P([(1, 29), (9, 14), (16, 6), (23, 14), (31, 29)])
    i.P([(16, 6), (23, 14), (31, 29), (19, 29), (20, 18)], M)
    return i.R(11, 20, 12, 21, C).R(15, 14, 16, 15, C).R(8, 25, 9, 26, C)


def mushroom(i):
    i.d.pieslice([1, 2, 30, 34], 180, 360, fill=B)
    i.R(12, 18, 19, 30, M)
    i.E(9, 11, 2, t=M).E(17, 7, 2, t=M).E(24, 13, 2, t=M)
    return i.R(1, 18, 30, 19, C).R(9, 29, 22, 30, M)


def drop(i):
    i.E(16, 20, 10, 10)
    i.P([(16, 1), (26, 19), (6, 19)])
    i.d.pieslice([6, 10, 26, 30], 320, 110, fill=M)
    return i.E(12, 18, 2, t=C)


def fence(i):
    for x in (3, 13, 23):
        i.R(x, 8, x + 4, 29)
        i.P([(x, 8), (x + 2, 4), (x + 4, 8)])
    return i.R(0, 13, 31, 16, M).R(0, 22, 31, 25, M)


def road(i):
    i.P([(11, 0), (20, 0), (30, 31), (1, 31)])
    for y0, y1 in ((2, 6), (10, 15), (20, 27)):
        i.R(15, y0, 16, y1, C)
    return i.P([(20, 0), (30, 31), (24, 31), (18, 0)], M)


def bigx(i):
    return i.L([(4, 4), (27, 27)], 6).L([(27, 4), (4, 27)], 6)


def drill(i):
    i.L([(6, 30), (15, 4)], 2, M).L([(25, 30), (16, 4)], 2, M)
    i.R(8, 19, 23, 20, M)
    i.R(12, 2, 19, 6)
    i.R(14, 6, 17, 22)
    i.P([(12, 22), (19, 22), (16, 31), (15, 31)])
    return i.L([(12, 24), (19, 26)], 1, C)


def ruin(i):
    i.R(3, 12, 8, 29).R(13, 5, 18, 29).R(23, 16, 28, 29)
    i.P([(3, 12), (8, 9), (8, 12)]).P([(13, 5), (15, 2), (18, 5)]).P([(23, 16), (26, 13), (28, 16)])
    i.R(1, 29, 30, 30, M)
    return i.R(9, 26, 12, 28, M).R(19, 25, 22, 28, M)


def flame(i):
    return i.flame(16, 30, 28)


def hammer(i):
    return i.hammer(16, 3, 29, 9)


# name -> (shape, light, dark)
BROWN, TAN = (150, 100, 60), (96, 62, 40)
RESOURCES = {
    "Kodo": (beast, (176, 132, 92), (112, 78, 54)), "Sheep": (sheep, (244, 240, 228), (150, 140, 130)),
    "Plainstriders": (strider, (232, 170, 150), (160, 100, 90)), "Tel'Abim Bananas": (banana, (250, 214, 70), (196, 150, 40)),
    "Wheat": (T("Farming"), (240, 200, 80), (176, 130, 40)), "Stone": (BI.blocks, (190, 190, 186), (120, 120, 122)),
    "Fish": (fish, (110, 180, 230), (50, 110, 170)), "Horses": (T("Riding"), (170, 112, 66), (100, 62, 38)),
    "Iron": (ore, (176, 182, 190), (104, 110, 122)), "Thorium": (ingot, (150, 210, 170), (70, 130, 100)),
    "Azerite": (T("Azerite Refinement"), (250, 200, 80), (60, 130, 200)), "Elementium": (ore, (190, 130, 220), (110, 60, 150)),
    "Arcane Crystals": (BI.crystal, (200, 150, 255), (120, 70, 190)), "Rugged Leather": (T("Skinning"), (170, 116, 70), (104, 66, 40)),
    "Peacebloom": (T("Nature's Blessing"), (250, 248, 236), (240, 196, 70)), "Moonglow Ink": (ink, (120, 170, 250), (60, 80, 170)),
    "Star Rubies": (gem, (240, 80, 90), (160, 30, 50)), "Gold Ore": (nuggets, (252, 210, 70), (190, 140, 30)),
    "Truesilver": (ingot, (214, 232, 244), (120, 150, 180)), "Mageroyal": (herb, (220, 120, 230), (70, 140, 70)),
    "Mammoth Ivory": (tusk, (246, 238, 214), (190, 170, 130)), "Mageweave": (cloth, (170, 130, 230), (100, 70, 160)),
    "Hot Spices": (pepper, (236, 70, 50), (80, 140, 60)), "Ale": (mug, (232, 170, 60), (250, 244, 226)),
    "Honeycomb": (honey, (250, 196, 60), (200, 130, 30)), "Marble": (column, (246, 244, 238), (176, 172, 170)),
    "Leviathans": (tail, (90, 150, 200), (50, 90, 150)), "Black Pearls": (pearl, (90, 90, 110), (200, 180, 190)),
    "Jeweled Trinkets": (ringjewel, (250, 206, 80), (90, 200, 220)), "Jade Carvings": (BI.serpent, (110, 210, 150), (50, 140, 90)),
    "Sunfruit": (fruit, (250, 160, 50), (90, 160, 60)), "Copper Ore": (ore, (226, 140, 80), (150, 80, 44)),
    "Crawlers": (crab, (232, 90, 70), (160, 50, 40)), "Deeprock Salt": (pile, (246, 246, 250), (176, 186, 204)),
    "Glowcap": (mushroom, (90, 230, 200), (220, 240, 210)), "Mana": (drop, (100, 170, 255), (50, 100, 210)),
    "Raid Trophy": (BI.cup, (250, 206, 80), (190, 140, 30)),
}

GREEN, WOOD, STONE, GOLD, RED = ((120, 200, 90), (60, 130, 50)), ((190, 140, 80), (120, 80, 44)), ((200, 200, 196), (124, 124, 128)), ((250, 206, 80), (190, 140, 30)), ((230, 80, 60), (150, 40, 34))
IMPROVEMENTS = {
    "Farm": (T("Farming"), (240, 200, 80), (176, 130, 40)), "Lumber mill": (BI.saw, (210, 210, 214), (150, 100, 56)),
    "Mine": (T("Mining"), (200, 204, 212), (150, 100, 56)), "Trading post": (BI.stall, (240, 200, 90), (190, 70, 60)),
    "Camp": (BI.tent,) + WOOD, "Azerite Drill": (drill, (250, 200, 80), (110, 120, 136)), "Tidal Drill": (BI.wave, (120, 190, 240), (60, 120, 190), "gear"),
    "Pasture": (fence,) + WOOD, "Plantation": (fruit, (250, 160, 50), (90, 160, 60)), "Quarry": (BI.blocks,) + STONE,
    "Fishing Boats": (lambda i: i.ship(), (240, 236, 220), (150, 100, 56)), "Fort": (BI.castle,) + STONE, "Road": (road, (190, 170, 130), (130, 110, 84)),
    "Railroad": (T("Tramways"), (190, 194, 204), (110, 114, 126)),
    "Remove Forest": (BI.tree,) + GREEN + ("x",), "Remove Jungle": (T("Herbalism"),) + GREEN + ("x",),
    "Remove Blighted Land": (BI.skull, (200, 190, 150), (130, 120, 90), "x"), "Remove Marsh": (BI.wave, (120, 170, 150), (70, 110, 100), "x"),
    "Remove Road": (road, (190, 170, 130), (130, 110, 84), "x"), "Remove Railroad": (T("Tramways"), (190, 194, 204), (110, 114, 126), "x"),
    "Cancel improvement order": (bigx,) + RED, "Repair": (hammer, (200, 204, 212), (150, 100, 56)),
    "Arcane Academy": (BI.spire, (190, 150, 250), (110, 70, 180)), "Hall of Heroes": (BI.armory,) + GOLD,
    "Great Workshop": (BI.gears, (220, 180, 90), (140, 110, 60)), "Trade Company": (BI.coins,) + GOLD,
    "Sacred Grounds": (BI.brazier, (250, 190, 70), (200, 90, 40)), "Bastion": (BI.fortress,) + STONE,
    "Ancient ruins": (BI.stones,) + STONE, "City ruins": (ruin,) + STONE, "City center": (BI.hall, (240, 226, 190), (170, 80, 60)),
    "Barbarian encampment": (BI.burrow,) + RED, "Remove Fel-Scorched Land": (flame, (150, 240, 80), (60, 150, 40), "x"),
    "Remove Plagued Land": (BI.cauldron, (160, 200, 90), (90, 120, 50), "x"), "Spread Blight": (BI.skull, (170, 220, 120), (90, 140, 60), "drop"),
    "Deep Mine": (T("Mining"), (200, 204, 212), (150, 100, 56), "gem"),
}


def b_x(i, x, y):
    i.L([(x - 4, y - 4), (x + 4, y + 4)], 3).L([(x + 4, y - 4), (x - 4, y + 4)], 3)


def b_drop(i, x, y):
    i.E(x, y + 2, 4).P([(x, y - 6), (x + 4, y + 1), (x - 4, y + 1)])


MARK_RGB = {"x": (232, 60, 50), "gear": (220, 220, 226), "gem": (120, 220, 250), "drop": (150, 230, 90)}
MARK_FN = {"x": b_x, "drop": b_drop, "gear": BI.MARKS["gear"], "gem": BI.MARKS["gem"]}


def _tint(mask, light, dark):
    """L-mode drawing -> RGBA: bright tone in the light colour, mid tone in the dark colour."""
    px = mask.load()
    out = Image.new("RGBA", mask.size, (0, 0, 0, 0))
    o = out.load()
    for y in range(mask.size[1]):
        for x in range(mask.size[0]):
            v = px[x, y]
            if v >= 250:
                o[x, y] = light + (255,)
            elif v > 0:
                o[x, y] = dark + (255,)
    return out


def _outline(img):
    a = img.split()[3]
    grown = a.filter(ImageFilter.MaxFilter(3))
    ink = Image.new("RGBA", img.size, INK + (255,))
    ink.putalpha(grown)
    ink.alpha_composite(img)
    return ink


def render(spec):
    shape, light, dark = spec[:3]
    mark = spec[3] if len(spec) > 3 else None
    S = 34                                           # one spare pixel all round for the outline
    main = Ic()
    real = main.d
    main.d = BI._Scaled(real, 0.78 if mark else 0.97)
    shape(main)
    main.d = real
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    layer.alpha_composite(_tint(main.im, light, dark), (1, 1))
    layer = _outline(layer)
    if mark:
        m = Ic()
        MARK_FN[mark](m, 25, 25)
        ml = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        rgb = MARK_RGB[mark]
        ml.alpha_composite(_tint(m.im, rgb, tuple(int(c * 0.6) for c in rgb)), (1, 1))
        layer.alpha_composite(_outline(ml))
    big = layer.resize((S * 3, S * 3), Image.NEAREST)
    out = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    out.alpha_composite(big.crop((1, 1, 101, 101)))
    return out


def write_all(root):
    n = 0
    for sub, table in (("ResourceIcons", RESOURCES), ("ImprovementIcons", IMPROVEMENTS)):
        for pack in sorted(os.listdir(root)):
            folder = os.path.join(root, pack, sub)
            if pack.startswith("Images") and os.path.isdir(folder):
                for name, spec in table.items():
                    render(spec).save(os.path.join(folder, name + ".png"))
                    n += 1
    return n
