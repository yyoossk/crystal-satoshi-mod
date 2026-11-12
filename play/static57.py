import sys, re, glob
sys.path.insert(0,'tools')
import build_phase57 as P
import portmaps as PM
INV={}
for k,v in PM.MON.items():
    if not k.startswith('UNOWN_') and v not in INV: INV[v]=k
JN={}
for l in open(glob.glob(P.KIT+'入手のしかた_151.md')[0],encoding='utf-8'):
    m=re.match(r'\| (\d+) \| (\S+) \|',l)
    if m: JN[m.group(2)]=int(m.group(1))
m=open('build/p58.gbc','rb').read()
G={}; o=0x2B140
while m[o]!=0xff: G[(m[o],m[o+1])]=m[o:o+47]; o+=47
W={}; o=0x2BD05
while m[o]!=0xff: W[(m[o],m[o+1])]=m[o:o+9]; o+=9
bad=0
for name,rates,mons in P.kit_grass():
    e=G[P.KIT_MAP[name]]
    if list(e[2:5])!=rates or [(e[5+2*i],e[6+2*i]) for i in range(21)]!=mons: print('MISMATCH',name); bad+=1
for name,rate,mons in P.kit_water():
    e=W[P.KIT_MAP[name]]
    if e[2]!=rate or [(e[3+2*i],e[4+2*i]) for i in range(3)]!=mons: print('WMISMATCH',name); bad+=1
# star species
star={}; cur=None
for l in open(P.KIT+'野生_元のデータ.md',encoding='utf-8'):
    mm=re.match(r'## (\w+)',l)
    if mm: cur=mm.group(1)
    if '★' in l:
        mm=re.search(r'★ (\S+)（(\d+)）',l)
        if mm and cur: star.setdefault(cur,set()).add(int(mm.group(2)))
for name,s in sorted(star.items()):
    mp=P.KIT_MAP[name]; sp=set()
    tods=[set(G[mp][6+2*i] for i in range(t*7,t*7+7)) for t in range(3)] if mp in G else []
    allsp=set().union(*tods) if tods else set()
    if mp in W: allsp|={W[mp][4],W[mp][6],W[mp][8]}
    miss=s-allsp
    print(name, sorted(INV[x] for x in s), 'MISSING' if miss else 'ok', [sorted(INV[x] for x in (s&t)) for t in tods])
    bad+=bool(miss)
print('bad',bad, 'grass maps',len(G),'water',len(W))
