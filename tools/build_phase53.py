#!/usr/bin/env python3
"""Phase 53: Red's opening, ported from the Red full-color hack (akafc/akafc.gbc), colors as there:
 * copyright, the GAME FREAK shooting star, Gengar vs Nidorino (Red's sound effects and intro music);
 * Red's title screen: the logo slides in, Red with the Pokémon changing on the right, Red's title music;
   without "Red Version" and the 赤 emblem, the ポケットモンスター logo centered;
 * Red's Oak speech music (Routes 24/25) for phase 52's speech.
The music / sound effects are converted from Red's audio data; they take the places of Crystal's intro-only ones.
usage: build_phase53.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import lz
from gen1audio import Song
from build_phase52 import rgbds, db, ASM

FC = SC + '/akafc/akafc.gbc'
CODE_BANK, MON_BANK, AUD_BANK = 0x36, 0x2C, 0x20
PKMN = PR + '/tools/pkmncompress'
MUSIC_TABLE, SFX_TABLE = 0x506E, 0x527C          # bank 3A
MUS_TITLE, MUS_INTRO, MUS_OAK = 0x52, 0x53, 0x62   # Crystal: GS opening x2 (unused), Crystal opening
SFX = {'SHOOTING_STAR': (0xBE, 0xC2), 'INTRO_LUNGE': (0xBF, 0xB8), 'INTRO_HIP': (0xC0, 0xB9), 'INTRO_HOP': (0xC1, 0xBA),
       'INTRO_RAISE': (0xC2, 0xBB), 'INTRO_CRASH': (0xC3, 0xBC), 'INTRO_WHOOSH': (0xC4, 0xBD)}   # Crystal id, Red id
RED_SFX_HEADERS = 0x6EBF                          # bank 1F
TITLE_DEX = [4, 7, 1, 13, 32, 123, 25, 35, 112, 63, 92, 132, 17, 95, 77, 129]
MONPAL = 0x81D72                                  # + 8 * dex
PAL = {'Grey': 0x804AD, 'GF': 0x81D72, 'Star4': 0x81CE2, 'Star5': 0x81D02, 'Star7': 0x81C62, 'Gengar': 0x81CF2,
       'Nidorino': 0x81E7A, 'Logo': 0x81CC2, 'Copyright': 0x81D42, 'Player': 0x823AA}
LOGO_ROW, LOGO_H = 2, 6


def fcb(b, a): return b * 0x4000 + a - 0x4000


def tiles_px(t):
    return [[((t[2 * y] >> (7 - x)) & 1) | (((t[2 * y + 1] >> (7 - x)) & 1) << 1) for x in range(8)] for y in range(8)]


def px_tile(p):
    out = bytearray()
    for y in range(8):
        lo = hi = 0
        for x in range(8):
            v = p[y][x]; lo |= (v & 1) << (7 - x); hi |= (v >> 1) << (7 - x)
        out += bytes([lo, hi])
    return bytes(out)


def title_logo(F):
    """the logo without the 赤 emblem, centered; POCKET MONSTERS below: (tiles, 20 x LOGO_H map)"""
    T = F[0x10419:0x10419 + 85 * 16]
    def px(r, x, y): return tiles_px(T[(r * 17 + x // 8) * 16:(r * 17 + x // 8) * 16 + 16])[y][x % 8]
    W, H = 160, LOGO_H * 8
    can = [[0] * W for _ in range(H)]
    for y in range(32):
        for x in range(136):
            if (y <= 20 and x >= 116) or (y >= 21 and x >= 110) or (x, y) == (115, 20): continue
            can[y][22 + x] = px(y // 8, x, y % 8)
    for y in range(8):
        for x in range(136):
            can[40 + y][16 + x] = px(4, x, y)
    tiles = []; idx = {}; m = []
    for r in range(LOGO_H):
        for c in range(20):
            p = [row[c * 8:c * 8 + 8] for row in can[r * 8:r * 8 + 8]]
            if not any(any(row) for row in p): m.append(0x7F); continue
            t = px_tile(p)
            if t not in idx: idx[t] = 0x80 + len(tiles); tiles.append(t)
            m.append(idx[t])
    assert len(tiles) <= 0x80
    return b''.join(tiles), bytes(m)


def title_mon(F, dex):
    """Red full-color front pic as 7x7 tiles, column by column (Red's alignment)"""
    e = 0x38000 + (dex - 1) * 28
    dims = F[e + 10]; ptr = F[e + 11] | F[e + 12] << 8; bank = F[e + 27]
    w, h = dims >> 4, dims & 15
    with tempfile.TemporaryDirectory() as d:
        open(d + '/a.pic', 'wb').write(F[fcb(bank, ptr):fcb(bank, ptr) + 2000])
        subprocess.run([PKMN, '-u', d + '/a.pic', d + '/a.2bpp'], check=True)
        t = open(d + '/a.2bpp', 'rb').read()
    assert len(t) == w * h * 16
    out = bytearray(49 * 16)
    ox, oy = (8 - w) // 2, 7 - h
    for i in range(w * h):
        cx, cy = i % w, i // w
        j = (ox + cx) * 7 + (oy + cy)
        out[j * 16:j * 16 + 16] = t[i * 16:i * 16 + 16]
    return bytes(out)


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    F = open(FC, 'rb').read()
    log = []
    def free(b):
        f, n = bank_free_tail(rom, b); return f % 0x4000 + 0x4000 + 1, n - 1

    # ---------- audio (Red bank 1F / 02 -> AUD_BANK)
    aaddr, afree = free(AUD_BANK)
    songs = [('title', MUS_TITLE, Song(F, 0x1F, RED_SFX_HEADERS + 3 * 0xC3, {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}, 0)),
             ('intro', MUS_INTRO, Song(F, 0x1F, RED_SFX_HEADERS + 3 * 0xDC, {17: 2, 18: 3, 19: 4}, 2)),
             ('oak', MUS_OAK, Song(F, 0x02, 0x71FB, {3: 3}, 0))]
    sfx = [(n, cid, Song(F, 0x1F, RED_SFX_HEADERS + 3 * rid)) for n, (cid, rid) in SFX.items()]
    blob = bytearray(); ptrs = []
    for n, cid, s in [(a, b, c) for a, b, c in songs] + sfx:
        h, d_ = s.build(aaddr + len(blob)); blob += d_
        ptrs.append((n, cid, h))
    assert len(blob) <= afree, (len(blob), afree)
    rom[fcb(AUD_BANK, aaddr):fcb(AUD_BANK, aaddr) + len(blob)] = blob
    for n, cid, h in ptrs:
        t = MUSIC_TABLE if n in ('title', 'intro', 'oak') else SFX_TABLE
        o = fcb(0x3A, t) + 3 * cid
        rom[o:o + 3] = bytes([AUD_BANK, h & 0xFF, h >> 8])
    log.append('audio: %d bytes at %X:%04X (title, intro, Oak speech, %d sound effects)' % (len(blob), AUD_BANK, aaddr, len(sfx)))

    # Oak speech (phase 52): Red's music
    s36 = fcb(CODE_BANK, 0x4000)
    i = bytes(rom[s36:s36 + 0x4000]).find(bytes([0x11, 0x2B, 0x00, 0xCD, 0x24, 0x3B]))
    assert i >= 0
    rom[s36 + i + 1] = MUS_OAK

    # ---------- graphics and data
    logo, logomap = title_logo(F)
    G = {'GfxCopyright': lz(F[fcb(0x04, 0x4FB1):fcb(0x04, 0x4FB1) + 0x190]),
         'GfxGengar': lz(F[fcb(0x10, 0x4A4D):fcb(0x10, 0x4A4D) + 0x600]),
         'GfxGFIntro': lz(F[fcb(0x10, 0x490D):fcb(0x10, 0x490D) + 0x140]),
         'GfxNidorino': lz(F[fcb(0x10, 0x504D):fcb(0x10, 0x504D) + 0x6C0]),
         'GfxLogo': lz(logo),
         'GfxPlayer': lz(F[fcb(0x04, 0x5561):fcb(0x04, 0x5561) + 0x230])}
    stars = F[fcb(0x1E, 0x4586):fcb(0x1E, 0x4586) + 16] + F[fcb(0x1E, 0x4686):fcb(0x1E, 0x4686) + 16] + \
        F[fcb(0x1C, 0x46B5):fcb(0x1C, 0x46B5) + 16]
    inc = []
    for k, v in (('MUS_TITLE', MUS_TITLE), ('MUS_INTRO', MUS_INTRO), ('MON_BANK', MON_BANK), ('LOGO_ROW', LOGO_ROW),
                 ('LOGO_COL', 0), ('LOGO_W', 20), ('LOGO_H', LOGO_H)):
        inc.append('DEF %s EQU $%X' % (k, v))
    for n, (cid, rid) in SFX.items(): inc.append('DEF SFX_%s EQU $%X' % (n, cid))
    for k, a in PAL.items(): inc += ['Pal%s:' % k, db(F[a:a + 8])]
    # copyright screen: rows 7, 9, 11 from column 5 (Red's string)
    cs = [[0x60, 0x61, 0x62, 0x63, 0x6D, 0x6E, 0x6F, 0x70, 0x71, 0x72],
          [0x60, 0x61, 0x62, 0x63, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78, 0x6B, 0x6C],
          [0x60, 0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6A, 0x6B, 0x6C]]
    src = F[fcb(0x01, 0x4844):fcb(0x01, 0x4844) + 38]
    assert bytes(src[:10]) == bytes(cs[0]), src.hex()
    cl = bytearray()
    for r, row in zip((7, 9, 11), cs):
        a = 0x9800 + r * 32 + 5; cl += bytes([a & 0xFF, a >> 8]) + bytes(row) + b'\0'
    inc += ['CopyrightLayout:', db(bytes(cl) + b'\0')]
    for k, v in G.items(): inc += [k + ':', db(v)]
    inc += ['GfxStars:', db(stars)]
    inc += ['GFLogoOAM:', db(F[0x70665:0x70665 + 64]), 'BigStarOAM:', db(F[0x706A5:0x706A5 + 16]),
            'SmallStarOAM:', db(F[0x70613:0x70617])]
    wp = [F[0x70617 + 2 * i] | F[0x70618 + 2 * i] << 8 for i in range(6)]
    base = 0x4623; wdata = F[fcb(0x1C, base):fcb(0x1C, 0x4644) + 1]
    assert wp[0] == base and wp[4] == wp[5] == 0x4643
    inc += ['SmallStarWaves:', '\tdw ' + ', '.join('SmallStarData + %d' % (p - base) for p in wp), 'SmallStarData:', db(wdata)]
    gm = F[0x79C08:0x79C08 + 147]
    inc += ['GengarTilemap1:', db(gm[:49]), 'GengarTilemap2:', db(gm[49:98]), 'GengarTilemap3:', db(gm[98:])]
    an = F[0x408C4:0x4090D]
    offs = [0]
    for j, x in enumerate(an[:-1]):
        pass
    # 7 animations, each ends with $50 (pairs of bytes)
    k = 0; labs = []
    while k < len(an):
        labs.append(k); k2 = k
        while an[k2] != 0x50: k2 += 2
        k = k2 + 1
    assert len(labs) == 7, labs
    for j, o in enumerate(labs):
        e_ = labs[j + 1] if j + 1 < len(labs) else len(an)
        inc += ['NidoAnim%d:' % (j + 1), db(an[o:e_])]
    inc += ['TitleLogoMap:', db(logomap), 'TitleMons:', db(bytes(TITLE_DEX)),
            'TitleMonPals:', db(b''.join(F[MONPAL + 8 * d:MONPAL + 8 * d + 8] for d in TITLE_DEX)),
            'TitleMonPics:', '\tdw ' + ', '.join('TitleMonPic%d' % i for i in range(16))]
    maddr, mfree = free(MON_BANK)
    inc.append('SECTION "Phase53Mons", ROMX[$%X], BANK[$%X]' % (maddr, MON_BANK))
    msize = 0
    for i, d in enumerate(TITLE_DEX):
        p = lz(title_mon(F, d)); msize += len(p)
        inc += ['TitleMonPic%d:' % i, db(p)]
    assert msize <= mfree, (msize, mfree)
    caddr, cfree = free(CODE_BANK)
    with tempfile.TemporaryDirectory() as d:
        open(d + '/phase53_data.inc', 'w').write('\n'.join(inc) + '\n')
        open(d + '/in.gbc', 'wb').write(rom)
        subprocess.run([rgbds('rgbasm'), '-I', ASM, '-I', d, '-D', 'CODE_BANK=$%X' % CODE_BANK,
                        '-D', 'CODE_ADDR=$%X' % caddr, '-o', d + '/a.o', ASM + '/phase53.asm'], check=True)
        subprocess.run([rgbds('rgblink'), '-O', d + '/in.gbc', '-o', d + '/out.gbc', '-n', d + '/out.sym', d + '/a.o'],
                       check=True)
        new = open(d + '/out.gbc', 'rb').read()
        sym = {l.split()[1]: int(l.split()[0].split(':')[1], 16) for l in open(d + '/out.sym')
               if re.match(r'[0-9a-f]+:[0-9a-f]+ ', l)}
    assert len(new) == len(rom)
    rom[:] = new
    used = max(v for k, v in sym.items() if not k.startswith('TitleMonPic')) - caddr
    log.append('opening code + graphics at %X:%04X (~%d of %d bytes), title Pokémon %X:%04X (%d bytes)'
               % (CODE_BANK, caddr, used, cfree, MON_BANK, maddr, msize))

    # IntroSequence (01:6385): Red's opening instead of Crystal's splash / intro / title
    o = fcb(0x01, 0x6385); assert rom[o:o + 3] == bytes([0x21, 0x3A, 0x49])
    ro = sym['RedOpening']
    code = bytes([0xF0, 0x70, 0xF5, 0x3E, 0x05, 0xE0, 0x70,            # push WRAM bank, WRAM 5
                  0x3E, CODE_BANK, 0x21, ro & 0xFF, ro >> 8, 0xCF,       # farcall RedOpening
                  0xC3, 0xA5, 0x63])                                     # jp (after Crystal's title loop)
    rom[o:o + len(code)] = code
    log.append('IntroSequence -> %X:%04X' % (CODE_BANK, ro))

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    print('\n'.join(log))


if __name__ == '__main__':
    main()
