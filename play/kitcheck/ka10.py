from kt import *
rom=sys.argv[1]
b = start(rom, out='a10_'+rom)
b.setev(0x44); b.bank1(); v=b.peek(0xD836)[0]; b.g.poke(0xD836, v & 0xFE)
b.warp('IlexForest', 8, 25); b.wait(100); b.clear_text()
b.step('U'); b.wait(30); b.step('U'); b.wait(60)
b.g.shot(b.out+'/s1.png'); print(b.where(), b.objpos())
b.face('U'); b.press('A',60)
for i in range(12):
    b.g.shot(b.out+'/t%02d.png'%i); b.press('A',50)
    if b.in_battle(): break
print('battle', b.in_battle())
b.g.shot(b.out+'/b.png')
sheet([b.out+'/s1.png']+sorted(__import__('glob').glob(b.out+'/t*.png'))+[b.out+'/b.png'], b.out+'.png', W=8)
b.g.close()
