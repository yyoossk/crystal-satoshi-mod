import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq, seq
make_test_rom(SC+'/build/p70.gbc')
b=Bot(state=SC+'/play/nf8_p70.st', out=SC+'/run/vf4')
b.g.poke(0xDCA5+0x1F,20)
def fight(x,y,d):
    b.warp((26,84),x,y); b.wait(100); b.clear_text()
    b.step(d); fs=[]
    for i in range(60):
        if b.in_battle(): b.battle(); 
        if b.textbox(): b.press('A',30)
        else: b.wait(15)
        fs.append(b.shot())
    print((x,y), b.where(), b.pc())
    fs+=seq(b,'D',30,'d',3)+seq(b,'U',30,'u',3)
    print(' moved', b.where(), b.pc())
    return fs
fs=fight(27,33,'R')+fight(27,19,'R')+fight(1,17,'D')
sheet(uniq(fs)[-48:], SC+'/run/vf4.png', W=8)
# talk to the beaten trainer
b.warp((26,84),29,33); b.wait(100); b.clear_text(); b.face('R'); b.press('A',60)
fs=[]
for i in range(20):
    fs.append(b.shot())
    if b.textbox(): b.press('A',30)
    else: b.wait(15)
print('talk', b.where(), b.pc())
fs+=seq(b,'D',30,'d',3); print(' moved', b.where())
sheet(uniq(fs), SC+'/run/vf4b.png', W=8)
