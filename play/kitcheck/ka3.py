from kt import *
rom = sys.argv[1]
st = 'kitbase.st' if rom=='kit60' else 'blogbase2.st'
b = start(rom, state=st, out='a3_'+rom)
b.warp('GoldenrodCity', 21, 20); b.wait(80); b.clear_text()
b.step('D'); b.wait(40)
fs = seq(b, 'U', 40, 'up', 2)                       # A3: walking up
b.wait(30)
fs += seq(b, 'RB', 40, 'dash', 2)                   # A7: dash
fs += seq(b, 'LB', 40, 'turn', 2)                   # A8/A7: turn while dashing
b.wait(40); p=b.out+'/stop.png'; b.g.shot(p); fs.append(p)
sheet(fs, b.out + '.png', W=10)
print(b.out+'.png')
b.g.close()
