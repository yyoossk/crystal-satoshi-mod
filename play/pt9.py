from pt import *
b = B('s8a', 's9')
print(b.objs_of())
for (spr,x,y) in b.objs_of():
    cur=[p for p in b.objpos() if abs(p[0]-x)+abs(p[1]-y)<=3]
    p=cur[0] if cur else (x,y)
    r=b.talk_to(*p, n=0); snap(b); ev(b,20); print('talk', (x,y), r, b.where())
read_signs(b)
b.g.save_state(ST % 's9a')
done(b, last=120)
