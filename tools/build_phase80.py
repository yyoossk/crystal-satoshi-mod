#!/usr/bin/env python3
"""Phase 80: the Vermilion port passage's warps after the Kanto Hall of Fame (regression of phase 75).
 Phase 55 put the passage's after-Hall-of-Fame warp table (dock door -> Crystal's port) in the bank of the passage's
 events; phase 75 moved the events to another bank, so the switch (78:6326, ld hl, table) read zeros there: after the
 Hall of Fame the passage had no warps at all (its stairs did nothing, the port and the ship to Johto could not be
 reached).
 * the table is rebuilt from the current warps (the dock door -> Crystal's Vermilion Port) in the events' bank now.
 * the build checks that each switched table (passage, Lavender Town) sits in its map's events bank.
usage: build_phase80.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import Space

SWITCHES = (('LavenderTown', 0x5EA4, {1: ('LavRadioTower1F', 1)}),
            ('VermilionPortPassage', 0x6326, {4: ('VermilionPort', 1)}))


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom); log = []
    for name, fn, override in SWITCHES:
        a_ = attrs(rom, hdr_index(name)); sb = a_['scbank']
        ws = [bytearray(w) for _, w in parse_events(rom, sb, a_['events'])['warps']]
        o = fo(0x78, fn); assert rom[o] == 0x21
        p = rom[o + 1] | rom[o + 2] << 8; cur = rom[fo(sb, p):fo(sb, p) + 5 * len(ws)]
        want = [bytearray(w) for w in ws]
        for i, (mn, idx) in override.items():
            want[i][2] = idx; want[i][3], want[i][4] = mapid(mn)
        want = b''.join(bytes(w) for w in want)
        if bytes(cur) == want:
            log.append('%s: after-HoF warps OK (%X:%04X)' % (name, sb, p)); continue
        f, n = bank_free_tail(rom, sb)
        sp.set_area(sb, f + 1, sb * 0x4000 + 0x4000)
        na = sp.put(sb, want)
        rom[o + 1] = na & 0xFF; rom[o + 2] = na >> 8
        log.append('%s: after-HoF warps rebuilt in the events bank (%X:%04X)' % (name, sb, na))
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
