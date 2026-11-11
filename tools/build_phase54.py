#!/usr/bin/env python3
"""Phase 54:
 * The Kanto Hall of Fame and staff roll as in Red (layout, texts, colors and music from the Red full-color hack):
   each Pokémon's back picture passes by, its front picture slides in, name / level / types and
   「でんどう いり おめでとう！」; then the player with play time, money and Prof. Oak's Pokédex rating (Red's);
   Red's staff roll (pages, black Pokémon passing by, THE END).  Crystal's saving / Hall of Fame record stay.
   The Johto Hall of Fame stays Crystal's.
 * The trainer's lines after a battle (winlosstext) are read from the bank of the script that set them
   (Crystal: always the map's script bank, so lines of scripts in other banks were garbage).
 * Saves from before phase 52 (rival's name Crystal's default グリーン): the rival is シゲル when continuing.
Extended event flag 0x9F6 (index 502): the rival was named (set in phase 52's Oak speech).
usage: build_phase54.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import lz
from gen1audio import Song
from jpchar import encode
from build_phase52 import rgbds, db, ASM

FC = SC + '/akafc/akafc.gbc'
CODE_BANK, AUD_BANK = 0x35, 0x20
MUSIC_TABLE = 0x506E
MUS_HOF, MUS_CREDITS = 0x5E, 0x5F                 # Crystal: mobile adapter menu / mobile adapter (unused)
RED_HEADERS = 0x6EBF                              # Red bank 1F
WINLOSS_BANK = 0xDA5C                             # end of the extended flags' WRAM (unused)
CREDIT_DEX = [3, 24, 111, 22, 63, 75, 106, 114, 121, 130, 132, 139, 45, 34, 47]


def fcb(b, a): return b * 0x4000 + a - 0x4000


def until(F, o, term):
    e = o
    while F[e] not in term: e += 1
    return bytes(F[o:e + 1])


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    F = open(FC, 'rb').read()
    log = []
    def free(b):
        f, n = bank_free_tail(rom, b); return f % 0x4000 + 0x4000 + 1, n - 1

    # ---------- music: Red's Hall of Fame and staff roll
    aaddr, afree = free(AUD_BANK); blob = bytearray()
    for cid, rid in ((MUS_HOF, 0xCA), (MUS_CREDITS, 0xC7)):
        h, d = Song(F, 0x1F, RED_HEADERS + 3 * rid).build(aaddr + len(blob)); blob += d
        o = fcb(0x3A, MUSIC_TABLE) + 3 * cid; rom[o:o + 3] = bytes([AUD_BANK, h & 0xFF, h >> 8])
    assert len(blob) <= afree
    rom[fcb(AUD_BANK, aaddr):fcb(AUD_BANK, aaddr) + len(blob)] = blob
    log.append('music: Hall of Fame / staff roll, %d bytes at %X:%04X' % (len(blob), AUD_BANK, aaddr))

    # ---------- data
    inc = ['DEF MUS_HALL_OF_FAME EQU $%X' % MUS_HOF, 'DEF MUS_CREDITS EQU $%X' % MUS_CREDITS, 'DEF NUM_CRED_PAGES EQU 26']
    inc += ['MonPals:', db(F[0x81D72:0x81D72 + 152 * 8]), 'PalPlayer:', db(F[0x823AA:0x823B2])]
    inc += ['HoFText:', db(until(F, fcb(0x1C, 0x4790), (0x50,))),
            'HoFMonInfoText:', db(until(F, fcb(0x1C, 0x4850), (0x50,))),
            'HoFPlayTimeText:', db(until(F, fcb(0x1C, 0x4910), (0x50,))),
            'HoFMoneyText:', db(until(F, fcb(0x1C, 0x4917), (0x50,)))]
    t = bytearray(F[fcb(0x1C, 0x4922):fcb(0x1C, 0x4949)])
    assert t[-1] == 0x50 and t.count(bytes([0x09, 0x5B, 0xCC])) == 1 and t.count(bytes([0x09, 0x5C, 0xCC])) == 1
    t = t.replace(bytes([0x09, 0x5B, 0xCC]), bytes([0x09, 0x03, 0xCB])).replace(bytes([0x09, 0x5C, 0xCC]), bytes([0x09, 0x04, 0xCB]))
    inc += ['DexSeenOwnedText:', db(bytes(t)), 'DexRatingText:', db(until(F, fcb(0x1C, 0x4949), (0x57,)))]
    rt = ['DexRatings:']; rtx = []
    for i in range(16):
        o = 0x44339 + 3 * i; p = F[o + 1] | F[o + 2] << 8
        rt.append('\tdb %d\n\tdw DexRating%d' % (F[o], i)); rtx += ['DexRating%d:' % i, db(until(F, fcb(0x11, p), (0x57,)))]
    inc += rt + rtx
    # Crystal's type names
    tn = ['TypeNames:']; tns = []
    for i in range(28):
        o = fcb(0x14, 0x4A6B) + 2 * i; p = rom[o] | rom[o + 1] << 8
        tn.append('\tdw TypeName%d' % i); tns += ['TypeName%d:' % i, db(until(rom, fcb(0x14, p), (0x50,)))]
    inc += tn + tns
    # staff roll
    B = 0x1C
    pages = [F[fcb(B, 0x41F2) + 2 * i] | F[fcb(B, 0x41F2) + 2 * i + 1] << 8 for i in range(26)]
    inc.append('CreditsPages:\n\tdw ' + ', '.join('CreditsPage%d' % i for i in range(26)))
    nt = 0
    for i, p in enumerate(pages):
        o = fcb(B, p); seq = bytearray()
        while True:
            c = F[o]; o += 1; seq.append(c)
            if c >= 0xFA and c != 0xFB: break
        nt = max([nt] + [x + 1 for x in seq if x < 0xFA])
        inc += ['CreditsPage%d:' % i, db(bytes(seq))]
    inc.append('CreditsTexts:\n\tdw ' + ', '.join('CreditsText%d' % i for i in range(nt)))
    for i in range(nt):
        q = F[fcb(B, 0x4280) + 2 * i] | F[fcb(B, 0x4280) + 2 * i + 1] << 8
        inc += ['CreditsText%d:' % i, db(until(F, fcb(B, q), (0x50,)))]
    inc += ['CreditsXOffsets:', db(F[fcb(B, 0x445A):fcb(B, 0x445A) + nt]), 'CreditsMons:', db(bytes(CREDIT_DEX))]
    inc += ['GfxTheEnd:', db(F[fcb(B, 0x4485):fcb(B, 0x4485) + 160]),
            'TheEnd1:', db(until(F, fcb(B, 0x41D8), (0x50,))), 'TheEnd2:', db(until(F, fcb(B, 0x41E5), (0x50,)))]
    inc += ['GfxCopyright:', db(lz(F[fcb(0x04, 0x4FB1):fcb(0x04, 0x4FB1) + 0x190]))]
    cs = [[0x60, 0x61, 0x62, 0x63, 0x6D, 0x6E, 0x6F, 0x70, 0x71, 0x72],
          [0x60, 0x61, 0x62, 0x63, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78, 0x6B, 0x6C],
          [0x60, 0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6A, 0x6B, 0x6C]]
    cl = bytearray()
    for r, row in zip((7, 9, 11), cs):
        a = 0xC4A0 + r * 20 + 5; cl += bytes([a & 0xFF, a >> 8]) + bytes(row) + b'\0'
    inc += ['CopyrightLines:', db(bytes(cl) + b'\0'), 'DefaultRival:', db(encode('シゲル@@@'))]

    caddr, cfree = free(CODE_BANK)
    with tempfile.TemporaryDirectory() as d:
        open(d + '/phase54_data.inc', 'w').write('\n'.join(inc) + '\n')
        open(d + '/in.gbc', 'wb').write(rom)
        subprocess.run([rgbds('rgbasm'), '-I', ASM, '-I', d, '-D', 'CODE_BANK=$%X' % CODE_BANK,
                        '-D', 'CODE_ADDR=$%X' % caddr, '-o', d + '/a.o', ASM + '/phase54.asm'], check=True)
        subprocess.run([rgbds('rgblink'), '-O', d + '/in.gbc', '-o', d + '/out.gbc', '-n', d + '/out.sym', d + '/a.o'],
                       check=True)
        new = open(d + '/out.gbc', 'rb').read()
        sym = {l.split()[1]: int(l.split()[0].split(':')[1], 16) for l in open(d + '/out.sym')
               if re.match(r'[0-9a-f]+:[0-9a-f]+ ', l)}
    rom[:] = new
    end = max(sym.values())
    log.append('Hall of Fame / staff roll at %X:%04X (~%d of %d bytes)' % (CODE_BANK, caddr, end - caddr, cfree))

    # Crystal's HallOfFame (21:661B): call AnimateHallOfFame / pop af / ld b,a / farcall Credits / ret
    o = fcb(0x21, 0x661B); assert rom[o:o + 12] == bytes.fromhex('cd9566f1473e4221bf58cfc9')
    h = sym['HallOfFameAnimAndCredits']
    rom[o:o + 12] = bytes([0xF1, 0x47, 0x3E, CODE_BANK, 0x21, h & 0xFF, h >> 8, 0xCF, 0xC9, 0, 0, 0])
    # Continue (01:5D4E): farcall TryLoadSaveFile -> ContinueLoad
    o = fcb(0x01, 0x5D4E); assert rom[o:o + 6] == bytes.fromhex('3e0521874ecf')
    h = sym['ContinueLoad']
    rom[o:o + 6] = bytes([0x3E, CODE_BANK, 0x21, h & 0xFF, h >> 8, 0xCF])

    # winlosstext: remember the script's bank (Script_winlosstext 25:714A), PrintWinLossText (00:36E8) uses it once
    o = fcb(0x25, 0x714A); assert rom[o:o + 3] == bytes([0x21, 0x3D, 0xD0])
    f, n = bank_free_tail(rom, 0x25); ha = f % 0x4000 + 0x4000 + 1
    hk = bytes([0xFA, 0x2A, 0xD4, 0xEA, WINLOSS_BANK & 0xFF, WINLOSS_BANK >> 8, 0x21, 0x3D, 0xD0, 0xC9])
    rom[fcb(0x25, ha):fcb(0x25, ha) + len(hk)] = hk
    rom[o:o + 3] = bytes([0xCD, ha & 0xFF, ha >> 8])
    o = 0x36E8; assert rom[o:o + 3] == bytes([0xFA, 0x61, 0xD2]) and rom[0x3704:0x3707] == bytes([0xCD, 0x29, 0x2C])
    code = bytes([0xFA, 0xAE, 0xD0, 0x21, 0x3D, 0xD0, 0xE6, 0x0F, 0x28, 0x03, 0x21, 0x3F, 0xD0,   # win / loss text pointer
                  0x2A, 0x66, 0x6F,
                  0xFA, WINLOSS_BANK & 0xFF, WINLOSS_BANK >> 8, 0xA7, 0x20, 0x03,           # the script's bank, if set
                  0xCD, 0x29, 0x2C,                                                         # else the map's
                  0xF5, 0xAF, 0xEA, WINLOSS_BANK & 0xFF, WINLOSS_BANK >> 8, 0xF1])
    assert len(code) == 0x3707 - 0x36E8
    rom[0x36E8:0x3707] = code
    log.append('winlosstext: the script\'s bank (25:%04X)' % ha)

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    print('\n'.join(log))


if __name__ == '__main__':
    main()
