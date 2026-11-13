import sys; sys.path.insert(0,'play')
from t64a import *
from kt import seq, uniq, sheet
ROM=sys.argv[1]
make_test_rom(SC+'/build/%s.gbc'%ROM)
b=Bot(state=SC+'/play/ng_%s.st'%ROM, out=SC+'/run/nf1')
b.go_warp((13,3))
fs=[]
for i in range(70):
    b.wait(8); fs.append(b.shot())
    if b.textbox(): b.press('A',20)
for i in range(30):
    if b.textbox(): b.press('A',30)
    else: b.wait(20)
print(b.where())
sheet(uniq(fs)[:40], SC+'/run/nf1.png', W=8)
b.g.save_state(SC+'/play/nf1_%s.st'%ROM)
