"""The Azeroth world map: Kalimdor, the Eastern Kingdoms and Northrend.

Coordinates are tile columns/rows on a 104 x 64 map, x to the east, y to the south
(row 0 is the northern edge). Zones are laid out from the World of Warcraft world map:
each land tile belongs to the nearest zone seed on its own landmass, and takes that
zone's terrain mix. Mountain ranges, lakes, natural wonders, capitals and
city-states are then placed at their real locations.
"""
import json, math, random

W, H = 104, 64

# ------------------------------------------------------------------ landmasses
LAND = {
    "Kalimdor": [(23, 14), (26, 13), (29, 14), (31, 16), (33, 18), (35, 20), (37, 23), (37, 26),
                 (35, 27), (34, 29), (34, 32), (33, 34), (32, 36), (31, 38), (32, 40), (31, 41),
                 (32, 43), (31, 45), (31, 47), (32, 49), (33, 52), (31, 55), (30, 58), (28, 61),
                 (25, 62), (22, 61), (19, 59), (17, 58), (14, 57), (12, 55), (10, 52), (9, 49),
                 (9, 46), (10, 43), (10, 40), (9, 37), (10, 34), (11, 31), (12, 28), (12, 25),
                 (13, 22), (15, 19), (18, 17), (20, 15)],
    "Teldrassil": [(7, 14), (11, 13), (13, 16), (12, 20), (8, 21), (6, 18)],
    "Bloodmyst Isle": [(3, 21), (6, 20), (7, 23), (4, 24)],
    "Azuremyst Isle": [(3, 26), (7, 26), (8, 30), (4, 31)],
    "Echo Isles": [(35.5, 34.5), (37, 34.5), (37, 36.5), (35.5, 36.5)],
    "Theramore Isle": [(33.8, 41.5), (35.5, 41.5), (35.5, 43.5), (33.8, 43.5)],
    "Sardor Isle": [(5.5, 45.5), (7, 45.5), (7, 47.5), (5.5, 47.5)],
    "Eastern Kingdoms": [(83, 11), (86, 10), (90, 9), (94, 10), (96, 12), (96, 16), (97, 20),
                         (96, 24), (95, 27), (94, 30), (92, 32), (91, 34), (93, 36), (95, 39),
                         (94, 43), (92, 46), (91, 49), (92, 52), (92, 55), (91, 58), (88, 59),
                         (85, 58), (82, 59), (81, 61), (79, 62), (76, 63), (74, 61), (73, 58),
                         (72, 55), (71, 52), (72, 49), (74, 47), (75, 45), (74, 43), (75, 40),
                         (76, 37), (78, 35), (80, 34), (78, 32), (76, 30), (72, 33), (68, 33),
                         (67, 30), (69, 27), (71, 25), (72, 21), (73, 17), (75, 15), (78, 14),
                         (81, 12)],
    "Isle of Quel'Danas": [(84.5, 3), (91, 3), (92, 6.5), (85.5, 7.5)],
    "Tol Barad": [(71.5, 34.5), (73.5, 34.5), (73.5, 36.5), (71.5, 36.5)],
    "Northrend": [(38, 17), (42, 19), (46, 17), (50, 17), (54, 16), (58, 18), (62, 19), (66, 18),
                  (68, 15), (68, 10), (66, 6), (62, 3), (55, 1.5), (47, 1.5), (41, 3), (38, 6),
                  (37, 10), (37, 14)],
    "Kezan": [(55.5, 39.5), (58, 39.5), (58.5, 42), (56, 42.5)],
    "The Lost Isles": [(47, 40.5), (49.5, 40.5), (49.5, 42.5), (47, 42.5)],
    "The Wandering Isle": [(48, 50), (54, 49.5), (55, 54), (49, 55)],
    # v0.17
    "Kul Tiras": [(57, 22), (61, 21), (64, 23), (64.5, 27), (61, 29.5), (57.5, 28.5), (56, 25)],
    "Zandalar": [(37, 56), (42, 55), (45.5, 57), (45.5, 61), (42, 62.5), (38, 62), (36, 59)],
    "Isle of Thunder": [(57.5, 46), (60.5, 46), (61, 48.5), (58, 49)],
}

# ------------------------------------------------------------------ zones
# name: (landmass, [seed points], biome)
# biome: base terrain weights, then chances for Forest / Jungle / Marsh / Hill / Mountain / Blight / Oasis
def B(base, forest=0, jungle=0, marsh=0, hill=0, mountain=0, blight=0, oasis=0,
      fel=0, plague=0, ancient=0, bamboo=0, molten=0, crystal=0, titan=0):
    """Zone biome. forest..oasis: chance per tile. fel/plague/molten/titan: chance per
    tile (fel and plague overrun vegetation). ancient/bamboo/crystal: share of the
    zone's forests that are that kind of forest instead."""
    return dict(base=base, forest=forest, jungle=jungle, marsh=marsh, hill=hill,
                mountain=mountain, blight=blight, oasis=oasis, fel=fel, plague=plague,
                ancient=ancient, bamboo=bamboo, molten=molten, crystal=crystal, titan=titan)

