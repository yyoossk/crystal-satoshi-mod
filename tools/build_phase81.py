#!/usr/bin/env python3
"""Phase 81: the fast ship's first voyage (to New Bark Town): the arrival line after the captain's granddaughter.
 Phase 47 changed the ship's announcements for the first voyage to New Bark Town, but the line said in the captain's
 cabin when the granddaughter is back (SSAquaMetalCoatAndDocking: "...クチバこうに とうちゃくしました！") was left:
 on the first voyage it now says New Bark Town (later voyages: Crystal's line).
usage: build_phase81.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import Space
from jpchar import encode

SITE = 0x5174                      # bank 1A: writetext SSAquaHasArrivedVermilionText (captain's cabin)
OLD_TEXT = 0x5635
EV_ARRIVED = 0x34C                 # phase 47: the player has reached Johto
PB = 0x5B


def T(s): return encode('{00}' + s) + b'\x57'


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    o = fo(0x1A, SITE); assert rom[o:o + 3] == bytes([0x4C, OLD_TEXT & 0xFF, OLD_TEXT >> 8]), rom[o:o + 3].hex()
    for b in (PB, 0x1A):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1, b * 0x4000 + 0x4000)
    a = Asm(sp.here(PB)); a.bank = PB
    a.label('h'); a.checkevent(EV_ARRIVED); a.iftrue('o'); a.writetext('t'); a.end()
    a.label('o'); a.farwritetext(0x1A, OLD_TEXT); a.end()
    a.label('t'); a.raw(T('こうそくせん　アクアごうは<LINE>ワカバタウンに　とうちゃくしました！'))
    base = a.base; blob = a.done(); assert sp.put(PB, blob) == base
    stub = sp.put(0x1A, bytes([0x04, PB, a.labels['h'] & 0xFF, a.labels['h'] >> 8]))          # farsjump
    rom[o:o + 3] = bytes([0x00, stub & 0xFF, stub >> 8])                                      # scall stub
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('captain\'s cabin arrival line: %X:%04X (stub 1A:%04X)' % (PB, base, stub))


if __name__ == '__main__':
    main()
