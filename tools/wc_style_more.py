"""The rest of the Human and Orc roster in the painted style (v0.17).

Built from a kit of parts on top of wc_style_units.py: each unit is a short recipe
(body armour, headgear, weapon, shield, back item) drawn by one of a few posed
figures - foot soldier, gunner, robed civilian, rider - or a siege engine. All designs
are original; they follow the broad Warcraft look, not any specific Blizzard unit.
"""
import math
from wc_style_units import *          # noqa: F401,F403  (shared palette, parts and Fig)
from wc_style_units import Fig, frame, CTX, headfig, HAIR, sword, kite_shield, spear
from paint import mix, grey

BRASS = (205, 165, 80)
NAVY = (40, 50, 80)
RED = (170, 40, 35)
OIRON = (95, 88, 84)        # orcish black iron
WARPAINT = (150, 30, 25)


# ================================================================== weapons and props
def long_gun(f, butt, muzzle, rifle=False, bayonet=False, scope=False, color=WOOD):
    """Musket/rifle from the butt of the stock to the muzzle."""
    T = frame(butt, muzzle)
    L = math.hypot(muzzle[0] - butt[0], muzzle[1] - butt[1])
    # stock (wood) for the rear 45%, barrel (iron) the rest
    f.paint(f.poly([T(-L, -2.8), T(-L * 0.55, -2.2), T(-L * 0.55, 1.6), T(-L, 3.6)]), color, mat="wood")
    f.paint(f.cap(T(-L * 0.6, -0.4), T(0, -0.4), 1.6 if not rifle else 1.4), DSTEEL, mat="metal")
    f.paint(f.cap(T(-L * 0.62, 0.2), T(-L * 0.3, 0.6), 1.9), color, mat="wood", outline=0.5)
    if rifle:
        f.paint(f.cap(T(-L * 0.5, -1.8), T(-L * 0.4, -1.8), 1.0), BRASS, mat="gold", outline=0.4)
    if scope:
        f.paint(f.cap(T(-L * 0.5, -3.6), T(-L * 0.2, -3.6), 1.5), BRASS, mat="gold", outline=0.5)
    if bayonet:
        f.paint(f.poly([T(-1, -1.8), T(9, -0.4), T(-1, 0.8)]), STEEL, mat="metal", outline=0.5)


def crossbow(f, butt, tip):
    T = frame(butt, tip)
    L = math.hypot(tip[0] - butt[0], tip[1] - butt[1])
    f.paint(f.cap(T(-L, 0), T(0, 0), 2.0), WOOD, mat="wood")
    f.paint(f.curve([T(-3, -11), T(1, 0), T(-3, 11)], 1.8, 1.8), DSTEEL, mat="metal")
    for s in (-11, 11):
        f.paint(f.cap(T(-3, s), T(-L * 0.5, 0), 0.4), (235, 230, 215), mat="flat", outline=0)
    f.paint(f.cap(T(-L * 0.5, -0.5), T(2, -0.5), 0.8), (200, 200, 205), mat="metal", outline=0.3)


def halberd(f, base, top, blade=IRON):
    pole(f, base, top, 1.7)
    T = frame(base, top)
    f.paint(f.poly([T(-3, 1), T(-14, 9), T(-18, 8), T(-12, 1)]), blade, mat="metal", bevel=1.2)
    f.paint(f.poly([T(10, 0), T(-2, 2.4), T(-4, 0), T(-2, -2.4)]), STEEL, mat="metal", bevel=1.2)
    f.paint(f.poly([T(-6, -1), T(-9, -6), T(-11, -1)]), blade, mat="metal", outline=0.5)


def banner(f, base, top, w=14, h=18, emblem=True):
    pole(f, base, top, 1.6)
    tx, ty = top
    m = f.poly([(tx, ty + 2), (tx - w, ty + 2), (tx - w, ty + h), (tx - w / 2, ty + h - 4), (tx, ty + h)])
    f.paint(m, L_MAIN, layer="l2", mat="cloth")
    if emblem:
        f.paint(f.ell(tx - w / 2, ty + h / 2, w * 0.22, w * 0.22), L_MAIN, layer="l1", mat="gold", outline=0.4)
    f.paint(f.ell(tx, ty, 2.2, 2.2), GOLD, mat="gold", outline=0.4)


def warhammer(f, base, top, head=STEEL, glow=None, big=1.0):
    pole(f, base, top, 2.0)
    T = frame(base, top)
    m = f.poly([T(4 * big, -7 * big), T(4 * big, 7 * big), T(-6 * big, 7 * big), T(-6 * big, -7 * big)])
    if glow:
        f.c.glow(m, glow, radius=4, strength=0.7)
    f.paint(m, head, mat="metal", bevel=2)
    f.paint(f.poly([T(-0.5, -7.5 * big), T(-0.5, 7.5 * big), T(-2.5, 7.5 * big), T(-2.5, -7.5 * big)]), GOLD, mat="gold", outline=0.3)


def grenade(f, x, y, r=4.2):
    f.paint(f.ell(x, y, r, r), (60, 58, 62), mat="metal")
    f.paint(f.cap((x + r * 0.4, y - r), (x + r * 0.9, y - r * 1.7), 0.8), (160, 130, 90), mat="flat", outline=0.3)
    spark = f.ell(x + r * 1.0, y - r * 1.9, 1.4, 1.4)
    f.c.glow(spark, (255, 200, 80), radius=2, strength=0.8)
    f.paint(spark, (255, 240, 170), mat="glow", outline=0)


def tube(f, rear, front, r=4.5, col=DSTEEL):
    f.paint(f.cap(rear, front, r * 0.9, r), col, mat="metal")
    fx_, fy_ = front
    f.paint(f.ell(fx_, fy_, r * 0.55, r * 0.9), (30, 26, 26), mat="flat", outline=0.4)


def book(f, x, y, col=(120, 40, 35)):
    f.paint(f.poly([(x - 6, y - 5), (x + 5, y - 7), (x + 6, y + 5), (x - 5, y + 7)]), col, mat="leather")
    f.paint(f.poly([(x - 3, y - 3), (x + 3, y - 4), (x + 3.5, y), (x - 2.5, y + 1)]), GOLD, mat="gold", outline=0.3)


def lute(f, x, y):
    f.paint(f.ell(x, y, 6.5, 5.5, rot=-0.5), (170, 110, 55), mat="wood")
    f.paint(f.ell(x + 0.5, y - 0.5, 1.6, 1.6), (50, 30, 20), mat="flat", outline=0)
    f.paint(f.cap((x + 3, y - 3), (x + 15, y - 12), 1.3), (110, 70, 40), mat="wood")


def coin_bag(f, x, y):
    f.paint(f.ell(x, y, 6, 6.5), (175, 135, 85), mat="leather")
    f.paint(f.cap((x - 3, y - 6), (x + 3, y - 6), 1.2), (120, 85, 50), mat="leather", outline=0.4)
    for dx, dy in ((-2, -1), (1.5, 1), (-0.5, 3)):
        f.paint(f.ell(x + dx, y + dy, 1.5, 1.2), GOLD, mat="gold", outline=0.3)


def spyglass(f, a, b):
    f.paint(f.cap(a, b, 1.6, 2.2), BRASS, mat="gold")


def lantern(f, x, y, glow=(255, 210, 120)):
    f.paint(f.cap((x, y - 9), (x, y - 5), 0.6), (70, 60, 50), mat="flat", outline=0.3)
    m = f.ell(x, y, 3.2, 4.2)
    f.c.glow(m, glow, radius=4, strength=0.8)
    f.paint(m, mix(glow, (255, 255, 255), 0.4), mat="glow", outline=0.5)
    f.paint(f.poly([(x - 3.6, y - 4.5), (x + 3.6, y - 4.5), (x + 2.4, y - 6.4), (x - 2.4, y - 6.4)]), (70, 60, 50), mat="metal", outline=0.3)


def moonglaive(f, x, y, r=13):
    """Night elf moonglaive: three crescent blades around a central grip."""
    for k in range(3):
        a = math.radians(90 + k * 120)
        tip = (x + math.cos(a) * r, y - math.sin(a) * r)
        a2 = a + math.radians(70)
        mid = (x + math.cos(a2) * r * 0.75, y - math.sin(a2) * r * 0.75)
        f.paint(f.curve([(x + math.cos(a) * 3, y - math.sin(a) * 3), mid, tip], 2.6, 0.6), STEEL, mat="metal", outline=0.6)
    f.paint(f.ell(x, y, 3.2, 3.2), LEATHER, mat="leather", outline=0.5)


def walking_stick(f, base, top, col=(120, 82, 48)):
    """A traveller's staff: a stout, slightly crooked wooden stick with a knotted top."""
    from wc_style_units import pole
    mid = ((base[0] + top[0]) / 2 + 1.5, (base[1] + top[1]) / 2)
    pole(f, base, mid, 2.3, col)
    pole(f, mid, top, 2.3, col)
    f.paint(f.ell(top[0], top[1] - 1, 3.4, 3.0), col, mat="wood", dark=0.9)


