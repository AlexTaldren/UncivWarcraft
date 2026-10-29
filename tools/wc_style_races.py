"""Pixel-art sprites for the other 16 races, in the same style as the Human and Orc set.

Each race is drawn with the Human/Orc figure kit (wc_style_units, wc_style_more) and a
race context (wc_style_units.CTX) that changes:
  - colours: skin, hair/fur, eyes and the race's armour metals, leathers and trims;
  - proportions: stocky Dwarves, tiny Gnomes and Goblins, tall elves and Draenei, huge
    Tauren, lanky Trolls (body stretch plus head size);
  - the head: long-eared elves, horned and tendrilled Draenei, wolf-headed Worgen,
    rotting Forsaken, skull-faced Scourge, big-nosed Goblins and Gnomes, bearded
    Dwarves, bull-headed Tauren, tusked Trolls, panda-faced Pandaren;
  - headgear: each race's own helmets (horned dwarf helms, crescent Sentinel helms,
    crested elven helms, spiked saronite, goblin hard hats, Pandaren straw hats...);
  - weapons where the lore calls for it (Night Elf moonglaives and bows instead of
    guns, Dwarven hammers, Pandaren polearms, Tauren war hammers);
  - the mount: the race's own beast from mounts.py, redrawn through the pixel canvas.

Human-built races (Dwarves, Gnomes, elves, Draenei, Worgen, Forsaken, Scourge, Goblins,
Kul Tirans, Dark Irons) start from the Human recipes; big-bodied races (Tauren, Trolls,
Zandalari, Pandaren) from the Orc recipes. All designs are original.
"""
import math
import zlib

import wc_style_units as U
import wc_style_more as M
import mounts as MT
from wc_style_units import CTX, Fig, L_MAIN, L_DARK, BONE
from paint import mix

INK_DARK = (30, 24, 24)


def pick(options, *key):
    """A stable choice from a list (varies by unit, never between builds)."""
    if not isinstance(options, list):
        return options
    return options[zlib.crc32("|".join(key).encode()) % len(options)]


def eyes(f, x, y, col, glow=False, r=1.3):
    e = f.ell(x, y, r, r * 1.05)
    if glow:
        f.c.glow(e, col, radius=1.4, strength=0.55)
    f.paint(e, col, mat="glow" if glow else "flat", outline=0)


# ================================================================== human-built faces
# Every face draws at the head centre (x, y) of a uniform head Fig and returns the
# headgear that human_head should still draw ("hood", "kettle", "hair", "cap" or None).
def face_human(f, x, y, hat=None, beard=None, hood=False, hair=None, always_beard=False):
    sk = U.HSKIN
    f.paint(f.ell(x, y, 8.5, 9), sk, mat="skin")
    f.paint(f.ell(x + 7.5, y + 1, 2.2, 2.6), sk, mat="skin", outline=0.5)
    eyes(f, x + 4, y - 1.5, (40, 30, 30))
    f.paint(f.poly([(x + 2, y - 4.5), (x + 7, y - 4.5), (x + 7, y - 3.5), (x + 2, y - 3.5)]), mix(U.HAIR, (0, 0, 0), 0.3), mat="flat", outline=0)
    if beard or always_beard:
        f.paint(f.poly([(x - 6, y + 1), (x + 8, y + 3), (x + 7, y + 11), (x - 1, y + 13), (x - 6, y + 7)]), beard or U.HAIR, mat="fur")
        eyes(f, x + 4, y - 1.5, (40, 30, 30))
    return "hood" if hood else hat


def face_dwarf(f, x, y, hat=None, beard=None, hood=False, hair=None):
    sk = U.HSKIN
    bd = beard if beard not in (None, U.HAIR) else U.HAIR
    f.paint(f.ell(x, y, 9.5, 9), sk, mat="skin")
    eyes(f, x + 4.5, y - 1.5, (35, 25, 25))
    f.paint(f.poly([(x + 1, y - 5.5), (x + 8, y - 5), (x + 8, y - 3.2), (x + 1, y - 3.5)]), bd, mat="fur", outline=0.4)   # brow
    # a great braided beard down to the chest
    f.paint(f.poly([(x - 8, y - 1), (x + 10, y + 2), (x + 10, y + 11), (x + 5, y + 21), (x + 1, y + 23), (x - 3, y + 18),
                    (x - 8, y + 9)]), bd, mat="fur")
    f.paint(f.curve([(x + 2, y + 13), (x + 3, y + 18), (x + 2, y + 22)], 0.7), mix(bd, (0, 0, 0), 0.35), mat="flat", outline=0)
    f.paint(f.ell(x + 8.5, y + 1.5, 3.2, 3.0), mix(sk, (205, 90, 80), 0.3), mat="skin", outline=0.5)   # big ruddy nose
    if hood:
        return "hood"
    if hat in ("kettle", None, "cap"):
        dwarf_helm(f, x, y, horns=hat != "cap")
        return None
    if hat == "hair":
        f.paint(f.poly([(x - 9, y + 1), (x - 9, y - 6), (x - 2, y - 10), (x + 7, y - 8), (x + 8, y - 5), (x, y - 6), (x - 5, y + 2)]),
                bd, mat="fur")
        return None
    return hat


def dwarf_helm(f, x, y, horns=True, crest=False):
    if horns:
        for s, k in ((-1, 0.8), (1, 1.0)):
            f.paint(f.curve([(x + s * 6, y - 8), (x + s * 13, y - 10), (x + s * 14, y - 18)], 2.4, 0.7), BONE, mat="bone",
                    outline=0.6, dark=k)
    f.paint(f.poly([(x - 10, y - 1), (x - 9, y - 8), (x - 3, y - 12), (x + 5, y - 12), (x + 10, y - 7), (x + 11, y - 1)]), U.STEEL, mat="metal")
    f.paint(f.poly([(x - 10, y - 3), (x + 11, y - 3), (x + 11, y - 0.5), (x - 10, y - 0.5)]), U.GOLD, mat="gold", outline=0.4)
    f.paint(f.poly([(x + 7, y - 2), (x + 9.5, y - 2), (x + 9.5, y + 5), (x + 7, y + 5)]), U.STEEL, mat="metal", outline=0.4)  # nose guard
    if crest:
        f.paint(f.poly([(x - 2, y - 12), (x + 3, y - 12), (x + 1, y - 18)]), U.GOLD, mat="gold", outline=0.5)


