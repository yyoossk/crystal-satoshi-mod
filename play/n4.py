import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq
make_test_rom(SC+'/build/p69.gbc')
b=Bot(state=SC+'/play/n4.st', out=SC+'/run/n4b')
fs=[]
for k in 'A'*6+'B'*2+'A'*30:
    b.press(k,40); fs.append(b.shot())
print(b.where())
b.g.save_state(SC+'/play/n5.st')
sheet(fs, SC+'/run/n4.png', W=8)
