"""A small painter for chunky, hand-painted-looking unit sprites.

Shapes are drawn supersampled (S x), each shape is shaded as a rounded form lit from the
upper left (so flat polygons read as sculpted, painted volumes), gets a dark ink outline,
and lands on one of Unciv's three unit layers:
  "base"  - fixed colours
  "l1"    - multiplied by the nation's inner colour in game (draw it in greys)
  "l2"    - multiplied by the nation's outer colour in game (draw it in greys)
Every new shape covers whatever was drawn before it on all three layers, so painter's
order works across layers.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = 4                       # supersampling
INK = (28, 20, 16)
LIGHT = np.array([-0.55, -0.75, 0.85])
LIGHT = LIGHT / np.linalg.norm(LIGHT)
HALF = LIGHT + np.array([0, 0, 1.0])
HALF = HALF / np.linalg.norm(HALF)

# material: (ambient, diffuse, specular strength, specular power, bevel radius scale)
MATERIALS = {
    "cloth":   (0.42, 0.72, 0.05, 6, 1.0),
    "skin":    (0.40, 0.75, 0.18, 10, 1.0),
    "metal":   (0.30, 0.80, 0.85, 18, 0.8),
    "gold":    (0.35, 0.75, 0.70, 14, 0.8),
    "leather": (0.40, 0.70, 0.15, 8, 0.9),
    "wood":    (0.42, 0.68, 0.08, 6, 0.9),
    "fur":     (0.45, 0.65, 0.02, 4, 1.2),
    "bone":    (0.48, 0.65, 0.25, 10, 0.9),
    "flat":    (1.0, 0.0, 0.0, 1, 1.0),
    "glow":    (1.0, 0.0, 0.0, 1, 1.0),
}


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.W, self.H = w * S, h * S
        self.layers = {k: np.zeros((self.H, self.W, 4), np.float32) for k in ("base", "l1", "l2")}
        self.rng = np.random.default_rng(7)
        yy, xx = np.mgrid[0:self.H, 0:self.W]
        self.noise = self._noise()

    def _noise(self):
        """Low-frequency brush texture so big areas don't look airbrushed."""
        n = Image.effect_noise((self.W // 6 + 1, self.H // 6 + 1), 40).resize((self.W, self.H), Image.BICUBIC)
        a = np.asarray(n, np.float32) / 255.0
        return (a - a.mean()) * 0.18

    # ------------------------------------------------------------------ masks
    def mask(self):
        return Image.new("L", (self.W, self.H), 0)

    def poly(self, pts, m=None):
        m = m or self.mask()
        ImageDraw.Draw(m).polygon([(x * S, y * S) for x, y in pts], fill=255)
        return m

    def ellipse(self, cx, cy, rx, ry, m=None, rot=0):
        m = m or self.mask()
        if rot == 0:
            ImageDraw.Draw(m).ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], fill=255)
        else:
            pts = [(cx + rx * math.cos(t) * math.cos(rot) - ry * math.sin(t) * math.sin(rot),
                    cy + rx * math.cos(t) * math.sin(rot) + ry * math.sin(t) * math.cos(rot))
                   for t in np.linspace(0, 2 * math.pi, 48, endpoint=False)]
            self.poly(pts, m)
        return m

    def capsule(self, p1, p2, r1, r2=None, m=None):
        """A tapered limb: circles at both ends joined by tangent lines."""
        r2 = r1 if r2 is None else r2
        m = m or self.mask()
        (x1, y1), (x2, y2) = p1, p2
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1e-6
        nx, ny = -dy / L, dx / L
        self.poly([(x1 + nx * r1, y1 + ny * r1), (x2 + nx * r2, y2 + ny * r2),
                   (x2 - nx * r2, y2 - ny * r2), (x1 - nx * r1, y1 - ny * r1)], m)
        self.ellipse(x1, y1, r1, r1, m)
        self.ellipse(x2, y2, r2, r2, m)
        return m

    def curve(self, pts, r1, r2=None, m=None, steps=24):
        """A thick quadratic/cubic Bezier stroke (for blades, tails, bows, hair)."""
        r2 = r1 if r2 is None else r2
        m = m or self.mask()
        path = bezier(pts, steps)
        for i in range(len(path) - 1):
            t = i / (len(path) - 1)
            self.capsule(path[i], path[i + 1], r1 + (r2 - r1) * t, r1 + (r2 - r1) * (t + 1 / (len(path) - 1)), m)
        return m

    def union(self, *ms):
        out = self.mask()
        for m in ms:
            out = Image.fromarray(np.maximum(np.asarray(out), np.asarray(m)))
        return out

    def subtract(self, a, b):
        return Image.fromarray(np.clip(np.asarray(a, np.int16) - np.asarray(b, np.int16), 0, 255).astype(np.uint8))

    def intersect(self, a, b):
        return Image.fromarray(np.minimum(np.asarray(a), np.asarray(b)))

    # ------------------------------------------------------------------ painting
    def paint(self, m, color, layer="base", mat="cloth", outline=1.0, bevel=None, dark=1.0,
              gradient=0.18, texture=1.0, ink=INK):
        """Shade mask m as a rounded form and composite it (with an ink outline)."""
        a = np.asarray(m, np.float32) / 255.0
        if a.max() == 0:
            return
        amb, kd, ks, sp, bs = MATERIALS[mat]
        if outline:
            w = max(1, int(round(outline * S * 0.7)))
            ol = np.asarray(m.filter(ImageFilter.MaxFilter(2 * w + 1)), np.float32) / 255.0
            self._comp(ol, np.array(ink, np.float32), "base")
        if mat in ("flat", "glow"):
            rgb = np.broadcast_to(np.array(color, np.float32), a.shape + (3,)) * dark
        else:
            # size of the form decides how round it looks
            area = a.sum() / (S * S)
            r = bevel if bevel is not None else max(1.2, min(10.0, math.sqrt(area) * 0.26)) * bs
            hgt = np.asarray(m.filter(ImageFilter.GaussianBlur(r * S)), np.float32) / 255.0
            gy, gx = np.gradient(hgt)
            k = r * S * 2.2
            n = np.dstack([-gx * k, -gy * k, np.ones_like(gx)])
            n /= np.linalg.norm(n, axis=2, keepdims=True)
            dif = np.clip(n @ LIGHT, 0, 1)
            spec = np.clip(n @ HALF, 0, 1) ** sp * ks
            # top-to-bottom falloff within the shape
            ys = np.nonzero(a.max(axis=1))[0]
            y0, y1 = ys.min(), ys.max() + 1
            vg = np.zeros(a.shape[0], np.float32)
            vg[y0:y1] = np.linspace(gradient, -gradient, y1 - y0)
            light = (amb + kd * dif + vg[:, None]) * dark + self.noise * texture * (0.5 if mat == "metal" else 1)
            col = np.array(color, np.float32)
            rgb = col[None, None, :] * light[..., None] + 255 * spec[..., None] * dark
        rgb = np.clip(rgb, 0, 255)
        self._comp(a, rgb, layer)

    def _comp(self, a, rgb, layer):
        a = a[..., None]
        for k, L in self.layers.items():
            if k == layer:
                A = L[..., 3:4]
                out_a = a + A * (1 - a)
                c = np.broadcast_to(rgb, L[..., :3].shape)
                L[..., :3] = np.where(out_a > 0, (c * a + L[..., :3] * A * (1 - a)) / np.maximum(out_a, 1e-6), 0)
                L[..., 3:4] = out_a
            else:
                L[..., 3:4] *= (1 - a)

    def glow(self, m, color, radius=3, strength=0.8, layer="base"):
        """Soft additive-looking light around a shape (spell effects)."""
        g = np.asarray(m.filter(ImageFilter.GaussianBlur(radius * S)), np.float32) / 255.0
        g = np.clip(g * 2.2, 0, 1) * strength
        L = self.layers[layer]
        A = L[..., 3:4]
        a = g[..., None]
        # only add glow where the pixel isn't already solid, plus a light wash over it
        out_a = a + A * (1 - a)
        col = np.array(color, np.float32)
        L[..., :3] = np.where(out_a > 0, (col * a + L[..., :3] * A * (1 - a)) / np.maximum(out_a, 1e-6), 0)
        L[..., 3:4] = out_a

    def wash(self, m, color, alpha=0.5, blur=2.0, layer="base", clip=None):
        """Glaze a colour over what is already painted (soft painted shadows and
        highlights). Doesn't change coverage; `clip` limits it to another mask."""
        a = np.asarray(m.filter(ImageFilter.GaussianBlur(blur * S)) if blur else m, np.float32) / 255.0 * alpha
        if clip is not None:
            a = a * (np.asarray(clip, np.float32) / 255.0)
        L = self.layers[layer]
        a = a[..., None] * (L[..., 3:4] > 0)
        L[..., :3] = L[..., :3] * (1 - a) + np.array(color, np.float32) * a

    def fill_background(self, inner, outer, cx=0.5, cy=0.45):
        """Opaque radial-gradient backdrop (portraits)."""
        yy, xx = np.mgrid[0:self.H, 0:self.W].astype(np.float32)
        d = np.sqrt(((xx / self.W - cx) / 0.75) ** 2 + ((yy / self.H - cy) / 0.75) ** 2)
        t = np.clip(d / 0.75, 0, 1)[..., None]
        rgb = np.array(inner, np.float32) * (1 - t) + np.array(outer, np.float32) * t
        rgb = rgb + self.noise[..., None] * 60
        L = self.layers["base"]
        L[..., :3] = np.clip(rgb, 0, 255)
        L[..., 3] = 1.0

    def shadow(self, cx, cy, rx, ry, alpha=0.35):
        m = self.ellipse(cx, cy, rx, ry).filter(ImageFilter.GaussianBlur(1.5 * S))
        a = np.asarray(m, np.float32) / 255.0 * alpha
        L = self.layers["base"]
        A = L[..., 3:4]
        aa = a[..., None]
        out_a = aa + A * (1 - aa)
        L[..., :3] = np.where(out_a > 0, (0 * aa + L[..., :3] * A * (1 - aa)) / np.maximum(out_a, 1e-6), 0)
        L[..., 3:4] = out_a

    def finish(self, outer_ink=1.0):
        """Thicker silhouette outline, then downsample each layer to final size."""
        if outer_ink:
            alpha = np.maximum.reduce([L[..., 3] for L in self.layers.values()])
            m = Image.fromarray((np.clip(alpha, 0, 1) * 255).astype(np.uint8))
            w = int(round(outer_ink * S * 0.9))
            ol = np.asarray(m.filter(ImageFilter.MaxFilter(2 * w + 1)), np.float32) / 255.0
            ol = np.clip(ol - alpha, 0, 1)
            B = self.layers["base"]
            a = ol[..., None]
            out_a = a + B[..., 3:4] * (1 - a)
            B[..., :3] = np.where(out_a > 0, (np.array(INK, np.float32) * a + B[..., :3] * B[..., 3:4] * (1 - a)) / np.maximum(out_a, 1e-6), 0)
            B[..., 3:4] = out_a
        out = []
        for k in ("base", "l1", "l2"):
            L = self.layers[k]
            pre = np.dstack([L[..., :3] * L[..., 3:4], L[..., 3:4] * 255])
            im = Image.fromarray(np.clip(pre, 0, 255).astype(np.uint8), "RGBA")
            # premultiplied box downsample
            small = np.asarray(im.resize((self.w, self.h), Image.BOX), np.float32)
            a = small[..., 3:4] / 255.0
            rgb = np.where(a > 0.003, small[..., :3] / np.maximum(a, 1e-6), 0)
            arr = np.dstack([np.clip(rgb, 0, 255), small[..., 3:4]]).astype(np.uint8)
            out.append(Image.fromarray(arr, "RGBA"))
        return out


def bezier(pts, steps=24):
    pts = [np.array(p, float) for p in pts]
    out = []
    for i in range(steps + 1):
        t = i / steps
        q = pts[:]
        while len(q) > 1:
            q = [q[j] * (1 - t) + q[j + 1] * t for j in range(len(q) - 1)]
        out.append(tuple(q[0]))
    return out


def grey(v):
    """A grey for the tinted layers (v in 0..1)."""
    g = int(255 * v)
    return (g, g, g)


def mix(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
