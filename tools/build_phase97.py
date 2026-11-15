#!/usr/bin/env python3
"""Phase 97: Kanto's towns and routes change with the time of day (morning / day / night) as Crystal's do.
The Kanto map palettes come from the MOD's table-driven palette routine (6A:6EE9, phase 44's palhooks): one palette
set per tileset (Crystal's day colours), the same at every time (darkness only for Rock Tunnel).  For the outdoor
tilesets (towns / routes) there now are a morning and a night set too, made like Crystal's bg_tiles.pal:
  morning: the light colour (27,31,27) becomes Crystal's morning (28,31,16);
  night: palettes 0-2 and 4-6 (gray, red, green, yellow, brown, roof) are Crystal's night palettes where the colour is
  Crystal's day colour, other colours (the Kanto water palette 3, ...) by a fit of Crystal's day -> night colours.
Wrapper (called by phase 92's hook in place of 6A:6EE9): after the day set was loaded for a town or route, morning /
night copy their set over BG palettes 0-6 (palette 6's colours 1-2 are then Crystal's roof colours, as before;
palette 7 = phase 92).
usage: build_phase97.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from build_phase17 import US

PB = 0x6A
ROUTINE, TABLE = 0x6EE9, 0x6F2B    # palette routine / (tileset, pointer) table, $FF end
P92_CALL = 0x74AF                  # phase 92's wrapper: call $6EE9 / ret nc / ...
W_TILESET, W_ENVIRONMENT, W_TIMEOFDAYPAL = 0xD1CA, 0xD1CB, 0xD834
FARCOPYWRAM = 0x3037

DAY = [[(27, 31, 27), (21, 21, 21), (13, 13, 13), (7, 7, 7)], [(27, 31, 27), (31, 19, 24), (30, 10, 6), (7, 7, 7)],
       [(22, 31, 10), (12, 25, 1), (5, 14, 0), (7, 7, 7)], [(31, 31, 31), (8, 12, 31), (1, 4, 31), (7, 7, 7)],
       [(27, 31, 27), (31, 31, 7), (31, 16, 1), (7, 7, 7)], [(27, 31, 27), (24, 18, 7), (20, 15, 3), (7, 7, 7)],
       [(27, 31, 27), (15, 31, 31), (5, 17, 31), (7, 7, 7)]]
NITE = [[(15, 14, 24), (11, 11, 19), (7, 7, 12), (0, 0, 0)], [(15, 14, 24), (14, 7, 17), (13, 0, 8), (0, 0, 0)],
        [(15, 14, 24), (8, 13, 19), (0, 11, 13), (0, 0, 0)], [(15, 14, 24), (5, 5, 17), (3, 3, 10), (0, 0, 0)],
        [(30, 30, 11), (16, 14, 18), (16, 14, 10), (0, 0, 0)], [(15, 14, 24), (12, 9, 15), (8, 4, 5), (0, 0, 0)],
        [(15, 14, 24), (13, 12, 23), (11, 9, 20), (0, 0, 0)]]
FIT = ((0.32, 0.209, 0.102, -1.722), (-0.146, 0.567, -0.021, 0.541), (-0.086, 0.679, 0.192, 1.121))


def unpack(c): return (c & 31, (c >> 5) & 31, c >> 10)
def pack(t): return t[0] | t[1] << 5 | t[2] << 10


def night(pi, ci, col):
    if col == (7, 7, 7) and ci == 3: return (0, 0, 0)
    if pi < 7 and DAY[pi][ci] == col: return NITE[pi][ci]
    if ci == 0 and col == (27, 31, 27): return (15, 14, 24)
    return tuple(max(0, min(31, round(a * col[0] + b * col[1] + c * col[2] + d))) for a, b, c, d in FIT)


def morning(pi, ci, col):
    return (28, 31, 16) if col == (27, 31, 27) else col


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read()); log = []
    o = fo(PB, P92_CALL); assert rom[o:o + 4] == bytes([0xCD, ROUTINE & 0xFF, ROUTINE >> 8, 0xD0])
    # outdoor tilesets
    u = US.get(); G = u.groups(); out = set()
    for gi in range(len(G) - 1):
        for k in range((G[gi + 1] - G[gi]) // 9):
            h = G[gi] + 9 * k
            if rom[h + 2] in (1, 2): out.add(rom[h + 1])
    t = fo(PB, TABLE); ents = []
    while rom[t] != 0xFF:
        ents.append((rom[t], rom[t + 1] | rom[t + 2] << 8)); t += 3
    ents = [(i, p) for i, p in ents if i in out]
    assert ents
    f, n = bank_free_tail(rom, PB); f += 16
    base = 0x4000 + f % 0x4000
    sp = [base + 0x60]                       # data after the code
    data = b''; tab = b''
    for i, p in ents:
        q = fo(PB, p); cols = [unpack(rom[q + 2 * j] | rom[q + 2 * j + 1] << 8) for j in range(28)]
        sets = []
        for fn in (morning, night):
            sets.append(b''.join(pack(fn(j // 4, j % 4, c)).to_bytes(2, 'little') for j, c in enumerate(cols)))
        am = sp[0] + len(data); data += sets[0]; an = sp[0] + len(data); data += sets[1]
        tab += bytes([i, am & 0xFF, am >> 8, an & 0xFF, an >> 8])
        log.append('tileset %02X: morning %04X, night %04X' % (i, am, an))
    tab += b'\xff'
    tabaddr = sp[0] + len(data); data += tab
    def w(v): return bytes([v & 0xFF, v >> 8])
    a = Asm(base)
    a.raw(b'\xcd' + w(ROUTINE) + b'\xd0')                     # call routine / ret nc
    a.raw(b'\xfa' + w(W_ENVIRONMENT) + b'\x3d\xfe\x02')         # ld a,[wEnvironment] / dec a / cp 2
    code = bytearray(a.done())
    # hand-assembled rest (relative jumps)
    rest = bytearray()
    rest += b'\x30\x00'                                         # jr nc,.ok  (patched)
    j_nc1 = len(code) + len(rest) - 1
    rest += b'\xfa' + w(W_TIMEOFDAYPAL) + b'\xe6\x03'          # ld a,[wTimeOfDayPal] / and 3
    rest += b'\x1e\x01\xa7\x28\x00'                             # ld e,1 / and a / jr z,.look (patched)
    j_z = len(code) + len(rest) - 1
    rest += b'\x1e\x03\xfe\x02\x20\x00'                         # ld e,3 / cp 2 / jr nz,.ok (patched)
    j_nz = len(code) + len(rest) - 1
    look = len(code) + len(rest)
    rest += b'\xfa' + w(W_TILESET) + b'\x47\x21' + w(tabaddr)  # ld a,[wTileset] / ld b,a / ld hl,tab
    loop = len(code) + len(rest)
    rest += b'\x7e\xfe\xff\x28\x00'                             # ld a,[hl] / cp $ff / jr z,.ok (patched)
    j_z2 = len(code) + len(rest) - 1
    rest += b'\xb8\x28\x07\x23\x23\x23\x23\x23\x18\x00'        # cp b / jr z,.found / inc hl x5 / jr .loop (patched)
    j_loop = len(code) + len(rest) - 1
    rest += b'\x16\x00\x19\x2a\x66\x6f'                         # .found: ld d,0 / add hl,de / ld a,[hli] / ld h,[hl] / ld l,a
    rest += b'\x3e\x05\x11\x00\xd0\x01\x38\x00\xcd' + w(FARCOPYWRAM)   # copy 56 bytes to wBGPals1
    ok = len(code) + len(rest)
    rest += b'\x37\xc9'                                         # .ok: scf / ret
    code += rest
    def rel(at, to): code[at] = (to - (at + 1)) & 0xFF
    rel(j_nc1, ok); rel(j_z, look); rel(j_nz, ok); rel(j_z2, ok); rel(j_loop, loop)
    assert len(code) <= 0x60 and 0x60 + len(data) + 16 < n, (len(code), len(data), n)
    rom[f:f + len(code)] = code
    rom[f + 0x60:f + 0x60 + len(data)] = data
    rom[o + 1:o + 3] = w(base)
    log.append('routine %02X:%04X (phase 92 wrapper calls it)' % (PB, base))
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
