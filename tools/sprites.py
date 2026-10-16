"""Map sprites for the Human unique units, built from Unciv's AbsoluteUnits pixel art.

Each sprite keeps Unciv's 3-layer format (base, inner-color layer, outer-color layer)
so the game still tints it in the owning nation's colors.
"""
import os
from PIL import Image, ImageDraw, ImageFilter
from atlas import Atlas

P = "TileSets/AbsoluteUnits/Units/"


def layers(a, name):
    return [a.crop(P + name + s) for s in ("", "-1", "-2")]


def opaque_box(ims):
    m = Image.new("L", ims[0].size, 0)
    for im in ims:
        m = Image.fromarray(__import__("numpy").maximum(__import__("numpy").array(m),
                                                        __import__("numpy").array(im.split()[3])))
    return m, m.getbbox()


def glow(size, mask, color, radius, strength):
    """Soft colored halo around the opaque pixels of `mask`."""
    g = mask.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(radius))
    g = g.point(lambda v: min(255, int(v * strength)))
    out = Image.new("RGBA", size, color + (0,))
    out.putalpha(g)
    return out


def paladin(a):
    base, l1, l2 = layers(a, "Knight")
    mask, _ = opaque_box([base, l1, l2])
    halo = glow(base.size, mask, (255, 226, 120), 2.2, 1.6)
    new_base = Image.new("RGBA", base.size)
    new_base.alpha_composite(halo)
    new_base.alpha_composite(base)
    # small pixel sparkles of holy light
    d = ImageDraw.Draw(new_base)
    for x, y in ((60, 10), (66, 40)):
        d.point([(x, y), (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)], fill=(255, 245, 190, 255))
    return [new_base, l1, l2]


def mage(a):
    base, l1, l2 = layers(a, "Great Scientist")
    mask, (x0, y0, x1, y1) = opaque_box([base, l1, l2])
    # the scientist's raised arm points right: put a fireball-like arcane orb at its tip
    arr = __import__("numpy").array(mask)
    rows = [y for y in range(y0, y0 + (y1 - y0) // 2) if arr[y].any()]
    hand_y = max(rows[:len(rows)], key=lambda y: arr[y].nonzero()[0].max())
    hand_x = arr[hand_y].nonzero()[0].max()
    cx, cy = hand_x + 4, hand_y - 1
    orb = Image.new("RGBA", base.size)
    od = ImageDraw.Draw(orb)
    od.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(150, 90, 255, 110))
    orb = orb.filter(ImageFilter.GaussianBlur(1.5))
    od = ImageDraw.Draw(orb)
    od.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(185, 140, 255, 255))
    od.ellipse([cx - 2, cy - 2, cx + 1, cy + 1], fill=(235, 220, 255, 255))
    od.point([(cx - 7, cy - 6), (cx + 6, cy - 8), (cx + 8, cy + 4)], fill=(225, 205, 255, 255))
    new_base = base.copy()
    new_base.alpha_composite(orb)
    return [new_base, l1, l2]


def footman(a):
    return layers(a, "Swordsman")


SPRITES = {"Footman": footman, "Paladin": paladin, "Mage": mage}


def write_all(atlas_path, images_dir):
    a = Atlas(atlas_path)
    out = {}
    for name, f in SPRITES.items():
        ls = f(a)
        out[name] = ls
        for suffix, im in zip(("", "-1", "-2"), ls):
            p = os.path.join(images_dir, P, name + suffix + ".png")
            os.makedirs(os.path.dirname(p), exist_ok=True)
            im.save(p)
    return out