def wrench(f, base, top):
    f.paint(f.cap(base, top, 1.8), DSTEEL, mat="metal")
    tx, ty = top
    f.paint(f.c.subtract(f.ell(tx, ty, 4.5, 4.5), f.ell(tx + 2, ty - 2, 2.2, 2.2)), DSTEEL, mat="metal")


def drum(f, x, y):
    f.paint(f.ell(x, y, 8, 9), (165, 115, 70), mat="wood")
    f.paint(f.ell(x + 2, y - 1, 5, 7.5), (225, 205, 165), mat="leather", outline=0.5)
    f.paint(f.cap((x - 7, y - 6), (x + 6, y + 6), 0.8), RED, mat="flat", outline=0)


def back_pack(f, x, y, col=CLOTH_BROWN, dark=0.88):
    f.paint(f.poly([(x - 7, y - 10), (x + 5, y - 11), (x + 6, y + 8), (x - 8, y + 8)]), col, mat="leather", dark=dark)
    f.paint(f.cap((x - 8, y - 12), (x + 6, y - 12), 3), DLEATHER, mat="leather", dark=dark)


def cape(f, top_l, top_r, bottom_y, swirl=0, layer="l2", dark=0.85):
    (x0, y0), (x1, y1) = top_l, top_r
    f.paint(f.poly([(x0, y0), (x1, y1), (x1 - 4 + swirl, bottom_y), (x0 - 10 + swirl, bottom_y + 2), (x0 - 12 + swirl, bottom_y - 8)]),
            L_MAIN, layer=layer, mat="cloth", dark=dark)


# ================================================================== headgear
def human_hat(f, kind, x=5, y=-75):
    f, x, y = headfig(f, x, y)
    if CTX.spec.get("hat_swap"):
        kind = CTX.spec["hat_swap"](f, x, y, kind)
        if not kind:
            return
    if kind == "sallet":            # rounded helm with a visor slit
        f.paint(f.poly([(x - 10, y + 4), (x - 10, y - 6), (x - 2, y - 12), (x + 8, y - 10), (x + 12, y - 2), (x + 12, y + 3), (x + 2, y + 1)]),
                STEEL, mat="metal")
        f.paint(f.poly([(x + 2, y - 1), (x + 12, y - 1.5), (x + 12, y + 0.8), (x + 2, y + 1)]), (25, 22, 30), mat="flat", outline=0)
    elif kind == "plumed":          # cavalry helm with a tall plume
        f.paint(f.curve([(x, y - 11), (x - 4, y - 20), (x - 12, y - 22)], 3.2, 1.4), L_MAIN, layer="l2", mat="cloth")
        human_hat(f, "sallet", x, y)
    elif kind == "tricorn":
        f.paint(f.poly([(x - 13, y - 4), (x - 6, y - 13), (x + 6, y - 14), (x + 15, y - 5), (x + 2, y - 7)]), (40, 36, 40), mat="cloth")
        f.paint(f.curve([(x - 12, y - 5), (x + 2, y - 8), (x + 14, y - 6)], 0.9), L_MAIN, layer="l1", mat="gold", outline=0)
    elif kind == "officer":         # brimmed cap
        f.paint(f.ell(x + 2, y - 7, 12, 3), (50, 46, 50), mat="cloth")
        f.paint(f.poly([(x - 8, y - 7), (x - 6, y - 14), (x + 8, y - 14), (x + 10, y - 7)]), L_MAIN, layer="l2", mat="cloth")
        f.paint(f.ell(x + 4, y - 10, 2, 2), L_MAIN, layer="l1", mat="gold", outline=0.4)
    elif kind == "goggles":         # leather aviator cap and goggles
        f.paint(f.poly([(x - 9, y + 2), (x - 9, y - 6), (x - 2, y - 11), (x + 7, y - 9), (x + 9, y - 4), (x - 2, y - 3)]), LEATHER, mat="leather")
        for gx in (x + 2, x + 8):
            f.paint(f.ell(gx, y - 4.5, 2.8, 2.6), BRASS, mat="gold", outline=0.4)
            f.paint(f.ell(gx, y - 4.5, 1.7, 1.6), (120, 200, 220), mat="metal", outline=0)
    elif kind == "feather_cap":     # bard's cap with a feather
        f.paint(f.poly([(x - 10, y - 2), (x - 7, y - 11), (x + 6, y - 12), (x + 13, y - 5), (x + 2, y - 5)]), L_MAIN, layer="l2", mat="cloth")
        f.paint(f.curve([(x - 6, y - 10), (x - 12, y - 18), (x - 20, y - 18)], 1.8, 0.6), (240, 235, 220), mat="cloth", outline=0.5)
    elif kind == "crown":
        f.paint(f.poly([(x - 8, y - 7), (x - 8, y - 14), (x - 4, y - 10), (x, y - 15), (x + 4, y - 10), (x + 8, y - 14), (x + 8, y - 7)]),
                GOLD, mat="gold", outline=0.5)
    elif kind == "mitre":
        f.paint(f.poly([(x - 7, y - 6), (x - 5, y - 19), (x + 1, y - 23), (x + 7, y - 19), (x + 9, y - 6)]), (240, 235, 222), mat="cloth")
        f.paint(f.poly([(x - 1, y - 6), (x + 3, y - 6), (x + 3, y - 21), (x - 1, y - 21)]), L_MAIN, layer="l1", mat="gold", outline=0.3)


def orc_hat(f, kind, x=18, y=-67):
    f, x, y = headfig(f, x, y)
    if CTX.spec.get("hat_swap"):
        kind = CTX.spec["hat_swap"](f, x, y, kind)
        if not kind:
            return
    if kind == "goggles":
        f.paint(f.poly([(x - 9, y - 6), (x + 12, y - 5), (x + 12, y - 2), (x - 9, y - 3)]), LEATHER, mat="leather", outline=0.5)
        f.paint(f.ell(x + 8, y - 4, 3.2, 3), BRASS, mat="gold", outline=0.4)
        f.paint(f.ell(x + 8, y - 4, 2, 1.8), (120, 200, 220), mat="metal", outline=0)
    elif kind == "tricorn":
        f.paint(f.poly([(x - 13, y - 6), (x - 5, y - 15), (x + 7, y - 16), (x + 16, y - 7), (x + 2, y - 9)]), (40, 36, 40), mat="cloth")
        f.paint(f.curve([(x - 12, y - 7), (x + 2, y - 10), (x + 15, y - 8)], 0.9), L_MAIN, layer="l2", mat="cloth", outline=0)
    elif kind == "skullcap":       # iron cap with a single horn crest
        f.paint(f.poly([(x - 10, y - 2), (x - 9, y - 10), (x, y - 14), (x + 10, y - 10), (x + 12, y - 4), (x - 10, y - 1)]), OIRON, mat="metal")
        f.paint(f.poly([(x - 3, y - 13), (x - 8, y - 26), (x + 3, y - 14)]), BONE, mat="bone", outline=0.6)
    elif kind == "warhelm":        # horned iron war helm
        f.paint(f.poly([(x - 10, y - 2), (x - 9, y - 10), (x, y - 14), (x + 10, y - 10), (x + 12, y - 4), (x - 10, y - 1)]), OIRON, mat="metal")
        for s, k in ((-1, 0.85), (1, 1.0)):
            f.paint(f.curve([(x + s * 6, y - 11), (x + s * 13, y - 17), (x + s * 12, y - 27)], 2.6, 0.7), BONE, mat="bone", outline=0.6, dark=k)
    elif kind == "hood":
        f.paint(f.poly([(x - 12, y + 6), (x - 13, y - 6), (x - 4, y - 14), (x + 8, y - 13), (x + 13, y - 7), (x + 6, y - 7), (x - 2, y - 2),
                        (x - 3, y + 8)]), L_MAIN, layer="l2", mat="cloth")
    elif kind == "feathers":
        for k, col in enumerate(((240, 235, 220), (200, 60, 40), (240, 235, 220))):
            f.paint(f.curve([(x - 3 - k * 2, y - 10), (x - 8 - k * 3, y - 19), (x - 15 - k * 3, y - 21)], 1.7, 0.6), col, mat="cloth", outline=0.5)


def warpaint(f, x=18, y=-67):
    if CTX.race:
        return
    f.paint(f.poly([(x + 3, y - 3), (x + 13, y - 1), (x + 12, y + 1), (x + 3, y)]), WARPAINT, mat="flat", outline=0)