G, P, T, D, S = "Grassland", "Plains", "Tundra", "Desert", "Snow"

ZONES = {
    # --- Kalimdor
    "Teldrassil": ("Teldrassil", [(9, 17)], B({G: 1}, forest=.75, ancient=.6)),
    "Bloodmyst Isle": ("Bloodmyst Isle", [(5, 22)], B({P: 1}, forest=.4, marsh=.15, crystal=.2)),
    "Azuremyst Isle": ("Azuremyst Isle", [(5, 28)], B({G: 1}, forest=.45, hill=.1, crystal=.25)),
    "Darkshore": ("Kalimdor", [(14, 21), (13, 26)], B({G: .7, P: .3}, forest=.65, hill=.1, ancient=.4)),
    "Moonglade": ("Kalimdor", [(20, 17)], B({G: 1}, forest=.35, ancient=.5)),
    "Winterspring": ("Kalimdor", [(25, 16), (30, 18)], B({S: .45, T: .55}, forest=.3, hill=.25, mountain=.06)),
    "Felwood": ("Kalimdor", [(19, 21), (18, 24)], B({P: .6, G: .4}, forest=.65, marsh=.15, fel=.3)),
    "Mount Hyjal": ("Kalimdor", [(27, 22)], B({G: .7, T: .3}, forest=.55, hill=.3, mountain=.18, ancient=.4)),
    "Azshara": ("Kalimdor", [(33, 22), (35, 25)], B({G: .6, P: .4}, forest=.4, hill=.2, ancient=.2)),
    "Ashenvale": ("Kalimdor", [(19, 28), (25, 27)], B({G: 1}, forest=.8, hill=.08, ancient=.6)),
    "Stonetalon Mountains": ("Kalimdor", [(15, 31), (14, 35)], B({P: .6, T: .4}, forest=.2, hill=.4, mountain=.25)),
    "Durotar": ("Kalimdor", [(32, 30), (32, 33)], B({P: .75, D: .25}, hill=.2, forest=.05)),
    "Northern Barrens": ("Kalimdor", [(26, 32), (29, 35)], B({P: .9, G: .1}, forest=.04, hill=.1)),
    "Desolace": ("Kalimdor", [(13, 39), (12, 43)], B({D: .7, P: .3}, hill=.2, mountain=.05)),
    "Mulgore": ("Kalimdor", [(19, 38)], B({G: .6, P: .4}, hill=.15)),
    "Southern Barrens": ("Kalimdor", [(24, 40), (28, 39)], B({P: 1}, hill=.15, forest=.05)),
    "Dustwallow Marsh": ("Kalimdor", [(30, 42), (30, 45)], B({G: 1}, marsh=.6, forest=.15)),
    "Feralas": ("Kalimdor", [(12, 48), (15, 51)], B({G: 1}, jungle=.5, forest=.25, hill=.1, ancient=.3)),
    "Thousand Needles": ("Kalimdor", [(21, 45), (26, 46)], B({D: .5, P: .5}, hill=.3, mountain=.18)),
    "Tanaris": ("Kalimdor", [(28, 50), (30, 53)], B({D: 1}, hill=.15, oasis=.05, titan=.02)),
    "Un'Goro Crater": ("Kalimdor", [(22, 51)], B({G: 1}, jungle=.7, hill=.2, molten=.04)),
    "Silithus": ("Kalimdor", [(16, 54), (19, 57)], B({D: 1}, hill=.15)),
    "Uldum": ("Kalimdor", [(24, 58), (27, 58)], B({D: 1}, oasis=.1, hill=.05, titan=.08)),
    "Echo Isles": ("Echo Isles", [(36, 35)], B({P: 1}, jungle=.3)),
    "Theramore Isle": ("Theramore Isle", [(34, 42)], B({G: 1}, marsh=.2)),
    "Sardor Isle": ("Sardor Isle", [(6, 46)], B({G: 1}, forest=.5)),
    # --- Eastern Kingdoms
    "Isle of Quel'Danas": ("Isle of Quel'Danas", [(88, 5)], B({G: 1}, forest=.35)),
    "Eversong Woods": ("Eastern Kingdoms", [(87, 12), (92, 12)], B({G: 1}, forest=.6)),
    "Ghostlands": ("Eastern Kingdoms", [(92, 16)], B({P: .6, G: .4}, forest=.5, marsh=.1, plague=.15)),
    "Eastern Plaguelands": ("Eastern Kingdoms", [(90, 20), (94, 22)], B({P: .7, T: .3}, forest=.2, hill=.15, plague=.35)),
    "Western Plaguelands": ("Eastern Kingdoms", [(85, 20)], B({P: 1}, forest=.1, hill=.1, plague=.25)),
    "Tirisfal Glades": ("Eastern Kingdoms", [(77, 17), (81, 15)], B({G: .7, P: .3}, forest=.4, marsh=.2, plague=.05)),
    "Silverpine Forest": ("Eastern Kingdoms", [(74, 21), (73, 25)], B({T: .5, P: .5}, forest=.7, hill=.2)),
    "Gilneas": ("Eastern Kingdoms", [(70, 30)], B({G: .5, P: .5}, forest=.5, hill=.2)),
    "Hillsbrad Foothills": ("Eastern Kingdoms", [(78, 28)], B({G: 1}, forest=.2, hill=.2)),
    "Alterac Mountains": ("Eastern Kingdoms", [(80, 23)], B({S: .5, T: .5}, hill=.4, mountain=.4)),
    "The Hinterlands": ("Eastern Kingdoms", [(89, 26), (93, 27)], B({G: 1}, forest=.4, hill=.4)),
    "Arathi Highlands": ("Eastern Kingdoms", [(84, 31), (88, 32)], B({G: .6, P: .4}, hill=.3)),
    "Wetlands": ("Eastern Kingdoms", [(79, 37)], B({G: 1}, marsh=.5, hill=.15)),
    "Twilight Highlands": ("Eastern Kingdoms", [(90, 38), (91, 42)], B({P: .5, G: .5}, hill=.4, mountain=.15)),
    "Dun Morogh": ("Eastern Kingdoms", [(77, 42)], B({S: .25, T: .75}, hill=.35, mountain=.1, forest=.2)),
    "Loch Modan": ("Eastern Kingdoms", [(84, 40)], B({G: .5, P: .5}, hill=.3)),
    "Badlands": ("Eastern Kingdoms", [(88, 45)], B({D: 1}, hill=.4, mountain=.15, titan=.08)),
    "Searing Gorge": ("Eastern Kingdoms", [(81, 45)], B({D: .5, P: .5}, hill=.4, mountain=.2, molten=.35)),
    "Burning Steppes": ("Eastern Kingdoms", [(83, 48)], B({D: .6, P: .4}, hill=.4, molten=.45)),
    "Elwynn Forest": ("Eastern Kingdoms", [(77, 50)], B({G: 1}, forest=.4)),
    "Redridge Mountains": ("Eastern Kingdoms", [(87, 50)], B({P: .5, G: .5}, hill=.5, mountain=.2)),
    "Westfall": ("Eastern Kingdoms", [(74, 54)], B({P: 1}, hill=.05)),
    "Duskwood": ("Eastern Kingdoms", [(78, 55)], B({G: 1}, forest=.8)),
    "Deadwind Pass": ("Eastern Kingdoms", [(82, 55)], B({T: .5, P: .5}, hill=.4, mountain=.5)),
    "Swamp of Sorrows": ("Eastern Kingdoms", [(88, 53)], B({G: 1}, marsh=.7, jungle=.2)),
    "Blasted Lands": ("Eastern Kingdoms", [(89, 57)], B({D: 1}, hill=.25, fel=.4)),
    "Stranglethorn Vale": ("Eastern Kingdoms", [(77, 59), (78, 61)], B({G: 1}, jungle=.8, hill=.2)),
    "Tol Barad": ("Tol Barad", [(72, 35)], B({P: 1}, hill=.3)),
    # --- Northrend
    "Borean Tundra": ("Northrend", [(41, 15), (39, 12)], B({T: 1}, forest=.1, marsh=.1, hill=.1)),
    "Sholazar Basin": ("Northrend", [(40, 7)], B({G: 1}, jungle=.7, titan=.05)),
    "Icecrown": ("Northrend", [(46, 5), (51, 4)], B({S: 1}, hill=.3, mountain=.25, plague=.15)),
    "Wintergrasp": ("Northrend", [(46, 10)], B({S: .5, T: .5}, hill=.3)),
    "Dragonblight": ("Northrend", [(50, 13), (54, 13)], B({S: .7, T: .3}, hill=.15, plague=.08)),
    "Crystalsong Forest": ("Northrend", [(55, 8)], B({T: 1}, forest=.7, crystal=.6)),
    "The Storm Peaks": ("Northrend", [(59, 4), (63, 5)], B({S: 1}, mountain=.5, hill=.3, titan=.07)),
    "Zul'Drak": ("Northrend", [(62, 10)], B({T: .6, S: .4}, hill=.3, plague=.08)),
    "Grizzly Hills": ("Northrend", [(63, 14)], B({T: 1}, forest=.7, hill=.25)),
    "Howling Fjord": ("Northrend", [(66, 16), (60, 17)], B({T: 1}, forest=.4, hill=.3, mountain=.1)),
    # --- South Seas
    "Kezan": ("Kezan", [(57, 41)], B({G: 1}, jungle=.5)),
    "The Lost Isles": ("The Lost Isles", [(48, 41)], B({P: 1}, jungle=.5, hill=.2)),
    "The Wandering Isle": ("The Wandering Isle", [(51, 52)], B({G: 1}, forest=.4, hill=.2, bamboo=.9)),
    # --- v0.17: Kul Tiras, Zandalar, the Isle of Thunder
    "Tiragarde Sound": ("Kul Tiras", [(61, 27)], B({G: .6, P: .4}, forest=.3, hill=.2)),
    "Drustvar": ("Kul Tiras", [(57, 24)], B({T: .5, G: .5}, forest=.7, hill=.25)),
    "Stormsong Valley": ("Kul Tiras", [(62, 23)], B({G: .7, P: .3}, forest=.25, hill=.25)),
    "Zuldazar": ("Zandalar", [(42, 58)], B({G: 1}, jungle=.55, hill=.3)),
    "Nazmir": ("Zandalar", [(41, 61)], B({G: 1}, marsh=.55, jungle=.3)),
    "Vol'dun": ("Zandalar", [(37, 58)], B({D: 1}, hill=.2, oasis=.05)),
    "Isle of Thunder": ("Isle of Thunder", [(59, 47)], B({G: 1}, jungle=.3, hill=.3)),
}