def face_gnome(f, x, y, hat=None, beard=None, hood=False, hair=None):
    sk = U.HSKIN
    f.paint(f.poly([(x - 6, y - 1), (x - 15, y - 7), (x - 5, y + 3)]), sk, mat="skin", dark=0.92)      # small pointed ear
    f.paint(f.ell(x, y, 9.5, 9.5), sk, mat="skin")
    eyes(f, x + 4.5, y - 1.5, (40, 60, 90), r=1.6)
    f.paint(f.ell(x + 9, y + 2, 3.4, 3.0), sk, mat="skin", outline=0.5)                                  # button nose
    if beard:
        f.paint(f.poly([(x - 5, y + 3), (x + 8, y + 5), (x + 4, y + 13), (x - 3, y + 11)]), U.HAIR, mat="fur")
    if hood:
        return "hood"
    if hat in (None, "hair", "cap"):
        # a big shock of brightly coloured hair (pink, teal, white, violet...)
        f.paint(f.poly([(x - 9, y + 2), (x - 12, y - 8), (x - 7, y - 19), (x - 1, y - 12), (x + 3, y - 20), (x + 6, y - 11),
                        (x + 9, y - 8), (x + 4, y - 6), (x - 3, y - 5), (x - 5, y + 3)]), U.HAIR, mat="fur")
        f.paint(f.ell(x + 1, y - 7.5, 6, 2), M.BRASS, mat="gold", outline=0.4)                           # goggles on the brow
        f.paint(f.ell(x + 4, y - 7.5, 2, 1.6), (130, 210, 230), mat="metal", outline=0)
        return None
    if hat == "kettle":
        return "goggles_cap"
    return hat


def face_elf(f, x, y, hat=None, beard=None, hood=False, hair=None, glow=(220, 235, 255), long_hair=True, brows=False):
    sk = U.HSKIN
    if long_hair and not hood and hat not in ("kettle",):
        f.paint(f.poly([(x - 1, y - 9), (x - 9, y - 7), (x - 13, y + 4), (x - 13, y + 17), (x - 7, y + 15), (x - 4, y + 3)]),
                U.HAIR, mat="fur")
    f.paint(f.ell(x, y, 8, 9), sk, mat="skin")
    f.paint(f.poly([(x + 6, y - 2), (x + 10, y + 2), (x + 6, y + 3)]), sk, mat="skin", outline=0.4)       # fine nose
    # long ear swept back and up, the mark of every elf
    f.paint(f.poly([(x - 3, y - 3), (x - 21, y - 13), (x - 17, y - 5), (x - 3, y + 5)]), sk, mat="skin")
    eyes(f, x + 4, y - 1.5, glow, glow=True)
    if brows:          # night elf males: long swept eyebrows
        f.paint(f.curve([(x + 1, y - 4), (x + 6, y - 5), (x + 9, y - 10)], 0.9, 0.4), U.HAIR, mat="fur", outline=0.3)
    if beard:
        f.paint(f.poly([(x - 3, y + 3), (x + 8, y + 4), (x + 5, y + 14), (x + 1, y + 16), (x - 2, y + 9)]), U.HAIR, mat="fur")
    if hood:
        return "hood"
    if hat in (None, "hair", "cap"):
        f.paint(f.poly([(x - 9, y + 1), (x - 9, y - 6), (x - 2, y - 10), (x + 7, y - 9), (x + 9, y - 4), (x + 1, y - 6), (x - 4, y + 1)]),
                U.HAIR, mat="fur")
        return None
    if hat == "kettle":
        return "elf_helm"
    return hat


def face_draenei(f, x, y, hat=None, beard=None, hood=False, hair=None):
    sk = U.HSKIN
    f.paint(f.ell(x, y, 8.5, 9.5), sk, mat="skin")
    f.paint(f.poly([(x + 6, y - 2), (x + 11, y + 2), (x + 6, y + 3)]), sk, mat="skin", outline=0.4)
    f.paint(f.poly([(x - 3, y - 1), (x - 12, y - 5), (x - 3, y + 3)]), sk, mat="skin", dark=0.9)         # ear
    eyes(f, x + 4, y - 1.5, (225, 240, 255), glow=True)
    # head tendrils hanging from the jaw
    for dx, k in ((-1, 0.85), (4, 1.0)):
        f.paint(f.curve([(x + dx, y + 6), (x + dx + 2, y + 12), (x + dx, y + 18)], 1.8, 0.8), mix(sk, (0, 0, 0), 0.15), mat="skin",
                outline=0.5, dark=k)
    if hood:
        return "hood"
    if hat in (None, "hair", "cap", "kettle"):
        f.paint(f.poly([(x - 9, y + 2), (x - 9, y - 6), (x - 2, y - 10), (x + 6, y - 9), (x + 7, y - 6), (x - 1, y - 6), (x - 5, y + 4)]),
                U.HAIR, mat="fur")
        draenei_horns(f, x, y)
        return None
    return hat


def draenei_horns(f, x, y):
    f.paint(f.curve([(x - 1, y - 7), (x - 8, y - 15), (x - 15, y - 12), (x - 16, y - 4)], 2.8, 1.0), (75, 60, 95), mat="bone", outline=0.6)


def face_worgen(f, x, y, hat=None, beard=None, hood=False, hair=None):
    fur = U.HAIR
    f.paint(f.ell(x - 4, y + 3, 9, 10), mix(fur, (0, 0, 0), 0.2), mat="fur")                                # shaggy mane
    f.paint(f.poly([(x - 5, y - 6), (x - 3, y - 18), (x + 2, y - 7)]), mix(fur, (0, 0, 0), 0.15), mat="fur")   # ears
    f.paint(f.ell(x, y, 8, 8), fur, mat="fur")
    f.paint(f.poly([(x + 2, y - 3), (x + 15, y - 1), (x + 17, y + 2), (x + 14, y + 7), (x + 2, y + 7)]), mix(fur, (255, 255, 255), 0.15), mat="fur")
    f.paint(f.ell(x + 16, y + 0.5, 1.6, 1.4), (25, 20, 20), mat="flat", outline=0)                        # nose
    f.paint(f.poly([(x + 6, y + 5), (x + 14, y + 5), (x + 13, y + 6.5), (x + 6, y + 6.5)]), (240, 235, 220), mat="bone", outline=0.4)  # fangs
    f.paint(f.poly([(x - 1, y - 7), (x + 1, y - 17), (x + 5, y - 7)]), fur, mat="fur")
    eyes(f, x + 4, y - 2.5, (255, 210, 60), glow=True)
    if hood:
        return "hood"
    return hat if hat in ("cap",) else None


