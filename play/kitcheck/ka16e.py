from kt import *
rom=sys.argv[1]; slot=int(sys.argv[2])
b = start(rom, state=('kitbase.st' if rom=='kit60' else 'blogbase2.st'), out='a16e_%s'%rom)
if rom=='kit60':
    b.bank1(); b.g.poke(0xdc9d+2, 25); b.g.poke(0xdca5+0x30, 25)
allf=[]
for m,d in (('GoldenrodCity','R'),('VioletCity','R'),('EcruteakCity','R'),('GoldenrodPokecenter1F','L'),('AzaleaTown','R')):
    x,y = straight(b, m, d, 2)
    b.bank1(); b.g.poke(0xD833, slot)
    b.warp(m,x,y); b.wait(80); b.clear_text()
    b.step(d); b.wait(30); b.step(d); b.wait(40)
    b.face({'L':'R','R':'L'}[d]); b.wait(20)
    before=b.out+'/%s_0.png'%m; b.g.shot(before)
    fs = tap(b,'A',160,m,every=1)
    for i in range(3): b.press('B',40)
    b.wait(30); after=b.out+'/%s_z.png'%m; b.g.shot(after)
    u=uniq(fs); allf += u+[after]
    print(m, len(u), b.where())
sheet(allf, b.out+'.png', W=10)
b.g.close()
