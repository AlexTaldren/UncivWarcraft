"""Map sprites for the eight raid bosses (Oct 2026 depth pass), in the mod's pixel-art style.

Original drawings on the shared figure kit (wc_style_units.Fig on a PixelCanvas), much larger
than ordinary units so a raid boss reads as a raid boss on the map:
Onyxia (black dragon), Hakkar (feathered blood serpent), Ragnaros (fire lord rising from lava
with his hammer), C'Thun (the great eye and its tentacles), Sapphiron (skeletal frost wyrm),
Deathwing (armoured black dragon split by molten seams), Kil'jaeden (winged eredar lord)
and N'Zoth (a mass of tentacles and eyes).
Bosses belong to the barbarians, so no nation-colour layers are drawn.
"""
import math
import os

from wc_style_units import Fig, shadow
from paint import mix

W, H = 190, 162          # 2x AbsoluteUnits (95x81)
UNIT_DIR = "TileSets/AbsoluteUnits/Units/"


def glow(f, x, y, r, col):
    m = f.ell(x, y, r, r)
    f.c.glow(m, col, radius=r * 1.2, strength=0.9)
    f.paint(m, mix(col, (255, 255, 255), 0.4), mat="glow", outline=0)


def wing(f, root, tips, membrane, bone, torn=False):
    """A bat-like wing: bone struts from the root to each tip, a scalloped membrane between them."""
    pts = [root, tips[0]]
    for t0, t1 in zip(tips, tips[1:]):
        mx, my = (t0[0] + t1[0]) / 2, (t0[1] + t1[1]) / 2
        pts += [(mx + (root[0] - mx) * 0.28, my + (root[1] - my) * 0.28), t1]
    f.paint(f.poly(pts), membrane, mat="leather")
    for t in tips:
        f.paint(f.cap(root, t, 1.8, 0.7), bone, mat="bone", outline=0.5)
    f.paint(f.cap(root, tips[0], 2.6, 1.4), bone, mat="bone", outline=0.6)   # leading edge


def dragon(f, body, belly, wingcol, horn, eye, seams=None, scale=1.0, bone=None):
    s = scale
    shadow(f, 70 * s)
    bone = bone or mix(body, (255, 255, 255), 0.15)
    # far wing
    wing(f, (-6 * s, -62 * s), [(-40 * s, -132 * s), (-62 * s, -112 * s), (-74 * s, -84 * s), (-66 * s, -60 * s)],
         mix(wingcol, (0, 0, 0), 0.3), bone)
    # tail
    f.paint(f.curve([(-30 * s, -36 * s), (-60 * s, -30 * s), (-82 * s, -14 * s)], 9 * s, 2 * s), body, mat="leather")
    f.paint(f.poly([(-86 * s, -18 * s), (-92 * s, -6 * s), (-78 * s, -10 * s)]), horn, mat="bone")
    # legs (far)
    f.paint(f.cap((-18 * s, -30 * s), (-22 * s, 0), 6 * s, 4 * s), mix(body, (0, 0, 0), 0.25), mat="leather")
    f.paint(f.cap((20 * s, -30 * s), (24 * s, 0), 6 * s, 4 * s), mix(body, (0, 0, 0), 0.25), mat="leather")
    # body
    f.paint(f.ell(0, -42 * s, 36 * s, 22 * s), body, mat="leather")
    f.paint(f.ell(4 * s, -30 * s, 26 * s, 9 * s), belly, mat="leather")
    # near legs
    f.paint(f.cap((-8 * s, -32 * s), (-12 * s, 0), 7 * s, 5 * s), body, mat="leather")
    f.paint(f.cap((28 * s, -34 * s), (34 * s, 0), 7 * s, 5 * s), body, mat="leather")
    for x in (-14, -9, 31, 37):
        f.paint(f.poly([(x * s, 0), ((x + 3) * s, 4 * s), ((x + 5) * s, 0)]), horn, mat="bone", outline=0.3)
    # neck and head
    f.paint(f.curve([(26 * s, -54 * s), (44 * s, -80 * s), (56 * s, -96 * s)], 11 * s, 8 * s), body, mat="leather")
    f.paint(f.ell(64 * s, -100 * s, 17 * s, 11 * s), body, mat="leather")
    f.paint(f.poly([(70 * s, -106 * s), (94 * s, -99 * s), (72 * s, -92 * s)]), body, mat="leather")      # snout
    f.paint(f.poly([(66 * s, -96 * s), (86 * s, -92 * s), (68 * s, -88 * s)]), mix(belly, (0, 0, 0), 0.2), mat="leather")  # jaw
    for k in range(3):
        f.paint(f.cap((58 * s - k * 4 * s, -106 * s), (44 * s - k * 6 * s, -122 * s + k * 6 * s), 2.4 * s, 0.6 * s), horn, mat="bone", outline=0.4)
    glow(f, 68 * s, -102 * s, 2.4 * s, eye)
    # near wing
    wing(f, (6 * s, -60 * s), [(-14 * s, -140 * s), (-36 * s, -130 * s), (-50 * s, -104 * s), (-40 * s, -70 * s)], wingcol, bone)
    if seams:
        for a, b in (((-20, -48), (4, -38)), ((10, -56), (28, -40)), ((-6, -60), (-2, -40)), ((36, -64), (48, -84))):
            m = f.cap((a[0] * s, a[1] * s), (b[0] * s, b[1] * s), 1.4 * s, 1.0 * s)
            f.c.glow(m, seams, radius=3, strength=0.8)
            f.paint(m, seams, mat="glow", outline=0)
        for x, y in ((-10, -64), (6, -66), (22, -62)):
            f.paint(f.poly([((x - 4) * s, y * s), (x * s, (y - 10) * s), ((x + 4) * s, y * s)]), (70, 70, 80), mat="metal")


