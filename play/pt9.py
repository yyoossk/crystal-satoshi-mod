from pt import *
b = B('s8a', 's9')
for (x,y) in ((13,20),(30,25),(6,23)):
    cur=[p for p in b.objpos() if abs(p[0]-x)+abs(p[1]-y)<=3]
    p=cur[0] if cur else (x,y)
    r=b.talk_to(*p, n=0); snap(b); ev(b,25,yes=False); print('talk', (x,y), r, b.where())
# the girl / old man from the south
b.goto(17,10); b.face('U'); b.press('A',40); snap(b); ev(b,15)
b.goto(18,10); b.face('U'); b.press('A',40); snap(b); ev(b,15)
b.g.save_state(ST % 's9a')
done(b, last=120)