# ------------------------------------------------------------------ mountain ranges & lakes
RIDGES = [  # (polyline, chance a tile on the line becomes Mountain)
    ([(14, 30), (16, 34), (15, 37)], .8),                 # Stonetalon spine
    ([(22, 35), (22, 38)], .7),                           # Mulgore escarpment
    ([(19, 44), (19, 49)], .7),                           # Feralas / Needles divide
    ([(70, 27), (71, 28), (74, 29)], .9),                 # Greymane Wall country
    ([(75, 40), (80, 40)], .8),                           # Khaz Modan ridge
    ([(76, 48), (86, 48)], .55),                          # Burning Steppes / Elwynn / Redridge
    ([(74, 57), (81, 57)], .4),                           # Duskwood / Stranglethorn
    ([(86, 55), (91, 55)], .6),                           # Swamp of Sorrows / Blasted Lands
    ([(42, 6), (43, 11)], .8),                            # Sholazar rim
]
RINGS = [((22, 51), 2.6, .7)]                             # Un'Goro crater rim
LAKES = [(77, 24), (78, 24), (84, 40), (86, 51), (83, 18)]  # Lordamere, Loch Modan, Lake Everstill, Brightwater

# ------------------------------------------------------------------ landmarks
NATURAL_WONDERS = {
    "The Maelstrom": (52, 34),
    "Mount Hyjal": (27, 21),
    "Teldrassil": (10, 16),
    "Moonglade": (21, 18),
    "Lake Elune'ara": (20, 18),
    "Stonetalon Peak": (14, 32),
    "Red Rocks of Mulgore": (20, 40),
    "Thousand Needles": (23, 46),
    "Un'Goro Crater": (22, 51),
    "Lakkari Tar Pits": (21, 52),
    "Lost City of the Tol'vir": (25, 59),
    "Blackrock Mountain": (81, 47),
    "Cape of Stranglethorn": (76, 62),
    "Kelp'thar Forest": (69, 50),
    "The Dark Portal": (90, 58),       # Blasted Lands
    "The Nexus": (37, 11),             # Coldarra, Borean Tundra
    "Galakrond's Rest": (52, 14),      # Dragonblight
    "Sunken Temple": (89, 53),         # Swamp of Sorrows
    "Maraudon": (12, 42),              # Desolace
    "The Lifeblood Pillar": (40, 7),   # Sholazar Basin
}
NW_BASE = {"Un'Goro Crater": "Desert", "The Dark Portal": "Desert", "The Nexus": "Snow",
           "Galakrond's Rest": "Snow", "Sunken Temple": "Grassland", "Maraudon": "Desert",
           "The Lifeblood Pillar": "Grassland"}
