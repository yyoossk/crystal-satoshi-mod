#!/usr/bin/env python3
"""Phase 64: the kit 「クリスタル追加機能キット（全機能・60fps・バグ修正）」 (kitfx/…, from the Crystal feature patch Ver.1.5.0):
every feature but the 251 version, 60fps and the original game's bug fixes, built on this MOD.  The ROM becomes 4 MB
(MBC30: the kit's banks 0x60-0x7B are moved to 0x80-0x9B, since this MOD uses 0x60-0x7F).

Not built (already in this MOD, or not for this MOD):
  src/safari/safari.asm (Red's Safari Zone: phase 28), src/legends_crystal.asm (Celebi: phase 61/63; the birds would put
  Gen I in Johto), src/starters_crystal.asm (Kanto's starters: phase 58), src/wild_crystal.asm (Gen I in Johto),
  the Kanto gym leaders' rematch patches in src/rematch.asm (phase 50), the rematch's winloss text bank
  (phase 54 reads it from the bank of the script that set it).
Moved / adapted for this MOD (the kit's files say 「この MOD：」 where they were changed):
  ROM0 60fps VBlank $3FAB; bank 2 picture colors $7A00; bank 3 bug fixes / follow: the unused LoadBoxMonListing
  ($6896-$6945); bank 4 start menu $7F1A; bank 5 follow $7E0E (the MOD's dead copies of the second sprite table),
  the lab ball sprite = id $79 (the MOD's second sprite table: Giovanni is $3F); bank 9 party menu $7EA0, quick ball
  in the unused Function241d5; bank 0A $7D72; bank 0B $7F60; bank 0D $7F48; bank 0F bug fixes in unused routines;
  bank 13 $7FD8; bank 14 $7A40; bank 1A prize TM names in the MOD's dead prize Pokémon script (phase 59); bank 20 B dash
  $6B60; bank 25 $7FB0; rematch party check in bank 7E (the MOD's trainer code, phase 13); the Safari Ball colors in
  bank 33; league (16 badges): only after Johto's Hall of Fame; the Pokégear's Friday line: Mantine (phase 60);
  the dex's fishing marks from this MOD's fishing (generated below).
After the build (here): the TM shop on the MOD's Red Celadon 3F clerk (after TM18 and Johto's Hall of Fame), the
always-bite fishing also for the MOD's own rods (phase 57's Kanto handler, phase 28's Safari Zone).
usage: build_phase64.py IN.gbc OUT.gbc OUT.ips   (rgbds 1.0.4: ref/rgbds1)
"""
import sys, os, re, shutil, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
import build_phase57 as P57
import portmaps as PM

KIT = os.path.join(SC, 'kitfx', 'クリスタル追加機能キット（全機能・60fps・バグ修正）')
ROM4 = 0x400000
EV_BEAT_E4 = 0x44
MAGIKARP, GOLDEEN, POLIWAG = 0x81, 0x76, 0x3C
FISH_BANK, FISH_GROUPS, N_FISH, TIME_FISH = 0x24, 0x69FB, 13, 0x6BE2
KEEP_SIDE = [(3, 83), (24, 1), (24, 2), (19, 1)]           # Crystal's Johto side (Tohjo Falls, Routes 26-28)


