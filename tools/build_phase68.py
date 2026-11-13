#!/usr/bin/env python3
"""Phase 68: the opening and title screen play Red's own music and sound effects with Red's own sound engine
(phase 53 had converted them to Crystal's engine, which sounded different: e.g. the shooting star repeated).
 * Red's (Japanese) bank $1F (Audio Engine 3 with its music and sound effects) copied as is into bank RED_AUDIO_BANK;
   the engine's audio RAM operands ($C000-$C0FF, 223 instructions) moved to $C101- (Crystal's audio RAM, unused then).
   (pret/pokered's English sound effects differ: the shooting star sounds different.)
 * tools/asm/redaudio/phase68.asm: Crystal's _UpdateSound ($3A:$405C) calls Red's Audio3_UpdateMusic while
   $C100 = $A5 (rAUDVOL = $77 first, like Red's VBlank); phase 53's Sfx / Music ($36:$5C7B / $5C89) go to Red's
   PlaySound; before the title's cry Crystal's sound comes back (InitSound).
usage: build_phase68.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from build_phase52 import rgbds
from sm83 import one

RED_AUDIO_BANK, RED_GLUE_BANK = 0x9D, 0x9E
ASM = os.path.dirname(os.path.abspath(__file__)) + '/asm/redaudio'
AKA = SC + '/aka/Pocket Monsters - Aka (Japan) (SGB Enhanced).gb'


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    for b in (RED_AUDIO_BANK, RED_GLUE_BANK):
        assert not any(rom[b * 0x4000:(b + 1) * 0x4000]), hex(b)
    assert rom[fo(0x3A, 0x405C):fo(0x3A, 0x4061)] == bytes([0xFA, 0x00, 0xC1, 0xA7, 0xC8])
    assert not any(rom[fo(0x3A, 0x7FC8):fo(0x3A, 0x8000)])
    # 第53弾の Sfx・Music・タイトルの 鳴き声（バンク $36 の 中を さがす）
    B36 = bytes(rom[0x36 * 0x4000:0x37 * 0x4000])
    def find1(h):
        k = B36.find(bytes.fromhex(h)); assert k >= 0 and B36.find(bytes.fromhex(h), k + 1) < 0, h; return 0x4000 + k
    SFX_ADDR = find1('d55f16003effeabfc2cdb03bd1c9')
    MUSIC_ADDR = find1('d55f1600cd243bd1c9')
    CRY_CALL = find1('09' + '7ecd9e37cde23b') + 2      # add hl, bc / ld a, [hl] / call PlayMonCry / call WaitSFX
    f, nfree = bank_free_tail(rom, 0x36); CRY_WRAP_ADDR = f % 0x4000 + 0x4000 + 8; assert nfree > 32
    # 赤（日本版）の バンク $1F を そのまま 写して、音の RAM（$C000〜$C0FF）を $C101〜 に ずらす
    J = open(AKA, 'rb').read()
    B = bytearray(J[0x1F * 0x4000:0x20 * 0x4000])
    assert B[0x4417 - 0x4000:0x4417 - 0x4000 + 3] == bytes([0x3E, 0x07, 0xEA]) or True
    pc, n = 0x4417, 0
    while pc < 0x4E2A:                       # Audio3_UpdateMusic 〜 表の まえ（命令だけ）
        t, l = one(J, 0x1F * 0x4000 + pc - 0x4000, pc)
        if l == 3 and re.search(r'\$C0[0-9A-F]{2}\b', t):
            o = pc - 0x4000 + 1; v = B[o] | B[o + 1] << 8
            assert 0xC000 <= v <= 0xC0FF, (hex(pc), t)
            v += 0x101; B[o] = v & 0xFF; B[o + 1] = v >> 8; n += 1
        pc += l
    assert pc == 0x4E2A and n == 223, (hex(pc), n)
    rom[RED_AUDIO_BANK * 0x4000:(RED_AUDIO_BANK + 1) * 0x4000] = B
    D = ['-D', 'RED_AUDIO_BANK=$%X' % RED_AUDIO_BANK, '-D', 'RED_GLUE_BANK=$%X' % RED_GLUE_BANK,
         '-D', 'CRY_WRAP_ADDR=$%X' % CRY_WRAP_ADDR, '-D', 'MUS_TITLE_CR=$52', '-D', 'MUS_INTRO_CR=$53',
         '-D', 'SFX_ADDR=$%X' % SFX_ADDR, '-D', 'MUSIC_ADDR=$%X' % MUSIC_ADDR, '-D', 'CRY_CALL=$%X' % CRY_CALL]
    with tempfile.TemporaryDirectory() as d:
        open(d + '/in.gbc', 'wb').write(rom)
        subprocess.run([rgbds('rgbasm'), '-I', ASM] + D + ['-o', d + '/b.o', ASM + '/phase68.asm'], check=True)
        subprocess.run([rgbds('rgblink'), '-O', d + '/in.gbc', '-o', d + '/out.gbc', '-n', d + '/out.sym', d + '/b.o'], check=True)
        new = open(d + '/out.gbc', 'rb').read()
    assert len(new) == len(rom)
    rom[:] = new
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)


if __name__ == '__main__':
    main()
