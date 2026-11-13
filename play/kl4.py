from kt import *
b = start('p69', out='kl4')
b.warp('Route1',10,10); b.wait(80); b.clear_text()
for i in range(40): b.poke(0xD000,0) if False else None
r=b.goto(12,32); print('goto', r, b.where())
b.warp('Route22',33,10); b.wait(80); b.clear_text()
r=b.goto(4,8); print('goto', r, b.where())
b.g.close()
