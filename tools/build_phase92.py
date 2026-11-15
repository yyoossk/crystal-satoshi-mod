#!/usr/bin/env python3
"""Phase 92: the map name sign of Kanto towns and routes had other colours than Crystal's.
The sign uses BG palette 7 (PAL_BG_TEXT).  Crystal loads it from the tileset palettes (the cream sign with a brown
frame, by time of day).  The Kanto maps' palettes come from the ported (Pikachu full-color) palette sets through
LoadSpecialMapPalette (phases 11-15 hooks), whose palette 7 is the blue text palette.  The Kanto maps' hook (6A:6EE9, farcalled from
12:7FF0) is wrapped: after a special palette set was loaded for a town or route (where the sign shows), palette 7 is Crystal's own text palette
for the time of day.
usage: build_phase92.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import LSMP

TILESET_BG_PAL = (0x02, 0x72D6)    # TilesetBGPalette (JP)
TEXT_IDX = (0x07, 0x0F, 0x17, 0x1F)  # EnvironmentColors' palette 7 by time of day (same for every environment)
W_TIMEOFDAYPAL = 0xD834
W_BGPALS7 = 0xD038                 # wBGPals1 palette 7 (WRAM bank 5)


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    # the outermost hook (12:7FF0): ld a,$6A / ld hl,$6EE9 / rst FarCall / ret c / ...  -> farcall our wrapper in 6A
    hk = fo(0x12, 0x7FF0)
    assert rom[hk:hk + 7] == bytes.fromhex('3e 6a 21 e9 6e cf d8'), rom[hk:hk + 7].hex()
    prev = 0x6EE9
    t = fo(*TILESET_BG_PAL)
    pals = b''.join(bytes(orig[t + 8 * i:t + 8 * i + 8]) for i in TEXT_IDX)
    assert pals[:8] == bytes.fromhex('ff43ff432e010000'), pals[:8].hex()
    f, n = bank_free_tail(rom, 0x6A); f += 4
    a = 0x4000 + f % 0x4000
    tab = a + 0x40
    code = bytes([0xCD, prev & 0xFF, prev >> 8,            # call previous hook chain
                  0xD0,                                     # ret nc
                  0xFA, 0xCB, 0xD1, 0x3D, 0xFE, 0x02,       # ld a,[wEnvironment] / dec a / cp 2 (TOWN/ROUTE only:
                  0x3F, 0xD8,                               # ccf / ret c (carry kept)   where the sign shows)
                  0xFA, W_TIMEOFDAYPAL & 0xFF, W_TIMEOFDAYPAL >> 8, 0xE6, 0x03,   # ld a,[wTimeOfDayPal] / and 3
                  0x87, 0x87, 0x87, 0x5F, 0x16, 0x00,       # ×8 -> de
                  0x21, tab & 0xFF, tab >> 8, 0x19,         # ld hl,tab / add hl,de
                  0xF0, 0x70, 0xF5, 0x3E, 0x05, 0xE0, 0x70, # wram bank 5
                  0x11, W_BGPALS7 & 0xFF, W_BGPALS7 >> 8, 0x0E, 0x08,
                  0x2A, 0x12, 0x13, 0x0D, 0x20, 0xFA,       # copy 8 bytes
                  0xF1, 0xE0, 0x70, 0x37, 0xC9])            # restore / scf / ret
    assert len(code) <= 0x40 and n >= 0x40 + len(pals) + 8
    rom[f:f + len(code)] = code
    rom[f + 0x40:f + 0x40 + len(pals)] = pals
    rom[hk + 3] = a & 0xFF; rom[hk + 4] = a >> 8
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('LoadSpecialMapPalette hook 6A:%04X (prev %04X): palette 7 = Crystal text palette' % (a, prev))


if __name__ == '__main__':
    main()
