#!/usr/bin/env python3
"""Phase 114: Saffron Gym's warp pads (2026-11-17, found in the honest playthrough).
 Phase 112's room gave each pad the collision phase 25's rule picks for a door: a staircase when the tile below is
 floor, else a carpet (a warp only when the player walks off in that direction).  Saffron Gym's pads often have a wall
 below or stand at the room's edge: 15 of its 32 pads were carpets (13 "down", 2 "right"), so stepping on them did
 nothing and Sabrina's room could not be reached; and a staircase makes the arriving player step down out of it.
 In Red a pad warps when stepped on and the player stays on the pad he arrives at: that is Crystal's warp panel
 ($7C: a step-on warp, no step out on arrival, the teleport sound).  Every pad of the gym is a warp panel now.  Only
 the gym's own block variants are changed (each changed block quadrant is checked to be a pad wherever it is used).
usage: build_phase114.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'play'))
from lib import *
from portlib import *
import portmaps as PM

GYM = (25, 4)
CARPETS = (0x70, 0x76, 0x78, 0x7E, 0x7A)     # (carpets and the staircase)
WARP_PANEL = 0x7C


def main():
    src, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src, 'rb').read())
    from mapdb import DB
    db = DB(src)
    TSO = PM.Tilesets(rom, Space(rom))
    m = db.maps[GYM]; ts = rom[m['hdr'] + 1]; co = TSO.coll_off(ts)
    a = attrs(rom, m['hdr']); bo = a['blkbank'] * 0x4000 + a['blk'] - 0x4000; w, h = a['w'], a['h']
    pads = {(x, y) for x, y, i, g, n in db.warps(GYM) if (g, n) == GYM}
    quads = {}
    for (x, y) in pads:
        b = rom[bo + (y // 2) * w + x // 2]; q = (y % 2) * 2 + x % 2
        if rom[co + 4 * b + q] in CARPETS: quads.setdefault((b, q), set()).add((x, y))
    # every use of those quadrants (in every map of this tileset) must be one of the gym's pads
    for k2, m2 in db.maps.items():
        if rom[m2['hdr'] + 1] != ts: continue
        a2 = attrs(rom, m2['hdr']); b3 = a2['blkbank'] * 0x4000 + a2['blk'] - 0x4000
        for i in range(a2['w'] * a2['h']):
            for q in range(4):
                if (rom[b3 + i], q) in quads:
                    p = ((i % a2['w']) * 2 + q % 2, (i // a2['w']) * 2 + q // 2)
                    assert k2 == GYM and p in pads, ('shared quadrant', k2, p, rom[b3 + i], q)
    n = 0
    for (b, q), ps in sorted(quads.items()):
        rom[co + 4 * b + q] = WARP_PANEL; n += len(ps)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('Saffron Gym: %d pads (%d block quadrants) -> warp panel' % (n, len(quads)))


if __name__ == '__main__':
    main()
