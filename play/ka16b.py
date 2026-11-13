from kt import *
rom=sys.argv[1]; slot=int(sys.argv[2]); m=sys.argv[3]; d=sys.argv[4]
b = start(rom, state=('kitbase.st' if rom=='kit60' else 'blogbase2.st'), out='a16b_%s_%d_%s'%(rom,slot,m))
x,y = straight(b, m, d, 3)
b.bank1(); b.g.poke(0xD833, slot)
b.warp(m,x,y); b.wait(80); b.clear_text()
b.step(d); b.wait(30); b.step(d); b.wait(40)
b.face({'L':'R','R':'L','U':'D','D':'U'}[d]); b.wait(20)
fs = tap(b,'A',200,'talk',every=1)
fs += tap(b,'A',120,'talk2',every=1)
fs += tap(b,'B',120,'talk3',every=1)
u=uniq(fs); print(len(u))
sheet(u[:48], b.out+'.png', W=8)
b.g.close()
