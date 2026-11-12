#!/usr/bin/env python3
"""Phase 65: in the Safari Zone (phase 28, Red's), the remaining steps and Safari Balls are always shown at the bottom
of the screen while walking (the kit 「クリスタル追加機能キット」's SafariHUD, src/safari/safari.asm, adapted to this
MOD's Safari game: tools/asm/safarihud.asm; bank 0x9C, hook PlaceMapNameSign .disappear $2E:$40BC).
usage: build_phase65.py IN.gbc OUT.gbc OUT.ips   (rgbds 1.0.4: ref/rgbds1)
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
    h = fo(0x2E, 0x40BC)
    assert rom[h:h + 10] == bytes([0x3E, 0x90, 0xE0, 0x4A, 0xE0, 0xD2, 0xAF, 0xE0, 0xC6, 0xC9]) == orig[h:h + 10]
    assert not any(rom[HUD_BANK * 0x4000:HUD_BANK * 0x4000 + 0x400])
    assert rom[fo(0x6E, 0x7140):fo(0x6E, 0x7143)] == bytes([0xFA, 0x7B, 0xDC])      # phase 28's "in the Safari Zone?"
    env = dict(os.environ, PATH=os.path.join(SC, 'ref', 'rgbds1') + ':' + os.environ['PATH'])
    with tempfile.TemporaryDirectory() as d:
        shutil.copy(src_rom, d + '/base.gbc')
        for c in (['rgbasm', '-o', d + '/h.o', os.path.join(SC, 'tools', 'asm', 'safarihud.asm')],
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
