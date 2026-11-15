#!/usr/bin/env python3
"""Phase 94: the Pokémon picture of `pokepic` (Oak's lab: the three starters' balls, as in the Pikachu full-color hack)
in colour instead of Crystal's gray.
_CGB_Pokepic (02:5456) fills the picture box with PAL_BG_GRAY.  Now the box uses PAL_BG_TEXT (7) and that palette is
the Pokémon's (white / colour 1 / colour 2 / black, GetMonPalettePointer of wCurPartySpecies) in wBGPals1 and
wBGPals2; ClosePokepic reloads the map's palettes as before.
usage: build_phase94.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

CGB_POKEPIC = 0x9456               # 02:5456
FILL = bytes.fromhex('3e 00 cd 20 56 cd 70 56 c9')    # ld a,PAL_BG_GRAY / call FillBoxCGB / call ApplyAttrmap / ret
GET_MON_PAL, LOAD_PAL, FILLBOX = 0x5732, 0x5600, 0x5620
W_CURPARTYSPECIES = 0xD0C8
BGPALS1_7, BGPALS2_7 = 0xD038, 0xD0B8


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    o = rom.index(FILL, CGB_POKEPIC, CGB_POKEPIC + 0x60)
    assert rom[fo(2, GET_MON_PAL):fo(2, GET_MON_PAL) + 4] == bytes.fromhex('cd ab 57 c9')
    assert rom[fo(2, LOAD_PAL):fo(2, LOAD_PAL) + 4] == bytes.fromhex('f0 70 f5 3e')
    f, n = bank_free_tail(rom, 2); f += 8
    a = 0x4000 + f % 0x4000
    def w(v): return bytes([v & 0xFF, v >> 8])
    code = (b'\xe5\xc5'                                            # push hl / push bc (the box)
            + b'\xfa' + w(W_CURPARTYSPECIES) + b'\xcd' + w(GET_MON_PAL)
            + b'\xe5\x11' + w(BGPALS1_7) + b'\xcd' + w(LOAD_PAL)   # push hl / ld de,pal7 / call LoadPalette...
            + b'\xe1\x11' + w(BGPALS2_7) + b'\xcd' + w(LOAD_PAL)   # pop hl / ld de,pal7 (2) / call LoadPalette...
            + b'\x3e\x01\xe0\xe5'                                  # ld a,1 / ldh [hCGBPalUpdate],a
            + b'\xc1\xe1\x3e\x07\xc3' + w(FILLBOX))                # pop bc / pop hl / ld a,PAL_BG_TEXT / jp FillBoxCGB
    assert len(code) + 8 < n
    rom[f:f + len(code)] = code
    rom[o:o + 5] = b'\xcd' + w(a) + b'\x00\x00'
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('_CGB_Pokepic: the Pokémon\'s palette in PAL_BG_TEXT (02:%04X)' % a)


if __name__ == '__main__':
    main()
