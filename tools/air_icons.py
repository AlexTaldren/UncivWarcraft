"""Unit icons for the 15 flying units (Oct 2026 lore pass).

Unciv never draws flying units on the map (they appear only as a small aircraft badge
on their city or carrier), so their unit icon is the picture players see: in the unit
panel, production lists and the Civilopedia. Each one is a full silhouette in the
style of the rest of the icon set (flat white, Unciv tints it), facing right, drawn
from the unit's place in Warcraft lore:

  Gyrocopter          gnomish/dwarven rotorcraft: goggled pilot in an open pod, twin-blade rotor
  Bomber Zeppelin     gnomish ribbed airship with a bomb rack under the gondola
  Gryphon Rider       Wildhammer dwarf on a gryphon, storm hammer raised
  War Zeppelin        armoured war airship: plated envelope, cannon gondola, tail fins
  Mana Bomb           runic bomb casing around an exposed arcane crystal
  Arcane Missile      a volley of three streaking arcane bolts
  Arcane Annihilator  hovering arcane construct: crystal crown, rune ring, eye
  Sky Golem           goblin-built flying shredder: canopy, rotor, claws, rocket thrusters
  Void Bomber         crescent void craft with a staring eye and trailing tendrils
  Batrider (Trolls)   Darkspear rider on a giant bat, hurling a fire bomb
  Frost Wyrm (Scourge)  skeletal dragon: rib cage, torn wings, horned skull
  Wind Rider (Tauren) horned rider on a wyvern with a barbed tail, spear raised
  Dragonhawk Rider (Blood Elves)  long-eared rider on a crested dragonhawk with tail plumes
  Goblin Zeppelin     patched balloon, ramshackle gondola, smokestack and propeller
  Cloud Serpent Rider (Pandaren)  serpent dragon coiling through cloud, pandaren rider
All shapes are original; lore is used only for what each unit is.
"""
import math
from icons import Icon


def _bomb(i, x, y, r, v=255):
    i.circle(x, y, r, v)
    i.rect(x - r * 0.35, y - r - 3, x + r * 0.35, y - r + 1, v)


# ------------------------------------------------------------------ gnomish machines
def gyrocopter():
    i = Icon()
    i.ellipse(46, 62, 24, 16)                                  # cockpit pod
    i.poly([(64, 56), (92, 52), (94, 58), (66, 70)])           # tail boom
    i.poly([(88, 44), (96, 44), (96, 62), (90, 62)])           # tail fin
    i.circle(93, 53, 7); i.circle(93, 53, 4, 0); i.circle(93, 53, 1.5)   # tail rotor
    i.rect(44, 22, 49, 48)                                     # rotor mast
    i.poly([(4, 22), (46, 18), (46, 24), (6, 28)])             # rotor blades
    i.poly([(48, 18), (96, 14), (94, 20), (48, 24)])
    i.ellipse(46.5, 21, 6, 4)
    i.circle(40, 44, 9)                                        # pilot head
    i.ellipse(43, 42, 6, 3.4, 0); i.circle(42, 42, 2.5); i.circle(48, 42, 2.5)   # goggles
    i.ellipse(46, 62, 16, 7, 0); i.ellipse(46, 62, 12, 4)      # open cockpit rim
    i.line([(20, 66), (8, 68)], 4)                             # nose gun
    i.line([(32, 76), (28, 88)], 3); i.line([(58, 76), (62, 88)], 3)
    i.line([(18, 90), (72, 90)], 4)                            # skids
    return i


def bomber_zeppelin():
    i = Icon()
    i.ellipse(52, 30, 44, 22)
    for x in (24, 38, 52, 66, 80):                             # rigid frame ribs
        i.arc(x, 30, 22, 250, 290, 2.4, 0)
        i.line([(x, 10), (x, 50)], 2, 0, caps=False)
    i.poly([(6, 14), (18, 26), (18, 34), (6, 46)])             # tail fins
    i.line([(34, 50), (38, 62)], 3); i.line([(72, 50), (68, 62)], 3)
    i.poly([(28, 62), (80, 62), (76, 74), (32, 74)])           # gondola
    for x in (38, 50, 62): i.rect(x - 3, 65, x + 3, 69, 0)
    i.ellipse(24, 68, 2.5, 9)                                  # rear propeller
    i.line([(30, 74), (78, 74)], 2)
    for x, y in ((40, 86), (54, 90), (68, 86)):                # bomb rack
        _bomb(i, x, y, 6)
        i.poly([(x - 3, y + 5), (x + 3, y + 5), (x, y + 10)])
    return i