# ================================================================== human figures
def h_soldier(c, fx, fy, u=1.0, armor="plate", tabard=True, hat="kettle", beard=None, weapon="spear",
              shield=None, pauldron=True, back=None, capecol=False, glow=None, plain_hair=None):
    """A human foot soldier. weapon: spear, pike, halberd, sword, mace, hammer, banner, bow,
    crossbow, musket, rifle, sniper, grenade, mortar, axe, torch, stick, none."""
    f = Fig(c, fx, fy, u)
    shadow(f, 21)
    gun = weapon in ("musket", "rifle", "sniper", "crossbow")
    # back items
    if back == "quiver":
        from wc_style_units import quiver
        quiver(f, -12, -46)
    elif back == "pack":
        back_pack(f, -14, -50)
    elif back == "bandolier":
        back_pack(f, -14, -50, col=LEATHER)
    if capecol:
        cape(f, (-12, -66), (6, -66), -24)
    if weapon == "banner":
        banner(f, (-16, -2), (-14, -104), 15, 18)
    human_legs(f, armor if armor in ("plate", "leather") else "cloth", near=False)
    # far arm
    if gun:
        human_arm(f, (-6, -60), (8, -54), (20, -58), STEEL if armor == "plate" else LEATHER,
                  "metal" if armor == "plate" else "leather", None if armor == "plate" else HSKIN, dark=0.8)
    elif weapon in ("sword", "mace", "hammer", "axe"):
        pass
    elif weapon == "grenade":
        human_arm(f, (-8, -60), (-18, -66), (-16, -80), LEATHER, "leather", HSKIN, dark=0.8)
        grenade(f, -16, -86)
    elif shield in ("round",):
        from wc_style_units import round_shield
        round_shield(f, -15, -50, 13, rim=STEEL if armor == "plate" else IRON, wood=armor != "plate", dark=0.8)
    if armor == "coat":
        body_col = L_MAIN
        torso = f.poly([(-14, -28), (12, -28), (16, -46), (18, -62), (6, -68), (-12, -67), (-17, -48)])
        f.paint(torso, body_col, layer="l2", mat="cloth")
        f.paint(f.c.intersect(torso, f.poly([(-2, -68), (4, -68), (6, -28), (0, -28)])), L_MAIN, layer="l1", mat="gold", outline=0.4)
        f.paint(f.c.intersect(torso, f.poly([(-30, -36), (30, -36), (30, -31), (-30, -31)])), DLEATHER, mat="leather", outline=0.5)
        f.paint(f.poly([(-13, -30), (13, -30), (15, -16), (-14, -16)]), L_MAIN, layer="l2", mat="cloth", dark=0.9)   # coat skirt
    else:
        human_torso(f, armor if armor in ("plate", "leather") else "cloth", tabard=tabard)
    if back == "bandolier":
        f.paint(f.poly([(-12, -66), (-6, -68), (14, -32), (8, -30)]), DLEATHER, mat="leather", outline=0.5)
    human_legs(f, armor if armor in ("plate", "leather") else "cloth", far=False)
    if pauldron and armor == "plate":
        round_pauldron(f, 1, -62, 0.9)
    # head
    SPECIAL = ("sallet", "plumed", "tricorn", "officer", "goggles", "feather_cap", "crown", "mitre")
    if hat == "great_helm":
        great_helm(f, 4, -76)
    elif hat == "hood":
        human_head(f, 5, -75, hood=True, beard=beard)
    else:
        base_hat = hat if hat in ("kettle", "hair", "cap") else ("hair" if plain_hair else None)
        human_head(f, 5, -75, hat=base_hat, beard=beard, hair=plain_hair or HAIR)
        if hat in SPECIAL:
            human_hat(f, hat)
    # weapon and near arm
    col, mat, glove = (STEEL, "metal", None) if armor == "plate" else ((LEATHER, "leather", HSKIN) if armor == "leather" else
                                                                       ((L_MAIN, "cloth", HSKIN) if armor == "coat" else (CLOTH_TAN, "cloth", HSKIN)))
    layer_arm = "l2" if armor == "coat" else "base"
    if weapon in ("spear", "pike"):
        spear(f, (24, -2), (24, -112 if weapon == "pike" else -104), 1.6)
        arm(f, (4, -58), (12, -46), (24, -50), col, mat, glove, layer_arm)
    elif weapon == "halberd":
        halberd(f, (24, -2), (24, -108))
        arm(f, (4, -58), (12, -46), (24, -50), col, mat, glove, layer_arm)
    elif weapon == "sword":
        sword(f, (22, -46), (34, -84), 2.6, 6)
        arm(f, (4, -58), (12, -46), (22, -46), col, mat, glove, layer_arm)
    elif weapon in ("mace", "hammer"):
        warhammer(f, (20, -36), (28, -76), STEEL, glow, 0.8 if weapon == "mace" else 1.0)
        arm(f, (4, -58), (11, -46), (21, -44), col, mat, glove, layer_arm)
    elif weapon == "axe":
        from wc_style_units import big_axe
        big_axe(f, (20, -30), (24, -86), 0.8)
        arm(f, (4, -58), (11, -46), (21, -44), col, mat, glove, layer_arm)
    elif weapon == "bow":
        from wc_style_units import bow
        bow(f, (30, -60), (22, -92), (22, -28), string_to=(14, -60))
        arm(f, (4, -62), (18, -61), (30, -60), col, mat, glove, layer_arm)
    elif weapon == "crossbow":
        arm(f, (4, -60), (12, -52), (18, -58), col, mat, glove, layer_arm)
        crossbow(f, (4, -58), (36, -62))
        f.paint(f.ell(18, -58, 4.6, 4.6), glove or STEEL, mat="skin" if glove else "metal")
    elif weapon in ("musket", "rifle", "sniper"):
        arm(f, (4, -60), (12, -52), (20, -58), col, mat, glove, layer_arm)
        long_gun(f, (0, -58), (42, -64), rifle=weapon != "musket", bayonet=weapon == "rifle", scope=weapon == "sniper")
        f.paint(f.ell(20, -59, 4.6, 4.6), glove or STEEL, mat="skin" if glove else "metal")
    elif weapon == "grenade":
        long_gun(f, (4, -30), (26, -64), rifle=True)
        arm(f, (4, -58), (12, -46), (20, -48), col, mat, glove, layer_arm)
    elif weapon == "mortar":
        tube(f, (-14, -58), (30, -82), 5.5)
        arm(f, (4, -58), (14, -60), (16, -70), col, mat, glove, layer_arm)
    elif weapon == "banner":
        arm(f, (4, -58), (12, -48), (18, -52), col, mat, glove, layer_arm)
        from wc_style_units import sword as _sw
        _sw(f, (18, -50), (30, -84), 2.4, 5)
    elif weapon == "claws":        # bare claws raised to strike
        arm(f, (4, -58), (14, -60), (24, -70), col, mat, glove, layer_arm)
        for k in range(3):
            f.paint(f.curve([(24 + k * 2.5, -74), (29 + k * 2.5, -78), (32 + k * 2.5, -74)], 1.1, 0.4), BONE, mat="bone", outline=0.5)
    elif weapon == "glaive":       # a moonglaive: three curved blades round a grip
        moonglaive(f, 26, -60)
        arm(f, (4, -58), (14, -54), (24, -58), col, mat, glove, layer_arm)
    elif weapon == "stick":
        walking_stick(f, (28, -2), (24, -84))
        arm(f, (4, -58), (12, -48), (25, -60), col, mat, glove, layer_arm)
        f.paint(f.ell(25, -60, 4.4, 4.4), glove or STEEL, mat="skin" if glove else "metal")
    elif weapon == "torch":
        pole(f, (18, -36), (26, -70), 1.6)
        lantern(f, 26, -74, (255, 170, 70))
        arm(f, (4, -58), (11, -46), (20, -44), col, mat, glove, layer_arm)
    if shield == "kite":
        kite_shield(f, 15, -44, 0.95)
    if glow:
        pass


def arm(f, sh, el, hand, col, mat, glove, layer="base"):
    if layer == "l2":
        sleeve_arm(f, sh, el, hand, r=6, cuff=(L_MAIN, "l1", "gold"))
    else:
        human_arm(f, sh, el, hand, col, mat, glove)


def h_robed(c, fx, fy, u=1.0, robe_col=L_MAIN, robe_layer="l2", hat="hair", hair=HAIR, beard=None,
            prop=None, glow=None, mantle=True, hood=False, hem=("l1", L_MAIN, "gold")):
    """A robed human civilian: prophets, scholars, inquisitors, clerics, merchants."""
    f = Fig(c, fx, fy, u)
    shadow(f, 19)
    if prop == "staff":
        pole(f, (-14, -2), (-12, -100), 1.9)
        orb = f.ell(-12, -104, 4, 4)
        f.c.glow(orb, glow or (255, 230, 140), radius=4, strength=0.8)
        f.paint(orb, mix(glow or (255, 230, 140), (255, 255, 255), 0.4), mat="glow", outline=0.5)
    sleeve_arm(f, (-6, -60), (-12, -48), (-8, -40), robe_col, robe_layer, dark=0.8)
    robe(f, col=robe_col, layer=robe_layer, hem_layer=hem[0], hem_col=hem[1], hem_mat=hem[2])
    if mantle:
        f.paint(f.poly([(-14, -68), (14, -68), (16, -61), (-15, -60)]), L_MAIN, layer="l1", mat="gold", outline=0.5)
    if hood:
        human_head(f, 5, -76, hood=True, beard=beard)
    else:
        human_head(f, 5, -76, hat=hat if hat in ("hair", "kettle", "cap") else "hair", hair=hair, beard=beard)
        if hat in ("tricorn", "officer", "feather_cap", "mitre", "goggles", "crown"):
            human_hat(f, hat, 5, -76)
    hand = (22, -54)
    if prop == "book":
        book(f, 14, -50)
        hand = (18, -52)
    elif prop == "censer":
        hand = (24, -46)
    elif prop == "coins":
        coin_bag(f, 22, -44)
        hand = (21, -50)
    elif prop == "light":
        hand = (22, -68)
    elif prop == "lute":
        lute(f, 12, -48)
        hand = (18, -54)
    elif prop == "spyglass":
        hand = (20, -70)
    sleeve_arm(f, (5, -61), (14, -54), hand, robe_col, robe_layer)
    if prop == "censer":
        f.paint(f.cap((24, -46), (26, -34), 0.5), (70, 60, 50), mat="flat", outline=0)
        lantern(f, 26, -30, glow or (255, 200, 110))
    elif prop == "light":
        m = f.ell(23, -74, 4, 4)
        f.c.glow(m, glow or (255, 225, 120), radius=5, strength=0.85)
        f.paint(m, (255, 245, 190), mat="glow", outline=0)
    elif prop == "spyglass":
        spyglass(f, (18, -72), (30, -78))


