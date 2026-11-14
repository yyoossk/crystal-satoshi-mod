#!/usr/bin/env python3
"""Phase 76: Strength boulders cross Red's elevation edges as in Red.
 Red's tile-pair elevation edges are Crystal side walls here (pairwalls.py).  Red checks the elevation only between
 the player's tile and the boulder's tile (CheckForCollisionWhenPushingBoulder -> CheckForTilePairCollisions2), so the
 boulder itself may be pushed over an edge (Victory Road 3F: the boulder in the gap at (13,12) is pushed down twice to
 reach the hole area).  Crystal's object movement stopped it at the side wall, so that area could not be reached.
 * WillObjectBumpIntoWater (01:789D, used for walking objects): for a Strength boulder (OBJECT_PALETTE bit 6) only the
   tile permission is checked, not the side walls.  The player's own step still checks its walls first (as Red does).
usage: build_phase76.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

SITE = 0x789D            # 01:789D WillObjectBumpIntoWater: call CanObjectLeaveTile
HOOK = 0x7EC0            # bank 1 free space (after the kit's code, before its next block)
CODE = bytes([0x21, 0x06, 0x00, 0x09,       # ld hl, OBJECT_PALETTE / add hl, bc
              0xCB, 0x76,                   # bit STRENGTH_BOULDER_F, [hl]
              0x20, 0x03,                   # jr nz, .boulder
              0xC3, 0xF5, 0x78,             # jp CanObjectLeaveTile (returns to the caller as before)
              0xE1,                         # .boulder: pop hl (skip the rest of WillObjectBumpIntoWater)
              0x21, 0x0E, 0x00, 0x09, 0x7E, # ld a, [bc + OBJECT_TILE_COLLISION]
              0xCD, 0x28, 0x18,             # call GetTilePermission
              0xA7, 0xC8,                   # and a / ret z  (land: it may move)
              0x37, 0xC9])                  # scf / ret


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    assert rom[SITE:SITE + 3] == bytes([0xCD, 0xF5, 0x78])
    assert rom[0x1828:0x182B] == bytes([0xD5, 0xE5, 0x21])
    assert rom[HOOK:HOOK + len(CODE)] == bytes(len(CODE))
    rom[HOOK:HOOK + len(CODE)] = CODE
    rom[SITE:SITE + 3] = bytes([0xCD, HOOK & 0xFF, HOOK >> 8])
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('Strength boulders ignore side walls (01:%04X)' % HOOK)


if __name__ == '__main__':
    main()
