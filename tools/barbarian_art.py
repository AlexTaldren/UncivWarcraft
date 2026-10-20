"""Map sprites for the themed barbarians (Oct 2026 systems pass), in the mod's pixel-art style.

Each barbarian people is drawn as a "race" on the shared figure kit (wc_style_races), using the
pose and kit of the generic unit it replaces: Kobolds (candles), Gnolls, Murlocs, Centaurs,
Harpies (wings), Quilboar, Ogres, Naga (serpent tails), Satyrs, the red-masked Defias, Bloodsail
pirates, Venture Co. goblins, Kvaldir, Twilight cultists and the Faceless. Barbarian ships reuse
the hull of the ship they replace. All designs are original.
"""
import os
import shutil

import mounts as MT
import wc_style_units as U
import wc_style_more as M
import wc_style_races as WR
from wc_style_units import Fig, BONE
from wc_style_races import eyes
from paint import mix
from wc_systems import BARBARIANS

UNIT_DIR = M.UNIT_DIR


# ================================================================== faces (human frame)
def face_kobold(f, x, y, hat=None, **k):
    fur = U.HSKIN
    f.paint(f.ell(x - 3, y - 6, 3.5, 5), mix(fur, (0, 0, 0), 0.15), mat="fur")             # ear
    f.paint(f.ell(x, y, 7.5, 7.5), fur, mat="fur")
    f.paint(f.poly([(x + 3, y - 3), (x + 15, y + 2), (x + 13, y + 5), (x + 3, y + 5)]), mix(fur, (255, 230, 210), 0.2), mat="fur")
    f.paint(f.ell(x + 14.5, y + 2.5, 1.6, 1.4), (230, 140, 150), mat="flat", outline=0)      # pink nose
    eyes(f, x + 4, y - 2, (20, 15, 15))
    # the candle
    f.paint(f.poly([(x - 4, y - 7), (x + 4, y - 7), (x + 3, y - 9), (x - 3, y - 9)]), (110, 90, 60), mat="wood", outline=0.5)
    f.paint(f.poly([(x - 1.6, y - 9), (x + 1.6, y - 9), (x + 1.6, y - 17), (x - 1.6, y - 17)]), (245, 238, 210), mat="cloth", outline=0.5)
    m = f.ell(x, y - 20, 1.8, 2.8)
    f.c.glow(m, (255, 210, 90), radius=4, strength=0.9)
    f.paint(m, (255, 230, 140), mat="glow", outline=0)
    return None


def face_murloc(f, x, y, hat=None, **k):
    sk = U.HSKIN
    f.paint(f.poly([(x - 8, y - 4), (x - 3, y - 16), (x + 1, y - 13), (x + 3, y - 18), (x + 6, y - 8)]), (200, 90, 80), mat="leather")  # fin
    f.paint(f.ell(x + 1, y + 1, 10, 9.5), sk, mat="skin")
    f.paint(f.poly([(x + 1, y + 3), (x + 12, y + 1), (x + 11, y + 6), (x + 2, y + 8)]), (130, 40, 50), mat="flat", outline=0.5)    # gaping mouth
    for k_ in range(3):
        f.paint(f.poly([(x + 4 + k_ * 2.4, y + 2.6), (x + 5.2 + k_ * 2.4, y + 4.8), (x + 6.4 + k_ * 2.4, y + 2.4)]), BONE, mat="bone", outline=0)
    f.paint(f.ell(x + 5, y - 4, 3.2, 3.2), (250, 245, 200), mat="flat", outline=0.5)
    f.paint(f.ell(x + 6, y - 4, 1.4, 1.6), (20, 20, 20), mat="flat", outline=0)
    return None


def face_harpy(f, x, y, hat=None, **k):
    WR.face_human(f, x, y)
    f.paint(f.curve([(x + 4, y - 9), (x - 6, y - 13), (x - 14, y - 6), (x - 12, y + 6)], 4.5, 2.0), U.HAIR, mat="fur")   # feathered mane
    for d in (-3, 3):
        f.paint(f.poly([(x - 12 + d, y - 4), (x - 20 + d, y + 2), (x - 13 + d, y + 2)]), mix(U.HAIR, (255, 255, 255), 0.2), mat="fur", outline=0.4)
    eyes(f, x + 4, y - 1.5, (255, 220, 80), glow=True)
    return None


