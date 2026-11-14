#!/usr/bin/env python3
"""Phase 79: Red's counter tiles (talking over the counter) in every ported Red tileset.
 Red talks over its tilesets' counter tiles (tileset_headers: 3 counter tiles each); the ported tilesets made them
 plain walls, except the Lobby (phase 12) and the Museum (phase 26).  So the Cerulean bike shop's clerk could not be
 talked to (no Bicycle -> no Cycling Road), and other people behind Red's counters neither.
 * every quadrant whose collision tile is one of its Red tileset's counter tiles and is a wall becomes COLL_COUNTER.
usage: build_phase79.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
import portmaps as PM
from portlib import Space, COLL_WALL, PY

COLL_COUNTER = 0x90
QUADS = ((1, 0), (1, 2), (3, 0), (3, 2))
# ported tileset id: (Red tileset, Red blockset, Red counter tiles)
COUNTERS = {33: ('Cemetery', 'cemetery.bst', (0x12,)), 34: ('Facility', 'facility.bst', (0x12,)),
            35: ('Lobby', 'lobby.bst', (0x15, 0x36)), 41: ('Pokecenter', 'pokecenter.bst', (0x18, 0x19, 0x1E)),
            45: ('Club', 'club.bst', (0x07, 0x17)), 46: ('Museum', 'gate.bst', (0x17, 0x32)),
            47: ('Gate', 'gate.bst', (0x17, 0x32)), 48: ('ForestGate', 'gate.bst', (0x17, 0x32)),
            52: ('Dojo', 'gym.bst', (0x3A,))}


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    T = PM.Tilesets(rom, Space(rom))
    log = []
    for i, (name, bst, tiles) in COUNTERS.items():
        e = T.entry(i); mo = fo(e[3], e[4] | e[5] << 8); co = fo(e[6], e[7] | e[8] << 8)
        red = open(PY + '/gfx/blocksets/' + bst, 'rb').read()
        n = len(red) // 16
        assert rom[mo:mo + 16] == red[:16], (name, 'not the Red blockset')
        k = 0
        for b in range(n):
            for q, (r, c) in enumerate(QUADS):
                if rom[mo + 16 * b + r * 4 + c] in tiles and rom[co + 4 * b + q] == COLL_WALL:
                    rom[co + 4 * b + q] = COLL_COUNTER; k += 1
        log.append('%s (%d): %d' % (name, i, k))
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('counter quadrants:', ', '.join(log))


if __name__ == '__main__':
    main()
