import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq, seq
make_test_rom(SC+'/build/p70.gbc')
b=Bot(state=SC+'/play/nf8_p70.st', out=SC+'/run/vf5')
b.strong(4,60)
def run(tag):
    fs=[]
    for i in range(80):
        if b.in_battle(): b.battle()
        if b.textbox(): b.press('A',30)
        else: b.wait(15)
        fs.append(b.shot())
    fs+=seq(b,'D',24,'d',3)
    print(tag, b.where(), b.pc()); return fs
fs=[]
# talk-initiated: stand next to each trainer from behind / side
for (x,y,d) in ((31,33,'L'),(31,19,'L'),(3,18,'L')):
    b.warp((26,84),x,y); b.wait(100); b.clear_text(); b.face(d); b.press('A',40)
    fs+=run((x,y))
    # talk again after
    b.warp((26,84),x,y); b.wait(100); b.clear_text(); b.face(d); b.press('A',40)
    fs+=run(('again',x,y))
sheet(uniq(fs)[-48:], SC+'/run/vf5.png', W=8)
