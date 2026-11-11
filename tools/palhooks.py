"""The chain of special-map-palette hooks in bank 12 (portmaps.Tilesets.add and later phases): parse it into
[(tileset id, (bank, palettes address))], (build_phase44 replaces it with one table-driven routine)."""
from lib import *
from portlib import *


def parse(rom):
    end = 0x4000 + (LSMP + 3) % 0x4000                      # the original routine, after its ld a, [wMapTileset]
    assert rom[LSMP] == 0xC3
    def r16(o): return rom[o] | rom[o + 1] << 8
    p = r16(LSMP + 1); out = []; ld_ts = None
    while p != end:
        o = fo(0x12, p); assert rom[o] == 0xFA, hex(p)
        ld_ts = bytes(rom[o:o + 3]); k = o + 3; targets = []; nxt = None
        while rom[k] == 0xFE:
            i = rom[k + 1]; op = rom[k + 2]
            if op == 0x28: d = rom[k + 3]; d = d - 256 if d > 127 else d; targets.append((i, k + 4 + d)); k += 4
            elif op == 0xC2: nxt = r16(k + 3); targets.append((i, k + 5)); k += 5; break
            else: raise ValueError(hex(p))
        if nxt is None:
            assert rom[k] == 0xC3, hex(p); nxt = r16(k + 1)
        for i, t in targets:
            if rom[t] == 0x21:                                  # ld hl, pals (bank 12)
                out.append((i, (0x12, r16(t + 1))))
            elif rom[t:t + 3] == bytes([0x3E, 0x05, 0x11]) and rom[t + 5] == 0x21:      # (phase 11's order)
                out.append((i, (0x12, r16(t + 6))))
            elif rom[t] == 0x3E and rom[t + 2] == 0x21:         # farcall bank:routine (ld hl, pals ...)
                b = rom[t + 1]; c = fo(b, r16(t + 3)); assert rom[c] == 0x21
                out.append((i, (b, r16(c + 1))))
            else: raise ValueError((hex(p), i))
        p = nxt
    return out, ld_ts, end

