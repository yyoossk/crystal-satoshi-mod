import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq, seq
ROM=sys.argv[1]; tag=sys.argv[2]
make_test_rom(SC+'/build/%s.gbc'%ROM)
b=Bot(state=SC+'/play/blogbase2.st', out=SC+'/run/earl_'+tag)
k=b.ids['VioletCity']; print(b.objs_of(k)[:3])
b.warp('VioletCity',13,17); b.wait(100); b.clear_text()
b.step('L'); b.step('R'); b.wait(30)
b.goto(13,17); b.face('U'); print(b.where())
b.press('A',60)
fs=[]
for i in range(200):
    fs.append(b.shot())
    if b.has('はい') and b.has('いいえ'): b.press('D',10); b.press('A',30)
    elif b.textbox(): b.press('A',20)
    else: b.wait(8)
    if i>30 and not b.textbox() and b.peek(0xD428)[0]==0: break
print(b.where())
for i in range(4): b.step('D'); fs.append(b.shot())
b.wait(30); fs.append(b.shot())
sheet(uniq(fs)[::2][:64], SC+'/run/earl_%s.png'%tag, W=8)
