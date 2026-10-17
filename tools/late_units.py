"""Warcraft replacements for Unciv's modern-era unit sprites.

Unciv's AbsoluteUnits art turns into WWII soldiers, tanks, helicopters and steel
warships in the late game. These functions draw Warcraft-style equivalents instead:
steam golems, siege engines and mechano-tanks, gnomish flying machines, goblin rocket
wagons, ironclads and airships, a giant turtle and an orcish juggernaught, titan-forged
parts for the Titan vessel. Late infantry are built from the medieval soldiers with new
gear (helms, pauldrons, bomb bandoliers, rocket packs, tricorns), so the race sprites
(race_sprites.py) and the Humans' blue and gold still apply to them.

Each function returns Unciv's 3 layers [base, inner-colour, outer-colour] on a canvas
of the same size and footprint as the sprite it replaces.
"""
import colorsys, math
from PIL import Image, ImageDraw, ImageFilter
from mounts import Paint, shade

P = "TileSets/AbsoluteUnits/Units/"
IRON, IRON_D, BRASS, WOOD, WOOD_D = (120, 122, 132), (80, 82, 92), (205, 165, 70), (140, 95, 55), (95, 65, 40)
GLOW, FEL, ARC = (255, 170, 60), (120, 230, 70), (120, 200, 255)
DARK = (35, 28, 26)


def layers(a, name):
    return [a.crop(P + name + s) for s in ("", "-1", "-2")]


def hsv(p):
    return colorsys.rgb_to_hsv(p[0] / 255, p[1] / 255, p[2] / 255)


def bbox_all(ls):
    bs = [l.getbbox() for l in ls if l.getbbox()]
    return min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)


def glow_of(im, color, radius=1.4, strength=1.2):
    m = im.split()[3].filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(radius))
    m = m.point(lambda v: min(255, int(v * strength)))
    g = Image.new("RGBA", im.size, tuple(color) + (0,))
    g.putalpha(m)
    return g


def paint_layers(size, fn, glows=()):
    """Run fn(p) on a Paint and return [base, -1, -2]; glows: (fn, colour) extra lit bits."""
    p = Paint(*size)
    fn(p)
    base, l1, l2 = p.render()
    out = Image.new("RGBA", size)
    for gfn, col in glows:
        g = Paint(*size)
        gfn(g)
        gl = g.render(None)[0]
        out.alpha_composite(glow_of(gl, col))
        base.alpha_composite(gl)
    out.alpha_composite(base)
    return [out, l1, l2]


def shadow(p, cx, cy, rx, ry=None):
    """A soft ground shadow is drawn by the game for units; we add a slim dark contact
    line only where wheels or feet touch."""
    pass


# ======================================================================= infantry
def stamp(ls, part):
    """Draw `part` over the sprite, clearing the tint layers beneath it."""
    pp = part.load()
    for l in ls[1:]:
        lp = l.load()
        for y in range(l.height):
            for x in range(l.width):
                if pp[x, y][3]:
                    lp[x, y] = (0, 0, 0, 0)
    ls[0].alpha_composite(part)
    return ls


