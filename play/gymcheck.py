import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k08.st', out=SC+'/play/run/gc')
b.ev(shots=False)
for g in ['CeruleanGym','VermilionGym','CeladonGym','FuchsiaGym','SaffronGym']:
    k=b.ids[g]; ob=b.objs_of(k)
    lead=[o for o in ob if o[0] in (0x1D,0x1F,0x20,0x0A,0x22)][0]
    b.warp(k, lead[1], lead[2]+1); b.wait(60); b.shot(g)
    b.face('U'); 
    for i in range(10): b.press('A',40); b.shot(g)
    b.sheet(g,5)
    # escape: reset by reloading state
    b.g.load_state(SC+'/play/k08.st'); b.wait(10); b.ev(shots=False)