def face_naga(f, x, y, hat=None, **k):
    WR.face_human(f, x, y)
    f.paint(f.poly([(x - 2, y - 2), (x - 14, y - 9), (x - 12, y - 1), (x - 15, y + 4), (x - 3, y + 4)]), (60, 160, 150), mat="leather")  # ear fin
    f.paint(f.curve([(x + 5, y - 9), (x - 4, y - 12), (x - 11, y - 4), (x - 9, y + 12)], 4.0, 1.8), U.HAIR, mat="fur")
    eyes(f, x + 4, y - 1.5, (200, 255, 240), glow=True)
    return None


def face_satyr(f, x, y, hat=None, **k):
    WR.face_human(f, x, y, beard=U.HAIR)
    for s, d in ((-2, 0.85), (2, 1.0)):
        f.paint(f.curve([(x + s, y - 7), (x + s - 7, y - 15), (x + s - 12, y - 9), (x + s - 9, y - 3)], 2.4, 1.0), (60, 45, 40), mat="bone",
                outline=0.5, dark=d)
    f.paint(f.poly([(x - 3, y - 2), (x - 12, y - 6), (x - 5, y + 2)]), U.HSKIN, mat="skin", outline=0.4)       # pointed ear
    eyes(f, x + 4, y - 1.5, (140, 255, 90), glow=True)
    return None


def face_defias(f, x, y, hat=None, **k):
    WR.face_human(f, x, y)
    red = (175, 35, 35)
    f.paint(f.poly([(x - 7, y + 0.5), (x + 9, y + 1), (x + 9.5, y + 8), (x + 2, y + 11), (x - 6, y + 8)]), red, mat="cloth")   # the red mask
    f.paint(f.poly([(x - 8, y - 9), (x + 6, y - 9), (x + 8, y - 4), (x - 8, y - 3)]), mix(red, (0, 0, 0), 0.15), mat="cloth")   # hood band
    return None


def face_pirate(f, x, y, hat=None, **k):
    WR.face_human(f, x, y, always_beard=True)
    f.paint(f.poly([(x + 1, y - 3.5), (x + 7, y - 3.5), (x + 7, y + 0.5), (x + 1, y + 0.5)]), (25, 25, 25), mat="flat", outline=0)   # eyepatch
    f.paint(f.poly([(x - 9, y - 6), (x + 7, y - 7), (x + 6, y - 12), (x - 8, y - 11)]), (185, 30, 30), mat="cloth")              # bandana
    f.paint(f.poly([(x - 9, y - 7), (x - 15, y - 2), (x - 12, y + 1), (x - 8, y - 4)]), (185, 30, 30), mat="cloth", outline=0.4)
    return None


def face_kvaldir(f, x, y, hat=None, **k):
    WR.face_human(f, x, y, beard=(70, 110, 80))
    for k_ in range(3):   # dripping kelp
        f.paint(f.curve([(x - 2 + k_ * 3, y + 9), (x - 3 + k_ * 3, y + 14), (x - 1 + k_ * 3, y + 18)], 0.9, 0.5), (60, 100, 60), mat="fur", outline=0)
    eyes(f, x + 4, y - 1.5, (150, 230, 255), glow=True)
    return "hood" if hat == "hood" else None


def face_cultist(f, x, y, hat=None, **k):
    f.paint(f.ell(x, y, 8.5, 9), (40, 30, 50), mat="flat")
    eyes(f, x + 4, y - 1, (190, 120, 255), glow=True)
    eyes(f, x - 0.5, y - 1, (190, 120, 255), glow=True, r=1.0)
    return "hood"


