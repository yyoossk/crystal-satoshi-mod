from pt import *
from bot import grid_of
b = B(None, 's1')
snap(b)
k=b.where()[0]; G=grid_of(b.db.r,b.db.maps[k]['hdr'])
for row in G: print(' '.join('%02x'%c for c in row))
if b.goto(0,2): b.face('U'); b.press('A',40); ev(b,30,yes=False); b.press('B',30); b.press('B',30)
for (x,y,d) in ((3,6,'U'),(2,5,'R'),(4,5,'L'),(3,4,'D')):
    if b.goto(x,y): b.face(d); b.press('A',40); ev(b,20); break
print('2F', mus(b))
b.go_warp((13,3)); ev(b, 60)
print('after mom', b.where(), mus(b))
b.face('L'); b.press('A',40); ev(b,20)
print('talk mom', mus(b))
# TV
G=grid_of(b.db.r,b.db.maps[b.where()[0]]['hdr'])
for row in G: print(' '.join('%02x'%c for c in row))
done(b)
b.tag='s1b'; b.fs=[]
for (x,y,d) in ((2,2,'U'),(3,2,'L')):
    if b.goto(x,y): b.face(d); b.press('A',40); ev(b,10)
done(b)
