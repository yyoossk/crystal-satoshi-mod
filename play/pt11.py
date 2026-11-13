from pt import *
b = B('s10a', 's11')
for i in range(40):
    if b.textbox(): b.press('A',40)
    else: b.wait(20)
    snap(b)
    if not b.textbox() and i>15:
        b.wait(60)
        if not b.textbox(): break
print('after dex', b.where(), mus(b), b.objpos())
# Oak again (Poke Balls? Red: talk -> 'come see me sometimes' / gives balls only after... )
b.talk_to(4,2,n=0); snap(b); ev(b,20)
b.travel((13,5)); b.wait(30)
b.goto(2,4); b.face('U'); b.press('A',40); snap(b); ev(b,30)
b.press('A',40); snap(b); ev(b,20)
b.go_warp((13,2)); b.wait(30); b.go_warp((13,5)); b.wait(60); snap(b)
talk_all(b)
print('daisy done', b.where(), mus(b), b.peek(0xD957,1) if False else '')
b.g.save_state(ST % 's11a')
done(b, last=100, W=10)
