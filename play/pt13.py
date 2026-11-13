from pt import *
b = B('s12a', 's13')
ok=False
for t in range(10):
    p=[q for q in b.objpos() if q!=(17,9)]
    if not p: b.goto(18,6); continue
    x,y=p[0]
    for (dx,dy,d) in ((1,0,'L'),(-1,0,'R'),(0,-1,'D'),(0,1,'U')):
        if b.goto(x+dx,y+dy):
            b.face(d); b.press('A',30)
            if b.textbox(): ok=True; break
    if ok: break
print('talking', ok, b.where())
for i in range(200):
    if b.textbox():
        if b.has('はい') and b.has('いいえ'): b.press('B',40)
        else: b.press('A',40)
        snap(b)
    elif b.in_battle(): b.wait(40); snap(b); b.press('A',20)
    else:
        b.wait(30); snap(b)
        if i>30 and not b.textbox() and not b.in_battle(): break
print('after', b.where(), mus(b))
b.g.save_state(ST % 's13a')
done(b, last=100, W=10)
