from kt import *
rom=sys.argv[1]
b = start(rom, out='kl_'+rom)
k=b.mapk('Route1'); G=grid_of(b.db.r, b.db.maps[k]['hdr']); H,W=len(G),len(G[0])
hops=[(x,y,hex(G[y][x])) for y in range(H) for x in range(W) if 0xA0<=G[y][x]<=0xA7]
print(H,W,len(hops), hops[-20:])
b.g.close()
b = start(rom, out='kl_'+rom)
b.warp('Route1',12,29); b.wait(80); b.clear_text()
print('start', b.where())
for i in range(3): b.step('U'); print('U ->', b.where())
b.warp('Route1',12,25); b.wait(80); b.clear_text()
print('start', b.where())
fs=seq(b,'D',60,'d',2); print('D ->', b.where())
sheet(fs[:24], b.out+'.png', W=8)
b.g.close()
