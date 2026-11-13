import sys; sys.path.insert(0,'play'); sys.path.insert(0,'tools')
from mapdb import DB, crystal_names
from jpchar import decode
SC='/tmp/claude-0/-home-claude/e85f874c-51bd-5d2c-9b1a-1d2b8ebf1451/scratchpad'
d=DB(SC+'/build/p54.gbc'); ids={v:k for k,v in crystal_names().items()}
r=d.r
def fo(b,a): return b*0x4000+a-0x4000
def txt(b,a):
    o=fo(b,a); e=o
    while r[e] not in (0x57,0x50,0x58) or e-o<2: e+=1
    return decode(r[o:e+1])[:150]
def scan(sb, p, n=60):
    code=r[fo(sb,p):fo(sb,p)+n]; i=0; out=[]
    while i<n-2:
        if code[i]==0x4C: out.append(('text',txt(sb, code[i+1]|code[i+2]<<8))); i+=3
        else: i+=1
    return out
for g in sys.argv[1:]:
    k=ids[g]; m=d.maps[k]; sb=m['scbank']
    print('=====',g,k,hex(sb))
    for o in d.objs(k):
        o=bytes(o); p=o[9]|o[10]<<8; typ=o[7]&0x0F
        print(' obj spr=%02x x=%d y=%d type=%x script=%04x'%(o[0],o[2]-4,o[1]-4,typ,p))
        if typ==2:   # trainer
            h=fo(sb,p); fl=r[h]|r[h+1]<<8; cls=r[h+2]; tid=r[h+3]
            ptr=[r[h+4+2*i]|r[h+5+2*i]<<8 for i in range(4)]
            print('   trainer flag=%x cls=%x id=%d'%(fl,cls,tid))
            for nm,pp in zip(('seen','win','loss'),ptr[:3]):
                if pp: print('    ',nm, txt(sb,pp))
            for t in scan(sb, ptr[3], 20): print('     after', t[1])
        else:
            for t in scan(sb,p,70): print('    ', t[1])
