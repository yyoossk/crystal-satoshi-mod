#!/usr/bin/env python3
"""Phase 99: Shigeru's walking picture in the same colours as in the Red full-color hack (blue: the hack draws the
rival with OBJ palette 1 = skin / blue (10,9,31), which is Crystal's PAL_OW_BLUE as the kit's skin colour made it).
Crystal's SPRITE_BLUE ($07, which this MOD uses for Shigeru everywhere: Oak's lab, Route 22, Cerulean, S.S. Anne,
Pokémon Tower, Silph Co., the champion's room, Viridian Gym) had PAL_OW_RED; none of his objects sets a colour of its
own, so the sprite table's palette decides.
usage: build_phase99.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

OW_SPRITES = 0x14727               # OverworldSprites (JP), 6 bytes from sprite 1
SPRITE_BLUE, PAL_OW_RED, PAL_OW_BLUE = 0x07, 0, 1


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    e = OW_SPRITES + (SPRITE_BLUE - 1) * 6
    assert rom[e + 5] == PAL_OW_RED, rom[e:e + 6].hex()
    rom[e + 5] = PAL_OW_BLUE
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('SPRITE_BLUE: PAL_OW_BLUE')


if __name__ == '__main__':
    main()
