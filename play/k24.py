import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k23e.st', out=SC+'/play/run/k24')
b.setflag(*range(0x23,0x2B))
b.warp((16,2),14,4); b.wait(60); b.ev(); b.step('U'); b.wait(80)
b.go_warp((16,3)); b.ev(); print(b.where())
for room in [(16,3),(16,4),(16,5),(16,6)]:
    b.ev(); print('room', b.where())
    b.talk_to(5,7); b.ev()
    nxt=(room[0],room[1]+1)
    b.go_warp(nxt); b.ev()
    print(b.where(), b.log[-2:])
b.g.save_state(SC+'/play/k24a.st')
