import functools; print = functools.partial(print, flush=True)
from mlib import *
import sys
b=Bot(state=SC+'/play/%s.st'%sys.argv[1], out=SC+'/play/run/team')
b.g.poke(0xDC9D, 1); b.g.poke(0xDC9F, 0xFF)       # test team: Mewtwo + five
for sp, lv in [(248,70),(214,70),(131,70),(135,70),(160,70)]:
    b.givepoke(sp, lv); b.wait(30)
print(b.peek(0xDC9D,8))
b.g.save_state(SC+'/play/%s.st'%sys.argv[2])
