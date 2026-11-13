import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k03.st', out=SC+'/play/run/k04')
b.clear_text(); print(b.objpos())
b.shot('o')
b.goto(5,8); b.shot('w')
for i in range(80):
    b.press('A',40); b.shot()
    if not b.in_battle() and not b.textbox() and i>10: break
print(b.where(), b.peek(0xDC9E,7), b.log)
b.g.save_state(SC+'/play/k04.st')
b.sheet('a',8)
