"""Pixel-art unit sprites in the manner of Unciv's FantasyHex unit set.

`PixelCanvas` is a drop-in replacement for paint.Canvas: the same unit-drawing code
(wc_style_units, wc_style_more) runs unchanged, but every shape is snapped to a coarse
art-pixel grid as it is drawn, shaded with a few flat tones, and given a 1-pixel black
outline where it overlaps what was drawn before, so arms, shields and weapons read as
separate parts the way they do in hand-made pixel sprites. finish() adds the black
silhouette outline and a flat ground shadow, snaps the colours to a small palette, and
scales the art back up with nearest-neighbour to the canvas size.

Scale: the renderers draw on a 2x copy of an AbsoluteUnits canvas (e.g. 190x162).
AbsoluteUnits sprites are about three times the size of FantasyHex ones; one art pixel
of FantasyHex would be 6 canvas pixels, but at that size faces, beards and fireballs
are lost, so one art pixel = BLOCK (4) canvas pixels: a 47x40 grid for a 95x81 tile,
figures about 24 art pixels tall (art pixels 2/3 the size of FantasyHex's). Layers are kept (every art pixel belongs to one of base / l1 / l2), so
nation colours still tint the sprites.
"""
import math
import numpy as np
from PIL import Image, ImageFilter
import paint
from paint import Canvas, MATERIALS, S

BLOCK = 4
INK = np.array([14, 11, 10], np.float32)
SHADOW = (40, 40, 40, 95)
LUM = np.array([0.3, 0.59, 0.11], np.float32)
PART_LINES = True
PART_MIN = 12
PART_CONTRAST = 18


