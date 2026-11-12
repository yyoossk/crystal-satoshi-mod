from kt import *
rom=sys.argv[1]
b = start(rom, out='e1_'+rom)
fs=[]
for m,x,y in (('VermilionCity',19,18),('AzaleaTown',10,10),('CeladonCity',20,20),('GoldenrodCity',14,16),('CianwoodCity',10,30),('PewterCity',16,18)):
    b.warp(m,x,y); b.wait(80); b.clear_text()
    for i in range(4):
        b.wait(40); p=b.out+'/%s_%d.png'%(m,i); b.g.shot(p); fs.append(p)
    print(m, b.where(), len(b.objpos()))
sheet(fs, b.out+'.png', W=8)
b.g.close()
