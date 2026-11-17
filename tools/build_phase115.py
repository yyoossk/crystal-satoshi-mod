#!/usr/bin/env python3
"""Phase 115: no second copy of an HM in Johto (2026-11-18 request 「元々カントーで持っているひでんましんはジョウトでは入手しないようにして」).
 The MOD's player gets HM01-05 in Kanto first; Crystal's Johto givers (the charcoal master in Ilex Forest: Cut,
 Chuck's wife: Fly, the Dance Theater gentleman: Surf, the Olivine Cafe sailor: Strength, Elder Li: Flash) gave a
 second copy.  Each giver's `promptbutton / verbosegiveitem HM_xx, 1` becomes `farscall` to a small routine in bank $21's free
 space (the givers' own banks are full):
     promptbutton / checkitem HM_xx / iftrue .have / verbosegiveitem HM_xx, 1 / end
     .have: writetext 「あれ？　その　ひでんマシンなら　もう　もっているようだね！」 / promptbutton / end
 (checkitem leaves TRUE for a following iffalse, so Chuck's wife's `iffalse .Done` still goes on; every event the
 giver sets is still set, so the story goes on as in Crystal).  HM06 Whirlpool and HM07 Waterfall are Johto's own.
usage: build_phase115.py IN.gbc OUT.gbc OUT.ips
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from jpchar import encode

GIVERS = [(0x65FB5, 0xF3, 'Ilex Forest: charcoal master (Cut)'),
          (0x980A0, 0xF4, "Cianwood: Chuck's wife (Fly)"),
          (0x60D82, 0xF5, 'Dance Theater: gentleman (Surf)'),
          (0x7510C, 0xF6, 'Olivine Cafe: sailor (Strength)'),
          (0x5C4A9, 0xF7, 'Sprout Tower 3F: Elder Li (Flash)')]
TEXT = encode('あれ？　その　ひでんマシンなら<LINE>もう　もっているようだね！<DONE>')


def main():
    src, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src, 'rb').read())
    B = 0x21
    o = bank_free_tail(rom, B)[0] + 16                                    # (a margin after the bank's last data)
    for at, hm, what in GIVERS:
        assert rom[at - 1:at + 3] == bytes([0x54, 0x9D, hm, 0x01]), (what, rom[at - 1:at + 3].hex())
        base = 0x4000 + (o - B * 0x4000)
        a = Asm(base)
        a.promptbutton(); a.checkitem(hm); a.iftrue('have'); a.verbosegiveitem(hm, 1); a.end()
        a.label('have'); a.writetext('txt'); a.promptbutton(); a.end()
        a.label('txt'); a.db(0x00); a.raw(TEXT)
        blob = a.done()
        assert o + len(blob) <= (B + 1) * 0x4000 and not any(rom[o:o + len(blob)]), what
        rom[o:o + len(blob)] = blob
        rom[at - 1:at + 3] = bytes([0x01, B, base & 0xFF, base >> 8])      # farscall
        print('%s: %02x:%04x' % (what, B, base))
        o += len(blob)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)


if __name__ == '__main__':
    main()
