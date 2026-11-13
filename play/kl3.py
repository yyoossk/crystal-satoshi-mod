from kt import *
b = start('p69', out='kl3')
from collections import Counter
for k,m in b.db.maps.items():
    try: G=grid_of(b.db.r, m['hdr'])
    except Exception: continue
    c=Counter(v for row in G for v in row if 0xA0<=v<=0xA7)
    if c: print(k, m.get('name'), m['hdr'][0] if isinstance(m['hdr'],(bytes,list)) else '', dict((hex(a),n) for a,n in c.items()))
b.g.close()
