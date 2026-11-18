#!/usr/bin/env python3
"""Phase 119: Crystal's own bugs, part 1 -- the battle engine (2026-11-18 request 「テストが終わって最後にクリスタルから
もともとあるバグが残ってるか確認して修正して」).  pret/pokecrystal docs/bugs_and_glitches.md, the bugs the feature
kit (bugfix.asm, 29) and phase 113 had not fixed; each fixed as the document says, at the Japanese ROM's places
(found from the US code; every site's bytes are checked first):
 1. Reflect / Light Screen: (Special) Defense wraps around above 1024 in link battles (the link check removed)
 2. Present: wrong damage in link battles (the link checks removed)
 3. Beat Up: desynchronizes link battles (cp [hl] -> cp c)
 4. Beat Up with only one Pokemon: the rest of the move's effect never runs (ret)
 5. Beat Up may trigger King's Rock even when it failed (wAttackMissed set)
 6. Metal Powder can make boosted (Special) Defense wrap and so increase the damage taken (x1.5 capped at 999,
    before TruncateHL_BC)
 7. A Pokemon that fainted from Pursuit keeps its old status when revived (UpdateFaintedPlayerMon, via a far call:
    bank $0F is full)
 8. RIVAL2 has lower DVs than RIVAL1 (9/8/8/8 -> 13/13/13/13)
 9. "Smart" AI discourages Conversion2 after the first turn (jr nz -> jr z)
10. "Smart" AI does not encourage Sunny Day with Solar Beam, Flame Wheel or Moonlight (the list, moved)
11. "Cautious" AI may fail to discourage residual moves (ret nc -> back to the loop)
12. AI does not discourage Nightmare if the player has any status (and SLP_MASK)
13. AI does not discourage Future Sight when it is already used (wEnemyFutureSightCount)
14. AI's false assumption about CheckTypeMatchup (the move type read in BattleCheckTypeMatchup; the AI's calls and
    the predef go to the new entry)
15-17. AI's Full Heal / Full Restore: Nightmare, confusion and burn/paralysis stat drops cured
18. AI might use its base reward value as an item (de reset each loop)
 Checked, not in this ROM: Heavy Ball's dex-entry bank (the Japanese ROM reads all entries from one bank);
 HELD_CATCH_CHANCE (no item has that effect).
usage: build_phase119.py IN.gbc OUT.gbc OUT.ips
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

FAR_BANK = 0x20                       # far code (bank $20 has free space)
W_ATTACK_MISSED = 0xC65B              # (the kit's bugfix.asm)


def expect(rom, o, hexs):
    b = bytes.fromhex(hexs.replace(' ', ''))
    assert rom[o:o + len(b)] == b, (hex(o), rom[o:o + len(b)].hex(' '), hexs)
    return b


def main():
    src, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src, 'rb').read())
    log = []
    # free space in bank $0D (its tail) and the far bank
    f0d = bank_free_tail(rom, 0x0D)[0] + 2
    def put0d(code):
        nonlocal f0d
        a = f0d; assert a + len(code) <= 0x0D * 0x4000 + 0x4000 and not any(rom[a:a + len(code)])
        rom[a:a + len(code)] = code; f0d += len(code); return 0x4000 + a - 0x0D * 0x4000
    ffar = bank_free_tail(rom, FAR_BANK)[0] + 16
    def putfar(code):
        nonlocal ffar
        a = ffar; assert a + len(code) <= FAR_BANK * 0x4000 + 0x4000 and not any(rom[a:a + len(code)])
        rom[a:a + len(code)] = code; ffar += len(code); return 0x4000 + a - FAR_BANK * 0x4000
    def w16(v): return bytes([v & 0xFF, v >> 8])

    # 1. Reflect / Light Screen: TruncateHL_BC.finish  ld a,[wLinkMode] ; cp LINK_COLOSSEUM ; jr z,.done
    o = 0x3536B; expect(rom, o, 'fa dc c2 fe 03 28 04 7c b0 20'); rom[o:o + 7] = bytes(7)
    log.append('1 Reflect/Light Screen link check removed at 0D:%04X' % (o - 0x30000))
    # 2. Present: both link checks
    o = 0x378C5; expect(rom, o, 'fa dc c2 fe 03 28 02 c5 d5 cd d2 46 fa dc c2 fe 03 28 02 d1 c1')
    rom[o:o + 7] = bytes(7); rom[o + 12:o + 19] = bytes(7)
    log.append('2 Present link checks removed at 0D:%04X' % (o - 0x30000))
    # 3. Beat Up: ld a,[wCurBeatUpPartyMon] ; ld c,a ; ld a,[wCurBattleMon] ; cp [hl] -> cp c
    o = 0x3548D + 19; expect(rom, o, 'fa 02 d0 4f fa 94 d0 be 21 30 c6 28 05'); rom[o + 7] = 0xB9
    log.append('3 Beat Up cp [hl] -> cp c at 0D:%04X' % (o + 7 - 0x30000))
    # 4. Beat Up with one Pokemon: .only_one_beatup  call BattleCommand_BeatUpFailText ; jp EndMoveEffect -> ret
    o = 0x36A2B; expect(rom, o, '3e 02 cd 96 39 cb 96 cd b5 55 c3 a3 52'); rom[o + 7:o + 13] = bytes([0xC9, 0, 0, 0, 0, 0])
    log.append('4 Beat Up one Pokemon: ret at 0D:%04X' % (o + 7 - 0x30000))
    # 5. Beat Up fail text: ... jp PrintButItFailed -> jp (inc a ; ld [wAttackMissed],a ; jp PrintButItFailed)
    o = 0x355B5; expect(rom, o, 'fa 21 c7 a7 c0 c3 9f 73')
    a = put0d(bytes([0x3C, 0xEA]) + w16(W_ATTACK_MISSED) + bytes([0xC3, 0x9F, 0x73]))
    rom[o + 6:o + 8] = w16(a)
    log.append('5 Beat Up fail sets wAttackMissed: 0D:%04X' % a)
    # 6. Metal Powder: the x1.5 capped at 999, and called before TruncateHL_BC (push/pop hl)
    o = 0x352B1 + 26; expect(rom, o, '79 cb 3f 81 4f d0 cb 38 78 a7 20 01 04 37 cb 19 c9')
    fix = bytes([0x60, 0x69, 0xCB, 0x38, 0xCB, 0x19, 0x09, 0x44, 0x4D, 0x3E, 0x03, 0xB8, 0x38, 0x05, 0xC0, 0x3E, 0xE7,
                 0xB9, 0xD0, 0x01, 0xE7, 0x03, 0xC9])
    a = put0d(fix); rom[o:o + 3] = bytes([0xC3]) + w16(a)
    wrap = put0d(bytes([0xE5, 0xCD, 0xB1, 0x52, 0xE1, 0xC3, 0x4D, 0x53]))    # push hl ; call DittoMetalPowder ; pop hl ; jp TruncateHL_BC
    for o in (0x3533F, 0x35453):
        b = expect(rom, o, 'cd 4d 53'); assert rom[o + 6] == 0x5F and rom[o + 7:o + 10] == bytes([0xCD, 0xB1, 0x52])
        rom[o + 1:o + 3] = w16(wrap); rom[o + 7:o + 10] = bytes(3)
    log.append('6 Metal Powder: 0D:%04X, wrapper 0D:%04X' % (a, wrap))
    # 7. Pursuit: ld a,[wLastPlayerMon] ; ld c,a ; ld hl,wBattleParticipantsNotFainted ; ld b,RESET_FLAG ; predef
    o = 0x3DC4B + 0x4F; expect(rom, o, 'fa 0e c7 4f 21 58 c6 06 00 3e 03 cd 55 2d cd 2e 54')
    far = putfar(bytes([0xFA, 0x94, 0xD0, 0xF5, 0xFA, 0x0E, 0xC7, 0xEA, 0x94, 0xD0,       # push [wCurBattleMon] ; = [wLastPlayerMon]
                        0x3E, 0x0F, 0x21, 0x9D, 0x51, 0xCF,                               # farcall UpdateFaintedPlayerMon
                        0xF1, 0xEA, 0x94, 0xD0, 0xC9]))                                    # pop ; ret
    expect(rom, 0x3D19D, 'fa 94 d0 4f 21 58 c6 06 00 3e 03 cd 55 2d')                     # (UpdateFaintedPlayerMon)
    rom[o:o + 14] = bytes([0x3E, FAR_BANK, 0x21]) + w16(far) + bytes([0xCF]) + bytes(8)
    log.append('7 Pursuit faint: far %02X:%04X' % (FAR_BANK, far))
    # 8. RIVAL2's DVs (both copies of the table: RIVAL1 = class 9 = dd dd, RIVAL2 = class 42)
    n = 0
    for base in (0x2742F, 0x27DD8):
        if rom[base + 16:base + 18] == b'\xdd\xdd' and rom[base + 82:base + 84] == b'\x98\x88':
            rom[base + 82:base + 84] = b'\xdd\xdd'; n += 1
    assert n >= 1
    log.append('8 RIVAL2 DVs 13/13/13/13 (%d tables)' % n)

    # ---- the AI.  Free space in bank $0E: Crystal's unused AI_Items.UnusedHealItem (0E:42AE-42F8, 75 bytes)
    uo = 0x382AE; expect(rom, uo, '21 6f 52 3e 0e cf 38 2e c5 11 4a d2 21 48 d2 1a 96 28 26')
    uend = 0x382F9; expect(rom, uend, '3e 0e 21')  if False else None
    def put0e(code):
        nonlocal uo
        a = uo; assert a + len(code) <= 0x382F9
        rom[a:a + len(code)] = code; uo += len(code); return 0x4000 + a - 0x38000
    rom[uo:0x382F9] = bytes(0x382F9 - uo)
    # 9. Conversion2
    o = 0x38DB6; expect(rom, o, 'fa 0f c7 a7 20 2b'); rom[o + 4] = 0x28
    # 10. Sunny Day moves: FIRE_PUNCH EMBER FLAMETHROWER SOLARBEAM FIRE_SPIN FIRE_BLAST FLAME_WHEEL SACRED_FIRE MORNING_SUN
    #     SYNTHESIS MOONLIGHT
    expect(rom, 0x39152, '07 34 35 53 7e dd ea eb ff')
    t = put0e(bytes([0x07, 0x34, 0x35, 0x4C, 0x53, 0x7E, 0xAC, 0xDD, 0xEA, 0xEB, 0xEC, 0xFF]))
    o = 0x39111 + 23; expect(rom, o, '21 52 51 cd'); rom[o + 1:o + 3] = w16(t)
    # 11. Cautious: call Random ; cp 90 percent + 1 ; ret nc ; inc [hl] ; jr .loop (.loop = 0E:5443)
    o = 0x39436 + 40; expect(rom, o, 'fe e6 d0 34 18 df')
    hlp = put0e(bytes([0xD2, 0x43, 0x54, 0x34, 0xC3, 0x43, 0x54]))
    rom[o + 2:o + 6] = bytes([0xC3]) + w16(hlp) + bytes([0])
    # 15-17. AI_HealStatus (0E:44EC) -> the full routine in the free space
    o = 0x384EC; expect(rom, o, 'fa 57 c6 21 d9 d2 01 30 00 cd ca 30 af 77 ea 45 d2 21 65 c6 cb 86 c9')
    new = bytes(rom[o:o + 17]) + bytes([0xEA, 0x6F, 0xC6,                 # ld [wEnemyConfuseCount], a
                                        0x21, 0x63, 0xC6, 0xCB, 0xBE,     # res SUBSTATUS_CONFUSED, [wEnemySubStatus3]
                                        0x21, 0x61, 0xC6, 0xCB, 0x86,     # res SUBSTATUS_NIGHTMARE, [wEnemySubStatus1]
                                        0x21, 0x65, 0xC6, 0xCB, 0x86,     # res SUBSTATUS_TOXIC, [wEnemySubStatus5]
                                        0x3E, 0x0D, 0x21, 0x0A, 0x66, 0xCF,   # farcall CalcEnemyStats
                                        0xC9])
    expect(rom, 0x3660A, '21 c8 c6 11 b5 c6')                                 # (CalcEnemyStats)
    hs = put0e(new); rom[o:o + 3] = bytes([0xC3]) + w16(hs)
    # 18. AI_TryItem: both jumps back to .loop go to the ld de, wEnemyTrainerItem1 before it
    o = 0x38105 + 36; expect(rom, o, '11 46 c6 7e a7 3c c8')
    assert rom[0x38105 + 57] == 0xED and rom[0x38105 + 74] == 0xDC
    rom[0x38105 + 57] = 0xEA; rom[0x38105 + 74] = 0xD9
    log.append('9-11, 15-18 AI (bank 0E: Sunny Day list 0E:%04X, Cautious 0E:%04X, HealStatus 0E:%04X)' % (t, hlp, hs))
    # 12. Nightmare (bank $0B): ld a,[wBattleMonStatus] ; and a ; jr z,.Redundant -> and SLP_MASK
    o = 0x2D5BD; expect(rom, o, 'fa 30 c6 a7 28 64 fa 5c c6')
    red = 0x4000 + (o + 6 + 0x64) - 0x2C000; nxt = 0x4000 + (o + 6) - 0x2C000
    f0b = bank_free_tail(rom, 0x0B)[0] + 2; assert f0b + 8 <= 0x30000
    code = bytes([0xE6, 0x07, 0xCA]) + w16(red) + bytes([0xC3]) + w16(nxt)
    rom[f0b:f0b + len(code)] = code; rom[o + 3:o + 6] = bytes([0xC3]) + w16(0x4000 + f0b - 0x2C000)
    # 13. Future Sight: ld a,[wEnemyScreens] ; bit SCREENS_UNUSED,a -> ld a,[wEnemyFutureSightCount] ; and a
    o = 0x2D619; expect(rom, o, 'fa f4 c6 cb 6f c9'); rom[o:o + 5] = bytes([0xFA, 0x12, 0xC7, 0xA7, 0x00])
    expect(rom, 0x37D85 + 31, '21 12 c7')                                         # (wEnemyFutureSightCount)
    log.append('12-13 AI redundant: Nightmare 0B:%04X, Future Sight' % (0x4000 + f0b - 0x2C000))
    # 14. CheckTypeMatchup: the move type read in BattleCheckTypeMatchup, CheckTypeMatchup 5 bytes later
    o = 0x347C8; expect(rom, o, '21 55 d2 f0 e4 a7 28 03 21 40 c6 e5 d5 c5 3e 0f cd 90 39 57')
    rom[o + 11:o + 19] = bytes([0x3E, 0x0F, 0xCD, 0x90, 0x39, 0xE5, 0xD5, 0xC5])
    n = 0
    for c in (0x34877, 0x348B7, 0x348CA, 0x34902, 0x34A67, 0x34AD5, 0x34B50, 0x34B60):
        expect(rom, c, 'cd d3 47'); rom[c + 1] = 0xD8; n += 1
    expect(rom, 0x862E, 'd3 47 0d'); rom[0x862E] = 0xD8
    log.append('14 CheckTypeMatchup 0D:47D3 -> 47D8 (%d calls + predef)' % n)

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
