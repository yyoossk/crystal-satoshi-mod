import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq, seq
ROM=sys.argv[1]
make_test_rom(SC+'/build/%s.gbc'%ROM)
b=Bot(state=SC+'/play/nf6_%s.st'%ROM, out=SC+'/run/nf7')
def mus(): return '%02x mapmus %02x' % (b.peek(0xC101)[0], b.peek(0xC2C0)[0])
fs=[]
for i in range(60):
    fs.append(b.shot())
    if i%5==0: print(i, mus())
    if b.textbox(): b.press('A',30)
    else: b.wait(20)
print(b.where(), mus())
sheet(uniq(fs)[:40], SC+'/run/nf7.png', W=8)
b.g.save_state(SC+'/play/nf7_%s.st'%ROM)
