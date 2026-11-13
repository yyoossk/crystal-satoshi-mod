import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq
make_test_rom(SC+'/build/p69.gbc')
b=Bot(state=SC+'/play/n2.st', out=SC+'/run/n3')
print(b.db.warps(b.where()[0]))
b.go_warp(b.ids['PalletTown']); print(b.where())
b.wait(60); b.shot('pallet')
k,x,y=b.where()
r=b.goto(10,1) or b.goto(11,1); print(r, b.where())
fs=[]
for i in range(120):
    b.step('U'); b.wait(10); fs.append(b.shot())
    if b.textbox(): b.press('A',30)
    if b.where()[0]==b.ids['OaksLab']: break
for i in range(40):
    b.wait(15); fs.append(b.shot())
    if b.textbox(): b.press('A',30)
print(b.where(), b.objs_of())
sheet(uniq(fs)[-48:], SC+'/run/n3.png', W=8)
b.g.save_state(SC+'/play/n3.st')