# ================================================================== faces (big frame)
def bface_gnoll(f, x, y, hair="topknot", helm=False):
    fur = U.OSKIN
    f.paint(f.ell(x - 7, y, 8, 11), U.OHAIR, mat="fur")                                       # mane
    f.paint(f.poly([(x - 4, y - 6), (x - 7, y - 18), (x + 1, y - 8)]), fur, mat="fur")         # ear
    f.paint(f.ell(x, y - 1, 9, 9), fur, mat="fur")
    f.paint(f.poly([(x + 2, y - 4), (x + 17, y), (x + 17, y + 5), (x + 10, y + 9), (x + 2, y + 8)]), mix(fur, (0, 0, 0), 0.15), mat="fur")
    f.paint(f.ell(x + 16.5, y + 1, 1.7, 1.5), (25, 20, 20), mat="flat", outline=0)
    for (sx, sy) in ((-3, -3), (1, 3), (-5, 4)):
        f.paint(f.ell(x + sx, y + sy, 1.6, 1.4), mix(fur, (0, 0, 0), 0.45), mat="flat", outline=0)   # spots
    f.paint(f.poly([(x + 8, y + 6), (x + 14, y + 5.5), (x + 13, y + 7), (x + 8, y + 7.4)]), BONE, mat="bone", outline=0.3)
    eyes(f, x + 6, y - 3, (255, 200, 60), glow=True)


def bface_quilboar(f, x, y, hair="topknot", helm=False):
    sk = U.OSKIN
    for k in range(5):   # spiked mane
        a = -12 + k * 4
        f.paint(f.poly([(x - 6 + k * 2, y - 6), (x - 14 + a * 0.6, y - 20 + abs(k - 2) * 2), (x - 2 + k * 2, y - 8)]), (90, 70, 50), mat="wood", outline=0.4)
    f.paint(f.ell(x, y, 10, 9.5), sk, mat="skin")
    f.paint(f.poly([(x + 3, y - 3), (x + 16, y - 1), (x + 17, y + 6), (x + 4, y + 8)]), mix(sk, (255, 220, 220), 0.2), mat="skin")
    f.paint(f.ell(x + 16, y + 2.5, 2.2, 3), mix(sk, (0, 0, 0), 0.2), mat="skin", outline=0.4)
    f.paint(f.curve([(x + 11, y + 7), (x + 16, y + 4), (x + 16, y - 3)], 1.8, 0.6), BONE, mat="bone", outline=0.5)    # tusk
    eyes(f, x + 6, y - 3, (230, 60, 40), glow=True)


def bface_ogre(f, x, y, hair="topknot", helm=False):
    sk = U.OSKIN
    f.paint(f.ell(x, y, 10.5, 10), sk, mat="skin")
    f.paint(f.poly([(x - 2, y + 2), (x + 13, y + 1), (x + 14, y + 10), (x + 4, y + 13), (x - 3, y + 10)]), sk, mat="skin")   # jaw
    f.paint(f.poly([(x + 11, y + 4), (x + 13, y - 2), (x + 14, y + 4)]), BONE, mat="bone", outline=0.4)                      # single tusk
    eyes(f, x + 5, y - 2, (30, 25, 20), r=1.6)
    f.paint(f.poly([(x + 1, y - 5), (x + 9, y - 4), (x + 9, y - 3), (x + 1, y - 3.5)]), mix(sk, (0, 0, 0), 0.35), mat="flat", outline=0)   # brow
    if not helm:
        f.paint(f.curve([(x - 2, y - 9), (x - 5, y - 16), (x - 10, y - 15)], 2.2, 1.2), U.OHAIR, mat="fur", outline=0.4)       # topknot


def bface_faceless(f, x, y, hair="topknot", helm=False):
    sk = U.OSKIN
    f.paint(f.ell(x, y - 1, 10, 10.5), sk, mat="skin")
    for k in range(5):   # tentacles where the face should be
        f.paint(f.curve([(x + 2 + k * 1.6, y + 1), (x + 6 + k * 2, y + 9), (x + 3 + k * 2.4, y + 16)], 1.5, 0.6), mix(sk, (255, 120, 160), 0.25),
                mat="skin", outline=0.4)
    eyes(f, x + 6, y - 4, (255, 120, 255), glow=True)
    eyes(f, x + 2, y - 6, (255, 120, 255), glow=True, r=1.0)


def bface_centaur(f, x, y, hair="topknot", helm=False):
    WR.bface_troll(f, x, y, hair="none", helm=True)
    f.paint(f.curve([(x + 2, y - 9), (x - 8, y - 13), (x - 14, y - 4), (x - 13, y + 10)], 4.5, 2.2), U.OHAIR, mat="fur")


