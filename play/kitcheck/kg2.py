from kt import *
rom=sys.argv[1]
b = start(rom, out='g2_'+rom)
fs=[]
for mvs in [tuple(int(x,16) for x in sys.argv[2].split(','))]:
    b.bank1()
    for i,mv in enumerate(mvs): b.g.poke(0xdca5+2+i, mv)
    b.press('S',40)
    for i in range(8): b.press('U',12)
    b.press('D',12); b.press('A',80); b.press('A',60)
    p=b.out+'/%02x.png'%mvs[3]; b.g.shot(p); fs.append(p)
    for i in range(4): b.press('B',40)
sheet(fs, b.out+'.png', W=4)
b.g.close()
