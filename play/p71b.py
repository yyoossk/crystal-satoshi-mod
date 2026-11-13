import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq, seq
make_test_rom(SC+'/build/p71.gbc')
b=Bot(state=SC+'/play/vir_p70.st', out=SC+'/run/p71b')
b.strong(4,60)
b.warp((26,84),27,33); b.wait(100); b.clear_text(); b.step('R')
fs=[]
for i in range(30):
    b.wait(30); fs.append(b.shot())
    if b.textbox() and not b.in_battle(): b.press('A',20)
# bike: give bicycle and use via state flag: wPlayerState=1 (PLAYER_BIKE)
sheet(uniq(fs)[-12:], SC+'/run/p71b.png', W=6, scale=2)
