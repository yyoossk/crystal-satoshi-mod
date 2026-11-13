#!/usr/bin/env python3
"""Phase 74: the stale win/loss-text bank (phase 54's WINLOSS_BANK $DA5C).
 A script battle ("winlosstext") stores its script bank in $DA5C; PrintWinLossText uses it and clears it.  But when the
 text is never printed (the player lost the battle: Route 22's rival), $DA5C stayed, and the next map trainer's text
 (Viridian Forest's bug catcher) was read from that bank -> garbage -> the game reset.
 * reloadmapafterbattle (run after every script and map-trainer battle, won or lost) clears $DA5C first.
usage: build_phase74.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

ENTRY = 0x96D6F          # bank $25 script command table: reloadmapafterbattle -> $7457
HOOK = 0x97FF9           # bank $25 free tail (7 bytes)


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    assert rom[ENTRY:ENTRY + 2] == bytes([0x57, 0x74])
    assert rom[0x97457:0x9745D] == bytes([0x21, 0x4A, 0xD4, 0x56, 0x36, 0x00])
    assert rom[HOOK:HOOK + 7] == bytes(7)
    rom[HOOK:HOOK + 7] = bytes([0xAF, 0xEA, 0x5C, 0xDA, 0xC3, 0x57, 0x74])   # xor a / ld [$DA5C],a / jp $7457
    rom[ENTRY:ENTRY + 2] = (0x7FF9).to_bytes(2, 'little')
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('reloadmapafterbattle clears $DA5C (25:7FF9)')


if __name__ == '__main__':
    main()
