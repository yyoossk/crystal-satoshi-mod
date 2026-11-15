#!/usr/bin/env python3
"""Phase 107: the S.S. Anne leaving looks as in the Red full-color hack.
 * The dock's water did not move at all (the ported ship-port tileset had no tile animation), so only the scrolled
   band around the ship moved and the water seemed to sail off with the ship.  Red animates the water tile ($14)
   on the dock as everywhere (UpdateMovingBgTiles: every 20 frames the tile is rotated one pixel, 4 times right then
   4 times left): the dock tileset now has that animation (Crystal's tile-animation routines ReadTileToAnimBuffer /
   ScrollTileRightLeft / WriteTileFromAnimBuffer, then waits: one step every 20 frames).
 * The smoke puffs were white; the Red full-color hack draws them with its OBJ palette 3 (light orange / brown,
   read from the hack during the departure): palette 7 of phase 45 now has those colours.
usage: build_phase107.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
import portmaps as PM
from portlib import Space

DOCK_TS = 0x27
ANIM_BANK = 0x3F
T14, TILE_BUF = 0x9140, 0xCF35                    # vTiles2 tile $14, wTileAnimBuffer
READ, SCROLL_RL, WRITE, WAIT, DONE = 0x46A2, 0x4309, 0x4696, 0x42FE, 0x42FB
SMOKE_BANK = 0x59
SMOKE_PAL = [(27, 31, 27), (31, 24, 17), (15, 10, 3), (0, 0, 0)]     # Red full-color hack, OBJ palette 3


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read()); log = []
    def w(v): return bytes([v & 0xFF, v >> 8])
    # check Crystal's routines: the unused water animation 3F:4103 = read $14 / scroll / write
    u = fo(ANIM_BANK, 0x4103)
    assert rom[u:u + 12] == w(T14) + w(READ) + w(TILE_BUF) + w(SCROLL_RL) + w(T14) + w(WRITE)
    assert rom[u + 12:u + 16] == bytes(2) + w(WAIT)
    tab = w(T14) + w(READ) + w(TILE_BUF) + w(SCROLL_RL) + w(T14) + w(WRITE) + (bytes(2) + w(WAIT)) * 16 + bytes(2) + w(DONE)
    f, n = bank_free_tail(rom, ANIM_BANK); f += 2; assert n > len(tab) + 8
    rom[f:f + len(tab)] = tab; ta = 0x4000 + f % 0x4000
    TS = PM.Tilesets(rom, Space(rom)); e = TS.tab + 15 * DOCK_TS
    assert rom[e + 9:e + 11] == w(0x42E7), rom[e + 9:e + 11].hex()          # no animation before
    rom[e + 9:e + 11] = w(ta)
    log.append('dock tileset %02X: water animation %02X:%04X (20 frames a step)' % (DOCK_TS, ANIM_BANK, ta))
    # smoke palette (phase 45's prep: ld hl,wOBPals2+7*8 / ld c,4 / .pp ld [hl],$ff / inc hl / ld [hl],$7f / inc hl / dec c / jr nz)
    old = bytes.fromhex('21 f8 d0 0e 04 36 ff 23 36 7f 23 0d 20 f7')
    s = fo(SMOKE_BANK, 0x4000); i = rom.index(old, s, s + 0x4000)
    f2, n2 = bank_free_tail(rom, SMOKE_BANK); f2 += 2; assert n2 > 32
    pal = b''.join(w(r | g << 5 | b << 10) for r, g, b in SMOKE_PAL)
    a2 = 0x4000 + f2 % 0x4000
    code = bytes([0x21, 0xF8, 0xD0, 0x11]) + w(a2 + 15) + bytes([0x0E, 8, 0x1A, 0x22, 0x13, 0x0D, 0x20, 0xFA, 0xC9]) + pal
    assert len(code) == 15 + 8
    rom[f2:f2 + len(code)] = code
    rom[i:i + len(old)] = bytes([0xCD]) + w(a2) + bytes(len(old) - 3)
    log.append('smoke palette: %02X:%04X' % (SMOKE_BANK, a2))
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
