#!/usr/bin/env python3
"""Phase 102: Viridian Forest's music as in Red / the Red full-color hack: Red's Music_Dungeon2, converted to Crystal's
sound engine (tools/gen1audio.py, as phase 53 did), so Crystal's sound effects still play in the forest.
Red plays the same song in Diglett's Cave, the Seafoam Islands and the Route 22 gate: those maps too.
 * The song takes music id $52 (MUSIC_GS_OPENING: never played by Crystal; phase 53's converted title, which phase 68
   replaced with Red's own engine).  Red's drums 9-13 = Crystal's drum kit 1 entries 2-6 (same noise notes).
 * Map music (map header byte 6): Viridian Forest 26:84, Diglett's Cave 26:86 / 26:110 / 26:149, Seafoam Islands
   26:63-67; the gate between Routes 22 and 23 is Crystal's Victory Road Gate here (23:13), its own music stays.
usage: build_phase102.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from gen1audio import Song
from build_phase17 import US

FC = SC + '/akafc/akafc.gbc'
MUSIC_TABLE = 0x506E               # bank 3A, 3 bytes per song
MUS_ID = 0x52
RED_SFX_HEADERS, MUSIC_DUNGEON2 = 0x6EBF, 0xE4      # bank 1F
AUD_BANK = 0x20
MAPS = [(26, 84), (26, 86), (26, 110), (26, 149), (26, 63), (26, 64), (26, 65), (26, 66), (26, 67)]


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read()); log = []
    F = open(FC, 'rb').read()
    song = Song(F, 0x1F, RED_SFX_HEADERS + 3 * MUSIC_DUNGEON2, {9: 2, 10: 3, 11: 4, 12: 5, 13: 6}, 1)
    f, n = bank_free_tail(rom, AUD_BANK); f += 16
    base = 0x4000 + f % 0x4000
    h, data = song.build(base)
    assert len(data) + 32 < n
    rom[f:f + len(data)] = data
    t = fo(0x3A, MUSIC_TABLE) + 3 * MUS_ID
    rom[t:t + 3] = bytes([AUD_BANK, h & 0xFF, h >> 8])
    log.append('Music_Dungeon2 -> music $%02X (%02X:%04X, %d bytes)' % (MUS_ID, AUD_BANK, h, len(data)))
    G = US.get().groups()
    for g, m in MAPS:
        hd = G[g - 1] + 9 * (m - 1)
        log.append('%d:%d music %02X -> %02X' % (g, m, rom[hd + 6], MUS_ID)); rom[hd + 6] = MUS_ID
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
