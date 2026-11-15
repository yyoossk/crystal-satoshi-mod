#!/usr/bin/env python3
"""Phase 101: the map name sign when entering Kanto's caves and buildings.
 * Landmarks (map header byte 5) of the MOD's new maps that were wrong:
     Mt. Moon 1F / B1F / B2F (26:37-39): Route 3 -> おつきみやま (LANDMARK_MT_MOON);
     the Underground Path entrances on Routes 6 / 7 / 8 (26:140-142): Route 5 -> Route 6 / 7 / 8;
     Diglett's Cave's Route 11 entrance (26:110): Route 11 -> ディグダのあな (as the Route 2 entrance, 26:86).
   (Viridian Forest, Pokémon Tower, Silph Co., Cerulean Cave, ... have no landmark of their own in Crystal: they keep
   the town's / route's, so no sign shows, as in Crystal for places without a name.)
 * Colour: phase 92 gave the sign Crystal's colours (palette 7 = Crystal's text palette) only in towns and routes; the
   sign also shows in caves (Mt. Moon, Rock Tunnel, Seafoam, Victory Road, ...): now for every Kanto map with the
   ported palettes.
usage: build_phase101.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from build_phase17 import US

MT_MOON, ROUTE_3, ROUTE_5, ROUTE_6, ROUTE_7, ROUTE_8, ROUTE_11, DIGLETTS = 0x35, 0x34, 0x3A, 0x3C, 0x3F, 0x40, 0x49, 0x3E
FIX = {(26, 37): (ROUTE_3, MT_MOON), (26, 38): (ROUTE_3, MT_MOON), (26, 39): (ROUTE_3, MT_MOON),
       (26, 140): (ROUTE_5, ROUTE_6), (26, 141): (ROUTE_5, ROUTE_7), (26, 142): (ROUTE_5, ROUTE_8),
       (26, 110): (ROUTE_11, DIGLETTS)}
P92 = (0x6A, 0x74AF)               # call / ret nc / ld a,[wEnvironment] / dec a / cp 2 / ccf / ret c


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read()); log = []
    G = US.get().groups()
    for (g, m), (old, new) in FIX.items():
        h = G[g - 1] + 9 * (m - 1)
        assert rom[h + 5] == old, ((g, m), hex(rom[h + 5]))
        rom[h + 5] = new
        log.append('%d:%d landmark %02X -> %02X' % (g, m, old, new))
    o = fo(*P92)
    assert rom[o + 4:o + 12] == bytes.fromhex('fa cb d1 3d fe 02 3f d8'), rom[o:o + 12].hex()
    rom[o + 11] = 0x00                                     # ret c -> nop: every environment
    log.append('sign colours: every Kanto map')
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
