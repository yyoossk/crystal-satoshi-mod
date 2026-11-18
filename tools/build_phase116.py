#!/usr/bin/env python3
"""Phase 116: Victory Road after the Kanto Hall of Fame: no boulder puzzle again
(2026-11-18 request 「殿堂入り一回終わってるなら、二回目は岩はやらなくても通れるようにして」).
 Red's Victory Road (phase 23) puts its boulders and switches back every time (Route 23 resets them, 2F resets 1F's
 switch), so the Johto trip to the Indigo Plateau had the whole puzzle again.  Now each floor's MAPCALLBACK_TILES
 first checks the Kanto Hall of Fame: once it is done, every switch's opened blocks are put in (the barriers stay
 open) whatever the boulders and switches are; before it, the floor goes on as in Red (phase 23's own callback).
usage: build_phase116.py IN.gbc OUT.gbc OUT.ips
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

EV_KANTO_HOF = 0x034A
VR = [(26, 68), (26, 69), (26, 70)]               # Victory Road 1F / 2F / 3F (phase 23)
MGP = 0x94000                                     # MapGroupPointers (bank $25)


def header(rom, g, m):
    G = rom[MGP + 2 * (g - 1)] | rom[MGP + 2 * (g - 1) + 1] << 8
    return fo(0x25, G) + 9 * (m - 1)


def main():
    src, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src, 'rb').read())
    for g, m in VR:
        at = attrs(rom, header(rom, g, m))
        B = at['scbank']; o = fo(B, at['scripts'])
        ns = rom[o]; p = o + 1 + 4 * ns                       # scene scripts (dw script, dw 0)
        nc = rom[p]; p += 1
        cbs = [(p + 3 * i, rom[p + 3 * i], rom[p + 3 * i + 1] | rom[p + 3 * i + 2] << 8) for i in range(nc)]
        ent = [c for c in cbs if c[1] == 1]; assert len(ent) == 1, cbs
        at_, _, old = ent[0]
        # phase 23's callback: (checkevent fl ; iffalse L ; changeblock x, y, b ...)* endcallback
        q = fo(B, old); changes = []
        while rom[q] != 0x8F:
            op = rom[q]
            if op == 0x31 or op == 0x08: q += 3
            elif op == 0x79: changes.append(tuple(rom[q + 1:q + 4])); q += 4
            else: raise AssertionError('%d:%d %02x at %x' % (g, m, op, q))
        assert changes, (g, m)
        o2 = bank_free_tail(rom, B)[0] + 16
        base = 0x4000 + (o2 - B * 0x4000)
        a = Asm(base)
        a.checkevent(EV_KANTO_HOF); a.iffalse(old)
        for x, y, b in changes: a.changeblock(x, y, b)
        a.endcallback()
        blob = a.done()
        assert o2 + len(blob) <= (B + 1) * 0x4000 and not any(rom[o2:o2 + len(blob)])
        rom[o2:o2 + len(blob)] = blob
        rom[at_ + 1] = base & 0xFF; rom[at_ + 2] = base >> 8
        print('Victory Road %d:%d: %d blocks open after the Kanto Hall of Fame (%02X:%04X, old %04X)' % (g, m, len(changes), B, base, old))
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)


if __name__ == '__main__':
    main()