def war_zeppelin():
    i = Icon()
    i.ellipse(52, 30, 44, 24)
    for k, x in enumerate(range(16, 92, 12)):                  # armour plates
        i.line([(x, 8 + abs(52 - x) * 0.18), (x - 4, 52 - abs(52 - x) * 0.18)], 2, 0, caps=False)
    i.line([(10, 30), (94, 30)], 2, 0, caps=False)
    i.poly([(96, 30), (86, 22), (86, 38)])                     # ram nose
    i.poly([(4, 8), (20, 22), (20, 30), (2, 30)])              # upper fin
    i.poly([(4, 52), (20, 38), (20, 30), (2, 30)])             # lower fin
    for x in (32, 54, 76):                                     # spikes on top
        i.poly([(x - 4, 9), (x, 0), (x + 4, 9)])
    i.line([(36, 52), (36, 62)], 3); i.line([(70, 52), (70, 62)], 3)
    i.poly([(22, 62), (86, 62), (80, 80), (28, 80)])           # gondola
    i.rect(26, 66, 82, 67, 0)
    for x in (36, 52, 68):                                     # cannon ports
        i.rect(x - 4, 70, x + 4, 76, 0)
        i.line([(x, 73), (x + 8, 86)], 4)
    i.circle(90, 70, 4)
    return i


# ------------------------------------------------------------------ riders and beasts
def gryphon_rider():
    i = Icon()
    for k in range(6):                                         # great feathered wing fanning up behind
        a = math.radians(196 + k * 15)
        tip = (44 + 50 * math.cos(a), 52 + 50 * math.sin(a))
        a2 = math.radians(196 + k * 15 + 9)
        tip2 = (44 + 40 * math.cos(a2), 52 + 40 * math.sin(a2))
        i.poly([(44, 54), tip, tip2])
    i.ellipse(46, 64, 26, 13)                                  # lion body
    i.taper((22, 66), (12, 70), (8, 80), (12, 88), 5, 2)        # tail
    i.ellipse(13, 89, 4, 6)
    i.line([(30, 72), (24, 92)], 6); i.line([(40, 74), (38, 94)], 5)
    i.line([(62, 72), (70, 88), (78, 94)], 5)                  # foreleg with talons
    i.poly([(74, 92), (86, 92), (80, 98)])
    i.poly([(60, 60), (66, 42), (76, 32), (88, 32), (98, 38), (92, 44), (84, 46), (76, 66)])   # neck, eagle head
    i.poly([(92, 40), (98, 38), (96, 48)])                     # hooked beak
    i.circle(82, 37, 2.2, 0)
    i.poly([(70, 38), (62, 34), (72, 34)])                     # head feathers
    i.circle(54, 38, 8)                                        # dwarf rider: helmet, beard
    i.poly([(46, 36), (62, 36), (60, 30), (48, 30)], 0); i.poly([(46, 34), (62, 34), (54, 26)])
    i.poly([(46, 44), (62, 44), (66, 58), (44, 60)])
    i.poly([(49, 44), (59, 44), (54, 56)], 0); i.poly([(50, 45), (58, 45), (54, 54)])
    i.line([(60, 46), (74, 20)], 3.4)                           # storm hammer
    i.rect(66, 8, 84, 20)
    i.poly([(84, 4), (90, 8), (86, 10), (92, 14)])
    return i