def face_forsaken(f, x, y, hat=None, beard=None, hood=False, hair=None):
    sk = U.HSKIN
    f.paint(f.ell(x, y, 8, 9), sk, mat="skin")
    f.paint(f.poly([(x + 1, y + 2), (x + 9, y + 2), (x + 8, y + 8), (x + 2, y + 8)]), (60, 45, 45), mat="flat", outline=0.4)   # rotted jaw
    for k in range(3):
        f.paint(f.poly([(x + 2 + k * 2.2, y + 3.5), (x + 3.4 + k * 2.2, y + 3.5), (x + 3.4 + k * 2.2, y + 6.5), (x + 2 + k * 2.2, y + 6.5)]),
                BONE, mat="bone", outline=0)
    f.paint(f.ell(x + 6.5, y - 0.5, 1.3, 1.6), (40, 30, 30), mat="flat", outline=0)                        # missing nose
    f.paint(f.ell(x + 4, y - 2.5, 2.2, 2), (30, 25, 25), mat="flat", outline=0)                            # sunken eye
    eyes(f, x + 4, y - 2.5, (255, 230, 90), glow=True, r=1.1)
    if hood:
        return "hood"
    if hat in (None, "hair", "cap"):
        for dx in (-7, -4, -1):
            f.paint(f.curve([(x + dx + 3, y - 9), (x + dx - 2, y - 2), (x + dx - 3, y + 8)], 1.0, 0.5), U.HAIR, mat="fur", outline=0.3)
        return None
    return hat


def face_skeleton(f, x, y, hat=None, beard=None, hood=False, hair=None):
    b = U.HSKIN
    f.paint(f.ell(x, y - 1, 8, 8.5), b, mat="bone")
    f.paint(f.poly([(x, y + 3), (x + 9, y + 3), (x + 8, y + 9), (x + 1, y + 9)]), b, mat="bone")           # jaw
    f.paint(f.poly([(x + 2, y + 5.5), (x + 9, y + 5.5), (x + 9, y + 6.5), (x + 2, y + 6.5)]), (35, 35, 45), mat="flat", outline=0)
    f.paint(f.ell(x + 4, y - 2, 2.6, 2.6), (20, 20, 30), mat="flat", outline=0)                            # socket
    f.paint(f.ell(x + 7.5, y + 1, 1.2, 1.4), (20, 20, 30), mat="flat", outline=0)
    eyes(f, x + 4, y - 2, (120, 200, 255), glow=True, r=1.2)
    if hood:
        return "hood"
    return None if hat in (None, "hair", "cap") else ("saronite" if hat == "kettle" else hat)


def face_goblin(f, x, y, hat=None, beard=None, hood=False, hair=None):
    sk = U.HSKIN
    f.paint(f.poly([(x - 4, y - 2), (x - 23, y - 9), (x - 20, y - 3), (x - 4, y + 4)]), sk, mat="skin")      # huge ear
    f.paint(f.ell(x, y, 8.5, 8), sk, mat="skin")
    f.paint(f.poly([(x + 5, y - 2), (x + 17, y + 3), (x + 15, y + 6), (x + 5, y + 4)]), sk, mat="skin", outline=0.5)   # long nose
    f.paint(f.curve([(x + 2, y + 5), (x + 7, y + 7), (x + 11, y + 6)], 0.7), (40, 30, 25), mat="flat", outline=0)       # grin
    eyes(f, x + 4, y - 2, (255, 215, 80), glow=True, r=1.2)
    if hood:
        return "hood"
    if hat in (None, "hair"):
        f.paint(f.poly([(x - 7, y - 4), (x - 3, y - 9), (x + 4, y - 8), (x + 1, y - 6)]), U.HAIR, mat="fur")
        return None
    if hat == "kettle":
        return "hardhat"
    return hat


# ================================================================== big-bodied faces (orc frame)
def bface_tauren(f, x, y, hair="topknot", helm=False):
    fur = U.OSKIN
    f.paint(f.ell(x - 7, y + 1, 9, 11), U.OHAIR, mat="fur")                                                  # mane
    f.paint(f.poly([(x - 6, y - 4), (x - 17, y - 7), (x - 6, y + 1)]), fur, mat="fur", dark=0.9)            # ear
    f.paint(f.ell(x, y - 1, 10, 10), fur, mat="fur")
    f.paint(f.poly([(x + 2, y - 4), (x + 15, y - 1), (x + 18, y + 7), (x + 12, y + 12), (x + 2, y + 9)]), mix(fur, (255, 240, 220), 0.25), mat="fur")
    f.paint(f.ell(x + 15, y + 4, 1.4, 1.2), (30, 20, 20), mat="flat", outline=0)                          # nostril
    f.paint(f.ell(x + 17, y + 7, 2.2, 2.2), U.GOLD, mat="gold", outline=0.5)                              # nose ring
    eyes(f, x + 6, y - 3, (35, 25, 20))
    # horns sweeping forward and up
    for s, k in ((-4, 0.8), (2, 1.0)):
        f.paint(f.curve([(x + s, y - 8), (x + s - 6, y - 17), (x + s - 1, y - 25), (x + s + 7, y - 26)], 3.0, 1.0), BONE, mat="bone",
                outline=0.6, dark=k)
    if hair == "topknot":     # braided forelock
        f.paint(f.curve([(x + 1, y - 9), (x + 4, y - 3), (x + 3, y + 3)], 1.6, 1.0), U.OHAIR, mat="fur", outline=0.4)


