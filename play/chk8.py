import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k16.st', out=SC+'/play/run/chk8')
for name,(x,y),dirs in [('PokemonMansion1F',(26,26),'DD'),('PokemonMansion1F',(27,26),'DD'),('PokemonMansion2F',(18,15),'UU'),('PokemonMansion2F',(17,14),'RR'),('VictoryRoad2F',(22,17),'UU'),('VictoryRoad2F',(21,16),'RR')]:
    k=b.mapk(name) if name in b.ids else None
    if k is None:
        pn={l.split()[0]:tuple(map(int,l.split()[1].split(':'))) for l in open(SC+'/play/portnames.txt')}; k=pn[name]
    G=grid_of(b.db.r,b.db.maps[k]['hdr'])
    b.g.load_state(SC+'/play/k16.st'); b.wait(5)
    b.warp(k,x,y); b.wait(60); w0=b.where()
    for d in dirs: b.step(d); b.wait(40)
    b.wait(80); print(name,(x,y),'start',w0,'->',b.where(), [hex(G[yy][xx]) for (xx,yy) in [(x,y-1),(x,y),(x,y+1),(x+1,y),(x-1,y)] if 0<=yy<len(G) and 0<=xx<len(G[0])]); b.shot()
