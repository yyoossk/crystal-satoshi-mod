#!/usr/bin/env python3
"""Phase 52: the Kanto rival's name is chosen by the player.
 * New game: Red's Oak speech (Red's lines, Nidorino) with the rival naming of Red (じぶんできめる / シゲル / グリーン /
   ジョン); no boy/girl question (Crystal's clock setting stays).  The name is kept in Crystal's saved wGreensName.
 * Every Kanto text that said シゲル now prints that name (text code <GREEN>), and the rival's battles (class 0x40:
   Kanto rival, Viridian gym leader) use it as the trainer name.
 * The Johto rival (Silver) keeps Crystal's wRivalName, named when the officer asks in Elm's lab.
usage: build_phase52.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from jpchar import encode
import redtexts as RT

CODE_BANK = 0x36
OAK_MUSIC = 0x2B
ASM = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'asm')
GREEN = 0x39                                   # text code: wGreensName
NAME_BANKS = (0x5D, 0x61, 0x62, 0x6F, 0x71, 0x72, 0x77, 0x78, 0x7A, 0x7B)   # Kanto texts naming the rival


def rgbds(tool):
    p = os.environ.get('RGBDS')
    if p: return os.path.join(p, tool)
    for d in (SC + '/ref/rgbds1', SC + '/sameboy-harness/deps/rgbds'):
        if os.path.exists(os.path.join(d, tool)): return os.path.join(d, tool)
    return tool


def red_text(s):
    """a JP Red text (from its {00}) up to and including its terminator"""
    k = encode(s).rstrip(b'\x50'); i = RT.R.find(b'\x00' + k)
    assert i >= 0, s
    e = i + 1
    while RT.R[e] not in (0x50, 0x57, 0x58): e += 1
    return bytes(RT.R[i:e + 1])


def db(b): return '\n'.join('\tdb ' + ','.join('$%02X' % x for x in b[i:i + 16]) for i in range(0, len(b), 16))


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    log = []

    # ---------- the rival's name in Kanto texts
    k = encode('シゲル').rstrip(b'\x50'); n = 0
    for b in NAME_BANKS:
        s = b * 0x4000
        for m in list(re.finditer(re.escape(k), bytes(rom[s:s + 0x4000]))):
            o = s + m.start()
            rom[o:o + 3] = bytes([GREEN, 0x50, 0x00])          # name, end of segment, new text segment
            n += 1
    log.append('Kanto texts: %d シゲル -> <GREEN>' % n)

    # default names: wGreensName "シゲル" (Crystal: グリーン); the player's default サトシ (Crystal: クリス)
    o = fo(0x01, 0x5D01); assert rom[o:o + 5] == encode('グりーン@')
    rom[o:o + 5] = encode('シゲル@@')
    o = fo(0x01, 0x625D); assert rom[o:o + 4] == encode('クリス@')
    rom[o:o + 4] = encode('サトシ@')

    # trainer name of class 0x40 (GetTrainerName in bank 7E, unused copy routine at 59AE)
    o = fo(0x7E, 0x598B); assert rom[o:o + 4] == bytes([0x0D, 0xC5, 0x06, 0x00])
    h = fo(0x7E, 0x59AE); assert rom[h:h + 3] == bytes([0x11, 0x5B, 0xD0])
    rom[o:o + 2] = bytes([0x18, (0x59AE - 0x598D) & 0xFF])
    hook = bytes([0x79, 0xFE, 0x40, 0x21, 0xA6, 0xD4, 0x28, 0, 0x0D, 0xC5, 0x18, 0])
    hook = bytearray(hook)
    hook[7] = (0x59A2 - (0x59AE + 8)) & 0xFF
    hook[11] = (0x598D - (0x59AE + 12)) & 0xFF
    rom[h:h + 12] = hook
    log.append('rival trainer name: class 0x40 -> wGreensName')

    # ---------- new game: no boy/girl question; Red's Oak speech
    o = fo(0x01, 0x5B7E); assert rom[o:o + 2] == bytes([0x3E, 0x41])
    rom[o:o + 5] = bytes([0xAF, 0xEA, 0x63, 0xD4, 0xC9])          # xor a / ld [wPlayerGender], a / ret

    t1 = red_text('はじめまして！')
    t2a = red_text('この　せかいには'); assert t2a[-1] == 0x50
    t2b = red_text('<PARA>その　<POKEMON>　という')
    t3 = red_text('では　はじめに')
    t4 = red_text('ふむ・・・')
    t5 = red_text('こいつは　わたしの　まご')
    t6 = red_text('そうだ　そうだ！').replace(b'\x53', bytes([GREEN]))
    t7 = red_text('<PLAYER>！<PARA>いよいよ')
    hdr = rom[fo(0x22, 0x42CA):fo(0x22, 0x42D3)]
    assert hdr[:5] == bytes([0x40, 0, 0, 0x0B, 0x0A])
    names = ['じぶんできめる', 'シゲル', 'グりーン', 'ジョン']
    o = fo(0x22, 0x42D3); assert rom[o] == 0x91
    tail = bytes(rom[o + 2:o + 64]); title = tail[tail.index(b'\x50\x02') + 1:]
    title = title[:title.index(0x50) + 1]
    menu = bytes([0x91, len(names)]) + b''.join(encode(x + '@') for x in names) + title
    inc = ['OakText1:', db(t1), 'OakText2:', db(t2a + b'\x08'), '\tjp OakText2Cry', 'OakText2b:', db(t2b),
           'OakText3:', db(t3), 'OakText4:', db(t4), 'OakText5:', db(t5), 'OakText6:', db(t6), 'OakText7:', db(t7),
           'RivalNameMenuHeader:', '\tdb $40, 0, 0, 9, 10', '\tdw RivalNameMenuData', '\tdb 1',
           'RivalNameMenuData:', db(menu), 'DefaultRivalName:', db(encode('シゲル@'))]
    f, free = bank_free_tail(rom, CODE_BANK)
    addr = f % 0x4000 + 0x4000 + 1
    with tempfile.TemporaryDirectory() as d:
        open(d + '/phase52_data.inc', 'w').write('\n'.join(inc) + '\n')
        open(d + '/in.gbc', 'wb').write(rom)
        subprocess.run([rgbds('rgbasm'), '-I', ASM, '-I', d, '-D', 'CODE_BANK=$%X' % CODE_BANK, '-D', 'CODE_ADDR=$%X' % addr,
                        '-D', 'OAK_MUSIC=$%X' % OAK_MUSIC, '-o', d + '/a.o', ASM + '/phase52.asm'], check=True)
        subprocess.run([rgbds('rgblink'), '-O', d + '/in.gbc', '-o', d + '/out.gbc', '-n', d + '/out.sym', d + '/a.o'],
                       check=True)
        new = open(d + '/out.gbc', 'rb').read()
        sym = {l.split()[1]: int(l.split()[0].split(':')[1], 16) for l in open(d + '/out.sym')
               if re.match(r'[0-9a-f]+:[0-9a-f]+ ', l)}
    assert len(new) == len(rom)
    used = sum(1 for i in range(len(rom)) if rom[i] != new[i])
    rom[:] = new
    sp = sym['RedOakSpeech']
    o = fo(0x01, 0x5F89); assert rom[o:o + 3] == bytes([0x3E, 0x24, 0x21])
    rom[o:o + 6] = bytes([0x3E, CODE_BANK, 0x21, sp & 0xFF, sp >> 8, 0xCF]); rom[o + 6] = 0xC9
    log.append("Red's Oak speech at %X:%04X (free before %d bytes)" % (CODE_BANK, addr, free))

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    print('\n'.join(log))


if __name__ == '__main__':
    main()