def bface_troll(f, x, y, hair="topknot", helm=False, zandalari=False):
    sk = U.OSKIN
    f.paint(f.poly([(x - 5, y - 2), (x - 25, y - 14), (x - 21, y - 8), (x - 4, y + 4)]), sk, mat="skin", dark=0.92)   # long ear
    f.paint(f.ell(x, y - 1, 9, 9.5), sk, mat="skin")
    f.paint(f.poly([(x - 1, y + 1), (x + 12, y + 1), (x + 15, y + 8), (x + 8, y + 12), (x - 1, y + 10)]), sk, mat="skin")
    f.paint(f.poly([(x + 7, y - 3), (x + 18, y + 3), (x + 12, y + 4)]), sk, mat="skin", outline=0.5)      # long nose
    f.paint(f.curve([(x + 10, y + 9), (x + 16, y + 4), (x + 14, y - 5)], 2.2, 0.6), BONE, mat="bone", outline=0.6)   # tusks
    f.paint(f.curve([(x + 4, y + 9), (x + 7, y + 5), (x + 6, y + 1)], 1.5, 0.5), BONE, mat="bone", outline=0.5, dark=0.85)
    eyes(f, x + 6, y - 2, (255, 150, 70), glow=True)
    if zandalari:     # gold ear cuffs and a diadem
        f.paint(f.ell(x - 13, y - 6, 2.4, 2.4), U.GOLD, mat="gold", outline=0.5)
        f.paint(f.poly([(x - 7, y - 8), (x + 9, y - 8), (x + 8, y - 5), (x - 7, y - 5)]), U.GOLD, mat="gold", outline=0.5)
    if hair in ("topknot", "mohawk", None) and not helm:
        f.paint(f.curve([(x + 6, y - 9), (x, y - 21), (x - 12, y - 19), (x - 16, y - 10)], 4.2, 2.0), U.OHAIR, mat="fur")


def bface_zandalari(f, x, y, hair="topknot", helm=False):
    bface_troll(f, x, y, hair, helm, zandalari=True)


def bface_panda(f, x, y, hair="topknot", helm=False):
    white, black = (238, 234, 226), (42, 38, 36)
    for ex in (-6, 4):
        f.paint(f.ell(x + ex, y - 10, 3.8, 3.8), black, mat="fur")
    f.paint(f.ell(x, y - 1, 11, 10), white, mat="fur")
    f.paint(f.ell(x + 6, y - 2, 3.6, 2.8, rot=0.4), black, mat="fur", outline=0)                         # eye patch
    eyes(f, x + 6.5, y - 2.3, (250, 245, 235), r=1.0)
    f.paint(f.ell(x + 10, y + 4, 5, 4), white, mat="fur", outline=0.5)                                   # snout
    f.paint(f.ell(x + 14, y + 2.8, 1.7, 1.3), black, mat="flat", outline=0)
    f.paint(f.curve([(x + 9, y + 6.5), (x + 12, y + 7.5), (x + 14, y + 6)], 0.6), black, mat="flat", outline=0)


def face_naga(f, x, y, hat=None, beard=None, hood=False, hair=None, **k):
    """Naga: an elven face with a webbed fin for an ear and a crest of sea-coloured tendrils."""
    out = face_elf(f, x, y, hat=hat, beard=None, hood=hood, hair=hair, glow=(255, 215, 90), long_hair=True)
    fin = mix(tuple(U.HSKIN), (20, 60, 70), 0.3)
    f.paint(f.poly([(x - 3, y - 2), (x - 20, y - 15), (x - 16, y - 10), (x - 22, y - 8), (x - 15, y - 4), (x - 19, y + 1), (x - 3, y + 4)]),
            fin, mat="skin", outline=0.5)
    return out


def bface_highmountain(f, x, y, hair="topknot", helm=False):
    """Highmountain tauren: a tauren face crowned with broad moose antlers instead of horns."""
    fur = U.OSKIN
    f.paint(f.ell(x - 7, y + 1, 9, 11), U.OHAIR, mat="fur")
    f.paint(f.poly([(x - 6, y - 4), (x - 17, y - 7), (x - 6, y + 1)]), fur, mat="fur", dark=0.9)
    f.paint(f.ell(x, y - 1, 10, 10), fur, mat="fur")
    f.paint(f.poly([(x + 2, y - 4), (x + 15, y - 1), (x + 18, y + 7), (x + 12, y + 12), (x + 2, y + 9)]), mix(fur, (255, 240, 220), 0.25), mat="fur")
    f.paint(f.ell(x + 15, y + 4, 1.4, 1.2), (30, 20, 20), mat="flat", outline=0)
    eyes(f, x + 6, y - 3, (35, 25, 20))
    ant = (210, 196, 158)
    for s, k in ((-5, 0.8), (1, 1.0)):
        f.paint(f.poly([(x + s, y - 8), (x + s - 6, y - 16), (x + s - 4, y - 24), (x + s + 4, y - 26), (x + s + 8, y - 20), (x + s + 3, y - 12)]),
                ant, mat="bone", outline=0.6, dark=k)
        for tx, ty in ((-6, -26), (-1, -30), (5, -29), (10, -24)):
            f.paint(f.curve([(x + s + tx * 0.6, y + ty * 0.8), (x + s + tx, y + ty)], 1.4, 0.6), ant, mat="bone", outline=0.4, dark=k)
    if hair == "topknot":
        f.paint(f.curve([(x + 1, y - 9), (x + 4, y - 3), (x + 3, y + 3)], 1.6, 1.0), U.OHAIR, mat="fur", outline=0.4)


def coral_crown(f, x, y):
    """Naga headdress: a gilded crest of coral spines."""
    for i, (dx, h) in enumerate(((-6, 10), (-1, 14), (4, 11))):
        f.paint(f.poly([(x + dx - 2, y - 7), (x + dx, y - 7 - h), (x + dx + 2, y - 7)]), U.GOLD, mat="gold", outline=0.5)
    f.paint(f.poly([(x - 9, y - 4), (x + 9, y - 4), (x + 8, y - 8), (x - 8, y - 8)]), U.GOLD, mat="gold", outline=0.5)


# ================================================================== headgear swaps
def moon_helm(f, x, y):
    """Sentinel helm: a smooth cap with a tall crescent crest."""
    f.paint(f.curve([(x - 6, y - 10), (x - 2, y - 22), (x + 8, y - 24)], 2.2, 0.6), U.STEEL, mat="metal", outline=0.5)
    f.paint(f.poly([(x - 9, y + 2), (x - 9, y - 6), (x - 2, y - 11), (x + 7, y - 10), (x + 11, y - 4), (x + 9, y + 1), (x + 4, y - 3), (x - 4, y + 3)]),
            U.STEEL, mat="metal")
    f.paint(f.ell(x + 2, y - 7, 2, 2), L_MAIN, layer="l1", mat="gold", outline=0.4)


