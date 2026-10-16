"""Render the Azeroth map spec as a hex image with zone names, capitals and city-states."""
import json, math, sys
from PIL import Image, ImageDraw, ImageFont

COL = {"Ocean": (38, 72, 120), "Coast": (62, 110, 160), "Lakes": (70, 130, 180),
       "Grassland": (98, 150, 70), "Plains": (170, 165, 90), "Tundra": (140, 140, 120),
       "Desert": (220, 195, 130), "Snow": (235, 240, 245), "Mountain": (105, 95, 90)}
FEAT = {"Forest": (40, 95, 45), "Jungle": (20, 120, 60), "Marsh": (80, 110, 100),
        "Blighted Land": (120, 140, 40), "Oasis": (60, 170, 160), "Ice": (220, 235, 245),
        "Fel-Scorched Land": (110, 235, 60), "Plagued Land": (120, 95, 130), "Ancient Woods": (110, 75, 165),
        "Bamboo Grove": (130, 190, 70), "Molten Fields": (240, 110, 30), "Crystal Grove": (160, 170, 255),
        "Titan Ruins": (200, 200, 190)}


def render(spec, out, s=11, labels=True):
    W, H = spec["width"], spec["height"]
    hw, hh = s * 2, s * math.sqrt(3)
    img = Image.new("RGB", (int(W * hw * .75 + hw), int(H * hh + hh)), (20, 30, 50))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
        bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
    except OSError:
        font = bold = ImageFont.load_default()

    def cxy(c, r):
        return (c * hw * .75 + hw / 2, (r - .5 * (c % 2)) * hh + hh)

    for r in range(H):
        for c in range(W):
            t = spec["tiles"][r][c]
            x, y = cxy(c, r)
            pts = [(x + s * math.cos(math.radians(a)), y + s * math.sin(math.radians(a))) for a in range(0, 360, 60)]
            col = COL.get(t["t"], (255, 0, 255))
            d.polygon(pts, fill=col, outline=(0, 0, 0))
            for f in t["f"]:
                if f == "Hill":
                    d.polygon([(x - 5, y + 4), (x, y - 3), (x + 5, y + 4)], outline=(60, 50, 40))
                elif f in FEAT:
                    d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=FEAT[f])
            if t.get("nw"):
                d.regular_polygon((x, y, 7), 4, fill=(255, 120, 200))
    if labels:
        # zone labels at the centroid of their tiles
        acc = {}
        for r in range(H):
            for c in range(W):
                z = spec["zones"][r][c]
                if z:
                    a = acc.setdefault(z, [0, 0, 0]); x, y = cxy(c, r); a[0] += x; a[1] += y; a[2] += 1
        for z, (sx, sy, n) in acc.items():
            tw = d.textlength(z, font=font)
            d.text((sx / n - tw / 2, sy / n - 6), z, fill=(255, 255, 255), font=font,
                   stroke_width=2, stroke_fill=(0, 0, 0))
        for group, colr in (("capitals", (255, 215, 0)), ("cityStates", (120, 230, 255))):
            for name, (c, r) in spec[group].items():
                x, y = cxy(c, r)
                d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=colr, outline=(0, 0, 0), width=2)
                d.text((x + 8, y + 2), name, fill=colr, font=bold, stroke_width=2, stroke_fill=(0, 0, 0))
    img.save(out)


if __name__ == "__main__":
    render(json.load(open(sys.argv[1])), sys.argv[2])


def from_saved(map_path, spec_json):
    """Rebuild a renderable spec from the real saved Unciv map (coasts, rivers, resources included)."""
    import base64, gzip
    raw = open(map_path).read().strip()
    d = json.loads(gzip.decompress(base64.b64decode(raw)).decode())
    spec = json.load(open(spec_json))
    W, H = spec["width"], spec["height"]
    tiles = [[None] * W for _ in range(H)]
    rivers, res = [], {}
    for t in d["tileList"]:
        pos = t.get("position", {}); x, y = pos.get("x", 0), pos.get("y", 0)
        col, two = y - x, x + y
        row = (two - (1 if abs(col) % 2 == 1 else 0)) // 2
        c, r = col + W // 2, (H - 1) // 2 - row
        tiles[r][c] = {"t": t["baseTerrain"], "f": t.get("terrainFeatures", []),
                       "nw": t.get("naturalWonder", ""), "res": t.get("resource"),
                       "imp": t.get("improvement")}
        for k, side in (("hasBottomRiver", "B"), ("hasBottomLeftRiver", "BL"), ("hasBottomRightRiver", "BR")):
            if t.get(k):
                rivers.append((c, r, side))
    spec["tiles"] = tiles
    spec["rivers"] = rivers
    return spec


def render_saved(map_path, spec_json, out, ruleset_dir):
    spec = from_saved(map_path, spec_json)
    kinds = {r["name"]: r.get("resourceType", "Bonus")
             for r in json.load(open(f"{ruleset_dir}/TileResources.json"))}
    render(spec, out)
    img = Image.open(out); d = ImageDraw.Draw(img)
    s = 11; hw, hh = s * 2, s * math.sqrt(3)
    def cxy(c, r): return (c * hw * .75 + hw / 2, (r - .5 * (c % 2)) * hh + hh)
    # rivers run along the lower edges of a tile
    for c, r, side in spec["rivers"]:
        x, y = cxy(c, r)
        a, b = {"B": (60, 120), "BL": (120, 180), "BR": (0, 60)}[side]
        p1 = (x + s * math.cos(math.radians(a)), y + s * math.sin(math.radians(a)))
        p2 = (x + s * math.cos(math.radians(b)), y + s * math.sin(math.radians(b)))
        d.line([p1, p2], fill=(80, 170, 255), width=3)
    colors = {"Strategic": (230, 60, 60), "Luxury": (190, 90, 230), "Bonus": (250, 230, 90)}
    for r, row in enumerate(spec["tiles"]):
        for c, t in enumerate(row):
            x, y = cxy(c, r)
            if t.get("res"):
                d.rectangle([x + 2, y - 7, x + 6, y - 3], fill=colors[kinds.get(t["res"], "Bonus")], outline=(0, 0, 0))
            if t.get("imp") == "Ancient ruins":
                d.text((x - 3, y - 6), "?", fill=(255, 255, 255))
    img.save(out)
