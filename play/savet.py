import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq, seq, start_menu
make_test_rom(SC+'/build/p71.gbc')
b=Bot(state=SC+'/play/blogbase2.st', out=SC+'/run/savet')
b.warp('VioletCity',20,20); b.wait(100); b.clear_text(); b.step('L'); b.step('L')
fs=[b.shot()]
b.press('S',40); b.press('D',12); b.press('D',12); b.press('A',60); b.wait(60); fs.append(b.shot()); b.press('B',40); b.press('B',40)
for n in []:
    b.press('S',40)
    for j in range(n): b.press('D',12)
    b.press('A',60); fs.append(b.shot())
    if b.has('かきますか') or b.has('レポートを'): break
    for j in range(4): b.press('B',30)
for i in range(10):
    if b.has('はい'): b.press('A',90)
    else: b.press('A',40)
    fs.append(b.shot())
b.wait(200); b.g.reset(); b.wait(600)
for k in 'AAAA': b.press(k,80); fs.append(b.shot())
b.wait(200); fs.append(b.shot()); b.step('R'); b.wait(30); fs.append(b.shot())
print(b.where())
sheet(uniq(fs)[-16:], SC+'/run/savet.png', W=8)
