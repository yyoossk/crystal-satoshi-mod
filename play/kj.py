from kt import *
b = start('p69', out='kj')
print(b.objs_of(b.mapk('Route1')))
b.warp('Route1',6,22); b.wait(60); b.clear_text()
fs=seq(b,'',400,'w',4)
sheet(uniq(fs)[:48], b.out+'.png', W=8)
b.g.close()
