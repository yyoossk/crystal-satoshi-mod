import sys; sys.argv=['x']
exec(open('t61.py').read())
make_test_rom(SC + '/build/p61.gbc')
b = Bot(state='postjhof2.st', out=SC + '/run/t61/lose')
b.bank1(); b.g.poke(0xDC9D, 1)
b.g.pokes(0xDCA5 + 2, [0x96, 0, 0, 0]); b.g.pokes(0xDCA5 + 0x17, [40, 0, 0, 0]); b.g.pokes(0xDCA5 + 0x22, [0, 1])
print('flags', flags(b))
act(b, ILEX, 8, 23, 'U', 'l1'); b.wait(200); b.shot('lb')
for i in range(60):
    if not b.in_battle() and not b.textbox(): break
    b.press('A', 60)
    if i % 4 == 0: b.shot('lx')
b.wait(200); b.shot('after'); print('after lose', b.where(), flags(b))
for i in range(10):
    if b.textbox(): b.press('A', 60)
b.bank1(); b.g.pokes(0xDCA5 + 0x22, [1, 0])
act(b, ILEX, 8, 23, 'U', 'l2'); b.wait(200); b.shot('again'); print('again battle', b.in_battle())