def onyxia(c, fx, fy, u):
    f = Fig(c, fx, fy, u)
    dragon(f, (52, 44, 56), (140, 80, 70), (120, 50, 70), (215, 205, 195), (255, 90, 60), scale=0.95)


def deathwing(c, fx, fy, u):
    f = Fig(c, fx, fy, u)
    dragon(f, (40, 36, 40), (80, 56, 50), (95, 50, 40), (205, 195, 185), (255, 150, 40), seams=(255, 120, 30), scale=1.08)


def sapphiron(c, fx, fy, u):
    f = Fig(c, fx, fy, u)
    s = 1.0
    shadow(f, 64)
    bone, ice, dark = (210, 225, 240), (150, 200, 240), (90, 110, 140)
    wing(f, (-6, -62), [(-40, -132), (-62, -112), (-74, -84), (-66, -60)], mix(ice, (0, 0, 0), 0.35), bone)
    for k in range(7):                                                       # tail vertebrae
        f.paint(f.ell(-34 - k * 8, -34 + k * 3, 5 - k * 0.4, 4 - k * 0.3), bone, mat="bone")
    for x in (-16, 22):
        f.paint(f.cap((x, -30), (x - 4, 0), 3.5, 2.5), dark, mat="bone")
    f.paint(f.ell(0, -42, 30, 18), mix(ice, (40, 60, 90), 0.5), mat="cloth", dark=0.7)      # cold glow inside the ribs
    for k in range(6):                                                        # ribs
        x = -22 + k * 9
        f.paint(f.curve([(x, -58), (x - 4, -42), (x + 2, -28)], 2.2, 1.6), bone, mat="bone", outline=0.4)
    f.paint(f.curve([(-28, -58), (0, -62), (28, -56)], 3.0), bone, mat="bone")              # spine
    for x in (-8, 30):
        f.paint(f.cap((x, -32), (x - 4, 0), 4, 3), bone, mat="bone")
    for k in range(6):                                                        # neck
        f.paint(f.ell(30 + k * 5, -60 - k * 7, 5, 4), bone, mat="bone")
    f.paint(f.ell(64, -100, 13, 8), bone, mat="bone")
    f.paint(f.poly([(70, -104), (90, -98), (72, -92)]), bone, mat="bone")
    f.paint(f.poly([(66, -94), (84, -88), (68, -86)]), dark, mat="bone")
    for k in range(2):
        f.paint(f.cap((58 - k * 5, -106), (46 - k * 6, -124 + k * 4), 2.4, 0.6), bone, mat="bone", outline=0.4)
    glow(f, 68, -102, 2.6, (120, 220, 255))
    wing(f, (6, -60), [(-14, -140), (-36, -130), (-50, -104), (-40, -70)], mix(ice, (0, 0, 0), 0.15), bone)
    for x, y in ((92, -92), (100, -84), (94, -78)):                           # frost breath
        glow(f, x, y, 3, (190, 235, 255))


