"""Faction-styled farms, mines, lumber mills, trading posts and pastures (HexaRealm).

Unciv draws an owned tile's improvement layer as "<image>-<owner>" when that image
exists (see race_works.py, which does the same for camps and forts). HexaRealm draws
these improvements as separate layers over the terrain:
  HutFarm / HutFarmT          the farmstead in the middle of the fields
  Mine / MineT                the pit head on a hill
  Lumber mill / Lumber millT  sheds and log piles among the trees
  Trading post / Trading postT market stalls
  Pasture                     barn and fences
so each faction gets its own version of every layer, built in the same architecture as
its city centers (citycenters.STYLES: house shape, wall and roof colours, trim, window
glow) with its camp prop and fort wall type from race_works. The fields, trees and
resources underneath stay stock. Snowy "T" versions get snow on their roofs.
City-states borrow the style of their city center. Original pixel art.
"""
import math
import os
import random

import numpy as np

from PIL import Image
from mounts import shade
import cc_legacy as CC
import race_works as RW

TW, TH = 64, 56
HEX = RW.HEX


def st_of(race):
    st = dict(CC.STYLES[race])
    st["prop"] = RW.CAMP[race]["prop"]
    st["fwall"] = RW.FORT[race]["wall"]
    st["fcol"] = RW.FORT[race]["col"]
    st["lamp"] = RW.FORT[race].get("lamp")
    return st


def building(s, st, x, y, w, h, kind=None, roof=None):
    k = kind or st["house"]
    rh = w * 0.9 if k in ("cone", "tent") else w * 0.5 if k == "thatch" else None
    s.piece(y, lambda p: CC.house(p, x, y, w, h, st["wall"], roof or st["roof"], kind=k, rh=rh, win=st.get("win"),
                                  trim=st.get("trim")))


def prop(s, race, st, x, y):
    RW.camp_prop(s, race, st["prop"], x, y)


# ================================================================== farmstead
def farmstead(race):
    st = st_of(race)
    s = RW.Scene()
    building(s, st, 25, 34, 13, 7)
    def stack(p):                       # a hay rick (or grain sacks)
        p.ell(42, 32, 3.5, 3, (215, 185, 90), "hay")
        p.ell(42, 30, 2.4, 2, shade((215, 185, 90), 1.12), "hay")
    if race not in ("Scourge", "Forsaken"):
        s.piece(32, stack)
    prop(s, race, st, 20, 34)
    return s.render()


# ================================================================== mine
def mine_frame(p, st, x, y, w=12, h=10):
    """The pit-head frame over the tunnel mouth, in the faction's fort material."""
    kind, col = st["fwall"], st["fcol"]
    if kind in ("stone", "saronite", "lacquer"):
        pc = shade(col, 1.05)
        p.poly([(x - 1, y), (x + 2, y), (x + 2, y - h), (x - 1, y - h)], pc, "pl")
        p.poly([(x + w - 2, y), (x + w + 1, y), (x + w + 1, y - h), (x + w - 2, y - h)], shade(pc, 0.82), "pr")
        p.poly([(x - 2, y - h), (x + w + 2, y - h), (x + w + 2, y - h - 3), (x - 2, y - h - 3)], pc, "lintel")
        if kind == "lacquer":
            p.poly([(x - 4, y - h - 3), (x + w + 4, y - h - 3), (x + w + 2, y - h - 5), (x - 2, y - h - 5)], st["roof"], "cap")
        if kind == "saronite":
            for sx in (x, x + w / 2, x + w):
                p.line(sx, y - h - 3, sx, y - h - 6, 1, shade(col, 0.7), "spike")
        if st.get("trim"):
            p.dot(x + w / 2, y - h - 1.5, st["trim"], "rune")
    elif kind == "metal":
        p.line(x, y, x, y - h, 2, col, "pl")
        p.line(x + w, y, x + w, y - h, 2, shade(col, 0.8), "pr")
        p.line(x - 1, y - h, x + w + 1, y - h, 2, col, "beam")
        p.ell(x + w / 2, y - h - 3, 3, 3, (200, 170, 80), "wheel")       # winding wheel
        p.ell(x + w / 2, y - h - 3, 1, 1, (80, 70, 60), "hub")
    elif kind == "thorn":
        p.line(x, y, x + 1, y - h, 2, col, "pl")
        p.line(x + w, y, x + w - 1, y - h, 2, shade(col, 0.82), "pr")
        p.ell(x + w / 2, y - h, w / 2 + 2, 3, st["roof"], "arch")           # a living, leafy arch
    else:                      # timber (palisade): orcs, tauren, trolls
        p.line(x, y, x, y - h, 2, col, "pl")
        p.line(x + w, y, x + w, y - h, 2, shade(col, 0.8), "pr")
        p.line(x - 2, y - h, x + w + 2, y - h, 2, col, "beam")
        p.line(x - 2, y - h, x - 4, y - h - 3, 1, (235, 225, 200), "tusk")
        p.line(x + w + 2, y - h, x + w + 4, y - h - 3, 1, (235, 225, 200), "tusk2")


