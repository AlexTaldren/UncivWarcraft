"""Policy, policy-branch and promotion icons (Nov 2026), in the same pixel-art hand as the tech and
building icons. Promotion icons are shown very small in play, so each is one bold shape; a corner mark
is used only where two abilities share a shape. Cooldowns show their ability with an hourglass mark.
"""
import math
import os

from PIL import Image

import building_icons as BI
import tech_icons as TI
from tech_icons import B, M, C, N, Ic

T = BI.from_tech


# ---------------------------------------------------------------- new shapes
def arrow(i):
    i.L([(5, 27), (22, 10)], 3)
    i.P([(17, 4), (28, 4), (28, 15)])
    return i.P([(2, 24), (8, 30), (3, 30), (2, 29)], M).L([(4, 22), (10, 28)], 2, M)


def arrows3(i):
    for x in (6, 16, 26):
        i.R(x - 1, 9, x, 29)
        i.P([(x - 5, 10), (x, 1), (x + 4, 10)])
        i.P([(x - 4, 31), (x - 1, 26), (x, 26), (x + 3, 31)], M)
    return i


def arrows_down(i):
    for x, y in ((4, 2), (13, 0), (22, 2)):
        i.L([(x, y), (x + 8, y + 18)], 2)
        i.P([(x + 4, y + 17), (x + 12, y + 14), (x + 10, y + 24)])
        i.L([(x - 2, y + 2), (x + 2, y)], 2, M)
    return i.R(0, 29, 31, 30, M)


def arc_shot(i):
    i.d.arc([2, 5, 28, 45], 180, 345, fill=B, width=3)
    i.P([(22, 16), (31, 16), (28, 25)])
    i.E(4, 26, 3, t=M)
    return i.R(0, 29, 31, 30, M)


def spears(i):
    for x in (6, 16, 26):
        i.R(x - 1, 9, x, 31, M)
        i.P([(x - 4, 10), (x - 1, 0), (x, 0), (x + 3, 10), (x, 13), (x - 1, 13)])
    return i


def hook(i):
    i.R(15, 0, 16, 18, M)
    i.ring(15, 2, 3, 1)
    for s in (-1, 1):
        i.L([(15, 18), (15 + 11 * s, 26), (15 + 12 * s, 16)], 3)
        i.P([(15 + 9 * s, 17), (15 + 12 * s, 11), (15 + 15 * s, 17)])
    return i.L([(15, 18), (15, 30)], 3).P([(12, 28), (15, 31), (18, 28)])


def wing(i):
    i.P([(2, 26), (4, 12), (12, 4), (30, 2), (24, 8), (28, 9), (21, 14), (25, 16), (17, 20), (20, 23), (10, 26)])
    for a, b in (((8, 12), (22, 6)), ((8, 17), (20, 13)), ((8, 22), (16, 19))):
        i.L([a, b], 1, C)
    return i


def feather(i):
    i.P([(27, 1), (30, 9), (22, 21), (10, 26), (12, 14), (19, 5)])
    i.L([(27, 3), (3, 30)], 2, M)
    for a, b in (((20, 11), (27, 12)), ((16, 16), (23, 18)), ((18, 12), (17, 6))):
        i.L([a, b], 1, C)
    return i


def boot(i):
    i.P([(8, 1), (19, 1), (19, 17), (28, 21), (30, 27), (6, 27), (7, 14)])
    i.R(6, 27, 30, 30, M)
    i.R(8, 4, 19, 5, C)
    return i.L([(20, 20), (24, 22)], 1, C)


def pierce(i):
    i.P([(9, 4), (27, 4), (27, 15), (18, 28), (9, 15)])
    i.P([(18, 4), (27, 4), (27, 15), (18, 28)], M)
    i.L([(0, 15), (22, 15)], 3)
    i.P([(20, 10), (27, 15), (20, 20)], C)
    return i.P([(21, 11), (26, 15), (21, 19)])


