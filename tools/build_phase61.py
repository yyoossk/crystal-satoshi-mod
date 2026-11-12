#!/usr/bin/env python3
"""Phase 61: the kit 「御三家・セレビィキット」 (kitgs/御三家・セレビィキット, from the Crystal feature patch Ver.1.5.0):
 * Celebi (src/celebi_crystal.asm, without the legendary birds: this MOD has Red's): after the Hall of Fame (Johto's,
   EVENT_BEAT_ELITE_FOUR) the Ilex Forest shrine: Celebi Lv 30, once.
 * Johto's starters (src/johto3_crystal.asm): choosing one at Prof. Elm's lab gives the other two too; on a save that
   already has one, Prof. Elm gives the other two.
 Kanto's starters (the kit's src/starters_crystal.asm) are not built: phase 58 already gives them in this MOD's
 (Red's) Kanto maps the Pikachu version's way (Melanie's house, Route 24, Officer Jenny).
 tools/overlap_check.py on the original Crystal: bank $77 (the kit's Celebi) is used by this MOD -> $47:$7E40 (free);
 bank $6E $4000 / $6E00, $19:$7FF8, $1B:$7FF8, $D836 / $D837 are free here; Elm's lab and the Ilex Forest shrine
 are Crystal's here (the kit's addresses hold).
usage: build_phase61.py IN.gbc OUT.gbc OUT.ips   (rgbds 1.0.4: ref/rgbds1)
"""
import sys, os, re, shutil, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

KIT = os.path.join(SC, 'kitgs', '御三家・セレビィキット')
LG_BANK, LG_ADDR = 0x47, 0x7E40


def main():
    src_rom, outrom, outips = [os.path.abspath(x) for x in sys.argv[1:4]]
    orig = open(JP_BASE, 'rb').read()
    rom = open(src_rom, 'rb').read()
    assert not any(rom[fo(LG_BANK, LG_ADDR):fo(LG_BANK, LG_ADDR) + 0xC0])
    for b, a, n in ((0x6E, 0x4000, 0x100), (0x6E, 0x6E00, 0x180), (0x19, 0x7FF8, 4), (0x1B, 0x7FF8, 4)):
        assert rom[fo(b, a):fo(b, a) + n] == orig[fo(b, a):fo(b, a) + n] and not any(rom[fo(b, a):fo(b, a) + n]), hex(b)
    assert rom[fo(0x1B, 0x7302):fo(0x1B, 0x7302) + 2] == bytes([0xF5, 0x61]) and rom[fo(0x19, 0x64CE):fo(0x19, 0x64CE) + 2] == bytes([0x22, 0x60])
    for a in (0x62B7, 0x62F9, 0x6335): assert rom[fo(0x1B, a)] == 0x2D and rom[fo(0x1B, a) + 2:fo(0x1B, a) + 5] == bytes([5, 0xAD, 0])
    shutil.copy(src_rom, os.path.join(KIT, 'base.gbc'))
    s = open(os.path.join(KIT, 'src', 'celebi_crystal.asm'), encoding='utf-8').read()
    s = re.sub(r'DEF LG_BANK\s+EQU \$77', 'DEF LG_BANK            EQU $%02x' % LG_BANK, s)
    s = re.sub(r'DEF LG_ADDR\s+EQU \$6000', 'DEF LG_ADDR            EQU $%04x' % LG_ADDR, s)
    assert '$%02x' % LG_BANK in s and '$%04x' % LG_ADDR in s
    open(os.path.join(KIT, 'src', 'celebi_mod.asm'), 'w', encoding='utf-8').write(s)
    env = dict(os.environ, PATH=os.path.join(SC, 'ref', 'rgbds1') + ':' + os.environ['PATH'])
    r = subprocess.run(['python3', 'build.py', 'feat.gbc', 'src/celebi_mod.asm', 'src/johto3_crystal.asm'],
                       cwd=KIT, env=env, capture_output=True, text=True)
    print(r.stdout.strip()); assert r.returncode == 0, r.stderr
    out = bytearray(open(os.path.join(KIT, 'feat.gbc'), 'rb').read())
    fix_checksum(out)
    open(outrom, 'wb').write(out)
    open(outips, 'wb').write(ips(orig, bytes(out)))
    d = [i for i in range(len(out)) if out[i] != rom[i] and i not in (0x14E, 0x14F)]
    print('kit bytes: %d' % len(d))


if __name__ == '__main__':
    main()
