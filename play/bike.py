import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq, seq
make_test_rom(SC+'/build/p71.gbc')
b=Bot(state=SC+'/play/vir_p70.st', out=SC+'/run/bike')
b.bank1(); b.g.poke(0xD950,1)
b.warp('Route1',10,20); b.wait(120); b.clear_text(); b.bank1(); b.g.poke(0xD950,1); b.warp('Route1',10,21); b.wait(120)
fs=seq(b,'D',16,'d',4)+seq(b,'L',16,'l',4)+seq(b,'U',16,'u',4)
sheet(fs, SC+'/run/bike.png', W=6, scale=2)
