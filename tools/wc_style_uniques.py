"""Pixel-art unique units, heroes and clerics for the other 16 races.

Most are recipes on the shared figure kit, drawn with their race's context (see
wc_style_races) plus a few unit-specific touches (Malfurion's antlers, Kel'Thuzad's
lich face, human-form Gilneans...). War machines and monsters get their own drawings:
Steam Armor, Spider Tank, Goblin Shredder, Dark Iron Golem, Lightforged Warframe,
Harvest Golem, Mountain Giant, Abomination, Ghoul, Crypt Fiend, Meat Wagon, Glaive
Thrower, Wisp and the Zandalari direhorn. All designs are original.
"""
import math

import wc_style_units as U
import wc_style_more as M
import wc_style_races as WR
from wc_style_units import CTX, Fig, L_MAIN, L_DARK, BONE, shadow, boot, pole
from wc_style_more import hs, os_, hr, or_
from paint import mix


# ================================================================== helpers
def ctx(draw, colors=None, **spec):
    """Run `draw` with extra colours / spec entries on top of the race context."""
    def run(c, fx, fy, u):
        old_c, old_s = dict(CTX.colors), dict(CTX.spec)
        CTX.colors.update(colors or {})
        CTX.spec.update(spec)
        try:
            draw(c, fx, fy, u)
        finally:
            CTX.colors, CTX.spec = old_c, old_s
    return run


def scaled(draw, k):
    return lambda c, fx, fy, u: draw(c, fx, fy, u * k)


def rider(kind, brute=False):
    return lambda c, fx, fy, u: (M.o_rider if brute else M.h_rider)(c, fx, fy, u, kind)


def glowball(f, x, y, r, col):
    m = f.ell(x, y, r, r)
    f.c.glow(m, col, radius=r * 0.9, strength=0.8)
    f.paint(m, mix(col, (255, 255, 255), 0.45), mat="glow", outline=0.4)


# faces with hero touches -------------------------------------------------------
def face_malfurion(f, x, y, **k):
    WR.face_elf(f, x, y, glow=(255, 230, 140), brows=True, **{**k, "beard": (60, 120, 80)})
    for s, d in ((-1, 0.85), (1, 1.0)):     # antlers
        f.paint(f.curve([(x + s * 3, y - 8), (x + s * 7 - 4, y - 18), (x + s * 4 - 6, y - 28)], 1.8, 0.8), (150, 110, 70), mat="wood",
                outline=0.5, dark=d)
        f.paint(f.curve([(x + s * 5 - 3, y - 18), (x + s * 10, y - 22)], 1.2, 0.6), (150, 110, 70), mat="wood", outline=0.4, dark=d)
    return None


def face_crown(face, gem=(255, 80, 60)):
    def fn(f, x, y, **k):
        hat = face(f, x, y, **{**k, "hat": "hair"})
        f.paint(f.poly([(x - 8, y - 7), (x - 8, y - 14), (x - 4, y - 10), (x, y - 15), (x + 4, y - 10), (x + 8, y - 14), (x + 8, y - 7)]),
                U.GOLD, mat="gold", outline=0.5)
        f.paint(f.ell(x, y - 10, 1.4, 1.4), gem, mat="glow", outline=0)
        return None
    return fn


def face_lich(f, x, y, **k):
    WR.face_skeleton(f, x, y)
    f.paint(f.poly([(x - 9, y - 6), (x - 6, y - 14), (x - 2, y - 9), (x + 2, y - 15), (x + 6, y - 9), (x + 9, y - 13), (x + 9, y - 5)]),
            (110, 160, 210), mat="metal", outline=0.5)
    return None


def face_pale_human(f, x, y, **k):
    return WR.face_human(f, x, y, **k)


def face_golem(eye=(255, 140, 50), crest=None):
    def fn(f, x, y, **k):
        f.paint(f.poly([(x - 9, y + 6), (x - 9, y - 6), (x - 4, y - 11), (x + 7, y - 11), (x + 11, y - 5), (x + 11, y + 6)]), U.STEEL, mat="metal")
        f.paint(f.poly([(x + 1, y - 3), (x + 11, y - 3), (x + 11, y), (x + 1, y)]), (30, 25, 25), mat="flat", outline=0)
        e = f.ell(x + 6, y - 1.5, 3.5, 1.2)
        f.c.glow(e, eye, radius=2, strength=0.7)
        f.paint(e, eye, mat="glow", outline=0)
        if crest:
            f.paint(f.poly([(x - 1, y - 11), (x + 2, y - 20), (x + 5, y - 11)]), crest, mat="glow", outline=0.5)
        return None
    return fn


