from pt import *
b = B('s14a', 'gear')
b.press('S',40); [b.press('U',12) for j in range(8)]; [b.press('D',12) for j in range(3)]; b.press('A',90); snap(b)
for k in 'RRR': b.press(k,60); snap(b)
b.press('B',60); b.press('B',60)
# Viridian PC people
b.travel((23,9)); b.wait(40); snap(b)
for (x,y) in ((6,5),(4,3)):
    cur=[p for p in b.objpos() if abs(p[0]-x)+abs(p[1]-y)<=2]
    p=cur[0] if cur else (x,y)
    b.talk_to(*p, n=0); snap(b); ev(b,20)
sheet(uniq(b.fs), SC+'/run/pt_gear.png', W=6)
