import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq, seq
ROM=sys.argv[1]
make_test_rom(SC+'/build/%s.gbc'%ROM)
b=Bot(state=SC+'/play/nf7_%s.st'%ROM, out=SC+'/run/nf8')
r=b.travel((13,5)); print('travel', r, b.where())
fs=[b.shot()]
b.goto(2,4); b.face('U'); b.press('A',40)
for i in range(30):
    fs.append(b.shot())
    if b.textbox(): b.press('A',30)
    else: b.wait(20)
b.press('A',40)
for i in range(10):
    fs.append(b.shot())
    if b.textbox(): b.press('A',30)
    else: b.wait(20)
b.go_warp((13,2)); b.wait(30); b.go_warp((13,5)); b.wait(60); fs.append(b.shot())
for i in range(8): b.wait(30); fs.append(b.shot())
sheet(uniq(fs)[:40], SC+'/run/nf8.png', W=8)
b.g.save_state(SC+'/play/nf8_%s.st'%ROM)