def outline(part, col=DARK):
    out = Image.new("RGBA", part.size)
    pp, op = part.load(), out.load()
    w, h = part.size
    for y in range(h):
        for x in range(w):
            if pp[x, y][3]:
                continue
            if any(0 <= x + dx < w and 0 <= y + dy < h and pp[x + dx, y + dy][3]
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                op[x, y] = col + (255,)
    out.alpha_composite(part)
    return out


def recolor(ls, test, new, layer_to=0):
    """Re-dye pixels matching test(h, s, v) with new(v) (layer_to 2 = faction colour)."""
    px = ls[0].load()
    tint = ls[layer_to].load() if layer_to else None
    for y in range(ls[0].height):
        for x in range(ls[0].width):
            p = px[x, y]
            if p[3] < 200:
                continue
            h, s, v = hsv(p)
            if test(h, s, v):
                c = new(v)
                px[x, y] = c + (255,)
                if tint:
                    g = int(min(255, 150 + 105 * v))
                    tint[x, y] = (g, g, g, 255)
    return ls


def head_and_gun(ls):
    """Head box (top of figure) and the barrel tip (leftmost pixel in the upper body)."""
    x0, y0, x1, y1 = bbox_all(ls)
    px = ls[0].load()
    top_rows = range(y0, y0 + int((y1 - y0) * 0.45))
    tip = min(((x, y) for y in top_rows for x in range(x0, x1) if px[x, y][3] > 200), key=lambda q: q[0])
    return (x0, y0, x1, y1), tip


def gear(ls, draw, glow=None):
    part = Image.new("RGBA", ls[0].size)
    d = ImageDraw.Draw(part)
    draw(d)
    part = outline(part)
    if glow:
        g = glow_of(part, glow)
        g.alpha_composite(part)
        part = g
    return stamp(ls, part)


def is_red(h, s, v):
    return (h < 0.03 or h > 0.93) and s > 0.45 and v > 0.3


def fusilier(ls):
    """Rifleman in a steel cuirass, steel helm and bayonet."""
    recolor(ls, is_red, lambda v: tuple(int(c * (0.6 + 0.6 * v)) for c in (150, 155, 165)))
    (x0, y0, x1, y1), (tx, ty) = head_and_gun(ls)
    hx = (x0 + x1) // 2 + 3
    def d(d):
        d.line([(tx - 5, ty), (tx, ty)], fill=(215, 220, 230, 255), width=1)            # bayonet
        d.ellipse([hx - 4, y0 - 1, hx + 3, y0 + 4], fill=(150, 155, 165, 255))         # steel helm
        d.line([(hx - 5, y0 + 3), (hx + 4, y0 + 3)], fill=(120, 125, 135, 255))
    return gear(ls, d)


def shock_trooper(ls):
    """Musketeer in heavy plate: crested helm, big pauldrons, tabard in faction colour."""
    recolor(ls, lambda h, s, v: 0.5 < h < 0.72 and s > 0.35, lambda v: tuple(int(c * (0.7 + 0.5 * v)) for c in (170, 175, 185)),
            layer_to=2)                                                                  # blue coat -> faction tabard
    (x0, y0, x1, y1), _ = head_and_gun(ls)
    hx = (x0 + x1) // 2 + 3
    def d(d):
        d.ellipse([hx - 4, y0 - 1, hx + 4, y0 + 5], fill=(160, 165, 175, 255))
        d.line([(hx, y0 - 4), (hx + 1, y0 - 1)], fill=(190, 40, 40, 255), width=2)      # crest
        for px_ in (hx - 8, hx + 6):
            d.ellipse([px_ - 3, y0 + 8, px_ + 3, y0 + 12], fill=(175, 180, 190, 255))  # pauldrons
    return gear(ls, d)


def grenadier(ls):
    """Musketeer with a bandolier of bombs and a lit bomb raised to throw."""
    (x0, y0, x1, y1), _ = head_and_gun(ls)
    cx = (x0 + x1) // 2
    def d(d):
        d.line([(cx - 4, y0 + 10), (cx + 6, y0 + 22)], fill=(110, 75, 45, 255), width=2)
        for k in range(3):
            bx, by = cx - 2 + k * 3, y0 + 13 + k * 4
            d.ellipse([bx - 1.5, by - 1.5, bx + 1.5, by + 1.5], fill=(40, 40, 45, 255))
        d.ellipse([x1 - 3, y0 - 2, x1 + 2, y0 + 3], fill=(35, 35, 40, 255))             # bomb in hand
        d.line([(x1, y0 - 2), (x1 + 2, y0 - 5)], fill=(150, 120, 80, 255))
        d.point((x1 + 2, y0 - 6), fill=(255, 220, 90, 255))
    return gear(ls, d, glow=None)


def mountaineer(ls):
    """Rifleman with a fur cap, a heavy pack and a long-barrelled mountain gun."""
    recolor(ls, is_red, lambda v: tuple(int(c * (0.6 + 0.6 * v)) for c in (120, 95, 65)))   # leather coat
    (x0, y0, x1, y1), (tx, ty) = head_and_gun(ls)
    hx = (x0 + x1) // 2 + 3
    def d(d):
        d.ellipse([hx - 5, y0 - 3, hx + 4, y0 + 3], fill=(95, 70, 45, 255))             # fur cap
        d.line([(tx - 7, ty), (tx, ty)], fill=(80, 80, 90, 255), width=2)               # long barrel
        d.rectangle([x1 - 4, y0 + 9, x1 + 2, y0 + 20], fill=(115, 85, 55, 255))         # pack
        d.line([(x1 - 4, y0 + 8), (x1 + 2, y0 + 8)], fill=(160, 160, 165, 255), width=2)  # bedroll
    return gear(ls, d)


def kul_tiran_marine(ls):
    """Rifleman in a navy coat (faction colour), tricorn hat and cutlass."""
    recolor(ls, is_red, lambda v: tuple(int(c * (0.7 + 0.5 * v)) for c in (170, 175, 185)), layer_to=2)
    (x0, y0, x1, y1), _ = head_and_gun(ls)
    hx = (x0 + x1) // 2 + 3
    def d(d):
        d.polygon([(hx - 7, y0 + 2), (hx + 6, y0 + 2), (hx + 3, y0 - 3), (hx - 4, y0 - 3)], fill=(40, 40, 50, 255))
        d.line([(hx - 7, y0 + 2), (hx + 6, y0 + 2)], fill=(220, 180, 70, 255))
        d.line([(x1 - 2, y1 - 22), (x1 + 3, y1 - 12)], fill=(210, 215, 225, 255), width=1)  # cutlass
        d.point((x1 - 2, y1 - 23), fill=(220, 180, 70, 255))
    return gear(ls, d)


def skyguard(ls):
    """Musketeer with a goblin rocket pack, flight goggles and a flaming exhaust."""
    (x0, y0, x1, y1), _ = head_and_gun(ls)
    hx = (x0 + x1) // 2 + 3
    def d(d):
        d.rounded_rectangle([x1 - 3, y0 + 7, x1 + 3, y0 + 21], 2, fill=(150, 150, 160, 255))
        d.rectangle([x1 - 3, y0 + 10, x1 + 3, y0 + 12], fill=(190, 80, 50, 255))
        d.line([(hx - 3, y0 + 3), (hx + 3, y0 + 3)], fill=(90, 200, 230, 255), width=2)  # goggles
    ls = gear(ls, d)
    def flame(d):
        d.polygon([(x1 - 2, y0 + 22), (x1 + 2, y0 + 22), (x1, y0 + 29)], fill=(255, 170, 60, 255))
        d.point((x1, y0 + 24), fill=(255, 240, 170, 255))
    return gear(ls, flame, glow=(255, 150, 50))


def siegebreaker(ls):
    """Musketeer shouldering a goblin rocket launcher for cracking siege engines."""
    (x0, y0, x1, y1), (tx, ty) = head_and_gun(ls)
    def d(d):
        d.line([(tx - 3, ty - 4), (x1 + 4, ty - 6)], fill=(100, 110, 90, 255), width=4)
        d.line([(tx - 3, ty - 5), (x1 + 4, ty - 7)], fill=(130, 140, 115, 255), width=1)
        d.polygon([(tx - 3, ty - 6), (tx - 8, ty - 4), (tx - 3, ty - 2)], fill=(200, 60, 40, 255))
        d.rectangle([x1, ty - 9, x1 + 4, ty - 3], fill=(80, 85, 70, 255))
    return gear(ls, d)


# ======================================================================= vehicles
def war_golem(a):
    """A walking iron golem with a furnace in its chest and smokestacks on its shoulders."""
    W, H = 77, 65
    def f(p):
        for x, b in ((44, -1), (58, 1)):                                  # legs
            p.line(x, 38, x + b, 46, 5, IRON_D, "leg%d" % x)
            p.line(x + b, 46, x, 51, 4, IRON_D, "leg%d" % x)
            p.line(x - 3, 51, x + 4, 51, 2, (60, 60, 68), "foot%d" % x)
        p.ell(51, 30, 12, 10, IRON, "body")
        p.poly([(43, 26), (59, 26), (58, 36), (44, 36)], (220, 220, 220), "plate", layer=2)
        p.line(39, 24, 33, 36, 4, IRON_D, "armL")
        p.ell(32, 38, 3.5, 3, (90, 92, 100), "fist")
        p.line(63, 24, 70, 34, 4, IRON_D, "armR")
        p.poly([(67, 33), (74, 33), (74, 39), (67, 39)], (100, 100, 110), "hammer")
        p.ell(51, 18, 4, 3.5, IRON_D, "head")
        for x in (44, 58):
            p.line(x, 22, x, 13, 3, (70, 70, 78), "stack%d" % x)
    def lit(p):
        p.ell(51, 31, 3, 2.5, GLOW, "furnace")
        p.dot(50, 17, (255, 220, 120), "eye"); p.dot(53, 17, (255, 220, 120), "eye")
        p.ell(44, 10, 2, 1.5, (170, 170, 170), "smoke"); p.ell(58, 9, 2.5, 2, (190, 190, 190), "smoke2")
    return paint_layers((W, H), f, ((lit, GLOW),))


def siege_engine(a):
    """The dwarves' steam siege engine: iron-banded wagon, spiked ram and a steam stack."""
    W, H = 77, 65
    def f(p):
        p.poly([(32, 44), (72, 44), (70, 30), (38, 28)], WOOD, "hull")
        p.poly([(38, 30), (70, 30), (70, 38), (38, 38)], (220, 220, 220), "panel", layer=2)
        for x in (40, 50, 60, 70):
            p.line(x, 28, x, 44, 1, IRON_D, "band%d" % x)
        p.line(72, 38, 77, 38, 3, IRON, "ram")
        p.poly([(74, 35), (77, 38), (74, 41)], (200, 200, 210), "ramtip")
        p.poly([(44, 28), (60, 28), (58, 22), (46, 22)], IRON, "turret")
        p.line(58, 24, 67, 22, 2, IRON_D, "gun")
        p.line(40, 28, 40, 17, 3, (70, 70, 78), "stack")
        for x in (38, 50, 62):
            p.ell(x, 46, 4.5, 4.5, (60, 55, 50), "wheel%d" % x)
            p.ell(x, 46, 1.5, 1.5, BRASS, "hub%d" % x)
    def lit(p):
        p.ell(40, 13, 2.5, 2, (180, 180, 180), "smoke"); p.ell(37, 9, 3, 2.3, (200, 200, 200), "smoke2")
    return paint_layers((W, H), f, ((lit, (200, 200, 200)),))


def mechano_tank(a):
    """A gnomish mechano-tank: treads, a glass dome with its pilot and twin rocket pods."""
    W, H = 77, 65
    def f(p):
        p.poly([(30, 48), (75, 48), (72, 40), (33, 40)], (70, 72, 80), "tread")
        for x in range(34, 74, 5):
            p.ell(x, 46, 2, 2, (110, 110, 118), "roller%d" % x)
        p.poly([(34, 40), (72, 40), (68, 30), (38, 30)], (230, 230, 230), "hull", layer=2)
        p.ell(53, 28, 8, 6, (150, 220, 230), "dome")
        p.ell(52, 29, 2.5, 2.5, (240, 200, 170), "gnome")
        p.ell(52, 26.5, 2.6, 1.3, (230, 110, 180), "hair")
        for y in (30, 35):
            p.line(64, y, 75, y - 3, 2, BRASS, "pod%d" % y)
        p.line(40, 30, 38, 21, 1, (150, 150, 155), "antenna")
    def lit(p):
        p.dot(38, 20, (255, 80, 80), "light")
    return paint_layers((W, H), f, ((lit, (255, 90, 90)),))


def mechagnomes(a):
    """Two mechagnome soldiers: gnome heads under glass, mechanical limbs, arm cannons."""
    W, H = 77, 65
    def one(p, x, y, k):
        p.line(x - 2, y, x - 3, y + 7, 2, IRON_D, "legL%d" % k)
        p.line(x + 2, y, x + 3, y + 7, 2, IRON_D, "legR%d" % k)
        p.ell(x, y - 4, 4.5, 5, (225, 225, 225), "torso%d" % k, layer=2)
        p.line(x - 5, y - 6, x - 9, y - 3, 2, IRON, "arm%d" % k)
        p.poly([(x - 12, y - 5), (x - 8, y - 5), (x - 8, y - 2), (x - 12, y - 2)], BRASS, "cannon%d" % k)
        p.ell(x, y - 11, 3.5, 3.5, (150, 220, 230), "glass%d" % k)
        p.ell(x, y - 10.5, 2, 2, (240, 200, 170), "face%d" % k)
    def f(p):
        one(p, 48, 42, 0)
        one(p, 64, 44, 1)
    def lit(p):
        for x, y in ((48, 38), (64, 40)):
            p.dot(x, y, ARC, "core")
    return paint_layers((W, H), f, ((lit, ARC),))


def iron_colossus(a):
    """A towering titan-forged colossus of iron, its runes glowing blue."""
    W, H = 64, 84
    def f(p):
        for x in (24, 40):
            p.poly([(x - 4, 60), (x + 4, 60), (x + 5, 82), (x - 5, 82)], IRON_D, "leg%d" % x)
        p.poly([(16, 30), (48, 30), (44, 60), (20, 60)], IRON, "torso")
        p.poly([(22, 34), (42, 34), (40, 50), (24, 50)], (225, 225, 225), "chest", layer=2)
        for x, s in ((10, -1), (54, 1)):
            p.ell(x + s * -2, 32, 6, 5, IRON_D, "shoulder%d" % x)
            p.line(x, 35, x + s * 2, 56, 6, IRON, "arm%d" % x)
            p.ell(x + s * 2, 60, 5, 5, IRON_D, "fist%d" % x)
        p.poly([(26, 20), (38, 20), (38, 30), (26, 30)], IRON_D, "head")
        p.poly([(24, 20), (40, 20), (36, 15), (28, 15)], (90, 92, 100), "crown")
    def lit(p):
        p.line(28, 24, 36, 24, 1, ARC, "eyes")
        for y in (38, 44):
            p.line(29, y, 35, y, 1, ARC, "rune%d" % y)
        p.dot(32, 41, ARC, "rune")
    return paint_layers((W, H), f, ((lit, ARC),))


def demolisher(a):
    """The Horde's demolisher: a spiked war wagon with a catapult arm and burning shot."""
    W, H = 77, 65
    def f(p):
        p.poly([(32, 48), (74, 48), (71, 38), (36, 38)], WOOD_D, "bed")
        p.poly([(38, 38), (69, 38), (67, 33), (40, 33)], (220, 220, 220), "side", layer=2)
        for x in range(38, 72, 6):
            p.line(x, 38, x + 1, 34, 1, (200, 200, 210), "spike%d" % x)
        p.line(46, 34, 66, 14, 3, WOOD, "arm")
        p.ell(67, 12, 3.5, 3, (60, 50, 45), "bucket")
        for x in (40, 66):
            p.ell(x, 50, 5, 5, (60, 50, 40), "wheel%d" % x)
            p.ell(x, 50, 1.5, 1.5, IRON, "hub%d" % x)
    def lit(p):
        p.ell(67, 9, 3, 3, (255, 140, 40), "fire")
        p.dot(67, 8, (255, 230, 140), "fire")
    return paint_layers((W, H), f, ((lit, (255, 120, 30)),))


def flak_wagon(a):
    """A goblin rocket wagon: a rack of rockets pointed at the sky."""
    W, H = 77, 65
    def f(p):
        p.poly([(32, 48), (74, 48), (72, 40), (34, 40)], WOOD, "bed")
        p.poly([(36, 40), (70, 40), (70, 36), (36, 36)], (225, 225, 225), "trim", layer=2)
        for k in range(5):
            x = 42 + k * 5
            p.line(x, 36, x + 6, 16, 3, (100, 105, 95), "tube%d" % k)
            p.poly([(x + 5, 17), (x + 8, 15), (x + 7, 12)], (210, 60, 40), "tip%d" % k)
        for x in (40, 66):
            p.ell(x, 50, 5, 5, (60, 55, 50), "wheel%d" % x)
            p.ell(x, 50, 1.5, 1.5, BRASS, "hub%d" % x)
    return paint_layers((W, H), f)


def flak_cannon(a):
    """A dwarven flak cannon: twin barrels on a swivel, aimed at the sky."""
    W, H = 64, 56
    def f(p):
        p.poly([(36, 44), (60, 44), (57, 38), (39, 38)], WOOD_D, "base")
        p.line(40, 44, 36, 48, 2, WOOD, "legL"); p.line(56, 44, 60, 48, 2, WOOD, "legR")
        p.ell(48, 36, 6, 4, IRON_D, "swivel")
        p.poly([(44, 36), (52, 36), (52, 31), (44, 31)], (225, 225, 225), "shield", layer=2)
        for dx in (-2, 2):
            p.line(48 + dx, 32, 56 + dx, 12, 2, IRON, "barrel%d" % dx)
        p.ell(48, 30, 2, 1.6, BRASS, "sight")
    return paint_layers((W, H), f)


def flying_machine(a):
    """The gnomish flying machine: a brass body under a spinning rotor, pilot and guns."""
    W, H = 64, 56
    def f(p):
        p.ell(48, 26, 9, 5, BRASS, "body")
        p.poly([(40, 24), (52, 24), (52, 28), (40, 28)], (225, 225, 225), "stripe", layer=2)
        p.line(39, 26, 28, 24, 2, (150, 120, 60), "tail")
        p.line(28, 21, 28, 27, 1, (90, 90, 95), "tailrotor")
        p.ell(50, 20, 2.5, 2.5, (240, 200, 170), "pilot")
        p.ell(50, 18.5, 2.6, 1.2, (240, 170, 60), "goggles")
        p.line(48, 18, 48, 13, 1, (90, 90, 95), "mast")
        p.line(36, 12, 60, 12, 1, (210, 210, 215), "rotor")
        p.line(56, 29, 62, 30, 1, IRON_D, "gun")
        p.line(44, 31, 42, 35, 1, IRON_D, "skidL"); p.line(52, 31, 54, 35, 1, IRON_D, "skidR")
        p.line(40, 35, 56, 35, 1, IRON_D, "skid")
    return paint_layers((W, H), f)


# ======================================================================= ships
def hull(p, x0, x1, wl, depth, col, part, bow=6):
    """A ship's hull seen from the side, bow to the right, waterline at wl."""
    p.poly([(x0, wl - depth), (x1 - bow, wl - depth), (x1, wl - depth - 2), (x1 - 3, wl), (x0 + 3, wl)], col, part)
    p.line(x0 + 1, wl - depth + 1, x1 - bow, wl - depth + 1, 1, shade(col, 1.2), part + "rail")


def water(p, x0, x1, wl):
    p.ell((x0 + x1) / 2, wl + 1, (x1 - x0) / 2 + 2, 2, (180, 210, 230), "wake")


def ironclad(a):
    def f(p):
        water(p, 32, 63, 46)
        hull(p, 32, 63, 46, 9, (90, 92, 100), "hull")
        p.poly([(38, 37), (56, 37), (54, 31), (40, 31)], IRON, "casemate")
        p.line(46, 31, 46, 18, 3, (60, 60, 66), "stack")
        p.ell(36, 40, 4, 4, WOOD_D, "paddle")
        p.line(56, 34, 62, 33, 2, IRON_D, "gun")
        p.line(42, 31, 42, 24, 1, WOOD_D, "mast"); p.poly([(42, 24), (37, 26), (42, 28)], (225, 225, 225), "flag", layer=2)
    def lit(p):
        p.ell(46, 15, 2.5, 2, (170, 170, 170), "smoke"); p.ell(44, 11, 3, 2.2, (195, 195, 195), "smoke2")
    return paint_layers((64, 56), f, ((lit, (200, 200, 200)),))


def destroyer(a):
    def f(p):
        water(p, 30, 64, 46)
        hull(p, 30, 64, 46, 7, (110, 115, 125), "hull", bow=8)
        p.poly([(34, 39), (52, 39), (52, 34), (36, 34)], (225, 225, 225), "deck", layer=2)
        for x in (40, 46):
            p.line(x, 34, x, 24, 2, (60, 60, 66), "stack%d" % x)
        p.ell(57, 37, 3, 2, IRON_D, "turret"); p.line(58, 36, 63, 35, 1, IRON_D, "gun")
        p.line(52, 34, 52, 22, 1, IRON_D, "mast")
    def lit(p):
        p.ell(40, 21, 2, 1.6, (180, 180, 180), "smoke")
    return paint_layers((64, 56), f, ((lit, (200, 200, 200)),))


def dreadnought(a):
    def f(p):
        water(p, 30, 64, 48)
        hull(p, 30, 64, 48, 11, (80, 82, 92), "hull", bow=7)
        p.poly([(36, 37), (58, 37), (56, 30), (38, 30)], IRON, "super")
        p.poly([(40, 30), (54, 30), (52, 25), (42, 25)], (225, 225, 225), "bridge", layer=2)
        for x in (42, 48):
            p.line(x, 25, x, 13, 3, (55, 55, 62), "stack%d" % x)
        for x, y in ((34, 36), (59, 35)):
            p.ell(x, y, 3.5, 2.5, IRON_D, "tur%d" % x)
            p.line(x + 1, y - 1, x + 7 if x > 40 else x - 5, y - 2, 2, IRON_D, "gun%d" % x)
        p.line(46, 30, 46, 6, 1, IRON_D, "mast")
    def lit(p):
        p.ell(42, 10, 2.5, 2, (170, 170, 170), "smoke"); p.ell(48, 9, 2.5, 2, (190, 190, 190), "smoke2")
    return paint_layers((64, 56), f, ((lit, (200, 200, 200)),))


def airship_tender(a):
    """An airship (like the Alliance and Horde gunships) carrying gyrocopters."""
    def f(p):
        p.ell(46, 16, 16, 7, (225, 225, 225), "envelope", layer=2)
        p.line(32, 16, 61, 16, 1, (200, 200, 200), "seam")
        p.poly([(29, 12), (33, 16), (29, 20)], (150, 150, 150), "fin")
        for x in (38, 54):
            p.line(x, 22, x, 28, 1, WOOD_D, "rope%d" % x)
        hull(p, 33, 62, 36, 7, WOOD, "gondola", bow=5)
        p.ell(32, 31, 1.5, 4, (190, 190, 195), "prop")
        p.poly([(44, 29), (52, 29), (52, 27), (44, 27)], BRASS, "gyro")
        p.line(43, 26, 53, 26, 1, (200, 200, 205), "gyrorotor")
    return paint_layers((64, 56), f)


def juggernaught(a):
    """The orcish juggernaught: a spiked, skull-prowed battleship with a catapult."""
    def f(p):
        water(p, 30, 64, 48)
        hull(p, 30, 64, 48, 11, (95, 60, 40), "hull", bow=4)
        for x in range(34, 60, 5):
            p.line(x, 37, x + 1, 33, 1, (215, 210, 200), "spike%d" % x)
        p.ell(62, 40, 3, 3, (230, 225, 210), "skull")
        p.dot(63, 40, (30, 25, 25), "skull")
        p.line(44, 37, 44, 10, 2, WOOD_D, "mast")
        p.poly([(44, 12), (56, 15), (55, 27), (44, 28)], (225, 225, 225), "sail", layer=2)
        p.line(36, 36, 32, 26, 2, WOOD, "catapult")
        p.ell(31, 25, 2, 1.6, (60, 55, 50), "shot")
    return paint_layers((64, 56), f)


def gnomish_submarine(a):
    def f(p):
        p.ell(48, 38, 15, 5, BRASS, "hull")
        p.ell(48, 40, 15, 3, (60, 90, 120), "sea")              # lower half under water
        p.poly([(44, 33), (52, 33), (51, 27), (45, 27)], (225, 225, 225), "tower", layer=2)
        p.line(50, 27, 50, 22, 1, IRON_D, "scope"); p.line(50, 22, 53, 22, 1, IRON_D, "scope")
        for x in (40, 56):
            p.ell(x, 36, 1.3, 1.3, (150, 220, 230), "port%d" % x)
        p.line(33, 38, 31, 34, 1, IRON_D, "screw")
    return paint_layers((64, 56), f)


def giant_turtle(a):
    """A giant sea turtle bred for war: a high armoured shell riding above the waves,
    plated with iron, carrying a spiked fighting platform and a ram on its brow."""
    def f(p):
        p.ell(38, 44, 19, 4, (120, 175, 195), "wave")
        p.line(23, 42, 17, 46, 3, (95, 130, 80), "flipper")
        p.line(50, 43, 55, 47, 3, (95, 130, 80), "flipper2")
        p.ell(38, 37, 16, 9, (70, 110, 60), "shell")
        p.ell(38, 41, 16, 3.5, (150, 140, 95), "plastron")
        for x, y in ((30, 35), (38, 32), (46, 35), (34, 39), (42, 39)):
            p.ell(x, y, 3, 2.2, (100, 140, 80), "plate%d%d" % (x, y))
        p.line(23, 38, 53, 38, 1, IRON_D, "band")
        p.ell(57, 37, 4.5, 3.5, (110, 140, 90), "head")
        p.dot(58, 35, (240, 200, 60), "eye")
        p.poly([(60, 34), (63, 33), (61, 37)], IRON, "ram")
        p.poly([(29, 30), (47, 30), (45, 24), (31, 24)], (225, 225, 225), "platform", layer=2)
        for x in (30, 34, 38, 42, 46):
            p.line(x, 24, x, 21, 1, (60, 55, 55), "spike%d" % x)
        p.line(38, 24, 38, 14, 1, WOOD_D, "pole")
        p.poly([(38, 14), (44, 15), (38, 18)], (225, 225, 225), "flag", layer=1)
    return paint_layers((64, 56), f)


# ======================================================================= Titan vessel parts
def cart(p, x0, x1, y):
    p.poly([(x0, y), (x1, y), (x1 - 1, y - 3), (x0 + 1, y - 3)], WOOD, "cart")
    for x in (x0 + 5, x1 - 5):
        p.ell(x, y + 2, 3.5, 3.5, (70, 55, 40), "wheel%d" % x)
        p.ell(x, y + 2, 1, 1, BRASS, "hub%d" % x)


TITAN = (175, 170, 160)


def ss_part(kind):
    def make(a):
        def f(p):
            cart(p, 3, 38, 46)
            if kind == "thruster":
                p.poly([(8, 43), (32, 43), (28, 24), (12, 24)], TITAN, "cone")
                p.ell(20, 24, 8, 3, (140, 135, 125), "rim")
            elif kind == "crystal":
                p.poly([(10, 43), (30, 43), (27, 38), (13, 38)], BRASS, "cradle")
                p.poly([(20, 10), (26, 24), (22, 38), (18, 38), (14, 24)], (130, 190, 255), "crystal")
            elif kind == "engine":
                p.poly([(7, 43), (33, 43), (33, 26), (7, 26)], TITAN, "drum")
                p.ell(20, 26, 13, 3, (150, 145, 135), "top")
                p.ell(20, 34, 5, 5, BRASS, "gear")
            else:                                            # stasis vault
                p.poly([(9, 43), (31, 43), (29, 20), (11, 20)], TITAN, "vault")
                p.ell(20, 20, 9, 3, (150, 145, 135), "lid")
            p.poly([(5, 46), (36, 46), (36, 44), (5, 44)], (225, 225, 225), "banner", layer=2)
        def lit(p):
            if kind == "thruster":
                p.ell(20, 45, 5, 1.5, ARC, "jet")
                for y in (30, 36): p.line(14, y, 26, y, 1, ARC, "rune%d" % y)
            elif kind == "crystal":
                p.line(20, 14, 18, 30, 1, (230, 245, 255), "shine")
            elif kind == "engine":
                for y in (29, 39): p.line(10, y, 30, y, 1, ARC, "rune%d" % y)
            else:
                p.poly([(16, 26), (24, 26), (23, 38), (17, 38)], (150, 230, 255), "window")
        return paint_layers((78, 65), f, ((lit, ARC),))
    return make


# ======================================================================= registry
INFANTRY = {   # Unciv source name -> (base soldier, gear); race/Human looks apply to the soldier first
    "Great War Infantry": ("Rifleman", fusilier), "Infantry": ("Musketman", shock_trooper),
    "Machine Gun": ("Musketman", grenadier), "Gatling Gun": ("Rifleman", mountaineer),
    "Marine": ("Rifleman", kul_tiran_marine), "Paratrooper": ("Musketman", skyguard),
    "Anti-Tank Gun": ("Musketman", siegebreaker),
}
MACHINES = {   # drawn once; these replace the stock art for every civ
    "Landship": war_golem, "Tank": siege_engine, "Modern Armor": mechano_tank,
    "Mechanized Infantry": mechagnomes, "Giant Death Robot": iron_colossus,
    "Rocket Artillery": demolisher, "Mobile SAM": flak_wagon, "Anti-Aircraft Gun": flak_cannon,
    "Helicopter Gunship": flying_machine, "Ironclad": ironclad, "Destroyer": destroyer,
    "Battleship": dreadnought, "Carrier": airship_tender, "Missile Cruiser": juggernaught,
    "Nuclear Submarine": giant_turtle,
    "SS Booster": ss_part("thruster"), "SS Cockpit": ss_part("crystal"),
    "SS Engine": ss_part("engine"), "SS Stasis Chamber": ss_part("vault"),
}
SOURCES = {**INFANTRY, **MACHINES}
_cache = {}


def source_layers(a, name, dress=None):
    """Layers for an Unciv unit sprite, with our replacement where we have one.
    For late infantry, `dress` (race or Human re-styling) is applied to the base
    soldier before the new gear is added, so faces, beards and tusks stay visible."""
    if name in INFANTRY:
        base, gear_fn = INFANTRY[name]
        ls = layers(a, base)
        if dress:
            ls = dress(ls, base)
        return gear_fn([l.copy() for l in ls])
    if name in MACHINES:
        if name not in _cache:
            _cache[name] = MACHINES[name](a)
        return [l.copy() for l in _cache[name]]
    return layers(a, name)


def is_dressed(name):
    return name in INFANTRY
