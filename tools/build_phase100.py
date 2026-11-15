#!/usr/bin/env python3
"""Phase 100: the Pokédex for this MOD (the journey starts in Kanto).
 * Area map (ぶんぷ, Pokedex_GetArea 24:5E2B): Crystal always opened Johto's map and let the player switch to Kanto's
   only after the Hall of Fame.  Now it opens the map of the region the player is in, Kanto's can always be shown,
   and Johto's only once the player has arrived in Johto (EV_ARRIVED $34C).
 * The kit's area time switch (START, nesttime: bank 96 NestTime_Input) rebuilds the screen and then calls .right
   (24:5ED1, Crystal's) to show Kanto again: now .right is at the new place (a jump into the middle of the new .left
   froze the game).
 * The list's default order is the number order (DEXMODE_OLD): set at a new game (wLastDexMode, after the gender part
   phase 52 replaced, 01:5B7E); the player's later choice is kept as before.
usage: build_phase100.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

B = 0x24
INIT_CALL = 0x5E84                 # xor a (JOHTO_REGION) / call .GetAndPlaceNest
LRI = 0x5EB5                       # .LeftRightInput
LEFT, RIGHT_END = 0x5EC0, 0x5EE7
GETNEST, CLEARSPRITES = 0x5F46, 0x2FD7
W_PLAYERICONLANDMARK, KANTO_LANDMARK = 0xD002, 0x2F
EV_ARRIVED = 0x34C
W_LASTDEXMODE, DEXMODE_OLD = 0xD94C, 1


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    def w(v): return bytes([v & 0xFF, v >> 8])
    def at(a): return fo(B, a)
    assert rom[at(INIT_CALL):at(INIT_CALL) + 4] == bytes.fromhex('af cd 46 5f')
    assert rom[at(LRI):at(LRI) + 11] == bytes.fromhex('7e e6 20 20 06 7e e6 10 20 12 c9')
    assert rom[at(LEFT):at(RIGHT_END)] == bytes.fromhex(
        'f0 d2 fe 90 c8 cd d7 2f 3e 90 e0 d2 af cd 46 5f c9 fa 3f d8 cb 77 c8 f0 d2 a7 c8 cd d7 2f af e0 d2 3e 01 cd 46 5f c9')
    fb = 0xDA65 + EV_ARRIVED // 8; mask = 1 << (EV_ARRIVED % 8)
    left = (b'\xfa' + w(fb) + bytes([0xE6, mask, 0xC8])           # Johto only after arriving there
            + bytes.fromhex('f0 d2 fe 90 c8') + b'\xcd' + w(CLEARSPRITES) + bytes.fromhex('3e 90 e0 d2 af c3') + w(GETNEST))
    right_at = LEFT + len(left)
    right = bytes.fromhex('f0 d2 a7 c8') + b'\xcd' + w(CLEARSPRITES) + bytes.fromhex('af e0 d2 3e 01 c3') + w(GETNEST)
    kanto = right_at + 4
    blk = left + right; assert LEFT + len(blk) <= RIGHT_END
    rom[at(LEFT):at(RIGHT_END)] = blk + bytes(RIGHT_END - LEFT - len(blk))
    rom[at(LRI) + 9] = right_at - (LRI + 10)
    # the kit's nesttime (bank 96: ld hl, NT_RIGHT = $5ED1 / ... / ld hl, NT_LEFT = $5EC0 / ld a, $24 / rst FarCall)
    nt = [m for m in range(fo(0x96, 0x5800), fo(0x96, 0x5900)) if rom[m:m + 3] == bytes.fromhex('21 d1 5e')]
    assert len(nt) == 1 and rom[nt[0] + 3:nt[0] + 6] == bytes.fromhex('28 03 21'), nt
    rom[nt[0] + 1:nt[0] + 3] = w(right_at)
    f, n = bank_free_tail(rom, B); f += 1; assert n >= 14
    ia = 0x4000 + f % 0x4000
    init = (b'\xfa' + w(W_PLAYERICONLANDMARK) + bytes([0xFE, KANTO_LANDMARK, 0xD2]) + w(kanto)
            + b'\xaf\xc3' + w(GETNEST))
    rom[f:f + len(init)] = init
    rom[at(INIT_CALL):at(INIT_CALL) + 4] = b'\xcd' + w(ia) + b'\x00'
    # new game: the number order
    o = fo(0x01, 0x5B7E)
    assert rom[o:o + 9] == bytes.fromhex('af ea 63 d4 c9 cf 38 07 3e')
    rom[o:o + 9] = bytes.fromhex('af ea 63 d4 3c ea') + w(W_LASTDEXMODE) + b'\xc9'
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('dex area: init 24:%04X, .right 24:%04X; new game dex order: number' % (ia, right_at))


if __name__ == '__main__':
    main()
