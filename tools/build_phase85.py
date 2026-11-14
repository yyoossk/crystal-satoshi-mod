#!/usr/bin/env python3
"""Phase 85: the fast ship after its first voyage (Vermilion -> New Bark Town).
 In Crystal the first voyage ends at Vermilion Port, whose script marks it (EVENT_FAST_SHIP_FIRST_TIME) and sends the
 granddaughter, her grandpa and the first trip's passengers away.  This MOD's first voyage ends at New Bark Town
 (phase 47), so none of that happened: on every later voyage the grandpa ran into the player on 1F again ("my
 granddaughter is missing!") while she sat with him in his cabin, and the first trip's passengers stayed aboard.
 * When the ship docks at the end of the first voyage (phase 81's line in the captain's cabin) those events are set.
usage: build_phase85.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import Space

STUB = (0x1A, 0x7FCC)              # phase 81: farsjump 5B:79A3 (the docking line)
HANDLER = (0x5B, 0x79A3)
EV_ARRIVED = 0x34C                 # phase 47: the player has reached Johto
SET = [0x30, 0x731, 0x730, 0x739]  # FAST_SHIP_FIRST_TIME, the granddaughter and her grandpa in the cabin, first trip's passengers
PB = 0x5B


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    f, n = bank_free_tail(rom, PB); sp.set_area(PB, f + 1, PB * 0x4000 + 0x4000)
    o = fo(*STUB); assert rom[o:o + 4] == bytes([0x04, HANDLER[0], HANDLER[1] & 0xFF, HANDLER[1] >> 8])
    here = sp.here(PB)
    fj = bytes([0x04, HANDLER[0], HANDLER[1] & 0xFF, HANDLER[1] >> 8])
    body = b''.join(bytes([0x33, e & 0xFF, e >> 8]) for e in SET) + fj              # setevent ... ; farsjump
    skip = here + 3 + 3 + len(body)
    blk = bytes([0x31, EV_ARRIVED & 0xFF, EV_ARRIVED >> 8, 0x09, skip & 0xFF, skip >> 8]) + body + fj
    assert sp.put(PB, blk) == here
    rom[o + 1] = PB; rom[o + 2] = here & 0xFF; rom[o + 3] = here >> 8
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('fast ship first voyage end: events set at %02X:%04X' % (PB, here))


if __name__ == '__main__':
    main()
