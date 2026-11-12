import sys, re, collections
sys.path.insert(0,'tools'); sys.path.insert(0,'play')
import portmaps as PM
from mapdb import crystal_names
INV={v:k for k,v in PM.MON.items() if not k.startswith('UNOWN')}
INV[201]='UNOWN'
m=open(sys.argv[1] if len(sys.argv)>1 else 'build/p59.gbc','rb').read()
names=crystal_names()
def fo(b,a): return b*0x4000+a-0x4000
def grass(off):
    out={}; o=off
    while m[o]!=0xff:
        out[(m[o],m[o+1])]=[(m[o+5+2*i],m[o+6+2*i]) for i in range(21)]; o+=47
    return out,o
def water(off):
    out={}; o=off
    while m[o]!=0xff:
        out[(m[o],m[o+1])]=[(m[o+3+2*i],m[o+4+2*i]) for i in range(3)]; o+=9
    return out,o
JG,e=grass(fo(0xA,0x660C)); print('johto grass',len(JG),hex(e))
JW,e=water(fo(0xA,0x7E3F)); print('johto water',len(JW),hex(e))
SG,e=grass(fo(0xA,0x7B89)) if m[fo(0xA,0x7B89)]!=0 else ({},0)
print('swarm @7DDE', m[fo(0xA,0x7DDE):fo(0xA,0x7E3F)].hex())
present=collections.defaultdict(set)
for k,v in JG.items():
    for lv,s in v: present[s].add(names.get(k,str(k)))
for k,v in JW.items():
    for lv,s in v: present[s].add('W:'+names.get(k,str(k)))
gen1=sorted(s for s in present if s<=151)
print('Gen1 in Johto grass/water:', [INV[s] for s in gen1])
print('Gen2 present:', sorted(INV[s] for s in present if s>151))
print('Gen2 missing:', [INV[s] for s in range(152,252) if s not in present])