HARMFUL = {"Blighted Land", "Fel-Scorched Land", "Plagued Land", "Molten Fields"}

CAPITALS = {  # major nations -> their capital's tile
    "Humans": (76, 50),            # Stormwind, Elwynn Forest
    "Orcs": (32, 29),              # Orgrimmar, Durotar
    "Night Elves": (9, 18),        # Darnassus, Teldrassil
    "Dwarves": (80, 42),           # Ironforge, Dun Morogh
    "Gnomes": (76, 43),            # Gnomeregan, Dun Morogh
    "Tauren": (19, 38),            # Thunder Bluff, Mulgore
    "Trolls": (33, 34),            # Sen'jin Village, Durotar
    "Blood Elves": (91, 12),       # Silvermoon, Eversong Woods
    "High Elves": (88, 5),         # Quel'Danas
    "Pandaren": (51, 52),          # The Wandering Isle
    "Forsaken": (78, 18),          # Undercity, Tirisfal Glades
    "Draenei": (5, 28),            # The Exodar, Azuremyst Isle
    "Goblins": (34, 24),           # Bilgewater Harbor, Azshara
    "Worgen": (70, 31),            # Gilneas
    "Scourge": (46, 5),            # Icecrown Citadel, Icecrown
    "Dark Iron Dwarves": (85, 49), # Shadowforge City, beneath Blackrock (Burning Steppes)
    "Kul Tirans": (61, 27),        # Boralus, Tiragarde Sound
    "Zandalari Trolls": (42, 58),  # Zuldazar
}
CITY_STATES = {
    "Dalaran": (79, 25),           # Alterac, on Lordamere Lake
    "Theramore": (34, 42),
    "Stromgarde": (82, 32),        # Arathi Highlands
    "Gadgetzan": (28, 50),         # Tanaris
    "Booty Bay": (77, 61),         # Stranglethorn
    "Ratchet": (31, 37),           # Barrens coast
    "Everlook": (28, 17),          # Winterspring
    "Steamwheedle Port": (31, 54), # Tanaris coast
    "Light's Hope Chapel": (93, 21),      # Eastern Plaguelands
    "Cenarion Hold": (17, 54),     # Silithus
    "Argent Vanguard": (54, 7),    # Icecrown, by the Crystalsong border
    "The Earthen Ring": (13, 41),  # Desolace
    "Knights of the Ebon Blade": (61, 10),   # Ebon Watch, Zul'Drak
    "Explorers' League": (88, 46), # Badlands, near Uldaman
    "Thorium Brotherhood": (81, 46),         # Thorium Point, Searing Gorge
    "Feathermoon Stronghold": (6, 46),        # Sardor Isle, Feralas
    "Timbermaw Hold": (23, 20),    # furbolgs, Felwood / Winterspring
    "Kamagua": (64, 15),           # tuskarr, Howling Fjord
    "Maraudine": (16, 46),         # centaurs, Desolace / Feralas
    "Jasperlode Mine": (80, 54),   # kobolds, Duskwood edge of Elwynn
    "Razorfen Kraul": (26, 43),    # quilboar, Southern Barrens
    "The Consortium": (42, 14),    # ethereals, Borean Tundra
    "Mogu'shan": (59, 47),         # mogu, Isle of Thunder
    "Ahn'Qiraj": (20, 57),         # qiraji, Silithus
}


