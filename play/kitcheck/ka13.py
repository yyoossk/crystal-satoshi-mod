from kt import *
rom=sys.argv[1]
b = start(rom, out='a13_'+rom)
fs=[]
first=[1]
def openparty(tag):
    b.press('S',40)
    if first: b.press('D',20); first.clear()
    b.press('A',80)
    p=b.out+'/%s.png'%tag; b.g.shot(p); fs.append(p)
    b.press('B',60); b.press('B',40); b.wait(30)
openparty('n1'); openparty('n2')
for st,name in ((2,'slp'),(8,'psn'),(0x10,'brn'),(0x20,'frz'),(0x40,'par')):
    b.bank1(); b.g.poke(0xdcc5, st); b.g.poke(0xdcc5+0x24*0, st)
    openparty(name)
b.bank1(); b.g.poke(0xdcc5, 0)
# all six statuses on different mons
for i,st in enumerate((2,8,0x10,0x20,0x40,0)):
    b.g.poke(0xdcc5+0x30*i, st)
openparty('all'); openparty('all2')
crops(fs, b.out+'.png', box=(0,0,160,100), W=4, scale=2)
b.g.close()