def face_pumpkin(f, x, y, **k):
    """Harvest golem: a sackcloth-and-iron head with a lantern glow inside."""
    f.paint(f.ell(x, y, 9, 9), (190, 150, 90), mat="cloth")
    for dx in (-4, 0, 4):
        f.paint(f.curve([(x + dx, y - 8), (x + dx, y + 8)], 0.5), (120, 90, 50), mat="flat", outline=0)
    for ex in (3, 8):
        e = f.ell(x + ex, y - 1, 1.6, 1.8)
        f.c.glow(e, (255, 200, 60), radius=1.5, strength=0.6)
        f.paint(e, (255, 220, 90), mat="glow", outline=0)
    f.paint(f.poly([(x - 10, y - 5), (x - 2, y - 16), (x + 12, y - 7), (x - 2, y - 9)]), (100, 80, 50), mat="cloth")     # floppy hat
    return None


def bface_giant(f, x, y, hair="topknot", helm=False):
    rock = U.OSKIN
    f.paint(f.ell(x, y - 1, 11, 11), rock, mat="bone")
    f.paint(f.poly([(x + 2, y + 1), (x + 14, y + 1), (x + 15, y + 9), (x + 3, y + 12)]), mix(rock, (0, 0, 0), 0.1), mat="bone")
    f.paint(f.poly([(x - 4, y + 4), (x + 12, y + 8), (x + 8, y + 18), (x - 2, y + 16)]), (80, 120, 60), mat="fur")       # moss beard
    f.paint(f.poly([(x + 1, y - 6), (x + 13, y - 5), (x + 12, y - 2), (x + 2, y - 3)]), mix(rock, (0, 0, 0), 0.35), mat="bone", outline=0.4)
    WR.eyes(f, x + 8, y - 1.5, (255, 220, 120), glow=True)
    for dx in (-6, 0):
        f.paint(f.poly([(x + dx - 2, y - 9), (x + dx + 1, y - 17), (x + dx + 3, y - 9)]), (100, 140, 80), mat="fur", outline=0.4)   # moss tufts


def bface_abom(f, x, y, hair="topknot", helm=False):
    sk = U.OSKIN
    f.paint(f.ell(x, y, 9, 8), sk, mat="skin")
    f.paint(f.poly([(x - 1, y + 2), (x + 12, y + 2), (x + 12, y + 8), (x, y + 9)]), sk, mat="skin")
    for k in range(4):     # stitches
        f.paint(f.cap((x - 6 + k * 3, y - 6), (x - 5 + k * 3, y - 2), 0.5), (60, 40, 40), mat="flat", outline=0)
    f.paint(f.poly([(x + 3, y + 5), (x + 12, y + 5), (x + 12, y + 6.5), (x + 3, y + 6.5)]), (50, 30, 30), mat="flat", outline=0)
    WR.eyes(f, x + 6, y - 2, (255, 230, 90), glow=True, r=1.1)


def bface_ghoul(f, x, y, hair="topknot", helm=False):
    sk = U.OSKIN
    f.paint(f.poly([(x - 4, y - 2), (x - 14, y - 8), (x - 4, y + 3)]), sk, mat="skin", dark=0.9)
    f.paint(f.ell(x, y - 1, 8, 8), sk, mat="skin")
    f.paint(f.poly([(x, y + 1), (x + 13, y + 2), (x + 12, y + 9), (x + 1, y + 9)]), sk, mat="skin")
    f.paint(f.poly([(x + 3, y + 4), (x + 13, y + 4.5), (x + 12, y + 7), (x + 3, y + 7)]), (60, 30, 30), mat="flat", outline=0)
    for k in range(4):
        f.paint(f.poly([(x + 4 + k * 2.2, y + 4), (x + 5 + k * 2.2, y + 6.5), (x + 6 + k * 2.2, y + 4)]), BONE, mat="bone", outline=0)
    WR.eyes(f, x + 6, y - 2, (130, 210, 255), glow=True, r=1.2)


# ================================================================== custom drawings
def wisp(c, fx, fy, u):
    f = Fig(c, fx, fy, u)
    shadow(f, 10)
    for k, (dx, dy, r) in enumerate(((-10, -26, 3.2), (-16, -20, 2.4), (-21, -15, 1.8))):
        glowball(f, dx, dy, r, (150, 220, 255))
    glowball(f, 0, -34, 9, (170, 230, 255))
    f.paint(f.ell(-2, -36, 3, 3), (255, 255, 255), mat="glow", outline=0)


