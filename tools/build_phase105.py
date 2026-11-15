#!/usr/bin/env python3
"""Phase 105: the music when a trainer of one of the MOD's new classes sees the player (Route 11's gamblers and
engineers played nothing).
PlayTrainerEncounterMusic (3A:5013; ld d,0 / ld hl,TABLE / add hl,de / ld e,[hl] at 3A:501C) reads TrainerEncounterMusic (3A:5027), one byte per trainer class; the table has
71 entries (classes 0-67 and 3 unused), but phase 10 added classes 68-79, so classes 71-79 read the bytes after the
table (GAMBLER: 0 = no music, ENGINEER: $78 ...).  The table is now copied, with entries for every new class, to a
bank with room, and read through a farcall (bank 3A has no room):
  68-70 Elite Four / Lance (Kanto): hiker (as before), 71 Giovanni / 72 Jessie & James: Rocket, 73 Jr. Trainer F
  (picnicker's): lass, 74 Tamer (juggler's): Pokémaniac, 75 Jr. Trainer M (camper's): youngster, 76 Engineer, 77 Cue
  Ball, 78 Gambler, 79 Rocker: hiker (the male trainers' encounter music, as their Crystal classes).
usage: build_phase105.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

B, TABLE = 0x3A, 0x5027
OLD_N = 71
NEW = [0x0A, 0x0A, 0x0A, 0x39, 0x39, 0x0B, 0x3A, 0x37, 0x0A, 0x0A, 0x0A, 0x0A]   # classes 68-79
NEW_FROM = 68


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    t = fo(B, TABLE)
    assert rom[t:t + 10] == bytes.fromhex('0a 37 0b 37 0c 0c 0b 0c 38 1f')
    h = fo(B, 0x501C)
    assert rom[h:h + 7] == bytes.fromhex('16 00 21 27 50 19 5e'), rom[h - 2:h + 10].hex()
    tab = bytearray(rom[t:t + OLD_N])
    tab[NEW_FROM:] = bytes(NEW)
    nb = next(x for x in range(0x40, len(rom) // 0x4000) if bank_free_tail(rom, x)[1] >= len(tab) + 32)
    f, n = bank_free_tail(rom, nb); f += 4
    a = 0x4000 + f % 0x4000
    code = bytes([0x16, 0x00, 0x21]) + (a + 8).to_bytes(2, 'little') + bytes([0x19, 0x5E, 0xC9])   # ld d,0 / ld hl,tab / add hl,de / ld e,[hl] / ret
    rom[f:f + 8] = code; rom[f + 8:f + 8 + len(tab)] = tab
    rom[h:h + 7] = bytes([0x3E, nb, 0x21, a & 0xFF, a >> 8, 0xCF, 0x00])                           # farcall / nop
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('TrainerEncounterMusic: %d entries at %02X:%04X (read via farcall from 3A:501C)' % (len(tab), nb, a + 8))


if __name__ == '__main__':
    main()
