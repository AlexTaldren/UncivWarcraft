"""Preview sheet of race sprite variants (rows = races, columns = units)."""
import sys
sys.path.insert(0, '/root/build')
from atlas import Atlas
import race_sprites as RS, wc_factions as F
from sprites_preview import composite, sheet

def main(atlas, out, races, units, scale=4):
    a = Atlas(atlas)
    col = {n["name"]: (tuple(n["innerColor"]), tuple(n["outerColor"])) for n in F.NATIONS}
    rows = []
    for r in races:
        row = []
        for u in units:
            ls = [a.crop(RS.P + u + s) for s in ("", "-1", "-2")]
            if r != "Humans":
                ls = RS.make(ls, r, u)
            im = composite(ls, *col[r]); bb = im.getbbox()
            row.append(im.crop((bb[0] - 3, 0, bb[2] + 3, im.height)))
        rows.append(row)
    sheet(rows, scale, out)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3].split(","), sys.argv[4].split(","))