def h_rider(c, fx, fy, u=1.0, kind="outrider"):
    """Human riders: outrider (spear, light horse), horse archer, lancer, Knight of the Silver Hand."""
    f = Fig(c, fx - 4, fy, u * 1.06)
    shadow(f, 34)
    from wc_style_units import horse
    coats = {"outrider": (150, 100, 60), "archer": (120, 85, 55), "lancer": (90, 70, 60), "silver": (235, 232, 225),
             "knight": (126, 84, 50), "warrider": (58, 46, 40), "champion": (196, 150, 84)}
    if CTX.spec.get("mount"):
        sx_, sy_ = CTX.spec["mount"](c, f, armored=kind in ("lancer", "silver", "knight", "warrider", "champion"))
        ry = CTX.spec.get("body", (1, 1))[1]
        r = Fig(c, sx_ - 2 * u, sy_ + 27 * u * 0.88 * ry, u * 0.88)
    else:
        horse(f, coat=coats.get(kind, (120, 85, 55)),
              barding="half" if kind in ("lancer", "silver", "knight", "warrider", "champion") else False)
        r = Fig(c, *f.p(-4, -22), u * 0.88)
    armor = "plate" if kind in ("lancer", "silver", "knight", "warrider", "champion") else "leather"
    col, mat, glove = (STEEL, "metal", None) if armor == "plate" else (LEATHER, "leather", HSKIN)
    if kind == "silver":     # holy hammer raised behind
        human_arm(r, (-8, -60), (-18, -66), (-14, -80), STEEL, "metal", None, dark=0.8)
        warhammer(r, (-14, -62), (2, -96), (245, 240, 225), (255, 230, 140), 1.0)
    human_torso(r, armor, tabard=armor == "plate")
    r.paint(r.cap((2, -30), (14, -26), 7.5, 7), col, mat=mat)
    r.paint(r.cap((14, -26), (13, -12), 6.5, 6), col if armor == "plate" else DLEATHER, mat=mat if armor == "plate" else "leather")
    boot(r, 13, -6, STEEL if armor == "plate" else DLEATHER, 0.95, mat="metal" if armor == "plate" else "leather")
    if armor == "plate":
        round_pauldron(r, 1, -62, 1.0)
    if kind == "silver":
        great_helm(r, 4, -76, plume=True)
        kite_shield(r, 16, -44, 0.95)
    elif kind == "lancer":
        human_head(r, 5, -75)
        human_hat(r, "plumed")
        pole(r, (-24, -30), (44, -86), 2.0)
        r.paint(r.poly([(44, -86), (36, -79), (39, -76)]), STEEL, mat="metal", outline=0.6)
        r.paint(r.poly([(30, -73), (22, -70), (24, -62), (32, -66)]), L_MAIN, layer="l2", mat="cloth", outline=0.5)   # pennon
        human_arm(r, (4, -58), (10, -46), (18, -50), col, mat, glove)
    elif kind == "outrider":
        human_head(r, 5, -75, hat="kettle")
        spear(r, (12, -20), (40, -100), 1.5)
        human_arm(r, (4, -58), (14, -48), (22, -54), col, mat, glove)
    elif kind == "archer":
        human_head(r, 5, -75, hood=True)
        from wc_style_units import bow
        bow(r, (30, -60), (22, -92), (22, -28), string_to=(14, -60))
        human_arm(r, (4, -62), (18, -61), (30, -60), col, mat, glove)
    elif kind == "glaive":         # night elf huntress: a moonglaive held high
        human_head(r, 5, -75)
        moonglaive(r, 28, -78, 12)
        human_arm(r, (4, -60), (16, -66), (26, -76), col, mat, glove)
    elif kind == "knight":         # sword raised, kite shield
        human_head(r, 5, -75)
        human_hat(r, "sallet")
        sword(r, (22, -50), (36, -88), 2.6, 6)
        human_arm(r, (4, -58), (12, -48), (22, -50), col, mat, glove)
        kite_shield(r, 16, -44, 0.9)
    elif kind == "warrider":       # lance with pennon, great helm, kite shield
        great_helm(r, 4, -76, plume=False)
        pole(r, (-24, -30), (46, -90), 2.2)
        r.paint(r.poly([(46, -90), (38, -83), (41, -80)]), STEEL, mat="metal", outline=0.6)
        r.paint(r.poly([(32, -76), (22, -72), (24, -63), (34, -68)]), L_MAIN, layer="l2", mat="cloth", outline=0.5)
        human_arm(r, (4, -58), (10, -46), (18, -50), col, mat, glove)
        kite_shield(r, 16, -44, 0.95)
    elif kind == "champion":       # plumed great helm, sword raised, banner on the back
        great_helm(r, 4, -76, plume=True)
        sword(r, (22, -52), (38, -94), 2.8, 7)
        human_arm(r, (4, -58), (12, -48), (22, -52), col, mat, glove)
        kite_shield(r, 16, -44, 1.0)
    elif kind == "cavalry":        # sabre and pistol era
        human_head(r, 5, -75)
        human_hat(r, "plumed")
        sword(r, (20, -56), (40, -86), 2.0, 5)
        human_arm(r, (4, -58), (12, -50), (20, -56), col, mat, glove)


# ================================================================== orc figures
def o_soldier(c, fx, fy, u=0.95, armor="hide", hat="topknot", weapon="axe", shield=None, pauldrons=1,
              back=None, glow=None, paint_face=False, eye=(255, 70, 40)):
    """An orc foot soldier. armor: bare, hide, iron, coat. weapon as h_soldier, plus cleaver."""
    from wc_style_units import (orc_legs, orc_torso, loincloth, spiked_pauldron, orc_head, orc_arm, fist,
                                big_axe, hide_shield, quiver, bow)
    f = Fig(c, fx, fy, u)
    shadow(f, 24)
    gun = weapon in ("musket", "rifle", "sniper", "crossbow")
    if back == "quiver":
        quiver(f, -16, -48)
    elif back == "pack":
        back_pack(f, -20, -52, col=CLOTH_TAN)
    elif back == "banner":
        banner(f, (-20, -2), (-18, -108), 15, 18)
    orc_legs(f, near=False)
    if gun:
        orc_arm(f, (-14, -62), (0, -52), (12, -50), dark=0.75)
    elif weapon == "grenade":
        orc_arm(f, (-16, -62), (-26, -70), (-22, -84), dark=0.75)
        grenade(f, -22, -90, 4.6)
    elif shield == "hide":
        hide_shield(f, -18, -50, 14, dark=0.8)
    else:
        orc_arm(f, (-16, -62), (-24, -48), (-20, -36), dark=0.75)
        fist(f, -20, -34, dark=0.75)
    orc_torso(f, loin=False)
    if armor == "hide":
        f.paint(f.poly([(-20, -66), (-6, -74), (6, -60), (2, -40), (-20, -42)]), (140, 105, 70), mat="fur", outline=0.6)
    elif armor == "iron":
        m = f.poly([(-20, -68), (16, -70), (22, -50), (18, -38), (-20, -38)])
        f.paint(m, OIRON, mat="metal")
        for x in (-12, -2, 8):
            f.paint(f.ell(x, -60, 1.2, 1.2), BONE, mat="metal", outline=0.3)
    elif armor == "coat":
        m = f.poly([(-20, -68), (16, -70), (22, -50), (20, -24), (-22, -24)])
        f.paint(m, L_MAIN, layer="l2", mat="cloth")
        f.paint(f.c.intersect(m, f.poly([(-30, -40), (30, -40), (30, -35), (-30, -35)])), DLEATHER, mat="leather", outline=0.5)
    orc_legs(f, far=False)
    if armor != "coat":
        loincloth(f)
    if pauldrons:
        spiked_pauldron(f, -1, -67, 0.85 if pauldrons == 1 else 1.0, spikes=2 if pauldrons == 1 else 3,
                        color=OIRON if armor == "iron" else IRON, trim=pauldrons > 1)
    # weapon arm, then the head in front of it
    if weapon in ("spear", "pike"):
        spear(f, (28, -2), (28, -112 if weapon == "pike" else -106), 1.7, feathers=True)
        orc_arm(f, (4, -55), (14, -46), (27, -48))
        hand = (28, -48)
    elif weapon == "halberd":
        halberd(f, (28, -2), (28, -110), OIRON)
        orc_arm(f, (4, -55), (14, -46), (27, -48))
        hand = (28, -48)
    elif weapon in ("axe", "cleaver"):
        big_axe(f, (22, -26), (28, -88), 0.9)
        orc_arm(f, (4, -55), (12, -44), (23, -38))
        hand = (24, -36)
    elif weapon in ("mace", "hammer"):
        warhammer(f, (22, -30), (30, -78), OIRON, glow, 1.0)
        orc_arm(f, (4, -55), (12, -44), (23, -38))
        hand = (24, -36)
    elif weapon == "bow":
        bow(f, (34, -62), (26, -98), (26, -26), string_to=(12, -64))
        orc_arm(f, (6, -62), (20, -63), (32, -62))
        hand = (33, -62)
    elif weapon == "stick":
        walking_stick(f, (32, -2), (28, -90), (110, 74, 42))
        orc_arm(f, (4, -55), (16, -50), (29, -62))
        hand = (29, -62)
    elif weapon == "crossbow":
        orc_arm(f, (4, -55), (14, -46), (24, -50))
        crossbow(f, (6, -48), (42, -52))
        hand = (24, -50)
    elif weapon in ("musket", "rifle", "sniper"):
        orc_arm(f, (4, -55), (14, -46), (25, -50))
        long_gun(f, (2, -46), (48, -54), rifle=weapon != "musket", bayonet=weapon == "rifle", scope=weapon == "sniper", color=(130, 85, 50))
        hand = (25, -50)
    elif weapon == "grenade":
        big_axe(f, (22, -26), (26, -78), 0.7)
        orc_arm(f, (4, -55), (12, -44), (23, -38))
        hand = (24, -36)
    elif weapon == "mortar":
        tube(f, (-18, -60), (32, -86), 6, OIRON)
        orc_arm(f, (4, -58), (16, -62), (18, -74))
        hand = (19, -74)
    elif weapon == "banner":
        big_axe(f, (22, -26), (28, -82), 0.8)
        orc_arm(f, (4, -55), (12, -44), (23, -38))
        hand = (24, -36)
    else:
        orc_arm(f, (4, -55), (12, -44), (22, -40))
        hand = (23, -38)
    orc_head(f, 18, -67, hair=hat if hat in ("topknot", "mohawk") else None, helm=False, eye=eye)
    if paint_face:
        warpaint(f)
    if hat not in ("topknot", "mohawk", None):
        orc_hat(f, hat)
    fist(f, *hand, r=6)


