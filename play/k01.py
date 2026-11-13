import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/ng0.st', out=SC+'/play/run/k01')
b.go_warp('RedsHouse1F'); b.shot('1f')
b.go_warp('PalletTown'); b.shot('pallet')
print(b.where())
b.goto(10,1); b.shot()
for i in range(3): b.step('U'); b.shot()
for i in range(40):
    b.press('A',40); b.shot()
    if b.where()[0]==b.ids['OaksLab'] and b.tilemap()[20*12]!=0x79: break
print(b.where(), b.log)
b.g.save_state(SC+'/play/k01.st')
b.sheet('a')