def hakkar(c, fx, fy, u):
    f = Fig(c, fx, fy, u)
    shadow(f, 56)
    red, dark, gold, feather = (170, 40, 40), (90, 20, 26), (230, 190, 70), (60, 150, 90)
    for k in range(6):                                                       # feathered wings
        a = math.radians(200 + k * 14)
        tip = (-6 + 76 * math.cos(a), -70 + 64 * math.sin(a))
        f.paint(f.cap((-4, -72), tip, 9, 3), feather if k % 2 else mix(feather, red, 0.5), mat="cloth")
    for k in range(5):
        a = math.radians(-20 - k * 14)
        tip = (10 + 70 * math.cos(a), -70 + 60 * math.sin(a))
        f.paint(f.cap((8, -72), tip, 9, 3), feather if k % 2 else mix(feather, red, 0.5), mat="cloth", dark=0.85)
    f.paint(f.curve([(-60, -6), (-20, -26), (20, -8), (40, -30)], 8, 12), red, mat="skin")   # coils
    f.paint(f.curve([(40, -30), (34, -60), (20, -84)], 13, 10), red, mat="skin")
    for k in range(6):
        f.paint(f.ell(36 - k * 3, -40 - k * 8, 6, 2), gold, mat="gold", outline=0.3)        # belly scales
    f.paint(f.ell(22, -94, 13, 11), red, mat="skin")                                         # head
    f.paint(f.poly([(26, -96), (46, -92), (28, -86)]), dark, mat="skin")
    for k in range(4):                                                                       # feather crest
        f.paint(f.cap((14, -100), (-4 - k * 4, -120 + k * 6), 3, 1), gold if k % 2 else feather, mat="cloth")
    glow(f, 26, -98, 2.4, (255, 60, 50))


def ragnaros(c, fx, fy, u):
    f = Fig(c, fx, fy, u)
    lava, rock, fire = (255, 120, 30), (80, 40, 30), (255, 200, 80)
    m = f.ell(0, -6, 74, 14)                                                                 # lava pool
    f.c.glow(m, lava, radius=6, strength=0.8)
    f.paint(m, lava, mat="glow", outline=0.4)
    f.paint(f.ell(0, -8, 56, 8), fire, mat="glow", outline=0)
    f.paint(f.poly([(-30, -10), (30, -10), (24, -70), (-24, -70)]), rock, mat="metal")       # torso of rock
    for a, b in (((-20, -20), (-6, -50)), ((14, -18), (4, -56)), ((-10, -60), (12, -64))):
        mm = f.cap(a, b, 2, 1.4)
        f.c.glow(mm, lava, radius=3, strength=0.8)
        f.paint(mm, lava, mat="glow", outline=0)
    f.paint(f.ell(0, -80, 26, 16), rock, mat="metal")                                        # shoulders
    f.paint(f.ell(0, -100, 13, 13), rock, mat="metal")                                       # head
    for side in (-1, 1):
        f.paint(f.curve([(side * 10, -106), (side * 24, -118), (side * 30, -136)], 4, 1.4), (60, 30, 24), mat="bone")   # horns
        f.paint(f.cap((side * 22, -82), (side * 40, -64), 9, 7), rock, mat="metal")         # arms
    glow(f, -4, -102, 2.4, fire)
    glow(f, 5, -102, 2.4, fire)
    for k in range(5):                                                                       # beard of flame
        x = -10 + k * 5
        mm = f.poly([(x - 3, -92), (x, -72 + (k % 2) * 6), (x + 3, -92)])
        f.c.glow(mm, lava, radius=3, strength=0.7)
        f.paint(mm, fire, mat="glow", outline=0)
    f.paint(f.cap((40, -64), (62, -128), 3, 3), (60, 40, 36), mat="metal")                 # Sulfuras, his hammer
    f.paint(f.poly([(46, -126), (80, -132), (82, -114), (48, -110)]), (70, 50, 44), mat="metal")
    f.c.glow(f.ell(64, -122, 16, 8), lava, radius=6, strength=0.7)


def cthun(c, fx, fy, u):
    f = Fig(c, fx, fy, u)
    shadow(f, 60)
    flesh, dark = (120, 70, 110), (70, 36, 66)
    for k, (x, h, lean) in enumerate(((-64, 70, -14), (-40, 96, -8), (40, 92, 10), (66, 66, 16))):   # tentacles
        f.paint(f.curve([(x, 0), (x + lean * 0.5, -h * 0.6), (x + lean, -h)], 9, 2), dark if k % 2 else flesh, mat="skin")
        for j in range(3):
            f.paint(f.ell(x + lean * (0.2 + j * 0.25), -h * (0.25 + j * 0.22), 2, 2), (230, 200, 160), mat="bone", outline=0)
    f.paint(f.cap((0, 0), (0, -70), 26, 20), flesh, mat="skin")                              # stalk
    f.paint(f.ell(0, -96, 36, 34), flesh, mat="skin")                                        # the eye
    f.paint(f.ell(0, -96, 24, 22), (240, 225, 200), mat="bone")
    glow(f, 0, -96, 10, (255, 90, 60))
    f.paint(f.ell(0, -96, 4, 9), (30, 10, 10), mat="flat", outline=0)
    for k in range(10):                                                                      # veins and lid folds
        a = math.radians(k * 36)
        f.paint(f.cap((math.cos(a) * 26, -96 + math.sin(a) * 24), (math.cos(a) * 34, -96 + math.sin(a) * 32), 1.2, 0.6),
                dark, mat="skin", outline=0)


