from kt import *
rom=sys.argv[1]
b = start(rom, state=('kitbase.st' if rom=='kit60' else 'blogbase2.st'), out='c4_'+rom)
b.press('S',40)
for i in range(8): b.press('U',12)
for i in range(8):
    if b.has('ずかん'): break
fs = tap(b,'A',120,'dex',every=1)
u=uniq(fs); print('open', len(u))
b.press('A',60); b.g.shot(b.out+'/entry.png')       # dex entry
b.press('D',30); b.press('D',30); b.g.shot(b.out+'/menu.png')
fs2 = tap(b,'A',120,'area',every=2)                   # ぶんぷ?
b.g.shot(b.out+'/area.png')
fs3 = tap(b,'B',120,'back',every=1)
u3=uniq(fs3); print('back', len(u3))
sheet(u[:40]+[b.out+'/entry.png',b.out+'/menu.png',b.out+'/area.png']+u3[:37], b.out+'.png', W=10)
b.g.close()
