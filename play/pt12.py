from pt import *
b = B('s11a', 's12')
b.travel('ViridianCity'); b.wait(40); print('vir', b.where(), mus(b))
b.goto(18,12); snap(b); print(b.objpos())
for p in b.objpos():
    if p[1] < 12 and abs(p[0]-17)<4:
        b.talk_to(*p, n=0); snap(b); ev(b,80); print('talk', p, b.where(), mus(b))
b.g.save_state(ST % 's12a')
done(b, last=100, W=10)
