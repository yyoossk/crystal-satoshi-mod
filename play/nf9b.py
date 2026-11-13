import sys; sys.path.insert(0,'play')
from t64a import *
ROM=sys.argv[1]
make_test_rom(SC+'/build/%s.gbc'%ROM)
b=Bot(state=SC+'/play/nf8_%s.st'%ROM, out=SC+'/run/nf9b')
r=b.travel('ViridianCity'); print(b.where())
def dump(tag):
    b.bank1()
    u=b.peek(0xD185,64); print(tag, ' '.join('%02x:%02x'%(u[2*i],u[2*i+1]) for i in range(32) if u[2*i]))
    for i in range(13):
        o=b.peek(0xD4C9+0x28*i,4)
        if o[0]: print('   obj',i,'spr %02x tile %02x'%(o[0],o[2]))
dump('viridian')
b.g.save_state(SC+'/play/vir_%s.st'%ROM)
r=b.travel('Route22'); print(b.where()); b.wait(30)
dump('route22')
b.warp('Route22',39,9); b.wait(100); b.clear_text()
dump('route22 warp')
