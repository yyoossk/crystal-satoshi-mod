import sys; sys.path.insert(0,'play')
from bot import *
b=Bot(out='play/run/ngd')
b.wait(400)
assert b.until_text('サトシ'); b.press('D'); b.press('A',60)
for i in range(12):
    t=b.tilemap(); print(i, decode(t[20*12:]) if True else '')
    b.shot('x'); b.press('A',20)
