#!/usr/bin/env python3
"""Phase 84: Prof. Oak opens Mt. Silver.
 After the Kanto Hall of Fame Oak's lab ran only the base mod's ticket script ("take the ship to New Bark Town"), also
 after the Johto League: Crystal's Oak, who lets a trainer with all sixteen badges into Mt. Silver
 (EVENT_OPENED_MT_SILVER; the black belt in the Victory Road gate steps aside), was never reached, so Mt. Silver and
 Hibiki's battle could not be reached.
 * With the Rising Badge (all eight Johto badges) Oak's lab runs Crystal's Oak: Mt. Silver opened, then his Pokédex
   rating.  His line "you collected the Kanto badges too!" -> "the Johto badges too!" (Satoshi came from Kanto).
usage: build_phase84.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import Space
from jpchar import encode
from evedit import copy_text

OAK_POST = (0x6F, 0x56D0)            # phase 29: Oak after the Kanto Hall of Fame -> farsjump 78:5D38 (the ticket)
TICKET = (0x78, 0x5D38)
CRYSTAL_OAK_OPEN, CRYSTAL_OAK_DEX = (0x1F, 0x7B77), (0x1F, 0x7B6A)
OPEN_TEXT = (0x1F, 0x7C0F)
EV_OPENED_MT_SILVER, ENGINE_RISINGBADGE = 0x74F, 0x22
BANK = 0x63


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    f, n = bank_free_tail(rom, BANK); sp.set_area(BANK, f + 1, BANK * 0x4000 + 0x4000)
    o = fo(*OAK_POST); assert rom[o:o + 4] == bytes([0x04, TICKET[0], TICKET[1] & 0xFF, TICKET[1] >> 8])
    for b, a, pre in [(0x1F, 0x7B77, bytes([0x4C, 0x0F, 0x7C, 0x54, 0x33, 0x4F, 0x07])),
                      (0x1F, 0x7B6A, bytes([0x4C, 0xDA, 0x7B, 0x53, 0x0F, 0x65, 0x00]))]:
        assert rom[fo(b, a):fo(b, a) + len(pre)] == pre, hex(a)
    here = sp.here(BANK)
    def fj(t): return bytes([0x04, t[0], t[1] & 0xFF, t[1] >> 8])
    l_tk = here + 6 + 12 + 4
    blk = bytes([0x34, ENGINE_RISINGBADGE, 0, 0x08, l_tk & 0xFF, l_tk >> 8])           # checkflag ; iffalse ticket
    l_dex = here + len(blk) + 12
    blk += bytes([0x6A, 0x47, 0x31, EV_OPENED_MT_SILVER & 0xFF, EV_OPENED_MT_SILVER >> 8,  # faceplayer ; opentext ; checkevent
                  0x09, l_dex & 0xFF, l_dex >> 8]) + fj(CRYSTAL_OAK_OPEN)               # iftrue dex ; farsjump open
    assert here + len(blk) == l_dex
    blk += fj(CRYSTAL_OAK_DEX)
    assert here + len(blk) == l_tk
    blk += fj(TICKET)
    assert sp.put(BANK, blk) == here
    rom[o:o + 4] = fj((BANK, here))
    # "カントー　バッジも　あつめたのか！" -> Johto
    t = fo(*OPEN_TEXT); old = copy_text(rom, t)
    x, y = encode('カントー　バッジも').rstrip(b'\x50'), encode('ジョウト　バッジも').rstrip(b'\x50'); assert len(x) == len(y)
    i = old.index(x); rom[t + i:t + i + len(y)] = y
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('Oak (after the Hall of Fame) %02X:%04X: Rising Badge -> Crystal Oak (Mt. Silver)' % (BANK, here))


if __name__ == '__main__':
    main()
