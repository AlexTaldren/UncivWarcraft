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
}

# ------------------------------------------------------------------ zones
# name: (landmass, [seed points], biome)
# biome: base terrain weights, then chances for Forest / Jungle / Marsh / Hill / Mountain / Blight / Oasis
def B(base, forest=0, jungle=0, marsh=0, hill=0, mountain=0, blight=0, oasis=0):
    return dict(base=base, forest=forest, jungle=jungle, marsh=marsh, hill=hill,
                mountain=mountain, blight=blight, oasis=oasis)

G, P, T, D, S = "Grassland", "Plains", "Tundra", "Desert", "Snow"

ZONES = {
    # --- Kalimdor
    "Teldrassil": ("Teldrassil", [(9, 17)], B({G: 1}, forest=.75)),
    "Bloodmyst Isle": ("Bloodmyst Isle", [(5, 22)], B({P: 1}, forest=.4, marsh=.15)),
    "Azuremyst Isle": ("Azuremyst Isle", [(5, 28)], B({G: 1}, forest=.45, hill=.1)),
    "Darkshore": ("Kalimdor", [(14, 21), (13, 26)], B({G: .7, P: .3}, forest=.65, hill=.1)),
    "Moonglade": ("Kalimdor", [(20, 17)], B({G: 1}, forest=.35)),
    "Winterspring": ("Kalimdor", [(25, 16), (30, 18)], B({S: .45, T: .55}, forest=.3, hill=.25, mountain=.06)),
    "Felwood": ("Kalimdor", [(19, 21), (18, 24)], B({P: .6, G: .4}, forest=.65, marsh=.15, blight=.15)),
    "Mount Hyjal": ("Kalimdor", [(27, 22)], B({G: .7, T: .3}, forest=.55, hill=.3, mountain=.18)),
    "Azshara": ("Kalimdor", [(33, 22), (35, 25)], B({G: .6, P: .4}, forest=.4, hill=.2)),
    "Ashenvale": ("Kalimdor", [(19, 28), (25, 27)], B({G: 1}, forest=.8, hill=.08)),
    "Stonetalon Mountains": ("Kalimdor", [(15, 31), (14, 35)], B({P: .6, T: .4}, forest=.2, hill=.4, mountain=.25)),
    "Durotar": ("Kalimdor", [(32, 30), (32, 33)], B({P: .75, D: .25}, hill=.2, forest=.05)),
    "Northern Barrens": ("Kalimdor", [(26, 32), (29, 35)], B({P: .9, G: .1}, forest=.04, hill=.1)),
    "Desolace": ("Kalimdor", [(13, 39), (12, 43)], B({D: .7, P: .3}, hill=.2, mountain=.05)),
    "Mulgore": ("Kalimdor", [(19, 38)], B({G: .6, P: .4}, hill=.15)),
    "Southern Barrens": ("Kalimdor", [(24, 40), (28, 39)], B({P: 1}, hill=.15, forest=.05)),
    "Dustwallow Marsh": ("Kalimdor", [(30, 42), (30, 45)], B({G: 1}, marsh=.6, forest=.15)),
    "Feralas": ("Kalimdor", [(12, 48), (15, 51)], B({G: 1}, jungle=.5, forest=.25, hill=.1)),
    "Thousand Needles": ("Kalimdor", [(21, 45), (26, 46)], B({D: .5, P: .5}, hill=.3, mountain=.18)),
    "Tanaris": ("Kalimdor", [(28, 50), (30, 53)], B({D: 1}, hill=.15, oasis=.05)),
    "Un'Goro Crater": ("Kalimdor", [(22, 51)], B({G: 1}, jungle=.7, hill=.2)),
    "Silithus": ("Kalimdor", [(16, 54), (19, 57)], B({D: 1}, hill=.15)),
    "Uldum": ("Kalimdor", [(24, 58), (27, 58)], B({D: 1}, oasis=.1, hill=.05)),
    "Echo Isles": ("Echo Isles", [(36, 35)], B({P: 1}, jungle=.3)),
    "Theramore Isle": ("Theramore Isle", [(34, 42)], B({G: 1}, marsh=.2)),
    "Sardor Isle": ("Sardor Isle", [(6, 46)], B({G: 1}, forest=.5)),
    # --- Eastern Kingdoms
    "Isle of Quel'Danas": ("Isle of Quel'Danas", [(88, 5)], B({G: 1}, forest=.35)),
    "Eversong Woods": ("Eastern Kingdoms", [(87, 12), (92, 12)], B({G: 1}, forest=.6)),
    "Ghostlands": ("Eastern Kingdoms", [(92, 16)], B({P: .6, G: .4}, forest=.5, marsh=.1, blight=.1)),
    "Eastern Plaguelands": ("Eastern Kingdoms", [(90, 20), (94, 22)], B({P: .7, T: .3}, forest=.2, hill=.15, blight=.3)),
    "Western Plaguelands": ("Eastern Kingdoms", [(85, 20)], B({P: 1}, forest=.1, hill=.1, blight=.2)),
    "Tirisfal Glades": ("Eastern Kingdoms", [(77, 17), (81, 15)], B({G: .7, P: .3}, forest=.4, marsh=.2)),
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
    "Badlands": ("Eastern Kingdoms", [(88, 45)], B({D: 1}, hill=.4, mountain=.15)),
    "Searing Gorge": ("Eastern Kingdoms", [(81, 45)], B({D: .5, P: .5}, hill=.4, mountain=.2)),
    "Burning Steppes": ("Eastern Kingdoms", [(83, 48)], B({D: .6, P: .4}, hill=.4)),
    "Elwynn Forest": ("Eastern Kingdoms", [(77, 50)], B({G: 1}, forest=.4)),
    "Redridge Mountains": ("Eastern Kingdoms", [(87, 50)], B({P: .5, G: .5}, hill=.5, mountain=.2)),
    "Westfall": ("Eastern Kingdoms", [(74, 54)], B({P: 1}, hill=.05)),
    "Duskwood": ("Eastern Kingdoms", [(78, 55)], B({G: 1}, forest=.8)),
    "Deadwind Pass": ("Eastern Kingdoms", [(82, 55)], B({T: .5, P: .5}, hill=.4, mountain=.5)),
    "Swamp of Sorrows": ("Eastern Kingdoms", [(88, 53)], B({G: 1}, marsh=.7, jungle=.2)),
    "Blasted Lands": ("Eastern Kingdoms", [(89, 57)], B({D: 1}, hill=.25, blight=.2)),
    "Stranglethorn Vale": ("Eastern Kingdoms", [(77, 59), (78, 61)], B({G: 1}, jungle=.8, hill=.2)),
    "Tol Barad": ("Tol Barad", [(72, 35)], B({P: 1}, hill=.3)),
    # --- Northrend
    "Borean Tundra": ("Northrend", [(41, 15), (39, 12)], B({T: 1}, forest=.1, marsh=.1, hill=.1)),
    "Sholazar Basin": ("Northrend", [(40, 7)], B({G: 1}, jungle=.7)),
    "Icecrown": ("Northrend", [(46, 5), (51, 4)], B({S: 1}, hill=.3, mountain=.25)),
    "Wintergrasp": ("Northrend", [(46, 10)], B({S: .5, T: .5}, hill=.3)),
    "Dragonblight": ("Northrend", [(50, 13), (54, 13)], B({S: .7, T: .3}, hill=.15)),
    "Crystalsong Forest": ("Northrend", [(55, 8)], B({T: 1}, forest=.7)),
    "The Storm Peaks": ("Northrend", [(59, 4), (63, 5)], B({S: 1}, mountain=.5, hill=.3)),
    "Zul'Drak": ("Northrend", [(62, 10)], B({T: .6, S: .4}, hill=.3)),
    "Grizzly Hills": ("Northrend", [(63, 14)], B({T: 1}, forest=.7, hill=.25)),
    "Howling Fjord": ("Northrend", [(66, 16), (60, 17)], B({T: 1}, forest=.4, hill=.3, mountain=.1)),
    # --- South Seas
    "Kezan": ("Kezan", [(57, 41)], B({G: 1}, jungle=.5)),
    "The Lost Isles": ("The Lost Isles", [(48, 41)], B({P: 1}, jungle=.5, hill=.2)),
    "The Wandering Isle": ("The Wandering Isle", [(51, 52)], B({G: 1}, forest=.4, hill=.2)),
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
}

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
    "Argent Vanguard": (50, 6),    # Icecrown
    "Feathermoon Stronghold": (6, 46),        # Sardor Isle, Feralas
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
def build(seed=7, width=W, height=H):
    """Build the map at any size. All coordinates above are authored on the 104 x 64
    grid and scaled here, so a larger map keeps the same shape and placements."""
    sx, sy = width / W, height / H
    k = (sx + sy) / 2
    S = lambda p: (p[0] * sx, p[1] * sy)
    land_polys = {n: [S(p) for p in poly] for n, poly in LAND.items()}
    zones = {z: (lm, [S(p) for p in seeds], b) for z, (lm, seeds, b) in ZONES.items()}
    ridges = [([S(p) for p in line], ch) for line, ch in RIDGES]
    rings = [(S(c), rad * k, ch) for c, rad, ch in RINGS]
    nb = lambda c, r: neighbors(c, r, width, height)
    rng = random.Random(seed)

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
    for lake in LAKES:
        c, r = snap(S(lake))
        tiles[r][c] = {"t": "Lakes", "f": []}
        if k > 1.2:                                       # bigger maps get bigger lakes
            for nc, nr in nb(c, r)[:2]:
                if land(nc, nr):
                    tiles[nr][nc] = {"t": "Lakes", "f": []}

    # Polar ice along the top edge
    for c in range(width):
        for r in range(0, 2):
            if not land(c, r) and rng.random() < (0.85 if r == 0 else 0.4):
                tiles[r][c] = {"t": "Ocean", "f": ["Ice"]}

    # capitals and city-states, scaled and snapped onto land
    capitals, city_states, taken = {}, {}, set()
    for src, dst in ((CAPITALS, capitals), (CITY_STATES, city_states)):
        for name, pt in src.items():
            if k == 1:
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
            tiles[nr][nc]["f"] = [f for f in tiles[nr][nc]["f"] if f != "Blighted Land"]

    wonders = {}
    for name, pt in NATURAL_WONDERS.items():
        water = name in ("The Maelstrom", "Kelp'thar Forest")
        c, r = pt if k == 1 else snap(S(pt), want_land=not water, avoid=taken)
        assert land(c, r) != water, name
        wonders[name] = (c, r)
        taken.add((c, r))
        if water:
            tiles[r][c] = {"t": "Ocean", "f": [], "nw": name}
            if name == "Kelp'thar Forest":           # occurs as a pair of tiles
                tiles[r + 1][c] = {"t": "Ocean", "f": [], "nw": name}
        else:
            tiles[r][c] = {"t": "Plains" if name != "Un'Goro Crater" else "Desert", "f": [], "nw": name}

    return dict(width=width, height=height, tiles=tiles, zones=grid,
                capitals=capitals, cityStates=city_states, wonders=wonders)


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
    m = build(width=width, height=height)
    json.dump(m, open(sys.argv[1], "w"))
    if len(sys.argv) > 2:
        write_tiles_txt(m, sys.argv[2])
    land = sum(1 for row in m["zones"] for z in row if z)
    print("land tiles:", land, "of", width * height)
