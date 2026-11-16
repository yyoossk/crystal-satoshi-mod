import sys,re,glob,os; sys.path.insert(0,'play'); sys.path.insert(0,'tools')
from mapdb import DB, crystal_names
from lib import attrs
import portmaps as PM
db=DB('build/p110.gbc'); nm=crystal_names(); r=db.r
PR='ref/pokered'
dims={}
for l in open(PR+'/constants/map_constants.asm'):
    m=re.match(r'\s*map_const (\w+),\s*(\d+),\s*(\d+)',l)
    if m: dims[m.group(1)]=(int(m.group(2)),int(m.group(3)))
def camel(c): return ''.join(p.capitalize() if not p.isdigit() else p for p in c.split('_'))
red={}
for f in glob.glob(PR+'/data/maps/objects/*.asm'):
    name=os.path.basename(f)[:-4]; t=open(f).read()
    ws=tuple((int(a),int(b)) for a,b in re.findall(r'warp_event\s+(\d+),\s*(\d+)',t))
    os_=re.findall(r'object_event\s+(\d+),\s*(\d+),\s*(\w+),\s*(\w+),\s*(\w+)',t)
    red[name]=(ws,os_)
redn={}
for c,(w,h) in dims.items():
    for name in red:
        if name.upper()==c.replace('_',''): redn[name]=(w,h)
out=[]
for k in sorted(db.maps):
    a=attrs(r,db.maps[k]['hdr']); ws=tuple((w[0],w[1]) for w in db.warps(k))
    cand=[n for n,(rw,ro) in red.items() if rw==ws and redn.get(n)==(a['w'],a['h'])]
    if nm.get(k) in red: cand=[nm[k]]
    if len(cand)!=1: continue
    n=cand[0]; ro=red[n][1]; mo=db.objs(k)
    # match by position
    mpos={(o[2]-4,o[1]-4):o for o in mo}
    for x,y,spr,mv,face in ro:
        o=mpos.get((int(x),int(y)))
        exp=PM.SPR.get(spr)
        if o is None: out.append((k,n,(x,y),spr,'missing/moved')); continue
        if exp is not None and o[0]!=exp: out.append((k,n,(x,y),spr,'MOD %02x expect %02x'%(o[0],exp)))
        if exp is None: out.append((k,n,(x,y),spr,'no map, MOD %02x'%o[0]))
for l in out: print(l)
print(len(out))
from collections import defaultdict
use=defaultdict(lambda: defaultdict(list))
for k in sorted(db.maps):
    a=attrs(r,db.maps[k]['hdr']); ws=tuple((w[0],w[1]) for w in db.warps(k))
    cand=[n for n,(rw,ro) in red.items() if rw==ws and redn.get(n)==(a['w'],a['h'])]
    if nm.get(k) in red: cand=[nm[k]]
    if len(cand)!=1: continue
    mpos={(o[2]-4,o[1]-4):o for o in db.objs(k)}
    for x,y,spr,mv,face in red[cand[0]][1]:
        o=mpos.get((int(x),int(y)))
        if o: use[spr][o[0]].append(cand[0])
print('---- inconsistent')
for spr,d in sorted(use.items()):
    if len(d)>1: print(spr, {hex(k):v[:4] for k,v in d.items()})
