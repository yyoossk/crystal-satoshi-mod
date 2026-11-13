import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq, seq
make_test_rom(SC+'/build/p70.gbc')
b=Bot(state=SC+'/play/blogbase2.st', out=SC+'/run/bdash')
b.warp('VioletCity',20,20); b.wait(100); b.clear_text(); b.step('L')
fs=seq(b,'BR',40,'r',4)+seq(b,'BL',40,'l',4)+seq(b,'BD',24,'d',4)
sheet(fs, SC+'/run/bdash.png', W=10)
