import sys; sys.path.insert(0,'play')
from t64a import *
make_test_rom(SC+'/build/p70.gbc')
b=Bot(state=SC+'/play/vir_p70.st', out=SC+'/run/vf')
from lib import attrs, parse_events
k=(26,84); h=b.db.maps[k]['hdr']
a=attrs(b.db.r,h); ev=parse_events(b.db.r,a['scbank'],a['events'])
for o,obj in ev['objs']: print(obj.hex(), 'x',obj[2]-4,'y',obj[1]-4,'type',obj[7]&15,'sight',obj[8])
print(b.db.warps(k))
