import sys
exec(open('kg1.py').read().replace("b.g.close()","""b.g.bsave(O+'/g1.sav'); d=open(O+'/g1.sav','rb').read()
def box(bank, a): o=bank*0x2000+a-0xa000; n=d[o]; return n, list(d[o+1:o+2+n])
print('sBox', box(1,0xad10)); print('box1', box(2,0xa000)); print('box2', box(2,0xa54a)); print('box3', box(2,0xaa94))
b.g.close()"""))