def o_robed(c, fx, fy, u=0.92, prop=None, glow=None, hat=None, pelt=True, robe_col=L_MAIN, robe_layer="l2"):
    from wc_style_units import orc_head, fist
    f = Fig(c, fx, fy, u)
    shadow(f, 21)
    if prop == "staff":
        pole(f, (-16, -2), (-14, -100), 2.0)
        m = f.ell(-14, -104, 4.5, 4.5)
        f.c.glow(m, glow or (120, 220, 255), radius=4, strength=0.8)
        f.paint(m, mix(glow or (120, 220, 255), (255, 255, 255), 0.35), mat="glow", outline=0.5)
    sleeve_arm(f, (-14, -62), (-22, -50), (-18, -40), robe_col, robe_layer, skin=OSKIN, dark=0.75, r=7.5, cuff=(L_DARK, "l1", "cloth"))
    robe(f, col=robe_col, layer=robe_layer, hem_layer="l1", hem_col=L_DARK, hem_mat="cloth", bulk=1.25, top=-68, waist_y=-38, sash=False)
    f.paint(f.poly([(-14, -41), (16, -41), (17, -35), (-14, -35)]), LEATHER, mat="leather", outline=0.6)
    if pelt:
        f.paint(f.ell(-4, -64, 17, 8), (122, 92, 62), mat="fur")
    hand = (27, -48)
    if prop == "book":
        book(f, 18, -48, (90, 60, 40))
        hand = (22, -50)
    elif prop == "coins":
        coin_bag(f, 26, -44)
        hand = (25, -50)
    elif prop == "drum":
        drum(f, 18, -42)
        hand = (24, -58)
    elif prop == "light":
        hand = (26, -66)
    elif prop == "spyglass":
        hand = (22, -70)
    elif prop == "wrench":
        wrench(f, (24, -40), (32, -66))
        hand = (25, -46)
    elif prop == "censer":
        hand = (27, -46)
    sleeve_arm(f, (4, -57), (14, -46), hand, robe_col, robe_layer, skin=OSKIN, r=7.5, cuff=(L_DARK, "l1", "cloth"))
    orc_head(f, 17, -68, hair="topknot" if hat is None else None, eye=(255, 200, 60) if not glow else glow)
    if hat:
        orc_hat(f, hat, 17, -68)
    fist(f, *hand, r=6)
    if prop == "light":
        m = f.ell(28, -74, 4.2, 4.2)
        f.c.glow(m, glow or (140, 220, 255), radius=5, strength=0.85)
        f.paint(m, (230, 250, 255), mat="glow", outline=0)
    elif prop == "spyglass":
        spyglass(f, (20, -72), (34, -80))
    elif prop == "censer":
        f.paint(f.cap((27, -46), (29, -34), 0.5), (70, 60, 50), mat="flat", outline=0)
        lantern(f, 29, -30, glow or (140, 240, 120))


def o_rider(c, fx, fy, u=1.0, kind="archer"):
    from wc_style_units import wolf, orc_torso, orc_head, orc_arm, fist, spiked_pauldron, bow, big_axe
    f = Fig(c, fx, fy, u * 1.08)
    shadow(f, 36)
    if CTX.spec.get("mount"):
        sx_, sy_ = CTX.spec["mount"](c, f, armored=kind in ("knight", "lancer", "cavalry", "warrider", "champion"))
        ry = CTX.spec.get("body", (1, 1))[1]
        r = Fig(c, sx_ - 2 * u, sy_ + 29 * u * 0.84 * ry, u * 0.84)
    else:
        wolf(f, fur=(70, 66, 64) if kind in ("knight", "raider", "warrider", "champion") else (92, 84, 78))
        if kind in ("knight", "raider", "lancer", "warrider", "champion"):     # iron barding on the wolf's chest
            f.paint(f.poly([(14, -56), (34, -52), (36, -40), (16, -36)]), OIRON, mat="metal", outline=0.6)
        r = Fig(c, *f.p(-2, -16), u * 0.84)
    if kind == "raider":
        orc_arm(r, (-16, -62), (-26, -56), (-24, -72), dark=0.75)
        fist(r, -24, -74, dark=0.75)
    orc_torso(r, loin=False)
    if kind in ("knight", "lancer", "raider", "warrider", "champion"):
        r.paint(r.poly([(-20, -68), (16, -70), (22, -50), (18, -38), (-20, -38)]), OIRON, mat="metal")
    r.paint(r.cap((2, -30), (16, -24), 9, 8), DLEATHER, mat="leather")
    r.paint(r.cap((16, -24), (15, -10), 7, 6.5), OSKIN, mat="skin")
    boot(r, 15, -4, DLEATHER, 1.0)
    spiked_pauldron(r, 0, -66, 0.95, spikes=3, trim=kind != "archer", color=OIRON if kind != "archer" else IRON)
    if kind == "outrider":         # light rider with a spear
        spear(r, (12, -20), (42, -104), 1.6, feathers=True)
        orc_arm(r, (6, -58), (16, -48), (24, -56))
        orc_head(r, 19, -66)
        fist(r, 25, -56)
    elif kind == "cavalry":        # heavy rider, axe raised
        big_axe(r, (24, -40), (36, -96), 0.9)
        orc_arm(r, (6, -58), (14, -50), (25, -44))
        orc_head(r, 19, -66, hair=None)
        orc_hat(r, "skullcap", 19, -66)
        fist(r, 26, -42)
    elif kind == "archer":
        bow(r, (34, -62), (26, -98), (26, -26), string_to=(12, -64))
        orc_arm(r, (6, -60), (20, -63), (32, -62))
        orc_head(r, 19, -66)
        fist(r, 33, -62, r=5.5)
    elif kind == "warrider":       # war spear with a banner, iron helm
        pole(r, (4, -20), (44, -106), 2.0)
        r.paint(r.poly([(44, -106), (37, -96), (41, -94)]), OIRON, mat="metal", outline=0.6)
        r.paint(r.poly([(36, -92), (24, -88), (26, -76), (38, -80)]), (150, 40, 30), layer="l2", mat="cloth", outline=0.5)
        orc_arm(r, (6, -58), (16, -48), (24, -56))
        orc_head(r, 19, -66, hair=None)
        orc_hat(r, "warhelm", 19, -66)
        fist(r, 25, -56)
    elif kind == "champion":       # great double axe raised high, war helm
        big_axe(r, (20, -30), (32, -104), 1.15, double=True)
        orc_arm(r, (6, -58), (12, -50), (22, -44))
        orc_head(r, 19, -66, hair=None)
        orc_hat(r, "warhelm", 19, -66)
        fist(r, 24, -44)
    elif kind == "knight":
        big_axe(r, (22, -26), (30, -92), 1.0, double=True)
        orc_arm(r, (6, -58), (12, -44), (22, -36))
        orc_head(r, 19, -66, hair=None)
        orc_hat(r, "warhelm", 19, -66)
        fist(r, 24, -34)
    elif kind == "lancer":
        pole(r, (-24, -34), (48, -84), 2.1)
        r.paint(r.poly([(48, -84), (38, -78), (41, -74)]), STEEL, mat="metal", outline=0.6)
        r.paint(r.poly([(32, -72), (24, -70), (26, -62), (34, -65)]), L_MAIN, layer="l2", mat="cloth", outline=0.5)
        orc_arm(r, (6, -58), (12, -46), (20, -50))
        orc_head(r, 19, -66, hair=None)
        orc_hat(r, "skullcap", 19, -66)
        fist(r, 21, -50)
    elif kind == "raider":    # whirling a chain and hook overhead
        chain = r.curve([(-24, -74), (-10, -96), (14, -100), (30, -88)], 0.9)
        r.paint(chain, (150, 145, 140), mat="metal", outline=0.5)
        r.paint(r.poly([(30, -88), (37, -84), (34, -80), (30, -84), (27, -80), (26, -86)]), STEEL, mat="metal", outline=0.5)
        big_axe(r, (22, -26), (28, -80), 0.8)
        orc_arm(r, (6, -58), (12, -44), (22, -36))
        orc_head(r, 19, -66)
        warpaint(r, 19, -66)
        fist(r, 24, -34)