def kiljaeden(c, fx, fy, u):
    f = Fig(c, fx, fy, u)
    shadow(f, 40)
    skin, armor, fel, wingc = (120, 70, 140), (60, 66, 60), (120, 255, 80), (60, 120, 50)
    for side in (-1, 1):                                                                     # wings
        wing(f, (side * 8, -96), [(side * 70, -150), (side * 86, -120), (side * 80, -90), (side * 56, -70)],
             mix(wingc, (0, 0, 0), 0.2), (90, 80, 70))
    for side in (-1, 1):                                                                     # legs (hooved)
        f.paint(f.cap((side * 12, -50), (side * 18, -4), 8, 6), skin, mat="skin")
        f.paint(f.ell(side * 19, -2, 7, 4), (40, 30, 30), mat="bone")
    f.paint(f.poly([(-22, -50), (22, -50), (28, -20), (-28, -20)]), armor, mat="metal")       # war skirt
    f.paint(f.ell(0, -74, 24, 24), armor, mat="metal")                                       # chest
    for side in (-1, 1):
        f.paint(f.ell(side * 26, -92, 13, 10), armor, mat="metal")                           # pauldrons
        f.paint(f.poly([(side * 20, -100), (side * 30, -122), (side * 34, -98)]), (200, 190, 170), mat="bone")
        f.paint(f.cap((side * 30, -88), (side * 40, -56), 7, 6), skin, mat="skin")           # arms
    f.paint(f.ell(0, -108, 11, 12), skin, mat="skin")                                        # head
    for side in (-1, 1):
        f.paint(f.curve([(side * 6, -116), (side * 18, -126), (side * 16, -146)], 3.6, 1), (40, 30, 30), mat="bone")
    glow(f, -4, -110, 2.2, fel)
    glow(f, 4, -110, 2.2, fel)
    f.paint(f.poly([(-6, -102), (6, -102), (0, -88)]), (60, 40, 70), mat="skin")             # tentacle beard
    for side in (-1, 1):                                                                     # fel fire in his hands
        mm = f.ell(side * 42, -54, 7, 7)
        f.c.glow(mm, fel, radius=5, strength=0.9)
        f.paint(mm, mix(fel, (255, 255, 255), 0.3), mat="glow", outline=0)


def nzoth(c, fx, fy, u):
    f = Fig(c, fx, fy, u)
    shadow(f, 70)
    flesh, dark, eye = (70, 40, 80), (40, 22, 48), (255, 210, 80)
    for k in range(9):                                                                       # crown of tentacles
        x = -72 + k * 18
        h = 60 + (k * 37 % 50)
        lean = (k - 4) * 4
        f.paint(f.curve([(x, -10), (x + lean, -h * 0.6), (x + lean * 2, -h)], 8, 2), dark if k % 2 else flesh, mat="skin")
    f.paint(f.ell(0, -40, 60, 34), flesh, mat="skin")                                        # body
    f.paint(f.ell(0, -82, 34, 26), flesh, mat="skin")                                        # head mass
    for (x, y, r) in ((-30, -40, 5), (-12, -30, 4), (12, -34, 5), (32, -44, 4), (0, -54, 6), (-18, -58, 3), (20, -60, 3)):
        f.paint(f.ell(x, y, r + 1.5, r + 1), dark, mat="skin", outline=0)
        glow(f, x, y, r * 0.6, eye)
    glow(f, -10, -86, 3.2, eye)
    glow(f, 10, -86, 3.2, eye)
    for k in range(6):                                                                       # face tentacles
        x = -15 + k * 6
        f.paint(f.curve([(x, -72), (x + 2, -58), (x - 2, -46)], 3, 1), dark, mat="skin")
    for side in (-1, 1):
        f.paint(f.curve([(side * 26, -100), (side * 40, -120), (side * 36, -140)], 5, 1.6), (30, 18, 36), mat="bone")


BOSSES = {
    "Onyxia": (onyxia, 0.82), "Hakkar the Soulflayer": (hakkar, 0.92), "Ragnaros the Firelord": (ragnaros, 0.92),
    "C'Thun": (cthun, 0.9), "Sapphiron": (sapphiron, 0.86), "Deathwing the Destroyer": (deathwing, 0.8),
    "Kil'jaeden the Deceiver": (kiljaeden, 0.88), "N'Zoth the Corruptor": (nzoth, 0.86),
}


def render(name):
    from pixelize import make_canvas
    draw, u = BOSSES[name]
    c = make_canvas(W, H)
    draw(c, W / 2, H - 6, u)
    return c.finish()[0]


def write_all(images_dir):
    folder = os.path.join(images_dir, UNIT_DIR)
    os.makedirs(folder, exist_ok=True)
    for name in BOSSES:
        render(name).save(os.path.join(folder, name + ".png"))
    return len(BOSSES)
