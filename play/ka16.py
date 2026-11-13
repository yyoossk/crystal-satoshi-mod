from kt import *
rom=sys.argv[1]; slot=int(sys.argv[2]) if len(sys.argv)>2 else 1
b = start(rom, out='a16_%s_%d'%(rom,slot))
allf=[]
for m,d in (('GoldenrodCity','R'),('VioletCity','R'),('EcruteakCity','R'),('GoldenrodPokecenter1F','L')):
    x,y = straight(b, m, d, 3)
    b.bank1(); b.g.poke(0xD833, slot)
    b.warp(m,x,y); b.wait(80); b.clear_text()
    b.step(d); b.wait(30); b.step(d); b.wait(40)
    before=b.out+'/%s_before.png'%m; b.g.shot(before)
    b.face({'L':'R','R':'L'}[d]); b.wait(20)
    fs = tap(b,'A',120,m+'_talk',every=1)
    for i in range(6): b.press('A',40)
    b.press('B',40); b.wait(60)
    after=b.out+'/%s_after.png'%m; b.g.shot(after)
    u=uniq(fs); allf += [before]+u[:14]+[after]
    print(m, len(u))
sheet(allf, b.out+'.png', W=8)
b.g.close()
