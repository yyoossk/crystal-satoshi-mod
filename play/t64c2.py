from t64c import *
from jpchar import encode
E=encode('にげる').rstrip(b'\x50')
def trial3(b, mon, lv, ball, status=0, tag='x', maxthrow=10):
    b.giveitem(ball, 30); setlast(b, ball)
    b.script([0x5C, mon, lv, 0x5E, 0x5F], 30)
    for i in range(60): b.wait(10)
    b.press('A',30); b.wait(300)
    if status: b.bank1(); b.g.poke(0xD245, status)
    throws=0
    for k in range(maxthrow):
        if not b.in_battle(): break
        b.g.press('s',6,30); throws+=1; b.wait(60); b.shot(tag)
        for j in range(8):
            if not b.in_battle(): break
            b.press('B',40)
        b.wait(60)
    caught = not b.in_battle()
    for i in range(15): b.press('B',30)
    return throws, caught
if __name__=='__main__':
    b=Bot(state='p64nb.st', out=OUT+'/catch5')
    for mon,lv,ball,st,name in ((0x13,5,0x05,0x40,'rattata PAR poke'),(0x10,5,0xA6,0,'pidgey love'),(0x54,10,0xA1,0,'doduo fast'),(0x8F,100,0x05,0x10,'snorlax lv100 FRZ'),(0x84,10,0x05,0,'ditto')):
        print(name, trial3(b,mon,lv,ball,st,tag=name.split()[0]), flush=True)
    strip(b.out,'s')