def elf_helm(f, x, y):
    """Elven helm: tall swept crest and cheek guards."""
    f.paint(f.poly([(x - 3, y - 11), (x - 14, y - 22), (x - 6, y - 10)]), U.GOLD, mat="gold", outline=0.5)
    f.paint(f.poly([(x - 9, y + 3), (x - 9, y - 6), (x - 2, y - 11), (x + 7, y - 10), (x + 11, y - 4), (x + 10, y + 2), (x + 5, y - 2), (x - 3, y + 4)]),
            U.STEEL, mat="metal")
    f.paint(f.poly([(x - 8, y - 6), (x + 9, y - 6), (x + 9, y - 4), (x - 8, y - 4)]), L_MAIN, layer="l1", mat="gold", outline=0.4)


def saronite_helm(f, x, y):
    f.paint(f.poly([(x - 10, y + 2), (x - 9, y - 8), (x, y - 12), (x + 10, y - 8), (x + 11, y + 2), (x + 5, y - 1), (x - 3, y + 3)]), U.STEEL, mat="metal")
    for sx_ in (-6, 0, 6):
        f.paint(f.poly([(x + sx_ - 2, y - 10), (x + sx_, y - 20), (x + sx_ + 2, y - 10)]), U.DSTEEL, mat="metal", outline=0.5)
    eyes(f, x + 5, y - 2, (120, 200, 255), glow=True, r=1.2)


def hardhat(f, x, y):
    f.paint(f.ell(x + 1, y - 5, 12, 2.6), (200, 160, 40), mat="metal")
    f.paint(f.ell(x, y - 8, 8.5, 6), (235, 190, 50), mat="metal")
    f.paint(f.ell(x + 6, y - 9, 2.4, 2), (255, 240, 170), mat="glow", outline=0.4)          # lamp


def kasa(f, x, y):
    """Pandaren conical straw hat."""
    f.paint(f.poly([(x - 18, y - 8), (x + 1, y - 22), (x + 20, y - 8), (x + 1, y - 11)]), (215, 185, 120), mat="wood")
    f.paint(f.curve([(x - 16, y - 8.5), (x + 1, y - 11.5), (x + 18, y - 8.5)], 0.8), L_MAIN, layer="l2", mat="cloth", outline=0)


def draenei_helm(f, x, y):
    f.paint(f.poly([(x - 9, y + 2), (x - 9, y - 6), (x - 2, y - 11), (x + 7, y - 10), (x + 11, y - 4), (x + 9, y + 1), (x + 4, y - 3), (x - 4, y + 3)]),
            U.STEEL, mat="metal")
    f.paint(f.poly([(x - 1, y - 11), (x + 2, y - 18), (x + 4, y - 11)]), (150, 220, 255), mat="glow", outline=0.5)   # crystal
    draenei_horns(f, x, y)


def _swapper(table):
    """hat_swap from {kind: replacement}: a callable draws a race helm, None removes the
    hat, a string swaps to another stock hat, and kinds not listed are kept."""
    def swap(f, x, y, kind):
        if kind not in table:
            return kind
        new = table[kind]
        if callable(new):
            new(f, x, y)
            return None
        return new
    return swap


def _helm_swap(table):
    sw = _swapper(table)

    def swap(f, x, y, kind):
        return sw(f, x, y, kind)
    return swap


HELMS = ("sallet", "plumed", "great_helm", "kettle", "warhelm", "skullcap")


def all_helms(fn, extra=None):
    t = {k: fn for k in HELMS}
    t.update(extra or {})
    return t


# hats drawn inside human_head that a face passes on as new names
INNER = {"goggles_cap": "goggles", "elf_helm": elf_helm, "saronite": saronite_helm, "hardhat": hardhat}


# ================================================================== mounts
def _mount_mat(part):
    if part in ("bard", "helm", "spike", "plate", "rivet", "rim", "frame", "rail", "fork", "plow", "exhaust", "hub", "hubnear",
                "hubfar", "wheel", "wheelnear", "wheelfar", "shell"):
        return "metal"
    if part in ("horn", "tusk", "fang", "quill", "beak", "toe", "frill"):
        return "bone"
    if part in ("saddle",):
        return "leather"
    if part in ("blanket", "trim"):
        return "cloth"
    if part in ("eye", "nose", "lamp", "whisker", "h", "smoke"):
        return "flat"
    return "skin"


class MountPainter:
    """Lets the mount designs in mounts.py (written for a small cell canvas, facing left)
    draw onto the pixel canvas, facing right. Consecutive strokes of one colour and part
    are merged into one shape before painting."""
    s = 1.0

    def __init__(self, c, ox, oy, k):
        self.c, self.ox, self.oy, self.k = c, ox, oy, k
        self.cur, self.mask = None, None

    def X(self, x):
        return self.ox + (MT.W - x) * self.k

    def Y(self, y):
        return self.oy + y * self.k

    def _add(self, m, col, part, layer):
        key = (tuple(int(v) for v in col), part, layer)
        if key != self.cur:
            self.flush()
            self.cur, self.mask = key, m
        else:
            self.mask = self.c.union(self.mask, m)

    def flush(self):
        if self.cur:
            col, part, layer = self.cur
            mat = _mount_mat(part)
            self.c.paint(self.mask, col if layer == 0 else L_MAIN, layer=("base", "l1", "l2")[layer], mat=mat,
                         outline=0 if mat == "flat" else 1.0)
        self.cur, self.mask = None, None

    def dot(self, x, y, col, part, layer=0):
        r = max(0.8 * self.k, 2.2)
        self._add(self.c.ellipse(self.X(x + 0.5), self.Y(y + 0.5), r, r), col, part, layer)

    def ell(self, cx, cy, rx, ry, col, part, layer=0):
        self._add(self.c.ellipse(self.X(cx), self.Y(cy), max(rx, 0.6) * self.k, max(ry, 0.6) * self.k), col, part, layer)

    def poly(self, pts, col, part, layer=0):
        self._add(self.c.poly([(self.X(x), self.Y(y)) for x, y in pts]), col, part, layer)

    def line(self, x0, y0, x1, y1, wd, col, part, layer=0):
        r = max(wd, 1.4) * self.k / 2
        self._add(self.c.capsule((self.X(x0), self.Y(y0)), (self.X(x1), self.Y(y1)), r), col, part, layer)

    def leg(self, x, top, length, wd, col, part, bend=0, hoof=None):
        mid = top + length * .5
        self.line(x, top, x + bend, mid, wd, col, part)
        self.line(x + bend, mid, x + bend * .3, top + length, max(1, wd - 1), col, part)
        if hoof:
            self.line(x + bend * .3 - 1, top + length, x + bend * .3 + max(1, wd - 1) - 1, top + length, 1.6, hoof, part + "h")