def mine(race):
    st = st_of(race)
    s = RW.Scene()
    rock = st["stone"]
    def mound(p):
        p.ell(30, 30, 19, 12, shade(rock, 0.9), "mound")
        p.ell(26, 26, 12, 7, rock, "mound")
        p.ell(30, 31, 6, 5, (28, 22, 22), "mouth")
    s.piece(24, mound)
    s.piece(32, lambda p: mine_frame(p, st, 24, 34))
    if st.get("lamp") or st.get("win"):
        s.piece(33, lambda p: p.ell(30, 31, 1.6, 1.6, st.get("lamp") or st["win"], "lamp"), outline=None,
                glow=st.get("lamp") or st["win"])
    def cart(p):                        # an ore cart heaped with ore, on two dark wheels
        p.poly([(41, 38), (50, 38), (49, 43), (42, 43)], (120, 85, 52), "cart")
        p.line(41, 38, 50, 38, 1, (90, 85, 80), "rim")
        p.ell(43.5, 37, 2.2, 1.6, (150, 145, 140), "ore")
        p.ell(47.5, 37, 2.2, 1.6, st.get("trim") or (205, 175, 90), "ore2")
        p.ell(43, 44, 1.6, 1.6, (55, 50, 45), "w1")
        p.ell(48, 44, 1.6, 1.6, (55, 50, 45), "w2")
    s.piece(44, cart)
    building(s, st, 8, 42, 10, 6)
    prop(s, race, st, 52, 32)
    return s.render()


# ================================================================== lumber mill
def logs(p, x, y, col=(130, 90, 55)):
    for k, (dx, dy) in enumerate(((0, 0), (4, 0), (2, -2.5))):
        p.ell(x + dx, y + dy, 2.4, 1.8, col, "log%d" % k)
        p.dot(x + dx - 1, y + dy, shade(col, 1.35), "ring%d" % k)


def lumber_mill(race):
    st = st_of(race)
    s = RW.Scene()
    building(s, st, 8, 42, 15, 7)
    building(s, st, 40, 30, 11, 6)
    nelf = race == "Night Elves"
    s.piece(46, lambda p: logs(p, 26, 46, (120, 95, 130) if nelf else (130, 90, 55)))   # night elves gather only deadwood
    def stump(p):
        p.ell(50, 44, 3, 1.6, (120, 85, 50), "stump")
        p.line(50, 43, 53, 39, 1, (110, 80, 50), "haft")
        p.poly([(52, 39), (55, 38), (54, 41)], (175, 180, 190), "axe")
    s.piece(44, stump)
    prop(s, race, st, 30, 34)
    return s.render()


# ================================================================== trading post
def stall(p, st, x, y, w=10):
    cloth = st.get("roof2") or st["roof"]
    p.line(x, y, x, y - 7, 1, (100, 75, 50), "post")
    p.line(x + w, y, x + w, y - 7, 1, (100, 75, 50), "post2")
    p.poly([(x - 2, y - 7), (x + w + 2, y - 7), (x + w, y - 10), (x, y - 10)], cloth, "awning")
    stripe = st.get("trim") or shade(cloth, 1.4)
    for k in range(int(x), int(x + w), 3):
        p.line(k, y - 7, k + 1, y - 10, 1, stripe, "stripe%d" % k)
    p.poly([(x + 1, y - 1), (x + w - 1, y - 1), (x + w - 1, y - 4), (x + 1, y - 4)], (150, 110, 70), "counter")
    p.dot(x + 3, y - 5, (220, 80, 60), "goods")
    p.dot(x + 6, y - 5, (240, 200, 70), "goods2")


