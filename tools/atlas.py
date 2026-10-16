"""Read libGDX .atlas files and crop named regions out of the packed pages."""
from PIL import Image
import os
class Atlas:
    def __init__(self, path):
        self.dir=os.path.dirname(path); self.regions={}; self.pages={}
        page=None; cur=None
        for line in open(path,encoding='utf-8').read().splitlines():
            if not line.strip(): page=None; cur=None; continue
            if page is None: page=line.strip(); continue
            if not line.startswith(' ') and ':' in line and cur is None: continue  # page header props
            if not line.startswith(' '):
                cur={'page':page}; self.regions[line.strip()]=cur; continue
            k,v=line.strip().split(':',1); v=v.strip()
            if cur is not None: cur[k]=v
    def page(self,p):
        if p not in self.pages: self.pages[p]=Image.open(os.path.join(self.dir,p)).convert('RGBA')
        return self.pages[p]
    def crop(self,name):
        r=self.regions[name]; x,y=map(int,r['xy'].split(',')); w,h=map(int,r['size'].split(','))
        im=self.page(r['page']).crop((x,y,x+w,y+h))
        if r.get('rotate')=='true': im=im.rotate(90,expand=True)
        ow,oh=map(int,r.get('orig',r['size']).split(','))
        if (ow,oh)!=(im.width,im.height):
            ox,oy=map(int,r.get('offset','0,0').split(','))
            full=Image.new('RGBA',(ow,oh)); full.paste(im,(ox,oh-oy-im.height)); im=full
        return im
