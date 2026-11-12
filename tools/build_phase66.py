#!/usr/bin/env python3
"""Phase 66: Jessie & James (trainer class 72) battle pic in two palettes like the Pikachu full-color hack
(PKFC $3A:$6B72: left 3 pic columns = James, blue-purple hair; right 4 = Jessie, magenta hair; colors from PKFC
$3A:$6C8C/$6C94), at the battle start and when they slide back in after the win. tools/asm/jjcolors.asm; bank 0x9C:$4400,
hook _CGB_FinishBattleScreenLayout's end $02:$4E73 (was a farcall to $90:$5E00, which the hook calls first).
usage: build_phase66.py IN.gbc OUT.gbc OUT.ips   (rgbds 1.0.4: ref/rgbds1)
"""
import sys, os, shutil, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

HUD_BANK = 0x9C


def main():
    src_rom, outrom, outips = [os.path.abspath(x) for x in sys.argv[1:4]]
    orig = open(JP_BASE, 'rb').read()
    rom = open(src_rom, 'rb').read()
    assert len(rom) == 0x400000
    h = fo(2, 0x4E73)
    assert rom[h:h + 9] == bytes([0x3E, 0x90, 0x21, 0x00, 0x5E, 0xCF, 0xC3, 0x70, 0x56])
    assert not any(rom[HUD_BANK * 0x4000 + 0x400:HUD_BANK * 0x4000 + 0x800])
    assert rom[fo(0x0F, 0x761F):fo(0x0F, 0x761F) + 6] == bytes([0x21, 0xAC, 0xC4, 0x01, 0x07, 0x07])  # hlcoord 12, 0 (wTilemap $C4A0)
    assert rom[fo(0x0F, 0x6BEA):fo(0x0F, 0x6BEA) + 4] == bytes([0xAF, 0xEA, 0x35, 0xD2])    # wTempEnemyMonSpecies $D235
    env = dict(os.environ, PATH=os.path.join(SC, 'ref', 'rgbds1') + ':' + os.environ['PATH'])
    with tempfile.TemporaryDirectory() as d:
        shutil.copy(src_rom, d + '/base.gbc')
        for c in (['rgbasm', '-o', d + '/h.o', os.path.join(SC, 'tools', 'asm', 'jjcolors.asm')],
                  ['rgblink', '-O', d + '/base.gbc', '-m', d + '/h.map', '-o', d + '/out.gbc', d + '/h.o']):
            r = subprocess.run(c, env=env, capture_output=True, text=True); assert r.returncode == 0, r.stderr
        out = bytearray(open(d + '/out.gbc', 'rb').read())
        print([l.strip() for l in open(d + '/h.map') if 'SECTION' in l])
    fix_checksum(out)
    open(outrom, 'wb').write(out)
    o2 = orig + bytes(len(out) - len(orig))
    p = ips(o2, bytes(out))
    p = p[:-3] + (len(out) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + out[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('changed bytes: %d' % len([i for i in range(len(out)) if out[i] != rom[i] and i not in (0x14E, 0x14F)]))


if __name__ == '__main__':
    main()