def fist(i):
    i.R(6, 8, 25, 20)
    for x in (6, 11, 16, 21):
        i.R(x, 4, x + 3, 10)
        i.L([(x + 4, 5), (x + 4, 14)], 1, C)
    i.P([(2, 14), (8, 11), (12, 16), (8, 22), (3, 20)])
    i.R(9, 20, 23, 30, M)
    return i.R(9, 20, 23, 21, C)


def swirl(i):
    pts = []
    for k in range(40):
        a = k * 0.42
        r = 2 + k * 0.33
        pts.append((16 + r * math.cos(a), 16 + r * math.sin(a)))
    i.L(pts, 3)
    return i.E(16, 16, 2, t=M)


def bird(i):
    i.P([(3, 30), (5, 14), (11, 6), (19, 3), (25, 7), (31, 11), (24, 13), (21, 18), (22, 30)])
    i.P([(25, 7), (31, 11), (24, 13)], M)
    i.E(19, 8, 1, t=C)
    return i.L([(8, 16), (14, 22)], 1, C).L([(7, 21), (12, 26)], 1, C)


def horn(i):
    i.P([(2, 8), (6, 6), (14, 16), (27, 20), (30, 14), (31, 26), (26, 30), (10, 24), (3, 13)])
    i.P([(27, 20), (30, 14), (31, 26), (26, 30)], M)
    i.R(1, 6, 5, 9)
    return i.L([(12, 17), (9, 22)], 1, C)


def hoof(i):
    # a cloven hoof slamming down, the ground splitting under it
    i.P([(11, 0), (21, 0), (22, 10), (26, 18), (26, 22), (6, 22), (6, 18), (10, 10)])
    i.P([(15, 14), (17, 14), (16, 22)], C)
    i.R(10, 8, 22, 9, M)
    i.L([(0, 24), (31, 24)], 2)
    for a, b in (((8, 26), (2, 31)), ((16, 26), (16, 31)), ((24, 26), (30, 31)), ((12, 26), (9, 30)), ((20, 26), (23, 30))):
        i.L([a, b], 2, M)
    return i


def claw(i):
    for x in (4, 13, 22):
        i.P([(x + 6, 1), (x + 8, 4), (x + 3, 30), (x, 26), (x + 1, 12)])
    return i


def triad(i):
    i.bolt(16, 0, 13)
    i.P([(1, 30), (7, 17), (10, 22), (12, 19), (15, 30)], M)
    i.flame(24, 30, 13)
    return i


def crest(i):
    i.P([(0, 30), (2, 16), (9, 7), (19, 3), (27, 7), (29, 14), (24, 12), (20, 12), (17, 16), (18, 23), (24, 28), (31, 30)])
    i.P([(27, 7), (29, 14), (24, 12)], M)
    i.L([(6, 22), (10, 14), (16, 10)], 1, C)
    return i.E(27, 18, 1, t=M).E(30, 22, 1, t=M)


def hand(i):
    i.R(9, 13, 23, 27)
    for x, top in ((9, 5), (13, 2), (17, 3), (21, 6)):
        i.R(x, top, x + 2, 14)
    i.P([(9, 17), (3, 12), (2, 15), (9, 24)])
    i.R(11, 27, 21, 30, M)
    return i.star(16, 20, 4, C)


def web(i):
    for k in range(8):
        a = k * math.pi / 4
        i.L([(16, 16), (16 + 15 * math.cos(a), 16 + 15 * math.sin(a))], 1)
    for r, t in ((5, B), (10, M), (14, B)):
        pts = [(16 + r * math.cos(k * math.pi / 4), 16 + r * math.sin(k * math.pi / 4)) for k in range(9)]
        i.L(pts, 2 if r != 10 else 1, t)
    return i


def bone(i):
    i.L([(7, 25), (25, 7)], 5)
    for x, y in ((4, 24), (8, 28), (24, 4), (28, 8)):
        i.E(x, y, 3)
    return i.L([(10, 23), (22, 11)], 1, M)