def trading_post(race):
    st = st_of(race)
    s = RW.Scene()
    building(s, st, 38, 22, 13, 7)
    s.piece(26, lambda p: stall(p, st, 10, 26))
    s.piece(44, lambda p: stall(p, st, 30, 44, 12))
    def crates(p):
        p.poly([(48, 44), (53, 44), (53, 40), (48, 40)], (150, 110, 70), "crate")
        p.poly([(50, 40), (54, 40), (54, 37), (50, 37)], (165, 120, 75), "crate2")
    s.piece(44.5, crates)
    prop(s, race, st, 18, 44)
    return s.render()


# ================================================================== pasture
def fence(p, st, pts):
    kind, col = st["fwall"], st["fcol"]
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        if kind in ("stone", "saronite"):
            p.line(x0, y0, x1, y1, 2, shade(col, 0.95), "wall%d" % i)
        elif kind == "thorn":
            p.line(x0, y0, x1, y1, 2, (70, 110, 80), "hedge%d" % i)
            p.dot((x0 + x1) / 2, (y0 + y1) / 2 - 1, st["roof"], "bloom%d" % i)
        else:                           # posts every few pixels with two rails between them
            rail = col if kind != "metal" else shade(col, 0.9)
            n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 4))
            for k in range(n + 1):
                t = k / n
                px_, py_ = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
                p.line(px_, py_ + 0.5, px_, py_ - 4, 1.4, shade(rail, 0.8), "post%d" % i)
            p.line(x0, y0 - 3, x1, y1 - 3, 1, rail, "post%d" % i)
            p.line(x0, y0 - 1, x1, y1 - 1, 1, rail, "post%d" % i)


def pasture(race):
    """Barn, fences and trough, kept clear of the middle where the herd stands
    (the stock animals of Sheep/Kodo/Horses sit inside x 12..50, y 14..44)."""
    st = st_of(race)
    s = RW.Scene()
    building(s, st, 23, 13, 14, 7)
    s.piece(30, lambda p: fence(p, st, [(51, 16), (57, 28), (53, 44)]))
    s.piece(50, lambda p: fence(p, st, [(6, 36), (12, 48), (26, 51)]))
    def trough(p):
        p.poly([(36, 48), (44, 48), (43, 51), (37, 51)], (120, 85, 52), "trough")
        p.line(37, 48, 43, 48, 1, (110, 160, 210), "water")
    s.piece(51, trough)
    building(s, st, 3, 30, 9, 5)
    prop(s, race, st, 50, 50)
    return s


# ================================================================== plantation
PLOT = [(5, 36), (27, 50), (55, 34), (33, 22)]       # the raised field, as in the stock plantation


def plantation(race, crops=None):
    """A raised, fenced field with the faction's farmhouse at its front corner.
    `crops` (the resource's crop rows cut from the stock combined image) grow on it."""
    st = st_of(race)
    s = RW.Scene()
    soil = (118, 84, 52) if race not in ("Scourge", "Forsaken") else (92, 84, 80)
    def plot(p):
        p.poly(PLOT, soil, "soil")
        p.poly([(5, 36), (27, 50), (27, 53), (5, 39)], shade(soil, 0.75), "bankL")
        p.poly([(27, 50), (55, 34), (55, 37), (27, 53)], shade(soil, 0.6), "bankR")
        if crops is None:                      # bare furrows
            for k in range(5):
                t = 0.18 + k * 0.16
                ax, ay = 5 + 28 * t, 36 - 14 * t
                p.line(ax, ay, ax + 22, ay + 14, 1, shade(soil, 0.8), "furrow%d" % k)
    s.piece(0, plot)
    s.piece(1, lambda p: fence(p, st, [(5, 36), (33, 22), (55, 34)]))
    if crops is not None:
        s.add(30, crops)
    s.piece(52, lambda p: fence(p, st, [(5, 37), (27, 51), (55, 35)]))
    building(s, st, 14, 48, 12, 6)
    return s