def batrider():
    i = Icon()
    for side in (-1, 1):                                       # membrane wings with finger bones
        m = lambda x, y: (50 + side * (x - 50), y)
        i.poly([m(56, 46), m(72, 24), m(98, 22), m(92, 46), m(84, 40), m(78, 56), m(70, 48), m(62, 64), m(56, 60)])
        for f in ((92, 46), (78, 56), (62, 64)):
            i.line([m(72, 24), m(*f)], 1.4, 0, caps=False)
        i.line([m(56, 46), m(72, 24), m(98, 22)], 3)
    i.ellipse(50, 60, 13, 16)                                  # bat body and head
    i.poly([(40, 50), (38, 34), (47, 46)]); i.poly([(60, 50), (62, 34), (53, 46)])
    i.circle(45, 56, 2.2, 0); i.circle(55, 56, 2.2, 0)
    i.poly([(46, 66), (48, 72), (50, 66), (52, 72), (54, 66)], 0)
    i.line([(44, 74), (40, 90)], 3); i.line([(56, 74), (60, 90)], 3)
    i.circle(50, 36, 8)                                        # troll rider: mohawk, tusks
    i.poly([(45, 30), (50, 12), (55, 30)])
    i.line([(43, 40), (38, 46)], 2.2, 0); i.line([(57, 40), (62, 46)], 2.2, 0)
    i.circle(46, 34, 1.6, 0); i.circle(54, 34, 1.6, 0)
    i.line([(57, 38), (70, 20)], 4.5)                          # arm raised with a fire bomb
    i.circle(74, 14, 7)
    for k in range(3):
        i.poly([(70 + k * 5, 9), (73 + k * 5, -2 + k * 2), (76 + k * 5, 9)])
    return i


def frost_wyrm():
    i = Icon()
    # one great torn wing of bone
    i.line([(46, 52), (34, 22), (10, 4)], 4)
    for f in ((2, 26), (8, 42), (22, 50)):
        i.line([(34, 22), f], 2.2)
    i.poly([(34, 22), (10, 4), (2, 26), (10, 24), (8, 42), (16, 36), (22, 50), (30, 44), (40, 50)])
    i.poly([(14, 16), (20, 22), (12, 24)], 0); i.poly([(18, 34), (24, 38), (16, 40)], 0)
    # spine and rib cage
    i.ellipse(42, 64, 20, 12)
    i.ellipse(42, 64, 15, 8, 0)
    for x in range(30, 56, 6):
        i.line([(x, 56), (x - 3, 72)], 2.4)
    i.line([(22, 60), (64, 58)], 3)
    # neck of vertebrae up to a horned skull
    for k, (x, y) in enumerate(((64, 56), (68, 50), (71, 44), (73, 38))):
        i.circle(x, y, 5 - k * 0.4)
    i.poly([(68, 34), (82, 26), (98, 30), (88, 34), (98, 40), (82, 40), (72, 42)])
    i.poly([(88, 34), (96, 36), (88, 37)], 0)
    i.circle(80, 31, 2.4, 0)
    i.taper((74, 30), (68, 20), (62, 14), (56, 12), 5, 1)
    i.taper((78, 28), (78, 18), (76, 12), (72, 8), 4, 1)
    # tail and claws
    for k in range(7):
        i.circle(22 - k * 2.4, 66 + k * 3.6, 4 - k * 0.4)
    i.line([(34, 74), (30, 90)], 3.4); i.line([(50, 74), (56, 90)], 3.4)
    i.poly([(26, 90), (34, 90), (30, 96)]); i.poly([(52, 90), (60, 90), (58, 96)])
    # frost breath
    for k, (x, y, r) in enumerate(((92, 48, 5), (84, 54, 3.6), (96, 58, 3))):
        i.star(x, y, r, r * 0.35, 6)
    return i


