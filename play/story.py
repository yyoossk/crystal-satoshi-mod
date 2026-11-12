"""story runner: python3 story.py IN.st OUT.st step..."""
import functools; print = functools.partial(print, flush=True)
from mlib import *
import sys, json
def run(b, steps):
    for st in steps:
        op=st[0]; b.refresh_grid()
        if op=='t':
            tgt=tuple(st[1]); r=False
            for k in range(3):
                r=b.travel(tgt); b.ev(shots=False)
                if b.where()[0]==tgt: break
            print('travel',tgt,b.where()[0]==tgt,b.where(),b.log[-2:])
        elif op=='talk':
            r=b.talk_to(st[1],st[2])
            for i in range(st[3] if len(st)>3 else 4): b.wait(40); b.ev()
            print('talk',st[1:3],r,b.where(),b.log[-1:])
        elif op=='go':
            print('go',st[1:],b.goto(st[1],st[2]),b.where())
            for i in range(3): b.wait(30); b.ev()
        elif op=='face':
            b.face(st[1]); b.press('A',60); b.ev()
        elif op=='save':
            b.g.save_state(SC+'/play/'+st[1]+'.st'); print('saved',st[1])
        elif op=='name':
            b.press('S',40); b.press('A',60); b.ev()
        elif op=='ev':
            for i in range(st[1]): b.wait(40); b.ev()
if __name__=='__main__':
    b=Bot(state=SC+'/play/'+sys.argv[1]+'.st', out=SC+'/play/run/'+sys.argv[2])
    run(b, json.loads(sys.argv[3]))
    b.g.save_state(SC+'/play/'+sys.argv[2]+'.st'); print('end', b.where(), b.peek(0xD857,2))
