import sys; sys.path.insert(0,'play'); from bot import *
for st in ['k27','k16']:
    b=Bot(state=SC+'/play/%s.st'%st, out=SC+'/play/run/chk4')
    for (x,y) in [(15,1),(16,1)]:
        b.warp('VermilionPortPassage',x,y); b.wait(40); b.step('U'); b.wait(30); b.g.down('U'); b.wait(30); b.g.up('U'); b.wait(90); print(st,'pass',(x,y), b.where(), b.names.get(b.where()[0]))
