from kt import *
import os
rom=sys.argv[1]; slot=int(sys.argv[2])
os.environ['GBWATCHLOG']=O+'/watch_%s.log'%rom
b = start(rom, state=('kitbase.st' if rom=='kit60' else 'blogbase2.st'), out='a16d')
m,d='GoldenrodCity','R'
x,y = straight(b, m, d, 3)
b.bank1(); b.g.poke(0xD833, slot)
b.warp(m,x,y); b.wait(80); b.clear_text()
b.step(d); b.wait(30); b.step(d); b.wait(40)
b.face('L'); b.wait(20)
b.g.cmd('watch d42a 3')
b.press('A',4); b.wait(200)
b.g.cmd('wflush'); b.g.close()
