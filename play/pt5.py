from pt import *
b = B('s4a', 's5')
b.goto(7,4); b.face('U'); b.press('A',40); snap(b)
n=0
for i in range(40):
    if b.has('ニックネームは'): break
    if b.has('つけますか') : b.press('A',60); snap(b); continue
    b.press('A',40); snap(b)
print('naming', b.has('ニックネームは'))
for k in 'RA': b.press(k,20); snap(b)     # type 2 chars
b.press('S',30); snap(b); b.press('A',60); snap(b)
for i in range(60):
    if b.textbox(): b.press('A',40)
    else: b.wait(20)
    snap(b)
    if not b.textbox() and i>10:
        b.wait(40)
        if not b.textbox(): break
print('picked', b.where(), mus(b), b.objpos(), 'fwslot', b.peek(0xD833)[0])
b.g.save_state(ST % 's5a')
done(b, last=96)
