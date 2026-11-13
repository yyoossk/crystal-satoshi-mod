from kt import *
rom=sys.argv[1]
b = start(rom, out='d2_'+rom)
b.script([0x5C, 0x13, 20, 0x5E, 0x5F], 30)
fs=[]
for i in range(60):
    b.wait(10); p=b.out+'/w%02d.png'%i; b.g.shot(p); fs.append(p)
fs += tap(b,'A',60,'a',every=3)
sheet(uniq(fs), b.out+'.png', W=10)
b.g.close()
