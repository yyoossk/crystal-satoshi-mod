import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq, seq
ROM=sys.argv[1]
make_test_rom(SC+'/build/%s.gbc'%ROM)
b=Bot(state=SC+'/play/nf8_%s.st'%ROM, out=SC+'/run/nf9')
def mus(): return '%02x mapmus %02x' % (b.peek(0xC101)[0], b.peek(0xC2C0)[0])
r=b.travel('Route22'); print('travel', r, b.where())
b.goto(30,5); print(b.where())
fs=seq(b,'L',30,'l',2)
for i in range(40):
    fs.append(b.shot())
    if b.in_battle():
        # enemy species / level: wEnemyMon? just screenshot
        for j in range(6): b.press('A',30); fs.append(b.shot())
        b.battle(); print('after battle', mus())
    elif b.textbox(): b.press('A',30)
    else: b.wait(5)
print(b.where(), mus())
sheet(uniq(fs)[:56], SC+'/run/nf9.png', W=8)
