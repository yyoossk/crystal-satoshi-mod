#!/usr/bin/env python3
"""Phase 125 (report 2026-11-21 「オーキドに荷物をわたしたらバグる」): a crash (reset to the title) while Red's music plays.
 Phase 68/98 made Crystal's _UpdateSound (called by the VBlank interrupt) "farcall" Red's sound engine (3A:7FCF:
 farcall 9E:4100, which farcalls again 9D / 9F).  FarCall (rst $08, home 2D35) keeps the target bank in hFF8B and
 the caller's bc in wCFAD/wCFAE: when VBlank came while the main program was inside a FarCall (between "ldh [$8B], a"
 and "ldh a, [$8B]", or in its return), the main program jumped into the wrong bank (e.g. 9F:5714, graphics) and crashed.
 It depends on timing (seen in Oak's lab when Shigeru comes in with Red's rival music).  Now:
 * 3A:7FCF: "ld a, $9E ; rst Bankswitch" (no FarCall); the next bytes are run in bank 9E (9E:7FD2): save hFF8B, wCFAD,
   wCFAE ; call 9E:4100 ; restore them ; ret (to VBlank, which switches its bank back itself).
usage: build_phase125.py IN.gbc OUT.gbc OUT.ips
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

GLUE = 0x9E


def expect(rom, o, hexs):
    b = bytes.fromhex(hexs.replace(' ', ''))
    assert rom[o:o + len(b)] == b, (hex(o), rom[o:o + len(b)].hex(' '), hexs)
    return b


def main():
    src, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src, 'rb').read())
    # _UpdateSound -> 3A:7FC8
    expect(rom, fo(0x3A, 0x405C), 'c3 c8 7f')
    o = fo(0x3A, 0x7FC8)
    expect(rom, o, 'fa 00 c1 fe a5 38 07 3e 9e 21 00 41 cf c9 a7 c8')
    # the VBlank handlers: ... ld a, $3A ; rst Bankswitch ; call _UpdateSound ; ldh a, [hFF8A] ; rst Bankswitch
    assert rom.count(bytes.fromhex('3e3ad7cd5c40f08ad7')) >= 1
    w = fo(GLUE, 0x7FD2)
    code = bytes([0xF0, 0x8B, 0xF5,                     # ldh a, [$8B] ; push af
                  0xFA, 0xAD, 0xCF, 0xF5,               # ld a, [$CFAD] ; push af
                  0xFA, 0xAE, 0xCF, 0xF5,               # ld a, [$CFAE] ; push af
                  0xCD, 0x00, 0x41,                     # call $4100
                  0xF1, 0xEA, 0xAE, 0xCF,               # pop af ; ld [$CFAE], a
                  0xF1, 0xEA, 0xAD, 0xCF,               # pop af ; ld [$CFAD], a
                  0xF1, 0xE0, 0x8B,                     # pop af ; ldh [$8B], a
                  0xC9])                                # ret
    assert not any(rom[w:w + len(code)]) and w + len(code) <= (GLUE + 1) * 0x4000
    rom[w:w + len(code)] = code
    rom[o + 7:o + 14] = bytes([0x3E, GLUE, 0xD7, 0, 0, 0, 0])   # ld a, $9E ; rst Bankswitch ; (runs on in 9E:7FD2)
    print('VBlank sound: 3A:7FCF -> bank %02X:7FD2 (hFF8B / wCFAD / wCFAE kept)' % GLUE)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)


if __name__ == '__main__':
    main()
