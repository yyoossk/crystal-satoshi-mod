from kt import *
rom=sys.argv[1]
b = start(rom, out='f1_'+rom)
b.bank1()
for i in range(4): b.g.poke(0xdca5+0x17+i, 0)
b.script([0x5C, 0x13, 20, 0x5E, 0x5F], 30)
b.wait(560); b.press('A',30); b.wait(400)
fs = tap(b,'A',600,'s',every=6)
sheet(uniq(fs)[:40], b.out+'.png', W=8)
b.g.close()
