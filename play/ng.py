import sys; sys.path.insert(0,'play')
from bot import *
b=Bot(out='play/run/ng')
b.wait(400)
assert b.until_text('サトシ'); b.shot('m1')
b.press('D'); b.press('A',60); b.shot('m2')
r=b.until_text('ョン',w=20); b.shot('m3'); assert r
b.press('D'); b.press('A',60); b.shot('m4')   # シゲル
for i in range(30):
    b.press('A',40)
    if b.where()[0]!=(0,0) and b.peek(0xC4A0+20*12+1)[0]==0x7F: pass
b.shot('end'); print(b.where(), b.pc(), b.peek(0xD48E,6), b.peek(0xD4A6,6))
b.g.save_state(SC+'/play/ng0.st')
