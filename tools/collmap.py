"""print a Crystal map's collision grid: collmap.py ROM MAPNAME"""
import sys
from portlib import *
import portmaps as PM
def grid(rom, name):
    h = hdr_index(name); a = attrs(rom, h)
    ts = rom[h + 1]
    TS = PM.Tilesets(rom, Space(rom)); co = TS.coll_off(ts)
    w, hh = a['w'], a['h']; bo = fo(a['blkbank'], a['blk'])
    G = [[0] * (2 * w) for _ in range(2 * hh)]
    for by in range(hh):
        for bx in range(w):
            b = rom[bo + by * w + bx]
            for q in range(4):
                G[2 * by + q // 2][2 * bx + q % 2] = rom[co + 4 * b + q]
    return G
if __name__ == '__main__':
    rom = open(sys.argv[1], 'rb').read(); G = grid(rom, sys.argv[2])
    sym = {0x00: '.', 0x07: '#', 0x18: ',', 0x29: '~', 0x12: 'T', 0x14: ',', 0x70: 'v', 0x71: 'D', 0x7A: 'S', 0x60: 'o'}
    print('   ' + ''.join(str(x // 10) for x in range(len(G[0]))))
    print('   ' + ''.join(str(x % 10) for x in range(len(G[0]))))
    for y, r in enumerate(G):
        print('%2d ' % y + ''.join(sym.get(c, 'L' if 0xA0 <= c <= 0xAF else '?') for c in r))
