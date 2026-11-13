#!/usr/bin/env python3
"""Phase 69: the ledges of Red's maps (tileset 40: Route 1, Viridian City, Route 22, ...) work as in Red.
Phase 30 gave the ledge tiles Crystal's hop collisions, but Crystal jumps only when standing ON a hop tile facing a
wall, so the player walked onto and through Red's ledges (both ways) without jumping.  Now on tileset 40, walking
into a ledge tile from the tile before it in the ledge's direction jumps it (Crystal's ledge jump: sound, 2 tiles);
from any other side it is a wall.  Johto is unchanged.
Hook: TryStep ($20:$4176, its call to CheckLandPerms) -> RedLedge (bank $20 free space). tools/asm/p69/phase69.asm
usage: build_phase69.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from build_phase52 import rgbds

ASM = os.path.dirname(os.path.abspath(__file__)) + '/asm/p69'


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    assert rom[fo(0x20, 0x4176):fo(0x20, 0x4176) + 3] == bytes([0xCD, 0x9E, 0x43])
    assert rom[fo(0x20, 0x41F3):fo(0x20, 0x41F3) + 9] == bytes.fromhex('fad7d45fe6f0fea020')   # .TryJump
    assert rom[fo(0x20, 0x421E):fo(0x20, 0x421E) + 8] == bytes([1, 2, 4, 8, 9, 0x0A, 5, 6])  # .ledge_table
    f, n = bank_free_tail(rom, 0x20); addr = f % 0x4000 + 0x4000 + 1; assert n > 64
    with tempfile.TemporaryDirectory() as d:
        open(d + '/in.gbc', 'wb').write(rom)
        subprocess.run([rgbds('rgbasm'), '-D', 'P69_ADDR=$%X' % addr, '-o', d + '/a.o', ASM + '/phase69.asm'], check=True)
        subprocess.run([rgbds('rgblink'), '-O', d + '/in.gbc', '-o', d + '/out.gbc', d + '/a.o'], check=True)
        new = open(d + '/out.gbc', 'rb').read()
    assert len(new) == len(rom)
    rom[:] = new
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)


if __name__ == '__main__':
    main()
