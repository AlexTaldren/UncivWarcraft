"""The Azeroth world map: Kalimdor, the Eastern Kingdoms, Northrend, Pandaria, the Broken Isles,
Kul Tiras and Zandalar, laid out as on Blizzard's in-game world map.

Land and zones come from azeroth_world.png, a low-resolution zone raster traced from the in-game
world and continent maps (each pixel holds a zone index from azeroth_world.json, 255 = lake; no
map art is shipped). Every other coordinate here is authored on a 180 x 110 grid that covers the
whole raster: x to the east, y to the south (row 0 is the northern edge). Any map size or regional
window is sampled from the raster, so all maps share one geography. Each land tile takes its
zone's terrain mix; mountain ranges, natural wonders, capitals and city-states are then placed at
their real locations.
"""
import json, math, os, random
from collections import Counter

W, H = 180, 110                        # authoring grid (= the Azeroth Huge map, tile for tile)
HERE = os.path.dirname(os.path.abspath(__file__))


def _load_raster():
    from PIL import Image
    img = Image.open(os.path.join(HERE, "azeroth_world.png"))
    meta = json.load(open(os.path.join(HERE, "azeroth_world.json")))
    return img.size, img.tobytes(), meta["names"], meta["lake"]


# ------------------------------------------------------------------ zone biomes
def B(base, forest=0, jungle=0, marsh=0, hill=0, mountain=0, blight=0, oasis=0,
      fel=0, plague=0, ancient=0, bamboo=0, molten=0, crystal=0, titan=0):
    """Zone biome. forest..oasis: chance per tile. fel/plague/molten/titan: chance per
    tile (fel and plague overrun vegetation). ancient/bamboo/crystal: share of the
    zone's forests that are that kind of forest instead."""
    return dict(base=base, forest=forest, jungle=jungle, marsh=marsh, hill=hill,
                mountain=mountain, blight=blight, oasis=oasis, fel=fel, plague=plague,
                ancient=ancient, bamboo=bamboo, molten=molten, crystal=crystal, titan=titan)


G, P, T, D, S = "Grassland", "Plains", "Tundra", "Desert", "Snow"

