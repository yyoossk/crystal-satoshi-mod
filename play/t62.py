from t57 import *
make_test_rom(SC + '/build/p62.gbc')
MF = lambda n: n ** 3
MS = lambda n: int(1.2 * n ** 3 - 15 * n * n + 100 * n - 140)
N = PM.MON
cases = [('ONIX', 0, MF, 36), ('ONIX', 0, MF, 37), ('SCYTHER', 0, MF, 37), ('POLIWHIRL', 0, MS, 37), ('SEADRA', 0, MF, 37),
         ('PORYGON', 0, MF, 37), ('KADABRA', 0, MS, 37), ('SLOWPOKE', 0x52, MF, 37), ('SLOWPOKE', 0, MF, 37)]
for name, item, g, target in cases:
    b = Bot(state='postjhof2.st', out=SC + '/run/t62/%s%d' % (name, target))
    b.g.poke(0xDC9D, 0); b.givepoke(N[name], target - 1)
    e = g(target) - 1; b.bank1()
    b.g.pokes(0xDCA5 + 1, [item]); b.g.pokes(0xDCA5 + 8, [e >> 16, (e >> 8) & 255, e & 255])
    b.g.pokes(0xDCA5 + 2, [0x21, 0x21, 0x21, 0x21]); b.g.pokes(0xDCA5 + 0x17, [30, 30, 30, 30])
    for t in range(4):
        b.warp((13, 1), 12, 22, 120)
        if b.where()[0] == (13, 1): break
    for i in range(300):
        b.wait(random.randint(1, 30)); b.step('R'); b.step('L')
        if b.textbox() and not b.in_battle(): b.ev(40, shots=False)
        if b.in_battle(): break
    for i in range(200):
        b.press('A', 40)
        if not b.in_battle() and not b.textbox():
            b.wait(60)
            if not b.textbox() and not b.in_battle(): break
    b.shot('end'); b.bank1()
    print(name, 'item' if item else '-', 'lv', b.peek(0xDCA5 + 0x1F)[0], '->', INV.get(b.peek(0xDC9E)[0]), 'item now', b.peek(0xDCA5 + 1)[0], flush=True)
    b.g.close()
