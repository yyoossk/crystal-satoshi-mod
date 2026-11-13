import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq
make_test_rom(SC+'/build/p70.gbc')
b=Bot(state=SC+'/play/vir_p70.st', out=SC+'/run/vf2')
b.strong() if hasattr(b,'strong') else None
for (wx,wy,sx,sy,d) in ((26,84,27,33,'R'),(26,84,27,19,'R'),(26,84,1,17,'D')):
    b.warp((wx,wy),sx,sy); b.wait(100); b.clear_text()
    fs=[]
    b.step(d)
    for i in range(120):
        if b.in_battle(): b.battle(); fs.append(b.shot('after'))
        elif b.textbox(): b.press('A',30); fs.append(b.shot())
        else: b.wait(20); fs.append(b.shot())
    print((sx,sy), b.where(), b.pc())
    sheet(uniq(fs)[-16:], SC+'/run/vf2_%d.png'%sy, W=8)
