from kt import *
from t64c import setlast
rom=sys.argv[1]
b = start(rom, out='d_'+rom)
fs=[]
def S(n):
    p=b.out+'/'+n+'.png'; b.g.shot(p); fs.append(p)
# party mon1 moves: Psychic, Dragon Rage, Ember, Gust (Charmander)
b.bank1()
for i,mv in enumerate((0x5e,0x52,0x34,0x10)): b.g.poke(0xdca5+2+i, mv); b.g.poke(0xdca5+0x17+i, 10)
b.giveitem(0x05,30); setlast(b,0x05)
for i in range(40): b.wait(10)
def menu():
    b.wait(250)
b.script([0x5C, 0x13, 20, 0x5E, 0x5F], 30)
b.wait(560); b.press('A',30); b.wait(400); S('menu')
b.press('A',60); S('mv1')
b.press('D',30); S('mv2'); b.press('D',30); S('mv3'); b.press('D',30); S('mv4')
b.press('D',30)   # back to first
b.press('D',30); b.press('D',30)                # Ember
fsx = tap(b,'A',400,'hit',every=8)
S('afterhit')
fs += uniq(fsx)[-16:]
# status colors in move menu: poison the battle mon
for st in (8,0x40):
    # wBattleMonStatus JP? search later
    pass
# D3 quick ball (SELECT)
menu(); S('beforeball')
fsq = tap(b,'s',200,'ball',every=1, hold=6)
u=uniq(fsq); print('ball frames', len(u)); fs += u[:4]
sheet(fs, b.out+'.png', W=8)
b.g.close()
