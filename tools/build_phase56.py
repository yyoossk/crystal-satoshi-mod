#!/usr/bin/env python3
"""Phase 56: Jessie and James (ムサシとコジロウ) look as in the Pikachu full-color hack on the map: their own walking
sprites (the Pikachu version's, from the full-color hack) with its colors -- Jessie's red hair (red palette), James's
blue hair (blue palette) -- instead of Crystal's Rocket grunt sprites.  Two more entries in phase 14's second sprite
table: ids 0x75 (Jessie) and 0x76 (James), used by the J&J objects of phases 11/12/14/15 (Pokémon Tower, Rocket
Hideout, Silph Co., Mt. Moon) and 48 (Slowpoke Well, Mahogany hideout, Radio Tower).
usage: build_phase56.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
import build_phase10 as P10
import build_phase14 as P14

PKFC_JESSIE, PKFC_JAMES = 0xFEF91, 0xFF111        # PKFC JessieSprite / JamesSprite (24 tiles each, walking)
SPRITE_JESSIE, SPRITE_JAMES = 0x75, 0x76
assert SPRITE_JESSIE == 0x67 + len(P14.NEW_SPRITES) + 3
PAL_OW_RED, PAL_OW_BLUE = 0, 1
BANK2 = 0x70


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (0x05, BANK2, 0x7D, 0x77, 0x76, 0x79):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1 if f > b * 0x4000 else f, b * 0x4000 + 0x4000)
    log = []
    stubs = []
    for off, d in P14.OW_READERS:
        assert rom[off] == 0xCD; s_ = fo(0x05, r16(off + 1))
        assert rom[s_:s_ + 2] == bytes([0xFE, 0x67]) and rom[s_ + 8] == 0x21
        stubs.append((s_, d))
    virt = r16(stubs[0][0] + 9) - stubs[0][1]
    n2 = len(P14.NEW_SPRITES) + 3                                   # + Old Amber (26), Safari worker (28), old man (29)
    t2 = virt + 0x66 * 6
    tab = bytes(rom[fo(0x05, t2):fo(0x05, t2) + 6 * n2])
    pk = open(P10.PKFC, 'rb').read()
    for off, pal in ((PKFC_JESSIE, PAL_OW_RED), (PKFC_JAMES, PAL_OW_BLUE)):
        gb = next(b for b in (BANK2, 0x7D, 0x77, 0x76, 0x79) if sp.cur[b][1] - sp.cur[b][0] > 24 * 16 + 16)
        ga = sp.put(gb, pk[off:off + 24 * 16])
        tab += bytes([ga & 0xFF, ga >> 8, 0xC0, gb, 1, pal])
    nt = sp.put(0x05, tab); nv = nt - 0x66 * 6
    for s_, d in stubs: w16(s_ + 9, nv + d)
    log.append('Jessie / James sprites -> ids %02X / %02X' % (SPRITE_JESSIE, SPRITE_JAMES))
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    print('\n'.join(log))


if __name__ == '__main__':
    main()