# ================================================================== siege engines (small 64x56 canvases, at 2x)
def wheel(f, x, y, r, col=WOOD):
    f.paint(f.ell(x, y, r, r), col, mat="wood")
    f.paint(f.ell(x, y, r * 0.35, r * 0.35), IRON, mat="metal", outline=0.4)
    for a in range(0, 180, 45):
        t = math.radians(a)
        f.paint(f.cap((x - math.cos(t) * r * 0.8, y - math.sin(t) * r * 0.8), (x + math.cos(t) * r * 0.8, y + math.sin(t) * r * 0.8), 0.6),
                mix(col, (0, 0, 0), 0.3), mat="flat", outline=0)


def crewman(f, x, race, s=0.38):
    """A tiny crew figure standing beside an engine."""
    c = f.c
    if race == "Orcs" or CTX.spec.get("family") == "brute":
        sub = Fig(c, *f.p(x, 0), f.u * s)
        from wc_style_units import orc_legs, orc_torso, orc_head, orc_arm, fist, loincloth
        orc_legs(sub, near=False); orc_torso(sub, loin=False); orc_legs(sub, far=False); loincloth(sub)
        orc_arm(sub, (4, -55), (12, -44), (22, -46)); orc_head(sub, 18, -67); fist(sub, 23, -46)
    else:
        sub = Fig(c, *f.p(x, 0), f.u * s)
        human_legs(sub, "leather", near=False); human_torso(sub, "leather", tabard=True); human_legs(sub, "leather", far=False)
        human_head(sub, 5, -75, hat="kettle"); human_arm(sub, (4, -58), (12, -48), (20, -50), LEATHER, "leather", HSKIN)


def catapult(c, fx, fy, u=1.0, race="Humans"):
    f = Fig(c, fx, fy, u)
    shadow(f, 30)
    wood = WOOD if race == "Humans" else (120, 80, 45)
    f.paint(f.poly([(-26, -14), (24, -14), (24, -8), (-26, -8)]), wood, mat="wood")                 # chassis
    f.paint(f.poly([(-6, -14), (0, -40), (6, -40), (2, -14)]), wood, mat="wood")                    # upright
    f.paint(f.cap((-28, -18), (10, -36), 2.2), wood, mat="wood")                                     # throwing arm
    f.paint(f.ell(-28, -20, 6, 4), (90, 60, 40), mat="leather")                                      # bucket
    f.paint(f.ell(-28, -24, 4, 3.5), (130, 125, 120) if race == "Humans" else BONE, mat="metal" if race == "Humans" else "bone")
    if race == "Orcs":
        for x in (-20, 14):
            f.paint(f.poly([(x, -14), (x + 2, -26), (x + 4, -14)]), BONE, mat="bone", outline=0.5)
        f.paint(f.poly([(4, -40), (12, -38), (12, -32), (4, -34)]), L_MAIN, layer="l2", mat="cloth")
    else:
        f.paint(f.poly([(4, -40), (12, -38), (12, -32), (4, -34)]), L_MAIN, layer="l2", mat="cloth")
        f.paint(f.poly([(4, -40), (12, -38), (12, -37), (4, -39)]), L_MAIN, layer="l1", mat="gold", outline=0.3)
    wheel(f, -16, -6, 7, wood); wheel(f, 16, -6, 7, wood)
    crewman(f, -36, race)


def ballista(c, fx, fy, u=1.0, race="Humans"):
    f = Fig(c, fx, fy, u)
    shadow(f, 30)
    wood = WOOD if race == "Humans" else (120, 80, 45)
    f.paint(f.poly([(-24, -14), (22, -14), (22, -8), (-24, -8)]), wood, mat="wood")
    f.paint(f.poly([(-4, -14), (2, -30), (8, -30), (4, -14)]), wood, mat="wood")
    f.paint(f.cap((-20, -26), (26, -36), 2.2), wood, mat="wood")                                    # stock
    f.paint(f.curve([(14, -50), (20, -34), (14, -20)], 2.0), DSTEEL if race == "Humans" else OIRON, mat="metal")  # bow arms
    f.paint(f.cap((-18, -26), (34, -38), 1.0), STEEL, mat="metal")                                  # bolt
    f.paint(f.poly([(34, -38), (28, -40), (29, -35)]), STEEL, mat="metal", outline=0.4)
    f.paint(f.poly([(-6, -32), (4, -34), (4, -28), (-6, -26)]), L_MAIN, layer="l2", mat="cloth")
    if race == "Orcs":
        f.paint(f.poly([(18, -14), (20, -26), (22, -14)]), BONE, mat="bone", outline=0.5)
    wheel(f, -14, -6, 7, wood); wheel(f, 14, -6, 7, wood)
    crewman(f, -34, race)


def steam_tank(c, fx, fy, u=1.0):
    f = Fig(c, fx, fy, u)
    shadow(f, 34)
    for x in (-20, -6, 8, 22):
        wheel(f, x, -7, 7, DSTEEL)
    hull = f.poly([(-30, -10), (30, -10), (34, -22), (24, -36), (-20, -38), (-30, -26)])
    f.paint(hull, STEEL, mat="metal")
    f.paint(f.c.intersect(hull, f.poly([(-40, -26), (40, -26), (40, -20), (-40, -20)])), L_MAIN, layer="l2", mat="cloth", outline=0.5)
    f.paint(f.c.intersect(hull, f.poly([(-40, -20), (40, -20), (40, -18), (-40, -18)])), L_MAIN, layer="l1", mat="gold", outline=0)
    f.paint(f.ell(4, -40, 12, 7), DSTEEL, mat="metal")                                              # turret
    tube(f, (10, -42), (38, -46), 3.5)
    f.paint(f.cap((-16, -38), (-16, -56), 3.2, 2.6), (80, 78, 82), mat="metal")                     # smokestack
    for k, (dx, dy, r) in enumerate(((-17, -62, 4), (-21, -68, 5), (-27, -72, 6))):
        f.paint(f.ell(dx, dy, r, r * 0.85), (190, 190, 195), mat="cloth", outline=0.4, dark=1 - k * 0.05)
    for x in (-18, -6, 6, 18):
        f.paint(f.ell(x, -30, 1.2, 1.2), BRASS, mat="gold", outline=0.3)


def mortar_team(c, fx, fy, u=1.0, race="Humans"):
    f = Fig(c, fx, fy, u)
    shadow(f, 28)
    f.paint(f.poly([(-4, -10), (22, -10), (20, -4), (-2, -4)]), (100, 95, 92), mat="metal")      # base plate
    tube(f, (6, -10), (24, -40), 6, DSTEEL if race == "Humans" else OIRON)
    f.paint(f.cap((10, -12), (2, -26), 1.4), (90, 85, 82), mat="metal")
    for x in (26, 30):
        f.paint(f.ell(x, -6, 3.2, 3.2), (60, 58, 62), mat="metal", outline=0.4)
    crewman(f, -14, race, 0.42)


# ================================================================== heroes and clerics
def uther(c, fx, fy, u=1.0):
    h_soldier(c, fx, fy, u * 1.05, armor="plate", hat="crown", beard=(200, 200, 205), weapon="hammer",
              glow=(255, 230, 140), capecol=True, plain_hair=(200, 200, 205))


