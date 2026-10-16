"""The Burning Legion: demon units that only appear through Legion incursion events.

Original pixel art drawn in code (mounts.Paint), in the AbsoluteUnits footprint
(95 x 81, figure on the right, feet near y = 59):
  - Felguard: a hulking red-skinned demon with swept horns, spiked pauldrons, a
    fel-green glow in its eyes and a huge notched axe.
  - Infernal: a giant of dark meteor-rock wreathed in green fel-fire.
Both stay red and green whatever their owner, with a small banner patch in the owner's
colours so they still read as "barbarian" on the map.
"""
from late_units import paint_layers, FEL
from mounts import shade

W, H = 95, 81
SKIN, SKIN_D = (170, 50, 40), (115, 30, 28)
ARMOR, ARMOR_D = (70, 64, 70), (45, 40, 46)
BONE = (225, 215, 190)


def felguard():
    def f(p):
        p.ell(73, 59, 13, 2.2, (0, 0, 0), "shadow")
        for x, b in ((67, -2), (79, 2)):                       # digitigrade legs, hooves
            p.line(x, 42, x + b, 50, 4, SKIN_D, "thigh%d" % x)
            p.line(x + b, 50, x, 57, 3, SKIN_D, "shin%d" % x)
            p.line(x - 2, 58, x + 2, 58, 2, (30, 26, 26), "hoof%d" % x)
        p.poly([(64, 42), (82, 42), (80, 47), (66, 47)], ARMOR, "kilt")
        p.poly([(68, 43), (78, 43), (77, 49), (69, 49)], (220, 220, 220), "tabard", layer=2)
        p.ell(73, 33, 10, 10, SKIN, "torso")                     # massive chest
        p.line(66, 30, 80, 30, 1, SKIN_D, "pec")
        for x, d in ((62, -1), (84, 1)):                        # spiked pauldrons
            p.ell(x, 25, 5, 4, ARMOR, "pauld%d" % x)
            for k in range(3):
                p.line(x - 3 + k * 3, 22, x - 3 + k * 3 + d, 18, 1, BONE, "spike%d%d" % (x, k))
        p.line(62, 27, 58, 39, 4, SKIN, "armL")
        p.line(84, 27, 88, 37, 4, SKIN, "armR")
        p.ell(73, 19, 4.5, 4.5, SKIN, "head")
        p.poly([(70, 21), (78, 21), (77, 24), (71, 24)], (60, 30, 25), "jaw")
        for d in (-1, 1):                                       # swept-back horns
            p.line(73 + d * 3, 16, 73 + d * 6, 12, 2, BONE, "horn%d" % d)
            p.line(73 + d * 6, 12, 73 + d * 5, 8, 1, shade(BONE, 0.85), "hornt%d" % d)
        p.line(90, 14, 86, 52, 2, (90, 60, 40), "haft")          # the great axe
        p.poly([(88, 12), (95, 8), (95, 26), (89, 22)], (175, 180, 190), "blade")
        p.poly([(93, 13), (95, 13), (95, 20), (93, 19)], (120, 125, 135), "notch")
        p.ell(88, 37, 2.5, 2.5, SKIN_D, "fist")

    def lit(p):
        p.dot(71, 18, FEL, "eye"); p.dot(75, 18, FEL, "eye")
        p.dot(73, 33, FEL, "rune"); p.dot(72, 34, FEL, "rune"); p.dot(74, 34, FEL, "rune")
    return paint_layers((W, H), f, ((lit, FEL),))


def infernal():
    ROCK, ROCK_D = (60, 58, 62), (38, 36, 40)

    def f(p):
        p.ell(70, 59, 18, 2.6, (0, 0, 0), "shadow")
        for x in (61, 79):                                      # stumpy boulder legs
            p.ell(x, 52, 5, 6, ROCK_D, "leg%d" % x)
        p.ell(70, 37, 15, 13, ROCK, "body")                     # meteor-rock torso
        for (x, y) in ((63, 31), (76, 41), (68, 45), (78, 30)):
            p.ell(x, y, 3, 2, ROCK_D, "crack%d%d" % (x, y))
        p.poly([(62, 40), (78, 40), (76, 46), (64, 46)], (220, 220, 220), "brand", layer=2)
        for x, d in ((54, -1), (86, 1)):                        # long arms with rock fists
            p.line(x + 2 * -d, 30, x, 46, 5, ROCK_D, "arm%d" % x)
            p.ell(x, 49, 5, 4.5, ROCK, "fist%d" % x)
        p.ell(70, 21, 6, 5, ROCK_D, "head")
        for d in (-1, 1):
            p.line(70 + d * 4, 18, 70 + d * 7, 13, 2, ROCK, "spike%d" % d)

    def lit(p):
        for (x, y, r) in ((70, 10, 3.5), (63, 13, 2.5), (77, 12, 2.5), (60, 26, 2), (81, 25, 2)):
            p.ell(x, y, r, r * 1.3, FEL, "flame%d%d" % (x, y))  # fel-fire wreathing the head
        p.dot(68, 21, (230, 255, 160), "eye"); p.dot(72, 21, (230, 255, 160), "eye")
        for (x, y) in ((63, 31), (76, 41), (68, 45), (78, 30)):
            p.dot(x, y, FEL, "seam%d%d" % (x, y))
    return paint_layers((W, H), f, ((lit, FEL),))


SPRITES = {"Felguard": felguard, "Infernal": infernal}

LORE = {
    "Felguard": "The elite shock troops of the Burning Legion: towering demons of the Eredar "
                "worlds, bound to Sargeras and armed with brutal axes. They appear only when "
                "the Legion tears a rift into Azeroth.",
    "Infernal": "A meteor of fel-scorched rock hurled from the Twisting Nether. Where it lands it "
                "rises as a hulking golem of stone and green fire that smashes everything nearby.",
}

# (new unit, Unciv base unit to copy stats from, extra stats)
UNITS = [
    ("Felguard", "Vanguard", {"strength": 24}),
    ("Infernal", "Shock Trooper", {"strength": 75}),
]