BIOMES = {
    # --- Kalimdor
    "Teldrassil": B({G: 1}, forest=.75, ancient=.6),
    "Bloodmyst Isle": B({P: 1}, forest=.4, marsh=.15, crystal=.2),
    "Azuremyst Isle": B({G: 1}, forest=.45, hill=.1, crystal=.25),
    "Darkshore": B({G: .7, P: .3}, forest=.65, hill=.1, ancient=.4),
    "Moonglade": B({G: 1}, forest=.35, ancient=.5),
    "Winterspring": B({S: .45, T: .55}, forest=.3, hill=.25, mountain=.06),
    "Felwood": B({P: .6, G: .4}, forest=.65, marsh=.15, fel=.3),
    "Mount Hyjal": B({G: .7, T: .3}, forest=.55, hill=.3, mountain=.18, ancient=.4),
    "Azshara": B({G: .6, P: .4}, forest=.4, hill=.2, ancient=.2),
    "Ashenvale": B({G: 1}, forest=.8, hill=.08, ancient=.6),
    "Stonetalon Mountains": B({P: .6, T: .4}, forest=.2, hill=.4, mountain=.25),
    "Durotar": B({P: .75, D: .25}, hill=.2, forest=.05),
    "Northern Barrens": B({P: .9, G: .1}, forest=.04, hill=.1),
    "Desolace": B({D: .7, P: .3}, hill=.2, mountain=.05),
    "Mulgore": B({G: .6, P: .4}, hill=.15),
    "Southern Barrens": B({P: 1}, hill=.15, forest=.05),
    "Dustwallow Marsh": B({G: 1}, marsh=.6, forest=.15),
    "Feralas": B({G: 1}, jungle=.5, forest=.25, hill=.1, ancient=.3),
    "Thousand Needles": B({D: .5, P: .5}, hill=.3, mountain=.18),
    "Tanaris": B({D: 1}, hill=.15, oasis=.05, titan=.02),
    "Un'Goro Crater": B({G: 1}, jungle=.7, hill=.2, molten=.04),
    "Silithus": B({D: 1}, hill=.15),
    "Ahn'Qiraj: The Fallen Kingdom": B({D: 1}, hill=.2, titan=.04),
    "Uldum": B({D: 1}, oasis=.1, hill=.05, titan=.08),
    "Echo Isles": B({P: 1}, jungle=.3),
    "Theramore Isle": B({G: 1}, marsh=.2),
    "Sardor Isle": B({G: 1}, forest=.5),
    # --- Eastern Kingdoms
    "Isle of Quel'Danas": B({G: 1}, forest=.35),
    "Eversong Woods": B({G: 1}, forest=.6),
    "Ghostlands": B({P: .6, G: .4}, forest=.5, marsh=.1, plague=.15),
    "Eastern Plaguelands": B({P: .7, T: .3}, forest=.2, hill=.15, plague=.35),
    "Western Plaguelands": B({P: 1}, forest=.1, hill=.1, plague=.25),
    "Tirisfal Glades": B({G: .7, P: .3}, forest=.4, marsh=.2, plague=.05),
    "Silverpine Forest": B({T: .5, P: .5}, forest=.7, hill=.2),
    "Gilneas": B({G: .5, P: .5}, forest=.5, hill=.2),
    "Hillsbrad Foothills": B({G: 1}, forest=.2, hill=.2),
    "Alterac Mountains": B({S: .5, T: .5}, hill=.4, mountain=.4),
    "The Hinterlands": B({G: 1}, forest=.4, hill=.4),
    "Arathi Highlands": B({G: .6, P: .4}, hill=.3),
    "Wetlands": B({G: 1}, marsh=.5, hill=.15),
    "Twilight Highlands": B({P: .5, G: .5}, hill=.4, mountain=.15),
    "Dun Morogh": B({S: .25, T: .75}, hill=.35, mountain=.1, forest=.2),
    "Loch Modan": B({G: .5, P: .5}, hill=.3),
    "Badlands": B({D: 1}, hill=.4, mountain=.15, titan=.08),
    "Searing Gorge": B({D: .5, P: .5}, hill=.4, mountain=.2, molten=.35),
    "Burning Steppes": B({D: .6, P: .4}, hill=.4, molten=.45),
    "Elwynn Forest": B({G: 1}, forest=.4),
    "Redridge Mountains": B({P: .5, G: .5}, hill=.5, mountain=.2),
    "Westfall": B({P: 1}, hill=.05),
    "Duskwood": B({G: 1}, forest=.8),
    "Deadwind Pass": B({T: .5, P: .5}, hill=.4, mountain=.5),
    "Swamp of Sorrows": B({G: 1}, marsh=.7, jungle=.2),
    "Blasted Lands": B({D: 1}, hill=.25, fel=.4),
    "Stranglethorn Vale": B({G: 1}, jungle=.8, hill=.2),
    "Tol Barad": B({P: 1}, hill=.3),
    # --- Northrend
    "Borean Tundra": B({T: 1}, forest=.1, marsh=.1, hill=.1),
    "Sholazar Basin": B({G: 1}, jungle=.7, titan=.05),
    "Icecrown": B({S: 1}, hill=.3, mountain=.25, plague=.15),
    "Wintergrasp": B({S: .5, T: .5}, hill=.3),
    "Dragonblight": B({S: .7, T: .3}, hill=.15, plague=.08),
    "Crystalsong Forest": B({T: 1}, forest=.7, crystal=.6),
    "The Storm Peaks": B({S: 1}, mountain=.5, hill=.3, titan=.07),
    "Zul'Drak": B({T: .6, S: .4}, hill=.3, plague=.08),
    "Grizzly Hills": B({T: 1}, forest=.7, hill=.25),
    "Howling Fjord": B({T: 1}, forest=.4, hill=.3, mountain=.1),
    # --- Pandaria
    "Kun-Lai Summit": B({S: .45, T: .55}, hill=.35, mountain=.12, forest=.1),
    "Townlong Steppes": B({P: .6, T: .4}, hill=.2, forest=.1),
    "Dread Wastes": B({D: .5, P: .5}, hill=.15, marsh=.1, crystal=.5, forest=.08),
    "Krasarang Wilds": B({G: 1}, jungle=.45, hill=.1, bamboo=.3),
    "Valley of the Four Winds": B({G: .7, P: .3}, forest=.06, hill=.06),
    "The Jade Forest": B({G: 1}, forest=.6, hill=.15, bamboo=.6),
    "Vale of Eternal Blossoms": B({G: 1}, forest=.25, ancient=.6),
    "The Veiled Stair": B({G: .5, P: .5}, hill=.5, mountain=.1, bamboo=.4, forest=.2),
    "Timeless Isle": B({G: 1}, forest=.35, hill=.2, ancient=.5),
    "Isle of Giants": B({G: 1}, jungle=.5, hill=.3),
    "Isle of Thunder": B({G: 1}, jungle=.3, hill=.3),
    # --- the Broken Isles
    "Azsuna": B({G: .6, P: .4}, forest=.35, hill=.15, ancient=.25),
    "Val'sharah": B({G: 1}, forest=.75, ancient=.6),
    "Highmountain": B({T: .6, G: .4}, hill=.4, mountain=.25, forest=.25),
    "Stormheim": B({T: .6, S: .4}, hill=.35, mountain=.15, forest=.15),
    "Suramar": B({G: .7, P: .3}, forest=.45, hill=.1, ancient=.35, titan=.03),
    "The Broken Shore": B({P: .7, D: .3}, hill=.25, fel=.4),
    "Eye of Azshara": B({P: 1}, hill=.25),
    # --- Kul Tiras and Zandalar
    "Tiragarde Sound": B({G: .6, P: .4}, forest=.3, hill=.2),
    "Drustvar": B({T: .5, G: .5}, forest=.7, hill=.25),
    "Stormsong Valley": B({G: .7, P: .3}, forest=.25, hill=.25),
    "Zuldazar": B({G: 1}, jungle=.55, hill=.3),
    "Nazmir": B({G: 1}, marsh=.55, jungle=.3),
    "Vol'dun": B({D: 1}, hill=.2, oasis=.05),
    # --- the South Seas (small hand-placed isles, see EXTRA_LAND)
    "Kezan": B({G: 1}, jungle=.5),
    "The Lost Isles": B({P: 1}, jungle=.5, hill=.2),
    "The Wandering Isle": B({G: 1}, forest=.4, hill=.2, bamboo=.9),
}

