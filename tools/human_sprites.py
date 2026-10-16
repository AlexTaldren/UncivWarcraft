"""Map sprites for the Humans, built from Unciv's AbsoluteUnits pixel art plus pixel
shapes drawn in code.

  Mage      a robed battle-mage with a crystal-topped staff (from the Great Prophet)
  Paladin   heavy plate, warhammer, on a barded charger, haloed in holy light
  Footman   a big heater shield in the nation's colours with a sunburst emblem
  Priest    white-and-gold robes with a soft holy glow (from the Missionary)
  Archmage  the robed scholar with an arcane orb (from the Great Scientist)
  Steam Tank            a riveted steam-driven war wagon
  Kul Tiran Man-o'-War  the frigate under striped sails
  "<Unit>-Humans"       every other unit in blue and gold cloth; the Peasant carries lumber

Each sprite keeps Unciv's 3-layer format: base, "-1" (tinted with the nation's inner
colour, gold for the Humans) and "-2" (outer colour, blue).
"""
import colorsys, os
from PIL import Image, ImageDraw, ImageFilter
import mounts
from mounts import Paint, shade

P = "TileSets/AbsoluteUnits/Units/"
OUTLINE = (30, 24, 22, 255)


def layers(a, name):
    return [a.crop(P + name + s) for s in ("", "-1", "-2")]


def bbox_all(ls):
    bs = [l.getbbox() for l in ls if l.getbbox()]
    return min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)


def shift(ls, dx, dy=0):
    out = []
    for l in ls:
        c = Image.new("RGBA", l.size)
        c.alpha_composite(l, (dx, dy)) if dx >= 0 and dy >= 0 else c.paste(l, (dx, dy), l)
        out.append(c)
    return out


def hsv(p):
    return colorsys.rgb_to_hsv(p[0] / 255, p[1] / 255, p[2] / 255)


def ramp_color(v, dark, light):
    t = max(0.0, min(1.0, v))
    return tuple(int(dark[i] + (light[i] - dark[i]) * t) for i in range(3))


def glow(size, mask, color, radius, strength):
    g = mask.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(radius))
    g = g.point(lambda v: min(255, int(v * strength)))
    out = Image.new("RGBA", size, color + (0,))
    out.putalpha(g)
    return out


def alpha_mask(ls, solid=0):
    """Opaque pixels of all layers; solid=200 leaves out the soft ground shadow."""
    m = Image.new("L", ls[0].size, 0)
    for l in ls:
        m.paste(255, mask=l.split()[3].point(lambda v: 255 if v > solid else 0))
    return m


def with_halo(ls, color, radius=2.0, strength=1.4):
    base = Image.new("RGBA", ls[0].size)
    base.alpha_composite(glow(ls[0].size, alpha_mask(ls, 200), color, radius, strength))
    base.alpha_composite(ls[0])
    return [base] + ls[1:]


