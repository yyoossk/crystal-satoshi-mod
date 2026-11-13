import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq, seq
ROM=sys.argv[1]
make_test_rom(SC+'/build/%s.gbc'%ROM)
b=Bot(state=SC+'/play/vir_%s.st'%ROM, out=SC+'/run/nf10')
r=b.travel('Route1'); print(b.where())
b.goto(10,32); print(b.where())
fs=seq(b,'D',90,'d',3)      # into Pallet: sign
print(b.where())
fs2=seq(b,'',150,'w',5)
sheet(uniq(fs+fs2)[:48], SC+'/run/nf10.png', W=8)
b.goto(10,1); fs=seq(b,'U',40,'u',4); b.goto(6,24); fs+=seq(b,'',600,'w',8)
sheet(uniq(fs)[-24:], SC+'/run/nf10b.png', W=8)