def make_mount(race, variant_key):
    fn = MT.RACE_MOUNT[race]
    scale = MT.SCALE.get(race, 1.2)

    def draw(c, f, armored=False):
        k = 1.62 * scale * f.u
        ox = f.fx - (MT.W / 2) * k
        oy = f.fy - MT.GY * k
        p = MountPainter(c, ox, oy, k)
        sx, sy = fn(p, zlib.crc32(variant_key.encode()) % 4, armored)
        p.flush()
        return p.X(sx), p.Y(sy)
    return draw


# ================================================================== races
SH = 0.95   # head size for slender races

RACES = {
    "Dwarves": dict(family="human", body=(1.18, 0.8), head=1.15, face=face_dwarf,
                    hats=all_helms(lambda f, x, y: dwarf_helm(f, x, y), {"tricorn": None, "officer": None}),
                    colors=dict(skin=(232, 172, 138), hair=[(155, 82, 40), (110, 62, 32), (70, 46, 32), (205, 150, 80), (150, 150, 150)],
                                gold=(215, 165, 80)),
                    weapons={"sword": "hammer", "halberd": "axe"}),
    "Dark Iron Dwarves": dict(family="human", body=(1.18, 0.8), head=1.15, face=face_dwarf,
                              hats=all_helms(lambda f, x, y: dwarf_helm(f, x, y, crest=True), {"tricorn": None, "officer": None}),
                              colors=dict(skin=(170, 156, 160), hair=[(56, 48, 50), (82, 70, 68)], steel=(166, 156, 156),
                                          dsteel=(112, 102, 102), gold=(255, 145, 55), leather=(108, 78, 58), dleather=(76, 56, 44)),
                              weapons={"sword": "hammer", "halberd": "axe"}),
    "Gnomes": dict(family="human", body=(0.86, 0.62), head=1.0, face=face_gnome,
                   hats=all_helms("goggles", {"tricorn": "goggles", "officer": "goggles"}),
                   colors=dict(skin=(242, 202, 176), hair=[(240, 110, 170), (80, 200, 200), (232, 232, 242), (170, 110, 220), (250, 200, 80)],
                               steel=(192, 202, 218)),
                   weapons={"sword": "hammer"}),
    "Night Elves": dict(family="human", body=(0.95, 1.12), head=SH,
                        face=lambda f, x, y, **k: face_elf(f, x, y, glow=(225, 240, 255), brows=True, **k),
                        hats=all_helms(moon_helm, {"tricorn": None, "officer": None, "goggles": None, "elf_helm": moon_helm}),
                        colors=dict(skin=[(140, 110, 192), (122, 96, 178), (158, 120, 202)],
                                    hair=[(40, 172, 172), (222, 226, 242), (72, 142, 92), (62, 92, 172)],
                                    steel=(160, 150, 195), dsteel=(104, 94, 142), leather=(92, 72, 108), dleather=(62, 48, 76),
                                    cloth_tan=(165, 152, 195), cloth_brown=(96, 82, 120), gold=(200, 220, 240)),
                        weapons={"musket": "bow", "rifle": "bow", "sniper": "bow", "sword": "glaive", "grenade": "bow"}),
    "High Elves": dict(family="human", body=(0.94, 1.07), head=SH,
                       face=lambda f, x, y, **k: face_elf(f, x, y, glow=(150, 205, 255), **k),
                       hats=all_helms(elf_helm, {"tricorn": None, "officer": None}),
                       colors=dict(skin=(246, 216, 186), hair=[(246, 226, 150), (250, 240, 205), (182, 122, 62), (42, 40, 40)],
                                   steel=(216, 222, 236), gold=(240, 210, 110))),
    "Blood Elves": dict(family="human", body=(0.94, 1.07), head=SH,
                        face=lambda f, x, y, **k: face_elf(f, x, y, glow=(140, 255, 120), **k),
                        hats=all_helms(elf_helm, {"tricorn": None, "officer": None}),
                        colors=dict(skin=(246, 212, 182), hair=[(240, 200, 110), (205, 62, 42), (250, 240, 212), (62, 42, 32)],
                                    steel=(210, 170, 96), dsteel=(150, 44, 40), gold=(250, 212, 92), leather=(130, 50, 40))),
    "Draenei": dict(family="human", body=(1.05, 1.12), head=1.0, face=face_draenei,
                    hats=all_helms(draenei_helm, {"tricorn": None, "officer": None}),
                    colors=dict(skin=[(112, 122, 202), (142, 112, 192), (92, 132, 192)], hair=[(40, 40, 62), (222, 222, 236), (62, 92, 142)],
                                steel=(192, 202, 228), gold=(232, 222, 150), leather=(92, 82, 112))),
    "Worgen": dict(family="human", body=(1.08, 1.06), head=1.05, face=face_worgen,
                   hats=all_helms(None, {"tricorn": "tricorn", "officer": "officer"}),
                   colors=dict(skin=[(92, 82, 72), (62, 56, 52), (122, 102, 82), (152, 146, 140)],
                               hair=[(92, 82, 72), (62, 56, 52), (122, 102, 82), (152, 146, 140)],
                               leather=(102, 72, 52), steel=(152, 156, 162))),
    "Forsaken": dict(family="human", body=(0.92, 1.0), head=SH, face=face_forsaken, hats={"plumed": "sallet"},
                     colors=dict(skin=(178, 194, 162), hair=[(104, 104, 104), (136, 128, 120), (74, 72, 72)],
                                 steel=(158, 156, 146), dsteel=(108, 106, 98), leather=(102, 88, 72), dleather=(72, 62, 52),
                                 gold=(176, 205, 85), cloth_tan=(160, 148, 122))),
    "Scourge": dict(family="human", body=(0.95, 1.0), head=SH, face=face_skeleton,
                    hats=all_helms(saronite_helm, {"tricorn": saronite_helm, "officer": saronite_helm, "goggles": saronite_helm}),
                    colors=dict(skin=(226, 226, 212), hair=(60, 60, 70), steel=(112, 132, 148), dsteel=(62, 74, 88),
                                gold=(140, 205, 245), leather=(62, 56, 62), dleather=(42, 38, 44), cloth_tan=(90, 90, 105),
                                cloth_brown=(70, 70, 80))),
    "Goblins": dict(family="human", body=(0.86, 0.66), head=1.0, face=face_goblin,
                    hats=all_helms(hardhat, {"tricorn": "tricorn", "officer": hardhat}),
                    colors=dict(skin=(112, 172, 62), hair=(40, 40, 40), steel=(170, 165, 155), gold=(240, 200, 70))),
    "Kul Tirans": dict(family="human", body=(1.12, 1.04), head=1.0,
                       face=lambda f, x, y, **k: face_human(f, x, y, always_beard=True, **k),
                       colors=dict(skin=[(236, 186, 146), (202, 152, 112), (162, 112, 82)],
                                   hair=[(110, 70, 35), (150, 70, 40), (60, 45, 35), (170, 170, 170)])),
    "Tauren": dict(family="brute", body=(1.2, 1.1), head=1.1, bface=bface_tauren,
                   hats=all_helms(None, {"tricorn": None, "hood": "hood"}),
                   colors=dict(oskin=[(140, 96, 60), (102, 72, 46), (172, 142, 112), (64, 54, 48)], ohair=(60, 42, 30),
                               iron=(122, 102, 82)),
                   weapons={"axe": "hammer", "cleaver": "hammer"}),
    "Trolls": dict(family="brute", body=(0.9, 1.12), head=SH, bface=bface_troll,
                   hats=all_helms(None, {"tricorn": None}),
                   colors=dict(oskin=[(72, 142, 172), (92, 162, 152), (82, 122, 172)],
                               ohair=[(205, 52, 42), (240, 150, 40), (62, 162, 82), (222, 222, 232)])),
    "Zandalari Trolls": dict(family="brute", body=(0.95, 1.18), head=0.98, bface=bface_zandalari,
                             hats=all_helms(None, {"tricorn": None}),
                             colors=dict(oskin=(72, 152, 162), ohair=[(232, 232, 238), (205, 62, 42)], gold=(250, 205, 80),
                                         iron=(205, 170, 90))),
    "Pandaren": dict(family="brute", body=(1.08, 0.95), head=1.1, bface=bface_panda,
                     hats=all_helms(kasa, {"tricorn": kasa, "hood": kasa}),
                     colors=dict(oskin=(74, 66, 62), ohair=(44, 40, 38), iron=(122, 112, 92), cloth_tan=(212, 182, 122),
                                 leather=(132, 82, 52)),
                     weapons={"axe": "halberd", "cleaver": "halberd"}),
    "Naga": dict(family="human", body=(1.04, 1.12), head=1.0, face=face_naga,
                 hats=all_helms(coral_crown, {"tricorn": None, "officer": None, "goggles": coral_crown, "hood": coral_crown}),
                 colors=dict(skin=[(70, 160, 150), (60, 140, 120), (90, 150, 175)],
                             hair=[(40, 170, 150), (150, 60, 150), (225, 205, 95), (60, 90, 160)],
                             steel=(200, 170, 110), dsteel=(140, 110, 70), gold=(240, 205, 90), leather=(60, 100, 95),
                             dleather=(40, 70, 70), cloth_tan=(120, 170, 160), cloth_brown=(60, 90, 90)),
                 weapons={"musket": "spear", "rifle": "spear", "sniper": "spear", "grenade": "spear", "sword": "halberd"},
                 tail=True),
    "Nightborne": dict(family="human", body=(0.95, 1.14), head=SH,
                       face=lambda f, x, y, **k: face_elf(f, x, y, glow=(200, 150, 255), brows=True, **k),
                       hats=all_helms(elf_helm, {"tricorn": None, "officer": None, "goggles": None}),
                       colors=dict(skin=[(150, 150, 205), (130, 135, 195), (168, 160, 214)],
                                   hair=[(236, 236, 246), (160, 120, 225), (70, 70, 120), (205, 190, 240)],
                                   steel=(200, 186, 140), dsteel=(110, 80, 150), gold=(240, 200, 110),
                                   leather=(80, 60, 110), dleather=(55, 40, 80), cloth_tan=(150, 120, 200), cloth_brown=(80, 60, 120)),
                       weapons={"musket": "bow", "rifle": "bow", "sniper": "bow", "grenade": "bow"}),
    "Highmountain Tauren": dict(family="brute", body=(1.24, 1.12), head=1.1, bface=bface_highmountain,
                                hats=all_helms(None, {"tricorn": None, "hood": "hood"}),
                                colors=dict(oskin=[(112, 82, 58), (88, 66, 50), (140, 112, 86), (98, 92, 86)], ohair=(52, 40, 32),
                                            iron=(132, 112, 90), gold=(120, 200, 225)),
                                weapons={"cleaver": "axe"}),
}
for _r, _s in RACES.items():
    _s["hats"] = {**{k: INNER[k] for k in INNER}, **_s.get("hats", {})}


