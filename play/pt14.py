from pt import *
b = B('s13a', 's14')
b.travel('Route22'); b.wait(40); print('r22', b.where(), mus(b))
b.goto(30,5); snap(b)
b.step('L'); snap(b)
for i in range(150):
    if b.in_battle(): b.battle(); snap(b); print('battle end', b.where(), mus(b))
    elif b.textbox(): b.press('A',40); snap(b)
    else:
        b.wait(30); snap(b)
        if i>20 and not b.textbox() and not b.in_battle(): break
print('after', b.where(), mus(b), b.objpos())
b.g.save_state(ST % 's14a')
done(b, last=100, W=10)
