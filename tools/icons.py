"""Original flat-silhouette icons for UncivWarcraft, drawn with Pillow.

Unciv tints these itself: unit, nation and religion icons are white,
building icons are black. Shapes are drawn on a 100x100 grid at 8x and
downsampled, which gives smooth anti-aliased edges.
"""
import math, os
from PIL import Image, ImageDraw

SS = 8


class Icon:
    def __init__(self):
        self.im = Image.new("L", (100 * SS, 100 * SS), 0)
        self.d = ImageDraw.Draw(self.im)

    # --- primitives (v=255 draws, v=0 cuts) --------------------------------
    def _p(self, pts):
        return [(x * SS, y * SS) for x, y in pts]

    def poly(self, pts, v=255):
        self.d.polygon(self._p(pts), fill=v)

    def circle(self, cx, cy, r, v=255):
        self.d.ellipse([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS], fill=v)

    def ellipse(self, cx, cy, rx, ry, v=255):
        self.d.ellipse([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS], fill=v)

    def ring(self, cx, cy, r, w, v=255):
        self.d.ellipse([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS],
                       outline=v, width=int(w * SS))

    def arc(self, cx, cy, r, a0, a1, w, v=255):
        self.d.arc([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS], a0, a1,
                   fill=v, width=int(w * SS))

    def rect(self, x0, y0, x1, y1, v=255):
        x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1))
        self.d.rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], fill=v)

    def line(self, pts, w, v=255, caps=True):
        self.d.line(self._p(pts), fill=v, width=int(w * SS), joint="curve")
        if caps:
            for x, y in (pts[0], pts[-1]):
                self.circle(x, y, w / 2, v)

    def bline(self, p0, p1, p2, p3, w, v=255):
        """Thick cubic Bezier stroke."""
        self.line(bez(p0, p1, p2, p3), w, v)

    def taper(self, p0, p1, p2, p3, w0, w1, v=255):
        """Cubic Bezier stroke whose width changes from w0 to w1 (horns, tusks, flames)."""
        pts = bez(p0, p1, p2, p3, 40)
        left, right = [], []
        for i, (x, y) in enumerate(pts):
            a = pts[min(i + 1, len(pts) - 1)]
            b = pts[max(i - 1, 0)]
            dx, dy = a[0] - b[0], a[1] - b[1]
            n = math.hypot(dx, dy) or 1
            nx, ny = -dy / n, dx / n
            w = (w0 + (w1 - w0) * i / (len(pts) - 1)) / 2
            left.append((x + nx * w, y + ny * w))
            right.append((x - nx * w, y - ny * w))
        self.poly(left + right[::-1], v)

    def star(self, cx, cy, r_out, r_in, n, rot=-90, v=255):
        pts = []
        for i in range(2 * n):
            r = r_out if i % 2 == 0 else r_in
            a = math.radians(rot + i * 180 / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        self.poly(pts, v)

    def rays(self, cx, cy, r0, r1, n, w, rot=0, v=255):
        for i in range(n):
            a = math.radians(rot + i * 360 / n)
            ca, sa = math.cos(a), math.sin(a)
            px, py = -sa * w / 2, ca * w / 2
            self.poly([(cx + ca * r0 + px, cy + sa * r0 + py), (cx + ca * r1, cy + sa * r1),
                       (cx + ca * r0 - px, cy + sa * r0 - py)], v)

    def save(self, path, color=(255, 255, 255)):
        mask = self.im.resize((100, 100), Image.LANCZOS)
        out = Image.new("RGBA", (100, 100), color + (0,))
        out.putalpha(mask)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        out.save(path)


def bez(p0, p1, p2, p3, n=30):
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        pts.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                    u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
    return pts


def scaled(pts, k, cx=50, cy=50):
    return [(cx + (x - cx) * k, cy + (y - cy) * k) for x, y in pts]


# ============================================================ units (white)
def footman():
    i = Icon()
    # sword behind the shield, hilt bottom-left, tip top-right
    i.poly([(30, 74), (84, 15), (91, 6), (88, 18), (34, 78)])
    i.line([(14, 92), (27, 78)], 5)
    i.line([(19, 70), (35, 85)], 6)
    i.circle(12, 94, 4.5)
    shield = [(20, 28), (32, 21), (50, 19), (68, 21), (80, 28), (78, 50), (68, 70), (50, 88),
              (32, 70), (22, 50)]
    i.poly(scaled(shield, 1.12, 50, 52), 0)
    i.poly(shield)
    i.poly([(28, 40), (50, 56), (72, 40), (72, 50), (50, 66), (28, 50)], 0)
    i.circle(50, 33, 5, 0)
    return i


def paladin():
    i = Icon()
    i.rays(50, 27, 27, 44, 10, 9, rot=-90)
    i.ring(50, 27, 25, 4)
    i.circle(50, 27, 21, 0)
    i.rect(17, 11, 83, 44, 0)
    i.rect(20, 14, 80, 41)               # hammer head
    i.rect(24, 19, 76, 22, 0)            # engraved bands
    i.rect(24, 33, 76, 36, 0)
    i.rect(44.5, 38, 55.5, 95, 0)
    i.rect(46.5, 38, 53.5, 94)           # haft
    i.rect(43, 78, 57, 82)               # grip wrap
    return i


def mage():
    i = Icon()
    i.line([(18, 94), (60, 38)], 6)
    i.ring(70, 26, 20, 3)
    i.circle(70, 26, 13)
    i.circle(66, 22, 4, 0)               # highlight
    i.taper((58, 40), (52, 30), (54, 18), (62, 12), 6, 1)  # claw cradling the orb
    i.taper((60, 42), (72, 46), (84, 40), (88, 32), 6, 1)
    i.star(26, 26, 13, 3.5, 4)
    i.star(86, 66, 9, 2.5, 4)
    i.star(40, 56, 6, 1.8, 4)
    return i



def priest():
    i = Icon()
    i.rays(50, 30, 20, 34, 12, 7, rot=-90)          # radiance of the Light
    i.circle(50, 30, 17)
    i.circle(50, 30, 12, 0)
    i.circle(50, 30, 7)
    # an open holy book
    i.poly([(14, 62), (48, 70), (48, 94), (14, 86)])
    i.poly([(86, 62), (52, 70), (52, 94), (86, 86)])
    i.line([(20, 70), (42, 75)], 2.5, 0)
    i.line([(20, 77), (42, 82)], 2.5, 0)
    i.line([(80, 70), (58, 75)], 2.5, 0)
    i.line([(80, 77), (58, 82)], 2.5, 0)
    return i


def archmage():
    i = Icon()
    i.poly([(22, 62), (56, 6), (60, 22), (78, 62)])  # tall pointed hat
    i.ellipse(50, 66, 42, 9)                          # brim
    i.star(46, 40, 8, 2.5, 5, v=0)
    i.circle(76, 84, 10)                              # arcane orb
    i.ring(76, 84, 15, 2.5)
    i.star(22, 86, 8, 2.2, 4)
    return i


def steam_tank():
    i = Icon()
    i.rect(10, 44, 80, 70)                            # hull
    i.poly([(10, 44), (22, 32), (68, 32), (80, 44)])
    i.rect(30, 20, 56, 34)                            # cab
    i.rect(14, 8, 22, 34)                             # smokestack
    i.circle(18, 6, 5)
    i.line([(78, 46), (96, 40)], 7)                   # cannon
    for cx in (22, 45, 68):                            # wheels
        i.circle(cx, 80, 12)
        i.circle(cx, 80, 5, 0)
    for x in range(18, 76, 10):
        i.circle(x, 55, 2, 0)                          # rivets
    return i


def man_o_war():
    i = Icon()
    i.poly([(8, 70), (92, 70), (80, 90), (20, 90)])   # hull
    i.rect(47, 8, 51, 72)                             # masts
    i.rect(23, 20, 27, 72)
    i.rect(71, 20, 75, 72)
    for x0, top in ((29, 10), (53, 10)):              # sails
        i.poly([(x0, top + 4), (x0 + 16, top), (x0 + 18, top + 22), (x0 + 2, top + 26)])
        i.poly([(x0, top + 32), (x0 + 16, top + 28), (x0 + 18, top + 52), (x0 + 2, top + 56)])
    i.poly([(5, 30), (21, 26), (21, 62), (5, 66)])
    i.rect(10, 76, 90, 79, 0)                         # gun-port line
    for x in range(18, 86, 12):
        i.rect(x, 74, x + 5, 80)
    return i


def royal_barracks():
    i = Icon()
    i.line([(16, 16), (84, 84)], 7)                    # crossed swords
    i.line([(84, 16), (16, 84)], 7)
    i.line([(22, 34), (34, 22)], 5)
    i.line([(66, 22), (78, 34)], 5)
    shield = [(28, 34), (72, 34), (72, 60), (50, 84), (28, 60)]
    i.poly(scaled(shield, 1.18, 50, 56), 0)
    i.poly(shield)
    i.rect(10, 92, 90, 96)
    return i


def lumber_mill():
    i = Icon()
    i.circle(64, 38, 30)                              # saw blade
    i.rays(64, 38, 28, 36, 16, 7)
    i.circle(64, 38, 8, 0)
    i.circle(64, 38, 4)
    for y in (70, 84):                                # stacked logs
        i.rect(6, y - 6, 70, y + 6)
        i.circle(70, y, 6)
        i.circle(70, y, 3, 0)
    return i


def castle():
    i = Icon()
    i.rect(14, 40, 86, 94)
    for x in (10, 70):                                # towers
        i.rect(x, 22, x + 20, 94)
        for k in range(3):
            i.rect(x + k * 7, 15, x + k * 7 + 5, 23)
    for k in range(4):                                # battlements of the wall
        i.rect(32 + k * 10, 33, 38 + k * 10, 41)
    i.rect(42, 64, 58, 94, 0)                         # gate
    i.circle(50, 64, 8, 0)
    i.rect(16, 34, 22, 44, 0)
    i.rect(78, 34, 84, 44, 0)
    return i


def altar_of_kings():
    i = Icon()
    i.poly([(28, 26), (36, 8), (44, 22), (50, 4), (56, 22), (64, 8), (72, 26)])  # crown
    i.rect(28, 26, 72, 34)
    i.rect(20, 46, 80, 56)                            # altar top
    i.rect(30, 56, 70, 84)
    i.rect(14, 84, 86, 94)
    i.rect(44, 62, 56, 78, 0)
    return i


# ============================================================ buildings (black)
def chapel_of_the_light():
    i = Icon()
    i.rays(50, 13, 9, 15, 8, 5, rot=-90)
    i.circle(50, 13, 7)
    i.rect(45, 21, 55, 34)
    i.poly([(16, 56), (50, 30), (84, 56)])
    i.rect(22, 54, 78, 92)
    i.circle(50, 46, 5, 0)
    i.rect(43, 74, 57, 92, 0)
    i.circle(50, 74, 7, 0)
    i.rect(28, 64, 36, 76, 0)
    i.rect(64, 64, 72, 76, 0)
    i.rect(10, 90, 90, 95)
    return i


# ============================================================ nations (white)
def n_humans():
    i = Icon()
    shield = [(18, 12), (82, 12), (82, 48)] + bez((82, 48), (82, 72), (64, 84), (50, 94))[1:] \
        + bez((50, 94), (36, 84), (18, 72), (18, 48))[1:]
    i.poly(shield)
    crown = [(30, 64), (30, 36), (40, 48), (50, 30), (60, 48), (70, 36), (70, 64)]
    i.poly(crown, 0)
    i.circle(30, 33, 3.5, 0); i.circle(50, 27, 3.5, 0); i.circle(70, 33, 3.5, 0)
    i.rect(30, 68, 70, 73, 0)
    return i


def _axe(i, base, top, flip):
    i.line([base, top], 6)
    dx, dy = top[0] - base[0], top[1] - base[1]
    n = math.hypot(dx, dy); ux, uy = dx / n, dy / n
    px, py = (-uy, ux) if flip else (uy, -ux)
    a = (top[0] - ux * 4, top[1] - uy * 4)
    b = (top[0] - ux * 26, top[1] - uy * 26)
    b = (top[0] - ux * 30, top[1] - uy * 30)
    tip1 = (a[0] + px * 30 + ux * 10, a[1] + py * 30 + uy * 10)
    tip2 = (b[0] + px * 30 - ux * 10, b[1] + py * 30 - uy * 10)
    mid = ((tip1[0] + tip2[0]) / 2 + px * 2, (tip1[1] + tip2[1]) / 2 + py * 2)
    edge = bez(tip1, (mid[0] + px * 6 + ux * 6, mid[1] + py * 6 + uy * 6),
               (mid[0] + px * 6 - ux * 6, mid[1] + py * 6 - uy * 6), tip2)
    i.poly([a, (a[0] + px * 10, a[1] + py * 10)] + edge + [(b[0] + px * 10, b[1] + py * 10), b])


def n_orcs():
    i = Icon()
    _axe(i, (14, 92), (74, 12), True)
    _axe(i, (86, 92), (26, 12), False)
    return i


def n_night_elves():
    i = Icon()
    for k in range(3):
        a0 = -90 + k * 120
        outer = [(50 + 44 * math.cos(math.radians(a)), 50 + 44 * math.sin(math.radians(a)))
                 for a in range(a0, a0 + 81, 4)]
        inner = [(50 + 25 * math.cos(math.radians(a)), 50 + 25 * math.sin(math.radians(a)))
                 for a in range(a0 + 62, a0 - 1, -4)]
        i.poly(outer + inner)
    i.ring(50, 50, 22, 6)
    i.circle(50, 50, 9)
    return i


def n_dwarves():
    i = Icon()
    i.poly([(6, 58), (86, 58), (86, 66), (70, 66), (62, 74), (62, 82), (74, 92), (26, 92),
            (38, 82), (38, 74), (30, 66), (22, 66)])
    # hammer, angled above the anvil
    i.line([(26, 52), (62, 18)], 8)
    c, s = math.cos(math.radians(45)), math.sin(math.radians(45))
    hx, hy = 66, 14
    w, h = 20, 40
    pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    i.poly([(hx + x * c - y * s, hy + x * s + y * c) for x, y in pts])
    return i


def n_gnomes():
    i = Icon()
    for k in range(10):
        a = math.radians(k * 36)
        ca, sa = math.cos(a), math.sin(a)
        pts = [(-6, 0), (6, 0), (4.5, 12), (-4.5, 12)]
        i.poly([(50 + ca * (32 + y) - sa * x, 50 + sa * (32 + y) + ca * x) for x, y in pts])
    i.circle(50, 50, 34)
    i.circle(50, 50, 14, 0)
    for k in range(5):
        a = math.radians(k * 72 - 90)
        i.circle(50 + 24 * math.cos(a), 50 + 24 * math.sin(a), 4, 0)
    return i


def n_tauren():
    i = Icon()
    i.taper((36, 42), (20, 40), (8, 28), (10, 8), 12, 2)
    i.taper((64, 42), (80, 40), (92, 28), (90, 8), 12, 2)
    i.poly([(30, 34), (70, 34), (66, 64), (58, 90), (42, 90), (34, 64)])
    i.poly([(30, 36), (16, 44), (30, 50)])
    i.poly([(70, 36), (84, 44), (70, 50)])
    i.poly([(38, 50), (47, 54), (40, 57)], 0)
    i.poly([(62, 50), (53, 54), (60, 57)], 0)
    i.ellipse(45, 82, 3, 4, 0); i.ellipse(55, 82, 3, 4, 0)
    i.ring(50, 72, 6, 2.5, 0)
    return i


def n_trolls():
    i = Icon()
    i.ellipse(50, 46, 27, 38)
    i.poly([(31, 36), (46, 42), (44, 48), (30, 42)], 0)
    i.poly([(69, 36), (54, 42), (56, 48), (70, 42)], 0)
    i.poly([(47, 54), (53, 54), (50, 64)], 0)
    i.rect(38, 70, 62, 74, 0)
    i.taper((36, 80), (30, 92), (14, 88), (10, 66), 9, 1)
    i.taper((64, 80), (70, 92), (86, 88), (90, 66), 9, 1)
    i.poly([(28, 14), (34, 2), (40, 12)]); i.poly([(60, 12), (66, 2), (72, 14)])
    return i


def n_blood_elves():
    i = Icon()
    for sgn in (-1, 1):
        def m(x, y): return (50 + sgn * (x - 50), y)
        wing = bez(m(50, 52), m(40, 30), m(22, 14), m(4, 8))[:-1] + \
            bez(m(4, 8), m(14, 26), m(22, 34), m(16, 42))[:-1] + \
            bez(m(16, 42), m(26, 44), m(32, 46), m(22, 56))[:-1] + \
            bez(m(22, 56), m(34, 58), m(40, 62), m(46, 66))
        i.poly(wing)
    i.ellipse(50, 50, 9, 20)
    i.circle(50, 26, 7)
    i.poly([(50, 18), (58, 24), (52, 26)])
    i.taper((50, 66), (44, 78), (38, 86), (34, 96), 10, 1)
    i.taper((50, 66), (50, 78), (50, 86), (50, 97), 10, 1)
    i.taper((50, 66), (56, 78), (62, 86), (66, 96), 10, 1)
    return i


def n_high_elves():
    i = Icon()
    i.star(50, 50, 46, 9, 4, rot=-90)
    i.star(50, 50, 30, 9, 4, rot=-45)
    i.circle(50, 50, 15, 0)
    i.circle(50, 50, 10)
    return i


def n_pandaren():
    i = Icon()
    for x0, h, w in ((36, 6, 9), (60, 16, 8)):
        top = h
        i.rect(x0 - w / 2, top, x0 + w / 2, 94)
        y = top + 16
        while y < 92:
            i.rect(x0 - w / 2 - 1.5, y, x0 + w / 2 + 1.5, y + 3)
            i.rect(x0 - w / 2, y - 1.2, x0 + w / 2, y, 0)
            y += 18
    def leaf(base, tip, bulge):
        mx, my = (base[0] + tip[0]) / 2, (base[1] + tip[1]) / 2
        dx, dy = tip[0] - base[0], tip[1] - base[1]
        n = math.hypot(dx, dy); px, py = -dy / n * bulge, dx / n * bulge
        i.poly(bez(base, (mx + px, my + py), (mx + px, my + py), tip) +
               bez(tip, (mx - px, my - py), (mx - px, my - py), base)[1:])
    leaf((40, 36), (14, 22), 6); leaf((40, 44), (16, 52), 5)
    leaf((64, 30), (90, 14), 6); leaf((64, 52), (90, 56), 5); leaf((64, 40), (86, 34), 5)
    return i


def n_forsaken():
    i = Icon()
    i.ellipse(50, 42, 34, 32)
    i.rect(30, 58, 70, 86)
    i.rect(26, 52, 74, 66)
    i.ellipse(37, 44, 9, 10, 0); i.ellipse(63, 44, 9, 10, 0)
    i.poly([(50, 54), (45, 64), (55, 64)], 0)
    for x in (39, 47, 55):
        i.rect(x, 74, x + 6, 86, 0)
    i.rect(30, 74, 70, 76, 0)
    return i


def n_draenei():
    i = Icon()
    def crystal(cx, top, bottom, w, v=255):
        mid = top + (bottom - top) * 0.35
        i.poly([(cx, top), (cx + w, mid), (cx + w * 0.7, bottom), (cx - w * 0.7, bottom),
                (cx - w, mid)], v)
    crystal(28, 30, 92, 15); crystal(72, 30, 92, 15)
    crystal(50, 6, 94, 20, 0)
    crystal(50, 10, 92, 17)
    i.line([(50, 12), (50, 88)], 2.2, 0, caps=False)
    i.line([(34, 41), (50, 50), (66, 41)], 2.2, 0, caps=False)
    return i


def n_goblins():
    i = Icon()
    for k in range(4):
        y = 84 - k * 10
        i.ellipse(36, y, 26, 8)
        i.arc(36, y, 26, 0, 180, 1.6, 0) if k < 3 else None
    i.circle(70, 52, 26, 0)
    i.circle(70, 52, 23)
    i.ring(70, 52, 17, 3, 0)
    i.star(70, 52, 10, 4, 4, v=0)
    return i


def n_worgen():
    i = Icon()
    i.circle(50, 50, 42)
    for k, dx in enumerate((-18, 0, 18)):
        i.taper((30 + dx + 10, 12 + abs(dx) * 0.3), (34 + dx + 8, 40), (28 + dx + 6, 62),
                (22 + dx + 4, 88 - abs(dx) * 0.3), 1, 9, 0)
    return i


def n_scourge():
    """The Helm of Domination: a horned crown over a dark visor."""
    i = Icon()
    i.poly([(22, 40), (50, 28), (78, 40), (74, 84), (50, 94), (26, 84)])            # helm
    for x, h in ((24, 6), (36, 14), (50, 2), (64, 14), (76, 6)):                       # crown spikes
        i.poly([(x - 6, 40 - (x == 50) * 4), (x + 6, 40 - (x == 50) * 4), (x, h)])
    i.poly([(32, 54), (68, 54), (62, 64), (38, 64)], 0)                               # visor
    i.rect(48, 64, 52, 86, 0)
    return i


# ============================================================ religions (white)
def r_holy_light():
    i = Icon()
    i.rays(50, 50, 22, 46, 12, 8)
    i.rays(50, 50, 22, 36, 12, 6, rot=15)
    i.circle(50, 50, 20)
    return i


def r_elune():
    i = Icon()
    i.circle(46, 52, 38)
    i.circle(62, 44, 32, 0)
    i.star(78, 22, 10, 2.5, 4)
    i.star(86, 48, 6, 1.6, 4)
    i.star(70, 72, 7, 2, 4)
    return i


def r_earth_mother():
    i = Icon()
    i.circle(50, 150, 82)                      # the curve of the earth
    i.rect(0, 92, 100, 100, 0)
    i.rays(30, 38, 15, 24, 10, 6)              # An'she, the sun
    i.circle(30, 38, 13)
    i.circle(72, 38, 15)                       # Mu'sha, the moon
    i.circle(79, 33, 13, 0)
    i.line([(14, 60), (86, 60)], 0.01, 0, caps=False)
    return i


def r_shamanism():
    i = Icon()
    i.ring(50, 50, 32, 5)
    for cx, cy in ((50, 14), (86, 50), (50, 86), (14, 50)):
        i.circle(cx, cy, 13, 0)
        i.circle(cx, cy, 10)
    i.circle(50, 50, 9)
    return i


def r_loa():
    i = Icon()
    for x in (26, 38, 50, 62, 74):
        i.poly([(x - 6, 26), (x, 4 + abs(x - 50) * 0.3), (x + 6, 26)])
    i.poly([(24, 24), (76, 24), (72, 84), (60, 96), (40, 96), (28, 84)])
    i.circle(39, 46, 9, 0); i.circle(61, 46, 9, 0)
    i.circle(39, 46, 4); i.circle(61, 46, 4)
    i.poly([(50, 52), (45, 66), (55, 66)], 0)
    i.rect(36, 74, 64, 86, 0)
    for x in (41, 48, 55):
        i.rect(x, 74, x + 3, 86)
    return i


def r_cenarion():
    i = Icon()
    i.poly(bez((50, 92), (8, 72), (14, 24), (50, 6)) + bez((50, 6), (86, 24), (92, 72), (50, 92))[1:])
    i.line([(50, 92), (50, 14)], 3, 0, caps=False)
    for y, dx in ((34, 20), (50, 26), (66, 24)):
        i.line([(50, y + 10), (50 - dx, y)], 2.4, 0, caps=False)
        i.line([(50, y + 10), (50 + dx, y)], 2.4, 0, caps=False)
    i.line([(50, 92), (50, 98)], 4)
    return i


def r_celestials():
    i = Icon()
    i.circle(34, 56, 18); i.circle(56, 46, 22); i.circle(76, 60, 14)
    i.rect(16, 60, 90, 74)
    i.circle(16, 67, 7); i.circle(90, 67, 7)
    i.arc(56, 46, 12, 160, 380, 3.2, 0)
    i.arc(58, 49, 5, 0, 220, 3, 0)
    i.taper((20, 84), (40, 90), (60, 80), (88, 88), 3, 1)
    return i


def r_titans():
    i = Icon()
    i.poly([(18, 8), (82, 8), (90, 92), (10, 92)])
    i.poly([(50, 20), (70, 50), (50, 80), (30, 50)], 0)
    i.poly([(50, 31), (62, 50), (50, 69), (38, 50)])
    i.line([(50, 14), (50, 86)], 3, 0, caps=False)
    i.line([(26, 50), (74, 50)], 3, 0, caps=False)
    return i


def r_forgotten_shadow():
    i = Icon()
    i.poly(bez((6, 44), (28, 14), (72, 14), (94, 44)) + bez((94, 44), (72, 72), (28, 72), (6, 44))[1:])
    i.circle(50, 44, 17, 0)
    i.circle(50, 44, 12)
    i.ellipse(50, 44, 3.5, 9, 0)
    for x, l in ((30, 20), (50, 30), (70, 22)):
        i.taper((x, 60), (x - 1, 60 + l * 0.4), (x + 1, 60 + l * 0.7), (x, 60 + l), 8, 3)
        i.circle(x, 60 + l, 3.5)
    return i


def r_sunwell():
    i = Icon()
    i.rays(50, 50, 18, 48, 8, 5, rot=22.5)
    i.poly([(50, 4), (72, 50), (50, 96), (28, 50)])
    i.poly([(50, 18), (64, 50), (50, 82), (36, 50)], 0)
    i.poly([(50, 28), (58, 50), (50, 72), (42, 50)])
    return i


def n_dark_iron():
    """An anvil wreathed in flame."""
    i = Icon()
    i.poly([(10, 62), (88, 62), (88, 70), (72, 70), (64, 78), (64, 84), (76, 94), (24, 94),
            (36, 84), (36, 78), (28, 70), (18, 70)])
    for x, h, w in ((30, 40, 14), (50, 56, 18), (70, 42, 14)):
        i.taper((x, 58), (x - w * 0.6, 58 - h * 0.45), (x + w * 0.3, 58 - h * 0.75), (x + 2, 58 - h), w, 1)
    i.circle(50, 48, 6, 0)
    return i


def n_kul_tirans():
    """An anchor."""
    i = Icon()
    i.ring(50, 14, 9, 5)
    i.line([(50, 22), (50, 84)], 9, caps=False)
    i.line([(30, 32), (70, 32)], 8)
    i.arc(50, 58, 34, 20, 160, 9)
    i.poly([(10, 66), (24, 64), (16, 78)]); i.poly([(90, 66), (76, 64), (84, 78)])
    return i


def n_zandalari():
    """A stepped golden pyramid under a sun."""
    i = Icon()
    for k, (w, y) in enumerate(((84, 92), (66, 76), (48, 60), (30, 44))):
        i.rect(50 - w / 2, y - 14, 50 + w / 2, y)
    i.rect(44, 62, 56, 92, 0)
    i.rays(50, 16, 8, 16, 8, 3)
    i.circle(50, 16, 7)
    return i


UNIT_ICONS = {"Footman": footman, "Paladin": paladin, "Mage": mage, "Priest": priest,
              "Archmage": archmage, "Steam Tank": steam_tank, "Kul Tiran Man-o'-War": man_o_war}
BUILDING_ICONS = {"Chapel of the Light": chapel_of_the_light, "Royal Barracks": royal_barracks,
                  "Lumber Mill": lumber_mill, "Castle": castle, "Altar of Kings": altar_of_kings}
NATION_ICONS = {"Humans": n_humans, "Orcs": n_orcs, "Night Elves": n_night_elves,
                "Dwarves": n_dwarves, "Gnomes": n_gnomes, "Tauren": n_tauren, "Trolls": n_trolls,
                "Blood Elves": n_blood_elves, "High Elves": n_high_elves, "Pandaren": n_pandaren,
                "Forsaken": n_forsaken, "Draenei": n_draenei, "Goblins": n_goblins,
                "Worgen": n_worgen, "Scourge": n_scourge, "Dark Iron Dwarves": n_dark_iron,
                "Kul Tirans": n_kul_tirans, "Zandalari Trolls": n_zandalari}
RELIGION_ICONS = {"Holy Light": r_holy_light, "Elune": r_elune, "Earth Mother": r_earth_mother,
                  "Shamanism": r_shamanism, "Loa": r_loa, "Cenarion Circle": r_cenarion,
                  "August Celestials": r_celestials, "Titans": r_titans,
                  "Forgotten Shadow": r_forgotten_shadow, "Light of the Sunwell": r_sunwell}


def write_all(images_dir):
    for n, f in UNIT_ICONS.items():
        f().save(os.path.join(images_dir, "UnitIcons", n + ".png"))
    for n, f in BUILDING_ICONS.items():
        f().save(os.path.join(images_dir, "BuildingIcons", n + ".png"), (0, 0, 0))
    for n, f in NATION_ICONS.items():
        f().save(os.path.join(images_dir, "NationIcons", n + ".png"))
    for n, f in RELIGION_ICONS.items():
        f().save(os.path.join(images_dir, "ReligionIcons", n + ".png"))


def contact_sheet(images_dir, out):
    """Preview every icon the way the game shows them: tinted, inside a colored circle."""
    groups = [("UnitIcons", UNIT_ICONS, (40, 40, 40), (255, 255, 255)),
              ("BuildingIcons", BUILDING_ICONS, (230, 230, 230), (0, 0, 0)),
              ("NationIcons", NATION_ICONS, None, None),
              ("ReligionIcons", RELIGION_ICONS, (60, 60, 70), (255, 255, 255))]
    import wc_factions as F
    colors = {n["name"]: (tuple(n["outerColor"]), tuple(n["innerColor"])) for n in F.NATIONS}
    cells = [(g, n, bg, fg) for g, d, bg, fg in groups for n in d]
    cols = 8; cw = 130
    sheet = Image.new("RGB", (cols * cw, ((len(cells) + cols - 1) // cols) * 150), (245, 243, 238))
    dr = ImageDraw.Draw(sheet)
    for k, (g, n, bg, fg) in enumerate(cells):
        if g == "NationIcons":
            bg, fg = colors[n]
        x, y = (k % cols) * cw + 15, (k // cols) * 150 + 10
        circ = Image.new("L", (100 * 4, 100 * 4), 0)
        ImageDraw.Draw(circ).ellipse([0, 0, 399, 399], fill=255)
        sheet.paste(Image.new("RGB", (100, 100), bg), (x, y), circ.resize((100, 100), Image.LANCZOS))
        ic = Image.open(os.path.join(images_dir, g, n + ".png")).resize((70, 70), Image.LANCZOS)
        sheet.paste(Image.new("RGB", (70, 70), fg), (x + 15, y + 15), ic.split()[3])
        dr.text((x, y + 108), n[:20], fill=(30, 30, 30))
    sheet.save(out)
