import sys; sys.path.insert(0,'play'); sys.path.insert(0,'tools')
import collaudit as C
from portlib import gen1_coll
TSN={37:'Cavern',33:'Cemetery',45:'Club',52:'Dojo',34:'Facility',49:'Forest',48:'ForestGate',47:'Gate',44:'House',36:'Interior',42:'Lab',35:'Lobby',50:'Mansion',46:'Museum',40:'Overworld',43:'Plateau',41:'Pokecenter',38:'Ship',39:'ShipPort',51:'Underground'}
PAS={n:set(gen1_coll(n)) for n in set(TSN.values())}
BLOCKED=(0x07,0x90,0xff)
db=C.db; r=C.r
tot={}
for k,m in sorted(db.maps.items()):
    ts=r[m['hdr']+1]
    if ts not in TSN: continue
    c,a=C.cells(k); pas=PAS[TSN[ts]]; A=[];B=[]
    for (x,y),(tl,co,blk) in c.items():
        rp = tl in pas; mp = co == 0 or 0x70 <= co <= 0x7f
        if mp and not rp: A.append((x,y,hex(tl),hex(co)))
        if rp and not mp: B.append((x,y,hex(tl),hex(co)))
    if A or B: print(k, TSN[ts], 'walk-into-wall', len(A), A[:6], '| blocked', len(B), B[:4])