def set_race(race, unit):
    """Point CTX at `race` for drawing `unit` (colours vary per unit within the race)."""
    s = RACES[race]
    CTX.race = race
    CTX.colors = {k: pick(v, race, unit, k) for k, v in s.get("colors", {}).items()}
    CTX.spec = {"family": s["family"], "body": s["body"], "head": s["head"],
                "face": s.get("face"), "bface": s.get("bface"),
                "hat_swap": _swapper(s["hats"]), "helm_swap": _helm_swap(s["hats"]), "draw_hat": M.human_hat,
                "mount": make_mount(race, race + unit), "tail": s.get("tail", False)}


def clear_race():
    CTX.race, CTX.spec, CTX.colors = None, {}, {}


# ================================================================== generic recipes per body family
def _f(fn, *a, **kw):
    return lambda c, fx, fy, u: fn(c, fx, fy, u, *a, **kw)


GENERIC = ["Archer", "Azerite Sharpshooter", "Ballista", "Catapult", "Cavalry", "Gladiator", "Great Admiral",
           "Great Artist", "Great Engineer", "Great General", "Great Merchant", "Great Prophet", "Great Scientist",
           "Grenadier", "Hunter", "Inquisitor", "Knight", "Kul Tiran Marine", "Lancer", "Man-at-Arms", "Militia",
           "Missionary", "Mortar Team", "Mountaineer", "Mounted Archer", "Outrider", "Peasant", "Pikeman", "Ranger",
           "Ranger Captain", "Ranger-General", "Rifleman", "Royal Guard", "Scout", "Settler", "Siegebreaker",
           "Skyguard", "Spearman", "Swordsman", "Vanguard", "Vanquisher",
           "War Rider", "Grand Champion", "Halberdier", "Phalanx"]


