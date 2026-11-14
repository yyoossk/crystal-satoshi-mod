#!/usr/bin/env python3
"""Phase 77: Red's eastern shore tile ($32) is water, as in Red.
 Red lets the player surf onto tile $32 (the eastern coastline tile: CollisionCheckOnWater / IsNextTileShoreOrWater);
 the ported Overworld tileset (id 40) made it a wall, because only $14 was taken as water.  So on Route 20 the column
 x=62 (blocks $65 / $18 edge) was a wall and the Fuchsia side of the route could not reach the Seafoam Islands.
 * every quadrant of the Overworld tileset whose collision tile is $32 and is a wall becomes COLL_WATER.
usage: build_phase77.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
import portmaps as PM
from portlib import Space, COLL_WALL, COLL_WATER

OVERWORLD_TS = 40
QUADS = ((1, 0), (1, 2), (3, 0), (3, 2))


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    T = PM.Tilesets(rom, Space(rom))
    e = T.entry(OVERWORLD_TS); mo = fo(e[3], e[4] | e[5] << 8); co = fo(e[6], e[7] | e[8] << 8)
    n = (co - mo) // 16
    fixed = []
    for b in range(n):
        for q, (r, c) in enumerate(QUADS):
            if rom[mo + 16 * b + r * 4 + c] == 0x32 and rom[co + 4 * b + q] == COLL_WALL:
                rom[co + 4 * b + q] = COLL_WATER; fixed.append((b, q))
    assert fixed, 'nothing to fix'
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('Overworld $32 shore quadrants -> water:', ', '.join('%02X/%d' % f for f in fixed))


if __name__ == '__main__':
    main()