# ================================================================== extra pieces
def harpy(draw):
    import boss_art
    def run(c, fx, fy, u):
        f = Fig(c, fx, fy, u)
        for sx, d in ((1, 0.75), (-1, 1.0)):
            col = mix((140, 90, 150), (0, 0, 0), 0.15 if d < 1 else 0)
            boss_art.wing(f, (-4, -66), [(-30 + sx * 4, -104), (-44, -86), (-42, -64), (-30, -50)], col, (90, 60, 90))
        draw(c, fx, fy, u)
    return run


def naga(draw):
    def run(c, fx, fy, u):
        draw(c, fx, fy, u)
        f = Fig(c, fx, fy, u)
        scale = (60, 150, 140)
        f.paint(f.ell(0, -20, 10, 15), scale, mat="leather")
        f.paint(f.curve([(0, -10), (-6, -2), (-22, -3), (-34, -10), (-38, -18)], 7.5, 1.6), scale, mat="leather")
        for k in range(4):
            f.paint(f.curve([(-4 - k * 8, -6 + k), (-8 - k * 8, -3 + k)], 0.7), mix(scale, (255, 255, 255), 0.35), mat="flat", outline=0)
    return run


def centaur_mount(p, v, armored):
    return MT.horse(p, v, armored, (138, 98, 64), (64, 44, 32))


# barbarian "races": family, body, head, face, colours, weapon swaps, hats, extra drawing
CREATURES = {
    "Kobold Tunneler": dict(family="human", body=(0.82, 0.72), head=1.1, face=face_kobold,
                            colors=dict(skin=(150, 120, 100), hair=(110, 90, 70), leather=(90, 70, 55), cloth_tan=(140, 120, 90))),
    "Gnoll Poacher": dict(family="brute", body=(0.95, 1.05), head=1.0, bface=bface_gnoll,
                          colors=dict(oskin=(176, 140, 90), ohair=(80, 60, 40), iron=(110, 95, 80))),
    "Murloc Tidehunter": dict(family="human", body=(0.88, 0.72), head=1.25, face=face_murloc,
                              recipe=M.hs(armor="leather", tabard=False, hat="hair", weapon="spear", pauldron=False),
                              colors=dict(skin=(90, 160, 110), hair=(90, 160, 110), leather=(80, 110, 90))),
    "Centaur Outrunner": dict(family="brute", body=(1.0, 1.05), head=1.0, bface=bface_centaur, mount=centaur_mount,
                              colors=dict(oskin=(176, 130, 92), ohair=(50, 36, 28), iron=(120, 100, 80))),
    "Harpy Windwitch": dict(family="human", body=(0.92, 1.0), head=1.0, face=face_harpy, extra=harpy,
                            colors=dict(skin=(186, 150, 196), hair=(110, 70, 130), leather=(100, 70, 110))),
    "Quilboar Thornguard": dict(family="brute", body=(1.05, 0.98), head=1.05, bface=bface_quilboar,
                                colors=dict(oskin=(200, 150, 140), ohair=(90, 70, 50), iron=(110, 95, 80))),
    "Ogre Mauler": dict(family="brute", body=(1.4, 1.18), head=1.05, bface=bface_ogre,
                        colors=dict(oskin=(196, 140, 100), ohair=(50, 40, 34), iron=(110, 100, 90)),
                        weapons={"pike": "mace", "spear": "mace", "halberd": "mace", "axe": "mace"}),
    "Naga Siren": dict(family="human", body=(0.95, 1.05), head=1.0, face=face_naga, extra=naga,
                       colors=dict(skin=(110, 190, 170), hair=(40, 90, 140), steel=(160, 200, 190), gold=(220, 200, 120))),
    "Naga Myrmidon": dict(family="human", body=(1.05, 1.08), head=1.0, face=face_naga, extra=naga,
                          recipe=M.hs(armor="plate", tabard=False, hat="hair", weapon="spear", shield="round", pauldron=True),
                          colors=dict(skin=(90, 170, 150), hair=(30, 70, 120), steel=(150, 190, 180), gold=(220, 200, 120))),
    "Satyr Hellcaller": dict(family="human", body=(1.0, 1.0), head=1.0, face=face_satyr,
                             colors=dict(skin=(150, 100, 160), hair=(60, 40, 50), leather=(80, 50, 70), steel=(110, 90, 100))),
    "Defias Pillager": dict(family="human", body=(1.0, 1.0), head=1.0, face=face_defias,
                            colors=dict(skin=(236, 186, 146), hair=(70, 50, 35), leather=(90, 60, 45), cloth_tan=(120, 90, 70))),
    "Bloodsail Sharpshooter": dict(family="human", body=(1.0, 1.0), head=1.0, face=face_pirate,
                                   colors=dict(skin=(214, 160, 120), hair=(50, 40, 30), leather=(80, 60, 45))),
    "Venture Co. Enforcer": dict(family="human", body=(0.86, 0.66), head=1.0, face=WR.face_goblin,
                                 hats=WR.all_helms(WR.hardhat, {"tricorn": WR.hardhat, "officer": WR.hardhat}),
                                 colors=dict(skin=(112, 172, 62), hair=(40, 40, 40), cloth_tan=(200, 90, 40), leather=(150, 70, 30))),
    "Kvaldir Reaver": dict(family="human", body=(1.2, 1.15), head=1.0, face=face_kvaldir,
                           colors=dict(skin=(150, 170, 180), hair=(60, 90, 80), steel=(90, 110, 115), leather=(60, 70, 70))),
    "Twilight Doomcaller": dict(family="human", body=(1.0, 1.0), head=1.0, face=face_cultist,
                                colors=dict(skin=(60, 50, 70), hair=(40, 30, 50), leather=(70, 50, 90), cloth_tan=(90, 60, 120),
                                            cloth_brown=(60, 40, 80), steel=(100, 90, 120))),
    "Faceless Destroyer": dict(family="brute", body=(1.25, 1.15), head=1.05, bface=bface_faceless,
                               colors=dict(oskin=(90, 60, 110), ohair=(40, 30, 50), iron=(70, 60, 80))),
}
WATER = [n for n, (base, _) in BARBARIANS.items() if n not in CREATURES]
ARCH = {"Centaur Outrunner": "mounted"}
HULL = {"Kvaldir Longship": "Longboat"}     # the Destroyer is a steam warship; the Kvaldir sail longships


