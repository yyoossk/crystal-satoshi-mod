import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq
ROM=sys.argv[1]
make_test_rom(SC+'/build/%s.gbc'%ROM)
b=Bot(state=SC+'/play/nf2b_%s.st'%ROM, out=SC+'/run/nf3')
def mus(): return '%02x mapmus %02x' % (b.peek(0xC101)[0], b.peek(0xC2C0)[0])
print('start', b.where(), mus())
b.goto(5,6); print(b.where(), mus())
fs=[]
b.step('D'); 
for i in range(80):
    fs.append(b.shot())
    if b.in_battle(): print('battle', mus()); b.battle(); print('after battle', mus())
    elif b.textbox(): b.press('A',30)
    else: b.wait(15)
    if i%10==0: print(i, b.where(), mus())
print(b.where(), mus())
sheet(uniq(fs)[-32:], SC+'/run/nf3.png', W=8)
b.g.save_state(SC+'/play/nf3_%s.st'%ROM)