def owl(i):
    i.P([(5, 2), (10, 6), (22, 6), (27, 2), (27, 20), (21, 29), (11, 29), (5, 20)])
    i.E(11, 12, 4, t=C).E(21, 12, 4, t=C).E(11, 12, 2).E(21, 12, 2)
    i.P([(14, 15), (18, 15), (16, 20)], M)
    return i.L([(10, 22), (13, 25)], 1, C).L([(22, 22), (19, 25)], 1, C).R(11, 29, 13, 31).R(19, 29, 21, 31)


def chevrons(i):
    for x, t in ((2, M), (12, B)):
        i.P([(x, 3), (x + 7, 3), (x + 17, 16), (x + 7, 29), (x, 29), (x + 10, 16)], t)
    return i


def plate(i):
    i.P([(3, 3), (29, 3), (29, 15), (16, 30), (3, 15)])
    i.P([(16, 3), (29, 3), (29, 15), (16, 30)], M)
    for x, y in ((7, 6), (24, 6), (7, 15), (24, 15), (12, 22), (20, 22)):
        i.R(x, y, x + 1, y + 1, C)
    return i


def bigflame(i):
    # a great drop of blood between two fangs
    i.E(16, 20, 8, 9)
    i.P([(16, 1), (24, 18), (8, 18)])
    i.E(13, 21, 2, t=M)
    i.P([(1, 3), (8, 3), (4, 17)]).P([(24, 3), (31, 3), (28, 17)])
    return i


def fel(i):
    return i.flame(16, 30, 28)


def blink(i):
    # a figure gone in a flash: fading afterimages trailing a bright burst
    i.star(21, 11, 10)
    i.E(21, 11, 2, t=C)
    i.star(9, 22, 5, M)
    i.R(3, 28, 4, 29, M).R(14, 17, 15, 18, M)
    return i.L([(1, 12), (8, 12)], 1, M).L([(3, 16), (9, 16)], 1, M)


def sword(i):
    return i.sword(15, 1, 30)


def scroll(i):
    return TI._scroll(i)


def b_hourglass(i, x, y):
    i.R(x - 4, y - 5, x + 4, y - 4).R(x - 4, y + 4, x + 4, y + 5)
    i.P([(x - 3, y - 3), (x + 3, y - 3), (x, y)]).P([(x, y), (x + 3, y + 3), (x - 3, y + 3)])


BI.MARKS["hourglass"] = b_hourglass

# ---------------------------------------------------------------- tables
POLICIES = {
    "Noble Houses": BI.shield, "Strom's Legacy": (sword, "crown"), "Keep and Garrison": BI.keep, "Crownlands": (T("Farming"), "crown"),
    "High Kingship": BI.crown,
    "Free Towns": BI.hall, "Ready to Work": T("Mining"), "Pioneers' Charter": T("Philosophy"), "Town Councils": T("Auctioneering"),
    "Kingsroads": T("Trade Guilds"),
    "Lok'tar Ogar": T("Bronze Working"), "Shield Wall": T("Battle Formations"), "Veterans' Lore": BI.helm, "Honor Guard": BI.armory,
    "Kor'kron Regulars": spears,
    "Ordained Clergy": BI.brazier, "Divine Mandate": BI.sun, "Temple Tithes": (BI.temple, "coin"), "Spiritual Renewal": T("Nature's Blessing"),
    "Many Paths": T("Navigation"),
    "Gilded Gifts": BI.chest, "Courtly Grace": T("Bardic Lore"), "Kirin Tor Exchange": T("Eye of Kilrogg"), "Embassies": BI.banner,
    "Heroes of Many Lands": T("Azerothian Unity"),
    "Admiralty": BI.anchor, "Merchant Guilds": BI.stall, "Harbor Masters": BI.lighthouse, "Steamwheedle Charter": (scroll, "coin"),
    "Cartel Monopolies": BI.coins,
    "Apprentice Mages": BI.spire, "Wonders of the Arcane": T("Arcane Science"), "Open Libraries": lambda i: i.book(),
    "Patrons of Dalaran": (T("Scrying"), "crown"), "Arcane Revolution": T("Unstable Mana"),
    "Charter of Kings": (scroll, "crown"), "Common Voice": horn, "Civic Guilds": BI.hammer_gear, "Open Council": T("Arathi Law"),
    "House of Nobles": BI.temple,
    "Rallying Cry": T("War Drums"), "Warchief's Coffers": (BI.chest, "skull"), "Iron Will": fist, "Inquisition": BI.bars,
    "Iron Horde Doctrine": T("War Doctrine"),
    "Brothers in Arms": BI.swords, "Grand Stewardship": (T("Farming"), "star"), "Ancestral Pride": BI.totem, "Common Granaries": BI.granary,
    "Collective Labor": T("Construction"),
    "Embraced the Fel": (fel, "skull"), "Rejected the Fel": (BI.shield, "flame"),
    "Sunwell Restored by the Light": lambda i: BI.well(i, "sun"), "Sunwell Rekindled by Arcane": lambda i: BI.well(i, "star"),
    "Kyrian Covenant": wing, "Venthyr Covenant": BI.cup, "Night Fae Covenant": BI.tree, "Necrolord Covenant": BI.skull,
}

