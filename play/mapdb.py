"""catalog of the MOD ROM's maps: headers, attributes, events"""
import sys
SC='/tmp/claude-0/-home-claude/e85f874c-51bd-5d2c-9b1a-1d2b8ebf1451/scratchpad'
sys.path.insert(0,SC+'/tools')
from lib import parse_events
def fo(b,a): return b*0x4000+a-0x4000
class DB:
    def __init__(s, path):
        r=s.r=open(path,'rb').read()
        G=[r[0x94000+2*i]|r[0x94001+2*i]<<8 for i in range(26)]
        s.maps={}
        for g in range(26):
            n=(G[g+1]-G[g])//9 if g<25 else 160
            for m in range(1,n+1):
                h=fo(0x25,G[g])+9*(m-1)
                b=r[h]; a=r[h+3]|r[h+4]<<8
                if not (0<b<0x80 and 0x4000<=a<0x8000): continue
                at=r[fo(b,a):fo(b,a)+12]
                eb,ea=at[6],at[9]|at[10]<<8
                if not (0x4000<=ea<0x8000) or at[1]==0 or at[2]==0 or at[1]>80 or at[2]>80: continue
                try: ev=parse_events(r,eb,ea)
                except Exception: continue
                s.maps[(g+1,m)]=dict(hdr=h,bank=b,attr=fo(b,a),h=at[1],w=at[2],scbank=at[6],scripts=at[7]|at[8]<<8,
                    events=ea,conn=at[11],tileset=r[h+1],ev=ev)
    def warps(s,k): return [(w[1],w[0],w[2],w[3],w[4]) for _,w in s.maps[k]['ev']['warps']]   # x,y,idx,g,m
    def objs(s,k): return [o for _,o in s.maps[k]['ev']['objs']]
def crystal_names():
    import re
    from lib import mapid
    names={}
    for l in open(SC+'/ref/pokecrystal/constants/map_constants.asm'):
        m=re.match(r'\s*map_const (\w+),',l)
        if m:
            n=''.join(w.capitalize() for w in m.group(1).split('_'))
            names[n]=m.group(1)
    out={}
    for l in open(SC+'/ref/pokecrystal/pokecrystal.sym'):
        m=re.match(r'\w+:\w+ (\w+)_MapAttributes$',l.strip())
        if m:
            try: out[mapid(m.group(1))]=m.group(1)
            except Exception: pass
    return out
def connections(d,k):
    m=d.maps[k]; o=m['attr']+12; out=[]
    for bit,name in ((3,'N'),(2,'S'),(1,'W'),(0,'E')):
        if m['conn']>>bit&1:
            c=d.r[o:o+12]; out.append((name,(c[0],c[1]))); o+=12
    return out
def reachable(d,start):
    seen={start}; todo=[start]
    while todo:
        k=todo.pop()
        nxt=[(w[3],w[4]) for w in d.warps(k)]+[t for _,t in connections(d,k)]
        for t in nxt:
            if t in d.maps and t not in seen: seen.add(t); todo.append(t)
    return seen
