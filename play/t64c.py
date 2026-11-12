from t64a import *
def setlast(b, ball):
    asm = bytes([0x3E,2,0xE0,0x70,0x3E,ball,0xEA,0xC9,0xDF,0x3E,1,0xE0,0x70,0xC9])
    for i, v in enumerate(asm): b.g.cmd('rpoke %x %d' % (SOFF + 0x40 + i, v))
    b.script([0x0E, SB, (SA + 0x40) & 0xFF, (SA + 0x40) >> 8], 30)
def trial(b, mon, lv, ball, status=0, tag='x', maxthrows=6):
    b.giveitem(ball, 30); setlast(b, ball)
    b.script([0x5C, mon, lv, 0x5E, 0x5F], 30)
    for i in range(80):
        b.wait(10)
        if b.in_battle(): break
    b.wait(400)
    if status:
        b.bank1(); b.g.poke(0xD245, status)
    throws=0
    for k in range(120):
        if not b.in_battle(): break
        if k % 3 == 0: b.press('s', 40); 
        else: b.press('B', 40)
        if k % 6 == 0: b.shot(tag)
    b.wait(120)
    for i in range(10): b.press('B',30)
    n, p = party(b)
    return n, p
if __name__=='__main__':
    import sys
    b=Bot(state='p64nb.st', out=OUT+'/catch')
    # make room: party 6 -> box gets the catch; fine
    for mon,lv,ball,st,name in ((0x13,5,0x05,0x40,'rattata PAR poke'),(0x23,10,0xA5,0,'clefairy moon'),(0x54,10,0xA1,0,'doduo fast'),(0x8F,100,0x05,0,'snorlax lv100'),(0x10,5,0xA6,0,'pidgey love')):
        print(name, trial(b,mon,lv,ball,st,tag=name.split()[0]), flush=True)
        b.bank1(); print(' boxcount', b.peek(0xAD10,1) if False else '', flush=True)
    strip(b.out,'s')