# ================================================================== quarry
def quarry(race):
    """Dressed blocks, a hoist in the faction's fort material and a mason's hut,
    laid over the stock rock (Stone, Marble...) that sits under it."""
    st = st_of(race)
    s = RW.Scene()
    stone = shade(st["stone"], 1.08)
    def cut(p):                                     # the stepped cut face
        p.poly([(18, 24), (36, 14), (46, 20), (28, 30)], shade(stone, 0.75), "face")
        p.poly([(22, 26), (36, 18), (42, 22), (28, 30)], stone, "step")
        p.poly([(28, 30), (42, 22), (42, 26), (28, 34)], shade(stone, 0.6), "riser")
    s.piece(22, cut)
    def hoist(p):                                   # a lifting crane, not a mine head
        kind, col = st["fwall"], st["fcol"]
        wood = col if kind in ("timber", "metal") else (125, 90, 55)
        if kind in ("stone", "saronite", "lacquer"):
            p.poly([(31, 30), (37, 30), (36, 27), (32, 27)], shade(col, 1.05), "footing")
        p.line(34, 28, 34, 9, 2, wood, "post")
        p.line(34, 10, 47, 7, 1.6, shade(wood, 0.9), "boom")
        p.line(34, 16, 41, 8, 1, shade(wood, 0.8), "brace")
        p.line(46, 8, 46, 17, 1, (90, 75, 60), "rope")
        p.poly([(44, 17), (49, 17), (49, 20), (44, 20)], stone, "block")
        p.poly([(34, 9), (34, 4), (39, 6)], st["roof"], "pennant")
        if kind == "thorn":
            p.ell(34, 9, 3, 2, (70, 120, 80), "leaves")
    s.piece(27, hoist)
    def blocks(p):
        for k, (bx, by) in enumerate(((38, 40), (43, 40), (40.5, 37))):
            p.poly([(bx, by), (bx + 5, by), (bx + 5, by - 3), (bx, by - 3)], shade(stone, 1.0 - 0.06 * k), "blk%d" % k)
    s.piece(40, blocks)
    building(s, st, 16, 42, 11, 6)
    def tools(p):
        p.line(30, 43, 33, 38, 1, (110, 80, 50), "haft")
        p.poly([(32, 38), (35, 37), (34, 39)], (175, 180, 190), "pick")
    s.piece(43, tools)
    return s


# ================================================================== fishing boats
def boat(p, ss, x, y, flip=False):
    """A small faction fishing boat whose hull sits on the water at (x, y)."""
    d = -1 if flip else 1
    hull, sail, acc = ss["hull"], ss["sail"], ss["acc"]
    p.poly([(x - 7 * d, y - 2), (x + 7 * d, y - 2), (x + 5 * d, y + 2), (x - 5 * d, y + 2)], hull, "hull")
    p.line(x - 6 * d, y - 2, x + 6 * d, y - 2, 1, acc, "rail")
    p.line(x, y - 2, x, y - 13, 1, (95, 70, 45), "mast")
    p.poly([(x + 0.5 * d, y - 13), (x + 6 * d, y - 4), (x + 0.5 * d, y - 4)], sail, "sail")
    p.line(x - 6 * d, y - 2, x - 9 * d, y - 6, 1, (200, 200, 190), "net")      # a net over the side
    if ss.get("glow"):
        p.dot(x - 4 * d, y - 4, ss["glow"], "lamp")


def fishing_boats(race, spots=((30, 26), (45, 40))):
    ss = RW.SHIP_STYLE[race]
    s = RW.Scene()
    for k, (x, y) in enumerate(spots):
        def wake(p, x=x, y=y):
            p.ell(x, y + 3, 9, 2, (120, 190, 215), "wake")
            p.line(x - 8, y + 3, x - 3, y + 3, 1, (230, 245, 250), "foam")
        s.piece(y - 1, wake, outline=None)
        s.piece(y, lambda p, x=x, y=y, k=k: boat(p, ss, x, y, flip=bool(k % 2)))
    return s


# ================================================================== writing
LAYERS = {"HutFarm": farmstead, "Mine": mine, "Lumber mill": lumber_mill, "Trading post": trading_post,
          "Pasture": lambda r: pasture(r).render(), "Plantation": lambda r: plantation(r).render(),
          "Quarry": lambda r: quarry(r).render(), "Fishing Boats": lambda r: fishing_boats(r).render()}