def base_recipe(family, unit):
    """(draw, archetype) for a generic unit, before the race's own changes."""
    R = M.RECIPES
    if family == "human":
        special = {"Peasant": (_f(U.peasant), "civ"), "Settler": (_f(U.settler_h), "civ"), "Missionary": (_f(U.priest), "civ"),
                   "Militia": (_f(U.militia), "foot"), "Archer": (_f(U.archer), "foot"), "Spearman": (_f(U.spearman), "foot"),
                   "Knight": (_f(M.h_rider, "knight"), "mounted"), "Cavalry": (_f(M.h_rider, "cavalry"), "mounted"),
                   "Great Scientist": (R["Archmage"][0].but(hair=U.HAIR, beard=U.HAIR), "civ"),
                   "Catapult": (_f(M.catapult, "Humans"), "siege"), "Ballista": (_f(M.ballista, "Humans"), "siege"),
                   "Mortar Team": (_f(M.mortar_team, "Humans"), "siege")}
        return special.get(unit) or R[unit + "-Humans"]
    special = {"Peasant": (_f(U.peon), "civ"), "Settler": (_f(U.settler_o), "civ"), "Missionary": (_f(U.shaman), "civ"),
               "Militia": (_f(U.militia_o), "foot"), "Archer": (_f(U.archer_o), "foot"), "Spearman": (_f(U.spearman_o), "foot"),
               "Outrider": (_f(M.o_rider, "outrider"), "mounted"), "Cavalry": (_f(M.o_rider, "cavalry"), "mounted"),
               "Catapult": (_f(M.catapult, "Orcs"), "siege"), "Ballista": (_f(M.ballista, "Orcs"), "siege"),
               "Mortar Team": (_f(M.mortar_team, "Orcs"), "siege")}
    return special.get(unit) or R[unit + "-Orcs"]


def race_recipe(race, unit):
    draw, arch = base_recipe(RACES[race]["family"], unit)
    swaps = RACES[race].get("weapons", {})
    if isinstance(draw, M.R) and draw.kw.get("weapon") in swaps:
        new = swaps[draw.kw["weapon"]]
        changes = {"weapon": new}
        if new == "bow" and draw.kw.get("back") in ("bandolier", "pack", None):
            changes["back"] = "quiver"
        draw = draw.but(**changes)
    return draw, arch


def recipes():
    """{sprite name: (race, unit, draw, archetype)} for every race and generic unit."""
    out = {}
    import wc_lines
    for race in RACES:
        for unit in GENERIC + list(wc_lines.SCHOOL_RACES) + ["Warbringer"]:
            if race not in wc_lines.SCHOOL_RACES.get(unit, [race]):
                continue          # magic schools: only their own races
            out[unit + "-" + race] = (race, unit) + race_recipe(race, unit)
    try:
        import wc_style_uniques as UQ
        for name, (race, draw, arch) in UQ.RECIPES.items():
            out[name] = (race, name, draw, arch)
    except ImportError:
        pass
    return out


# ================================================================== output
def render(name, ref_path, entry=None):
    from PIL import Image
    from pixelize import make_canvas
    race, unit, draw, arch = entry or recipes()[name]
    ref = Image.open(ref_path)
    w, h = ref.size
    x0, y0, x1, y1 = ref.getbbox()
    nom, lo, hi = M.SCALE[arch]
    sy = RACES[race]["body"][1]
    u = max(lo, min(hi, 2 * (y1 - y0) / nom)) / max(1.0, sy * 0.92)
    fx, fy = (x0 + x1), 2 * y1 + (2 if arch == "mounted" else 4)
    fy = min(fy, 2 * h - 2)
    top_room = {"foot": 112, "civ": 110, "mounted": 150, "siege": 72}[arch] * max(1.0, sy)
    if fy - top_room * u < 2:
        u = max(0.5, (fy - 2) / top_room)
    c = make_canvas(2 * w, 2 * h)
    set_race(race, unit)
    try:
        draw(c, fx, fy, u)
    finally:
        clear_race()
    return c.finish()


def _job(name, ref):
    return render(name, ref)


def write_all(image_dirs, only=None):
    """Overwrite every race sprite (and its era variants) with the pixel-art version."""
    import os
    from multiprocessing import Pool
    entries = recipes()
    jobs = []
    for name in entries:
        if only and entries[name][0] not in only:
            continue
        ref = M._find(image_dirs, name)
        if ref is None:
            print("race pixel art: no reference sprite for", name)
            continue
        jobs.append((name, ref))
    with Pool(min(8, os.cpu_count() or 2)) as pool:
        rendered = pool.starmap(_job, jobs)
    count = 0
    for (name, ref), layers in zip(jobs, rendered):
        targets = set()
        for d in image_dirs:
            folder = os.path.join(d, M.UNIT_DIR)
            if not os.path.isdir(folder):
                continue
            for fname in os.listdir(folder):
                stem = fname[:-4]
                if stem.endswith("-1") or stem.endswith("-2"):
                    stem = stem[:-2]
                if stem == name or (stem.startswith(name + "-") and stem[len(name) + 1:].startswith("Age of")):
                    targets.add((folder, stem))
        for folder, stem in targets:
            for suf, im in zip(("", "-1", "-2"), layers):
                im.save(os.path.join(folder, stem + suf + ".png"))
                count += 1
    return count
