import sys,os; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq, seq
make_test_rom(SC+'/build/p69.gbc')
b=Bot(state=SC+'/play/n5.st', out=SC+'/run/n7')
def vram():
    out={}
    for bk in (0,1):
        d=[]
        for a in range(0x8000,0x9800,256): d+=b.g.vpeek(bk,a,256)
        out[bk]=bytes(d)
    return out
b.warp('PalletTown',10,3); b.wait(60); b.clear_text(); b.wait(200)
v0=vram()
seq(b,'U',30,'u',8); print(b.where()); vA=vram()
seq(b,'U',40,'u',8); b.wait(30); print(b.where())
v1=vram()
b.wait(300); v2=vram()
for bk in (0,1):
    for name,v in (('pallet-moved',vA),('during',v1),('after',v2)):
        diff=sorted({i//16 for i in range(len(v0[bk])) if v0[bk][i]!=v[bk][i]})
        print(bk,name,len(diff),[hex(t) for t in diff][:80])
print(b.where())