def wind_rider():
    i = Icon()
    # wyvern: feline body, feathered wings, barbed tail
    i.ellipse(46, 64, 24, 11)
    i.taper((24, 62), (12, 56), (6, 46), (10, 36), 6, 2)       # tail curling up
    i.poly([(6, 38), (14, 30), (14, 40)])                      # stinger
    i.line([(32, 72), (28, 90)], 5); i.line([(58, 72), (62, 90)], 5)
    for k in range(5):                                         # feathered wing
        i.poly([(36, 58), (4 + k * 8, 10 + k * 5), (11 + k * 8, 14 + k * 6), (46, 60)])
    i.poly([(62, 58), (70, 44), (82, 40), (94, 46), (84, 50), (92, 54), (78, 56), (70, 66)])   # maned head
    i.poly([(72, 44), (68, 34), (78, 42)])
    i.circle(80, 45, 2, 0)
    # tauren rider: horns, spear raised
    i.ellipse(56, 40, 8, 8)
    i.taper((49, 36), (40, 32), (38, 24), (42, 18), 5, 1)
    i.taper((63, 36), (72, 32), (74, 24), (70, 18), 5, 1)
    i.circle(53, 40, 1.6, 0); i.circle(59, 40, 1.6, 0)
    i.poly([(46, 46), (66, 46), (66, 60), (44, 60)])
    i.line([(48, 50), (86, 14)], 3)                            # spear
    i.poly([(82, 14), (94, 4), (88, 18)])
    i.poly([(84, 18), (80, 24), (86, 20)])
    return i


def dragonhawk_rider():
    i = Icon()
    # long body and sweeping tail plumes
    i.ellipse(46, 60, 22, 9)
    for k in range(3):
        i.taper((26, 60), (14, 62 + k * 6), (8, 70 + k * 8), (2, 72 + k * 10), 5 - k, 1)
    # wings swept back, feathered
    for k in range(5):
        i.poly([(38, 56), (2 + k * 7, 8 + k * 5), (9 + k * 7, 12 + k * 6), (46, 58)])
    # long neck, hawk head with crest
    i.taper((60, 56), (70, 48), (74, 38), (80, 30), 9, 6)
    i.poly([(78, 26), (90, 26), (98, 32), (86, 34), (78, 36)])
    i.circle(84, 29, 1.8, 0)
    for k in range(3):                                         # crest plume
        i.taper((80, 26), (76, 18 - k * 2), (70, 14 - k * 3), (64, 12 - k * 4), 3, 1)
    i.line([(38, 66), (34, 80)], 3); i.line([(54, 66), (58, 80)], 3)
    # elf rider: long ears, flowing hair, glaive
    i.circle(50, 40, 6)
    i.poly([(45, 38), (36, 30), (46, 34)])
    i.taper((48, 36), (40, 40), (36, 46), (32, 50), 4, 1)
    i.poly([(44, 44), (56, 44), (58, 54), (42, 54)])
    i.line([(52, 46), (78, 70)], 2.6)
    i.poly([(74, 64), (88, 74), (78, 74)])
    return i


def cloud_serpent_rider():
    i = Icon()
    for x, y, r in ((14, 84, 10), (28, 88, 9), (44, 86, 10), (60, 88, 8), (74, 84, 10), (88, 88, 8)):
        i.circle(x, y, r)
    i.rect(4, 88, 98, 99, 0)
    i.taper((6, 76), (22, 48), (40, 90), (60, 64), 5, 15)      # serpent body coiling out of the cloud
    i.taper((60, 64), (70, 52), (72, 40), (72, 34), 15, 12)
    i.poly([(66, 32), (76, 22), (88, 24), (98, 30), (90, 34), (96, 38), (80, 42), (68, 40)])   # head
    i.circle(81, 28, 2.2, 0)
    i.taper((72, 24), (66, 14), (60, 10), (54, 8), 4.5, 1)     # horns
    i.taper((76, 22), (76, 12), (74, 8), (70, 4), 3.5, 1)
    i.taper((96, 36), (100, 44), (96, 52), (88, 56), 2, 1)     # whisker
    for k in range(3):                                         # mane behind the head
        i.poly([(66, 34 + k * 6), (56, 28 + k * 7), (62, 40 + k * 6)])
    i.poly([(36, 74), (24, 58), (34, 60), (30, 50), (46, 66)]) # small wing
    i.ellipse(52, 62, 9, 8, 0)                                 # pandaren rider sitting on the coil
    i.circle(52, 46, 8)
    i.circle(46, 39, 3.6); i.circle(58, 39, 3.6)
    i.circle(49, 46, 1.6, 0); i.circle(55, 46, 1.6, 0)
    i.ellipse(52, 60, 9, 8)
    i.line([(58, 56), (84, 66)], 2.8)                          # staff
    i.circle(86, 67, 3.6)
    return i


