from kt import *
def run(slot, d, n=2):
    b = start('p67', state=O+'/b1.st', out='b1m')
    b.bank1(); b.g.poke(0xD833, slot)
    k,x0,y0=b.where()
    b.g.down(d); f=0
    while True:
        b.g.wait(1); f+=1
        b.bank1(); yy,xx=b.peek(W_Y,2)
        if abs(xx-x0)+abs(yy-y0)>=n or f>300: break
    b.g.up(d); b.g.shot(b.out+'/end_%d_%s.png'%(slot,d)); print(slot, d, f, b.where(), len(b.objpos())); b.g.close()
for d in 'D':
    run(0,d); run(0xff,d)
