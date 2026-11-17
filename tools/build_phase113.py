#!/usr/bin/env python3
"""Phase 113: surfing across a map connection (2026-11-17, found in the honest playthrough).
 Crystal's Surf starts with a scripted step (applymovement) that skips the map-edge check: surfing straight from the
 land at a map's edge onto the next map's water left the player on the old map, outside it (Cinnabar Island's east
 shore -> Route 20: the player drifted off Cinnabar's edge and could not reach Route 20).  Red's maps have such shores
 (Red's Surf steps with simulated input, so the edge is checked there).  pokecrystal's documented fix
 (docs/bugs_and_glitches.md "Surfing directly across a map connection does not load the new map"):
  * UsedSurfScript: `special SurfStartStep` then `end` (the applymovement is gone);
  * SurfStartStep: the step into the water is an auto-input button press (a normal step: edges and warps are checked).
usage: build_phase113.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

SCRIPT = 0xC9AB          # UsedSurfScript: special UpdatePlayerSprite / PlayMapMusic / SurfStartStep, applymovement PLAYER, wMovementBuffer, end
SSS = 0x8379             # SurfStartStep (02:4379) .. its slow_step table ends at 0x839E
START_AUTO_INPUT = 0x09E4
W_PLAYER_DIR = 0xD4D1


def main():
    src, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src, 'rb').read())
    assert rom[SCRIPT:SCRIPT + 14] == bytes.fromhex('0f38000f3c000f3f00680007d090'), rom[SCRIPT:SCRIPT + 14].hex()
    assert rom[SSS:SSS + 37] == bytes.fromhex('cde91acd8843cd0a1b3e47cd0a1bc9fad1d4cb3fcb3fe6035f1600219a43197ec908090a0b')
    rom[SCRIPT + 9] = 0x90                                      # end (instead of applymovement)
    data = 0x4379 + 23
    code = bytes([0xFA, W_PLAYER_DIR & 255, W_PLAYER_DIR >> 8, 0xCB, 0x3F, 0xCB, 0x3F, 0xE6, 0x03, 0x5F, 0x16, 0x00,
                  0x21, data & 255, data >> 8, 0x19, 0x19, 0x19, 0x3E, 0x02, 0xC3, START_AUTO_INPUT & 255, START_AUTO_INPUT >> 8])
    assert len(code) == 23
    table = bytes([0x80, 0, 0xFF, 0x40, 0, 0xFF, 0x20, 0, 0xFF, 0x10, 0, 0xFF])   # D U L R, 0 frames, end
    blob = code + table
    rom[SSS:SSS + len(blob)] = blob
    rom[SSS + len(blob):SSS + 37] = bytes(37 - len(blob))
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('Surf: auto-input step (map edges checked)')


if __name__ == '__main__':
    main()