def sky_golem():
    i = Icon()
    i.rect(46, 4, 50, 18)                                      # rotor mast
    i.poly([(10, 6), (47, 2), (47, 8), (12, 12)]); i.poly([(49, 2), (90, 4), (88, 10), (49, 8)])
    i.poly([(26, 24), (70, 18), (78, 56), (22, 60)])           # armoured torso
    i.poly([(34, 26), (62, 22), (64, 40), (34, 42)], 0)        # canopy
    i.poly([(38, 30), (58, 27), (59, 37), (38, 38)])
    i.circle(48, 33, 4, 0)                                     # pilot
    i.rect(28, 48, 74, 51, 0)
    for side, x in ((-1, 22), (1, 76)):                        # arms with claws
        i.line([(x, 34), (x + side * 12, 50), (x + side * 10, 66)], 6)
        i.poly([(x + side * 4, 66), (x + side * 16, 66), (x + side * 18, 76), (x + side * 12, 70), (x + side * 10, 78), (x + side * 6, 70)])
    for x in (34, 62):                                         # rocket thrusters
        i.poly([(x - 7, 60), (x + 7, 60), (x + 5, 72), (x - 5, 72)])
        i.poly([(x - 4, 74), (x + 4, 74), (x, 96)])
        i.poly([(x - 2, 76), (x + 2, 76), (x, 88)], 0)
    return i


def goblin_zeppelin():
    i = Icon()
    i.ellipse(48, 30, 42, 24)
    i.rect(18, 12, 30, 24, 0); i.rect(20, 14, 28, 22)          # sewn patches
    i.poly([(56, 34), (70, 32), (72, 44), (58, 46)], 0); i.poly([(58, 36), (68, 34), (70, 42), (60, 44)])
    for x, y in ((19, 13), (29, 13), (19, 23), (29, 23)):
        i.circle(x, y, 1.2, 0)
    i.line([(40, 8), (36, 52)], 1.6, 0, caps=False)
    i.poly([(88, 20), (100, 14), (98, 30), (88, 34)])          # tail fin
    i.line([(30, 52), (28, 62)], 2.5); i.line([(66, 52), (70, 62)], 2.5)
    i.poly([(18, 62), (80, 62), (84, 80), (14, 78)])           # gondola, crooked
    for x in (24, 40, 56, 70): i.line([(x, 64), (x + 2, 78)], 1.6, 0, caps=False)
    i.rect(70, 46, 76, 62)                                     # smokestack
    for k, (x, y, r) in enumerate(((76, 40, 4), (82, 32, 5), (90, 24, 4))):
        i.circle(x, y, r)
    i.ellipse(8, 70, 3, 11)                                    # propeller
    i.line([(8, 70), (14, 70)], 3)
    i.rect(30, 82, 42, 92); i.rect(46, 82, 58, 92)             # dangling crates of bombs
    i.line([(36, 80), (36, 82)], 1.4); i.line([(52, 80), (52, 82)], 1.4)
    i.line([(30, 87), (42, 87)], 1.2, 0, caps=False)
    _bomb(i, 70, 90, 5)
    return i


# ------------------------------------------------------------------ arcane weapons
def mana_bomb():
    i = Icon()
    i.ellipse(50, 58, 26, 32)                                  # casing
    for y in (40, 58, 76):                                     # rune bands
        i.line([(26, 58 + (y - 58) * 0.98), (74, 58 + (y - 58) * 0.98)], 2.4, 0, caps=False)
    for x, y in ((40, 49), (60, 49), (50, 67)):
        i.star(x, y, 4, 1.6, 4, v=0)
    i.poly([(42, 88), (58, 88), (66, 98), (34, 98)])           # fins
    i.poly([(36, 30), (64, 30), (60, 22), (40, 22)], 0)        # open crown
    i.poly([(44, 28), (50, 2), (56, 28)])                      # exposed crystal
    i.poly([(36, 30), (40, 12), (46, 28)]); i.poly([(54, 28), (60, 12), (64, 30)])
    i.line([(50, 8), (50, 24)], 1.4, 0, caps=False)
    i.rays(50, 16, 20, 28, 8, 3, rot=22)
    return i


