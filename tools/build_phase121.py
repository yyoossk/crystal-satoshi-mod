#!/usr/bin/env python3
"""Phase 121: Crystal's own bugs, part 3 (docs/bugs_and_glitches.md, as phases 119-120):
 1. Confusion damage is boosted by type-boosting items (a flag in Crystal's unused byte after wTurnEnded, $C6A9:
    set by HitSelfInConfusion, read and cleared by the damage calculation's item step).  (The Explosion halving of
    the same document entry is left: only when a Pokemon using Explosion hurts itself in confusion.)
 2. Mania uses the wrong line when Shuckie is your last Pokemon (.nothingleft)
 3. Clair can give TM24 Dragonbreath twice (the Dragon's Den B1F scene does nothing once the TM is had)
 4. The Ruins of Alph research center's roof at night (group 3 roof colors = Cinnabar's)
 5. Slowpoke Well's stones use the wrong corner tile (johto_modern block $5B: $4B -> $47)
 6. The battle "..." ellipsis is two pixels too high
usage: build_phase121.py IN.gbc OUT.gbc OUT.ips
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

FLAG = 0xC6A9                       # (US: the `ds 1` between wTurnEnded and wPlayerStats; no code uses it)


def expect(rom, o, hexs):
    b = bytes.fromhex(hexs.replace(' ', ''))
    assert rom[o:o + len(b)] == b, (hex(o), rom[o:o + len(b)].hex(' '), hexs)
    return b


def w16(v): return bytes([v & 0xFF, v >> 8])
def ga(o): return o % 0x4000 + (0x4000 if o >= 0x4000 else 0)


def main():
    src, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src, 'rb').read())
    log = []
    free = {}
    def put(bank, code):
        if bank not in free: free[bank] = bank_free_tail(rom, bank)[0] + 2
        a = free[bank]; assert a + len(code) <= bank * 0x4000 + 0x4000 and not any(rom[a:a + len(code)]), hex(bank)
        rom[a:a + len(code)] = code; free[bank] += len(code); return ga(a)

    # 1. confusion damage and items
    o = 0x355DD + 50; expect(rom, o - 5, 'cd 4d 53 16 28 f1 5f c9')
    h = put(0x0D, bytes([0xF1, 0x5F, 0x3E, 0x01, 0xEA]) + w16(FLAG) + bytes([0xC9]))
    rom[o:o + 3] = bytes([0xC3]) + w16(h)
    dc = 0x35612; i = rom.find(bytes.fromhex('cd037e78a72826'), dc, dc + 0x80); assert i > 0
    hi = put(0x0D, bytes([0xFA]) + w16(FLAG) + bytes([0xA7, 0xCA, 0x03, 0x7E, 0xAF, 0xEA]) + w16(FLAG) + bytes([0x47, 0xC9]))
    rom[i + 1:i + 3] = w16(hi)
    log.append('1 confusion damage: HitSelfInConfusion -> 0D:%04X, item step -> 0D:%04X' % (h, hi))
    # 2. Mania: ifequal SHUCKIE_FAINTED, .default_postevent (19:65E4) -> .nothingleft (19:65DE)
    o = 0x665B0; expect(rom, o, '06 00 c9 65 06 01 d8 65 06 03 cf 65 06 04 e4 65')
    expect(rom, 0x665DE, '4c'); assert rom[0x665DE + 3:0x665DE + 6] == bytes([0x53, 0x49, 0x90])
    rom[o + 14] = 0xDE
    # 3. Clair's TM24 in the Dragon's Den B1F: the coord event's script checks EVENT_GOT_TM24_DRAGONBREATH ($0F) first
    co = None
    import mapdb_jp as M
    ce = M.coords(rom, 3, 81)
    assert len(ce) == 1 and ce[0][1][:4] == bytes([1, 0x1E, 0x13, 0]) and ce[0][1][4:6] == bytes([0x0D, 0x4E]), ce
    expect(rom, 0x1C * 0x4000 + 0x4E0D - 0x4000 + 28, '1f d7 01')                                     # giveitem TM24
    a = Asm(0)
    s = put(0x1C, bytes([0x31, 0x0F, 0x00, 0x09, 0, 0, 0x03, 0x0D, 0x4E, 0x14, 0x00, 0x90]))    # checkevent ; iftrue ; sjump ; setscene 0 ; end
    rom[0x1C * 0x4000 + s - 0x4000 + 4:0x1C * 0x4000 + s - 0x4000 + 6] = w16(s + 9)
    p = ce[0][0] + 4; rom[p:p + 2] = w16(s)
    log.append('2-3 Mania, Clair TM24 (1C:%04X)' % s)
    # 4. roof colors, group 3: morn/day 31,10,00 / 18,06,00 ; nite 18,05,09 / 17,08,07
    o = 0xB53E; expect(rom, o, 'b5 56 6b 2d b5 56 11 1d')
    def rgb(r_, g_, b_): return w16(r_ | g_ << 5 | b_ << 10)
    rom[o:o + 8] = rgb(31, 10, 0) + rgb(18, 6, 0) + rgb(18, 5, 9) + rgb(17, 8, 7)
    # 5. johto_modern block $5B
    o = 0xB67B0 + 0x5B * 16; expect(rom, o, '29 2a 29 2a 4b 48 4b 48 29 2a 55 57 4b 48 35 35')
    for k in (4, 6, 12): rom[o + k] = 0x47
    # 6. the ellipsis tile (1bpp, HPExpBarBorderGFX tile 2): row 4 -> row 6
    o = 0xF8AE0 + 16; expect(rom, o, '00 00 00 00 92 00 00 00'); rom[o + 4] = 0; rom[o + 6] = 0x92
    log.append('4-6 roof colors, Slowpoke Well tile, ellipsis')

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