# ------------------------------------------------------------------ geometry helpers
def center(c, r):
    """Tile center in map units; odd columns sit half a row north."""
    return (c, r - 0.5 * (c % 2))


def inside(pt, poly):
    x, y = pt
    n = len(poly); ins = False
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            ins = not ins
    return ins


def seg_dist(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    dx, dy = bx - ax, by - ay
    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy or 1)))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def neighbors(c, r, w=W, h=H):
    # flat-top hex offset grid where odd columns are shifted north
    if c % 2:
        d = [(0, -1), (0, 1), (-1, -1), (-1, 0), (1, -1), (1, 0)]
    else:
        d = [(0, -1), (0, 1), (-1, 0), (-1, 1), (1, 0), (1, 1)]
    return [(c + a, r + b) for a, b in d if 0 <= c + a < w and 0 <= r + b < h]


# ------------------------------------------------------------------ build
def build(seed=7, width=W, height=H, spec=None):
    """Build the map at any size. All coordinates above are authored on the 104 x 64
    grid and scaled here, so a larger map keeps the same shape and placements."""
    sp = spec or {}
    LAND_, ZONES_, RIDGES_, RINGS_ = sp.get("LAND", LAND), sp.get("ZONES", ZONES), sp.get("RIDGES", RIDGES), sp.get("RINGS", RINGS)
    LAKES_, NW_, NWB_ = sp.get("LAKES", LAKES), sp.get("NATURAL_WONDERS", NATURAL_WONDERS), sp.get("NW_BASE", NW_BASE)
    CAPS_, CS_ = sp.get("CAPITALS", CAPITALS), sp.get("CITY_STATES", CITY_STATES)
    sx, sy = width / sp.get("W", W), height / sp.get("H", H)
    k = (sx + sy) / 2
    S = lambda p: (p[0] * sx, p[1] * sy)
    land_polys = {n: [S(p) for p in poly] for n, poly in LAND_.items()}
    zones = {z: (lm, [S(p) for p in seeds], b) for z, (lm, seeds, b) in ZONES_.items()}
    ridges = [([S(p) for p in line], ch) for line, ch in RIDGES_]
    rings = [(S(c), rad * k, ch) for c, rad, ch in RINGS_]
    nb = lambda c, r: neighbors(c, r, width, height)
    rng = random.Random(seed)
    rng2 = random.Random(seed + 1000)                     # Warcraft features (v0.6)

    grid = [[None] * width for _ in range(height)]          # zone name or None (water)
    for r in range(height):
        for c in range(width):
            p = center(c, r)
            for land, poly in land_polys.items():
                if inside(p, poly):
                    best = min(((math.hypot(p[0] - zx, p[1] - zy), z)
                                for z, (lm, seeds, _) in zones.items() if lm == land
                                for zx, zy in seeds), default=(0, land))
                    grid[r][c] = best[1]
                    break

    def land(c, r):
        return grid[r][c] is not None

    def snap(pt, want_land=True, avoid=()):
        """Nearest tile to a scaled point that is land (or sea), searching outward."""
        c0, r0 = int(round(pt[0])), int(round(pt[1]))
        seen, frontier = {(c0, r0)}, [(c0, r0)]
        while frontier:
            for c, r in frontier:
                if 0 <= c < width and 0 <= r < height and land(c, r) == want_land and (c, r) not in avoid:
                    return (c, r)
            nxt = []
            for p in frontier:
                for q in nb(*p):
                    if q not in seen:
                        seen.add(q); nxt.append(q)
            frontier = nxt
        raise ValueError(pt)

    tiles = [[{"t": "Ocean", "f": []} for _ in range(width)] for _ in range(height)]
    for r in range(height):
        for c in range(width):
            z = grid[r][c]
            if z is None:
                continue
            b = zones[z][2]
            base = rng.choices(list(b["base"]), list(b["base"].values()))[0]
            t = {"t": base, "f": []}
            roll = rng.random()
            if roll < b["mountain"]:
                t["t"] = "Mountain"
            else:
                if rng.random() < b["hill"]:
                    t["f"].append("Hill")
                veg = rng.random()
                for feat, key, ok in (("Forest", "forest", base in (G, P, T)),
                                      ("Jungle", "jungle", base in (G, P)),
                                      ("Marsh", "marsh", base == G and "Hill" not in t["f"]),
                                      ("Oasis", "oasis", base == D and "Hill" not in t["f"])):
                    if ok and veg < b[key]:
                        t["f"].append(feat)
                        break
                    veg -= b[key]
                if rng.random() < b["blight"] and "Marsh" not in t["f"]:
                    t["f"].append("Blighted Land")
                for key, feat in (("ancient", "Ancient Woods"), ("bamboo", "Bamboo Grove"),
                                  ("crystal", "Crystal Grove")):
                    if "Forest" in t["f"] and rng2.random() < b[key]:
                        t["f"] = [feat if f == "Forest" else f for f in t["f"]]
                VEG = ("Forest", "Jungle", "Marsh", "Ancient Woods", "Bamboo Grove", "Crystal Grove")
                for key, feat, bases in (("fel", "Fel-Scorched Land", (G, P, D, T)),
                                         ("plague", "Plagued Land", (G, P, T, S)),
                                         ("molten", "Molten Fields", (D, P, T)),
                                         ("titan", "Titan Ruins", (G, P, D, T, S))):
                    if base in bases and rng2.random() < b[key] and "Blighted Land" not in t["f"]:
                        if key in ("fel", "plague"):
                            t["f"] = [f for f in t["f"] if f not in VEG]
                        elif any(f in VEG for f in t["f"]) or "Oasis" in t["f"]:
                            continue
                        t["f"].append(feat)
                        break
            tiles[r][c] = t

    ridge_width = 0.6 * max(1.0, k * 0.85)
    for line, chance in ridges:
        for r in range(height):
            for c in range(width):
                if land(c, r) and any(seg_dist(center(c, r), line[i], line[i + 1]) < ridge_width
                                      for i in range(len(line) - 1)) and rng.random() < chance:
                    tiles[r][c] = {"t": "Mountain", "f": []}
    for (cx, cy), rad, chance in rings:
        for r in range(height):
            for c in range(width):
                d = math.hypot(center(c, r)[0] - cx, center(c, r)[1] - cy)
                if land(c, r) and abs(d - rad) < 0.7 * max(1.0, k * 0.8) and rng.random() < chance:
                    tiles[r][c] = {"t": "Mountain", "f": []}
    for lake in LAKES_:
        c, r = snap(S(lake))
        tiles[r][c] = {"t": "Lakes", "f": []}
        if k > 1.2:                                       # bigger maps get bigger lakes
            for nc, nr in nb(c, r)[:2]:
                if land(nc, nr):
                    tiles[nr][nc] = {"t": "Lakes", "f": []}

    # Polar ice along the top edge
    for c in range(width if sp.get("ice", True) else 0):
        for r in range(0, 2):
            if not land(c, r) and rng.random() < (0.85 if r == 0 else 0.4):
                tiles[r][c] = {"t": "Ocean", "f": ["Ice"]}

    # capitals and city-states, scaled and snapped onto land
    capitals, city_states, taken = {}, {}, set()
    for src, dst in ((CAPS_, capitals), (CS_, city_states)):
        for name, pt in src.items():
            if k == 1 and not sp:
                assert land(*pt), f"{name} at {pt} is in the sea"
                pos = pt
            else:
                pos = snap(S(pt), avoid=taken)
            dst[name] = pos
            taken.add(pos)

    # settle-able ground for every capital and city-state; no mountains right beside them
    for name, (c, r) in {**capitals, **city_states}.items():
        z = grid[r][c]
        base = tiles[r][c]["t"]
        if base in ("Mountain", "Lakes", "Ocean", "Coast"):
            base = max(zones[z][2]["base"], key=zones[z][2]["base"].get)
        if base == "Snow":
            base = "Tundra"
        keep_hill = ["Hill"] if "Hill" in tiles[r][c]["f"] else []
        tiles[r][c] = {"t": base, "f": keep_hill}
        for nc, nr in nb(c, r):
            if tiles[nr][nc]["t"] in ("Mountain", "Lakes") and land(nc, nr):
                b = zones[grid[nr][nc]][2]["base"]
                tiles[nr][nc] = {"t": max(b, key=b.get), "f": ["Hill"]}
            tiles[nr][nc]["f"] = [f for f in tiles[nr][nc]["f"] if f not in HARMFUL]
        tiles[r][c]["f"] = [f for f in tiles[r][c]["f"] if f not in HARMFUL]
        if name == "Scourge":   # the Lich King's capital starts amid the blight it needs
            k_ = 0
            for nc, nr in nb(c, r):
                t_ = tiles[nr][nc]
                if t_["t"] in ("Snow", "Tundra", "Plains", "Grassland") and all(f == "Hill" for f in t_["f"]) and k_ < 3:
                    t_["f"] = t_["f"] + ["Plagued Land"]
                    k_ += 1

    wonders = {}
    for name, pt in NW_.items():
        water = name in ("The Maelstrom", "Kelp'thar Forest")
        c, r = snap(S(pt), want_land=not water, avoid=taken)
        assert land(c, r) != water, name
        wonders[name] = (c, r)
        taken.add((c, r))
        if water:
            tiles[r][c] = {"t": "Ocean", "f": [], "nw": name}
            if name == "Kelp'thar Forest":           # occurs as a pair of tiles
                tiles[r + 1][c] = {"t": "Ocean", "f": [], "nw": name}
        else:
            tiles[r][c] = {"t": NWB_.get(name, "Plains"), "f": [], "nw": name}

    return dict(width=width, height=height, tiles=tiles, zones=grid,
                capitals=capitals, cityStates=city_states, wonders=wonders)


