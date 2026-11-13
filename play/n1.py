import sys; sys.path.insert(0,'play')
from t64a import *
from kt import seq, uniq, sheet
make_test_rom(SC+'/build/'+ROM+'.gbc')
b=Bot(state=SC+'/play/ng_'+ROM+'.st', out=SC+'/run/n1')
b.go_warp((13,3)); print(b.where())
fs=[]
for i in range(60):
    b.wait(10); fs.append(b.shot())
    if b.textbox(): b.press('A',20)
print(b.where(), b.objpos())
sheet(uniq(fs)[:40], SC+'/run/n1.png', W=8)
b.g.save_state(SC+'/play/n1.st')
