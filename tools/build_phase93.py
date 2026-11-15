#!/usr/bin/env python3
"""Phase 93: balls with a Pokémon in them, and Fuchsia City's Voltorb, look as in the Pikachu full-color hack.
The Pikachu full-color hack draws SPRITE_POKE_BALL with other pictures on some maps (bank 3B: Fuchsia City -> a
Voltorb with eyes; Oak's lab, Celadon Mansion's roof room, the Fighting Dojo -> the Poké Ball with the black band and
button).  Here those objects used Crystal's item ball (the kit's: red top, white bottom, no band).
 * Oak's lab (3 balls), the Fighting Dojo (2), the Eevee room on Celadon Mansion's roof: the kit's lab ball, sprite $79
   (the same picture as the Pikachu full-color hack's).
 * Fuchsia City's Voltorb (25, 6): new sprite $7A (the second sprite table) with the hack's Voltorb picture (4 tiles,
   still, red palette).  The kit's field colours (01:7F00 FieldColors_InitFlags) make the lower half of $54 / $79 white;
   $7A is added there (01:7FF2).
usage: build_phase93.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import Space
import build_phase10 as P10
from build_phase17 import US, attrs

LAB_BALL, VOLTORB = 0x79, 0x7A
SPR2 = (0x05, 0x7F34)              # second sprite table ($67-)
PKFC_VOLTORB = 0xEED9B             # PKFC 3B:6D9B (4 tiles)
BALL_OBJS = {(13, 6): 3, (25, 3): 2, (26, 137): 1}   # Oak's lab, Fighting Dojo, Celadon Mansion roof room (Eevee)
FUCHSIA, VOLTORB_AT = (17, 5), (25, 6)
INITFLAGS = (0x01, 0x7F08)         # ld a,[bc] / cp $54 / jr z,.ball / cp $79 / ld a,h / jr nz,.set / db $fe / .ball ...
GFX_BANK = 0x6A


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read()); log = []
    pk = open(P10.PKFC, 'rb').read()
    u = US.get(); G = u.groups()
    def objs(k):
        hdr = G[k[0] - 1] + 9 * (k[1] - 1); a = attrs(rom, hdr)
        return parse_events(rom, a['scbank'], a['events'])['objs']
    # ---- balls
    for k, n in BALL_OBJS.items():
        hit = [p for p, o in objs(k) if o[0] == 0x54 and o[7] & 0x0F == 0]
        assert len(hit) == n, (k, len(hit))
        for p in hit: rom[p] = LAB_BALL
        log.append('%s: %d balls -> sprite %02X' % (k, n, LAB_BALL))
    # ---- Voltorb sprite
    v = pk[PKFC_VOLTORB:PKFC_VOLTORB + 64]
    assert v[:8] == bytes.fromhex('0000000003030c0f')
    f, n = bank_free_tail(rom, GFX_BANK); f += 16; assert n > 128
    rom[f:f + 64] = v; ga = 0x4000 + f % 0x4000
    e = fo(*SPR2) + 6 * (VOLTORB - 0x67)
    assert rom[e - 6:e] == bytes([0x00, 0x60, 0x40, 0x90, 0x03, 0x00]) and not any(rom[e:e + 6])
    rom[e:e + 6] = bytes([ga & 0xFF, ga >> 8, 0x40, GFX_BANK, 0x03, 0x00])     # 4 tiles, STILL_SPRITE, PAL_OW_RED
    hit = [p for p, o in objs(FUCHSIA) if o[0] == 0x54 and (o[2] - 4, o[1] - 4) == VOLTORB_AT]
    assert len(hit) == 1; rom[hit[0]] = VOLTORB
    log.append('Fuchsia Voltorb -> sprite %02X (gfx %02X:%04X)' % (VOLTORB, GFX_BANK, ga))
    # Fuchsia's map group: $7A into the outdoor sprite set (in place of an entry no outdoor map of the group uses)
    import build_phase17 as P17
    gi = FUCHSIA[0] - 1; tab = fo(*P17.OUTDOOR_SPRITES_PTR)
    lp = fo(5, rom[tab + 2 * gi] | rom[tab + 2 * gi + 1] << 8)
    lst = list(rom[lp:lp + 23]); used = set()
    for k in range((G[gi + 1] - G[gi]) // 9):
        hdr = G[gi] + 9 * k
        if rom[hdr + 2] not in (1, 2): continue
        used |= {o[0] for _, o in objs((FUCHSIA[0], k + 1))}
    free = [i for i, x in enumerate(lst) if x not in used]; assert free and VOLTORB not in lst
    lst[free[0]] = VOLTORB; rom[lp:lp + 23] = bytes(lst)
    log.append('outdoor sprites group %d: [%d] -> %02X' % (FUCHSIA[0], free[0], VOLTORB))
    # ---- field colours: $7A is a ball too
    o = fo(*INITFLAGS)
    old = bytes.fromhex('0a fe 54 28 06 fe 79 7c 20 04 fe 7c f6 01 e0 c2 c9')
    assert rom[o:o + len(old)] == old, rom[o:o + len(old)].hex()
    f1, n1 = bank_free_tail(rom, 0x01); assert n1 >= 12; f1 += 2
    ib = 0x4000 + f1 % 0x4000 if f1 >= 0x4000 else f1
    rom[f1:f1 + 10] = bytes.fromhex('0a fe 54 c8 fe 79 c8 fe 7a c9')       # z if $54 / $79 / $7A
    new = bytes([0xCD, ib & 0xFF, ib >> 8, 0x7C, 0x20, 0x02, 0xF6, 0x01, 0xE0, 0xC2, 0xC9])
    rom[o:o + len(old)] = new + bytes(len(old) - len(new))
    log.append('FieldColors_InitFlags: ball check 01:%04X' % ib)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
