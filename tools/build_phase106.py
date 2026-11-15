#!/usr/bin/env python3
"""Phase 106: S.S. Anne's doors and stairs.
 * The bow (deck): the door back into the ship (Red's (13,6) / (13,7), on the right) could not be
used by walking right.  The ported ship tileset gives the door block ($24) Crystal's carpet-up / carpet-down
collisions ($78 / $70) on its right half, so the warp only fired when pressing up (or down).  Both are now
COLL_WARP_CARPET_RIGHT ($7E): walking right through the door goes back to 3F, as in Red.  (Block $24 is only used on
the bow; its other copies, the deck's three bollards on the top wall, have no warp, so nothing else changes.)
 * Red's stairs in the captain's room (0,7) (down to 2F), 1F (37,15) (down to B1F) and B1F (27,5) (up to 1F) had
   carpet-down collisions: after arriving on them and stepping off, stepping back on did nothing (only pressing down
   while standing on them warped).  They are now $73 as phase 26's museum stairs: stepping on them warps at once, arriving on them does not
   (with $7A, arriving on the captain's room stairs reset the game).
usage: build_phase106.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
sys.path.insert(0, os.path.join(SC, 'play'))
from mapdb import DB
import portmaps as PM
from portlib import Space

BOW, DOOR_XY, BLOCK = (26, 45), (13, 6), 0x24
COLL_WARP_CARPET_RIGHT, COLL_STAIRCASE = 0x7E, 0x73     # $73: warps when stepped on, no step on arriving (phase 26)
STAIRS = [((26, 47), (0, 7)), ((26, 41), (37, 15)), ((26, 44), (27, 5))]   # captain's room, 1F, B1F


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    db = DB(src_rom)
    m = db.maps[BOW]; assert [(w[0], w[1]) for w in db.warps(BOW)] == [(13, 6), (13, 7)]
    a = attrs(rom, m['hdr']); ts = rom[m['hdr'] + 1]
    bo = a['blkbank'] * 0x4000 + a['blk'] - 0x4000
    assert rom[bo + (DOOR_XY[1] // 2) * a['w'] + DOOR_XY[0] // 2] == BLOCK
    for k, mm in db.maps.items():                      # the block is the bow's alone
        if k == BOW or rom[mm['hdr'] + 1] != ts: continue
        aa = attrs(rom, mm['hdr']); b2 = aa['blkbank'] * 0x4000 + aa['blk'] - 0x4000
        assert BLOCK not in rom[b2:b2 + aa['w'] * aa['h']], k
    co = PM.Tilesets(rom, Space(rom)).coll_off(ts) + 4 * BLOCK
    assert rom[co:co + 4] == bytes([0x00, 0x78, 0x00, 0x70]), rom[co:co + 4].hex()
    rom[co + 1] = rom[co + 3] = COLL_WARP_CARPET_RIGHT
    for k, (x, y) in STAIRS:
        mm = db.maps[k]; aa = attrs(rom, mm['hdr']); b2 = aa['blkbank'] * 0x4000 + aa['blk'] - 0x4000
        blk = rom[b2 + (y // 2) * aa['w'] + x // 2]; q = (y % 2) * 2 + x % 2
        assert (x, y) in [(w[0], w[1]) for w in db.warps(k)] and rom[mm['hdr'] + 1] == ts
        for k2, m2 in db.maps.items():
            if k2 == k or rom[m2['hdr'] + 1] != ts: continue
            a2 = attrs(rom, m2['hdr']); b3 = a2['blkbank'] * 0x4000 + a2['blk'] - 0x4000
            assert blk not in rom[b3:b3 + a2['w'] * a2['h']], (k, k2, hex(blk))
        c = PM.Tilesets(rom, Space(rom)).coll_off(ts) + 4 * blk + q
        assert rom[c] == 0x70, (k, rom[c])
        rom[c] = COLL_STAIRCASE
        print('S.S. Anne stairs %s %s: block %02X -> stairs $73' % (k, (x, y), blk))
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('S.S. Anne bow door: tileset %02X block %02X collision -> 00 7E 00 7E' % (ts, BLOCK))


if __name__ == '__main__':
    main()
