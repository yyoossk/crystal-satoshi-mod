import sys, re, collections
sys.path.insert(0,'tools'); sys.path.insert(0,'play')
import portmaps as PM
import build_phase60 as P
from lib import fo
INV={v:k for k,v in PM.MON.items() if not k.startswith('UNOWN')}; INV[201]='UNOWN'
m=open(sys.argv[1],'rb').read()
def r16(o): return m[o]|m[o+1]<<8
src=collections.defaultdict(set)
def add(s,w):
    if s: src[s].add(w)
def grass(off,only=None,tag='G'):
    o=fo(P.BA,off)
    while m[o]!=0xff:
        if only is None or (m[o],m[o+1]) in only:
            for i in range(21): add(m[o+6+2*i],tag)
        o+=47
def water(off,only=None):
    o=fo(P.BA,off)
    while m[o]!=0xff:
        if only is None or (m[o],m[o+1]) in only:
            for i in range(3): add(m[o+4+2*i],'W')
        o+=9
grass(P.JOHTO_GRASS); grass(P.SWARM_GRASS,tag='swarm'); grass(P.KANTO_GRASS,P.JOHTO_SIDE); water(P.JOHTO_WATER); water(P.KANTO_WATER,P.JOHTO_SIDE)
tabs=set()
for g in range(P.N_FISH):
    r=fo(P.FISH_BANK,P.FISH_GROUPS)+7*g
    for k in range(3): tabs.add(r16(r+1+2*k))
for t in tabs:
    o=fo(P.FISH_BANK,t)
    while True:
        add(m[o+1],'fish')
        if m[o]==0xff: break
        o+=3
for o in range(fo(P.FISH_BANK,P.TIME_FISH),fo(P.FISH_BANK,P.TIME_FISH_END),2): add(m[o],'fish')
o=P.TREEMONS
while o<P.TREEMONS_END:
    if m[o]==0xff: o+=1; continue
    add(m[o+1],'tree'); o+=3
o=P.CONTEST
while True:
    add(m[o+1],'contest')
    if m[o]==0xff: break
    o+=4
for o,a,b in P.GIFTS: add(m[o+1],'gift')
for o,a,b in P.STATICS: add(m[o+1],'static')
t0=fo(*P.TRADES)
for i in P.JOHTO_TRADES: add(m[t0+16*i+2],'trade')
N=PM.MON
for s in ('TOGEPI','SHUCKLE','TYROGUE','SUDOWOODO','LUGIA','HO_OH','SUICUNE','RAIKOU','ENTEI','WOBBUFFET'): add(N[s],'event')
for s in ('NATU','PHANPY'): add(N[s],'prize')
for s in ('PICHU','CLEFFA','IGGLYBUFF','SMOOCHUM','MAGBY','ELEKID','TYROGUE'): add(N[s],'oddegg')
gen1=[INV[s] for s in src if s<=151]
print('Gen1 in Johto:', gen1)
# evolution closure (pokecrystal evos)
ev=collections.defaultdict(list); cur=None
txt=open('ref/pokecrystal/data/pokemon/evos_attacks.asm').read()
for l in txt.split('\n'):
    mm=re.match(r'(\w+)EvosAttacks:',l)
    if mm: cur=mm.group(1).upper(); continue
    mm=re.match(r'\s*db EVOLVE_\w+,\s*(.*)',l)
    if mm and cur:
        to=mm.group(1).split(',')[-1].strip(); ev[cur].append(to)
NAME={k.replace('_',''):k for k in N}
have=set(src)
changed=True
while changed:
    changed=False
    for s in list(have):
        for t in ev.get(INV[s].replace('_',''),[]):
            t=N.get(NAME.get(t.replace('_',''),t))
            if t and t>151 and t not in have: have.add(t); changed=True
excl={N[x] for x in ('CHIKORITA','BAYLEEF','MEGANIUM','CYNDAQUIL','QUILAVA','TYPHLOSION','TOTODILE','CROCONAW','FERALIGATR','CELEBI',
 'CROBAT','BELLOSSOM','POLITOED','SLOWKING','KINGDRA','STEELIX','SCIZOR','BLISSEY','PORYGON2','ESPEON','UMBREON','PICHU','CLEFFA','IGGLYBUFF','SMOOCHUM','ELEKID','MAGBY')}
miss=[INV[s] for s in range(152,252) if s not in have and s not in excl]
print('Gen2 missing (target):', miss)
print('target covered', len([s for s in range(152,252) if s not in excl and s in have]), '/', 100-len(excl))
for s in range(152,252):
    if s in src: print(INV[s], sorted(src[s]))
