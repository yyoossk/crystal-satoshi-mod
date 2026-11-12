from kt import *
rom=sys.argv[1]
b = start(rom, out='d6_'+rom)
fs=[]
def S(n):
    p=b.out+'/'+n+'.png'; b.g.shot(p); fs.append(p)
b.bank1()
for i,(mv,pp) in enumerate(((0x5e,2),(0x52,0),(0x34,25),(0x10,8))): b.g.poke(0xdca5+2+i, mv); b.g.poke(0xdca5+0x17+i, pp)
b.script([0x5C, 0x13, 20, 0x5E, 0x5F], 30)
b.wait(560); b.press('A',30); b.wait(400); S('menu')
b.bank1(); b.g.poke(0xC630, 8)
b.press('A',60); S('mv1'); b.press('D',30); S('mv2'); b.press('D',30); S('mv3'); b.press('D',30); S('mv4')
crops(fs, b.out+'.png', box=(0,40,160,144), W=5, scale=2)
b.g.close()
