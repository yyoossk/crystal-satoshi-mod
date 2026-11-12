import collections
from t64a import *
import t57c
r = open(SC + '/build/p64.gbc', 'rb').read()
fc = r[0xD1F3:0xD1F9]
def fishstats(b, k, rod, n=20):
    asm = bytes([0x3E, k[0], 0xEA, 0x7B, 0xDC, 0x3E, k[1], 0xEA, 0x7C, 0xDC])
    asm += bytes([0x16, 0x01, 0x1E, rod]) + fc + bytes([0x7A, 0xEA, 0xDD, 0xC2, 0x3E, 24, 0xEA, 0x7B, 0xDC, 0x3E, 4, 0xEA, 0x7C, 0xDC, 0xC9])
    for i, v in enumerate(asm): b.g.cmd('rpoke %x %d' % (SOFF + 0x40 + i, v))
    c = collections.Counter()
    for i in range(n):
        b.g.cmd('rpoke %x %d' % (0xC2DD, 0)) if False else None
        b.poke(0xC2DD, 0xEE) if hasattr(b,'poke') else b.g.poke(0xC2DD,0xEE)
        b.script([0x0E, SB, (SA + 0x40) & 0xFF, (SA + 0x40) >> 8], 40)
        b.bank1(); v = b.peek(0xC2DD)[0]; c[INV.get(v, v) if v not in (0,0xEE) else ('-' if v==0 else 'norun')] += 1
    return dict(c)
b = Bot(state='p64nb.st', out=OUT+'/fish')
for k,nm in (((17,1),'kanto'),((26,88),'safari'),((10,1),'route32')):
    for rod in (0,1,2):
        print(nm,k,rod,fishstats(b,k,rod),flush=True)
