#!/usr/bin/env python3
"""Phase 108: Vermilion Gym's door in front of Lt. Surge looks as in Red / the Red full-color hack.
Phase 75 closed the opening (block 2,2) with a plain wall block until the 2nd lock opens.  Red puts its double door
there (Red's gym block $24: the two doors, tiles $20 $21 / $30 $31, on the upper half, the floor below; opened:
the floor, SFX_GO_INSIDE).  Crystal's room (tileset 14) gets Red's four door tiles in four of its unused tile slots
($AA-$AD, VRAM bank 1), a new block $40 (the doors above, the room's floor below; walls above, floor below as
collision), and phase 75's callback puts block $40 there instead of the wall.  The tileset's graphics, blocks and
collisions are moved to a bank with room (the other maps using tileset 14 keep the same blocks).
usage: build_phase108.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
import portmaps as PM
from portlib import Space, lz
from gsclz import unlz

TS_ID = 14
NEW_TILES = [0xAA, 0xAB, 0xAC, 0xAD]
RED_DOOR = [0x20, 0x21, 0x30, 0x31]                 # Red's gym tiles (block $24)
FLOOR_BLOCK, WALL_BLOCK, DOOR_BLOCK = 0x01, 0x20, 0x40
PAL = 0x00                                          # the room's floor palette (gray)
SCRIPT_BANK = 0x63


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    TS = PM.Tilesets(rom, Space(rom)); e = TS.tab + 15 * TS_ID
    gb, ga = rom[e], rom[e + 1] | rom[e + 2] << 8
    mb, ma = rom[e + 3], rom[e + 4] | rom[e + 5] << 8
    cb, ca = rom[e + 6], rom[e + 7] | rom[e + 8] << 8
    pa = rom[e + 13] | rom[e + 14] << 8
    gfx, _ = unlz(rom, fo(gb, ga)); gfx = bytearray(gfx); assert len(gfx) == 192 * 16
    nb = (ca - ma) // 16; assert mb == cb and nb == 0x40
    meta = bytearray(rom[fo(mb, ma):fo(mb, ma) + 16 * nb]); coll = bytearray(rom[fo(cb, ca):fo(cb, ca) + 4 * nb])
    for t in NEW_TILES: assert t not in meta, hex(t)
    red = open(os.path.join(PR, 'gfx/tilesets/gym.2bpp'), 'rb').read()
    for t, rt in zip(NEW_TILES, RED_DOOR):
        i = t - 0x80 + 0x60
        gfx[16 * i:16 * i + 16] = red[16 * rt:16 * rt + 16]
    fl = meta[16 * FLOOR_BLOCK:16 * FLOOR_BLOCK + 16]
    a_, b_, c_, d_ = NEW_TILES
    meta += bytes([a_, b_, a_, b_, c_, d_, c_, d_]) + fl[8:16]
    wc = coll[4 * WALL_BLOCK:4 * WALL_BLOCK + 4]; fc = coll[4 * FLOOR_BLOCK:4 * FLOOR_BLOCK + 4]
    coll += bytes([wc[0], wc[1], fc[2], fc[3]])
    # palette map (bank 13): two tiles a byte
    po = fo(0x13, pa)
    for t in NEW_TILES:
        j = t // 2                                 # tiles $00-$5F: bytes $00-$2F; $60-$7F: $30-$3F; $80-$DF: $40-$6F
        rom[po + j] = PAL << 4 | PAL
    # put the new data where there is room
    data = lz(bytes(gfx))
    need = len(data) + len(meta) + len(coll) + 16
    nb_ = next(x for x in range(0x40, len(rom) // 0x4000) if bank_free_tail(rom, x)[1] >= need)
    f, n = bank_free_tail(rom, nb_); f += 4
    def put(blob):
        nonlocal f
        o = f; rom[o:o + len(blob)] = blob; f += len(blob); return 0x4000 + o % 0x4000
    g2 = put(data); m2 = put(bytes(meta)); c2 = put(bytes(coll))
    rom[e:e + 9] = bytes([nb_, g2 & 0xFF, g2 >> 8, nb_, m2 & 0xFF, m2 >> 8, nb_, c2 & 0xFF, c2 >> 8])
    # phase 75's callback: changeblock 4,4,WALL -> DOOR
    s = fo(SCRIPT_BANK, 0x4000)
    hits = [m.start() for m in re.finditer(rb'\x79\x04\x04\x20\x8f', rom[s:s + 0x4000])]
    assert len(hits) == 1, hits
    rom[s + hits[0] + 3] = DOOR_BLOCK
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('tileset %d -> bank %02X (gfx %04X, blocks %04X, coll %04X); door block %02X; callback %02X:%04X'
          % (TS_ID, nb_, g2, m2, c2, DOOR_BLOCK, SCRIPT_BANK, 0x4000 + hits[0]))


if __name__ == '__main__':
    main()
