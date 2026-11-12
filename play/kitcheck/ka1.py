from kt import *
cases = [('CherrygroveCity','R'),('Route29','L'),('GoldenrodCity','U'),('Route34','U'),('VioletCity','R'),('Route36','L'),('Route31','L'),('PalletTown','U'),('ViridianCity','D'),('CeruleanCity','U')]
rom = sys.argv[1] if len(sys.argv)>1 else 'p66'
keys = sys.argv[2] if len(sys.argv)>2 else ''
for m, d in cases:
    b = start(rom, out='a1_%s_%s%s'%(m,d,keys))
    try: c = go_edge(b, m, d, 3)
    except IndexError: print(m,d,'no edge'); b.g.close(); continue
    k0 = b.where()
    rec = hold(b, d + keys, 110, shots=set(range(0,110,2)))
    maps = [r[2] for r in rec]; ch = next((i for i in range(1,len(maps)) if maps[i]!=maps[i-1]), None)
    print(m, d, 'start', k0, 'end', rec[-1][2:], 'mapchange@', ch, 'stall', stall(rec[3:]), flush=True)
    b.g.close()
