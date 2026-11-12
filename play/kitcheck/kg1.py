from kt import *
rom=sys.argv[1]
b = start(rom, out='g1_'+rom)
fs=[]
def S(n):
    p=b.out+'/%02d_%s.png'%(len(fs),n); b.g.shot(p); fs.append(p)
def boxfull():
    asm=[0x3E,0x0A,0xEA,0x00,0x00, 0x3E,0x01,0xEA,0x00,0x40, 0x21,0x10,0xAD, 0x36,29, 0x23, 0x06,29, 0x3E,0x10, 0x22, 0x05, 0x20,0xFC, 0x36,0xFF, 0xAF,0xEA,0x00,0x00, 0xC9]
    for i, v in enumerate(asm): b.g.cmd('rpoke %x %d' % (SOFF + 0x40 + i, v))
    b.script([0x0E, SB, (SA + 0x40) & 0xFF, (SA + 0x40) >> 8], 30)
boxfull()
b.bank1(); b.g.poke(0xD4AE, 1)
k=b.mapk('Route35NationalParkGate')
b.warp(k, 2, 3); b.wait(80); b.clear_text()
b.step('U'); b.wait(20); b.face('U'); b.wait(20)
b.press('A',60); S('talk')
for i in range(40):
    b.press('A',50)
    if b.where()[0]!=k: break
b.wait(120); S('park'); print(b.where())
# walk in grass until battle; catch twice
from t57 import cells
cs=cells(b, b.where()[0], False); print('grass cells', len(cs))
k0,x0,y0=b.where()
cs.sort(key=lambda c: abs(c[0]-x0)+abs(c[1]-y0))
for c in cs[:10]:
    b.goto(*c)
    if b.where()[1:]==c: break
print('at', b.where())
caught=0
for t in range(400):
    if b.in_battle():
        b.wait(300)
        outn=0
        for j in range(300):
            b.bank1(); m=b.peek(0xd240,0x10); h=None
            for q in range(0,12):
                if m[q]==0 and m[q+2]==0 and m[q+1]==m[q+3] and m[q+1]>1: h=q; break
            if h is not None: hpat=0xd240+h
            if globals().get('hpat'):
                b.g.poke(hpat,0); b.g.poke(hpat+1,1)
            if b.has('いれかえ') or b.has('パソコン'):
                S('prompt%d'%caught)
            if j%40==0: S('b%d_%d'%(caught,j)); print('hp', hex(globals().get('hpat') or 0), flush=True)
            if b.has('いれかえ') or b.has('おくりますか') or b.has('おくりました') or b.has('いっぱい'):
                S('q%d_%d'%(caught,j))
            b.press('R',10); b.press('A',40)
            outn = outn+1 if not b.in_battle() else 0
            if outn>=5: break
        caught+=1; S('after%d'%caught); print('out', caught, b.where(), flush=True)
        if caught>=4: break
        continue
    d='LR'[t%2]
    b.step(d); 
print('caught', caught)
sheet(fs, b.out+'.png', W=6)
b.g.close()