def ghoul(c, fx, fy, u):
    return ctx(lambda c, fx, fy, u: M.o_soldier(c, fx, fy, u * 0.95, armor="bare", hat=None, weapon="claws_none", pauldrons=0),
               {"oskin": (128, 140, 118), "dleather": (70, 60, 60)}, family="brute", body=(0.95, 0.82), head=0.95,
               bface=bface_ghoul, hat_swap=None)(c, fx, fy, u)


def abomination(c, fx, fy, u):
    def draw(c, fx, fy, u):
        M.o_soldier(c, fx, fy, u, armor="bare", hat=None, weapon="cleaver", pauldrons=0)
        f = Fig(c, fx, fy, u)
        # a hook on a chain and a bloated, stitched belly
        f.paint(f.ell(2, -44, 15, 12), mix(U.OSKIN, (255, 230, 230), 0.15), mat="skin")
        for k in range(4):
            f.paint(f.cap((-8 + k * 5, -50), (-6 + k * 5, -40), 0.6), (70, 40, 40), mat="flat", outline=0)
        f.paint(f.curve([(-16, -60), (-24, -46), (-22, -30)], 1.0), (130, 130, 135), mat="metal", outline=0.4)
        f.paint(f.curve([(-22, -30), (-26, -24), (-20, -22)], 1.6, 0.8), U.STEEL, mat="metal", outline=0.5)
    return ctx(draw, {"oskin": (170, 186, 150), "dleather": (80, 60, 60)}, family="brute", body=(1.4, 0.98), head=0.9,
               bface=bface_abom, hat_swap=None)(c, fx, fy, u)


def crypt_fiend(c, fx, fy, u):
    f = Fig(c, fx, fy, u)
    shadow(f, 30)
    shell, dark = (70, 80, 95), (45, 50, 60)
    for k, (x0, x1, d) in enumerate(((-22, -34, 0.7), (-8, -18, 0.7), (6, -2, 0.7))):     # far legs
        f.paint(f.curve([(x0, -26), (x1, -40), (x1 - 6, 0)], 2.2, 1.0), dark, mat="metal", dark=d)
    f.paint(f.ell(-12, -28, 20, 11), shell, mat="metal")                                  # abdomen
    for k in range(3):
        f.paint(f.curve([(-24 + k * 9, -36), (-22 + k * 9, -22)], 0.8), (140, 200, 230), mat="glow", outline=0)
    for k, (x0, x1) in enumerate(((-18, -26), (-4, -6), (10, 16))):                       # near legs
        f.paint(f.curve([(x0, -24), (x1, -42), (x1 + 6, 0)], 2.4, 1.0), shell, mat="metal")
    f.paint(f.ell(10, -46, 9, 12), mix(shell, (255, 255, 255), 0.1), mat="metal")      # upright thorax
    f.paint(f.cap((14, -50), (24, -60), 3.0, 2.2), shell, mat="metal")                   # webbing arm
    f.paint(f.ell(14, -62, 7, 6), shell, mat="metal")                                     # head
    f.paint(f.curve([(18, -58), (24, -54), (22, -50)], 1.2, 0.5), BONE, mat="bone", outline=0.5)   # mandible
    WR.eyes(f, 17, -64, (130, 220, 120), glow=True)
    f.paint(f.poly([(6, -60), (2, -72), (10, -64)]), dark, mat="metal", outline=0.5)      # crest spike


def meat_wagon(c, fx, fy, u):
    f = Fig(c, fx, fy, u)
    shadow(f, 30)
    wood = (95, 75, 60)
    f.paint(f.poly([(-26, -14), (24, -14), (24, -8), (-26, -8)]), wood, mat="wood")
    f.paint(f.poly([(-22, -14), (10, -14), (12, -28), (-24, -28)]), (70, 60, 55), mat="wood")      # cage
    for x in (-18, -10, -2, 6):
        f.paint(f.cap((x, -14), (x, -28), 0.8), (120, 115, 110), mat="metal", outline=0.3)
    for (x, y, r) in ((-14, -22, 4), (-6, -24, 3.5), (2, -21, 4)):     # grisly cargo
        f.paint(f.ell(x, y, r, r * 0.8), (170, 80, 80), mat="skin", outline=0.4)
    f.paint(f.poly([(10, -14), (14, -34), (18, -34), (16, -14)]), wood, mat="wood")
    f.paint(f.cap((-20, -36), (16, -32), 2.0), wood, mat="wood")
    f.paint(f.ell(-22, -38, 5, 3.5), (150, 70, 70), mat="skin")
    f.paint(f.poly([(18, -34), (26, -32), (26, -27), (18, -29)]), L_MAIN, layer="l2", mat="cloth")
    M.wheel(f, -16, -6, 7, wood)
    M.wheel(f, 16, -6, 7, wood)
    f.paint(f.ell(-34, -28, 9, 10), (150, 160, 140), mat="skin")      # a stitched ghoul pushing from behind
    f.paint(f.ell(-31, -42, 6, 6), (150, 160, 140), mat="skin")
    WR.eyes(f, -28, -43, (255, 230, 90), glow=True, r=1.0)
    f.paint(f.cap((-34, -20), (-34, -2), 3.5), (90, 80, 70), mat="cloth")