def outline_into(base, drawn):
    """Dark outline around the opaque pixels of `drawn` (where base is empty)."""
    bp, dp = base.load(), drawn.load()
    w, h = base.size
    for y in range(h):
        for x in range(w):
            if dp[x, y][3] or bp[x, y][3] > 200:
                continue
            if any(0 <= x + dx < w and 0 <= y + dy < h and dp[x + dx, y + dy][3]
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                bp[x, y] = OUTLINE


def clear_overlays(ls, drawn):
    """Faction-colour layers sit on top of the base: clear them where we drew."""
    dp = drawn.load()
    for l in ls[1:]:
        lp = l.load()
        for y in range(l.height):
            for x in range(l.width):
                if dp[x, y][3]:
                    lp[x, y] = (0, 0, 0, 0)


def stamp(ls, base_part=None, l1=None, l2=None, outline=True):
    """Draw new pixels: base_part goes in the base layer, l1/l2 in the tint layers."""
    drawn = Image.new("RGBA", ls[0].size)
    for part in (base_part, l1, l2):
        if part is not None:
            drawn.alpha_composite(part)
    if outline:
        outline_into(ls[0], drawn)
    clear_overlays(ls, drawn)
    for part, target in ((base_part, 0), (l1, 1), (l2, 2)):
        if part is None:
            continue
        ls[0].alpha_composite(part if target == 0 else part)
        if target:
            ls[target].alpha_composite(part)
    return ls


# ------------------------------------------------------------------ Human cloth
BLUE = ((22, 42, 105), (95, 135, 215))
GOLD = ((150, 105, 30), (250, 215, 110))


def human_cloth(im, region=None, gold=True):
    """Re-dye coloured cloth blue (yellows become gold); skin, leather, metal stay."""
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            p = px[x, y]
            if p[3] < 200 or (region and not region(x, y)):
                continue
            h, s, v = hsv(p)
            if s < 0.28 or v < 0.18:
                continue                                  # metal, white, black
            if 0.02 <= h <= 0.105:
                continue                                  # skin, leather, wood
            if 0.105 < h <= 0.18:
                c = ramp_color((v - 0.3) / 0.6, *GOLD)
                if not gold or s < 0.45:
                    continue                              # parchment, dun horses
            elif 0.5 <= h <= 0.72:
                continue                                  # already blue
            else:
                c = ramp_color((v - 0.2) / 0.65, *BLUE)
            px[x, y] = c + (p[3],)
    return im


def lumber(ls):
    """A bundle of logs carried on the back (left of the figure)."""
    x0, y0, x1, y1 = bbox_all(ls)
    part = Image.new("RGBA", ls[0].size)
    d = part.load()
    bark, end = (110, 72, 40), (205, 165, 110)
    top = y0 + (y1 - y0) // 4
    for i in range(3):                                    # three logs, diagonal
        for t in range(10):
            x, y = x0 - 2 + i * 2 + t // 3, top + i * 2 + t
            for dx in range(2):
                if 0 <= x + dx < part.width:
                    d[x + dx, y] = (shade(bark, 1.2 if dx == 0 else 0.85)) + (255,)
        d[x0 - 2 + i * 2, top + i * 2] = end + (255,)
        d[x0 - 1 + i * 2, top + i * 2] = end + (255,)
    # behind the figure: only where the figure is not
    fig = alpha_mask(ls)
    fp = fig.load()
    for y in range(part.height):
        for x in range(part.width):
            if fp[x, y]:
                d[x, y] = (0, 0, 0, 0)
    return stamp(ls, part)


def human_variant(ls, src):
    import race_sprites as RS
    out = [human_cloth(ls[0].copy(), gold=src not in RS.MOUNTED), ls[1].copy(), ls[2].copy()]
    if src == "Worker":
        out = lumber(out)
    return out


# ------------------------------------------------------------------ unique units
def mage(a):
    """A battle-mage: the robed Great Prophet moved to the military side of the tile,
    with blue-violet robes, brown hair and a staff topped by a glowing crystal."""
    ls = layers(a, "Great Prophet")
    x0, y0, x1, y1 = bbox_all(ls)
    tx0, _, tx1, ty1 = bbox_all(layers(a, "Crossbowman"))
    ls = shift(ls, (tx0 + tx1) // 2 - (x0 + x1) // 2, ty1 - y1)
    x0, y0, x1, y1 = bbox_all(ls)
    px = ls[0].load()
    hair_line = y0 + int((y1 - y0) * 0.24)
    staff_top = None
    for y in range(y0, y1):
        for x in range(x0, x1):
            p = px[x, y]
            if p[3] < 200:
                continue
            h, s, v = hsv(p)
            if s < 0.2 and v > 0.62:                      # white cloth / white hair
                if y <= hair_line:
                    px[x, y] = ramp_color((v - 0.6) / 0.4, (60, 40, 25), (125, 85, 50)) + (255,)
                else:
                    px[x, y] = ramp_color((v - 0.6) / 0.4, (35, 35, 105), (95, 95, 205)) + (255,)
            if 0.02 <= h <= 0.11 and s > 0.4 and v < 0.45 and x > (x0 + x1) // 2 + 4:
                if staff_top is None or y < staff_top[1]:
                    staff_top = (x, y)                    # the staff's tip (dark wood, right)
    # crystal + arcane glow on the staff
    cx, cy = staff_top if staff_top else (x1, y0)
    orb = Image.new("RGBA", ls[0].size)
    od = ImageDraw.Draw(orb)
    od.ellipse([cx - 5, cy - 7, cx + 5, cy + 3], fill=(120, 200, 255, 110))
    orb = orb.filter(ImageFilter.GaussianBlur(1.4))
    od = ImageDraw.Draw(orb)
    od.polygon([(cx, cy - 5), (cx + 2, cy - 2), (cx, cy + 1), (cx - 2, cy - 2)], fill=(150, 225, 255, 255))
    od.point([(cx, cy - 3), (cx - 1, cy - 2)], fill=(245, 255, 255, 255))
    od.point([(cx - 5, cy - 6), (cx + 5, cy - 8), (cx + 6, cy + 1)], fill=(200, 240, 255, 255))
    ls[0].alpha_composite(orb)
    clear_overlays(ls, orb)
    return ls


def archmage(a):
    """The Great Scientist (robe in the nation's colour) with an arcane orb at his hand."""
    ls = layers(a, "Great Scientist")
    mask = alpha_mask(ls)
    x0, y0, x1, y1 = mask.getbbox()
    m = mask.load()
    rows = [y for y in range(y0, y0 + (y1 - y0) // 2) if any(m[x, y] for x in range(x0, x1))]
    hand_y = max(rows, key=lambda y: max(x for x in range(x0, x1) if m[x, y]))
    hand_x = max(x for x in range(x0, x1) if m[x, hand_y])
    cx, cy = hand_x + 4, hand_y - 1
    orb = Image.new("RGBA", ls[0].size)
    od = ImageDraw.Draw(orb)
    od.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(150, 90, 255, 110))
    orb = orb.filter(ImageFilter.GaussianBlur(1.5))
    od = ImageDraw.Draw(orb)
    od.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(185, 140, 255, 255))
    od.ellipse([cx - 2, cy - 2, cx + 1, cy + 1], fill=(235, 220, 255, 255))
    od.point([(cx - 7, cy - 6), (cx + 6, cy - 8), (cx + 8, cy + 4)], fill=(225, 205, 255, 255))
    ls[0].alpha_composite(orb)
    return ls


def priest(a):
    """The Missionary in white robes with gold trim and a soft glow of the Light."""
    ls = layers(a, "Missionary")
    x0, y0, x1, y1 = bbox_all(ls)
    px = ls[0].load()
    neck = y0 + int((y1 - y0) * 0.22)
    feet = y1 - 4
    for y in range(neck, feet):
        for x in range(x0, x1):
            p = px[x, y]
            if p[3] < 200:
                continue
            h, s, v = hsv(p)
            if 0.0 <= h <= 0.12 and 0.15 <= s <= 0.75 and v < 0.62:     # brown robe
                px[x, y] = ramp_color((v - 0.12) / 0.45, (165, 160, 150), (250, 248, 240)) + (255,)
    # a gold sash down the front
    cx = (x0 + x1) // 2
    for y in range(neck + 2, feet - 2):
        if px[cx, y][3] > 200:
            px[cx, y] = (230, 190, 80, 255)
    return with_halo(ls, (255, 235, 150), 1.8, 1.1)


def footman(a):
    """Swordsman with a large heater shield: blue face, gold rim and sunburst."""
    ls = layers(a, "Swordsman")
    x0, y0, x1, y1 = bbox_all(ls)
    # the original round-topped shield is on the left of the figure
    sx0, sy0 = x0 - 1, y0 + 7
    wd, ht = 12, 19
    face, rim = Image.new("RGBA", ls[0].size), Image.new("RGBA", ls[0].size)
    fd, rd = ImageDraw.Draw(face), ImageDraw.Draw(rim)
    shape = [(sx0, sy0), (sx0 + wd, sy0), (sx0 + wd, sy0 + ht * 0.55), (sx0 + wd / 2, sy0 + ht),
             (sx0, sy0 + ht * 0.55)]
    rd.polygon(shape, fill=(235, 235, 235, 255))
    inner = [(sx0 + 1.5, sy0 + 1.5), (sx0 + wd - 1.5, sy0 + 1.5), (sx0 + wd - 1.5, sy0 + ht * 0.53),
             (sx0 + wd / 2, sy0 + ht - 2), (sx0 + 1.5, sy0 + ht * 0.53)]
    fd.polygon(inner, fill=(200, 200, 200, 255))
    # light from the upper left on the face
    fp = face.load()
    for y in range(face.height):
        for x in range(face.width):
            if fp[x, y][3] and (x - sx0) + (y - sy0) < 7:
                fp[x, y] = (235, 235, 235, 255)
    # sunburst emblem in the rim colour
    ex, ey = int(sx0 + wd / 2), int(sy0 + ht * 0.4)
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (2, 2), (-2, 2), (2, -2), (-2, -2),
                   (0, 3), (0, -3), (3, 0), (-3, 0)):
        rd.point((ex + dx, ey + dy), fill=(255, 255, 255, 255))
        fp[ex + dx, ey + dy] = (0, 0, 0, 0)
    return stamp(ls, None, l1=rim, l2=face)


def paladin(a, canvas, ground, center):
    """Plate-armoured rider with a warhammer on a barded white charger, in holy light."""
    import race_sprites as RS
    rider = layers(a, "Longswordsman")
    rider = RS.reshape(rider, 1.12, 1.0)                  # broader, heavier
    x0, y0, x1, y1 = bbox_all(rider)
    px = rider[0].load()
    head_c = (x0 + x1) // 2
    # remove the upright longsword (pale blue blade right of the head, upper body)
    blade = []
    for y in range(y0, y0 + int((y1 - y0) * 0.5)):
        for x in range(head_c + 3, x1):
            p = px[x, y]
            if p[3] > 0:
                h, s, v = hsv(p)
                if (0.5 <= h <= 0.7 and v > 0.45) or (v > 0.85 and s < 0.15) or y < y0 + 6:
                    blade.append((x, y))
    for l in rider:
        lp = l.load()
        for x, y in blade:
            lp[x, y] = (0, 0, 0, 0)
    hx = max(x for x, _ in blade) if blade else x1 - 3
    hy = max(y for _, y in blade) if blade else y0 + 20
    # warhammer: wooden haft rising from the hand, a heavy steel head with gold bands
    ham = Image.new("RGBA", rider[0].size)
    hd = ImageDraw.Draw(ham)
    top = hy - 17
    hd.line([(hx - 1, hy + 1), (hx - 1, top)], fill=(110, 75, 45, 255), width=2)
    hd.rectangle([hx - 5, top - 4, hx + 3, top + 1], fill=(170, 175, 190, 255))
    hd.rectangle([hx - 5, top - 4, hx + 3, top - 3], fill=(215, 220, 230, 255))
    hd.line([(hx - 2, top - 4), (hx - 2, top + 1)], fill=(230, 190, 70, 255))
    hd.line([(hx, top - 4), (hx, top + 1)], fill=(230, 190, 70, 255))
    hd.rectangle([hx - 2, top - 6, hx, top - 5], fill=(230, 190, 70, 255))
    rider = stamp(rider, ham)
    # gold trim on the plate: brighten the plate's edge highlights into gold
    px = rider[0].load()
    for y in range(y0, y1):
        for x in range(x0, x1):
            p = px[x, y]
            if p[3] > 200:
                h, s, v = hsv(p)
                if s < 0.2 and 0.55 < v < 0.62 and (x + y) % 3 == 0:
                    px[x, y] = (215, 175, 70, 255)
    out = mounts.compose(rider, "Humans", 0, True, canvas, ground, center, mount=paladin_horse)
    out = with_halo(out, (255, 226, 120), 2.2, 1.3)
    d = ImageDraw.Draw(out[0])
    bb = out[0].getbbox()
    for x, y in ((bb[0] + 6, bb[1] + 8), (bb[2] - 4, bb[1] + 24)):
        d.point([(x, y), (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)], fill=(255, 245, 190, 255))
    return out


def paladin_horse(p, v, armored):
    """A white charger in full barding: blue caparison (outer colour) with gold trim."""
    seat = mounts.horse(p, v, False, (232, 228, 220), (200, 190, 170))
    # caparison over the body, down to the knees
    p.poly([(21, 17), (40, 17), (42, 30), (19, 30)], (225, 225, 225), "capar", layer=2)
    p.line(19, 30, 42, 30, 1, (225, 225, 225), "trim", layer=1)
    p.line(21, 17, 40, 17, 1, (225, 225, 225), "trim2", layer=1)
    p.poly([(15, 9), (8, 12), (9, 14), (15, 12)], mounts.METAL, "chanfron")
    p.line(14, 6, 15, 9, 1, mounts.GOLD, "plume")
    mounts.blanket(p, 30, 15, 10, 4)
    return seat


def steam_tank(size, ground, right):
    """A riveted steam wagon: three iron wheels, armoured hull in the nation's colour,
    a smokestack and a short cannon, facing right."""
    w, h = size
    p = Paint(w, h)
    gy = ground
    rx = right
    iron, dark = (95, 98, 108), (55, 56, 62)
    for i, cx in enumerate((rx - 26, rx - 16, rx - 6)):            # wheels
        p.ell(cx, gy - 5, 5, 5, dark, "wheel%d" % i)
        p.ell(cx, gy - 5, 2, 2, iron, "hub%d" % i)
        p.dot(cx, gy - 5, mounts.GOLD, "hub%d" % i)
    p.poly([(rx - 31, gy - 9), (rx - 1, gy - 9), (rx + 1, gy - 18), (rx - 4, gy - 23),
            (rx - 28, gy - 23), (rx - 32, gy - 17)], (220, 220, 220), "hull", layer=2)
    p.line(rx - 31, gy - 9, rx - 1, gy - 9, 2, iron, "skirt")
    p.line(rx - 28, gy - 23, rx - 4, gy - 23, 1, (225, 225, 225), "trim", layer=1)
    for x in range(rx - 27, rx - 3, 4):                           # rivets
        p.dot(x, gy - 13, (235, 235, 240), "rivet")
    p.poly([(rx - 22, gy - 23), (rx - 10, gy - 23), (rx - 11, gy - 29), (rx - 21, gy - 29)],
           iron, "cab")
    p.dot(rx - 18, gy - 26, (255, 220, 120), "port")
    p.dot(rx - 14, gy - 26, (255, 220, 120), "port")
    p.line(rx - 3, gy - 18, rx + 6, gy - 20, 3, dark, "barrel")
    p.line(rx - 26, gy - 23, rx - 26, gy - 32, 3, dark, "stack")
    p.ell(rx - 27, gy - 35, 2.5, 2, (170, 170, 170), "smoke")
    p.ell(rx - 30, gy - 39, 3, 2.5, (200, 200, 200), "smoke2")
    return list(p.render())


def kul_tiran(a):
    """The frigate under sails striped in the nation's colour."""
    ls = layers(a, "Frigate")
    px = ls[0].load()
    stripe = Image.new("RGBA", ls[0].size)
    sp = stripe.load()
    for y in range(ls[0].height):
        for x in range(ls[0].width):
            p = px[x, y]
            if p[3] > 200:
                h, s, v = hsv(p)
                if v > 0.72 and s < 0.25 and (y // 4) % 3 == 0:       # pale canvas
                    g = int(170 + 80 * (v - 0.72) / 0.28)
                    sp[x, y] = (g, g, g, 255)
    clear_overlays(ls, stripe)
    ls[2].alpha_composite(stripe)
    ls[0].alpha_composite(stripe)
    return ls


# ------------------------------------------------------------------ writing
def write_all(atlas_path, images_dir, race_dir, renames, eras):
    """Unique-unit sprites go in images_dir (the WarcraftMap pack); the blue-and-gold
    "<Unit>-Humans" variants go in race_dir (the RaceUnits pack)."""
    from atlas import Atlas
    import race_sprites as RS
    a = Atlas(atlas_path)

    def save(d, name, ls):
        for s, im in zip(("", "-1", "-2"), ls):
            path = os.path.join(d, P, name + s + ".png")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            im.save(path)

    kn = layers(a, "Knight")
    w, h = kn[0].size
    bb = kn[0].getbbox()
    canvas = (95, round(h * 95 / w))
    save(images_dir, "Footman", footman(a))
    save(images_dir, "Mage", mage(a))
    save(images_dir, "Priest", priest(a))
    save(images_dir, "Archmage", archmage(a))
    save(images_dir, "Paladin", paladin(a, canvas, round(bb[3] / h * canvas[1]),
                                        (bb[0] + bb[2]) / 2 / w * 95))
    cn = layers(a, "Cannon")[0]
    save(images_dir, "Steam Tank", steam_tank(cn.size, cn.getbbox()[3] - 1, cn.width - 8))
    save(images_dir, "Kul Tiran Man-o'-War", kul_tiran(a))

    count = 0
    for src in RS.FOOT + RS.MOUNTED + RS.CREW:
        new = renames.get(src, src)
        variants = [""] + [r[len(P + src):] for r in a.regions
                           if r.startswith(P + src + "-") and r.endswith(" era")
                           and r[len(P + src):].count("-") == 1]
        for v in variants:
            era = "-" + eras.get(v[1:], v[1:]) if v else ""
            import late_units
            if not v and late_units.is_dressed(src):
                out = late_units.source_layers(a, src, lambda ls, b: human_variant(ls, b))
            else:
                out = human_variant(late_units.source_layers(a, src) if not v else layers(a, src + v), src)
            save(race_dir, f"{new}-Humans{era}", out)
            count += 3
    return count
