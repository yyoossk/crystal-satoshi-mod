#!/usr/bin/env python3
"""Phase 124: back from the main menu (B) the title screen is Red's (phase 53), not Crystal's.
 Phase 53 put Red's opening in IntroSequence (01:6385); _MainMenu still ended in "jp StartTitleScreen" (01:6393),
 Crystal's own title screen (whose first bytes phase 53's patch had even overwritten).  Now:
 * _MainMenu jumps to 01:6395 (Crystal's title loop, unused since phase 53): set a flag ($C6A9, a free byte outside battles) and go
   to IntroSequence (Red's opening);
 * Red's opening skips the intro (copyright, shooting star, Gengar / Nidorino) when the flag is set and clears it,
   so the title screen comes at once, as in Red.
usage: build_phase124.py IN.gbc OUT.gbc OUT.ips
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

FLAG = 0xC6A9
OPEN_BANK = 0x36


def expect(rom, o, hexs):
    b = bytes.fromhex(hexs.replace(' ', ''))
    assert rom[o:o + len(b)] == b, (hex(o), rom[o:o + len(b)].hex(' '), hexs)
    return b


def w16(v): return bytes([v & 0xFF, v >> 8])
def ga(o): return o % 0x4000 + (0x4000 if o >= 0x4000 else 0)


def main():
    src, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src, 'rb').read())
    # IntroSequence (phase 53): push WRAM bank ; WRAM 5 ; farcall RedOpening ; jp 63A5
    st = expect(rom, 0x6385, 'f0 70 f5 3e 05 e0 70 3e 36 21')
    ro = rom[0x6385 + 10] | rom[0x6385 + 11] << 8
    expect(rom, 0x6385 + 12, 'cf c3 a5 63')
    # _MainMenu: ... farcall MainMenu ; jp StartTitleScreen (01:6393)
    expect(rom, 0x5B01, 'c3 93 63')
    # Crystal's title loop after phase 53's 16-byte stub (01:6395..639C, unused): set the flag ; jp IntroSequence
    expect(rom, 0x6395, 'f5 3e 05 e0 70 cd ec 63')
    rom[0x6395:0x6395 + 8] = bytes([0x3E, 0x01, 0xEA]) + w16(FLAG) + bytes([0xC3, 0x85, 0x63])
    rom[0x5B02:0x5B04] = w16(0x6395)
    # RedOpening: ... call PlayIntro ; call TitleScreen ; ld [wTitleScreenSelectedOption], a
    o = fo(OPEN_BANK, ro)
    seq = bytes.fromhex('cd d7 2f cd c2 5c cd d8 5c cd e6 60 ea 58 cf'.replace(' ', ''))
    i = rom.find(seq, o, o + 0x80); assert i > 0
    play_intro = rom[i + 7] | rom[i + 8] << 8
    a = bank_free_tail(rom, OPEN_BANK)[0] + 2
    code = bytes([0xFA]) + w16(FLAG) + bytes([0xA7, 0xCA]) + w16(play_intro) + \
        bytes([0xAF, 0xEA]) + w16(FLAG) + bytes([0xC9])
    assert not any(rom[a:a + len(code)]) and a + len(code) <= (OPEN_BANK + 1) * 0x4000
    rom[a:a + len(code)] = code
    rom[i + 7:i + 9] = w16(ga(a))
    print('main menu B -> Red\'s title (01:6395), PlayIntro wrapper %02X:%04X' % (OPEN_BANK, ga(a)))
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)


if __name__ == '__main__':
    main()
