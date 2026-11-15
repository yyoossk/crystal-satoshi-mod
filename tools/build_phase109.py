#!/usr/bin/env python3
"""Phase 109: the Pokégear's town map in Kanto: pressing down past Pallet Town ran into Johto's places (and on through
every landmark) while Kanto's map was shown.
TownMap_GetKantoLandmarkLimits (24:5083) gives the cursor's range: after Johto's Hall of Fame all of Kanto
(KANTO_LANDMARK $2F .. $5E), before it Crystal's (Victory Road $58 .. Route 28 $5E: before its Hall of Fame Crystal's
player only reaches that corner of Kanto).  In this MOD the journey starts in Kanto, so the cursor stood below
the range's bottom and was never wrapped.  The range is now all of Kanto at any time.
usage: build_phase109.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    o = fo(0x24, 0x5083)
    assert rom[o:o + 17] == bytes.fromhex('fa 3f d8 cb 77 28 05 16 5e 1e 2f c9 16 5e 1e 58 c9'), rom[o:o + 17].hex()
    rom[o + 15] = 0x2F
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('Kanto town map cursor: $2F-$5E before the Hall of Fame too')


if __name__ == '__main__':
    main()