# ------------------------------------------------------------------ regional maps (Oct 2026)
# Each region is a window on the world map above: only landmasses wholly inside the window are
# kept, coordinates are shifted, and factions with a lore foothold there get extra starts
# (Unciv places any other chosen faction on its own).
REGIONS = {
    "Kalimdor": dict(box=(1, 11, 48, 64), ice=False,
                     lands=["Kalimdor", "Teldrassil", "Bloodmyst Isle", "Azuremyst Isle", "Echo Isles", "Theramore Isle",
                            "Sardor Isle", "Zandalar"],
                     starts={"Kul Tirans": (34, 42),       # Jaina's Theramore
                             "Humans": (29, 45)},          # Northwatch Hold, Southern Barrens
                     drop=["Theramore"]),
    "Eastern Kingdoms": dict(box=(54, 1, 98, 64),
                             lands=["Eastern Kingdoms", "Isle of Quel'Danas", "Tol Barad", "Kul Tiras", "Kezan", "Isle of Thunder"],
                             starts={"Orcs": (74, 56),        # Grom'gol Base Camp, Stranglethorn
                                     "Trolls": (95, 15),      # Zul'Aman, Ghostlands
                                     "Scourge": (90, 17),     # Stratholme, Eastern Plaguelands
                                     "Goblins": (56.5, 41)}),  # Kezan
    "Northrend": dict(box=(36, 0, 69, 20),
                      lands=["Northrend"],
                      starts={"Humans": (41, 16),             # Valiance Keep, Borean Tundra
                              "Orcs": (45, 16),               # Warsong Hold
                              "Tauren": (51, 15),             # Taunka'le, Dragonblight
                              "Trolls": (58, 9),              # Zul'Drak
                              "Dwarves": (62, 16),            # Valgarde, Howling Fjord
                              "Forsaken": (66, 13)}),         # Vengeance Landing
}


