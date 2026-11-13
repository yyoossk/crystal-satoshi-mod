import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq
ROM=sys.argv[1]
make_test_rom(SC+'/build/%s.gbc'%ROM)
b=Bot(state=SC+'/play/nf1_%s.st'%ROM, out=SC+'/run/nf2')
b.go_warp(b.ids['PalletTown']); b.wait(60)
b.goto(10,1)
fs=[]
for i in range(120):
    b.step('U'); b.wait(10); fs.append(b.shot())
    if b.textbox(): b.press('A',30)
    if b.where()[0]==b.ids['OaksLab']: break
for i in range(40):
    b.wait(15); fs.append(b.shot())
    if b.textbox(): b.press('A',30)
print(b.where())
sheet(uniq(fs)[-16:], SC+'/run/nf2.png', W=8)
b.g.save_state(SC+'/play/nf2_%s.st'%ROM)
# pick fire from below
b.goto(6,4); b.face('U'); fs=[]
for k in 'A'*11:
    b.press(k,40); fs.append(b.shot())
for i in range(12):
    if b.has('はい'): break
    b.press('A',40); fs.append(b.shot())
b.press('D',20); b.press('A',40); fs.append(b.shot())
for i in range(16):
    b.press('A',40); fs.append(b.shot())
print(b.where())
sheet(fs[-24:], SC+'/run/nf2b.png', W=8)
b.g.save_state(SC+'/play/nf2b_%s.st'%ROM)
