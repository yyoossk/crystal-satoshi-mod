import sys; sys.path.insert(0,'.')
from t64a import *
rom=sys.argv[1]; O=SC+'/run/t66/'+sys.argv[2]; import os, shutil; shutil.rmtree(O,ignore_errors=True); os.makedirs(O,exist_ok=True)
make_test_rom(SC+'/build/%s.gbc'%rom)
b=Bot(state='blogbase2.st', out=O)
T=SA+16
txt=[0x00]+list(encode('やなかんじー！'))+[0x57]
sc=[0x63, T&255, T>>8, T&255, T>>8, 0x5D, 72, 1, 0x5E, 0x5F, 0x90]
sc+= [0]*(16-len(sc)) + txt
b.script(sc[:-1] if False else sc, 30)
b.wait(300)
n=0; out=0
print('enemyHP',b.peek(0xd246,4))
for i in range(400):
    b.bank1(); h=b.peek(0xd246,2)
    if b.peek(0xd235)[0] and (h[0] or h[1]>1): b.g.poke(0xd246,0); b.g.poke(0xd247,1)
    if i%5==0 and b.peek(0xd235)[0]:
        m=bytes(b.peek(0xc000,0x1000))+bytes(b.peek(0xd000,0x1000))
        k=m.find(bytes([0x2d,0x34,0x6c,0x63]))
        while k>=0:
            b.g.poke(0xc000+k,0x34); b.g.poke(0xc001+k,0x2d); k=m.find(bytes([0x2d,0x34,0x6c,0x63]),k+1)
    b.press('B' if i%5>=3 else 'A',20)
    if i%2==0: b.g.shot(O+'/w%03d.png'%n); n+=1
    out = out+1 if not b.in_battle() else 0
    if out>=4: break
b.g.close()
print(n)
