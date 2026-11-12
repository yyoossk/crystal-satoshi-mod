from kt import *
rom = sys.argv[1]
b = start(rom, out='a3b_'+rom)
b.warp('GoldenrodCity', 21, 24); b.wait(80); b.clear_text()
seq(b,'U',40,'pre',40); b.wait(40)
fs = seq(b, 'U', 36, 'up', 1)
crops(fs[:30], b.out+'.png', box=(48,40,112,104))
b.g.close()
