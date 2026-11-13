import sys; sys.path.insert(0,'play'); from bot import *
sys.path.insert(0,SC+'/tools'); import build_phase15 as P15
for st in ['k16','k27']:
    b=Bot(state=SC+'/play/%s.st'%st)
    b.warp('LavenderTown',3,8); b.wait(60)
    p=b.peek(P15.W_WARPS_PTR,2); a=p[0]|p[1]<<8; n=b.peek(P15.W_WARPS_PTR-1,1)
    sb=b.db.maps[(18,4)]['scbank']; o=sb*0x4000+a-0x4000
    print(st, hex(a), n, b.db.r[o:o+30].hex())
    print('   table', b.db.warps((18,4)))
