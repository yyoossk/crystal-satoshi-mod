#!/usr/bin/env python3
"""Phase 120: Crystal's own bugs, part 2 -- the rest of the engine (docs/bugs_and_glitches.md, as phase 119):
 1. Beat Up blocked by Protect / Detect does not raise the Substitute again (EFFECT_BEAT_UP -> .multihit)
 2. HP bar animation is slow for high HP (ld a,e before the pops)
 3. A Park Ball outside the Bug-Catching Contest has a broken animation (wBattleType == BATTLETYPE_CONTEST)
 4. SFX_RUN does not play right when a wild Pokemon flees (WaitPlaySFX)
 5. Magikarp in the Lake of Rage are shorter, not longer (the map checks were inverted; the Japanese ROM keeps the
    length in mm, so the US unit-conversion bug is not here)
 6. Magikarp lengths can be miscalculated (BCLessThanDE: ret nc -> ret nz)
 7. Entei's Pokedex cry can distort Raikou's and Suicune's (PlayMonCry, the document's workaround)
 8. No bump noise when standing on tile $3E (the STANDING check first)
 9. The "HOF Master!" title (200 times) could never show (cp 201 -> cp 200)
10. Slot machine payout sounds cut each other off (ret z -> ret nz)
11. TryObjectEvent could run data as code (pop bc before the jr nc)
12. ScriptCall can overflow wScriptStack (at most 5 calls deep)
13. LoadSpriteGFX does not keep b (push / pop bc around GetSprite)
14. ChooseWildEncounter does not really check the species (ld a,b before ValidateTempWildMonSpecies)
15. RandomUnseenWildMon always picks a morning Pokemon (the time of day added first)
16. ReadObjectEvents overflows into wObjectMasks (NUM_OBJECTS - 1)
17. ClearWRAM only clears WRAM bank 1 (jr nc -> jr c)
18. BattleAnimCmd_ClearObjs clears only 6 2/3 objects ($a0 -> 10 * $18)
19. Tackle's hit animation misses a part (BattleAnim_TargetObj_1Row)
20. The options menu does not clear the joypad first (ClearJoypad)
21. Team Rocket's battle music is not used for the Executives (Scientists keep theirs: in this MOD Silph Co.'s
    scientists are Red's ordinary trainers)
usage: build_phase120.py IN.gbc OUT.gbc OUT.ips
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *


def expect(rom, o, hexs):
    b = bytes.fromhex(hexs.replace(' ', ''))
    assert rom[o:o + len(b)] == b, (hex(o), rom[o:o + len(b)].hex(' '), hexs)
    return b


def w16(v): return bytes([v & 0xFF, v >> 8])
def ga(o): return o % 0x4000 + (0x4000 if o >= 0x4000 else 0)          # file offset -> bank address


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

    # 1. Beat Up + Protect: BattleCommand_FailureText  cp EFFECT_POISON_MULTI_HIT ; jr z,.multihit ; jp EndMoveEffect
    o = 0x3503A + 8; expect(rom, o, 'fe 4d 28 03 c3 a3 52 cd')
    multihit = ga(o + 7)
    h = put(0x0D, bytes([0xFE, 0x9A, 0xCA]) + w16(multihit) + bytes([0xC3, 0xA3, 0x52]))
    rom[o + 4:o + 7] = bytes([0xC3]) + w16(h)
    log.append('1 Beat Up substitute 0D:%04X' % h)
    # 2. HP bar slow: call ComputeHPBarPixels ; pop bc ; pop de ; pop hl ; ld a,e -> ld a,e first
    o = 0xD99D; expect(rom, o + 3, 'c1 d1 e1 7b 21'); rom[o + 3:o + 7] = bytes([0x7B, 0xC1, 0xD1, 0xE1])
    # 3. Park Ball: ld a,[wCurItem] ; cp PARK_BALL -> ld a,[wBattleType] ; cp BATTLETYPE_CONTEST
    o = 0xEB76; expect(rom, o, 'af ea 44 c6 fa c6 d0 fe b1 c4'); rom[o + 4:o + 9] = bytes([0xFA, 0x61, 0xD2, 0xFE, 0x06])
    # 4. SFX_RUN: call PlaySFX -> call WaitPlaySFX
    o = 0x3C11E; expect(rom, o, '38 06 11 2b 00 cd b0 3b'); expect(rom, 0x3BDB, 'cd e2 3b cd b0 3b c9')
    rom[o + 6:o + 8] = w16(0x3BDB)
    # 5. Magikarp in the Lake of Rage: jr z,.Happiness (x2) -> jr nz
    o = 0x3EA0D; expect(rom, o, 'fa 7b dc fe 09 28 15 fa 7c dc fe 06 28 0e'); rom[o + 5] = 0x20; rom[o + 12] = 0x20
    # 6. Magikarp length: BCLessThanDE  ld a,b ; cp d ; ret c ; ret nc -> ret nz
    o = 0xFBDF5; expect(rom, o, '78 ba d8 d0 79 bb c9'); rom[o + 3] = 0xC0
    # 7. Entei's cry: Pokedex .Cry -> ld a,[wCurPartySpecies] ; call PlayMonCry ; ret
    o = 0x40286; expect(rom, o, 'cd 7d 4a fa 96 d2 cd ee 37 59 50 cd 70 3b c9'); expect(rom, 0x379E, 'cd a5 37 cd e2 3b c9')
    rom[o:o + 15] = bytes([0xFA, 0xC8, 0xD0, 0xCD, 0x9E, 0x37, 0xC9]) + bytes(8)
    log.append('2-7 HP bar, Park Ball, SFX_RUN, Magikarp x2, Entei cry')
    # 8. Bump noise on $3E: DoPlayerMovement.CheckWarp
    o = 0x80226
    expect(rom, o, 'fa 39 d0 5f 16 00 21 5b 42 19 fa d7 d4 be 20 23 3e 01 ea 37 d0 fa 39 d0 fe ff 28 17')
    rom[o:o + 28] = bytes.fromhex('fa39d0 feff 282c 5f 1600 215b42 19 fad7d4 be 201f 3e01 ea37d0 fa39d0')   # (a = wWalkingDirection again for the facing check: warps facing down / left / right)
    # 9. HOF Master: cp HOF_MASTER_COUNT + 1 -> cp HOF_MASTER_COUNT
    o = 0x86882; expect(rom, o, 'fe c9 38'); rom[o + 1] = 0xC8
    # 10. Slots payout: and $7 ; ret z -> ret nz
    o = 0x92F38; expect(rom, o, '73 2b 72 fa 58 cf e6 07 c8 11 67 00'); rom[o + 8] = 0xC0
    # 11. TryObjectEvent: call IsInArray ; jr nc,.nope ; pop bc -> pop bc ; jr nc,.nope
    o = 0x969DA + 10; d = rom[o + 1]; expect(rom, o, '30'); assert rom[o + 2] == 0xC1
    rom[o:o + 3] = bytes([0xC1, 0x30, d - 1])
    # 12. ScriptCall: ld hl,wScriptStackSize ; ld a,[hl] ; cp 5 ; ret nc ; inc [hl] ; hl += 3 * size + 1 (= the entry)
    o = 0x974C9; expect(rom, o, 'd5 21 2d d4 5e 34 16 00 21 2e d4 19 19 19 d1 fa 2a d4 22')
    rom[o:o + 15] = bytes.fromhex('212dd4 7e fe05 d0 34 87 86 85 6f 000000')
    log.append('8-12 bump $3E, HOF Master, slots, TryObjectEvent, ScriptCall')
    # 13. LoadSpriteGFX.LoadSprite: call GetSprite ; ld a,l ; ret -> push bc / pop bc around
    o = 0x142F7 + 19; expect(rom, o, 'cd 2d 42 7d c9')
    h = put(0x05, bytes([0xC5, 0xCD, 0x2D, 0x42, 0xC1, 0x7D, 0xC9])); rom[o:o + 3] = bytes([0xC3]) + w16(h)
    # 14. ChooseWildEncounter: ld b,[hl] ; ld a,b ; call ValidateTempWildMonSpecies ; jr c ; (ld a,b moved up)
    o = 0x2A19A; expect(rom, o, '78 ea 03 d1 46 cd 90 64 38 0d 78 fe c9')
    rom[o + 5:o + 11] = bytes([0x78, 0xCD, 0x90, 0x64, 0x38, 0x0C])
    # 15. RandomUnseenWildMon.GetGrassmon: the time of day first
    o = 0x2A4B6; expect(rom, o, 'e5 01 0d 00 09 fa 9a d2 01 0e 00 cd ca 30')
    rom[o:o + 14] = bytes.fromhex('fa9ad2 010e00 cdca30 e5 010d00 09')
    # 16. ReadObjectEvents: ld c,a ; ld a,NUM_OBJECTS ; sub c ; jr z,.skip -> cpl ; add NUM_OBJECTS - 1 ; jr nc,.skip ; inc a
    o = 0x23FD; expect(rom, o + 3, '4f 3e 10 91 28'); d = rom[o + 8]
    rom[o + 3:o + 9] = bytes([0x2F, 0xC6, 0x0F, 0x30, d + 1, 0x3C])
    # 17. ClearWRAM: cp 8 ; jr nc -> jr c
    o = 0x25A + 17; expect(rom, o, 'fe 08 30 ed'); rom[o + 2] = 0x38
    # 18. BattleAnimCmd_ClearObjs: ld a,$a0 -> NUM_BATTLE_ANIM_STRUCTS * BATTLEANIMSTRUCT_LENGTH
    o = 0xCC46A; expect(rom, o, '21 0a d3 3e a0 36 00 23 3d 20 fa c9'); rom[o + 4] = 0xF0
    # 19. Tackle: anim_call BattleAnim_TargetObj_2Row -> _1Row
    o = 0xCA27F; expect(rom, o, 'd1 01 fe 3f 7c f0 24'); rom[o + 3] = 0x47
    # 20. Options: call ClearJoypad first
    o = 0xE41D0; expect(rom, o, '21 aa ff 7e f5 36 01'); expect(rom, 0x92F, 'af e0 a7 e0 a8 c9')
    h = put(0x39, bytes([0xCD, 0x2F, 0x09, 0x21, 0xAA, 0xFF, 0xC9])); rom[o:o + 3] = bytes([0xCD]) + w16(h)
    # 21. Rocket music for EXECUTIVEM / EXECUTIVEF: cp GRUNTF ; jr z,.done
    o = 0x2FD66; expect(rom, o, '11 31 00 fe 1f 28 4c fe 42 28 48 11')
    done = ga(o + 11 + 0x48); nxt = ga(o + 11)
    h = put(0x0B, bytes([0xFE, 0x42, 0xCA]) + w16(done) + bytes([0xFE, 0x33, 0xCA]) + w16(done) +
            bytes([0xFE, 0x37, 0xCA]) + w16(done) + bytes([0xC3]) + w16(nxt))
    rom[o + 7:o + 11] = bytes([0xC3]) + w16(h) + bytes([0])
    log.append('13-21 sprites, wild mons, objects, WRAM, anims, options, Rocket music (0B:%04X)' % h)

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