def grom(c, fx, fy, u=1.0):
    from wc_style_units import (orc_legs, orc_torso, loincloth, orc_head, orc_arm, fist, spiked_pauldron)
    f = Fig(c, fx, fy, u)
    shadow(f, 26)
    # a huge two-handed blade raised high, wreathed in fire
    blade = f.poly([(-20, -50), (-14, -54), (24, -116), (20, -120), (16, -118)])
    f.c.glow(blade, (255, 120, 60), radius=4, strength=0.6)
    f.paint(blade, STEEL, mat="metal", bevel=1.4)
    f.paint(f.cap((-26, -40), (-18, -52), 2.2), DLEATHER, mat="leather")
    f.paint(f.cap((-24, -56), (-12, -48), 2.0), OIRON, mat="metal", outline=0.5)
    orc_legs(f, near=False)
    orc_arm(f, (-16, -62), (-26, -56), (-22, -48), dark=0.75)
    orc_torso(f, loin=False, skin=(110, 150, 70))
    for y in (-60, -52):     # tattooed chest
        f.paint(f.curve([(-14, y), (0, y - 3), (14, y)], 1.0), (40, 40, 45), mat="flat", outline=0)
    orc_legs(f, far=False)
    loincloth(f)
    spiked_pauldron(f, -2, -68, 0.8, spikes=3)
    orc_arm(f, (4, -55), (10, -46), (-14, -48))
    orc_head(f, 18, -67, hair="topknot", eye=(255, 90, 50))
    f.paint(f.poly([(22, -61), (34, -60), (33, -56), (22, -57)]), (25, 25, 30), mat="flat", outline=0)   # black-painted jaw
    fist(f, -16, -50)


# ================================================================== recipes
H, O = "Humans", "Orcs"


class R:
    """A recipe: a figure function plus its settings (kept so other races can adapt them)."""
    def __init__(self, fn, kw, scale=1.0):
        self.fn, self.kw, self.scale = fn, kw, scale

    def __call__(self, c, fx, fy, u):
        return self.fn(c, fx, fy, u * self.scale, **self.kw)

    def but(self, **changes):
        return R(self.fn, {**self.kw, **changes}, self.scale)


def hs(**kw):
    return R(h_soldier, kw)


def os_(**kw):
    return R(o_soldier, kw, 0.95)


def hr(**kw):
    return R(h_robed, kw)


def or_(**kw):
    return R(o_robed, kw, 0.92)


# name -> (draw(c, fx, fy, u), archetype); archetype picks the size reference
RECIPES = {
    # ---- Humans: soldiers
    # Scouts are not ranged units (no ranged attack in the ruleset), so they carry a walking
    # stick and a travel pack, not a bow. Keep this for every race unless its scout is ranged.
    "Scout-Humans": (hs(armor="leather", tabard=False, hat="hood", weapon="stick", pauldron=False, back="pack"), "foot"),
    # Oct 2026 unit lines (wc_lines): Archer -> Hunter -> Ranger line (bows) or Rifleman line (guns);
    # the melee line carries no guns: Vanguard -> Man-at-Arms -> Royal Guard -> Gladiator -> Vanquisher
    "Hunter-Humans": (hs(armor="leather", tabard=False, hat="hair", weapon="bow", pauldron=False, back="quiver"), "foot"),
    "Ranger-Humans": (hs(armor="leather", tabard=False, hat="hood", weapon="bow", pauldron=False, back="quiver", capecol=True), "foot"),
    "Ranger Captain-Humans": (hs(armor="coat", tabard=False, hat="hood", weapon="bow", pauldron=True, back="quiver", capecol=True), "foot"),
    "Ranger-General-Humans": (hs(armor="plate", hat="plumed", weapon="bow", back="quiver", capecol=True), "foot"),
    "Man-at-Arms-Humans": (hs(armor="plate", hat="kettle", weapon="mace", shield="kite"), "foot"),
    "Royal Guard-Humans": (hs(armor="plate", hat="great_helm", weapon="sword", shield="kite", capecol=True), "foot"),
    "Gladiator-Humans": (hs(armor="plate", hat="sallet", weapon="axe", shield="round", capecol=True), "foot"),
    "Vanquisher-Humans": (hs(armor="plate", hat="plumed", weapon="halberd", capecol=True), "foot"),
    "Azerite Sharpshooter-Humans": (hs(armor="plate", hat="goggles", weapon="sniper", back="pack", capecol=True), "foot"),
    "Warbringer-Humans": (hs(armor="plate", hat="great_helm", weapon="axe", back="banner", capecol=True), "foot"),
    "Pikeman-Humans": (hs(armor="plate", hat="sallet", weapon="pike", shield="round"), "foot"),
    "Vanguard-Humans": (hs(armor="plate", hat="great_helm", weapon="halberd"), "foot"),
    "Rifleman-Humans": (hs(armor="coat", hat="tricorn", weapon="musket", pauldron=False, back="bandolier"), "foot"),
    "Grenadier-Humans": (hs(armor="coat", hat="kettle", weapon="grenade", pauldron=False, back="bandolier"), "foot"),
    "Mountaineer-Humans": (hs(armor="leather", hat="goggles", weapon="sniper", pauldron=False, back="pack"), "foot"),
    "Kul Tiran Marine-Humans": (hs(armor="coat", hat="tricorn", weapon="rifle", pauldron=False, back="bandolier", beard=HAIR), "foot"),
    "Skyguard-Humans": (hs(armor="leather", hat="goggles", weapon="rifle", pauldron=False, back="pack", capecol=True), "foot"),
    "Siegebreaker-Humans": (hs(armor="plate", hat="great_helm", weapon="mortar", back="pack"), "foot"),
    "Swordsman-Humans": (hs(armor="plate", hat="sallet", weapon="sword", shield="kite"), "foot"),
    # ---- Humans: riders
    "Outrider-Humans": (lambda c, fx, fy, u: h_rider(c, fx, fy, u, "outrider"), "mounted"),
    "Mounted Archer-Humans": (lambda c, fx, fy, u: h_rider(c, fx, fy, u, "archer"), "mounted"),
    "Lancer-Humans": (lambda c, fx, fy, u: h_rider(c, fx, fy, u, "lancer"), "mounted"),
    "Knight of the Silver Hand": (lambda c, fx, fy, u: h_rider(c, fx, fy, u, "silver"), "mounted"),
    "Knight-Humans": (lambda c, fx, fy, u: h_rider(c, fx, fy, u, "knight"), "mounted"),   # Humans field Knights again (Paladin is endgame)
    "War Rider-Humans": (lambda c, fx, fy, u: h_rider(c, fx, fy, u, "warrider"), "mounted"),
    "Grand Champion-Humans": (lambda c, fx, fy, u: h_rider(c, fx, fy, u, "champion"), "mounted"),
    "Halberdier-Humans": (hs(armor="plate", hat="kettle", weapon="halberd", pauldron=True), "foot"),
    "Phalanx-Humans": (hs(armor="plate", hat="great_helm", weapon="pike", shield="kite", capecol=True), "foot"),
    # ---- Humans: siege
    "Catapult-Humans": (lambda c, fx, fy, u: catapult(c, fx, fy, u, H), "siege"),
    "Ballista-Humans": (lambda c, fx, fy, u: ballista(c, fx, fy, u, H), "siege"),
    "Steam Tank": (lambda c, fx, fy, u: steam_tank(c, fx, fy, u), "siege"),
    "Mortar Team-Humans": (lambda c, fx, fy, u: mortar_team(c, fx, fy, u, H), "siege"),
    # ---- Humans: great people, religious units, hero, cleric
    "Great Artist-Humans": (hr(robe_col=L_MAIN, hat="feather_cap", prop="lute", mantle=False), "civ"),
    "Great Engineer-Humans": (hs(armor="cloth", tabard=False, hat="goggles", weapon="hammer", pauldron=False, back="pack"), "civ"),
    "Great General-Humans": (hs(armor="plate", hat="crown", weapon="banner", capecol=True, beard=(120, 80, 40)), "civ"),
    "Great Merchant-Humans": (hr(robe_col=L_MAIN, hat="hair", prop="coins", beard=HAIR), "civ"),
    "Great Prophet-Humans": (hr(robe_col=(240, 235, 222), robe_layer="base", hat="mitre", prop="staff", glow=(255, 230, 140)), "civ"),
    "Archmage": (hr(robe_col=L_MAIN, hat="hair", hair=(205, 205, 212), beard=(232, 232, 238), prop="book",
                    glow=(170, 140, 255)), "civ"),
    "Great Admiral-Humans": (hr(robe_col=L_MAIN, hat="tricorn", prop="spyglass", beard=HAIR), "civ"),
    "Inquisitor-Humans": (hr(robe_col=(70, 60, 60), robe_layer="base", hood=True, prop="censer", glow=(255, 200, 110)), "civ"),
    "Northshire Cleric": (hr(robe_col=(240, 235, 222), robe_layer="base", hat="hair", prop="light"), "civ"),
    "Uther the Lightbringer": (uther, "foot"),
    # ---- Orcs: soldiers
    "Scout-Orcs": (os_(armor="hide", hat="mohawk", weapon="stick", pauldrons=0, back="pack"), "foot"),
    "Hunter-Orcs": (os_(armor="hide", hat="feathers", weapon="bow", pauldrons=0, back="quiver"), "foot"),
    "Ranger-Orcs": (os_(armor="hide", hat="hood", weapon="bow", pauldrons=0, back="quiver"), "foot"),
    "Ranger Captain-Orcs": (os_(armor="iron", hat="feathers", weapon="bow", pauldrons=1, back="quiver"), "foot"),
    "Ranger-General-Orcs": (os_(armor="iron", hat="warhelm", weapon="bow", pauldrons=2, back="quiver", paint_face=True), "foot"),
    "Man-at-Arms-Orcs": (os_(armor="iron", hat="skullcap", weapon="axe", shield="hide", pauldrons=1), "foot"),
    "Royal Guard-Orcs": (os_(armor="iron", hat="warhelm", weapon="axe", shield="hide", pauldrons=2), "foot"),
    "Gladiator-Orcs": (os_(armor="iron", hat="warhelm", weapon="axe", shield="hide", pauldrons=2, back="banner"), "foot"),
    "Vanquisher-Orcs": (os_(armor="iron", hat="warhelm", weapon="cleaver", pauldrons=2, paint_face=True), "foot"),
    "Warbringer-Orcs": (os_(armor="iron", hat="warhelm", weapon="axe", pauldrons=2, back="banner", paint_face=True), "foot"),
    "Azerite Sharpshooter-Orcs": (os_(armor="iron", hat="goggles", weapon="sniper", pauldrons=1, back="pack"), "foot"),
    "Pikeman-Orcs": (os_(armor="iron", hat="skullcap", weapon="pike", shield="hide"), "foot"),
    "Vanguard-Orcs": (os_(armor="iron", hat="warhelm", weapon="halberd", pauldrons=2), "foot"),
    "Rifleman-Orcs": (os_(armor="hide", hat="skullcap", weapon="musket", pauldrons=1, back="pack"), "foot"),
    "Grenadier-Orcs": (os_(armor="hide", hat="goggles", weapon="grenade", pauldrons=1), "foot"),
    "Mountaineer-Orcs": (os_(armor="hide", hat="goggles", weapon="sniper", pauldrons=0, back="pack"), "foot"),
    "Kul Tiran Marine-Orcs": (os_(armor="coat", hat="tricorn", weapon="rifle", pauldrons=0, back="pack"), "foot"),
    "Skyguard-Orcs": (os_(armor="hide", hat="goggles", weapon="rifle", pauldrons=1, back="pack"), "foot"),
    "Siegebreaker-Orcs": (os_(armor="iron", hat="warhelm", weapon="mortar", pauldrons=2), "foot"),
    "Swordsman-Orcs": (os_(armor="iron", hat="topknot", weapon="axe", shield="hide"), "foot"),
    # ---- Orcs: riders
    "Mounted Archer-Orcs": (lambda c, fx, fy, u: o_rider(c, fx, fy, u, "archer"), "mounted"),
    "Knight-Orcs": (lambda c, fx, fy, u: o_rider(c, fx, fy, u, "knight"), "mounted"),
    "Lancer-Orcs": (lambda c, fx, fy, u: o_rider(c, fx, fy, u, "lancer"), "mounted"),
    "Raider": (lambda c, fx, fy, u: o_rider(c, fx, fy, u, "raider"), "mounted"),
    "War Rider-Orcs": (lambda c, fx, fy, u: o_rider(c, fx, fy, u, "warrider"), "mounted"),
    "Grand Champion-Orcs": (lambda c, fx, fy, u: o_rider(c, fx, fy, u, "champion"), "mounted"),
    "Halberdier-Orcs": (os_(armor="iron", hat="skullcap", weapon="halberd", pauldrons=1), "foot"),
    "Phalanx-Orcs": (os_(armor="iron", hat="warhelm", weapon="pike", shield="hide", pauldrons=2, paint_face=True), "foot"),
    # ---- Orcs: siege
    "Catapult-Orcs": (lambda c, fx, fy, u: catapult(c, fx, fy, u, O), "siege"),
    "Ballista-Orcs": (lambda c, fx, fy, u: ballista(c, fx, fy, u, O), "siege"),
    "Mortar Team-Orcs": (lambda c, fx, fy, u: mortar_team(c, fx, fy, u, O), "siege"),
    # ---- Orcs: great people, religious units, hero, cleric
    "Great Artist-Orcs": (or_(prop="drum", hat="feathers"), "civ"),
    "Great Engineer-Orcs": (or_(prop="wrench", hat="goggles", pelt=False, robe_col=CLOTH_BROWN, robe_layer="base"), "civ"),
    "Great General-Orcs": (os_(armor="iron", hat="warhelm", weapon="banner", pauldrons=2, back="banner", paint_face=True), "civ"),
    "Great Merchant-Orcs": (or_(prop="coins"), "civ"),
    "Great Prophet-Orcs": (or_(prop="staff", glow=(150, 230, 255), hat="feathers"), "civ"),
    "Great Scientist-Orcs": (or_(prop="book", hat="hood", glow=(255, 140, 80)), "civ"),
    "Great Admiral-Orcs": (or_(prop="spyglass", hat="tricorn", pelt=False), "civ"),
    "Inquisitor-Orcs": (or_(prop="censer", hat="hood", glow=(150, 240, 110)), "civ"),
    "Earthen Shaman": (or_(prop="light", hat="feathers", glow=(150, 255, 160)), "civ"),
    "Grom Hellscream": (grom, "foot"),
}

