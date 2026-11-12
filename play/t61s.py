import sys; sys.argv=['x']
exec(open('t61.py').read())
b = Bot(state='t61elm.st', out=SC + '/run/t61/save')
act(b, ILEX, 8, 23, 'U', 'c'); b.wait(150); run_away(b); act2(b, 'c')
print('before', flags(b))
b.press('S', 40)
for i in range(8):
    if b.has('レポート'): break
    b.wait(20)
b.shot('menu')
for i in range(5): b.g.press('D', 6, 20)
b.press('A', 60); b.shot('q')
for i in range(6): b.press('A', 120); b.shot('s')
b.wait(300); b.shot('saved')
b.g.reset(); b.wait(400)
for i in range(12): b.press('A', 90); b.shot('t')
for i in range(6):
    if b.where()[0] == ILEX and not b.textbox(): break
    b.press('A', 90)
b.wait(120); b.shot('cont')
print('after reload', b.where(), flags(b))
act(b, ILEX, 8, 23, 'U', 'c3'); act2(b, 'c3'); print('shrine battle', b.in_battle())
act(b, LAB, 5, 3, 'U', 'e3'); act2(b, 'e3'); print('elm', party(b))