class PixelCanvas(Canvas):
    def __init__(self, w, h, block=BLOCK):
        super().__init__(w, h)
        self.noise = np.zeros_like(self.noise)      # flat paint, no brush texture
        self.B = block
        self.gw, self.gh = w // block, h // block
        self.rgb = np.zeros((self.gh, self.gw, 3), np.float32)
        self.own = np.full((self.gh, self.gw), -1, np.int8)     # -1 empty, 0 base, 1 l1, 2 l2
        self.ink = np.zeros((self.gh, self.gw), bool)            # outline pixels
        self.fill = np.zeros((self.gh, self.gw), bool)           # glow pixels (no outline)
        self.shadows = []

    # ------------------------------------------------------------ helpers
    def _cov(self, a):
        """coverage of each art pixel by a full-resolution float mask"""
        k = self.B * S
        gh, gw = self.gh, self.gw
        a = a[:gh * k, :gw * k]
        return a.reshape(gh, k, gw, k).mean((1, 3))

    def _snap(self, cov):
        cell = cov >= 0.5
        if cov.max() < 0.62:          # a thin part (spear shaft, staff, bowstring)
            cell |= cov >= 0.27
        if not cell.any() and cov.max() > 0.12:
            cell = cov >= cov.max() * 0.999
        return cell

    @staticmethod
    def _ring(cell):
        p = np.pad(cell, 1)
        return (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]) & ~cell

    # ------------------------------------------------------------ drawing API
    def paint(self, m, color, layer="base", mat="cloth", outline=1.0, bevel=None, dark=1.0,
              gradient=0.18, texture=1.0, ink=paint.INK):
        a = np.asarray(m, np.float32) / 255.0
        if a.max() == 0:
            return
        cov = self._cov(a)
        cell = self._snap(cov)
        if not cell.any():
            return
        # shading: reuse the painter's lighting at full resolution, then average per cell
        amb, kd, ks, sp, bs = MATERIALS[mat]
        col = np.array(color, np.float32)
        if mat in ("flat", "glow"):
            shade = np.broadcast_to(col * dark, cov.shape + (3,)).copy()
        else:
            area = a.sum() / (S * S)
            r = bevel if bevel is not None else max(1.2, min(10.0, math.sqrt(area) * 0.26)) * bs
            hgt = np.asarray(m.filter(ImageFilter.GaussianBlur(r * S)), np.float32) / 255.0
            gy, gx = np.gradient(hgt)
            kk = r * S * 2.2
            n = np.dstack([-gx * kk, -gy * kk, np.ones_like(gx)])
            n /= np.linalg.norm(n, axis=2, keepdims=True)
            dif = np.clip(n @ paint.LIGHT, 0, 1)
            spec = np.clip(n @ paint.HALF, 0, 1) ** sp * ks
            light = (amb + kd * dif) * dark
            lc = self._cov(light * a) / np.maximum(cov, 1e-6)
            sc = self._cov(spec * a) / np.maximum(cov, 1e-6)
            # vertical falloff, then three flat tones per part: shadow / mid / light
            ys = np.nonzero(cell.any(1))[0]
            vg = np.zeros(self.gh, np.float32)
            if len(ys) > 1:
                vg[ys.min():ys.max() + 1] = np.linspace(gradient, -gradient, ys.max() - ys.min() + 1)
            lc = lc + vg[:, None] * dark
            mid = np.median(lc[cell])
            tone = np.where(lc < mid - 0.12, 0.74, np.where(lc > mid + 0.14, 1.18, 0.98))
            shade = col[None, None, :] * (tone * max(0.55, mid) / 0.98 * 1.0)[..., None]
            shade += 255 * np.where(sc > 0.35, 0.22, 0.0)[..., None] * dark
        shade = np.clip(shade, 0, 255)
        lid = {"base": 0, "l1": 1, "l2": 2}[layer]
        # an outline where this part overlaps earlier ones (only for parts big enough
        # to carry one; tiny details and glows stay bare)
        if PART_LINES and outline and mat not in ("flat", "glow") and cell.sum() >= PART_MIN:
            ring = self._ring(cell) & (self.own >= 0) & ~self.fill & ~self.ink
            # only where this part meets something of a clearly different tone or layer
            prev = self.rgb @ LUM
            mine = float(np.median(shade[cell] @ LUM))
            ring &= (np.abs(prev - mine) > PART_CONTRAST) | ((self.own != {"base": 0, "l1": 1, "l2": 2}[layer]) & (self.own > 0))
            self.own[ring], self.ink[ring] = 0, True
            self.rgb[ring] = INK
        self.rgb[cell] = shade[cell]
        self.own[cell] = lid
        self.ink[cell] = False
        self.fill[cell] = mat == "glow"

    def glow(self, m, color, radius=3, strength=0.8, layer="base"):
        a = np.asarray(m.filter(ImageFilter.GaussianBlur(radius * S * 0.6)), np.float32) / 255.0
        cov = self._cov(np.clip(a * 2.0, 0, 1) * strength)
        cell = (cov >= 0.45) & (self.own < 0)
        col = np.array(color, np.float32)
        self.rgb[cell] = col
        self.own[cell] = 0
        self.fill[cell] = True

    def shadow(self, cx, cy, rx, ry, alpha=0.35):
        self.shadows.append((cx, cy, rx, ry))

    # ------------------------------------------------------------ output
    def finish(self, outer_ink=1.0, colors=16, grey_levels=4):
        own, rgb = self.own.copy(), self.rgb.copy()
        solid = own >= 0
        # drop stray single pixels
        p = np.pad(solid, 1)
        n4 = p[:-2, 1:-1].astype(int) + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]
        lone = solid & (n4 == 0)
        own[lone] = -1
        solid = own >= 0
        # palette: base colours snap to a small shared palette, tint layers to a few greys
        base = solid & (own == 0) & ~self.ink
        rgb = _kmeans(rgb, base, colors)
        for i in (1, 2):
            m = own == i
            if m.any():
                g = rgb[m] @ LUM
                lo, hi = 75.0, 245.0
                q = np.round((np.clip(g, lo, hi) - lo) / (hi - lo) * (grey_levels - 1)) / (grey_levels - 1)
                v = lo + q * (hi - lo)
                rgb[m] = np.stack([v, v, v], 1)
        rgb[self.ink & solid] = INK
        # silhouette outline
        sil = self._ring(solid) if outer_ink else np.zeros_like(solid)
        # ground shadow: flat ellipse under the feet, behind the figure
        sh = np.zeros_like(solid)
        if self.shadows:
            yy, xx = np.mgrid[0:self.gh, 0:self.gw]
            for cx, cy, rx, ry in self.shadows:
                cxg, cyg = cx / self.B, cy / self.B
                rxg, ryg = max(2.0, rx / self.B), max(0.9, ry / self.B)
                sh |= ((xx + 0.5 - cxg) / rxg) ** 2 + ((yy + 0.5 - cyg) / ryg) ** 2 <= 1.0
        sh &= ~solid & ~sil
        layers = [np.zeros((self.gh, self.gw, 4), np.uint8) for _ in range(3)]
        for i in range(3):
            m = own == i
            layers[i][m, :3] = np.clip(rgb[m], 0, 255)
            layers[i][m, 3] = 255
        layers[0][sil, :3] = INK
        layers[0][sil, 3] = 255
        layers[0][sh] = SHADOW
        out = []
        for L in layers:
            big = Image.fromarray(L, "RGBA").resize((self.gw * self.B, self.gh * self.B), Image.NEAREST)
            c = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
            c.paste(big, (0, 0))
            out.append(c)
        return out


def _kmeans(rgb, mask, k, iters=10):
    pts = rgb[mask]
    if len(pts) == 0:
        return rgb
    uniq = np.unique(pts.round(), axis=0)
    k = min(k, len(uniq))
    order = np.argsort(pts @ LUM)
    cent = pts[order[np.linspace(0, len(pts) - 1, k).astype(int)]].copy()
    for _ in range(iters):
        lab = ((pts[:, None] - cent[None]) ** 2).sum(-1).argmin(1)
        for j in range(k):
            s = pts[lab == j]
            if len(s):
                cent[j] = s.mean(0)
    lab = ((pts[:, None] - cent[None]) ** 2).sum(-1).argmin(1)
    out = rgb.copy()
    out[mask] = cent[lab]
    return out


# Which look the Human/Orc sprites use: "pixel" (FantasyHex-like) or "painted".
STYLE = "pixel"


def make_canvas(w, h):
    return PixelCanvas(w, h) if STYLE == "pixel" else Canvas(w, h)