def arcane_missile():
    i = Icon()
    for k, (x, y, s) in enumerate(((78, 22, 1.0), (62, 52, 0.85), (84, 74, 0.7))):
        i.taper((x - 60 * s, y + 30 * s), (x - 40 * s, y + 14 * s), (x - 18 * s, y + 6 * s), (x, y), 2 * s, 12 * s)
        i.star(x, y, 13 * s, 5 * s, 4, rot=-45)
        i.circle(x, y, 4 * s, 0)
        i.circle(x - 34 * s, y + 22 * s, 2.5 * s)
    return i


def arcane_annihilator():
    i = Icon()
    i.ring(50, 54, 40, 4)                                      # rune ring
    for a in range(0, 360, 45):
        r = math.radians(a)
        i.rect(50 + 40 * math.cos(r) - 3, 54 + 40 * math.sin(r) - 3, 50 + 40 * math.cos(r) + 3, 54 + 40 * math.sin(r) + 3, 0)
    i.poly([(30, 40), (70, 40), (78, 62), (62, 80), (38, 80), (22, 62)])   # floating body
    i.circle(50, 58, 11, 0); i.circle(50, 58, 7); i.circle(50, 58, 3, 0)    # eye
    for x, h in ((36, 18), (50, 32), (64, 18)):                # crystal crown
        i.poly([(x - 5, 40), (x, 40 - h), (x + 5, 40)])
    i.poly([(40, 80), (60, 80), (50, 98)])                     # hovering point
    i.line([(14, 58), (2, 52)], 4); i.line([(86, 58), (98, 52)], 4)
    return i


def void_bomber():
    i = Icon()
    # crescent hull
    i.ellipse(50, 44, 46, 22)
    i.ellipse(50, 28, 40, 16, 0)
    for x in (8, 92):
        i.poly([(x, 40), (x + (8 if x < 50 else -8), 46), (x - (6 if x < 50 else -6), 22)])
    # central eye
    i.ellipse(50, 48, 12, 9, 0); i.ellipse(50, 48, 8, 6); i.ellipse(50, 48, 2.5, 5, 0)
    # spines on the rim
    for x in (24, 36, 64, 76):
        i.poly([(x - 3, 36), (x, 28 - abs(50 - x) * 0.1), (x + 3, 36)])
    # trailing tendrils and falling void orbs
    for k, x in enumerate((28, 42, 58, 72)):
        i.taper((x, 60), (x - 4, 72), (x + 6, 80), (x + (2 if k % 2 else -4), 92), 5, 1)
    i.circle(50, 84, 6); i.circle(50, 84, 2.5, 0)
    return i


ICONS = {
    "Gyrocopter": gyrocopter, "Bomber Zeppelin": bomber_zeppelin, "War Zeppelin": war_zeppelin,
    "Gryphon Rider": gryphon_rider, "Batrider": batrider, "Frost Wyrm": frost_wyrm, "Wind Rider": wind_rider,
    "Dragonhawk Rider": dragonhawk_rider, "Cloud Serpent Rider": cloud_serpent_rider, "Sky Golem": sky_golem,
    "Goblin Zeppelin": goblin_zeppelin, "Mana Bomb": mana_bomb, "Arcane Missile": arcane_missile,
    "Arcane Annihilator": arcane_annihilator, "Void Bomber": void_bomber,
}


def write_all(images_dir):
    import os
    for name, fn in ICONS.items():
        fn().save(os.path.join(images_dir, "UnitIcons", name + ".png"))
    return len(ICONS)