_K = list(BIOMES)
_span = lambda a, b: _K[_K.index(a):_K.index(b) + 1]
CONTINENTS = {"Kalimdor": _span("Teldrassil", "Sardor Isle"), "Eastern Kingdoms": _span("Isle of Quel'Danas", "Tol Barad"),
              "Northrend": _span("Borean Tundra", "Howling Fjord"), "Pandaria": _span("Kun-Lai Summit", "Isle of Thunder"),
              "Broken Isles": _span("Azsuna", "Eye of Azshara"), "Kul Tiras": _span("Tiragarde Sound", "Stormsong Valley"),
              "Zandalar": _span("Zuldazar", "Vol'dun"), "South Seas": _span("Kezan", "The Wandering Isle")}

# Isles too small or too far off for the reference maps: (center, radius) on the 180 x 110 grid
EXTRA_LAND = {
    "The Lost Isles": ((74.0, 61.5), 2.0),
    "Kezan": ((84.5, 52.5), 2.2),
    "The Wandering Isle": ((59.5, 97.5), 2.4),
}

# ------------------------------------------------------------------ mountain ranges & lakes
RIDGES = [  # (polyline, chance a tile on the line becomes Mountain)
    ([(26.1, 50.6), (27.5, 55.6), (26.3, 58.7)], .8),     # Stonetalon spine
    ([(33.4, 58.4), (33.0, 61.9)], .7),                   # Mulgore escarpment
    ([(29.5, 67.6), (29.0, 73.2)], .7),                   # Feralas / Needles divide
    ([(145.1, 54.4), (147.5, 54.9), (149.8, 55.6)], .9),  # Greymane Wall
    ([(150.9, 63.7), (156.0, 63.2)], .8),                 # Khaz Modan ridge
    ([(152.0, 71.7), (162.3, 70.8)], .55),                # Burning Steppes / Elwynn / Redridge
    ([(149.9, 80.9), (157.1, 80.2)], .4),                 # Duskwood / Stranglethorn
    ([(162.3, 77.6), (167.4, 77.1)], .6),                 # Swamp of Sorrows / Blasted Lands
    ([(74.3, 11.7), (76.3, 17.2)], .8),                   # Sholazar rim
    ([(76.3, 87.8), (80.7, 88.2), (84.8, 87.7)], .7),     # the Kun-Lai range
    ([(77.8, 91.7), (80.9, 96.2), (82.4, 100.8)], .85),    # the Serpent's Spine
    ([(103.1, 37.8), (105.6, 42.6)], .6),                 # Highmountain peaks
]
RINGS = [((31.7, 76.3), 3.4, .7)]                         # Un'Goro crater rim
LAKES = [(160.2, 62.7), (162.3, 73.6), (159.0, 40.7), (33.2, 39.0), (84.1, 93.2)]
# Loch Modan, Lake Everstill, Brightwater, Lake Elune'ara, the Vale's pools (Lordamere is in the raster)

