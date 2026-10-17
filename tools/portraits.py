"""Leader portraits for the diplomacy screen (Images/LeaderIcons/<leader>.png).

Original painted busts, one per race: tight 3/4 close-ups on a dark backdrop with a
black frame, in the spirit of classic strategy-game portraits. They show each race's
broad traits (skin, ears, tusks, horns, hair), not any specific Blizzard character.
"""
import math, os
import numpy as np
from PIL import Image
from paint import Canvas, mix

W = H = 130
INK = (24, 16, 14)


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


ZOOM, PIVOT = 1.24, (62, 56)


class P:
    """Thin wrapper: draw on a portrait canvas. Coordinates are in a 130-px layout that is
    zoomed about PIVOT so the face fills the frame (the top of the head is cropped)."""
    def __init__(self, bg_in, bg_out, zoom=ZOOM):
        self.c = Canvas(W, H)
        self.c.fill_background(bg_in, bg_out)
        self.k = zoom

    def t(self, q):
        return (PIVOT[0] + (q[0] - PIVOT[0]) * self.k, PIVOT[1] + (q[1] - PIVOT[1]) * self.k)

    def poly(self, pts, smooth=3):
        """Closed shape, rounded off with Chaikin corner cutting so nothing looks faceted."""
        for _ in range(smooth):
            out = []
            n = len(pts)
            for i in range(n):
                (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
                out += [(0.75 * x0 + 0.25 * x1, 0.75 * y0 + 0.25 * y1), (0.25 * x0 + 0.75 * x1, 0.25 * y0 + 0.75 * y1)]
            pts = out
        return self.c.poly([self.t(q) for q in pts])

    def ell(self, x, y, rx, ry, rot=0):
        X, Y = self.t((x, y))
        return self.c.ellipse(X, Y, rx * self.k, ry * self.k, rot=rot)

    def cap(self, a, b, r1, r2=None):
        return self.c.capsule(self.t(a), self.t(b), r1 * self.k, None if r2 is None else r2 * self.k)

    def curve(self, pts, r1, r2=None):
        return self.c.curve([self.t(q) for q in pts], r1 * self.k, None if r2 is None else r2 * self.k)

    def paint(self, m, col, mat="skin", outline=0.5, **kw):
        if kw.get("bevel"):
            kw["bevel"] *= self.k
        self.c.paint(m, col, mat=mat, outline=outline * self.k, ink=INK, **kw)

    def wash(self, m, col, alpha=0.5, blur=2.0, clip=None):
        self.c.wash(m, col, alpha, blur * self.k, clip=clip)

    def glow(self, m, col, radius=3, strength=0.8):
        self.c.glow(m, col, radius=radius * self.k, strength=strength)

    def strands(self, clip, pts_list, col, r=0.55, alpha=0.55):
        for pts in pts_list:
            self.wash(self.curve(pts, r, r * 0.4), col, alpha, blur=0.3, clip=clip)

    def frame(self):
        """Black frame with a faint inner bevel, like the reference portraits."""
        out = self.c.finish(outer_ink=0)[0]
        px = np.asarray(out, np.float32).copy()
        b = 5
        px[:b, :, :3] = 8; px[-b:, :, :3] = 8; px[:, :b, :3] = 8; px[:, -b:, :3] = 8
        for k, v in ((b, 46), (b + 1, 22)):
            px[k, k:-k, :3] = v; px[-k - 1, k:-k, :3] = v
            px[k:-k, k, :3] = v; px[k:-k, -k - 1, :3] = v
        px[..., 3] = 255
        return Image.fromarray(px.astype(np.uint8), "RGBA")


# ------------------------------------------------------------------ shared face parts
def shoulders(p, col, mat="cloth", trim=None, trim_mat="gold", armor=False, fur=None):
    m = p.poly([(-30, 140), (-30, 100), (10, 90), (40, 88), (60, 94), (88, 88), (120, 92), (160, 104), (160, 140)], smooth=2)
    p.paint(m, col, mat="metal" if armor else mat, outline=0.6)
    if armor:
        p.paint(p.ell(14, 100, 28, 16), col, mat="metal", outline=0.6)
        p.paint(p.ell(112, 100, 28, 15), col, mat="metal", outline=0.6)
    if trim:
        p.paint(p.poly([(30, 90), (44, 90), (62, 104), (80, 90), (94, 90), (62, 116)], smooth=1), trim, mat=trim_mat, outline=0.5)
    if fur:
        p.paint(p.poly([(-20, 106), (6, 88), (28, 86), (42, 92), (36, 106), (14, 114), (-20, 118)]), fur, mat="fur", outline=0.5)
        p.paint(p.poly([(150, 106), (120, 88), (98, 86), (86, 92), (90, 106), (110, 114), (150, 118)]), fur, mat="fur", outline=0.5)


def neck(p, skin, cx, top, w=15):
    m = p.poly([(cx - w, top), (cx + w + 2, top), (cx + w + 8, 104), (cx - w - 6, 104)], smooth=1)
    p.paint(m, skin, outline=0.5)
    p.wash(p.poly([(cx - w - 4, top - 4), (cx + w + 6, top - 4), (cx + w, top + 14), (cx - w, top + 14)]), (0, 0, 0), 0.6, 3, clip=m)


def head_shape(p, cx, cy, rx, ry, jaw="square", chin=0.0):
    """Skull + jaw for a 3/4 view facing right."""
    skull = p.ell(cx, cy - 6, rx, ry * 0.86)
    jw = {"square": 6, "heavy": 0, "narrow": 12, "pointed": 14}[jaw]
    jaw_m = p.poly([(cx - rx + 1, cy - 4), (cx - rx + 4 + jw * 0.4, cy + ry * 0.45), (cx - 6 + jw * 0.3, cy + ry - 2),
                    (cx + 10 + chin, cy + ry + 1 - (3 if jaw == "pointed" else 0)), (cx + rx - 4 - jw * 0.4, cy + ry * 0.62),
                    (cx + rx, cy + 2)])
    return p.c.union(skull, jaw_m)


def face_light(p, face, cx, cy, rx, ry, skin, rim=None, warm=(255, 224, 196)):
    """Painted form: far side and under-jaw in shadow, forehead/cheekbone/nose lit, a
    coloured rim light on the far edge (the backdrop's colour bouncing back)."""
    dark = shade(skin, 0.38)
    p.wash(p.ell(cx - rx * 1.05, cy + 4, rx * 0.75, ry * 1.3), dark, 0.75, 7, clip=face)       # far side
    p.wash(p.ell(cx + rx * 0.35, cy - 4, rx * 0.5, ry * 0.7), warm, 0.18, 8, clip=face)        # key light on the near half
    p.wash(p.ell(cx + 2, cy + ry + 4, rx * 0.9, ry * 0.3), dark, 0.6, 5, clip=face)          # under the jaw
    p.wash(p.ell(cx + 8, cy - ry * 0.55, rx * 0.55, ry * 0.28), warm, 0.35, 6, clip=face)     # forehead
    p.wash(p.ell(cx + rx * 0.55, cy + 4, rx * 0.28, ry * 0.14), warm, 0.35, 3, clip=face)     # near cheekbone
    p.wash(p.ell(cx + rx * 0.45, cy + 19, rx * 0.3, ry * 0.2), dark, 0.4, 4, clip=face)       # hollow under the cheekbone
    p.wash(p.curve([(cx + 12, cy + 14), (cx + 8, cy + 24), (cx + 10, cy + 30)], 1.6), dark, 0.35, 2, clip=face)   # cheek fold
    p.wash(p.ell(cx + 12, cy + ry * 0.92, rx * 0.25, ry * 0.12), warm, 0.3, 3, clip=face)     # chin
    if rim:
        edge = p.c.subtract(face, p.ell(cx + 3, cy - 2, rx * 0.98, ry * 1.02))
        p.wash(edge, rim, 0.7, 1.5, clip=face)

def eye(p, x, y, size, col, glow=False, iris=None, lid=INK, socket=None, angle=-0.12, far=False):
    sx = size * (0.78 if far else 1.0)
    if socket:
        p.wash(p.ell(x, y - 0.5, sx * 2.1, size * 1.45), socket, 0.7, 2.8)
        p.wash(p.ell(x + sx * 0.3, y + size * 1.4, sx * 1.4, size * 0.4), socket, 0.35, 1.5)   # lower lid bag
    almond = p.ell(x, y, sx * 1.15, size * 0.55, rot=angle)
    if glow:
        p.glow(almond, col, radius=size * 0.9, strength=0.75)
        p.paint(almond, col, mat="glow", outline=0.4)
        p.paint(p.ell(x - sx * 0.2, y - size * 0.1, sx * 0.45, size * 0.22), (255, 255, 240), mat="glow", outline=0)
    else:
        p.paint(almond, (232, 226, 214), mat="flat", outline=0.4)
        p.paint(p.ell(x + sx * 0.15, y, size * 0.48, size * 0.5), iris or col, mat="flat", outline=0)
        p.paint(p.ell(x + sx * 0.15, y, size * 0.22, size * 0.24), (15, 10, 10), mat="flat", outline=0)
        p.paint(p.ell(x + sx * 0.0, y - size * 0.2, size * 0.13, size * 0.13), (255, 255, 255), mat="flat", outline=0)
    # lid crease, then the heavy upper lid
    p.wash(p.curve([(x - sx * 1.1, y - size * 0.7), (x, y - size * 1.25), (x + sx * 1.2, y - size * 0.8)], 0.6), shade(lid, 1.0), 0.35, 0.5)
    p.paint(p.curve([(x - sx * 1.2, y + 0.3), (x, y - size * 0.75), (x + sx * 1.25, y - size * 0.15)], 0.9, 0.5), lid, mat="flat", outline=0)


def brow(p, x0, y0, x1, y1, col, thick=2.2, arch=-1.5):
    p.paint(p.curve([(x0, y0), ((x0 + x1) / 2, min(y0, y1) + arch), (x1, y1)], thick, thick * 0.55), col, mat="fur", outline=0.4)


def nose(p, cx, ey, cy, skin, kind="human"):
    """Painted into the face: a soft bulb and nostril wing, a lit bridge, a shadowed side
    plane and a cast shadow; only the tip carries a faint line, like a painted portrait."""
    L = {"human": (19, 16, 4.6, 1.0), "broad": (19, 16, 6.4, 1.35), "big": (21, 16, 7.0, 1.2), "long": (31, 19, 4.8, 1.0),
         "fine": (17, 15, 3.8, 0.85)}[kind]
    tipx, tipy, bulb, wing = cx + L[0], cy + L[1] - 2, L[2], L[3]
    dark = shade(skin, 0.42)
    side = p.poly([(cx + 4, ey + 1), (cx + 8, ey), (tipx - bulb * 0.4, tipy - bulb), (tipx - bulb * 1.6, tipy + bulb * 0.6), (cx + 2, tipy - 2)])
    p.wash(side, dark, 0.5, 1.6)                                                   # side plane of the nose
    if kind == "long":
        p.paint(p.cap((cx + 8, ey + 2), (tipx - 1, tipy - 1), 2.6, bulb * 0.8), skin, outline=0.3, bevel=2.4)
    p.paint(p.ell(tipx - bulb * 0.4, tipy, bulb, bulb * 0.82), shade(skin, 0.86), outline=0.15, bevel=3.5)
    p.paint(p.ell(tipx - bulb * 1.5, tipy + 0.8, bulb * 0.75 * wing, bulb * 0.6), shade(skin, 0.74), outline=0.15, bevel=2.5)
    p.paint(p.ell(tipx - bulb * 1.1, tipy + bulb * 0.55, bulb * 0.42, bulb * 0.22), shade(skin, 0.28), mat="flat", outline=0)
    p.wash(p.cap((cx + 10, ey + 3), (tipx - bulb * 0.6, tipy - bulb * 1.0), 1.2, 1.6), (255, 242, 222), 0.22, 1.6)   # lit bridge
    p.wash(p.ell(tipx - bulb * 0.2, tipy - bulb * 0.35, bulb * 0.35, bulb * 0.25), (255, 248, 235), 0.35, 0.6)        # tip highlight
    p.wash(p.ell(tipx - bulb * 0.8, tipy + bulb + 2.2, bulb * 1.5, 2), dark, 0.55, 1.4)                            # shadow under it

def mouth(p, cx, my, skin, w=18, grim=0.0, lip=None):
    lipc = lip or mix(shade(skin, 0.85), (170, 80, 70), 0.25)
    p.wash(p.ell(cx + w * 0.55, my - 2, w * 0.45, 2.2), shade(lipc, 0.85), 0.55, 0.8)           # upper lip
    p.wash(p.ell(cx + w * 0.55, my + 2.6, w * 0.38, 2.4), lipc, 0.55, 0.8)                       # lower lip
    p.paint(p.curve([(cx + 1, my + grim), (cx + w * 0.55, my - 0.6), (cx + w, my + grim * 0.6)], 0.8, 0.55), shade(skin, 0.25), mat="flat", outline=0)
    p.wash(p.ell(cx + w * 0.55, my + 2.2, w * 0.18, 0.9), (255, 240, 230), 0.4, 0.5)             # lip highlight
    p.wash(p.ell(cx + w * 0.55, my + 7, w * 0.3, 2), shade(skin, 0.4), 0.4, 1.5)                  # shadow under the lip


def ear(p, kind, cx, cy, rx, skin, dark=0.85):
    ex, ey = cx - rx + 4, cy + 2
    s = shade(skin, dark)
    if kind == "human":
        m = p.ell(ex - 2, ey, 5, 9)
    elif kind == "elf":        # long, swept up and back
        m = p.poly([(ex + 2, ey - 6), (ex - 40, ey - 34), (ex - 34, ey - 26), (ex - 6, ey + 10), (ex + 2, ey + 8)])
    elif kind == "goblin":     # huge, sideways
        m = p.poly([(ex + 2, ey - 8), (ex - 44, ey - 18), (ex - 40, ey - 10), (ex - 4, ey + 12)])
    elif kind == "troll":
        m = p.poly([(ex + 2, ey - 6), (ex - 36, ey - 12), (ex - 32, ey - 5), (ex - 4, ey + 10)])
    elif kind == "orc":
        m = p.poly([(ex + 2, ey - 6), (ex - 12, ey - 16), (ex - 8, ey + 4), (ex - 2, ey + 10)])
    elif kind == "gnome":
        m = p.poly([(ex + 2, ey - 6), (ex - 18, ey - 12), (ex - 14, ey - 4), (ex - 3, ey + 10)])
    else:
        return None
    p.paint(m, s, outline=0.5)
    p.wash(m, shade(skin, 0.4), 0.35, 2, clip=p.ell(ex - 6, ey + 2, 10, 6))
    return (ex, ey)


def hoops(p, x, y, n=2, col=(235, 190, 70)):
    for i in range(n):
        r = 3.2
        ring = p.c.subtract(p.ell(x - i * 5, y + 4 + i * 3, r, r * 1.2), p.ell(x - i * 5, y + 4 + i * 3, r - 1.2, r * 1.2 - 1.2))
        p.paint(ring, col, mat="gold", outline=0.3)


def tusks(p, cx, cy, ry, kind="small"):
    bone = (238, 228, 198)
    my = cy + ry * 0.62
    if kind == "small":
        for x, s in ((cx + 18, 1.0), (cx + 2, 0.8)):
            p.paint(p.curve([(x, my + 6), (x + 1.5 * s, my - 1), (x - 0.5, my - 6 * s)], 2.2 * s, 0.7), bone, mat="bone", outline=0.5)
    else:   # troll: long, sweeping up past the cheeks
        for x, s in ((cx + 22, 1.0), (cx + 2, 0.75)):
            p.paint(p.curve([(x, my + 7), (x + 6 * s, my - 2), (x + 5 * s, my - 13 * s)], 2.8 * s, 0.7), bone, mat="bone", outline=0.5)


def portrait(spec):
    s = spec
    p = P(s["bg_in"], s["bg_out"])
    cx, cy, rx, ry = s.get("head", (62, 60, 31, 38))
    skin = s["skin"]
    # hair behind the head
    if s.get("hair_back"):
        hb = p.poly(s["hair_back"])
        p.paint(hb, shade(s["hair"], 0.8), mat="fur", outline=0.4)
        xs = [q[0] for q in s["hair_back"]]; ys = [q[1] for q in s["hair_back"]]
        p.strands(hb, [[(min(xs) + (max(xs) - min(xs)) * t, min(ys)), (min(xs) + (max(xs) - min(xs)) * t * 0.9, max(ys))]
                       for t in np.linspace(0.05, 0.95, 10)], shade(s["hair"], 1.2), r=0.4, alpha=0.4)
    neck(p, skin, cx - 2, cy + ry * 0.55, s.get("neck", 21))
    shoulders(p, s["cloth"], s.get("cloth_mat", "cloth"), s.get("trim"), s.get("trim_mat", "gold"), armor=s.get("armor", False), fur=s.get("fur"))
    for fn in s.get("behind", []):
        fn(p, cx, cy, rx, ry)
    earpos = ear(p, s.get("ears"), cx, cy, rx, skin)
    face = head_shape(p, cx, cy, rx, ry, s.get("jaw", "square"), s.get("chin", 0))
    p.paint(face, skin, outline=0.6, bevel=s.get("round", 13), texture=1.2)
    face_light(p, face, cx, cy, rx, ry, skin, rim=shade(s["bg_in"], 1.5))
    if s.get("brow_ridge"):
        m = p.poly([(cx - rx + 6, cy - 9), (cx + rx - 2, cy - 12), (cx + rx, cy - 5), (cx - rx + 6, cy - 3)])
        p.paint(p.c.intersect(m, face), shade(skin, 0.95), outline=0.4, bevel=2)
        p.wash(p.poly([(cx - rx, cy - 5), (cx + rx, cy - 7), (cx + rx, cy), (cx - rx, cy + 1)]), shade(skin, 0.35), 0.5, 2, clip=face)
    ey = cy - 2 + s.get("eye_dy", 0)
    es = s.get("eye_size", 5) * 1.15
    socket = shade(skin, 0.35)
    eye(p, cx - 8, ey + 0.5, es, s["eye"], s.get("glow", False), far=True, socket=socket)
    eye(p, cx + 14, ey, es, s["eye"], s.get("glow", False), socket=socket)
    bc = s.get("brow_col", s["hair"])
    bt = s.get("brow_thick", 2.2)
    brow(p, cx - 17, ey - 6 + s.get("brow_tilt", 0), cx - 1, ey - 6.5 - s.get("brow_tilt", 0) * 0.5, bc, bt * 0.85)
    brow(p, cx + 5, ey - 6.5 + s.get("brow_tilt", 0), cx + 24, ey - 8.5 - s.get("brow_tilt", 0), bc, bt)
    nose(p, cx, ey, cy, skin, s.get("nose", "human"))
    mouth(p, cx + 2, cy + ry * 0.62, skin, s.get("mouth_w", 17), s.get("grim", 0.8))
    for fn in s.get("front", []):
        fn(p, cx, cy, rx, ry)
    if s.get("tusks"):
        tusks(p, cx, cy, ry, s["tusks"])
    if s.get("hair_front"):
        hm = p.poly(s["hair_front"])
        p.paint(hm, s["hair"], mat="fur", outline=0.4)
        p.wash(p.ell(cx - rx * 0.7, cy - 10, rx * 0.6, ry), shade(s["hair"], 0.4), 0.5, 4, clip=hm)
        xs = [q[0] for q in s["hair_front"]]; ys = [q[1] for q in s["hair_front"]]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        auto = [[(x0 + (x1 - x0) * t, y0 + 2), (x0 + (x1 - x0) * (t * 0.8 + 0.02), (y0 + y1) / 2), (x0 + (x1 - x0) * (t * 0.6), y1)]
                for t in np.linspace(0.05, 0.95, 12)]
        p.strands(hm, auto + s.get("strands", []), shade(s["hair"], 1.4), r=0.4, alpha=0.5)
    if s.get("hoops") and earpos:
        hoops(p, earpos[0] - 4, earpos[1] + 6, s["hoops"])
    for fn in s.get("top", []):
        fn(p, cx, cy, rx, ry)
    return p.frame()


# ------------------------------------------------------------------ extras
def beard_full(col, length=40, braid=False):
    def f(p, cx, cy, rx, ry):
        top = cy + 8
        m = p.poly([(cx - rx + 4, cy - 2), (cx - rx + 8, cy + 18), (cx - 10, top + length), (cx + 4, top + length + 6), (cx + 18, top + length - 4),
                    (cx + rx - 2, cy + 18), (cx + rx, cy + 6), (cx + 22, cy + 16), (cx + 8, cy + 20), (cx - 2, cy + 12)])
        p.wash(m, col, 0.45, 2.5)
        p.paint(m, col, mat="fur", outline=0.2)
        p.wash(p.ell(cx - rx * 0.6, top + length * 0.4, rx * 0.5, length), shade(col, 0.45), 0.5, 4, clip=m)
        p.strands(m, [[(cx + dx, top - 2), (cx + dx * 0.85 + 1, top + length * 0.5), (cx + dx * 0.55 + 3, top + length + 2)] for dx in range(-24, 26, 4)],
                  shade(col, 1.45), r=0.45, alpha=0.5)
        p.strands(m, [[(cx + dx + 2, top), (cx + dx * 0.85 + 3, top + length * 0.6)] for dx in range(-22, 24, 4)], shade(col, 0.55), r=0.45, alpha=0.45)
        # moustache over the mouth
        mm = p.poly([(cx + 2, cy + 18), (cx + 10, cy + 15.5), (cx + 22, cy + 17), (cx + 25, cy + 22), (cx + 14, cy + 20.5), (cx + 4, cy + 22)])
        p.paint(mm, shade(col, 1.08), mat="fur", outline=0.35)
        p.strands(mm, [[(cx + 4 + d, cy + 15), (cx + 6 + d * 1.1, cy + 22)] for d in range(0, 20, 3)], shade(col, 0.6), r=0.4, alpha=0.5)
        if braid:
            for bx in (cx - 6, cx + 12):
                for k in range(3):
                    p.paint(p.ell(bx, top + length + 2 + k * 6, 3.5, 3.2), shade(col, 1.0 - k * 0.08), mat="fur", outline=0.4)
                p.paint(p.ell(bx, top + length - 2, 3.8, 2), (200, 170, 90), mat="gold", outline=0.4)
    return f


def goatee(col):
    def f(p, cx, cy, rx, ry):
        p.paint(p.poly([(cx + 4, cy + 16), (cx + 22, cy + 15), (cx + 24, cy + 21), (cx + 14, cy + 19), (cx + 4, cy + 21)]), col, mat="fur", outline=0.4)
        p.paint(p.poly([(cx + 6, cy + ry * 0.7), (cx + 20, cy + ry * 0.7), (cx + 16, cy + ry + 8), (cx + 10, cy + ry + 8)]), col, mat="fur", outline=0.4)
    return f


def stubble(col):
    def f(p, cx, cy, rx, ry):
        p.wash(p.poly([(cx - rx + 6, cy + 6), (cx + rx - 2, cy + 8), (cx + 16, cy + ry + 2), (cx - 4, cy + ry)]), col, 0.35, 2.5)
    return f


def scar(p, cx, cy, rx, ry):
    p.paint(p.curve([(cx + 10, cy - 14), (cx + 16, cy - 2), (cx + 20, cy + 8)], 0.7), (190, 120, 110), mat="flat", outline=0)


def goggles(p, cx, cy, rx, ry):
    p.paint(p.poly([(cx - rx - 2, cy - 22), (cx + rx + 4, cy - 26), (cx + rx + 4, cy - 21), (cx - rx - 2, cy - 17)]), (70, 50, 35), mat="leather", outline=0.4)
    for x, r in ((cx - 4, 7), (cx + 16, 8)):
        p.paint(p.ell(x, cy - 24, r, r * 0.9), (170, 150, 100), mat="gold", outline=0.5)
        lens = p.ell(x, cy - 24, r * 0.68, r * 0.6)
        p.paint(lens, (110, 200, 220), mat="metal", outline=0.3)
        p.paint(p.ell(x - r * 0.25, cy - 25.5, r * 0.22, r * 0.18), (255, 255, 255), mat="flat", outline=0)


def circlet(col, gem):
    def f(p, cx, cy, rx, ry):
        p.paint(p.curve([(cx - rx + 2, cy - 20), (cx + 6, cy - 26), (cx + rx + 2, cy - 22)], 1.4), col, mat="gold", outline=0.4)
        g = p.ell(cx + 10, cy - 25, 2.6, 3)
        p.glow(g, gem, radius=2, strength=0.6)
        p.paint(g, gem, mat="metal", outline=0.4)
    return f


def face_marks(col):
    def f(p, cx, cy, rx, ry):
        for pts in ([(cx - 16, cy - 2), (cx - 6, cy + 2), (cx - 2, cy + 12)], [(cx + 26, cy - 2), (cx + 20, cy + 3), (cx + 18, cy + 12)]):
            p.paint(p.curve(pts, 1.4, 0.4), col, mat="flat", outline=0)
    return f


def draenei_tendrils(col):
    def f(p, cx, cy, rx, ry):
        for x0, sw, k, ln in ((cx - rx + 10, -3, 0.75, 26), (cx - 4, 0, 0.85, 30), (cx + 12, 3, 1.0, 30), (cx + rx - 6, 5, 0.9, 24)):
            y0 = cy + ry * 0.55 if abs(x0 - cx - 4) > 14 else cy + ry * 0.85
            p.paint(p.curve([(x0, y0), (x0 + sw, y0 + ln * 0.5), (x0 + sw * 2.2, y0 + ln)], 2.4, 0.7), shade(col, k), outline=0.35)
    return f

def draenei_horns(p, cx, cy, rx, ry):
    col = (60, 55, 70)
    for x0, k in ((cx - 4, 0.8), (cx + 14, 1.0)):
        p.paint(p.curve([(x0, cy - ry * 0.7), (x0 - 18, cy - ry * 0.95), (x0 - 34, cy - ry * 0.6)], 4.5 * k, 1.2), shade(col, k), mat="bone", outline=0.5)


def spiked_helm(p, cx, cy, rx, ry):
    iron = (70, 80, 95)
    m = p.poly([(cx - rx - 4, cy - 2), (cx - rx, cy - ry * 0.8), (cx - 4, cy - ry - 4), (cx + rx, cy - ry * 0.7), (cx + rx + 4, cy - 8),
                (cx + rx - 2, cy - 12), (cx + 4, cy - 16), (cx - rx + 6, cy - 10), (cx - rx + 4, cy + 10)])
    p.paint(m, iron, mat="metal", outline=0.6)
    p.wash(m, (120, 190, 240), 0.25, 3)
    for x, h, k, lean in ((cx - 26, 26, 0.75, -6), (cx - 10, 38, 0.95, -3), (cx + 6, 40, 1.0, 1), (cx + 22, 30, 0.9, 5)):
        base_y = cy - ry * 0.78 - (5 if abs(x - cx) < 14 else 0)
        p.paint(p.poly([(x - 6, base_y + 5), (x + lean, base_y - h), (x + 6, base_y + 5)], smooth=0), shade(iron, k * 1.1), mat="metal", outline=0.5)
    # frost rime
    p.wash(p.ell(cx, cy - ry * 0.9, rx, 8), (210, 240, 255), 0.35, 2.5)


def hood(col):
    def f(p, cx, cy, rx, ry):
        m = p.poly([(cx - rx - 10, cy + ry + 10), (cx - rx - 8, cy - 10), (cx - 14, cy - ry - 10), (cx + 14, cy - ry - 8), (cx + rx + 8, cy - ry * 0.4),
                    (cx + rx + 2, cy - 14), (cx + 6, cy - ry * 0.7), (cx - rx + 4, cy - ry * 0.4), (cx - rx + 2, cy + 6), (cx - rx + 2, cy + ry + 10)])
        p.paint(m, col, mat="cloth", outline=0.6)
        p.wash(p.ell(cx - 4, cy - ry * 0.55, rx, 8), (0, 0, 0), 0.5, 3)
    return f


def bone_jaw(p, cx, cy, rx, ry):
    """Forsaken: the flesh worn through at the far corner of the mouth, teeth showing."""
    my = cy + ry * 0.62
    gash = p.poly([(cx - 14, my - 4), (cx + 4, my - 2), (cx + 4, my + 3), (cx - 12, my + 5)])
    p.paint(gash, (60, 25, 25), mat="flat", outline=0.3)
    for x in range(int(cx - 12), int(cx + 4), 3):
        p.paint(p.poly([(x, my - 2.5), (x + 2.2, my - 2.5), (x + 1.8, my + 1), (x + 0.4, my + 1)]), (225, 215, 185), mat="bone", outline=0.2)
    p.wash(p.ell(cx - 10, cy + 8, 8, 10), (40, 50, 35), 0.45, 2.5)    # sunken cheek

def mohawk(col, tall=34, swept=True):
    def f(p, cx, cy, rx, ry):
        m = p.poly([(cx - rx * 0.7, cy - ry * 0.6), (cx - rx * 0.4 - (18 if swept else 0), cy - ry - tall), (cx - 2, cy - ry - tall * 0.8),
                    (cx + rx * 0.6, cy - ry - 4), (cx + rx * 0.5, cy - ry * 0.72), (cx - 4, cy - ry * 0.9)])
        p.paint(m, col, mat="fur", outline=0.5)
        p.strands(m, [[(cx - 4 + d, cy - ry * 0.8), (cx - 10 + d, cy - ry - tall * 0.6)] for d in (-8, -2, 4, 10)], shade(col, 1.4))
    return f


def topknot(col):
    def f(p, cx, cy, rx, ry):
        p.paint(p.curve([(cx - 4, cy - ry * 0.85), (cx - 14, cy - ry - 14), (cx - 30, cy - ry - 8), (cx - 40, cy - ry + 14)], 5, 2.5), col, mat="fur")
        p.paint(p.ell(cx - 4, cy - ry * 0.86, 7, 4), col, mat="fur", outline=0.5)
        p.paint(p.ell(cx - 6, cy - ry * 0.95, 4, 2.5), (200, 160, 70), mat="gold", outline=0.4)
    return f


def gold_tooth(p, cx, cy, rx, ry):
    my = cy + ry * 0.62
    p.paint(p.poly([(cx + 4, my - 1), (cx + 24, my - 2), (cx + 22, my + 5), (cx + 6, my + 5)]), (40, 15, 15), mat="flat", outline=0.4)   # grin
    for i, x in enumerate(range(int(cx + 6), int(cx + 22), 3)):
        col = (240, 200, 70) if i == 3 else (240, 235, 215)
        p.paint(p.poly([(x, my - 1), (x + 2.6, my - 1.2), (x + 1.3, my + 2.6)]), col, mat="gold" if i == 3 else "bone", outline=0.3)


# ------------------------------------------------------------------ muzzle heads (tauren, worgen, pandaren)
def muzzle_portrait(kind, fur, bg_in, bg_out, eye_col, cloth, trim=None, extra=None):
    p = P(bg_in, bg_out)
    cx, cy = 58, 62
    dark, light = shade(fur, 0.6), shade(fur, 1.3)
    shoulders(p, cloth, "cloth", trim, fur=fur if kind != "pandaren" else None)
    if kind == "tauren":
        horn = (232, 222, 196)
        for x0, k in ((cx - 18, 0.8), (cx + 14, 1.0)):
            sgn = -1 if x0 < cx else 1
            p.paint(p.curve([(x0, cy - 24), (x0 + sgn * 26, cy - 34), (x0 + sgn * 34, cy - 58)], 6.5 * k, 2), shade(horn, k), mat="bone", outline=0.6)
            p.wash(p.ell(x0 + sgn * 6, cy - 26, 6, 4), (90, 70, 50), 0.6, 1)
        neck_m = p.poly([(cx - 30, cy + 10), (cx + 30, cy + 10), (cx + 38, 112), (cx - 34, 112)])
        p.paint(neck_m, fur, mat="fur", outline=0.5)
        head = p.c.union(p.ell(cx - 2, cy - 6, 30, 30), p.poly([(cx - 20, cy), (cx + 30, cy - 8), (cx + 44, cy + 14), (cx + 40, cy + 36), (cx + 6, cy + 40), (cx - 22, cy + 22)]))
        p.paint(head, fur, mat="fur", outline=0.6)
        for side in (-1, 1):                        # floppy ears
            ex = cx - 30 if side < 0 else cx + 22
            p.paint(p.ell(ex, cy - 14, 10, 5, rot=0.4 * side), shade(fur, 0.9), mat="fur", outline=0.5)
        muzzle = p.ell(cx + 28, cy + 22, 17, 14)
        p.paint(muzzle, shade(fur, 1.15), mat="skin", outline=0.5)
        p.wash(muzzle, (60, 40, 35), 0.35, 3, clip=p.ell(cx + 32, cy + 30, 18, 8))
        for nx in (cx + 26, cx + 38):
            p.paint(p.ell(nx, cy + 22, 2.6, 2), (35, 22, 20), mat="flat", outline=0)
        ring = p.c.subtract(p.ell(cx + 32, cy + 31, 7, 6), p.ell(cx + 32, cy + 29.5, 5, 4))
        p.paint(ring, (235, 190, 70), mat="gold", outline=0.4)
        p.paint(p.poly([(cx - 30, cy - 34), (cx + 10, cy - 38), (cx + 20, cy - 30), (cx - 26, cy - 24)]), shade(fur, 0.7), mat="fur", outline=0.4)  # forelock
        for bx in (cx - 30, cx - 22):                # braids with beads
            p.paint(p.curve([(bx, cy - 4), (bx - 2, cy + 18), (bx, cy + 36)], 3, 2), shade(fur, 0.65), mat="fur", outline=0.4)
            p.paint(p.ell(bx, cy + 30, 3, 3.5), (200, 70, 50), mat="bone", outline=0.4)
        ex, ey = cx + 10, cy - 6
        eye(p, ex - 18, ey + 1, 4.5, eye_col, far=True, socket=dark)
        eye(p, ex + 4, ey, 4.8, eye_col, socket=dark)
        brow(p, ex - 2, ey - 6, ex + 12, ey - 8, dark, 2.4)
        p.wash(p.ell(cx - 24, cy, 18, 30), dark, 0.5, 5, clip=head)
    elif kind == "worgen":
        for x0, k in ((cx - 20, 0.8), (cx - 2, 1.0)):   # tall ears
            m = p.poly([(x0 - 8, cy - 24), (x0 - 4, cy - 62), (x0 + 10, cy - 26)])
            p.paint(m, shade(fur, k), mat="fur", outline=0.5)
            p.wash(p.poly([(x0 - 3, cy - 28), (x0 - 2, cy - 52), (x0 + 5, cy - 28)]), (150, 100, 100), 0.4, 1.5)
        mane = p.poly([(cx - 46, 116), (cx - 40, cy - 10), (cx - 20, cy - 30), (cx + 20, cy - 28), (cx + 34, cy), (cx + 40, 116)])
        p.paint(mane, dark, mat="fur", outline=0.5)
        p.strands(mane, [[(cx + d, cy - 20), (cx + d * 1.3, cy + 20), (cx + d * 1.4, 110)] for d in (-30, -20, -10, 0, 10, 20)], shade(fur, 1.1))
        head = p.c.union(p.ell(cx - 4, cy - 4, 26, 24), p.poly([(cx + 4, cy - 14), (cx + 40, cy + 2), (cx + 46, cy + 10), (cx + 40, cy + 24), (cx + 4, cy + 26)]))
        p.paint(head, fur, mat="fur", outline=0.6)
        p.paint(p.poly([(cx + 8, cy + 18), (cx + 42, cy + 20), (cx + 38, cy + 30), (cx + 10, cy + 32)]), shade(fur, 0.8), mat="fur", outline=0.5)   # lower jaw
        p.paint(p.poly([(cx + 10, cy + 17), (cx + 42, cy + 18), (cx + 40, cy + 22), (cx + 12, cy + 23)]), (90, 25, 30), mat="flat", outline=0.3)   # mouth
        for x in range(int(cx + 14), int(cx + 40), 4):
            p.paint(p.poly([(x, cy + 17), (x + 2.6, cy + 17), (x + 1.3, cy + 22)]), (240, 232, 210), mat="bone", outline=0.3)
        for x in (cx + 18, cx + 34):
            p.paint(p.poly([(x, cy + 30), (x + 3, cy + 30), (x + 1.5, cy + 24)]), (240, 232, 210), mat="bone", outline=0.3)
        p.paint(p.ell(cx + 44, cy + 7, 4.2, 3.4), (25, 20, 22), mat="skin", outline=0.4)    # nose
        p.wash(p.cap((cx + 10, cy - 6), (cx + 40, cy + 4), 3), light, 0.35, 2, clip=head)
        brow(p, cx - 12, cy - 12, cx + 2, cy - 13, dark, 2.6)
        brow(p, cx + 6, cy - 13, cx + 20, cy - 9, dark, 2.8)
        eye(p, cx - 6, cy - 6, 4.4, eye_col, glow=True, far=True)
        eye(p, cx + 12, cy - 6, 4.6, eye_col, glow=True)
        p.wash(p.ell(cx - 26, cy + 4, 14, 24), dark, 0.5, 4, clip=head)
    elif kind == "pandaren":
        black, white = (38, 36, 36), (236, 232, 222)
        for x0 in (cx - 24, cx + 12):                    # round black ears
            p.paint(p.ell(x0, cy - 34, 10, 9), black, mat="fur", outline=0.5)
        head = p.c.union(p.ell(cx, cy - 2, 36, 32), p.ell(cx + 22, cy + 16, 18, 13))
        p.paint(head, white, mat="fur", outline=0.6)
        p.wash(p.ell(cx - 30, cy + 6, 16, 30), (120, 115, 105), 0.5, 5, clip=head)
        for x0, k in ((cx - 10, 0.85), (cx + 14, 1.0)):   # eye patches
            p.paint(p.ell(x0, cy - 4, 9 * k, 7, rot=-0.5), black, mat="fur", outline=0)
        eye(p, cx - 9, cy - 4, 4.0, eye_col, far=True, lid=(10, 10, 10))
        eye(p, cx + 15, cy - 5, 4.3, eye_col, lid=(10, 10, 10))
        p.paint(p.ell(cx + 34, cy + 12, 6, 4.2), black, mat="skin", outline=0.4)     # nose
        mouth(p, cx + 18, cy + 22, white, 18, 1.5, lip=(200, 190, 180))
        p.paint(p.curve([(cx - 30, cy - 22), (cx, cy - 30), (cx + 34, cy - 22)], 2.6), (200, 60, 50), mat="cloth", outline=0.4)   # headband
        p.paint(p.ell(cx + 22, cy - 26, 3.4, 3.2), (240, 200, 80), mat="gold", outline=0.4)
        # shoulders in robes with a fur collar of black
        p.paint(p.poly([(10, 134), (20, 100), (40, 94), (60, 100), (86, 94), (110, 104), (120, 134)]), black, mat="fur", outline=0.5)
    if extra:
        extra(p, cx, cy)
    return p.frame()


# ------------------------------------------------------------------ the 15 races
def specs():
    S = {}
    S["Humans"] = dict(bg_in=(70, 90, 140), bg_out=(14, 18, 34), skin=(232, 180, 140), hair=(120, 85, 45), eye=(80, 130, 200),
                       cloth=(150, 160, 175), armor=True, trim=(40, 70, 150), jaw="square", nose="human",
                       hair_front=[(30, 50), (34, 30), (50, 20), (76, 20), (92, 30), (96, 42), (82, 34), (64, 32), (48, 36), (40, 56), (34, 70)],
                       hair_back=[(26, 50), (30, 26), (60, 16), (90, 26), (92, 50), (80, 96), (36, 100), (24, 80)],
                       strands=[[(46, 26), (40, 40), (36, 60)], [(60, 22), (52, 34)], [(74, 22), (84, 32)]],
                       front=[stubble((110, 75, 40)), goatee((120, 85, 45))], ears="human", brow_tilt=1.5)
    S["Dwarves"] = dict(bg_in=(120, 80, 45), bg_out=(26, 16, 10), skin=(226, 160, 120), hair=(190, 90, 40), eye=(90, 120, 160),
                        head=(62, 58, 33, 36), cloth=(110, 100, 95), armor=True, trim=(210, 150, 50), jaw="heavy", nose="big",
                        brow_thick=3.6, brow_ridge=True, eye_size=4.2,
                        hair_front=[(28, 46), (30, 28), (52, 16), (80, 18), (96, 34), (82, 30), (60, 28), (40, 36), (34, 54)],
                        front=[beard_full((190, 90, 40), 34, braid=True)], ears="human", brow_tilt=2)
    S["Gnomes"] = dict(bg_in=(60, 140, 140), bg_out=(10, 26, 30), skin=(240, 196, 168), hair=(240, 110, 180), eye=(70, 170, 120),
                       head=(62, 62, 36, 38), cloth=(70, 120, 150), trim=(230, 200, 80), jaw="narrow", nose="big", eye_size=6.5,
                       hair_back=[(22, 40), (40, 20), (84, 18), (104, 34), (110, 70), (96, 60), (90, 40), (40, 40), (30, 70), (16, 66)],
                       hair_front=[(30, 40), (44, 22), (80, 20), (98, 34), (80, 30), (60, 30), (42, 38)],
                       top=[goggles], ears="gnome", grim=-1.2, brow_tilt=-1.5)
    S["Night Elves"] = dict(bg_in=(60, 50, 120), bg_out=(10, 8, 26), skin=(150, 120, 190), hair=(40, 80, 150), eye=(225, 235, 255),
                            glow=True, cloth=(60, 70, 90), trim=(190, 200, 220), trim_mat="metal", jaw="narrow", nose="fine",
                            hair_back=[(24, 46), (30, 20), (64, 12), (96, 24), (100, 60), (92, 124), (60, 130), (30, 124), (20, 90)],
                            hair_front=[(30, 52), (32, 28), (54, 16), (84, 18), (100, 36), (86, 34), (70, 28), (54, 32), (40, 46), (36, 70)],
                            strands=[[(50, 22), (42, 40), (38, 62)], [(66, 18), (58, 30)], [(82, 22), (94, 34)]],
                            front=[face_marks((60, 40, 110))], top=[circlet((200, 210, 230), (180, 220, 255))], ears="elf",
                            brow_col=(40, 80, 150), brow_thick=1.6, grim=0.3)
    S["Draenei"] = dict(bg_in=(80, 90, 160), bg_out=(12, 14, 34), skin=(120, 140, 210), hair=(30, 30, 45), eye=(200, 235, 255), glow=True,
                        cloth=(220, 220, 235), trim=(120, 90, 190), jaw="square", nose="human",
                        hair_back=[(26, 40), (34, 22), (66, 16), (92, 28), (96, 50), (84, 110), (40, 110), (26, 80)],
                        hair_front=[(30, 44), (36, 26), (60, 18), (86, 24), (98, 38), (80, 32), (60, 30), (44, 36), (36, 54)],
                        front=[draenei_tendrils((120, 140, 210))], top=[draenei_horns], ears=None, brow_tilt=1.5)
    S["Worgen"] = None
    S["High Elves"] = dict(bg_in=(70, 110, 170), bg_out=(14, 22, 40), skin=(240, 210, 185), hair=(235, 235, 240), eye=(120, 180, 255),
                           glow=True, cloth=(235, 235, 240), trim=(40, 90, 190), jaw="narrow", nose="fine",
                           hair_back=[(24, 46), (30, 20), (64, 12), (96, 24), (100, 60), (94, 124), (60, 130), (28, 124), (20, 90)],
                           hair_front=[(30, 52), (32, 28), (54, 16), (84, 18), (100, 36), (86, 34), (70, 28), (54, 32), (40, 46), (36, 70)],
                           strands=[[(50, 22), (42, 40), (38, 62)], [(66, 18), (58, 30)], [(82, 22), (94, 34)]],
                           top=[circlet((240, 210, 120), (90, 150, 255))], ears="elf", brow_col=(220, 220, 230), brow_thick=1.6, grim=0.3)
    S["Orcs"] = dict(bg_in=(120, 50, 30), bg_out=(26, 10, 6), skin=(110, 160, 70), hair=(30, 26, 24), eye=(220, 60, 40), eye_size=4.8,
                     head=(60, 62, 34, 38), cloth=(90, 80, 75), armor=True, fur=(120, 95, 70), jaw="heavy", nose="broad",
                     brow_ridge=True, brow_thick=3.4, tusks="small", ears="orc", hoops=2,
                     top=[topknot((30, 26, 24))], front=[scar, stubble((40, 70, 30))], brow_tilt=2.5, grim=2.2, mouth_w=22)
    S["Trolls"] = dict(bg_in=(40, 120, 110), bg_out=(6, 24, 22), skin=(90, 140, 190), hair=(220, 50, 40), eye=(250, 220, 90),
                       head=(56, 62, 30, 38), cloth=(120, 90, 60), fur=(150, 120, 80), jaw="pointed", nose="long", tusks="troll",
                       ears="troll", hoops=3, top=[mohawk((220, 50, 40))], eye_size=4.6, brow_tilt=2, grim=1.5)
    S["Tauren"] = None
    S["Forsaken"] = dict(bg_in=(60, 80, 50), bg_out=(10, 14, 10), skin=(160, 170, 145), hair=(30, 30, 34), eye=(250, 230, 90), glow=True,
                         cloth=(60, 55, 70), trim=(120, 170, 70), jaw="narrow", nose="fine",
                         hair_back=[(26, 46), (34, 20), (64, 14), (94, 24), (96, 54), (88, 110), (40, 110), (24, 80)],
                         hair_front=[(30, 50), (36, 24), (60, 16), (88, 22), (96, 36), (84, 30), (72, 34), (60, 28), (46, 40), (38, 64)],
                         behind=[], front=[bone_jaw], top=[hood((60, 55, 70))], ears=None, brow_thick=1.4, grim=1.8)
    S["Blood Elves"] = dict(bg_in=(150, 40, 40), bg_out=(30, 8, 10), skin=(245, 214, 190), hair=(235, 190, 80), eye=(120, 255, 90),
                            glow=True, cloth=(170, 30, 40), trim=(240, 200, 80), jaw="narrow", nose="fine",
                            hair_back=[(26, 46), (34, 18), (70, 12), (100, 30), (60, 26), (40, 40), (30, 70), (14, 118), (4, 100)],
                            hair_front=[(30, 52), (32, 26), (58, 14), (88, 20), (102, 40), (88, 34), (72, 26), (56, 30), (42, 44), (36, 66)],
                            strands=[[(50, 20), (42, 36), (38, 60)], [(70, 18), (60, 28)], [(86, 24), (98, 36)]],
                            top=[circlet((240, 200, 80), (255, 80, 60))], ears="elf", brow_col=(220, 170, 70), brow_thick=1.5, grim=0.2)
    S["Goblins"] = dict(bg_in=(130, 120, 40), bg_out=(24, 22, 8), skin=(120, 175, 70), hair=(40, 30, 25), eye=(240, 180, 60),
                        head=(56, 64, 28, 34), cloth=(110, 80, 50), trim=(240, 200, 60), jaw="pointed", nose="long", eye_size=4.4,
                        ears="goblin", hoops=2, top=[goggles], front=[gold_tooth], brow_tilt=-2, grim=0)
    S["Pandaren"] = None
    S["Scourge"] = dict(bg_in=(40, 70, 110), bg_out=(4, 8, 18), skin=(170, 185, 200), hair=(30, 30, 40), eye=(140, 220, 255), glow=True,
                        cloth=(60, 70, 90), armor=True, trim=(140, 200, 240), trim_mat="metal", jaw="square", nose="human",
                        front=[stubble((60, 70, 90))], top=[spiked_helm], ears=None, brow_thick=2.4, brow_tilt=3, grim=2)
    return S


LEADERS = {"Humans": "Anduin Wrynn", "Orcs": "Thrall", "Night Elves": "Tyrande Whisperwind", "Dwarves": "Magni Bronzebeard",
           "Gnomes": "Gelbin Mekkatorque", "Tauren": "Cairne Bloodhoof", "Trolls": "Vol'jin", "Blood Elves": "Lor'themar Theron",
           "High Elves": "Anasterian Sunstrider", "Pandaren": "Emperor Shaohao", "Forsaken": "Sylvanas Windrunner",
           "Draenei": "Velen", "Goblins": "Jastor Gallywix", "Worgen": "Genn Greymane", "Scourge": "Arthas Menethil"}


def render(race):
    sp = specs()[race]
    if race == "Tauren":
        return muzzle_portrait("tauren", (120, 80, 50), (150, 95, 40), (26, 14, 6), (90, 60, 30), (150, 110, 60), (230, 200, 120))
    if race == "Worgen":
        return muzzle_portrait("worgen", (110, 108, 112), (70, 75, 90), (10, 12, 16), (250, 190, 60), (60, 60, 70))
    if race == "Pandaren":
        return muzzle_portrait("pandaren", (236, 232, 222), (60, 130, 90), (8, 22, 14), (90, 170, 90), (40, 40, 40))
    return portrait(sp)


def write_all(images_dir, leaders=None):
    """Writes Images/LeaderIcons/<leader>.png for every race; `leaders` maps race -> leader."""
    leaders = leaders or LEADERS
    d = os.path.join(images_dir, "LeaderIcons")
    os.makedirs(d, exist_ok=True)
    for race, leader in leaders.items():
        render(race).save(os.path.join(d, leader + ".png"))
    return len(leaders)