BRANCHES = {
    "Old Kingdoms": BI.castle, "Frontier": BI.tent, "Blood and Thunder": T("Storm Hammers"), "Devotion": BI.brazier,
    "Diplomacy": T("Azerothian Unity"), "Trade Princes": BI.coins, "Arcane Inquiry": T("Mana Theory"), "Free Peoples": T("Arathi Law"),
    "Dominion": fist, "Unity": T("Battle Formations"), "Fateful Choices": BI.hourglass,
}

PROMOTIONS = {
    "Heal Instantly": (BI.heart, "bolt"), "Deadeye": BI.target, "Barrage": arrows3, "Volley": arrows_down, "Extended Range": (T("Archery"), "star"),
    "Indirect Fire": arc_shot, "Heroic Strike": sword, "Weapon Mastery": BI.swords, "Charge": T("Riding"), "Besiege": T("Siege Engineering"),
    "Spear Wall": spears, "Bloodlust": bigflame, "Woodsman": BI.tree, "Amphibious": BI.wave, "Medic": BI.heart, "Scouting": T("Eye of Kilrogg"),
    "Survivalism": BI.tent, "Boarding Party": hook, "Coastal Raider": lambda i: i.ship(), "Landing Party": BI.anchor,
    "Broadsides": TI._cannon, "Iron Plating": plate, "Aerie Deck": wing, "Ship's Carpenter": lambda i: i.hammer(16, 3, 29, 9),
    "Siege": T("Demolition"), "Evasion": feather, "Sky Sentinel": (wing, "star"), "Aerial Combat": T("Gnomish Flight"),
    "Aerial Targeting": (BI.target, "bolt"), "Skyguard Patrol": (wing, "eye"), "Long Flight": T("Navigation"), "Field Repairs": BI.wrench,
    "Mobility": boot, "Armor Piercing": pierce, "Defend": BI.shield, "March": lambda i: TI._banner(i, 16), "Sentry": BI.tower,
    "Rapid Fire": T("Long Rifles"), "Ambush": BI.mask, "Bombardment": T("Siege Barrage"), "Morale": BI.banner, "Rejuvenation": T("Soil Enrichment"),
    "Ignore terrain cost": chevrons, "Devout": BI.brazier,
    "Hero's Might": T("Mithril Forged Swords"), "Commanding Presence": BI.crown, "Second Wind": (BI.heart, "leaf"), "Battle-Hardened": BI.helm,
    "Swift Strider": (boot, "bolt"), "Legend of Azeroth": BI.cup, "Portal Adept": T("Portal Networks"), "Portal Attunement": (T("Portal Networks"), "star"),
    "Raid Veteran": (BI.helm, "star"), "Shadowmeld": BI.moon, "Keen Eyes": T("Focused Arcana"), "Flanker": T("Animal War Training"),
    "Hold the Line": BI.wall, "Shield Wall": T("Battle Formations"), "Cleave": BI.cleaver, "Last Stand": (BI.shield, "skull"),
    "Arcane Intellect": lambda i: i.book(), "Spell Ward": (BI.shield, "star"), "Blink": blink, "Eagle Eye": (bird, "eye"),
    "Volley Fire": (arrows_down, "flame"), "Camouflage": T("Herbalism"),
    # hero abilities
    "Rallying Cry": horn, "Mana Shield": BI.crystal, "Hunter's Mark": (BI.target, "paw"), "Divine Shield": (BI.shield, "sun"),
    "Hellscream's Fury": T("Bronze Working"), "Thunder Clap": T("Storm Hammers"), "Overclock": BI.gear, "War Stomp": hoof,
    "Holy Light": BI.sun, "Call the Sappers": T("Seaforium"), "Pounce": T("Beast Taming"), "Call the Fireguard": BI.campfire,
    "Rally the Admiralty": (BI.anchor, "crown"), "Storm, Earth and Fire": triad, "Phoenix Fire": (bird, "flame"), "Raise Dead": BI.coffin,
    "Pact of Bwonsamdi": BI.tiki, "Tranquility": T("Nature's Blessing"), "Windrunner Volley": (arrows3, "star"), "Black Arrow": (arrow, "skull"),
    "Voodoo Hex": (BI.tiki, "bolt"), "Tidal Wave": crest, "Time Stop": BI.hourglass, "Spirit of the Mountain": BI.mountain,
    "Frost Armor": T("Frost Enchantment"), "Drain Life": (BI.heart, "skull"), "Wild Growth": T("Natural Lore"), "Lightning Shield": (BI.shield, "bolt"),
    "Holy Ward": (BI.shield, "heart"), "Raise Ghoul": BI.skull, "Hex": BI.cauldron, "Death Coil": T("Secrets of the Void"),
    "Spell Steal": T("Scrying"), "Drunken Haze": BI.brewery, "Lay on Hands": hand, "Berserk": fist, "Arcane Torrent": T("Unstable Mana"),
    "Web": web, "Chi Wave": swirl, "Cannibalize": bone, "Aimed Shot": T("Optics"), "Sentinel Owl": owl, "Feral Leap": claw,
}


