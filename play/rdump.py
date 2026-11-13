import sys; sys.path.insert(0,'/tmp/claude-0/-home-claude/e85f874c-51bd-5d2c-9b1a-1d2b8ebf1451/scratchpad/tools')
import redtexts as RT; from jpchar import decode
R=RT.R
def segs(a,b):
    o=a
    while o<b:
        if R[o]==0x00 and R[o+1] not in (0,):
            e=o+1
            while R[e] not in (0x50,0x57,0x58): e+=1
            print('%x %02x %s'%(o,R[e],decode(R[o:e]))); o=e+1
        else:
            print('%x [%02x]'%(o,R[o]), end=' '); o+=1
            if R[o-1] in (0x50,0x57,0x58): print()
    print()
for a in sys.argv[1:]:
    a,b=[int(x,16) for x in a.split('-')]; print('=====',hex(a)); segs(a,b)
