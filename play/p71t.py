import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq, seq
make_test_rom(SC+'/build/p71.gbc')
b=Bot(state=SC+'/play/vir_p70.st', out=SC+'/run/p71t')
b.strong(4,60)
fs=[]
b.warp('Route1',10,20); b.wait(120); b.clear_text()
fs+=seq(b,'D',20,'d',5)+seq(b,'L',20,'l',5)+seq(b,'U',20,'u',5)
# bike
b.giveitem(0x07) if False else None
b.g.poke(0xD95D,1) if False else None
# battle: grass walk
for i in range(80):
    b.step('L' if i%2 else 'R')
    if b.in_battle(): break
b.wait(200); fs.append(b.shot('battle'))
sheet(fs, SC+'/run/p71t.png', W=6, scale=2)
