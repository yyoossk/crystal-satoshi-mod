#!/usr/bin/env python3
"""Phase 13:
 * Pokémon Tower ghost battles as in Red/Pikachu: without the Silph Scope a wild battle on tower 3F-7F
   (including the ghost Marowak) is against the unidentifiable 「ゆうれい」 (ghost pic from the Pikachu
   full-color hack), nobody can attack, running always works, balls are dodged.
   The ghost Marowak can't be caught even with the scope.
 * Giovanni's overworld sprite from the Pikachu full-color hack (sprite slot 0x3F, unused in Crystal).
 * Trainer party data moved out of the full bank 0x0E into bank 0x7E (read code copied along).
usage: build_phase13.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import Space
from jpchar import encode
import build_phase10 as P10

PKFC = SC + '/pkfc/pkfc.gbc'
PKFC_GHOST_PIC = 0x77EAA
PKFC_GIOVANNI_SPRITE = 0x165D2          # 24 tiles, same layout as Crystal walking sprites
OW_SPRITES = 0x14727                    # OverworldSprites (6 bytes per sprite id, from id 1)
SPRITE_GIOVANNI = 0x3F                  # SPRITE_UNUSED_GUY slot
PAL_OW_BLUE = 1

# JP Crystal addresses
W_BATTLEMODE, W_BATTLETYPE, W_TURNENDED = 0xD25E, 0xD261, 0xC6A8
W_TEMPENEMYSPECIES, W_CURPARTYSPECIES, W_ENEMYNICK = 0xD235, 0xD0C8, 0xC616
W_CURITEM, W_NUMITEMS, W_MAPGROUP, W_MAPNUMBER = 0xD0C6, 0xD885, 0xDC7B, 0xDC7C
H_BATTLETURN = 0xE4
CHECKITEM, BATTLETEXTBOX, GET2BPP, PRINTTEXT = 0x2F4B, 0x3A50, 0x0F6C, 0x1041
SILPH_SCOPE, MAROWAK, GHOST_PAL_MON = 0x87, 0x69, 0x4B   # Graveler's grey palette
TOWER_G, TOWER_3F, TOWER_7F, TOWER_6F = 26, 16, 20, 19
# hook sites
H_INITWILD_LOADENEMY = 0x3F669          # bank 0F: call LoadEnemyMon (cd fa 68)
H_BSM_STDTEXT = 0x3FD2E                 # bank 0F: BattleStartMessage call StdBattleTextbox (cd 62 3a)
H_ENEMYHUD_GENDER = 0x3E089            # bank 0F: DrawEnemyHUD callfar GetGender
GETGENDER = (0x14, 0x4C93)
H_RUN = 0x3D8A3                         # bank 0F: TryToRunAwayFromBattle ld a,[wBattleType]
H_DOTURN = 0x3401D                      # bank 0D: DoTurn xor a / ld [wTurnEnded],a
H_POKEBALL = 0xEB58                     # bank 03: PokeBallEffect ld a,[wBattleMode] / dec a / jp nz
H_UBITB = 0xFBCE                        # bank 03: UseBallInTrainerBattle
H_SCENE = 0x4E93E                       # bank 13: CheckBattleScene
H_GETFRONTPIC = 0x5113B                 # bank 14: _GetFrontpic
H_ENEMYPAL = 0x96F7 + 9                 # bank 02: GetEnemyFrontpicPalettePointer ld a,[wTempEnemyMonSpecies]

# trainer data relocation
TR_CODE = (0x3954B, 0x399BA)            # GetTrainerClassName .. TrainerGroups (code copied as is)
TR_BANK = 0x7E
TR_ATTR_REF = 0x395A4                   # in GetTrainerAttributes: ld hl, TrainerClassAttributes
NCLS = P10.NEW_N                        # Crystal 67 + phase 10's new classes
PHONE_TG_REF, NAME_TG_REF = 0x2A590, 0xFDAC9
US_RANGE = (0x557B, 0x599C)             # same code in the US build (labels for far-call search)


def fl(b, a): return b * 0x4000 + (a - 0x4000)


def bank_addr(o): return 0x4000 + o % 0x4000


def ghost_tiles():
    with tempfile.TemporaryDirectory() as d:
        open(d + '/g.pic', 'wb').write(open(PKFC, 'rb').read()[PKFC_GHOST_PIC:PKFC_GHOST_PIC + 0x200])
        subprocess.run([PR + '/tools/pkmncompress', '-u', d + '/g.pic', d + '/g.2bpp'], check=True)
        rm = open(d + '/g.2bpp', 'rb').read()
    assert len(rm) >= 36 * 16, len(rm)
    blank = bytes(16)
    out = blank * 7                                   # Crystal PadFrontpic (6x6): empty first column,
    for col in range(6):                              # then each column = empty tile + 6 tiles
        out += blank
        for row in range(6):
            out += rm[(row * 6 + col) * 16:(row * 6 + col + 1) * 16]
    assert len(out) == 49 * 16
    return out


def far_patterns(rom, lo, hi, old_bank):
    """farcall (ld a,b / ld hl,x / rst 08) and callfar (ld hl,x / ld a,b / rst 08) sites into [lo,hi)"""
    out = []
    for m in re.finditer(re.escape(bytes([0x3E, old_bank, 0x21])) + b'(..)' + re.escape(b'\xCF'), rom, re.S):
        a = m.group(1)[0] | m.group(1)[1] << 8
        if lo <= a < hi: out.append(m.start() + 1)
    for m in re.finditer(b'\x21(..)' + re.escape(bytes([0x3E, old_bank, 0xCF])), rom, re.S):
        a = m.group(1)[0] | m.group(1)[1] << 8
        if lo <= a < hi: out.append(m.start() + 4)
    return out


def relocate_trainers(rom, log):
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    lo, hi = TR_CODE
    xs = fl(TR_BANK, bank_addr(lo)); xe = xs + (hi - lo)
    free_from, _ = bank_free_tail(rom, TR_BANK)
    assert free_from <= xs, hex(free_from)
    code = bytearray(rom[lo:hi])
    tg_old = bank_addr(hi)
    # current data
    attr_cur = fo(0x0E, r16(TR_ATTR_REF + 1))
    attr = bytes(rom[attr_cur:attr_cur + NCLS * 7])
    P10.OLD_N = NCLS
    _, groups, _ = P10.parse_groups(bytes(rom), attr_cur)
    assert len(groups[71]) == 4
    # layout in bank 0x7E: area A (below the copied code) and area B (after it)
    a_lo = free_from + 1; a_hi = xs; b_lo = xe; b_hi = (TR_BANK + 1) * 0x4000
    blobs = [b''.join(nm + d for nm, d in g) for g in groups]
    cur = {'A': a_lo, 'B': b_lo}; lim = {'A': a_hi, 'B': b_hi}
    def alloc(n):
        for k in ('A', 'B'):
            if cur[k] + n <= lim[k]:
                o = cur[k]; cur[k] += n; return o
        raise AssertionError('trainer bank full')
    tg = alloc(2 * NCLS); at = alloc(len(attr))
    rom[at:at + len(attr)] = attr
    for i, bl in enumerate(blobs):
        o = alloc(len(bl)); rom[o:o + len(bl)] = bl; w16(tg + 2 * i, bank_addr(o))
    # code copy: TrainerGroups and attribute pointers
    n_tg = 0
    for i in range(len(code) - 2):
        if code[i] in (0x21, 0x11, 0x01) and code[i + 1] | code[i + 2] << 8 == tg_old:
            code[i + 1] = bank_addr(tg) & 0xFF; code[i + 2] = bank_addr(tg) >> 8; n_tg += 1
    k = TR_ATTR_REF - lo
    assert code[k] == 0x21 and code[k + 1] | code[k + 2] << 8 == bank_addr(attr_cur)
    code[k + 1] = bank_addr(at) & 0xFF; code[k + 2] = bank_addr(at) >> 8
    rom[xs:xe] = code
    # far calls into the code -> new bank
    sites = far_patterns(rom, bank_addr(lo), bank_addr(hi), 0x0E)
    for s in sites:
        rom[s] = TR_BANK
    # RandomPhoneMon (bank 0x0A) reads TrainerGroups/parties with GetFarByte/GetFarWord
    # (and a name reader in bank 0x3F)
    refs = [m.start() for m in re.finditer(re.escape(bytes([0x21, tg_old & 0xFF, tg_old >> 8])), rom)
            if not (lo <= m.start() < hi) and not (xs <= m.start() < xe)]
    assert refs == [PHONE_TG_REF, NAME_TG_REF], [hex(x) for x in refs]
    nb = 0
    for r_, win, want in ((PHONE_TG_REF, 0x68, 6), (NAME_TG_REF, 0x20, 2)):
        w16(r_ + 1, bank_addr(tg))
        got = [j for j in range(r_, r_ + win) if rom[j] == 0x3E and rom[j + 1] == 0x0E]
        assert len(got) == want, (hex(r_), len(got))
        for j in got:
            rom[j + 1] = TR_BANK; nb += 1
    log.append('trainer code copied to %X:%04X, TrainerGroups %04X (%d refs), attributes %04X, parties up to A=%04X B=%04X '
               '(free %d+%d bytes), far calls patched %d, phone refs %d / bank loads %d'
               % (TR_BANK, bank_addr(xs), bank_addr(tg), n_tg, bank_addr(at), bank_addr(cur['A']), bank_addr(cur['B']),
                  lim['A'] - cur['A'], lim['B'] - cur['B'], len(sites), len(refs), nb))
    return sites


def main():
    src, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (0x02, 0x03, 0x0D, 0x0F, 0x13, 0x14, 0x78, 0x7D):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1, b * 0x4000 + 0x4000)
    log = []

    # ================= Giovanni overworld sprite
    pk = open(PKFC, 'rb').read()
    a_spr = sp.put(0x7D, pk[PKFC_GIOVANNI_SPRITE:PKFC_GIOVANNI_SPRITE + 24 * 16])
    e = OW_SPRITES + 6 * (SPRITE_GIOVANNI - 1)
    rom[e:e + 6] = bytes([a_spr & 0xFF, a_spr >> 8, 0xC0, 0x7D, 0x01, PAL_OW_BLUE])
    log.append('Giovanni sprite -> id %02X (7D:%04X)' % (SPRITE_GIOVANNI, a_spr))

    # ================= ghost battle routines (bank 0x78)
    a_pic = sp.put(0x78, ghost_tiles())
    def tx(s): return encode(s)
    a = Asm(sp.here(0x78))
    # IsGhost: carry if wild battle on tower 3F-7F without the Silph Scope
    def wbk1(lab, core):          # run core with WRAM bank 1 selected (the battle/map variables live there)
        a.label(lab)
        a.db(0xC5, 0xF0, 0x70, 0x47, 0x3E, 0x01, 0xE0, 0x70, 0xCD); a.dw(core)
        a.db(0x78, 0xE0, 0x70, 0xC1, 0xC9)
    wbk1('isghost', 'c_isghost'); wbk1('isgm', 'c_isgm'); wbk1('gpic', 'c_gpic')
    a.label('c_isghost')
    a.db(0xFA); a.dw(W_BATTLEMODE); a.db(0x3D, 0x20); a.db(0); jr_no1 = len(a.b) - 1
    a.db(0xFA); a.dw(W_MAPGROUP); a.db(0xFE, TOWER_G, 0x20); a.db(0); jr_no2 = len(a.b) - 1
    a.db(0xFA); a.dw(W_MAPNUMBER); a.db(0xD6, TOWER_3F, 0xFE, TOWER_7F - TOWER_3F + 1, 0x30); a.db(0); jr_no3 = len(a.b) - 1
    a.db(0xC5, 0xD5, 0xE5)                                         # push bc/de/hl
    a.db(0xFA); a.dw(W_CURITEM); a.db(0xF5)                        # ld a,[wCurItem] ; push af
    a.db(0x3E, SILPH_SCOPE, 0xEA); a.dw(W_CURITEM)
    a.db(0x21); a.dw(W_NUMITEMS); a.db(0xCD); a.dw(CHECKITEM)
    a.db(0x9F, 0x47)                                               # sbc a ; ld b,a
    a.db(0xF1, 0xEA); a.dw(W_CURITEM)                              # pop af ; ld [wCurItem],a
    a.db(0x78, 0xE1, 0xD1, 0xC1)                                   # ld a,b ; pop hl/de/bc
    a.db(0xFE, 0x01, 0xC9)                                         # cp 1 (a=0 -> carry) ; ret
    no = len(a.b)
    a.db(0xA7, 0xC9)                                               # .no: and a ; ret
    for j in (jr_no1, jr_no2, jr_no3):
        a.b[j] = no - (j + 1)
    # IsGhostOrMarowak: also the ghost Marowak itself (6F, species MAROWAK) -> can't be caught
    a.label('c_isgm')
    a.db(0xCD); a.dw('c_isghost'); a.db(0xD8)                        # call isghost ; ret c
    a.db(0xFA); a.dw(W_BATTLEMODE); a.db(0xFE, 0x01, 0x20, 0x15)
    a.db(0xFA); a.dw(W_MAPGROUP); a.db(0xFE, TOWER_G, 0x20, 0x0E)
    a.db(0xFA); a.dw(W_MAPNUMBER); a.db(0xFE, TOWER_6F, 0x20, 0x07)
    a.db(0xFA); a.dw(W_TEMPENEMYSPECIES); a.db(0xFE, MAROWAK)
    a.db(0x37, 0xC8)                                               # scf ; ret z
    a.db(0xA7, 0xC9)
    # GhostName: enemy nickname -> ゆうれい
    a.label('gname')
    a.db(0xCD); a.dw('isghost'); a.db(0xD0)
    nm = encode('ゆうれい@'); nm = nm + b'\x50' * (6 - len(nm))
    for i, c in enumerate(nm):
        a.db(0x3E, c, 0xEA); a.dw(W_ENEMYNICK + i)
    a.db(0xC9)
    # GhostIntro: "だめだ！ ゆうれい ポケモンの しょうたいが わからない！"
    a.label('gintro')
    a.db(0xCD); a.dw('isghost'); a.db(0xD0)
    a.db(0x21); a.dw('t_cantid'); a.db(0xCD); a.dw(BATTLETEXTBOX); a.db(0xC9)
    # GhostTurn: carry = skip the turn after the scared / get-out text
    a.label('gturn')
    a.db(0xCD); a.dw('isghost'); a.db(0xD0)
    a.db(0xF0, H_BATTLETURN, 0xA7, 0x21); a.dw('t_scared'); a.db(0x28, 0x03); a.db(0x21); a.dw('t_getout')
    a.db(0xCD); a.dw(BATTLETEXTBOX); a.db(0x37, 0xC9)
    # GhostPic: carry if the front pic being loaded is the ghost (enemy species in a ghost battle)
    a.label('c_gpic')
    a.db(0xCD); a.dw('c_isghost'); a.db(0xD0)
    a.db(0xFA); a.dw(W_CURPARTYSPECIES); a.db(0x47, 0xFA); a.dw(W_TEMPENEMYSPECIES); a.db(0xB8)   # cp b
    a.db(0x37, 0xC8, 0xA7, 0xC9)                                   # scf ; ret z ; and a ; ret
    a.label('t_cantid'); a.raw(encode('{00}だめだ！　ゆうれい　<POKEMON>の<LINE>しょうたいが　わからない！<PROMPT>'))
    a.label('t_scared'); a.raw(encode('{00}<USER>は　こわがっている！<LINE>わざを　だすことが　できない！<PROMPT>'))
    a.label('t_getout'); a.raw(encode('{00}ゆうれい{72}タチサレ<……>タチサレ<……><PROMPT>'))
    base = a.base; blob = a.done(); assert sp.put(0x78, blob) == base
    L = a.labels

    def farcall(asm, lab):
        asm.db(0x3E, 0x78, 0x21); asm.dw(L[lab]); asm.db(0xCF)

    # ---- bank 0F: enemy name / intro text / running
    a = Asm(sp.here(0x0F))
    a.label('name'); a.db(0xCD); a.dw(0x68FA); farcall(a, 'gname'); a.db(0xC9)
    a.label('intro'); a.db(0xCD); a.dw(0x3A62); farcall(a, 'gintro'); a.db(0xC9)
    a.label('run'); farcall(a, 'isghost'); a.db(0x3E, 0x02, 0xD8, 0xFA); a.dw(W_BATTLETYPE); a.db(0xC9)
    # enemy HUD: no ♂/♀ for the ghost (carry = genderless)
    a.label('gender'); farcall(a, 'isghost'); a.db(0xD8, 0x21); a.dw(GETGENDER[1]); a.db(0x3E, GETGENDER[0], 0xCF, 0xC9)
    b0f = a.base; blob = a.done(); assert sp.put(0x0F, blob) == b0f
    assert rom[H_INITWILD_LOADENEMY:H_INITWILD_LOADENEMY + 3] == bytes([0xCD, 0xFA, 0x68])
    w16(H_INITWILD_LOADENEMY + 1, a.labels['name'])
    assert rom[H_BSM_STDTEXT:H_BSM_STDTEXT + 3] == bytes([0xCD, 0x62, 0x3A])
    w16(H_BSM_STDTEXT + 1, a.labels['intro'])
    assert rom[H_RUN:H_RUN + 3] == bytes([0xFA, W_BATTLETYPE & 0xFF, W_BATTLETYPE >> 8])
    rom[H_RUN] = 0xCD; w16(H_RUN + 1, a.labels['run'])
    assert rom[H_ENEMYHUD_GENDER:H_ENEMYHUD_GENDER + 6] == bytes([0x21, GETGENDER[1] & 0xFF, GETGENDER[1] >> 8, 0x3E, GETGENDER[0], 0xCF])
    rom[H_ENEMYHUD_GENDER:H_ENEMYHUD_GENDER + 6] = bytes([0xCD, a.labels['gender'] & 0xFF, a.labels['gender'] >> 8, 0, 0, 0])

    # ---- bank 0D: DoTurn
    a = Asm(sp.here(0x0D))
    a.db(0xAF, 0xEA); a.dw(W_TURNENDED); farcall(a, 'gturn'); a.db(0xD0, 0xE1, 0xC9)   # ret nc ; pop hl ; ret
    b0d = a.base; blob = a.done(); assert sp.put(0x0D, blob) == b0d
    assert rom[H_DOTURN:H_DOTURN + 4] == bytes([0xAF, 0xEA, W_TURNENDED & 0xFF, W_TURNENDED >> 8])
    rom[H_DOTURN] = 0xCD; w16(H_DOTURN + 1, b0d); rom[H_DOTURN + 3] = 0x00

    # ---- bank 03: balls are dodged
    ub = rom[H_UBITB:H_UBITB + 48]
    assert ub[23:26] == bytes([0x3E, 0x37, 0xCD]) and ub[40] == 0x18
    use_disposable = bank_addr(H_UBITB) + 42 + (ub[41] - 256)
    pb = rom[H_POKEBALL:H_POKEBALL + 7]
    assert pb[0] == 0xFA and pb[3] == 0x3D and pb[4] == 0xC2
    a = Asm(sp.here(0x03))
    farcall(a, 'isgm'); a.db(0x38, 0x0A)                           # jr c,.dodge
    a.raw(pb); a.db(0xC3); a.dw(bank_addr(H_POKEBALL) + 7)
    a.raw(ub[:28])                                             # throw animation (as when a trainer blocks it)
    a.db(0x21); a.dw('t'); a.db(0xCD); a.dw(PRINTTEXT); a.db(0xC3); a.dw(use_disposable)
    a.label('t'); a.raw(encode('{00}よけられた！<LINE>こいつは　つかまりそうにないぞ！<PROMPT>'))
    b03 = a.base; blob = a.done(); assert sp.put(0x03, blob) == b03
    rom[H_POKEBALL] = 0xC3; w16(H_POKEBALL + 1, b03)

    # ---- bank 13: CheckBattleScene -> "off" in ghost battles (no front pic animation)
    sc = rom[H_SCENE:H_SCENE + 5]; assert sc[0] == 0x3E and sc[2] == 0x21
    a = Asm(sp.here(0x13))
    farcall(a, 'isghost'); a.db(0xD8); a.raw(sc); a.db(0xC3); a.dw(bank_addr(H_SCENE) + 5)
    b13 = a.base; blob = a.done(); assert sp.put(0x13, blob) == b13
    rom[H_SCENE] = 0xC3; w16(H_SCENE + 1, b13)

    # ---- bank 14: _GetFrontpic -> ghost pic
    gf = rom[H_GETFRONTPIC:H_GETFRONTPIC + 4]; assert gf[0] == 0xD5 and gf[1] == 0xCD
    a = Asm(sp.here(0x14))
    # run the original routine (pic decompressed and copied as usual, hl = destination on return),
    # then overwrite the 7x7 tiles with the ghost
    a.db(0xCD); a.dw('orig')
    a.db(0xE5, 0xF0, 0x70, 0xF5, 0x3E, 0x01, 0xE0, 0x70)            # push hl ; WRAM bank 1 (wram vars)
    farcall(a, 'gpic')
    a.db(0xC1, 0x78, 0xE0, 0x70, 0xE1, 0xD0)                        # restore WRAM bank ; pop hl ; ret nc
    a.db(0xE5, 0x11); a.dw(a_pic); a.db(0x06, 0x78, 0x0E, 49, 0xCD); a.dw(GET2BPP); a.db(0xE1, 0xC9)
    a.label('orig'); a.raw(gf); a.db(0xC3); a.dw(bank_addr(H_GETFRONTPIC) + 4)
    b14 = a.base; blob = a.done(); assert sp.put(0x14, blob) == b14
    rom[H_GETFRONTPIC] = 0xC3; w16(H_GETFRONTPIC + 1, b14)

    # ---- bank 02: ghost colours
    assert rom[H_ENEMYPAL:H_ENEMYPAL + 3] == bytes([0xFA, W_TEMPENEMYSPECIES & 0xFF, W_TEMPENEMYSPECIES >> 8])
    a = Asm(sp.here(0x02))
    # same as the Pikachu full-color hack: the real species' colours (its table = Gen II palettes),
    # never the shiny ones (Gen I has none)
    farcall(a, 'isghost'); a.db(0x30, 0x03, 0x01); a.dw('dv0')
    a.db(0xFA); a.dw(W_TEMPENEMYSPECIES); a.db(0xC9)
    a.label('dv0'); a.db(0x00, 0x00)
    b02 = a.base; blob = a.done(); assert sp.put(0x02, blob) == b02
    rom[H_ENEMYPAL] = 0xCD; w16(H_ENEMYPAL + 1, b02)
    log.append('ghost battle hooks (palette: species, non-shiny): 78:%04X, 0F:%04X, 0D:%04X, 03:%04X, 13:%04X, 14:%04X, 02:%04X'
               % (base, b0f, b0d, b03, b13, b14, b02))

    # ================= trainer data -> bank 0x7E
    if not os.environ.get("NOREL"): relocate_trainers(rom, log)

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    print('\n'.join(log))


if __name__ == '__main__':
    main()


# ---------------- helpers for later phases: trainer parties in bank 0x7E
TG7E = 0x45B3; ATTR7E = TG7E + 2 * NCLS
HOOK7E = 0x7F80                     # 7E:7F80-7FFF reserved for small hooks (phase 17)


def _areas():
    lo, hi = TR_CODE
    xs = bank_addr(lo); xe = xs + (hi - lo)
    return [(ATTR7E + NCLS * 7, xs), (xe, HOOK7E)]


def read_groups7e(rom):
    base = TR_BANK * 0x4000 - 0x4000
    starts = [rom[base + TG7E + 2 * i] | rom[base + TG7E + 2 * i + 1] << 8 for i in range(NCLS)]
    bounds = sorted(set(starts + [e for _, e in _areas()]))
    groups = []
    for gi, s in enumerate(starts):
        end = min(b for b in bounds if b > s)
        if s in starts[gi + 1:]:                   # empty group sharing its start with the next one
            groups.append([]); continue
        o = base + s; parties = []
        while o < base + end and rom[o] != 0:
            e = rom.index(0x50, o); name = bytes(rom[o:e + 1]); o = e + 1
            t = rom[o]; q = o + 1
            while rom[q] != 0xFF:
                q += P10.ESZ[t]
            parties.append([name, bytes(rom[o:q + 1])]); o = q + 1
        groups.append(parties)
    return groups


def write_groups7e(rom, groups):
    base = TR_BANK * 0x4000 - 0x4000
    areas = _areas()
    for a, e in areas:
        rom[base + a:base + e] = bytes(e - a)
    cur = [a for a, _ in areas]
    for i, g in enumerate(groups):
        bl = b''.join(nm + d for nm, d in g)
        for k, (a, e) in enumerate(areas):
            if cur[k] + len(bl) <= e:
                o = cur[k]; cur[k] += len(bl); break
        else:
            raise AssertionError('trainer bank full')
        rom[base + o:base + o + len(bl)] = bl
        rom[base + TG7E + 2 * i] = o & 0xFF; rom[base + TG7E + 2 * i + 1] = o >> 8
    return sum(e - c for (a, e), c in zip(areas, cur))