# ------------------------------------------------------------------ landmarks
NATURAL_WONDERS = {
    "The Maelstrom": (79.9, 53.5),
    "Mount Hyjal": (39.6, 44.4),
    "Teldrassil": (23.5, 33.9),
    "Moonglade": (34.1, 38.7),
    "Lake Elune'ara": (33.2, 39.5),
    "Stonetalon Peak": (25.8, 52.8),
    "Red Rocks of Mulgore": (30.8, 63.4),
    "Thousand Needles": (33.8, 71.0),
    "Un'Goro Crater": (31.7, 76.3),
    "Lakkari Tar Pits": (30.6, 77.4),
    "Lost City of the Tol'vir": (33.8, 86.1),
    "Blackrock Mountain": (157.1, 70.2),
    "Cape of Stranglethorn": (152.0, 86.9),
    "Kelp'thar Forest": (142.0, 71.0),     # the sunken kingdom of Vashj'ir
    "The Dark Portal": (166.4, 80.2),      # Blasted Lands
    "The Nexus": (69.0, 20.3),             # Coldarra, Borean Tundra
    "Galakrond's Rest": (89.6, 22.2),      # Dragonblight
    "Sunken Temple": (165.3, 75.3),        # Swamp of Sorrows
    "Maraudon": (22.8, 63.3),              # Desolace
    "The Lifeblood Pillar": (72.4, 13.2),  # Sholazar Basin
}
NW_BASE = {"Un'Goro Crater": "Desert", "The Dark Portal": "Desert", "The Nexus": "Snow",
           "Galakrond's Rest": "Snow", "Sunken Temple": "Grassland", "Maraudon": "Desert",
           "The Lifeblood Pillar": "Grassland"}
WATER_WONDERS = ("The Maelstrom", "Kelp'thar Forest")
HARMFUL = {"Blighted Land", "Fel-Scorched Land", "Plagued Land", "Molten Fields"}

