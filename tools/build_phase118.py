#!/usr/bin/env python3
"""Phase 118: Blue's (Viridian Gym) rematch team at Crystal's levels (found by the post-game check of 2026-11-18).
 The Kanto gym leaders' rematches are Crystal's teams (phase 50), but Blue's six were three levels lower than
 Crystal's (Pidgeot 53 / Alakazam 51 / Rhydon 53 / Gyarados 55 / Exeggutor 55 / Arcanine 55 since the MOD's first
 base); now 56 / 54 / 56 / 58 / 58 / 58 as in Crystal (data/trainers/parties.asm BlueGroup), in both copies of the
 party (the trainer data and phase 50's rematch copy).
usage: build_phase118.py IN.gbc OUT.gbc OUT.ips
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

SPECIES = [18, 65, 112, 130, 103, 59]
OLD, NEW = [53, 51, 53, 55, 55, 55], [56, 54, 56, 58, 58, 58]


def main():
    src, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src, 'rb').read())
    hits = []
    for o in range(len(rom) - 40):
        if all(rom[o + 6 * i] == OLD[i] and rom[o + 6 * i + 1] == SPECIES[i] for i in range(6)) and rom[o + 36] == 0xFF:
            hits.append(o)
    assert len(hits) == 2, [hex(h) for h in hits]
    for o in hits:
        for i in range(6): rom[o + 6 * i] = NEW[i]
        print("Blue's party at %X: %s" % (o, NEW))
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)


if __name__ == '__main__':
    main()