def glaive_thrower(c, fx, fy, u):
    M.ballista(c, fx, fy, u, "Humans")
    f = Fig(c, fx, fy, u)
    M.moonglaive(f, 34, -40, 9)


def goblin_sapper(c, fx, fy, u):
    M.h_soldier(c, fx, fy, u, armor="leather", tabard=False, hat="goggles", weapon="grenade", pauldron=False)
    f = Fig(c, fx, fy, u)
    f.paint(f.ell(-14, -52, 11, 11), (50, 50, 55), mat="metal")             # a huge bomb on his back
    f.paint(f.poly([(-17, -64), (-11, -64), (-11, -61), (-17, -61)]), (110, 105, 100), mat="metal", outline=0.4)
    f.paint(f.curve([(-14, -64), (-18, -72), (-12, -76)], 0.8), (120, 90, 60), mat="flat", outline=0)
    glowball(f, -12, -77, 2.4, (255, 190, 60))


def shredder(c, fx, fy, u):
    f = Fig(c, fx, fy, u)
    shadow(f, 26)
    metal, dark = (150, 140, 120), (95, 88, 80)
    for x, d in ((-10, 0.75), (8, 1.0)):                                             # piston legs
        f.paint(f.cap((x, -40), (x - 4, -20), 4.5, 3.6), dark, mat="metal", dark=d)
        f.paint(f.cap((x - 4, -20), (x + 2, -4), 3.6, 3.2), metal, mat="metal", dark=d)
        f.paint(f.poly([(x - 6, -6), (x + 9, -6), (x + 11, 0), (x - 7, 0)]), dark, mat="metal", dark=d)
    body = f.poly([(-18, -38), (16, -38), (20, -56), (12, -78), (-14, -78), (-20, -58)])
    f.paint(body, metal, mat="metal")
    f.paint(f.c.intersect(body, f.poly([(-30, -50), (30, -50), (30, -44), (-30, -44)])), L_MAIN, layer="l2", mat="cloth", outline=0.4)
    f.paint(f.poly([(-10, -78), (10, -78), (8, -66), (-8, -66)]), (40, 60, 70), mat="metal")   # cockpit
    WR.face_goblin(Fig(c, *f.p(0, -74), f.u * 0.75, uniform=True), 0, 0)
    f.paint(f.cap((-20, -80), (-20, -98), 2.6, 2.2), (70, 68, 70), mat="metal")           # exhaust
    for k, (dx, dy, r) in enumerate(((-21, -103, 3), (-25, -108, 4))):
        f.paint(f.ell(dx, dy, r, r * 0.8), (200, 200, 205), mat="cloth", outline=0.4)
    f.paint(f.cap((14, -62), (30, -56), 4, 3.5), dark, mat="metal")                      # saw arm
    saw = f.ell(36, -54, 10, 10)
    f.paint(saw, (205, 210, 215), mat="metal")
    for a in range(0, 360, 45):
        t = math.radians(a)
        f.paint(f.poly([(36 + math.cos(t) * 9, -54 - math.sin(t) * 9), (36 + math.cos(t + 0.3) * 13, -54 - math.sin(t + 0.3) * 13),
                        (36 + math.cos(t + 0.5) * 9, -54 - math.sin(t + 0.5) * 9)]), (220, 225, 230), mat="metal", outline=0.4)
    f.paint(f.ell(36, -54, 3, 3), dark, mat="metal", outline=0.4)