def fishnest_inc(rom):
    """src/fishnest_maps_mod.inc: Johto's spots as the kit's (Crystal's maps), Johto's groups from this ROM (phase 60),
    Kanto's spots and species from phase 57's fishing (one group per Super Rod group, after Johto's 13)"""
    ents = []
    for l in open(os.path.join(KIT, 'src', 'fishnest_maps_crystal.inc'), encoding='utf-8'):
        m = re.match(r'\s*db \$(\w+), \$(\w+) ; map (\d+)\.(\d+)', l)
        if m: ents.append((int(m.group(1), 16), int(m.group(2), 16), int(m.group(3)), int(m.group(4))))
    old, good, sup, fmaps = P57.kit_fish()
    tab = {P57.KIT_MAP[n]: k for n, k in fmaps.items()}
    for mp, k in P57.EXTRA_FISH.items(): tab[mp] = fmaps[k] if isinstance(k, str) else k
    G = US.get().groups()
    lm = {(g, n): l for l, f, g, n in ents}
    out = []
    for l, f, g, n in ents:
        if l < 0x2F or (g, n) in KEEP_SIDE: out.append((l, f, g, n))
    nosup = N_FISH + 1 + len(sup)
    for (g, n), k in sorted(tab.items()):
        l = lm.get((g, n)) or rom[G[g - 1] + 9 * (n - 1) + 5]
        assert l >= 0x2F, (g, n, l)
        out.append((l, N_FISH + 1 + k if k != 0xFF else nosup, g, n))
    seen = set(); lines = ['; 「ぶんぷをみる」の 釣りの 場所の 表（この MOD。tools/build_phase64.py が 作った）', '', 'FishNestMaps:']
    for l, f, g, n in out:
        if (l, f) in seen: continue
        seen.add((l, f)); lines.append('\tdb $%02x, $%02x ; map %d.%d' % (l, f, g, n))
    lines += ['\tdb 0', '', 'FishNestGroupMons:']
    groups = []
    for gi in range(N_FISH):                                     # Crystal's groups as in this ROM
        o = fo(FISH_BANK, FISH_GROUPS) + 7 * gi + 1; mons = []
        for r in range(3):
            p = fo(FISH_BANK, rom[o + 2 * r] | rom[o + 2 * r + 1] << 8)
            while True:
                ch, s_, lv = rom[p], rom[p + 1], rom[p + 2]
                cand = [rom[fo(FISH_BANK, TIME_FISH) + lv * 4], rom[fo(FISH_BANK, TIME_FISH) + lv * 4 + 2]] if s_ == 0 else [s_]
                for c in cand:
                    if c not in mons: mons.append(c)
                p += 3
                if ch == 0xFF: break
        groups.append(mons)
    for k in range(len(sup)):                                    # phase 57: old / good / this Super Rod group
        mons = [MAGIKARP, GOLDEEN, POLIWAG]
        for thr, s_, lv in sup[k]:
            if s_ not in mons: mons.append(s_)
        groups.append(mons)
    groups.append([MAGIKARP, GOLDEEN, POLIWAG])                  # no Super Rod data
    assert len(groups) == nosup
    for gi in range(len(groups)): lines.append('\tdw .group%d' % (gi + 1))
    lines.append('.end_ptrs')
    for gi, mons in enumerate(groups):
        lines += ['.group%d' % (gi + 1), '\tdb ' + ', '.join('$%02x' % m for m in mons) + ', 0']
    return '\n'.join(lines) + '\n', len(seen)