def register():
    for name, spec in CREATURES.items():
        WR.RACES[name] = {k: v for k, v in spec.items() if k not in ("mount", "extra", "recipe")}
        WR.RACES[name]["hats"] = {**WR.INNER, **spec.get("hats", {})}
        MT.RACE_MOUNT[name] = spec.get("mount") or centaur_mount


def entry(name):
    base = BARBARIANS[name][0]
    if "recipe" in CREATURES[name]:
        draw, arch = CREATURES[name]["recipe"], "foot"
    else:
        draw, arch = WR.race_recipe(name, base)
    extra = CREATURES[name].get("extra")
    if extra:
        draw = extra(draw)
    return (name, base, draw, ARCH.get(name, arch))


def _job(name, ref):
    register()
    return WR.render(name, ref, entry(name))


def write_all(out_dir, image_dirs, stock_atlas=None):
    """Draw the creature sprites into out_dir/<UNIT_DIR> and give the barbarian ships the hulls
    of the ships they replace. image_dirs: where the built mod's unit sprites are."""
    from multiprocessing import Pool
    register()
    folder = os.path.join(out_dir, UNIT_DIR)
    os.makedirs(folder, exist_ok=True)
    jobs = []
    for name in CREATURES:
        ref = M._find(image_dirs, "Outrider" if ARCH.get(name) == "mounted" else "Militia")
        jobs.append((name, ref))
    with Pool(min(8, os.cpu_count() or 2)) as pool:
        rendered = pool.starmap(_job, jobs)
    n = 0
    for (name, _), layers in zip(jobs, rendered):
        for suf, im in zip(("", "-1", "-2"), layers):
            im.save(os.path.join(folder, name + suf + ".png"))
            n += 1
    for name in WATER:
        base = HULL.get(name, BARBARIANS[name][0])
        for suf in ("", "-1", "-2"):
            src = M._find(image_dirs, base + suf)
            if src:
                shutil.copy(src, os.path.join(folder, name + suf + ".png"))
                n += 1
            elif stock_atlas is not None:
                region = "TileSets/AbsoluteUnits/Units/" + base + suf
                if region in stock_atlas.regions:
                    stock_atlas.crop(region).save(os.path.join(folder, name + suf + ".png"))
                    n += 1
        assert os.path.exists(os.path.join(folder, name + ".png")), name
    return n
