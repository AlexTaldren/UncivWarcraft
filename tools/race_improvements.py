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
glow) and its wall material (improvement_art.MATERIAL), drawn by improvement_art.py. The fields, trees and
resources underneath stay stock. Snowy "T" versions get snow on their roofs.
City-states borrow the style of their city center. Original pixel art.
"""
import math
import os
import random

import numpy as np

from PIL import Image
from mounts import shade
import race_works as RW

TW, TH = 64, 56
HEX = RW.HEX


import improvement_art as IA

# The layers are drawn by improvement_art.py with the city-center renderer, so every
# faction's improvements share its city-center architecture and clean 1-px line work.
farmstead = IA.farmstead
mine = IA.mine
lumber_mill = IA.lumber_mill
trading_post = IA.trading_post
pasture = IA.pasture_scene
plantation = IA.plantation_scene
quarry = IA.quarry_scene
fishing_boats = IA.fishing_boats_scene


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
