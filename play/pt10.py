from pt import *
b = B('s9a', 's10')
b.travel((23,9)); b.wait(40); print('pc', b.where(), mus(b)); snap(b)
nx=[p for (sp,*p) in [(o[0],o[1],o[2]) for o in b.objs_of()] if True][0]
b.talk_to(*nx, n=0); snap(b); ev(b,30)
b.go_warp((23,3)); b.wait(30)
b.travel((26,97)); b.wait(40); print('mart', b.where(), mus(b)); snap(b); ev(b,40)
b.travel((13,6)); b.wait(40); print('lab', b.where(), mus(b))
b.goto(4,3); b.face('U'); b.press('A',40); snap(b)
for i in range(60):
    if b.textbox(): b.press('A',40)
    else: b.wait(20)
    snap(b)
    if i%10==0: print(i, mus(b))
    if not b.textbox() and i>40: break
print('dex', b.where(), mus(b))
b.g.save_state(ST % 's10a')
done(b, last=150, W=10)