CAPITALS = {  # major nations -> their capital's tile
    "Humans": (152.0, 73.7),          # Stormwind, Elwynn Forest
    "Orcs": (43.8, 54.6),             # Orgrimmar, Durotar
    "Night Elves": (22.4, 35.8),      # Darnassus, Teldrassil
    "Dwarves": (156.0, 65.1),         # Ironforge, Dun Morogh
    "Gnomes": (152.0, 66.6),          # Gnomeregan, Dun Morogh
    "Tauren": (30.1, 60.9),           # Thunder Bluff, Mulgore
    "Trolls": (45.3, 60.3),           # Sen'jin Village, Durotar
    "Blood Elves": (167.1, 33.8),     # Silvermoon, Eversong Woods
    "High Elves": (164.1, 27.1),      # Quel'Danas
    "Pandaren": (59.5, 97.5),         # the Temple of Five Dawns, the Wandering Isle
    "Forsaken": (153.8, 41.2),        # Undercity, Tirisfal Glades
    "Draenei": (17.4, 45.7),          # The Exodar, Azuremyst Isle
    "Goblins": (46.2, 49.6),          # Bilgewater Harbor, Azshara
    "Worgen": (145.6, 55.1),          # Gilneas
    "Scourge": (78.6, 10.1),          # Icecrown Citadel, Icecrown
    "Dark Iron Dwarves": (161.3, 71.7),  # Shadowforge City, beneath Blackrock (Burning Steppes)
    "Kul Tirans": (133.6, 59.4),      # Boralus, Tiragarde Sound
    "Zandalari Trolls": (94.2, 70.4),   # Dazar'alor, Zuldazar
}
CITY_STATES = {
    "Dalaran": (154.9, 48.1),         # Alterac, on Lordamere Lake
    "Theramore": (44.4, 69.7),
    "Stromgarde": (158.0, 54.9),      # Arathi Highlands
    "Gadgetzan": (37.7, 76.9),        # Tanaris
    "Booty Bay": (153.1, 84.6),       # Stranglethorn
    "Ratchet": (42.0, 63.3),          # Barrens coast
    "Everlook": (41.1, 40.1),         # Winterspring
    "Steamwheedle Port": (40.2, 82.3),   # Tanaris coast
    "Light's Hope Chapel": (169.3, 42.6),  # Eastern Plaguelands
    "Cenarion Hold": (26.4, 78.2),    # Silithus
    "Argent Vanguard": (89.0, 12.5),  # Icecrown, by the Crystalsong border
    "The Earthen Ring": (23.9, 62.6), # Desolace
    "Knights of the Ebon Blade": (98.7, 16.3),  # Ebon Watch, Zul'Drak
    "Explorers' League": (164.3, 68.3),  # Badlands, near Uldaman
    "Thorium Brotherhood": (157.1, 69.1),  # Thorium Point, Searing Gorge
    "Feathermoon Stronghold": (16.5, 66.1),  # Sardor Isle, Feralas
    "Timbermaw Hold": (35.8, 42.0),   # furbolgs, Felwood / Winterspring
    "Kamagua": (104.3, 23.0),         # tuskarr, Howling Fjord
    "Maraudine": (26.3, 68.9),        # centaurs, Desolace / Feralas
    "Jasperlode Mine": (156.1, 77.2), # kobolds, Duskwood edge of Elwynn
    "Razorfen Kraul": (36.5, 68.6),   # quilboar, Southern Barrens
    "The Consortium": (77.6, 22.7),   # ethereals, Borean Tundra
    "Mogu'shan": (68.8, 81.2),        # mogu, Isle of Thunder
    "Ahn'Qiraj": (29.1, 82.4),        # qiraji, Silithus
}