# Oct 2026: the magic schools' units ("<unit>-Humans" / "<unit>-Orcs" templates) and the Kirin Tor Magus
import wc_lines as _lines
RECIPES.update(_lines.magic_recipes(hr, or_))

# canvases (1x) for sprites the stock art doesn't have (new units): copied from their base unit's sprite
NEW_CANVAS = {"Knight of the Silver Hand": "Cavalry-Humans", "Raider": "Cavalry-Orcs"}
# design height of each archetype at u = 1, in 2x pixels (bbox of a typical figure incl. weapon)
NOMINAL = {"foot": 96, "civ": 96, "mounted": 132, "siege": 56}


# ================================================================== output
UNIT_DIR = "TileSets/AbsoluteUnits/Units/"
SCALE = {"foot": (92, 0.95, 1.15), "civ": (92, 0.9, 1.2), "mounted": (135, 0.75, 1.1), "siege": (60, 0.9, 1.5)}


def _find(image_dirs, stem):
    import os
    for d in image_dirs:
        p = os.path.join(d, UNIT_DIR, stem + ".png")
        if os.path.exists(p):
            return p
    return None


def render(name, ref_path):
    """Draw recipe `name` on a 2x copy of the reference sprite's canvas, feet where the
    reference figure stands and sized to match it."""
    from PIL import Image
    from pixelize import make_canvas as Canvas
    draw, arch = RECIPES[name]
    ref = Image.open(ref_path)
    w, h = ref.size
    x0, y0, x1, y1 = ref.getbbox()
    nom, lo, hi = SCALE[arch]
    u = max(lo, min(hi, 2 * (y1 - y0) / nom))
    fx, fy = (x0 + x1), 2 * y1 + (2 if arch == "mounted" else 4)
    fy = min(fy, 2 * h - 2)
    # keep the figure on the canvas: shrink if its design height would poke out of the top
    top_room = {"foot": 112, "civ": 110, "mounted": 150, "siege": 72}[arch]
    if fy - top_room * u < 2:
        u = max(0.5, (fy - 2) / top_room)
    c = Canvas(2 * w, 2 * h)
    draw(c, fx, fy, u)
    return c.finish()


def write_all(image_dirs):
    """Overwrite (or add) the painted sprites, including era variants such as
    "Great Artist-Humans-Age of the Lich King", so the look holds in every era."""
    import os
    from multiprocessing import Pool
    jobs = []
    for name in RECIPES:
        ref = _find(image_dirs, name) or _find(image_dirs, NEW_CANVAS.get(name, ""))
        if ref is None:
            print("painted: no reference sprite for", name)
            continue
        jobs.append((name, ref))
    with Pool(min(8, os.cpu_count() or 2)) as pool:
        rendered = pool.starmap(render, jobs)
    count = 0
    for (name, ref), layers in zip(jobs, rendered):
        targets = set()
        for d in image_dirs:
            folder = os.path.join(d, UNIT_DIR)
            if not os.path.isdir(folder):
                continue
            for fname in os.listdir(folder):
                stem = fname[:-4]
                if stem.endswith("-1") or stem.endswith("-2"):
                    stem = stem[:-2]
                if stem == name or (stem.startswith(name + "-") and stem[len(name) + 1:].startswith("Age of")):
                    targets.add((folder, stem))
        if not targets:      # a new unit: goes beside its reference
            targets.add((os.path.dirname(ref), name))
        for folder, stem in targets:
            for suf, im in zip(("", "-1", "-2"), layers):
                im.save(os.path.join(folder, stem + suf + ".png"))
                count += 1
    return count
