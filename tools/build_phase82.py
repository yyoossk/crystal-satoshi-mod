#!/usr/bin/env python3
"""Phase 82: Team Rocket's Goldenrod / Radio Tower events count the Johto badges only.
 Each Johto gym leader's script reads VAR_BADGES and starts the Goldenrod takeover at 6 badges and the Radio Tower
 takeover at 7 (Crystal).  VAR_BADGES counts the Johto and the Kanto badges together; in this MOD the player already
 has the 8 Kanto badges, so the count was 14 / 15 and the takeover never started: the story stopped after the 7th
 Johto badge (Radio Tower, Ice Path, ...).
 * the gyms' "activate rockets" subscripts (ifequal 7 / ifequal 6 / end) now first count the Johto badges only.
usage: build_phase82.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import Space

COUNTSETBITS = 0x332B            # home: CountSetBits (hl, b bytes) -> a
W_JOHTO_BADGES, W_SCRIPTVAR = 0xD84A, 0xC2DD
BANK = 0x63


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    f, n = bank_free_tail(rom, BANK); sp.set_area(BANK, f + 1, BANK * 0x4000 + 0x4000)
    # the counting routine
    asm = bytes([0x21, W_JOHTO_BADGES & 0xFF, W_JOHTO_BADGES >> 8, 0x06, 0x01,
                 0xCD, COUNTSETBITS & 0xFF, COUNTSETBITS >> 8,
                 0xEA, W_SCRIPTVAR & 0xFF, W_SCRIPTVAR >> 8, 0xC9])
    cnt = sp.put(BANK, asm)
    sites = []
    for m in re.finditer(rb'\x1c\x07\x00(..)', rom):
        bank = m.start() // 0x4000; ta = m.group(1)[0] | m.group(1)[1] << 8
        if not 0x4000 <= ta < 0x8000: continue
        t = fo(bank, ta)
        r = rom[t:t + 9]
        if r[0] == 0x06 and r[1] == 7 and r[4] == 0x06 and r[5] == 6 and r[8] == 0x90:
            sites.append((bank, ta, r[2] | r[3] << 8, r[6] | r[7] << 8))
    assert len(sites) == 7, sites
    log = []
    for bank, ta, rt, gt in sites:
        blk = bytes([0x0E, BANK, cnt & 0xFF, cnt >> 8])                       # callasm count (0E)
        here = sp.here(BANK)
        # ifequal 7, +R ; ifequal 6, +G ; end ; R: farsjump bank:rt ; G: farsjump bank:gt
        base = here
        r_at = base + 4 + 4 + 4 + 1; g_at = r_at + 4
        blk += bytes([0x06, 7, r_at & 0xFF, r_at >> 8, 0x06, 6, g_at & 0xFF, g_at >> 8, 0x90,
                      0x04, bank, rt & 0xFF, rt >> 8, 0x04, bank, gt & 0xFF, gt >> 8])
        assert sp.put(BANK, blk) == base
        t = fo(bank, ta); rom[t:t + 4] = bytes([0x04, BANK, base & 0xFF, base >> 8])   # farsjump
        log.append('%02X:%04X -> %02X:%04X' % (bank, ta, BANK, base))
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('Johto badge count for the rockets:', ', '.join(log))


if __name__ == '__main__':
    main()
