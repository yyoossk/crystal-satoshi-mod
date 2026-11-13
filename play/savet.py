import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/j18b.st', out=SC+'/play/run/savet')
b.press('S',40)
for i in range(5): b.press('D',15)
b.shot('sel'); b.press('A',60); b.shot('q')
for i in range(8):
    b.press('A',60); b.shot('s%d'%i)
b.wait(200); b.shot('done')
b.g.cmd('reset'); b.wait(600)
for i in range(8): b.press('S',60); b.shot('t%d'%i)
