#!/usr/bin/env python3
"""Phase 78: wild Pokémon do not run away in Kanto, as in Red.
 Crystal's TryEnemyFlee makes some wild Pokémon run away (Articuno / Zapdos / Moltres / Cubone often, Magnemite /
 Grimer / Tangela / Dratini ... sometimes).  Red has no such thing (the Safari Zone has its own battle loop and rules),
 so Zapdos in the Power Plant could fly off.  In Kanto (IsInJohto) TryEnemyFlee now always stays; Johto is unchanged.
 * 0F:4542 TryEnemyFlee: its first two checks (wild battle / can't-run) move to a far function that also checks the
   region: ld a, BANK / ld hl, Far / rst FarCall / jr nz, .Stay  (FarCall keeps the flags).
usage: build_phase78.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

SITE = 0x0F * 0x4000 + 0x0542          # 0F:4542 TryEnemyFlee
OLD = bytes([0xFA, 0x5E, 0xD2, 0x3D, 0x20, 0x4D, 0xFA, 0x60, 0xC6, 0xCB, 0x7F, 0x20, 0x46])
BANK, ADDR = 0x63, 0x7600
FAR = bytes([0xFA, 0x5E, 0xD2, 0x3D, 0xC0,         # ld a, [wBattleMode] / dec a / ret nz   (not wild: stay)
             0xFA, 0x60, 0xC6, 0xCB, 0x7F, 0xC0,   # ld a, [wPlayerSubStatus5] / bit SUBSTATUS_CANT_RUN, a / ret nz
             0xCD, 0xE9, 0x2E,                     # call IsInJohto  (0 = Johto, 1 = Kanto)
             0xA7, 0xC9])                          # and a / ret     (nz in Kanto: stay)
NEW = bytes([0x3E, BANK, 0x21, ADDR & 0xFF, ADDR >> 8, 0xCF, 0x20, 0x4B]) + bytes(5)   # jr nz, .Stay (0F:4595)


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    assert rom[SITE:SITE + len(OLD)] == OLD
    assert rom[0x2EE9:0x2EED] == bytes([0xFA, 0x7B, 0xDC, 0x47])          # IsInJohto
    far = BANK * 0x4000 + ADDR - 0x4000
    f, _ = bank_free_tail(rom, BANK); assert far >= f + 16, hex(f)
    assert rom[far:far + len(FAR)] == bytes(len(FAR))
    rom[far:far + len(FAR)] = FAR
    rom[SITE:SITE + len(NEW)] = NEW
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('TryEnemyFlee: no running away in Kanto (%02X:%04X)' % (BANK, ADDR))


if __name__ == '__main__':
    main()