def region_spec(name):
    reg = REGIONS[name]
    x0, y0, x1, y1 = reg["box"]
    pad = 2
    inside = lambda p: x0 <= p[0] <= x1 and y0 <= p[1] <= y1
    sh = lambda p: (p[0] - x0 + pad, p[1] - y0 + pad)
    lands = {n: [sh(p) for p in poly] for n, poly in LAND.items() if n in reg["lands"]}
    for n in reg["lands"]:
        assert all(inside(p) for p in LAND[n]), (name, n)
    zones = {z: (lm, [sh(p) for p in seeds], b) for z, (lm, seeds, b) in ZONES.items() if lm in lands}
    caps = {n: sh(p) for n, p in CAPITALS.items() if inside(p) and n not in reg["starts"]}
    caps.update({n: sh(p) for n, p in reg["starts"].items()})
    return dict(W=x1 - x0 + 2 * pad, H=y1 - y0 + 2 * pad, LAND=lands, ZONES=zones, ice=reg.get("ice", True),
                RIDGES=[([sh(p) for p in line], ch) for line, ch in RIDGES if all(inside(p) for p in line)],
                RINGS=[(sh(c), r, ch) for c, r, ch in RINGS if inside(c)],
                LAKES=[sh(p) for p in LAKES if inside(p)],
                NATURAL_WONDERS={n: sh(p) for n, p in NATURAL_WONDERS.items() if inside(p)},
                NW_BASE=NW_BASE, CAPITALS=caps,
                CITY_STATES={n: sh(p) for n, p in CITY_STATES.items() if inside(p) and n not in reg.get("drop", [])})


