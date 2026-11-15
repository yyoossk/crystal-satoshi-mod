#!/usr/bin/env python3
"""Phase 96: going in and out of buildings faster (closer to Red).
Crystal's door / warp / fly fades (FadeOutToWhite, FadeInFromWhite, FadeInFromBlack, FadeOutToBlack) step through
4 palettes with 2 frames each (ConvertTimePalsIncHL / ConvertTimePalsDecHL, 23:415E / 23:416D).  Now 1 frame each,
so every door takes 8 frames less (the fade out and the fade in are half as long).
usage: build_phase96.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

SITES = ((0x23, 0x415E, 0x23), (0x23, 0x416D, 0x2B))   # ConvertTimePalsIncHL (inc hl) / DecHL (dec hl)


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    for b, a, op in SITES:
        o = fo(b, a)
        assert rom[o:o + 15] == bytes([0xCD, 0x4E, 0x41, op, op, op, 0x0E, 0x02, 0xCD, 0x68, 0x04, 0x05, 0x20, 0xF2, 0xC9]), rom[o:o + 15].hex()
        rom[o + 7] = 1
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('door fades: 1 frame per step')


if __name__ == '__main__':
    main()
