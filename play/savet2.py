import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq, seq
make_test_rom(SC+'/build/p71.gbc')
b=Bot(state=SC+'/play/blogbase2.st', out=SC+'/run/savet2')
b.warp('VioletCity',20,20); b.wait(100); b.clear_text(); b.step('L'); b.step('L')
fs=[b.shot()]
b.press('S',40); [b.press('U',12) for j in range(8)]; [b.press('D',12) for j in range(6)]; b.press('A',80); fs.append(b.shot())
for i in range(8):
    if b.has('はい'): b.press('A',120)
    elif b.textbox(): b.press('A',60)
    else: b.wait(30)
    fs.append(b.shot())
b.wait(120); b.g.reset(); b.wait(700)
for k in 'AAAAAAAA': b.press(k,90); fs.append(b.shot())
b.wait(200); fs.append(b.shot()); b.step('R'); b.step('R'); b.wait(30); fs.append(b.shot())
print(b.where())
sheet(uniq(fs)[-12:], SC+'/run/savet2.png', W=6)