# Pandaria, a continent of its own (authored on a 60 x 44 grid)
PANDARIA = dict(
    W=60, H=44, ice=False,
    LAND={"Pandaria": [(14, 6), (22, 4), (32, 5), (40, 7), (46, 10), (50, 15), (52, 21), (51, 27), (48, 32), (44, 36), (38, 39),
                       (30, 40), (22, 39), (16, 36), (11, 31), (8, 25), (8, 18), (10, 11)],
          "Timeless Isle": [(53, 34.5), (56.5, 34.5), (57, 38), (53.5, 38.5)],
          "Isle of Giants": [(52, 3.5), (56, 3.5), (57, 7.5), (53, 8.5)],
          "Isle of Thunder": [(3.5, 3.5), (9, 3), (10, 8), (4.5, 8.5)]},
    ZONES={"Kun-Lai Summit": ("Pandaria", [(28, 9), (36, 10)], B({S: .45, T: .55}, hill=.35, mountain=.12, forest=.1)),
           "Townlong Steppes": ("Pandaria", [(15, 11), (17, 17)], B({P: .6, T: .4}, hill=.2, forest=.1)),
           "Dread Wastes": ("Pandaria", [(13, 26), (18, 31)], B({D: .5, P: .5}, hill=.15, marsh=.1, crystal=.5, forest=.08)),
           "Krasarang Wilds": ("Pandaria", [(26, 35), (34, 35)], B({G: 1}, jungle=.45, hill=.1, bamboo=.3)),
           "Valley of the Four Winds": ("Pandaria", [(28, 28), (36, 29)], B({G: .7, P: .3}, forest=.06, hill=.06)),
           "The Jade Forest": ("Pandaria", [(44, 18), (45, 26), (40, 32)], B({G: 1}, forest=.6, hill=.15, bamboo=.6)),
           "Vale of Eternal Blossoms": ("Pandaria", [(30, 20)], B({G: 1}, forest=.25, ancient=.6)),
           "The Veiled Stair": ("Pandaria", [(38, 16)], B({G: .5, P: .5}, hill=.5, mountain=.1, bamboo=.4, forest=.2)),
           "Timeless Isle": ("Timeless Isle", [(55, 36)], B({G: 1}, forest=.35, hill=.2, ancient=.5)),
           "Isle of Giants": ("Isle of Giants", [(54, 6)], B({G: 1}, jungle=.5, hill=.3)),
           "Isle of Thunder": ("Isle of Thunder", [(6, 6)], B({G: 1}, jungle=.3, hill=.3))},
    RIDGES=[([(22, 12), (30, 13), (38, 13)], .7),            # the Kun-Lai range
            ([(21, 18), (22, 25), (20, 32)], .85)],          # the Serpent's Spine
    RINGS=[], LAKES=[(31, 21)], NATURAL_WONDERS={}, NW_BASE={},
    CAPITALS={"Pandaren": (32, 28),        # Halfhill, Valley of the Four Winds
              "Humans": (37, 37),          # Lion's Landing, Krasarang
              "Orcs": (24, 37),            # Domination Point, Krasarang
              "Dwarves": (45, 30),         # Paw'don Village, Jade Forest
              "Trolls": (46, 14)},         # Honeydew Village, Jade Forest
    CITY_STATES={"Mogu'shan": (6, 6)},
)


def spec_for(name):
    if name == "Pandaria":
        return PANDARIA
    return region_spec(name) if name in REGIONS else None


def write_tiles_txt(m, path):
    """Plain-text tile list for the Java map builder: col row base features|... wonder"""
    with open(path, "w", encoding="utf-8") as f:
        for r in range(m["height"]):
            for c in range(m["width"]):
                t = m["tiles"][r][c]
                f.write("\t".join(["T", str(c), str(r), t["t"], "|".join(t["f"]), t.get("nw", "")]) + "\n")
        for n, (c, r) in {**m["capitals"], **m["cityStates"]}.items():
            f.write("\t".join(["S", str(c), str(r), n]) + "\n")


if __name__ == "__main__":
    import sys
    width, height = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (W, H)
    m = build(width=width, height=height, spec=spec_for(sys.argv[5]) if len(sys.argv) > 5 else None)
    json.dump(m, open(sys.argv[1], "w"))
    if len(sys.argv) > 2:
        write_tiles_txt(m, sys.argv[2])
    land = sum(1 for row in m["zones"] for z in row if z)
    print("land tiles:", land, "of", width * height)
