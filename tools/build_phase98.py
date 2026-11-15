#!/usr/bin/env python3
"""Phase 98: Shigeru's own music, as in Red: 「ライバルあらわる」 (Music_MeetRival) when he appears and when he leaves
(Red's alternate starts / tempo), with Red's own sound engine (Audio Engine 1) instead of Crystal's rival music.
 * Red's (Japanese) bank 2 (Audio Engine 1 with its music) copied into bank RED_AUDIO1_BANK; the engine's audio RAM
   operands ($C000-$C0FF) moved to $C101- like phase 68's bank $1F.
 * tools/asm/redaudio/phase98.asm: scripts' playmusic $F0-$F3 start it ($F0 from the beginning, $F1 alternate start
   (after a battle / leaving), $F2 alternate tempo (Route 22's second battle), $F3 both); while $C100 = $A6 Red's
   Audio1_UpdateMusic runs; any Crystal music (map, battle) first resets Crystal's sound (_PlayMusic hook).
 * Shigeru's scenes: Oak's lab, Route 22 (both battles), Cerulean City, the S.S. Anne, Oak's lab's Pokédex scene,
   Pokémon Tower, Silph Co. (Red's playmusic places).
usage: build_phase98.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from build_phase52 import rgbds
from sm83 import one

RED_AUDIO_BANK, RED_GLUE_BANK, RED_AUDIO1_BANK = 0x9D, 0x9E, 0x9F
ASM = os.path.dirname(os.path.abspath(__file__)) + '/asm/redaudio'
AKA = SC + '/aka/Pocket Monsters - Aka (Japan) (SGB Enhanced).gb'
ENGINE_END = 0x4A13
MUS_RIVAL, MUS_RIVAL_AFTER = 0x1F, 0x20
# (bank, address of "playmusic", new id): the MOD's Shigeru scenes
SCENES = {0x62: None, 0x72: None, 0x61: None, 0x6F: None}


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read()); log = []
    assert not any(rom[RED_AUDIO1_BANK * 0x4000:(RED_AUDIO1_BANK + 1) * 0x4000])
    assert rom[fo(0x3A, 0x4B30):fo(0x3A, 0x4B33)] == bytes([0xCD, 0x57, 0x40])
    assert rom[fo(0x3A, 0x7FC8):fo(0x3A, 0x7FCD)] == bytes([0xFA, 0x00, 0xC1, 0xFE, 0xA5])
    assert not any(rom[fo(RED_GLUE_BANK, 0x4100):fo(RED_GLUE_BANK, 0x4200)])
    J = open(AKA, 'rb').read()
    B = bytearray(J[2 * 0x4000:3 * 0x4000])
    assert B[0x71C8 - 0x4000:0x71C8 - 0x4000 + 9] == bytes.fromhex('80 1d 60 01 b8 60 02 30 61')   # MUSIC_MEET_RIVAL ($DE)
    pc, n = 0x4000, 0
    while pc < ENGINE_END:
        t, l = one(J, 2 * 0x4000 + pc - 0x4000, pc)
        if l == 3 and re.search(r'\$C0[0-9A-F]{2}\b', t):
            o = pc - 0x4000 + 1; v = B[o] | B[o + 1] << 8
            assert 0xC000 <= v <= 0xC0FF, (hex(pc), t)
            v += 0x101; B[o] = v & 0xFF; B[o + 1] = v >> 8; n += 1
        pc += l
    assert pc == ENGINE_END and n == 223, (hex(pc), n)
    rom[RED_AUDIO1_BANK * 0x4000:(RED_AUDIO1_BANK + 1) * 0x4000] = B
    D = ['-D', 'RED_AUDIO_BANK=$%X' % RED_AUDIO_BANK, '-D', 'RED_GLUE_BANK=$%X' % RED_GLUE_BANK,
         '-D', 'RED_AUDIO1_BANK=$%X' % RED_AUDIO1_BANK]
    with tempfile.TemporaryDirectory() as d:
        open(d + '/in.gbc', 'wb').write(rom)
        subprocess.run([rgbds('rgbasm'), '-I', ASM] + D + ['-o', d + '/b.o', ASM + '/phase98.asm'], check=True)
        subprocess.run([rgbds('rgblink'), '-O', d + '/in.gbc', '-o', d + '/out.gbc', '-n', d + '/out.sym', d + '/b.o'], check=True)
        new = open(d + '/out.gbc', 'rb').read(); sym = open(d + '/out.sym').read()
    assert len(new) == len(rom)
    rom[:] = new
    print([l for l in sym.splitlines() if 'Hook' in l or 'Rival' in l or 'Red' in l])
    # ---- scripts: playmusic $1F / $20 in the MOD's Shigeru scenes -> $F0-$F3
    def pm(bank):
        s = rom[bank * 0x4000:(bank + 1) * 0x4000]; out = []
        for m in re.finditer(rb'\x7e([\x1f\x20])\x00', s):
            i = bank * 0x4000 + m.start()
            if orig[i:i + 3] == bytes(m.group(0)) if i < len(orig) else False: continue
            out.append((0x4000 + m.start(), m.group(1)[0]))
        return out
    plan = {}
    for a, v in pm(0x62): plan[(0x62, a)] = 0xF0 if v == MUS_RIVAL else 0xF1        # lab, Cerulean (and phase 17's old Route 22)
    for a, v in pm(0x61): plan[(0x61, a)] = 0xF0 if v == MUS_RIVAL else 0xF1        # S.S. Anne (phase 45)
    for a, v in pm(0x6F): plan[(0x6F, a)] = 0xF1                                     # lab's Pokédex scene (Red: alternate start)
    r22 = pm(0x72); assert len(r22) == 8, r22
    for k, (a, v) in enumerate(r22):                                                # 1st battle (2 coords), 2nd battle (2 coords)
        second = k >= 4
        plan[(0x72, a)] = {(False, MUS_RIVAL): 0xF0, (False, MUS_RIVAL_AFTER): 0xF1,
                           (True, MUS_RIVAL): 0xF2, (True, MUS_RIVAL_AFTER): 0xF3}[(second, v)]
    for (b, a), v in sorted(plan.items()):
        rom[fo(b, a) + 1] = v
        log.append('%02X:%04X playmusic -> %02X' % (b, a, v))
    # ---- Pokémon Tower 2F and Silph Co. 7F (phases 11 / 14 played no music): Red plays Music_MeetRival when he comes,
    # Music_RivalAlternateStart after the battle, then the map's music
    SB, TB = 0x7A, 0x7B                         # Silph Co. 7F's scripts / Pokémon Tower 2F's scripts (new blocks here)
    f7b, n7b = bank_free_tail(rom, TB); f7b += 8; assert n7b > 0x60
    f7a, n7a = bank_free_tail(rom, SB); f7a += 2; assert n7a >= 16
    def here(f): return 0x4000 + f % 0x4000
    def put(bank_off, data):
        nonlocal f7b
        a = here(f7b); rom[f7b:f7b + len(data)] = data; f7b += len(data); return a
    def w(v): return bytes([v & 0xFF, v >> 8])
    def after_block(bank, at):
        """at: 'opentext / writetext t / waitbutton / closetext / disappear o / setevent e / end' after the battle"""
        o = fo(bank, at); seg = rom[o:o + 14]
        assert seg[0:2] == b'\x47\x4c' and seg[4:6] == b'\x53\x49' and seg[6] == 0x6D and seg[8] == 0x33 and seg[11] == 0x90, seg.hex()
        t = seg[2] | seg[3] << 8
        blk = (b'\x7e\xf1\x00\x47\x4b' + bytes([bank]) + w(t) + b'\x53\x49' + bytes(seg[6:11]) + b'\x81\x90')
        a = put(TB, blk)
        rom[o:o + 4] = b'\x04' + bytes([TB]) + w(a)
        log.append('%02X:%04X after the battle -> %02X:%04X' % (bank, at, TB, a))
    # Silph Co. 7F: the two coord scripts' "applymovement $0A / sjump rvb"
    seg = rom[SB * 0x4000:(SB + 1) * 0x4000]
    hits = [m.start() for m in re.finditer(rb'\x68\x0a..\x03\xa2\x66', seg, re.S)]
    assert len(hits) == 2, hits
    for h in hits:
        o = SB * 0x4000 + h; cp = bytes(rom[o:o + 7])
        ca = here(f7a); rom[f7a:f7a + 7] = cp; f7a += 7                     # the copy, in its own bank
        na = put(TB, b'\x7e\xf0\x00\x04' + bytes([SB]) + w(ca))
        rom[o:o + 7] = b'\x04' + bytes([TB]) + w(na) + b'\x00\x00\x00'
        log.append('%02X:%04X Shigeru comes -> %02X:%04X' % (SB, 0x4000 + h, TB, na))
    k = seg.find(bytes.fromhex('5e 5f 47 4c 30 6a')); assert k > 0 and seg.find(bytes.fromhex('5e 5f 47 4c 30 6a'), k + 1) < 0
    after_block(SB, 0x4000 + k + 2)
    # Pokémon Tower 2F: "faceplayer / opentext / writetext intro" at the start of his talk script
    seg = rom[TB * 0x4000:(TB + 1) * 0x4000]
    k = seg.find(bytes.fromhex('6a 47 4c af 73 53 49 63')); assert k > 0
    o = TB * 0x4000 + k
    na = put(TB, b'\x6a\x7e\xf0\x00\x47\x4c\xaf\x73\x03' + w(0x4000 + k + 5))
    rom[o:o + 3] = b'\x03' + w(na)
    log.append('%02X:%04X Shigeru talks -> %02X:%04X' % (TB, 0x4000 + k, TB, na))
    k = seg.find(bytes.fromhex('5e 5f 47 4c 38 74')); assert k > 0
    after_block(TB, 0x4000 + k + 2)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
