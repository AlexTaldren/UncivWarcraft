"""Composite layered unit sprites with a nation's colors (as the game does) for previewing."""
import sys, os
from PIL import Image, ImageChops
def tint(im, rgb):
    r,g,b,a = im.split()
    c = Image.new('RGB', im.size, rgb)
    rgbim = ImageChops.multiply(Image.merge('RGB',(r,g,b)), c)
    return Image.merge('RGBA', (*rgbim.split(), a))
def composite(layers, inner, outer):
    base = layers[0].copy()
    for k, lay in enumerate(layers[1:], 1):
        base.alpha_composite(tint(lay, inner if k == 1 else outer))
    return base
def sheet(rows, scale, out, bg=(96,128,72)):
    w = max(sum(im.width for im in r)+10*len(r) for r in rows); h=sum(max(im.height for im in r)+10 for r in rows)
    s = Image.new('RGBA', (w, h), bg+(255,)); y=0
    for r in rows:
        x=0
        for im in r: s.alpha_composite(im, (x, y)); x+=im.width+10
        y+=max(im.height for im in r)+10
    s.resize((s.width*scale, s.height*scale), Image.NEAREST).save(out)