def render(spec, mark=None, rgb=(255, 255, 255)):
    main, m0 = spec if isinstance(spec, tuple) else (spec, None)
    i = Ic()
    if mark:                                   # a cooldown: the whole ability icon smaller, hourglass in the corner
        main, m0 = (lambda j, s=spec: _draw(j, s)), mark
    if m0:
        real = i.d
        i.d = BI._Scaled(real, 0.8)
        main(i)
        i.d = real
        BI._halo(i, 26, 26, 6)
        BI.MARKS[m0](i, 26, 26)
    else:
        main(i)
    a = i.im.resize((N * 3, N * 3), Image.NEAREST)
    out = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    ink = Image.new("RGBA", a.size, rgb + (255,))
    ink.putalpha(a)
    out.alpha_composite(ink, (2, 2))
    return out


def _draw(i, spec):
    main = spec[0] if isinstance(spec, tuple) else spec
    main(i)


def write_all(root):
    """root is the mod folder; writes into whichever image folders hold each icon set."""
    n = 0
    for sub, table in (("PolicyIcons", POLICIES), ("PolicyBranchIcons", BRANCHES), ("UnitPromotionIcons", PROMOTIONS)):
        for pack in sorted(os.listdir(root)):
            folder = os.path.join(root, pack, sub)
            if not pack.startswith("Images") or not os.path.isdir(folder):
                continue
            for name, spec in table.items():
                render(spec).save(os.path.join(folder, name + ".png"))
                n += 1
                if sub == "UnitPromotionIcons" and os.path.exists(os.path.join(folder, name + " Cooldown.png")):
                    render(spec, "hourglass").save(os.path.join(folder, name + " Cooldown.png"))
                    n += 1
    return n
