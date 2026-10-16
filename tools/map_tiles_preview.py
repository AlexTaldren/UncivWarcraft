"""Render part of the Azeroth map with the actual HexaRealm tile art (and this mod's
tiles), roughly as it looks in game. usage: map_tiles_preview.py <Tilesets.atlas>
<mod_dir> <azeroth.json> <out.png> c0 r0 c1 r1"""
import json, os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from atlas import Atlas
import azeroth as AZ

HR = "TileSets/HexaRealm/Tiles/"


def main(atlas_path, mod, spec, out, c0, r0, c1, r1):
    a = Atlas(atlas_path)
    mod_tiles = os.path.join(mod, "Images.WarcraftMap", HR)
    cache = {}

    def img(name):
        if name not in cache:
            p = os.path.join(mod_tiles, name + ".png")
            if os.path.exists(p):
                cache[name] = Image.open(p).convert("RGBA")
            elif HR + name in a.regions:
                cache[name] = a.crop(HR + name)
            else:
                cache[name] = None
        return cache[name]

    m = json.load(open(spec))
    W, H = m["width"], m["height"]
    land = lambda c, r: m["zones"][r][c] is not None
    sx, sy = 48, 52
    canvas = Image.new("RGBA", ((c1 - c0 + 1) * sx + 20, (r1 - r0 + 2) * sy + 20), (25, 30, 40, 255))
    for r in range(r0, r1 + 1):
        for parity in (1, 0):                       # odd columns sit higher: draw them first
            for c in range(c0, c1 + 1):
                if c % 2 != parity:
                    continue
                t = m["tiles"][r][c]
                base = t["t"]
                if base == "Ocean" and any(land(*q) for q in AZ.neighbors(c, r, W, H)):
                    base = "Coast"
                layers = []
                if t.get("nw"):
                    layers = [t["nw"]]
                else:
                    f = t["f"]
                    if "Hill" in f and img(base + "+Hill") is not None:
                        layers.append(base + "+Hill")
                    else:
                        layers.append(base)
                        if "Hill" in f:
                            layers.append("Hill")
                    letter = {"Grassland": "G", "Plains": "P", "Tundra": "T"}.get(base, "G")
                    for x in f:
                        if x == "Hill":
                            continue
                        name = {"Forest": "Forest" + letter, "Jungle": "Jungle" + ("P" if base == "Plains" else "G")}.get(x, x)
                        layers.append(name)
                x = (c - c0) * sx + 10
                y = (r - r0) * sy + 10 + (0 if c % 2 == 0 else -sy // 2) + sy // 2
                for n in layers:
                    im = img(n)
                    if im is None:
                        continue
                    canvas.alpha_composite(im, (x, y + 56 - im.height))
    canvas.save(out)
    print(out, canvas.size)


if __name__ == "__main__":
    main(*sys.argv[1:5], *map(int, sys.argv[5:9]))
