import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k04b.st', out=SC+'/play/run/k05')
b.strong(); print(b.peek(0xDC9D,8))
b.go_warp('PalletTown'); b.shot()
b.warp_near('ViridianCity',29,20); b.shot('vc')
b.step('U'); b.wait(60); b.shot('mart')
print(b.where(), b.objpos())
for i in range(25):
    b.press('A',40); b.shot()
print(b.where())
b.g.save_state(SC+'/play/k05.st')
b.sheet('a',8)
