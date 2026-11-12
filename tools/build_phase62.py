#!/usr/bin/env python3
"""Phase 62: the kit 「御三家・セレビィ・交換進化キット」 (kitev/御三家・セレビィ・交換進化キット): only what this MOD did not
have yet, the trade evolutions (src/tradeevo_crystal.asm): Politoed, Kingdra, Steelix, Scizor, Porygon2 at Lv 37
(Poliwhirl, Seadra, Onix, Scyther, Porygon), Slowking: Slowpoke holding the King's Rock at Lv 37 or more (else
Slowbro at Lv 37); the trade check of EvolveAfterBattle ($10:$641C) -> ED_TradeCheck ($10:$7FA0, free here).
Already in this MOD (not built): Kanto's starters (phase 58), Celebi and Johto's starters (phase 61), and
Alakazam / Machamp / Golem / Gengar at Lv 37 (phase 57: the same bytes as the kit's).
tools/overlap_check.py on the original Crystal: only those four entries (the same bytes) and the checksum.
usage: build_phase62.py IN.gbc OUT.gbc OUT.ips   (rgbds 1.0.4: ref/rgbds1)
"""
import sys, os, shutil, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

KIT = os.path.join(SC, 'kitev', '御三家・セレビィ・交換進化キット')


def main():
    src_rom, outrom, outips = [os.path.abspath(x) for x in sys.argv[1:4]]
    orig = open(JP_BASE, 'rb').read()
    rom = open(src_rom, 'rb').read()
    assert not any(rom[fo(0x10, 0x7FA0):fo(0x10, 0x7FB7)])
    assert rom[fo(0x10, 0x641C):fo(0x10, 0x6423)] == orig[fo(0x10, 0x641C):fo(0x10, 0x6423)]
    for a in (0x6E2F, 0x7125, 0x7317, 0x739A, 0x74BD, 0x6FC9): assert rom[fo(0x10, a)] == 0x03, hex(a)
    for a in (0x6E5D, 0x6EA5, 0x6F5E, 0x70F6): assert rom[fo(0x10, a):fo(0x10, a) + 2] == bytes([0x01, 37])
    shutil.copy(src_rom, os.path.join(KIT, 'base.gbc'))
    env = dict(os.environ, PATH=os.path.join(SC, 'ref', 'rgbds1') + ':' + os.environ['PATH'])
    r = subprocess.run(['python3', 'build.py', 'feat.gbc', 'src/tradeevo_crystal.asm'], cwd=KIT, env=env, capture_output=True, text=True)
    print(r.stdout.strip()); assert r.returncode == 0, r.stderr
    out = bytearray(open(os.path.join(KIT, 'feat.gbc'), 'rb').read())
    fix_checksum(out)
    open(outrom, 'wb').write(out)
    open(outips, 'wb').write(ips(orig, bytes(out)))
    print('kit bytes: %d' % len([i for i in range(len(out)) if out[i] != rom[i] and i not in (0x14E, 0x14F)]))


if __name__ == '__main__':
    main()
