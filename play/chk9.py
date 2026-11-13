import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k16.st', out=SC+'/play/run/chk9')
pn={l.split()[0]:tuple(map(int,l.split()[1].split(':'))) for l in open(SC+'/play/portnames.txt')}
k=pn['PokemonMansion1F']
b.warp(k,26,26); b.wait(60); print(b.where())
for d in 'ULDRD':
    b.g.down(d); b.wait(20); b.g.up(d); b.wait(40); print(d,b.where())
G=grid_of(b.db.r,b.db.maps[k]['hdr'])
for y in range(22,len(G)): print(y,' '.join('%02x'%G[y][x] for x in range(20,len(G[0]))))
print(b.peek(0xDBC1,1), [hex(v) for v in b.peek(0xD210,2)])
