from pt import *
b = B('s5a', 's6')
b.goto(5,6); snap(b); b.step('D'); snap(b)
res=None
for i in range(150):
    if b.in_battle():
        b.battle(); snap(b)
    elif b.textbox(): b.press('A',40); snap(b)
    else:
        b.wait(30); snap(b)
        if not b.textbox() and not b.in_battle() and i>20:
            b.wait(60)
            if not b.textbox(): break
print('after', b.where(), mus(b), b.objpos(), 'fwslot', b.peek(0xD833)[0])
hp=b.peek(0xDCA5+0x22,2); print('hp', hp)
b.step('D'); b.step('U'); snap(b); b.wait(30); snap(b)
b.talk_to(4,2,n=0); snap(b); ev(b,20)
b.g.save_state(ST % 's6a')
done(b, last=96)
