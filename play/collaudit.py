import sys; sys.path.insert(0,'play'); sys.path.insert(0,'tools')
from bot import *
from mapdb import DB
from lib import attrs, fo
import portmaps as PM
from portlib import Space, gen1_coll
db=DB(SC+'/build/p110.gbc'); r=db.r
TS=PM.Tilesets(bytearray(r),Space(bytearray(r)))
def cells(k):
    h=db.maps[k]['hdr']; a=attrs(r,h); ts=r[h+1]
    e=TS.entry(ts); mo=fo(e[3],e[4]|e[5]<<8); co=TS.coll_off(ts)
    bo=fo(a['blkbank'],a['blk'])
    out={}
    for y in range(a['h']*2):
        for x in range(a['w']*2):
            b=r[bo+(y//2)*a['w']+x//2]; q=(y%2)*2+x%2
            tl=r[mo+16*b+(2*(q//2)+1)*4+2*(q%2)]
            out[(x,y)]=(tl, r[co+4*b+q], b)
    return out, a
if __name__=='__main__':
    k=eval(sys.argv[1]); name=sys.argv[2]
    pas=set(gen1_coll(name)); c,a=cells(k)
    for y in range(a['h']*2):
        print(' '.join('%02x/%02x%s'%(c[(x,y)][0],c[(x,y)][1],'!' if (c[(x,y)][0] in pas)!=(c[(x,y)][1] not in (0x07,0x90,0xff)) else ' ') for x in range(a['w']*2)))
