"""Parse Unciv's relaxed JSON (comments, trailing commas)."""
import json, re
def clean(s):
    out=[];i=0;n=len(s);ins=False
    while i<n:
        c=s[i]
        if ins:
            out.append(c)
            if c=='\\': out.append(s[i+1]); i+=2; continue
            if c=='"': ins=False
            i+=1; continue
        if c=='"': ins=True; out.append(c); i+=1; continue
        if s.startswith('//',i):
            j=s.find('\n',i); i=n if j<0 else j; continue
        if s.startswith('/*',i):
            j=s.find('*/',i); i=n if j<0 else j+2; continue
        out.append(c); i+=1
    t=''.join(out)
    t=re.sub(r',(\s*[\]}])',r'\1',t)
    return t
def load(path):
    return json.loads(clean(open(path,encoding='utf-8').read()))
def dump(obj,path):
    with open(path,'w',encoding='utf-8') as f:
        json.dump(obj,f,indent=2,ensure_ascii=False); f.write('\n')
