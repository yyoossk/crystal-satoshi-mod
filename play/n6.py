import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq, seq
make_test_rom(SC+'/build/p69.gbc')
b=Bot(state=SC+'/play/n5.st', out=SC+'/run/n6')
b.warp('PalletTown',10,2); b.wait(60); b.clear_text()
fs=seq(b,'U',200,'u',4)
print(b.where())
b.goto(6,24) ; print(b.where())
fs+=seq(b,'',400,'w',6)
u=uniq(fs)
sheet(u[-36:], SC+'/run/n6.png', W=6, scale=1)
b.g.save_state(SC+'/play/n6.st')