# ------------------------------------------------------------------ geometry helpers
def center(c, r):
    """Tile center in map units; odd columns sit half a row north."""
    return (c, r - 0.5 * (c % 2))


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
    """Build the map at any size from the zone raster. spec may give a window (box, in
    authoring units), extra starts, dropped city-states and whether to add polar ice."""
    sp = spec or {}
    x0, y0, x1, y1 = sp.get("box", (0, 0, W, H))
    sx, sy = width / (x1 - x0), height / (y1 - y0)
    k = (sx + sy) / 2 * W / 104                           # tiles per unit of the old 104-wide map
    S = lambda p: ((p[0] - x0) * sx, (p[1] - y0) * sy)
    inwin = lambda p: x0 <= p[0] <= x1 and y0 <= p[1] <= y1
    nb = lambda c, r: neighbors(c, r, width, height)
    rng = random.Random(seed)
    rng2 = random.Random(seed + 1000)                     # Warcraft features (v0.6)

    # ---- land and zones, sampled from the raster over each tile's footprint
    (RW, RH), px, names, LAKE = _load_raster()
    allowed = {z for c in sp.get("lands", CONTINENTS) for z in CONTINENTS[c]}
    ok = [i == LAKE or (0 < i < len(names) and names[i] in allowed) for i in range(256)]
    fx, fy = RW / W, RH / H                               # raster px per authoring unit
    grid = [[None] * width for _ in range(height)]          # zone name or None (water)
    lake = set()
    N = 5
    for r in range(height):
        for c in range(width):
            cc, rr = center(c, r)
            ax, ay = x0 + (cc + 0.5) / sx, y0 + (rr + 0.5) / sy
            votes, lakes, n = Counter(), 0, 0
            for i in range(N):
                for j in range(N):
                    u = int((ax + ((i + 0.5) / N - 0.5) / sx) * fx)
                    v = int((ay + ((j + 0.5) / N - 0.5) / sy) * fy)
                    n += 1
                    if 0 <= u < RW and 0 <= v < RH:
                        z = px[v * RW + u]
                        if not ok[z]:
                            continue
                        if z == LAKE:
                            lakes += 1
                        elif z:
                            votes[z] += 1
            land_n = sum(votes.values()) + lakes
            if land_n >= 0.42 * n and votes:
                grid[r][c] = names[votes.most_common(1)[0][0]]
                if lakes >= 0.5 * n:
                    lake.add((c, r))
    # zones big enough to matter but too small to win a tile get the tile at their centroid
    have = {z for row in grid for z in row if z}
    acc = {}
    for v in range(int(y0 * fy), min(RH, int(y1 * fy))):
        for u in range(max(0, int(x0 * fx)), min(RW, int(x1 * fx))):
            z = px[v * RW + u]
            if z and z != LAKE and ok[z]:
                a = acc.setdefault(z, [0, 0, 0]); a[0] += u; a[1] += v; a[2] += 1
    tile_px = fx / sx * fy / sy
    for z, (su, sv, n) in acc.items():
        if names[z] not in have and n >= 0.15 * tile_px:
            c = int(round((su / n / fx - x0) * sx - 0.5)); c = min(width - 1, max(0, c))
            r = int(round((sv / n / fy - y0) * sy - 0.5 + 0.5 * (c % 2))); r = min(height - 1, max(0, r))
            grid[r][c] = names[z]
    for z, (pt, rad) in EXTRA_LAND.items():
        if not inwin(pt) or z not in allowed:
            continue
        cx, cy = S(pt)
        best = None
        for r in range(height):
            for c in range(width):
                d = math.hypot(center(c, r)[0] - cx + 0.5, center(c, r)[1] - cy + 0.5)
                if d <= rad * (sx + sy) / 2 and grid[r][c] is None:
                    grid[r][c] = z
                if best is None or d < best[0]:
                    best = (d, c, r)
        grid[best[2]][best[1]] = z

    def land(c, r):
        return grid[r][c] is not None

    def snap(pt, want_land=True, avoid=()):
        """Nearest tile to a scaled point that is land (or sea), searching outward."""
        c0, r0 = int(pt[0]), int(pt[1] + 0.5 * (int(pt[0]) % 2))
        c0, r0 = min(width - 1, max(0, c0)), min(height - 1, max(0, r0))
        seen, frontier = {(c0, r0)}, [(c0, r0)]
        while frontier:
            for c, r in frontier:
                if land(c, r) == want_land and (c, r) not in avoid and (c, r) not in lake:
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
            b = BIOMES[z]
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
    for line, chance in RIDGES:
        if not all(inwin(p) for p in line):
            continue
        line = [S(p) for p in line]
        for r in range(height):
            for c in range(width):
                if land(c, r) and any(seg_dist(center(c, r), line[i], line[i + 1]) < ridge_width
                                      for i in range(len(line) - 1)) and rng.random() < chance:
                    tiles[r][c] = {"t": "Mountain", "f": []}
    for ctr, rad, chance in RINGS:
        if not inwin(ctr):
            continue
        cx, cy = S(ctr)
        for r in range(height):
            for c in range(width):
                d = math.hypot(center(c, r)[0] - cx, center(c, r)[1] - cy)
                if land(c, r) and abs(d - rad * (sx + sy) / 2) < 0.7 * max(1.0, k * 0.8) and rng.random() < chance:
                    tiles[r][c] = {"t": "Mountain", "f": []}
    for c, r in lake:
        tiles[r][c] = {"t": "Lakes", "f": []}
    for pt in LAKES:
        if not inwin(pt):
            continue
        c, r = snap(S(pt))
        tiles[r][c] = {"t": "Lakes", "f": []}
        lake.add((c, r))
        if k > 1.2:                                       # bigger maps get bigger lakes
            for nc, nr in nb(c, r)[:2]:
                if land(nc, nr):
                    tiles[nr][nc] = {"t": "Lakes", "f": []}
                    lake.add((nc, nr))

    # Polar ice along the top edge of the world
    for c in range(width if sp.get("ice", y0 == 0) else 0):
        for r in range(0, 2):
            if not land(c, r) and rng.random() < (0.85 if r == 0 else 0.4):
                tiles[r][c] = {"t": "Ocean", "f": ["Ice"]}

    # capitals and city-states, scaled and snapped onto land
    caps = {n: p for n, p in CAPITALS.items() if inwin(p) and n not in sp.get("starts", {})}
    caps.update(sp.get("starts", {}))
    css = {n: p for n, p in CITY_STATES.items() if inwin(p) and n not in sp.get("drop", ())}
    capitals, city_states, taken = {}, {}, set()
    for src, dst in ((caps, capitals), (css, city_states)):
        for name, pt in src.items():
            pos = snap(S(pt), avoid=taken)
            dst[name] = pos
            taken.update([pos] + nb(*pos))               # keep cities at least two tiles apart

    # settle-able ground for every capital and city-state; no mountains right beside them
    for name, (c, r) in {**capitals, **city_states}.items():
        z = grid[r][c]
        base = tiles[r][c]["t"]
        if base in ("Mountain", "Lakes", "Ocean", "Coast"):
            base = max(BIOMES[z]["base"], key=BIOMES[z]["base"].get)
        if base == "Snow":
            base = "Tundra"
        keep_hill = ["Hill"] if "Hill" in tiles[r][c]["f"] else []
        tiles[r][c] = {"t": base, "f": keep_hill}
        for nc, nr in nb(c, r):
            if tiles[nr][nc]["t"] == "Mountain" and land(nc, nr):
                b = BIOMES[grid[nr][nc]]["base"]
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
    for name, pt in NATURAL_WONDERS.items():
        if not inwin(pt):
            continue
        water = name in WATER_WONDERS
        c, r = snap(S(pt), want_land=not water, avoid=taken)
        wonders[name] = (c, r)
        taken.add((c, r))
        if water:
            tiles[r][c] = {"t": "Ocean", "f": [], "nw": name}
            if name == "Kelp'thar Forest" and r + 1 < height and not land(c, r + 1):   # occurs as a pair of tiles
                tiles[r + 1][c] = {"t": "Ocean", "f": [], "nw": name}
        else:
            tiles[r][c] = {"t": NW_BASE.get(name, "Plains"), "f": [], "nw": name}

    return dict(width=width, height=height, tiles=tiles, zones=grid,
                capitals=capitals, cityStates=city_states, wonders=wonders)


