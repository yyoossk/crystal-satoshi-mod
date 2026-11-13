from kt import *
rom=sys.argv[1]; slot=int(sys.argv[2]); m=sys.argv[3]; d=sys.argv[4]
b = start(rom, state=('kitbase.st' if rom=='kit60' else 'blogbase2.st'), out='a16c_%s_%d_%s'%(rom,slot,m))
x,y = straight(b, m, d, 3)
b.bank1(); b.g.poke(0xD833, slot)
b.warp(m,x,y); b.wait(80); b.clear_text()
b.step(d); b.wait(30); b.step(d); b.wait(40)
print('pos', b.where())
b.face({'L':'R','R':'L','U':'D','D':'U'}[d]); b.wait(20)
fs = tap(b,'A',400,'talk',every=4)
print('pos', b.where(), b.in_battle())
sheet(fs, b.out+'.png', W=10)
b.g.close()
