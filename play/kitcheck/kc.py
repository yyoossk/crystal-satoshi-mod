from kt import *
rom=sys.argv[1]
b = start(rom, state=('kitbase.st' if rom=='kit60' else 'blogbase2.st'), out='c_'+rom)
b.wait(30)
b.press('S',40); b.g.shot(b.out+'/menu.png')
b.press('D',20)
fs = tap(b,'A',60,'party')                 # C2
u = uniq(fs); print('party frames', len(u))
sheet(u, b.out+'_party.png', W=8)
# C3: swap first two with SELECT? use A -> ならびかえ
b.press('A',30); b.g.shot(b.out+'/sub.png')
b.press('B',30)
fs = tap(b,'A',20,'sub')                   # D4: submenu open
sheet(uniq(fs), b.out+'_sub.png', W=8)
b.wait(40); b.press('D',30); b.g.shot(b.out+'/sub2.png'); b.press('A',40); b.press('D',30); b.g.shot(b.out+'/sel.png')
fs = tap(b,'A',120,'swap')                   # C3
u=uniq(fs); print('swap frames', len(u)); sheet(u, b.out+'_swap.png', W=8)
b.g.close()