# ------------------------------------------------------------------ regional maps
# Each region is a window on the world; factions with a lore foothold there get extra starts
# (Unciv places any other chosen faction on its own).
REGIONS = {
    "Kalimdor": dict(lands=["Kalimdor"], box=(4, 27, 57, 92),
                     starts={"Kul Tirans": (44.4, 69.7),     # Jaina's Theramore
                             "Humans": (39.9, 67.5)},        # Northwatch Hold, Southern Barrens
                     drop=["Theramore"]),
    "Eastern Kingdoms": dict(lands=["Eastern Kingdoms"], box=(138, 20, 176, 92),
                             starts={"Orcs": (150.3, 80.8),      # Grom'gol Base Camp, Stranglethorn
                                     "Trolls": (171.3, 36.4),    # Zul'Aman, Ghostlands
                                     "Scourge": (167.0, 43.5)}),  # Stratholme, Eastern Plaguelands
    "Northrend": dict(lands=["Northrend"], box=(62, 0, 112, 35),
                      starts={"Humans": (77.3, 25.5),        # Valiance Keep, Borean Tundra
                              "Orcs": (82.0, 25.3),          # Warsong Hold
                              "Tauren": (88.9, 23.6),        # Taunka'le, Dragonblight
                              "Trolls": (97.1, 17.2),        # Zul'Drak
                              "Dwarves": (103.8, 27.6),      # Valgarde, Howling Fjord
                              "Forsaken": (107.5, 25.2)}),   # Vengeance Landing
    "Pandaria": dict(lands=["Pandaria"], box=(63, 76, 111, 110),
                     starts={"Pandaren": (87.1, 97.7),       # Halfhill, Valley of the Four Winds
                             "Humans": (92.9, 103.2),        # Lion's Landing, Krasarang
                             "Orcs": (86.3, 103.8),          # Domination Point, Krasarang
                             "Dwarves": (94.6, 98.3),        # Paw'don Village, Jade Forest
                             "Trolls": (89.3, 88.1)}),       # Honeydew Village, Jade Forest
}


def spec_for(name):
    return REGIONS.get(name)


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
