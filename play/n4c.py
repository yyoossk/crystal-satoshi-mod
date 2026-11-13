import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq
make_test_rom(SC+'/build/p69.gbc')
b=Bot(state=SC+'/play/n4.st', out=SC+'/run/n4c')
fs=[]
for k in 'A'*11+'DA'+'A'*12:
    b.press(k,40); fs.append(b.shot())
sheet(fs[10:], SC+'/run/n4c.png', W=7)
b.g.save_state(SC+'/play/n5b.st')
