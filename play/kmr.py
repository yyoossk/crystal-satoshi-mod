from kt import *
rom=sys.argv[1]
b = start(rom, out='mr_'+rom)
k=b.mapk('MoveDeletersHouse'); print(b.objs_of(k))
b.warp(k, 5, 6); b.wait(80); b.clear_text()
print(b.where(), b.objpos())
b.step('U'); b.wait(20); b.face('U'); b.wait(10)
fs=[]
for i in range(14):
    b.press('A',60); p=b.out+'/%02d.png'%i; b.g.shot(p); fs.append(p)
sheet(fs, b.out+'.png', W=7)
b.g.close()
