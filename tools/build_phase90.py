#!/usr/bin/env python3
"""Phase 90: the follower right after the first rival battle in Oak's lab showed a broken Pikachu.
The sprites were reloaded after the battle before the follower existed (no lead yet -> the kit's fallback picture,
Pikachu, and the battle's tiles left in VRAM).  When the follower then appeared (kit Fw_SpawnHere), its sprite entry
($E2) was already in wUsedSprites, so nothing was loaded, and Fw_CheckReload saw wFwLoaded already equal to the lead
(Fw_GetSprite had set it) -> the wrong tiles stayed.
Fix: Fw_SpawnHere (the follower appearing where the player stands, not on a map load) always reloads every sprite
(Fw_RefreshAll, as it did when the entry was missing), so the follower's tiles (VRAM bank and number) are right.
usage: build_phase90.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

FB = 0x99
SPAWN_LOOP = 0x48E6                # ld hl,wUsedSprites / ld c,32 / .find ... / call Fw_RefreshAll  (17 bytes)
REFRESH_ALL = 0x4914


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    o = fo(FB, SPAWN_LOOP)
    old = bytes.fromhex('21 85 d1 0e 20 2a fe e2 28 07 23 0d 20 f7 cd 14 49')
    assert rom[o:o + 17] == old, rom[o:o + 17].hex()
    f, n = bank_free_tail(rom, FB); f += 16
    a = 0x4000 + (f - FB * 0x4000)
    code = bytes.fromhex('c3 14 49')                 # jp Fw_RefreshAll (always)
    assert len(code) < n - 32
    rom[f:f + len(code)] = code
    rom[o:o + 17] = bytes([0xCD, a & 0xFF, a >> 8]) + bytes(14)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('Fw_SpawnHere -> %02X:%04X' % (FB, a))


if __name__ == '__main__':
    main()
