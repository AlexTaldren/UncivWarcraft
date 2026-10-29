"""FantasyHex copies of the race improvements (content pass, Oct 2026).

race_works and race_improvements draw each race's camps, forts, mines, quarries, pastures,
plantations, trading posts, lumber mills and fishing boats for HexaRealm (64 x 56). FantasyHex
tiles are 32 x 28 and draw the resource and the improvement as separate layers, so only the
plain "<improvement>-<race>" images are needed. Each is reduced 2:1 by taking the commonest
colour of every 2 x 2 block (so outlines and highlights survive instead of blurring), then
given a fresh dark outline.
"""
import os
from collections import Counter
from PIL import Image

HR = "TileSets/HexaRealm/Tiles/"
FH = "TileSets/FantasyHex/Tiles/"
IMPROVEMENTS = ["Camp", "Fort", "Mine", "Quarry", "Pasture", "Plantation", "Trading post", "Lumber mill",
                "Fishing Boats"]
DARK = (30, 24, 22, 255)


def reduce(im):
    im = im.convert("RGBA")
    w, h = im.size
    src = im.load()
    out = Image.new("RGBA", (w // 2, h // 2))
    px = out.load()
    for y in range(h // 2):
        for x in range(w // 2):
            cols = [src[2 * x + dx, 2 * y + dy] for dx in (0, 1) for dy in (0, 1)]
            solid = [c[:3] for c in cols if c[3] > 128]
            if len(solid) >= 2:
                # prefer non-outline colours so thin bright details are kept
                light = [c for c in solid if sum(c) > 120]
                px[x, y] = Counter(light or solid).most_common(1)[0][0] + (255,)
    # re-outline: transparent pixels touching the figure turn dark
    edge = []
    for y in range(out.height):
        for x in range(out.width):
            if px[x, y][3]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < out.width and 0 <= ny < out.height and px[nx, ny][3] and sum(px[nx, ny][:3]) > 120:
                    edge.append((x, y)); break
    for x, y in edge:
        px[x, y] = DARK
    return out


def write_all(images_dir, races):
    n = 0
    for imp in IMPROVEMENTS:
        for race in races:
            src = os.path.join(images_dir, HR, "%s-%s.png" % (imp, race))
            if not os.path.exists(src):
                continue
            dst = os.path.join(images_dir, FH, "%s-%s.png" % (imp, race))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            reduce(Image.open(src)).save(dst)
            n += 1
    return n
