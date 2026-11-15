import sys, re; sys.path.insert(0,'play'); sys.path.insert(0,'tools')
from mapdb import DB, crystal_names
from lib import fo
rom=sys.argv[1]
db=DB(rom); r=db.r; nm=crystal_names()
# crystal item names
cn={}; i=0
for l in open('ref/pokecrystal/constants/item_constants.asm'):
    m=re.match(r'\s*const (\w+)',l)
    if m and 'const_def' not in l: cn[i]=m.group(1); i+=1
def iname(x):
    if 0xBF<=x<=0xF2: return 'TM%02d'%(x-0xBF+1 - (1 if x>0xC3 else 0) - (1 if x>0xDC else 0))
    return cn.get(x,hex(x))
# mart table: locate via Lavender list as phase 41 did -> use pointer table in bank 5
ids=[]
def table():
    import build_phase41 as P41
    return None
def scan(s, depth=0, seen=None):
    out=[]
    for j in range(0,90):
        b=r[s+j]
        if b==0x93 and r[s+j+1]==0: out.append(r[s+j+2]|r[s+j+3]<<8)
        if b==0x04 and depth<2:
            bk=r[s+j+1]; ad=r[s+j+2]|r[s+j+3]<<8
            if 0x4000<=ad<0x8000 and bk<0x80: out+=scan(fo(bk,ad),depth+1)
    return out
TB=None
# Marts pointer table: find pointer to Cherrygrove list; JP Crystal: table in bank 5
for k in sorted(db.maps):
    n=str(nm.get(k))
    m=db.maps[k]
    for o in db.objs(k):
        p=o[9]|o[10]<<8
        if p<0x4000 or o[0]!=0x39 and k[0]!=26 and k!=(15,11) and k!=(16,2): continue
        ms=sorted(set(x for x in scan(fo(m['scbank'],p)) if x<40))
        if ms: print(k, n, (o[2]-4,o[1]-4), ms)
sys.path.insert(0,'tools')
from lib import JP_BASE
orig=open(JP_BASE,'rb').read()
import build_phase15 as P15
ids_=[P15.item_id(n) for n in ('GREAT_BALL','POTION','SUPER_POTION','MAX_REPEL','ANTIDOTE','PARLYZ_HEAL','AWAKENING','BURN_HEAL')]
mo=orig.find(bytes([8]+ids_)); p_=0x4000+mo%0x4000
refs=[i for i in range(0x14000,0x18000-1) if orig[i]==p_&0xFF and orig[i+1]==p_>>8]
table=refs[0]-2*21
print('table', hex(table))
for mid in range(34):
    p=r[table+2*mid]|r[table+2*mid+1]<<8; o=fo(5,p); n=r[o]
    print(mid, [iname(x) for x in r[o+1:o+1+n]])
