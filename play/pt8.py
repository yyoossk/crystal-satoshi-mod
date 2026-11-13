from pt import *
b = B('s7a', 's8')
for (spr,x,y) in b.objs_of():
    for t in range(3):
        cur=[p for p in b.objpos() if abs(p[0]-x)+abs(p[1]-y)<=3]
        p=cur[0] if cur else (x,y)
        b.goto(p[0], p[1]+2) if False else None
        r=b.talk_to(*p, n=0); snap(b); ev(b,20)
        if r!=-1: break
    print('talked', (x,y), b.where())
print('items', b.peek(0xD892,8) if False else '')
b.travel('ViridianCity'); b.wait(60); print('viridian', b.where(), mus(b)); snap(b)
b.g.save_state(ST % 's8a')
done(b, last=96)
