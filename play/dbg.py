import sys; sys.path.insert(0,'play')
from t64a import *
from bot import _reach_set, _edge_cells, grid_of
make_test_rom(SC+'/build/p70.gbc')
b=Bot(state=SC+'/play/nf3_p70.st', out=SC+'/run/dbg')
for m,st in (('OaksLab',[(5,7)]),('PalletTown',[(12,12)]),('Route1',[(10,35)]),('ViridianCity',[(21,35)])):
    k=b.ids[m]; print(m, [(h[0],h[1],h[2],len(h[3])) for h in b.hops(k,st)])
    G=grid_of(b.db.r,b.db.maps[k]['hdr']); print('  red',getattr(G,'red',None), len(_reach_set(G,st)))