def main():
    src_rom, outrom, outips = [os.path.abspath(x) for x in sys.argv[1:4]]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    assert len(rom) == 0x200000 and rom[0x147] == 0x10 and rom[0x148] == 6
    def r16(o): return rom[o] | rom[o + 1] << 8
    log = []

    # ---------- what the kit's moved pieces assume about this MOD
    for b, lo, hi in ((3, 0x6896, 0x6946), (9, 0x41D5, 0x4216), (0x0F, 0x76B9, 0x76F5), (0x0F, 0x6DBF, 0x6DE3),
                      (0x0F, 0x6BD6, 0x6BE7), (0x0F, 0x73B7, 0x73E7)):
        assert rom[fo(b, lo):fo(b, hi)] == orig[fo(b, lo):fo(b, hi)], 'unused routine changed: %02X:%04X' % (b, lo)
    assert rom[fo(3, 0x6895)] == 0xC9 and rom[fo(9, 0x41D4)] == 0xC9
    stub = fo(0x05, r16(0x14231 + 1)); assert rom[stub:stub + 2] == bytes([0xFE, 0x67])
    t2 = r16(stub + 9) + 0x66 * 6
    assert t2 == 0x7F34 and t2 + 6 * (0x78 - 0x66) == 0x7FA0, hex(t2)      # sprite ids $67-$78; $79 = the lab ball
    assert not any(rom[fo(0x05, 0x7FA0):fo(0x05, 0x7FA6)])
    # 05:7E0E-7EF9: the copies of the second sprite table left by phases 26 / 28 / 29 (only $7F34 is read now)
    for c_, n_ in ((0x7E0E, 12), (0x7E57, 13), (0x7EA6, 14)):
        assert rom[fo(0x05, c_):fo(0x05, c_) + 6 * n_] == rom[fo(0x05, t2):fo(0x05, t2) + 6 * n_], hex(c_)
    assert rom[fo(0x1A, 0x74C6)] == 0x04 and rom[fo(0x1A, 0x74CA):fo(0x1A, 0x759B)] == orig[fo(0x1A, 0x74CA):fo(0x1A, 0x759B)]
    assert rom[fo(0x0F, 0x75FE):fo(0x0F, 0x7604)] == bytes([0x21, 0x8F, 0x57, 0x3E, 0x7E, 0xCF])   # ReadTrainerParty: bank 7E (phase 13)
    assert rom[fo(0x7E, 0x57AB):fo(0x7E, 0x57AE)] == orig[fo(0x0E, 0x57AB):fo(0x0E, 0x57AE)]
    assert not any(rom[fo(0x7E, 0x7FEB):fo(0x7E, 0x8000)])
    assert rom[0x3F80:0x3FAB] != bytes(0x2B) and not any(rom[0x3FAB:0x4000])
    assert not any(rom[fo(0x33, 0x7FE0):fo(0x33, 0x8000)])

    # ---------- 4 MB
    rom4 = rom + bytes(ROM4 - len(rom)); rom4[0x148] = 7
    inc, n = fishnest_inc(rom)
    open(os.path.join(KIT, 'src', 'fishnest_maps_mod.inc'), 'w', encoding='utf-8').write(inc)
    log.append('fishing marks: %d spots' % n)
    open(os.path.join(KIT, 'base.gbc'), 'wb').write(rom4)
    env = dict(os.environ, PATH=os.path.join(SC, 'ref', 'rgbds1') + ':' + os.environ['PATH'])
    asms = open(os.path.join(KIT, 'buildlist.txt')).read().split()
    r = subprocess.run(['python3', 'build.py', 'feat.gbc'] + asms, cwd=KIT, env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    out = bytearray(open(os.path.join(KIT, 'feat.gbc'), 'rb').read())
    assert len(out) == ROM4
    sym = {}
    for l in open(os.path.join(KIT, 'feat.sym')):
        m = re.match(r'([0-9a-f]+):([0-9a-f]+) (\S+)', l)
        if m: sym[m.group(3)] = (int(m.group(1), 16), int(m.group(2), 16))

    # ---------- the TM shop: the MOD's Red Celadon 3F clerk (phase 41), after TM18 and Johto's Hall of Fame
    tb, ta = sym['TmShopScript']
    tm18 = PM.item_id('TM_COUNTER')
    # faceplayer / opentext / checkevent got / iftrue .e / writetext / promptbutton / verbosegiveitem TM18, 1
    pat = re.compile(rb'\x6A\x47\x31..\x09(..)\x4C..\x54\x9D' + bytes([tm18]) + rb'\x01', re.S)
    hits = []
    for b in range(0x40, 0x80):
        for m in pat.finditer(out, fo(b, 0x4000), fo(b, 0x8000)):
            e = fo(b, m.group(1)[0] | m.group(1)[1] << 8)
            if out[e] == 0x4C and out[e + 3:e + 6] == bytes([0x53, 0x49, 0x90]): hits.append((b, m.start(), e))
    assert len(hits) == 1, [(hex(b), hex(s_), hex(e)) for b, s_, e in hits]
    b, s_, e = hits[0]
    stub = bytes([0x31, EV_BEAT_E4 & 0xFF, EV_BEAT_E4 >> 8, 0x09, ta & 0xFF, ta >> 8,      # checkevent / iftrue TmShopScript
                  0x4B, b, out[e + 1], out[e + 2], 0x53, 0x49, 0x90])                   # farwritetext (Red's) / waitbutton / closetext / end
    end_ = fo(tb, 0x8000)
    while out[end_ - 1] == 0: end_ -= 1
    sa = end_ - fo(tb, 0x4000) + 0x4000 + 16
    assert sa + len(stub) < 0x8000 and not any(out[fo(tb, sa):fo(tb, sa) + len(stub)])
    out[fo(tb, sa):fo(tb, sa) + len(stub)] = stub
    out[e:e + 4] = bytes([0x04, tb, sa & 0xFF, sa >> 8])                    # writetext / waitbutton -> farsjump stub
    log.append('TM shop: Celadon 3F clerk %02X:%04X -> %02X:%04X' % (b, e % 0x4000 + 0x4000, tb, sa))

    # ---------- always bite: the MOD's rods too
    n_ = 0
    for m in re.finditer(rb'\xCD\x5E\x2F\xFE\x80\x30.\x7B\xA7\x28', out[fo(0x47, 0x4000):fo(0x47, 0x8000)], re.S):
        o = fo(0x47, 0x4000) + m.start() + 5; out[o:o + 2] = bytes(2); n_ += 1      # phase 57 (Kanto): bite 50% -> always
    assert n_ == 1, n_
    m = list(re.finditer(rb'\xCD\x5E\x2F\xCB\x3F\x38.\xE6\x03\xFE\x02', out[fo(0x6E, 0x4000):fo(0x6E, 0x8000)], re.S))
    assert len(m) == 1
    o = fo(0x6E, 0x4000) + m[0].start() + 5; out[o:o + 2] = bytes(2)      # phase 28 (Safari Zone): the Good Rod's 50%
    log.append('always bite: phase 57 Kanto rods, phase 28 Safari Good Rod')

    fix_checksum(out)
    open(outrom, 'wb').write(out)
    o2 = orig + bytes(ROM4 - len(orig))
    p = ips(o2, bytes(out))
    p = p[:-3] + (ROM4 - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + out[-1:] + b'EOF'   # the file is 4 MB
    open(outips, 'wb').write(p)
    log.append('kit bytes: %d' % len([i for i in range(len(rom)) if out[i] != rom[i] and i not in (0x14E, 0x14F)]))
    print('\n'.join(log))


if __name__ == '__main__':
    main()