def steam_armor(c, fx, fy, u):
    f = Fig(c, fx, fy, u)
    shadow(f, 26)
    metal, dark = U.STEEL, U.DSTEEL
    for x, d in ((-11, 0.75), (9, 1.0)):
        f.paint(f.cap((x, -36), (x, -8), 6.5, 6), dark, mat="metal", dark=d)
        f.paint(f.poly([(x - 8, -8), (x + 10, -8), (x + 11, 0), (x - 9, 0)]), metal, mat="metal", dark=d)
    body = f.poly([(-22, -34), (20, -34), (24, -60), (14, -80), (-16, -80), (-24, -60)])
    f.paint(body, metal, mat="metal")
    f.paint(f.c.intersect(body, f.poly([(-30, -46), (30, -46), (30, -40), (-30, -40)])), L_MAIN, layer="l2", mat="cloth", outline=0.4)
    for x in (-16, -6, 4, 14):
        f.paint(f.ell(x, -70, 1.4, 1.4), M.BRASS, mat="gold", outline=0.3)
    f.paint(f.poly([(-8, -80), (10, -80), (10, -66), (-8, -66)]), (50, 60, 70), mat="metal")   # open cockpit
    WR.face_dwarf(Fig(c, *f.p(1, -76), f.u * 0.8, uniform=True), 0, 0, hat="cap")
    f.paint(f.cap((-18, -78), (-20, -100), 3.2, 2.6), (80, 78, 82), mat="metal")
    for dx, dy, r in ((-21, -105, 3.5), (-26, -111, 4.5)):
        f.paint(f.ell(dx, dy, r, r * 0.85), (200, 200, 205), mat="cloth", outline=0.4)
    f.paint(f.cap((16, -64), (28, -52), 6, 5), dark, mat="metal")                           # cannon arm
    M.tube(f, (24, -54), (44, -58), 4.5)
    f.paint(f.cap((-20, -64), (-26, -44), 5.5, 5), dark, mat="metal")                       # hammer fist
    f.paint(f.ell(-26, -42, 6, 6), metal, mat="metal")


def spider_tank(c, fx, fy, u):
    f = Fig(c, fx, fy, u)
    shadow(f, 32)
    metal, dark = U.STEEL, U.DSTEEL
    for x0, x1, d in ((-14, -30, 0.7), (8, 22, 0.7)):
        f.paint(f.curve([(x0, -26), (x1, -40), (x1 + (4 if x1 > 0 else -4), 0)], 2.4, 1.6), dark, mat="metal", dark=d)
    f.paint(f.ell(-2, -28, 22, 12), metal, mat="metal")
    f.paint(f.poly([(-18, -26), (14, -26), (14, -22), (-18, -22)]), L_MAIN, layer="l2", mat="cloth", outline=0.4)
    for x in (-14, -6, 2, 10):
        f.paint(f.ell(x, -33, 1.3, 1.3), M.BRASS, mat="gold", outline=0.3)
    for x0, x1 in ((-10, -24), (4, 18), (-2, 6)):
        f.paint(f.curve([(x0, -22), (x1, -36), (x1 + (5 if x1 > 0 else -5), 0)], 2.6, 1.6), metal, mat="metal")
    M.tube(f, (8, -36), (32, -40), 4)
    f.paint(f.ell(-4, -40, 8, 6), (70, 80, 90), mat="metal")                                # dome
    WR.face_gnome(Fig(c, *f.p(-4, -46), f.u * 0.62, uniform=True), 0, 0)


def big_warframe(face, colors, weapon="hammer", glow=None):
    """A walking war machine on the human soldier frame, much larger than a man."""
    def draw(c, fx, fy, u):
        M.h_soldier(c, fx, fy, u, armor="plate", tabard=True, hat="hair", weapon=weapon, pauldron=True, glow=glow)
    return ctx(draw, colors, face=face, body=(1.35, 1.22), head=1.05, hat_swap=None)


def mountain_giant(c, fx, fy, u):
    def draw(c, fx, fy, u):
        M.o_soldier(c, fx, fy, u, armor="bare", hat=None, weapon="mace", pauldrons=0)
    return ctx(draw, {"oskin": (128, 130, 110), "iron": (110, 80, 50), "dleather": (90, 110, 70)},
               family="brute", body=(1.45, 1.25), head=1.1, bface=bface_giant, hat_swap=None)(c, fx, fy, u * 0.9)


# ---------------------------------------------------------------- the direhorn mount
def direhorn(p, v, armored):
    """A frilled, three-horned beast, in mounts.py's coordinates (facing left)."""
    from mounts import shade, quad_body, barding, blanket
    hide = [(110, 130, 90), (130, 110, 80), (90, 120, 120)][v % 3]
    dk = shade(hide, .7)
    p.leg(17, 28, 13, 6, dk, "far", hoof=(55, 45, 35))
    p.leg(41, 28, 13, 6, dk, "far", hoof=(55, 45, 35))
    p.line(46, 22, 54, 28, 4, dk, "tail")
    quad_body(p, 30, 24, 34, 16, hide, shade(hide, 1.15))
    p.leg(21, 29, 12, 6, hide, "near", hoof=(55, 45, 35))
    p.leg(45, 29, 12, 6, hide, "near", hoof=(55, 45, 35))
    p.poly([(12, 8), (22, 10), (22, 26), (12, 24)], (200, 80, 60), "frill")
    p.ell(10, 22, 7, 6, hide, "head")
    p.poly([(4, 22), (-1, 24), (4, 27)], shade(hide, .8), "beak")
    p.line(8, 17, 1, 11, 2, (235, 225, 200), "horn")
    p.line(12, 16, 7, 9, 2, (235, 225, 200), "horn")
    p.line(5, 21, 1, 19, 2, (235, 225, 200), "horn")
    p.dot(9, 20, (30, 25, 20), "eye")
    if armored:
        barding(p, 18, 42, 18, 9)
    blanket(p, 31, 14, 13, 6)
    return 31, 14