SNOWY = {"HutFarmT": "HutFarm", "MineT": "Mine", "Lumber millT": "Lumber mill", "Trading postT": "Trading post",
         "QuarryT": "Quarry"}
COMBO = ("Pasture", "Plantation", "Quarry", "QuarryT", "Fishing Boats")


def render_race(race):
    out = {name: fn(race) for name, fn in LAYERS.items()}
    for snowy, base in SNOWY.items():
        out[snowy] = RW.snow(out[base])
    return out


def _arr(im):
    return np.asarray(im.convert("RGBA")).astype(int)


def _minus(combined, part):
    """Pixels of `combined` that aren't identical to `part` at the same place."""
    c, q = _arr(combined), _arr(part)
    same = (q[..., 3] > 0) & (np.abs(c - q).sum(-1) == 0)
    c[same] = 0
    return Image.fromarray(c.astype(np.uint8), "RGBA")


def _spots(im, min_area=40):
    """Centres (x, bottom) of the separate objects in an image, e.g. the stock boats."""
    from scipy import ndimage
    a = _arr(im)[..., 3] > 0
    lab, _ = ndimage.label(a)
    out = []
    for sl in ndimage.find_objects(lab):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if h * w >= min_area:
            out.append(((sl[1].start + sl[1].stop) / 2, sl[0].stop - 3))
    return sorted(out, key=lambda t: t[1])


def combo_art(race, name, load):
    """The faction version of a stock/mod "<resource>+<improvement>" image."""
    res, imp = name.split("+", 1)
    if imp == "Pasture":                      # the herd stands in the middle of the faction's pasture
        r = load(res)
        if r is None:
            return None
        s = pasture(race)
        s.add(35, r)
        return s.render()
    if imp == "Plantation":                   # the crop rows, cut out of the combined image
        whole, stock = load(name), load("Plantation")
        if whole is None or stock is None:
            return None
        return plantation(race, _minus(whole, stock)).render()
    if imp in ("Quarry", "QuarryT"):           # the rock under the faction quarry
        r = load(res)
        if r is None:
            return None
        q = quarry(race).render()
        if imp == "QuarryT":
            q = RW.snow(q)
        out = r.copy()
        out.alpha_composite(q)
        return out
    if imp == "Fishing Boats":                # the creature, with faction boats where the stock boats were
        whole, r = load(name), load(res)
        if whole is None or r is None:
            return None
        spots = _spots(_minus(whole, r))
        if not spots:
            return None
        out = r.copy()
        out.alpha_composite(fishing_boats(race, spots).render())
        return out
    return None


def write_tiles(out_dir, nations, city_states, tiles_atlas=None, renames=None):
    """Write "<layer>-<owner>" improvement images into the HexaRealm tile folder, and
    "<resource>+<improvement>-<owner>" for the combined resource images HexaRealm uses
    instead of separate layers (pastures, plantations, quarries, whales + boats)."""
    import re
    tiles_dir = os.path.join(out_dir, HEX)
    os.makedirs(tiles_dir, exist_ok=True)
    owners = RW._owners(nations, city_states)
    art = {race: render_race(race) for race in set(owners.values())}
    n = 0
    for owner, race in owners.items():
        for name, im in art[race].items():
            im.save(os.path.join(tiles_dir, "%s-%s.png" % (name, owner)))
            n += 1
    if tiles_atlas is None:
        return n
    renames = renames or {}
    fwd = lambda name: "+".join(renames.get(t, t) for t in name.split("+"))
    back_map = {v: k for k, v in renames.items()}
    back = lambda name: "+".join(back_map.get(t, t) for t in name.split("+"))
    def load(name):
        return RW._load(name, tiles_dir, tiles_atlas, back)
    pat = re.compile(r"^[^+-]+\+(%s)$" % "|".join(COMBO))
    names = {f[:-4] for f in os.listdir(tiles_dir) if f.endswith(".png") and pat.match(f[:-4])}
    names |= {fwd(r[len(HEX):]) for r in tiles_atlas.regions if r.startswith(HEX) and pat.match(r[len(HEX):])}
    for name in sorted(names):
        per_race = {race: combo_art(race, name, load) for race in set(owners.values())}
        for owner, race in owners.items():
            if per_race[race] is not None:
                per_race[race].save(os.path.join(tiles_dir, "%s-%s.png" % (name, owner)))
                n += 1
    return n
