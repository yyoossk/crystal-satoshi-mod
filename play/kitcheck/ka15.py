from kt import *
rom=sys.argv[1]
def run(slot, m, x, y, d, n):
    b = start(rom, state=('kitbase.st' if rom=='kit60' else 'blogbase2.st'), out='a15')
    b.bank1(); b.g.poke(0xD833, slot)
    x, y = straight(b, m, d, n); b.warp(m, x, y); b.wait(80); b.clear_text()
    b.step({'L':'R','R':'L','U':'D','D':'U'}[d]); b.wait(40); b.step(d); b.wait(40); b.step(d); b.wait(40)
    k, x0, y0 = b.where()
    b.g.down(d); f = 0
    while True:
        b.g.wait(1); f += 1
        b.bank1(); yy, xx = b.peek(W_Y, 2)
        if abs(xx - x0) + abs(yy - y0) >= n or f > 400: break
    b.g.up(d); b.g.close(); return f
for m,x,y,d,n in (('GoldenrodCity',0,0,'R',7),('Route29',0,0,'L',7),('CeladonCity',0,0,'R',7)):
    print(m, 'follow', run(0,m,x,y,d,n), 'none', run(0xff,m,x,y,d,n))