def direhorn_mount():
    import mounts as MT
    MT.RACE_MOUNT.setdefault("_direhorn", direhorn)
    MT.SCALE.setdefault("_direhorn", 1.3)
    return WR.make_mount("_direhorn", "direhorn")


# ================================================================== the roster
FOOT, CIV, MOUNT, SIEGE = "foot", "civ", "mounted", "siege"
GILNEAN = dict(face=WR.face_human, body=(1.0, 1.0), head=1.0, hat_swap=None)
GILNEAN_C = {"skin": (232, 186, 150), "hair": (80, 60, 45)}

RECIPES = {
    # ---- Dwarves
    "Ironforge Rifleman": ("Dwarves", hs(armor="leather", hat="kettle", weapon="rifle", pauldron=False, back="pack", tabard=True), FOOT),
    "Ram Rider": ("Dwarves", rider("knight"), MOUNT),
    "Steam Armor": ("Dwarves", steam_armor, FOOT),
    "Muradin Bronzebeard": ("Dwarves", ctx(hs(armor="plate", hat="kettle", weapon="hammer", capecol=True, glow=(160, 220, 255)),
                                           {"hair": (40, 32, 28)}), FOOT),
    "Dwarven Priest": ("Dwarves", hr(robe_col=(236, 230, 214), robe_layer="base", hat="hair", prop="light", beard=U.HAIR), CIV),
    # ---- Dark Iron Dwarves
    "Fireguard": ("Dark Iron Dwarves", hs(armor="plate", hat="kettle", weapon="halberd", glow=(255, 140, 50)), FOOT),
    "Dark Iron Golem": ("Dark Iron Dwarves", big_warframe(face_golem((255, 130, 40)), {"steel": (96, 88, 88), "dsteel": (60, 54, 54),
                                                                                      "gold": (240, 120, 40)}), FOOT),
    "Dagran Thaurissan": ("Dark Iron Dwarves", ctx(hs(armor="plate", hat="hair", weapon="hammer", capecol=True),
                                                   face=face_crown(WR.face_dwarf)), FOOT),
    "Flamekeeper": ("Dark Iron Dwarves", hr(robe_col=(130, 45, 30), robe_layer="base", hat="hair", prop="light", glow=(255, 140, 50)), CIV),
    # ---- Gnomes
    "Mechanostrider Rider": ("Gnomes", rider("outrider"), MOUNT),
    "Gnomish Bombardier": ("Gnomes", lambda c, fx, fy, u: M.mortar_team(c, fx, fy, u * 1.45, "Humans"), SIEGE),
    "Spider Tank": ("Gnomes", spider_tank, SIEGE),
    # Oct 2026: the Gnomes' own top melee unit - a gnome rebuilt in mechanical plate (Mechagon)
    "Mechagnome Trooper": ("Gnomes", scaled(ctx(hs(armor="plate", hat="goggles", weapon="hammer", shield="kite", pauldron=True,
                                                   glow=(120, 220, 255)),
                                               {"steel": (150, 160, 178), "dsteel": (96, 104, 120), "skin": (200, 205, 215),
                                                "gold": (120, 220, 255)}), 1.12), FOOT),
    "Kelsey Steelspark": ("Gnomes", hs(armor="leather", tabard=False, hat="hair", weapon="sword", pauldron=False, capecol=True), FOOT),
    "Decontaminator": ("Gnomes", hr(robe_col=(215, 200, 70), robe_layer="base", hat="goggles", prop="censer", glow=(150, 240, 120)), CIV),
    # ---- Night Elves
    "Huntress": ("Night Elves", rider("glaive"), MOUNT),
    "Glaive Thrower": ("Night Elves", glaive_thrower, SIEGE),
    "Mountain Giant": ("Night Elves", mountain_giant, FOOT),
    "Wisp": ("Night Elves", scaled(wisp, 1.7), CIV),
    # Wisps are the Night Elves' builders, so their Peasant art is the Wisp too (user decision).
    # (moved right so its trailing light stays on the civilian's side of the tile)
    "Peasant-Night Elves": ("Night Elves", lambda c, fx, fy, u: wisp(c, fx + 34 * u, fy, u * 1.7), CIV),
    "Malfurion Stormrage": ("Night Elves", ctx(hr(robe_col=(70, 110, 70), robe_layer="base", hat="hair", hair=(40, 120, 90),
                                                   prop="staff", glow=(140, 255, 140)), face=face_malfurion), CIV),
    "Cenarion Druid": ("Night Elves", hr(robe_col=(90, 110, 60), robe_layer="base", hat="hair", prop="staff", glow=(150, 255, 150)), CIV),
    # ---- Draenei
    "Vindicator": ("Draenei", hs(armor="plate", hat="great_helm", weapon="hammer", shield="kite", glow=(255, 230, 150)), FOOT),
    "Elekk Rider": ("Draenei", rider("lancer"), MOUNT),
    "Lightforged Warframe": ("Draenei", big_warframe(face_golem((200, 240, 255), crest=(150, 220, 255)),
                                                     {"steel": (232, 226, 196), "dsteel": (170, 160, 120), "gold": (250, 215, 110)}), FOOT),
    "Maraad": ("Draenei", hs(armor="plate", hat="hair", weapon="hammer", glow=(255, 230, 150), capecol=True), FOOT),
    "Anchorite": ("Draenei", hr(robe_col=(220, 225, 240), robe_layer="base", hat="hair", prop="light", glow=(200, 230, 255)), CIV),
    # ---- Worgen
    "Worgen Stalker": ("Worgen", hs(armor="leather", tabard=False, hat="hair", weapon="claws", pauldron=False), FOOT),
    "Worgen Ravager": ("Worgen", scaled(hs(armor="leather", tabard=False, hat="hair", weapon="claws", pauldron=False, capecol=True), 1.08), FOOT),
    "Gilnean Rifleman": ("Worgen", ctx(hs(armor="coat", hat="officer", weapon="rifle", pauldron=False, back="bandolier"), GILNEAN_C, **GILNEAN), FOOT),
    "Gilnean Hunter": ("Worgen", ctx(hs(armor="leather", tabard=False, hat="hood", weapon="bow", pauldron=False, back="quiver"),
                                     GILNEAN_C, **GILNEAN), FOOT),
    "Harvest Golem": ("Worgen", big_warframe(face_pumpkin, {"steel": (120, 100, 80), "dsteel": (90, 70, 55), "gold": (200, 160, 80)},
                                             weapon="halberd"), FOOT),
    "Darius Crowley": ("Worgen", hs(armor="leather", tabard=False, hat="hair", weapon="sword", pauldron=False, capecol=True), FOOT),
    "Harvest Witch": ("Worgen", ctx(hr(robe_col=(80, 60, 50), robe_layer="base", hat="hair", prop="censer", glow=(255, 180, 80)),
                                    {"skin": (232, 186, 150), "hair": (60, 40, 30)}, **GILNEAN), CIV),
    # ---- High Elves
    "Farstrider": ("High Elves", hs(armor="leather", tabard=False, hat="hair", weapon="bow", pauldron=False, back="quiver", capecol=True), FOOT),
    "Ranger-Lord": ("High Elves", hs(armor="plate", hat="hair", weapon="bow", back="quiver", capecol=True), FOOT),
    "Alleria Windrunner": ("High Elves", ctx(hs(armor="leather", tabard=False, hat="hair", weapon="bow", pauldron=False, back="quiver",
                                                capecol=True), {"hair": (250, 230, 150)}), FOOT),
    "Lightwarden": ("High Elves", hr(robe_col=(240, 236, 220), robe_layer="base", hat="hair", prop="light"), CIV),
    # ---- Blood Elves
    "Spellbreaker": ("Blood Elves", hs(armor="plate", hat="sallet", weapon="sword", shield="kite"), FOOT),
    "Blood Knight": ("Blood Elves", rider("knight"), MOUNT),
    "Kael'thas Sunstrider": ("Blood Elves", ctx(hr(robe_col=(170, 40, 40), robe_layer="base", hat="hair", prop="light", glow=(140, 255, 120)),
                                                {"hair": (240, 200, 110)}), CIV),
    "Sunfury Priest": ("Blood Elves", hr(robe_col=(180, 50, 45), robe_layer="base", hat="hair", prop="light", glow=(255, 220, 120)), CIV),
    # ---- Forsaken
    "Abomination": ("Forsaken", abomination, FOOT),
    "Meat Wagon": ("Forsaken", meat_wagon, SIEGE),
    "Deathstalker": ("Forsaken", hs(armor="leather", tabard=False, hat="hood", weapon="crossbow", pauldron=False, back="quiver", capecol=True), FOOT),
    "Nathanos Blightcaller": ("Forsaken", hs(armor="leather", tabard=False, hat="hood", weapon="bow", pauldron=False, back="quiver", capecol=True), FOOT),
    # ---- Scourge
    "Ghoul": ("Scourge", ghoul, FOOT),
    "Acolyte": ("Scourge", ctx(hr(robe_col=(52, 44, 62), robe_layer="base", hood=True, prop=None), {"skin": (210, 196, 182)},
                               face=WR.face_human), CIV),
    "Death Knight": ("Scourge", rider("knight"), MOUNT),
    "Crypt Fiend": ("Scourge", scaled(crypt_fiend, 1.4), FOOT),
    "Kel'Thuzad": ("Scourge", ctx(hr(robe_col=(50, 70, 110), robe_layer="base", hat="hair", prop="staff", glow=(130, 210, 255)),
                                  face=face_lich), CIV),
    # ---- Goblins
    "Goblin Shredder": ("Goblins", scaled(shredder, 1.35), FOOT),
    "Goblin Sapper": ("Goblins", goblin_sapper, FOOT),
    "Gazlowe": ("Goblins", hs(armor="cloth", tabard=False, hat="goggles", weapon="hammer", pauldron=False, back="pack"), FOOT),
    "Hazmat Crew": ("Goblins", hr(robe_col=(220, 190, 60), robe_layer="base", hat="goggles", prop="censer", glow=(150, 240, 110)), CIV),
    # ---- Kul Tirans
    "Admiralty Gunner": ("Kul Tirans", hs(armor="coat", hat="tricorn", weapon="musket", pauldron=False, back="bandolier"), FOOT),
    "Daelin Proudmoore": ("Kul Tirans", ctx(hs(armor="coat", hat="tricorn", weapon="sword", pauldron=False, capecol=True),
                                            {"hair": (200, 200, 205)}), FOOT),
    "Tidesage": ("Kul Tirans", hr(robe_col=(50, 110, 105), robe_layer="base", hat="hair", prop="staff", glow=(120, 240, 230)), CIV),
    # ---- Tauren
    "Tauren Warrior": ("Tauren", os_(armor="hide", hat="topknot", weapon="hammer", pauldrons=1), FOOT),
    "Kodo Beast": ("Tauren", rider("archer", brute=True), MOUNT),
    "Baine Bloodhoof": ("Tauren", os_(armor="iron", hat="topknot", weapon="hammer", pauldrons=2, glow=(255, 230, 150)), FOOT),
    "Sunwalker": ("Tauren", or_(prop="light", glow=(255, 225, 120), robe_col=(225, 200, 120), robe_layer="base"), CIV),
    # ---- Trolls
    "Headhunter": ("Trolls", os_(armor="hide", hat="mohawk", weapon="spear", pauldrons=0, back="quiver"), FOOT),
    "Troll Berserker": ("Trolls", os_(armor="hide", hat="mohawk", weapon="axe", pauldrons=1), FOOT),
    "Rokhan": ("Trolls", os_(armor="hide", hat="mohawk", weapon="spear", pauldrons=1, paint_face=True), FOOT),
    "Witch Doctor": ("Trolls", or_(prop="staff", glow=(150, 255, 120), hat="feathers"), CIV),
    # ---- Zandalari Trolls
    "Raptor Rider": ("Zandalari Trolls", rider("outrider", brute=True), MOUNT),
    "Direhorn Rider": ("Zandalari Trolls", ctx(rider("knight", brute=True), mount=direhorn_mount()), MOUNT),
    "Rastakhan": ("Zandalari Trolls", or_(prop="staff", glow=(255, 215, 90), robe_col=(205, 165, 60), robe_layer="base"), CIV),
    "Loa Speaker": ("Zandalari Trolls", or_(prop="staff", glow=(255, 200, 80), hat="feathers"), CIV),
    # ---- Pandaren
    "Brewmaster": ("Pandaren", os_(armor="hide", hat="topknot", weapon="stick", pauldrons=0, back="pack"), FOOT),
    "Shado-Pan Monk": ("Pandaren", os_(armor="coat", hat="hood", weapon="halberd", pauldrons=0), FOOT),
    "Chen Stormstout": ("Pandaren", scaled(os_(armor="hide", hat="topknot", weapon="stick", pauldrons=0, back="pack"), 1.06), FOOT),
    "Mistweaver": ("Pandaren", or_(prop="light", glow=(140, 240, 220), hat="hood"), CIV),
}
