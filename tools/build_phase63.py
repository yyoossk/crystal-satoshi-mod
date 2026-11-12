#!/usr/bin/env python3
"""Phase 63: Celebi comes back after the next Hall of Fame (Johto's) when it was not caught (beaten or fled from):
Lance's script, where it sets EVENT_BEAT_ELITE_FOUR ($1D:$7285), clears Celebi's "met" bit (the kit's wLegendFlags
$D836 bit 0) unless the Pokédex has Celebi caught.
usage: build_phase63.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *

PB = 0x47
SITE = 0x77285                     # $1D:$7285  setevent EVENT_BEAT_ELITE_FOUR / setevent $077C
W_LEGEND, W_DEX_CAUGHT, CELEBI = 0xD836, 0xDE2D, 251


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    f, n = bank_free_tail(rom, PB); sp.set_area(PB, f + 16, PB * 0x4000 + 0x4000)
    old = bytes(rom[SITE:SITE + 6]); assert old == bytes([0x33, 0x44, 0x00, 0x33, 0x7C, 0x07])
    a = Asm(sp.here(PB)); a.bank = PB
    a.label('s'); a.raw(old); a.callasm(PB, 'asm'); a.end()
    i = CELEBI - 1
    a.label('asm'); a.db(0xFA); a.dw(W_DEX_CAUGHT + i // 8); a.db(0xCB, 0x47 | ((i % 8) << 3), 0xC0)   # bit n,a / ret nz
    a.db(0x21); a.dw(W_LEGEND); a.db(0xCB, 0x86, 0xC9)                                                 # res 0,[hl]
    base = a.base; blob = a.done(); assert sp.put(PB, blob) == base
    l_ = a.labels['s']; rom[SITE:SITE + 6] = bytes([0x01, PB, l_ & 0xFF, l_ >> 8, 0x13, 0x13])        # farscall / checkscene x2
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    print('Celebi reset at the Hall of Fame: %02X:%04X' % (PB, base))


if __name__ == '__main__':
    main()
