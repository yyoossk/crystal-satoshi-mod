#!/usr/bin/env python3
"""Phase 28: Red's Safari Zone (ported from the Pikachu full-color hack / Red), for good:
 * The gate at the top of Fuchsia City (Crystal's closed door opens): ¥500 for 30 Safari Balls and 500 steps,
   the worker who explains the game, leaving early, the PA ("ding-dong") when the steps or the balls are used up.
 * Center / East / North / West areas, their rest houses, the secret house (HM03 Surf), Red's items, signs and
   wild Pokémon (Red version), Red's fishing there (Super Rod: Dratini / Krabby / Psyduck / Slowpoke).
 * The Safari battle (Ball / Bait / Rock / Run, Red's catch and flee rules, no Pokémon sent out): the battle loop is
   taken from the Safari Zone of a JP Crystal hack the user provided (its texts are Red's).
 * The warden (Crystal's warden's home): Red's Gold Teeth (new key item, found in the West area) for HM04 Strength.
   The worker of Crystal's Safari Zone office in Fuchsia no longer gives HM03 (Red: from the secret house).
 * Start menu: the remaining steps and Safari Balls during the game.
usage: build_phase28.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
import portmaps as PM
import pairwalls
import redmap as RM
import redtexts as RT
import build_phase10 as P10
import build_phase12 as P12
import build_phase14 as P14
import build_phase15 as P15
import build_phase17 as P17
import build_phase25 as P25
import build_phase27 as P27

P15.TS_CAP = P27.TS_CAP
FIRST_FLAG = 240                   # 229-239: phase 27
FIRST_MAP = 87                     # 26:81-86 = phase 27
BANK, BANK2, SAF = 0x6C, 0x6D, 0x6E   # free in the JP original (SAF: the Safari engine, ref layout)
REF = SC + '/safref/ref.gbc'       # the user's JP Crystal hack with a Safari Zone (bank 0x74: battle loop + texts)
REF_BANK = 0x74
REF_COPY = [(0x62E4, 0x6307), (0x6826, 0x68FF), (0x6A03, 0x6A35), (0x7400, 0x76C7), (0x7800, 0x7844)]
IN_SAFARI = 0x7140                 # the ref's "in the Safari Zone?" (carry) -- ours, same address
GATE_TS, FOREST_TS, LAB_TS = 47, 49, 42
GOLD_TEETH = 0x95                  # unused item slot -> key item きんのいれば
HM03, HM04 = 0xF5, 0xF6
W_STATUS2, W_BATTLE_TYPE, W_MAP_GROUP, W_MAP_NUMBER = 0xD840, 0xD261, 0xDC7B, 0xDC7C
W_BALLS, W_STEPS, W_SCRIPT_VAR = 0xDC3F, 0xDC40, 0xC2DD
W_WILD_MON, W_WOBBLES = 0xC644, 0xC6F1
BT_SAFARI = 0x0D
SFX_DING = 0x27                    # SFX_ELEVATOR_END: the PA
SPECIAL_MONEY = 0x51               # PlaceMoneyTopRight (US 0x52)
# hooks (JP Crystal, unchanged by the earlier phases)
H_BATTLE = 0x3C05A                 # 0F:405A  ld a, [wBattleType]          (DoBattle, wild)
H_STEP = 0x96B79                   # 25:6B79  ld a, [$C2DC]                (CountStep)
H_WOBBLE = 0xFE8D                  # 03:7E8D  ld a,[wWildMon]/and a/ld c,0/jr nz (ball wobbles)
H_FISH = 0xD1F3                    # 03:51F3  farcall 24:6975 (Fish)
H_MENU = [(0x127C0, 'fa40d8e606c8'), (0x127CD, 'fa40d8e60620')]   # 04:67C0 / 67CD: bug contest box -> also Safari
H_MENU_BOX, H_MENU_PRINT = 0x24BF6, 0x24C01                       # 09:4BF6 ld hl,$C4A0 / 09:4C01 ld hl,$CFC0
HIDE_ENEMY = 0x3FFE0               # 0F:7FE0 (the ref's helper, same place)
FUCHSIA_DOOR = (9, 1)              # Crystal's gate building wall (18,3): no door -> Red's door
KANTO_TS = 3
SCENE_GATE, SCENE_AREAS = 0xDA5E, 0xDA5D   # scene bytes (end of the extended flags' WRAM)
FUCHSIA_GATE_WARP = 7              # Crystal's (inaccessible) Fuchsia warp at (18,3)
SAFARI_WORKER_SPRITE = 0x12D50     # PKFC SafariZoneWorkerSprite (12 tiles, standing)
SPR = dict(P27.SPR)
MAPS = [('SafariZoneGate', 0x9C, 'Gate'), ('SafariZoneCenter', 0xDC, 'Forest'), ('SafariZoneCenterRestHouse', 0xDD, 'Gate'),
        ('SafariZoneEast', 0xD9, 'Forest'), ('SafariZoneEastRestHouse', 0xE0, 'Gate'),
        ('SafariZoneNorth', 0xDA, 'Forest'), ('SafariZoneNorthRestHouse', 0xE1, 'Gate'),
        ('SafariZoneWest', 0xDB, 'Forest'), ('SafariZoneWestRestHouse', 0xDF, 'Gate'),
        ('SafariZoneSecretHouse', 0xDE, 'Lab')]
CONST = {'SAFARI_ZONE_GATE': 'SafariZoneGate', 'SAFARI_ZONE_CENTER': 'SafariZoneCenter',
         'SAFARI_ZONE_CENTER_REST_HOUSE': 'SafariZoneCenterRestHouse', 'SAFARI_ZONE_EAST': 'SafariZoneEast',
         'SAFARI_ZONE_EAST_REST_HOUSE': 'SafariZoneEastRestHouse', 'SAFARI_ZONE_NORTH': 'SafariZoneNorth',
         'SAFARI_ZONE_NORTH_REST_HOUSE': 'SafariZoneNorthRestHouse', 'SAFARI_ZONE_WEST': 'SafariZoneWest',
         'SAFARI_ZONE_WEST_REST_HOUSE': 'SafariZoneWestRestHouse', 'SAFARI_ZONE_SECRET_HOUSE': 'SafariZoneSecretHouse'}
AREAS = ['SafariZoneCenter', 'SafariZoneEast', 'SafariZoneNorth', 'SafariZoneWest']
GEN1_TM_NO = {'TM_EGG_BOMB': 37, 'TM_SKULL_BASH': 40, 'TM_DOUBLE_TEAM': 32}
FOREST_WATER = (0x14, 0x48, 0x32)
SUPER_ROD = [(15, 147), (15, 98), (15, 54), (15, 79)]     # Red .Group6: Dratini, Krabby, Psyduck, Slowpoke
# JP Red texts (text_far bodies)
T = dict(welcome=0x7551C, would=0x7552D, pay1=0x755EE, pay2=0x7564B, again=0x75688, poor=0x7569A, leave=0x756A9,
         ret_balls=0x756FE, luck=0x75719, haul=0x75724, first=0x75764, explain=0x7577B, regular=0x757FB,
         timesup=0x1FAB9, gameover=0x1FAD2,
         w_gib1=0x751C5, w_gib2=0x751F8, w_gib3=0x75215, w_gave=0x75233, w_popped=0x7524E, w_thanks=0x75268,
         w_recv1=0x752D4, w_recv2=0x752E4, w_expl=0x752EF, w_full=0x75384)


def jp(o):
    """a JP Red text body (from its {00}) up to and with its terminator, as Crystal text"""
    b = RT.raw(o); t = RT.R[o + len(b)]
    return b + bytes([0x57 if t == 0x50 else t])          # a text_far followed by text_asm in Red: end it here


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    ref = open(REF, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (0x03, 0x05, 0x09, 0x0B, 0x0F, 0x25, 0x0A, BANK, BANK2):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1 if f > b * 0x4000 else f, b * 0x4000 + 0x4000)
    runs = []; i = fo(0x13, 0x7900)
    while i < fo(0x13, 0x8000):
        if rom[i] == 0:
            j = i
            while j < fo(0x13, 0x8000) and rom[j] == 0: j += 1
            runs.append((j - i, i, j)); i = j
        else: i += 1
    n_, g0, g1 = max(runs); sp.set_area(0x13, g0 + 1, g1)
    log = []
    FL = PM.Flags(FIRST_FLAG)
    fuchsia = mapid('FuchsiaCity')
    mapids = {n: (G26, FIRST_MAP + i) for i, (n, g, tk) in enumerate(MAPS)}
    TS = PM.Tilesets(rom, sp)
    got_hm03, got_hm04, gave_teeth, game_over = FL.new(), FL.new(), FL.new(), FL.new()

    # ================= the Safari Zone worker's sprite (PKFC), one more entry in phase 14's second table
    stubs = []
    for off, d in P14.OW_READERS:
        assert rom[off] == 0xCD; s_ = fo(0x05, r16(off + 1))
        assert rom[s_:s_ + 2] == bytes([0xFE, 0x67]) and rom[s_ + 8] == 0x21
        stubs.append((s_, d))
    virt = r16(stubs[0][0] + 9) - stubs[0][1]
    t2 = virt + 0x66 * 6; n2 = len(P14.NEW_SPRITES) + 1                   # + phase 26's Old Amber
    tab = bytes(rom[fo(0x05, t2):fo(0x05, t2) + 6 * n2])
    pk = open(P10.PKFC, 'rb').read()
    ga = sp.put(BANK2, pk[SAFARI_WORKER_SPRITE:SAFARI_WORKER_SPRITE + 12 * 16])
    tab += bytes([ga & 0xFF, ga >> 8, 0xC0, BANK2, 2, 2])
    nt = sp.put(0x05, tab); nv = nt - 0x66 * 6
    for s_, d in stubs: w16(s_ + 9, nv + d)
    SPR['SPRITE_SAFARI_ZONE_WORKER'] = 0x67 + n2
    log.append('Safari Zone worker sprite -> id %02X' % SPR['SPRITE_SAFARI_ZONE_WORKER'])

    # ================= the Safari engine (bank SAF): the ref's battle loop / texts / start menu box at their places
    for lo_, hi_ in REF_COPY:
        rom[fo(SAF, lo_):fo(SAF, hi_)] = ref[fo(REF_BANK, lo_):fo(REF_BANK, hi_)]
    for a_ in (0x75A7, 0x75AA):                                  # the battle menu's dba (strings / ball count)
        assert rom[fo(SAF, a_)] == REF_BANK; rom[fo(SAF, a_)] = SAF
    # the ref's own bait / rock animations (ids $16E1 / $16E2) don't exist here (Crystal's move animations leave the
    # screen broken without a Pokémon sent out): the throw is shown by its text only
    o_ = fo(SAF, 0x752B); assert rom[o_:o_ + 6] == bytes([0x3E, 0x33, 0x21, 0xE5, 0x40, 0xCF]); rom[o_:o_ + 6] = bytes(6)
    o_ = fo(SAF, 0x757A); assert rom[o_:o_ + 6] == bytes([0x3E, 0x0F, 0x21, 0xE0, 0x7F, 0xCF])   # farcall 0F:7FE0
    def far(bank, addr): return bytes([0x3E, bank, 0x21, addr & 0xFF, addr >> 8, 0xCF])
    # ---- carry if the current map is one of the Safari Zone's (areas, rest houses, secret house; not the gate)
    a = JAsm(IN_SAFARI); a.bank = SAF
    a.db(0xFA); a.dw(W_MAP_GROUP); a.db(0xFE, G26); a.jr(0x20, 'no')
    a.db(0xFA); a.dw(W_MAP_NUMBER); a.db(0xD6, FIRST_MAP + 1, 0xFE, len(MAPS) - 1, 0xC9)
    a.label('no'); a.db(0xA7, 0xC9)
    blob = a.fin(); assert IN_SAFARI + len(blob) <= 0x7400
    rom[fo(SAF, IN_SAFARI):fo(SAF, IN_SAFARI) + len(blob)] = blob
    sa = JAsm(0x5000); sa.bank = SAF
    # ---- one step (CountStep): steps -1 during the game in the Safari Zone
    sa.label('step')
    sa.db(0xFA); sa.dw(W_STATUS2); sa.db(0xCB, 0x4F, 0xC8)                             # bit 1 / ret z
    sa.db(0xCD); sa.dw(IN_SAFARI); sa.db(0xD0)                                          # ret nc
    sa.db(0x21); sa.dw(W_STEPS); sa.db(0x2A, 0xB6, 0xC8)                                # ld a,[hl+]; or [hl]; ret z
    sa.db(0x7E, 0xD6, 0x01, 0x32, 0x7E, 0xDE, 0x00, 0x77, 0xC9)                         # 16-bit (big endian) -1
    # ---- ball wobbles (03:7E8D, c = wobble number): Red's count (the ref's) in a Safari battle
    sa.label('wobble')
    sa.db(0xFA); sa.dw(W_BATTLE_TYPE); sa.db(0xFE, BT_SAFARI); sa.jr(0x20, 'wb_n')
    sa.db(0xFA); sa.dw(W_WOBBLES); sa.db(0xB9, 0x0E, 0x00); sa.jr(0x30, 'wb_k'); sa.db(0x0E, 0x02)
    sa.label('wb_k'); sa.db(0xF6, 0x01, 0xC9)
    sa.label('wb_n'); sa.db(0xFA); sa.dw(W_WILD_MON); sa.db(0xA7, 0x0E, 0x00, 0xC9)
    # ---- fishing (03:51F3): Red's rods in the Safari Zone (d = fishing group, e = rod; out d = species, e = level)
    sa.label('fish')
    sa.db(0xCD); sa.dw(IN_SAFARI); sa.jr(0x38, 'f_saf')
    sa.raw(far(0x24, 0x6975)); sa.db(0xC9)                                              # farcall Fish
    sa.label('f_saf'); sa.db(0x7B, 0xA7); sa.jr(0x28, 'f_old'); sa.db(0x3D); sa.jr(0x28, 'f_good')
    sa.db(0xCD, 0x5E, 0x2F, 0xE6, 0x03, 0x87, 0x5F, 0x16, 0x00, 0x21); sa.dw('rodtab')   # Super Rod: Red's .Group6
    sa.db(0x19, 0x5E, 0x23, 0x56, 0xC9)                                                 # e = level, d = species
    sa.label('f_old'); sa.db(0x11, 0x05, 0x81, 0xC9)                                    # Magikarp Lv 5
    sa.label('f_good'); sa.db(0xCD, 0x5E, 0x2F, 0xCB, 0x3F); sa.jr(0x38, 'f_none')
    sa.db(0xE6, 0x03, 0xFE, 0x02); sa.jr(0x30, 'f_good')
    sa.db(0x11, 0x0A, 0x76, 0xA7, 0xC8, 0x11, 0x0A, 0x3C, 0xC9)                         # Goldeen / Poliwag Lv 10
    sa.label('f_none'); sa.db(0x16, 0x00, 0xC9)                                         # no bite
    sa.label('rodtab')
    for lv, mon in SUPER_ROD: sa.db(lv, mon)
    # ---- map scene: game over when the steps or the balls are used up (wScriptVar = 1)
    sa.label('over')
    sa.db(0xAF, 0xEA); sa.dw(W_SCRIPT_VAR)
    sa.db(0xFA); sa.dw(W_STATUS2); sa.db(0xCB, 0x4F, 0xC8)
    sa.db(0xFA); sa.dw(W_BALLS); sa.db(0xA7); sa.jr(0x28, 'ov_y')
    sa.db(0x21); sa.dw(W_STEPS); sa.db(0x2A, 0xB6, 0xC0)
    sa.label('ov_y'); sa.db(0x3E, 0x01, 0xEA); sa.dw(W_SCRIPT_VAR); sa.db(0xC9)
    # ---- the game starts: 30 balls, 502 steps; ends: no balls
    sa.label('start')
    sa.db(0x21); sa.dw(W_STATUS2); sa.db(0xCB, 0xCE)                                     # set 1, [hl]
    sa.db(0x3E, 30, 0xEA); sa.dw(W_BALLS)
    sa.db(0x3E, 502 >> 8, 0xEA); sa.dw(W_STEPS); sa.db(0x3E, 502 & 0xFF, 0xEA); sa.dw(W_STEPS + 1); sa.db(0xC9)
    sa.label('stop')
    sa.db(0x21); sa.dw(W_STATUS2); sa.db(0xCB, 0x8E, 0xAF, 0xEA); sa.dw(W_BALLS); sa.db(0xC9)
    blob = sa.fin(); rom[fo(SAF, 0x5000):fo(SAF, 0x5000) + len(blob)] = blob
    L = sa.labels; LBL.update(L)

    # ================= hooks
    # battle start (bank 0F)
    assert rom[H_BATTLE:H_BATTLE + 3] == bytes([0xFA, 0x61, 0xD2])
    b0 = JAsm(sp.here(0x0F)); b0.bank = 0x0F
    b0.db(0xFA); b0.dw(W_BATTLE_TYPE); b0.db(0xFE, BT_SAFARI); b0.jr(0x28, 'go')
    b0.db(0xA7); b0.jr(0x28, 'chk'); b0.db(0xFE, 0x04, 0xC0)                            # normal or fishing, else ret
    b0.label('chk'); b0.db(0xFA); b0.dw(W_STATUS2); b0.db(0xCB, 0x4F); b0.jr(0x28, 'r0')
    b0.raw(far(SAF, IN_SAFARI)); b0.jr(0x30, 'r0')
    b0.db(0x3E, BT_SAFARI, 0xEA); b0.dw(W_BATTLE_TYPE)
    b0.label('go'); b0.db(0xE1); b0.raw(far(SAF, 0x7400)); b0.db(0xC9)                  # instead of the battle
    b0.label('r0'); b0.db(0xFA); b0.dw(W_BATTLE_TYPE); b0.db(0xC9)
    stub = b0.base; blob = b0.fin(); assert sp.put(0x0F, blob) == stub
    assert stub + len(blob) <= HIDE_ENEMY
    rom[H_BATTLE] = 0xCD; w16(H_BATTLE + 1, stub)
    # helper of the ref's loop: hide the enemy picture (0F:7FE0)
    assert not any(rom[HIDE_ENEMY:HIDE_ENEMY + 8])
    rom[HIDE_ENEMY:HIDE_ENEMY + 8] = bytes([0x21, 0xB2, 0xC4, 0x3E, 0x08, 0xC3, 0x83, 0x54])
    # one step (bank 25)
    assert rom[H_STEP:H_STEP + 3] == bytes([0xFA, 0xDC, 0xC2])
    s25 = sp.put(0x25, far(SAF, L['step']) + bytes([0xFA, 0xDC, 0xC2, 0xC9]))
    rom[H_STEP] = 0xCD; w16(H_STEP + 1, s25)
    # wobbles (bank 3): ld c, a / farcall
    assert rom[H_WOBBLE:H_WOBBLE + 8] == bytes.fromhex('fa44c6a70e002025')
    s3 = sp.put(0x03, bytes([0x4F]) + far(SAF, L['wobble']) + b'\xc9')
    rom[H_WOBBLE:H_WOBBLE + 8] = bytes([0xCD, s3 & 0xFF, s3 >> 8, 0x20, 0x28, 0, 0, 0])
    # fishing
    assert rom[H_FISH:H_FISH + 6] == far(0x24, 0x6975)
    rom[H_FISH:H_FISH + 6] = far(SAF, L['fish'])
    # start menu: the status box also during the Safari game
    for o_, new in H_MENU:
        assert rom[o_:o_ + 5] == bytes([0x21, 0x40, 0xD8, 0xCB, 0x56]); rom[o_:o_ + 6] = bytes.fromhex(new)
    for o_, orig3 in ((H_MENU_BOX, bytes([0x21, 0xA0, 0xC4])), (H_MENU_PRINT, bytes([0x21, 0xC0, 0xCF]))):
        assert rom[o_:o_ + 3] == orig3
        s9 = sp.put(0x09, bytes([0xFA, W_STATUS2 & 0xFF, W_STATUS2 >> 8, 0xCB, 0x4F, 0x20, 0x04]) + orig3 + b'\xc9' +
                    bytes([0xE1]) + far(SAF, 0x7800) + b'\xc9')
        rom[o_] = 0xCD; w16(o_ + 1, s9)
    log.append('Safari engine %X (hooks 0F:%04X 25:%04X 03:%04X)' % (SAF, stub, s25, s3))

    # ================= Gold Teeth (key item)
    nb = rom[P12.ITEMNAMES_PTR]; o = fo(nb, r16(P12.ITEMNAMES_PTR + 1)); names = []
    for i in range(256):
        e_ = rom.index(0x50, o); names.append(bytes(rom[o:e_ + 1])); o = e_ + 1
    names[GOLD_TEETH - 1] = encode('きんのいれば@')
    an = sp.put(BANK, b''.join(names)); rom[P12.ITEMNAMES_PTR] = BANK; w16(P12.ITEMNAMES_PTR + 1, an)
    rom[P12.ITEMATTR + 7 * (GOLD_TEETH - 1):P12.ITEMATTR + 7 * GOLD_TEETH] = rom[P12.ITEMATTR + 7 * (P25.SECRET_KEY - 1):][:7]
    w16(P12.ITEMDESC + 2 * (GOLD_TEETH - 1), sp.put(0x0B, encode('サファりゾーンの　えんちょうが<NEXT>なくした　いれば@')))

    # ================= tilesets: Gate / Forest / Lab variant blocks for the warps of the new maps
    tss = {'Gate': Tileset('Gate', 12, 'gate.bst', SC + '/out/pk_gate.pkl'),
           'Forest': Tileset('Forest', 3, 'forest.bst', SC + '/out/pk_forest.pkl', grass=0x20),
           'Lab': Tileset('Lab', 20, 'lab.bst', SC + '/out/pk_lab.pkl')}
    ts_id = {'Gate': GATE_TS, 'Forest': FOREST_TS, 'Lab': LAB_TS}
    maps = {}; objs_of = {}
    for n, g, tk in MAPS:
        h = RM.header(g); maps[n] = MapPort(n, tss[tk], h['w'], h['h'], n + '.blk')
        objs_of[n] = P25.red_objects(n)
    ov = {n: {(x, y): P25.warp_override(maps[n].ts, maps[n], x, y) for x, y, d, w in objs_of[n][1]} for n in maps}
    for tk in ('Gate', 'Forest', 'Lab'):
        ts = tss[tk]; e = TS.entry(ts_id[tk])
        am_, ac_ = e[4] | e[5] << 8, e[7] | e[8] << 8
        nb0 = (ac_ - am_) // 16
        meta = bytes(rom[fo(e[3], am_):fo(e[3], am_) + 16 * nb0]); coll = bytes(rom[fo(e[6], ac_):fo(e[6], ac_) + 4 * nb0])
        assert meta[:16 * ts.nblocks] == bytes(ts.blocks)
        mm = {n: maps[n] for n, g, k in MAPS if k == tk}
        wt = (0x14,)
        if tk == 'Forest':                    # Red: water ($14) and its shore tiles ($48 / $32) can be surfed / fished
            wt = FOREST_WATER; coll = bytearray(coll)
            for b_ in range(nb0):
                for q in range(4):
                    r_, c_ = ((1, 0), (1, 2), (3, 0), (3, 2))[q]
                    if meta[16 * b_ + 4 * r_ + c_] in FOREST_WATER: coll[4 * b_ + q] = COLL_WATER
            coll = bytes(coll); ts.coll = bytearray(coll[:4 * ts.nblocks])
        meta2, coll2, blks = pairwalls.variants(ts, meta, coll, mm, P27.FOREST_PAIRS if tk == 'Forest' else [],
                                                {n: ov[n] for n in mm}, water_tiles=wt)
        if tk == 'Gate':                      # Crystal's block 0 = wall (the rest house floor): a copy
            meta2, coll2, blks = P27.block0_copy(meta2, coll2, blks)
        assert len(coll2) // 4 <= 256
        am = sp.put(BANK2, meta2 + coll2); ac = am + len(meta2)
        t0 = TS.tab + 15 * ts_id[tk]
        rom[t0 + 3] = BANK2; w16(t0 + 4, am); rom[t0 + 6] = BANK2; w16(t0 + 7, ac)
        for n in mm: maps[n].blk = blks[n]
        log.append('tileset %s: %d blocks (+%d)' % (tk, len(coll2) // 4, len(coll2) // 4 - nb0))

    def rt(g, tid):
        b, p = RM.text_ptr(g, tid); k, v = RM.text_body(b, p)
        if k == 'text': return RM.crystal_text(b, p)
        return hl(g, tid)[0]
    def hl(g, tid, **kw):
        return [RM.crystal_text(b, p) for b, p in RM.asm_hl(g, tid, **kw) if RM.R[RM.fo(b, p)] in (0x00, 0x17)]
    # ================= headers 26:87-96 (move what lies there)
    u = US.get(); G = u.groups()
    lo, hi = GROUP26_END + 9 * (FIRST_MAP - G26_COUNT - 1), GROUP26_END + 9 * (FIRST_MAP - G26_COUNT - 1 + len(MAPS))
    for gi in range(26):
        n_ = (G[gi + 1] - G[gi]) // 9 if gi + 1 < 26 else FIRST_MAP - 1
        for k in range(n_):
            hdr = G[gi] + 9 * k
            if not rom[hdr]: continue
            ab = rom[hdr]; ap = r16(hdr + 3); ao_ = fo(ab, ap)
            nconn = bin(rom[ao_ + 11] & 0xF).count('1'); size = 12 + 12 * nconn
            if ao_ < hi and ao_ + size > lo:
                rom[hdr] = BANK; w16(hdr + 3, sp.put(BANK, bytes(rom[ao_:ao_ + size])))
                log.append('moved map attributes %X:%04X' % (ab, ap))
    rom[lo:hi] = bytes(hi - lo)

    hof = hdr_index('SafariZoneMainOffice'); hpark = hdr_index('NationalPark')
    gate = mapids['SafariZoneGate']; center = mapids['SafariZoneCenter']
    for n, g, tk in MAPS:
        objs, warps, bgl = objs_of[n]
        a = Asm(sp.here(BANK)); a.bank = BANK; texts = {}; obj_bytes = []; bgs = []; coords = []; scenes = []
        a.label('end'); a.end()
        for idx, o in enumerate(objs):
            tid = idx + 1; lab = 'o%d' % tid; fl = 0xFFFF; typ = 0
            mv, rng = P25.face((0, 0, 0, o['move'], o['face']))
            spr = SPR[o['sprite']]
            if o['sprite'] == 'SPRITE_POKE_BALL':
                it = o['extra'][0]
                iid = GOLD_TEETH if it == 'GOLD_TEETH' else PM.item_id(it)
                typ = 1; fl = FL.new(); a.label(lab); a.db(iid, 1)
            elif n == 'SafariZoneGate' and tid == 2:
                a.label(lab); a.faceplayer(); a.opentext(); a.writetext('g_first'); a.yesorno(); a.iffalse(lab + 'r')
                a.writetext('g_explain'); a.waitbutton(); a.closetext(); a.end()
                a.label(lab + 'r'); a.writetext('g_regular'); a.waitbutton(); a.closetext(); a.end()
            elif n == 'SafariZoneGate' and tid == 1:
                a.label(lab); a.jumptextfaceplayer('g_welcome')
            elif n == 'SafariZoneSecretHouse':
                hm03 = b'\x00' + encode('ひでんマシン03').rstrip(b'\x50') + b'\x50'
                texts.update(sh_won=jp(0x4BE69), sh_expl=jp(0x4BEFB), sh_full=jp(0x4BF71),
                             sh_recv=RT.raw(0x4BEDF) + b'\x50' + hm03 + RT.raw(0x4BEF0) + b'\x50\x0f\x50')
                a.label(lab); a.faceplayer(); a.opentext(); a.checkevent(got_hm03); a.iftrue(lab + 'g')
                a.writetext('sh_won'); a.db(0x1F, HM03, 1); a.iffalse(lab + 'f')
                a.writetext('sh_recv'); a.waitbutton(); a.setevent(got_hm03); a.closetext(); a.end()
                a.label(lab + 'f'); a.writetext('sh_full'); a.waitbutton(); a.closetext(); a.end()
                a.label(lab + 'g'); a.writetext('sh_expl'); a.waitbutton(); a.closetext(); a.end()
            else:
                a.label(lab); a.jumptextfaceplayer(lab + 't'); texts[lab + 't'] = rt(g, tid)
            obj_bytes.append([spr, o['y'] + 4, o['x'] + 4, mv, rng, 0xFF, 0xFF, typ, 0, lab, fl])
        for k, (x, y, tconst) in enumerate(bgl):
            L_ = 'bg%d' % k; a.label(L_); a.jumptext(L_ + 't'); texts[L_ + 't'] = rt(g, len(objs) + k + 1)
            bgs.append((y, x, 0, L_))
        for k, (x, y, fn, arg) in enumerate(P25.hidden(PM.map_const(n))):
            if fn != 'HiddenItems': continue                         # rest houses: Red's leftover bench / PC
            if x >= maps[n].w * 2 or y >= maps[n].h * 2: continue    # the gate's nugget: outside the map in Red
            L_ = 'hi%d' % k; a.label(L_); a.dw(FL.new()); a.db(PM.item_id(arg)); bgs.append((y, x, 7, L_))
        if n == 'SafariZoneGate':
            safari_gate(a, texts, coords, scenes, game_over, mapids)
        else:
            # game over: the PA, the texts, back to the gate
            a.label('scene0'); a.callasm(SAF, L['over']); a.iffalse('end')
            a.db(0x7E, 0, 0)                                                     # playmusic MUSIC_NONE
            a.playsound(SFX_DING); a.waitsfx()
            a.opentext(); a.readmem(W_BALLS); a.iffalse('go_b'); a.writetext('go_t'); a.waitbutton()
            a.label('go_b'); a.writetext('go_o'); a.waitbutton(); a.closetext()
            a.setevent(game_over); a.warp(*gate, 3, 0); a.end()
            texts['go_t'] = jp(T['timesup']); texts['go_o'] = jp(T['gameover'])
            scenes.append('scene0')
        for k_, v in texts.items():
            a.label(k_); a.raw(v if v[-1] in (0x50, 0x57, 0x58) else P12.text(v))
        a.label('mapscripts'); a.db(len(scenes))
        for s_ in scenes: a.dw(s_); a.dw(0)
        a.db(0)
        a.label('events'); a.db(0, 0)
        wl = []
        for x, y, dest, wid in warps:
            if dest == 'LAST_MAP': wl.append((y, x, FUCHSIA_GATE_WARP, *fuchsia))
            else: wl.append((y, x, wid, *mapids[CONST[dest]]))
        a.db(len(wl))
        for w_ in wl: a.db(*w_)
        a.db(len(coords))
        for (sc, y_, x_, l_) in coords: a.db(sc, y_, x_, 0); a.dw(l_); a.db(0, 0)
        a.db(len(bgs))
        for (y_, x_, t_, l_) in bgs: a.db(y_, x_, t_); a.dw(l_)
        a.db(len(obj_bytes))
        for ob in obj_bytes: a.db(*ob[:9]); a.dw(ob[9]); a.dw(ob[10])
        base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
        mp = maps[n]; blkp = sp.put(BANK, mp.blk)
        aa = sp.put(BANK, bytes([0x0A if tk != 'Forest' else 0x00, mp.h, mp.w, BANK, blkp & 0xFF, blkp >> 8, BANK,
                                 a.labels['mapscripts'] & 0xFF, a.labels['mapscripts'] >> 8, a.labels['events'] & 0xFF,
                                 a.labels['events'] >> 8, 0]))
        hh = GROUP26_END + 9 * (mapids[n][1] - G26_COUNT - 1)
        if tk == 'Forest':
            hdr = [BANK, ts_id[tk], 6, aa & 0xFF, aa >> 8, rom[hof + 5], rom[hpark + 6], 0x01, rom[hof + 8]]
        else:
            hdr = [BANK, ts_id[tk], 6 if tk == 'Gate' else 3, aa & 0xFF, aa >> 8, rom[hof + 5], rom[hof + 6], rom[hof + 7],
                   rom[hof + 8]]
        rom[hh:hh + 9] = bytes(hdr)
        log.append('%s -> map %d:%d  scripts %X:%04X (%d bytes)' % (n, *mapids[n], BANK, base, len(blob)))

    # ================= Fuchsia City: the gate's door opens, its warp leads to Red's gate
    # (Crystal's Kanto tileset gets one block: the building's wall 0x7D with Red's door at its bottom left)
    e = TS.entry(KANTO_TS); mo_, co_ = fo(e[3], e[4] | e[5] << 8), fo(e[6], e[7] | e[8] << 8)
    assert (co_ - mo_) // 16 == 128
    meta = bytearray(rom[mo_:mo_ + 16 * 128]); coll = bytearray(rom[co_:co_ + 4 * 128])
    door = bytearray(meta[16 * 0x7D:16 * 0x7E]); door[8:10] = bytes([0x0B, 0x0C]); door[12:14] = bytes([0x1B, 0x1C])
    assert bytes(meta[16 * 0x3A + 8:16 * 0x3A + 10]) == bytes([0x0B, 0x0C])
    dc = bytearray(coll[4 * 0x7D:4 * 0x7E]); dc[2] = 0x71                               # COLL_DOOR
    am = sp.put(BANK2, bytes(meta) + bytes(door) + bytes(coll) + bytes(dc))
    t0 = TS.tab + 15 * KANTO_TS
    rom[t0 + 3] = BANK2; w16(t0 + 4, am); rom[t0 + 6] = BANK2; w16(t0 + 7, am + 16 * 129)
    af = attrs(rom, hdr_index('FuchsiaCity')); bx, by = FUCHSIA_DOOR
    o_ = fo(af['blkbank'], af['blk']) + by * af['w'] + bx; assert rom[o_] == 0x7D; rom[o_] = 128
    ev = parse_events(rom, af['scbank'], af['events'])
    o_, w = ev['warps'][FUCHSIA_GATE_WARP - 1]; assert (w[0], w[1]) == (3, 18)
    rom[o_ + 2] = 1; rom[o_ + 3:o_ + 5] = bytes(gate)

    # ================= the warden (Crystal's warden's home): Red's Gold Teeth -> HM04
    a = Asm(sp.here(BANK)); a.bank = BANK; texts = {}
    a.label('wd'); a.faceplayer(); a.opentext(); a.checkevent(got_hm04); a.iftrue('wd_g')
    a.checkitem(GOLD_TEETH); a.iftrue('wd_t'); a.checkevent(gave_teeth); a.iftrue('wd_th')
    a.writetext('wd1'); a.yesorno(); a.iffalse('wd_n')
    a.writetext('wd2'); a.waitbutton(); a.closetext(); a.end()
    a.label('wd_n'); a.writetext('wd3'); a.waitbutton(); a.closetext(); a.end()
    a.label('wd_t'); a.writetext('wd_gave'); a.db(0x20, GOLD_TEETH, 1); a.setevent(gave_teeth)        # takeitem
    a.label('wd_th'); a.writetext('wd_thx'); a.db(0x1F, HM04, 1); a.iffalse('wd_f')
    a.writetext('wd_recv'); a.waitbutton(); a.setevent(got_hm04); a.closetext(); a.end()
    a.label('wd_f'); a.writetext('wd_full'); a.waitbutton(); a.closetext(); a.end()
    a.label('wd_g'); a.writetext('wd_expl'); a.waitbutton(); a.closetext(); a.end()
    hm04 = b'\x00' + encode('ひでんマシン04').rstrip(b'\x50') + b'\x50'
    texts.update(wd1=jp(T['w_gib1']), wd2=jp(T['w_gib2']), wd3=jp(T['w_gib3']),
                 wd_gave=RT.raw(T['w_gave']) + b'\x50\x0f' + jp(T['w_popped']), wd_thx=jp(T['w_thanks']),
                 wd_recv=RT.raw(T['w_recv1']) + b'\x50' + hm04 + RT.raw(T['w_recv2']) + b'\x50\x0f\x50',
                 wd_expl=jp(T['w_expl']), wd_full=jp(T['w_full']))
    # the secret house's texts (Red): received HM03 / no room
    for k_, v in texts.items():
        a.label(k_); a.raw(v)
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    for n_, lab_ in (('SafariZoneWardensHome', 'wd'),):
        aw = attrs(rom, hdr_index(n_)); ev = parse_events(rom, aw['scbank'], aw['events'])
        o_, ob = ev['objs'][0]; p_ = fo(aw['scbank'], ob[9] | ob[10] << 8)
        assert rom[p_] == 0x04, n_                                      # farsjump (the base mod's)
        rom[p_ + 1] = BANK; w16(p_ + 2, a.labels[lab_])
    # Crystal's Safari Zone office in Fuchsia: no more HM03 there (Red's Fuchsia meeting room worker's line)
    ao = attrs(rom, hdr_index('SafariZoneMainOffice')); ev = parse_events(rom, ao['scbank'], ao['events'])
    o_, ob = ev['objs'][0]; p_ = fo(ao['scbank'], ob[9] | ob[10] << 8); assert rom[p_] == 0x04
    a2 = Asm(sp.here(BANK)); a2.bank = BANK
    a2.label('mo'); a2.jumptextfaceplayer('mot'); a2.label('mot'); a2.raw(rt(0x9E, 1))
    base = a2.base; blob = a2.done(); assert sp.put(BANK, blob) == base
    rom[p_ + 1] = BANK; w16(p_ + 2, base)

    # ================= scene bytes (map scene table): the gate (scene 0 / 1), the other maps share one (always 0)
    # (the last two bytes of the extended flags: flags 0x800+736.. stay unused)
    import build_phase21 as P21
    sr = P21.SCENES_REF
    tb = fo(rom[sr], r16(sr + 3)); n_ = 0
    while rom[tb + 4 * n_] != 0xFF: n_ += 1
    tab = bytes(rom[tb:tb + 4 * n_])
    for n, g, tk in MAPS:
        sb_ = SCENE_GATE if n == 'SafariZoneGate' else SCENE_AREAS
        tab += bytes([*mapids[n], sb_ & 0xFF, sb_ >> 8])
    assert rom[sr] == 0x61
    at = sp_put61(rom, tab + b'\xff')
    w16(sr + 3, at)
    rom[tb:tb + 4 * n_ + 1] = b'\xff' * (4 * n_ + 1)
    assert FL.i <= 0x800 + 8 * (SCENE_AREAS - 0xDA01) - 0x800 + 0x800 and FL.i < 8 * (SCENE_AREAS - 0xDA01)

    # ================= wild Pokémon (Red): the four areas
    kg = P27.kanto_grass(rom); p = kg; ents = []
    while rom[p] != 0xFF: ents.append(bytes(rom[p:p + 47])); p += 47
    end_old = p + 1
    def red_wild(name, mp):
        t = open(PR + '/data/wild/maps/%s.asm' % name, encoding='utf-8').read()
        t = re.sub(r'IF DEF\(_BLUE\).*?ENDC', '', t, flags=re.S)
        rate = int(re.search(r'def_grass_wildmons (\d+)', t).group(1))
        slots = [(int(l), s) for l, s in re.findall(r'db\s+(\d+), (\w+)', t.split('end_grass_wildmons')[0])]
        assert len(slots) == 10, name
        pick = [slots[i] for i in (0, 1, 2, 3, 6, 8, 9)]
        return bytes([*mp, rate, rate, rate]) + bytes(sum(([lv, PM.MON[P10.MON_ALIAS.get(s, s)]] for lv, s in pick), [])) * 3
    for n in AREAS: ents.append(red_wild(n, mapids[n]))
    blob = b''.join(ents) + b'\xff'
    assert all(v == 0 for v in rom[end_old:kg + len(blob)])
    rom[kg:kg + len(blob)] = blob

    P17.fix_outdoor_sprites(rom, log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


def sp_put61(rom, data):
    """the map scene table stays in bank 0x61 (GetMapSceneID switches to it): its free tail"""
    f, n = bank_free_tail(rom, 0x61); assert n > len(data) + 1, n
    rom[f + 1:f + 1 + len(data)] = data; return 0x4000 + (f + 1) % 0x4000


def safari_gate(a, texts, coords, scenes, game_over, mapids):
    """Red's SafariZoneGate scripts"""
    U, D, Rr = 0x0D, 0x0C, 0x0F
    gate, center = mapids['SafariZoneGate'], mapids['SafariZoneCenter']
    texts.update(g_welcome=jp(T['welcome']), g_would=jp(T['would']),
                 g_pay=RT.raw(T['pay1']) + b'\x50\x0f' + jp(T['pay2']), g_again=jp(T['again']), g_poor=jp(T['poor']),
                 g_leave=jp(T['leave']), g_ret=jp(T['ret_balls']), g_luck=jp(T['luck']), g_haul=jp(T['haul']),
                 g_first=jp(T['first']), g_explain=jp(T['explain']), g_regular=jp(T['regular']))
    # scene 0: in front of the counter (Red: (3,2) / (4,2))
    for x in (3, 4):
        L_ = 'c%d' % x; coords.append((0, 2, x, L_))
        a.label(L_); a.opentext(); a.writetext('g_welcome'); a.waitbutton(); a.closetext()
        if x == 3: a.applymovement(0, 'mv_r')
        a.sjump('ask')
    a.label('ask'); a.turnobject(0, 3)
    a.opentext(); a.special(SPECIAL_MONEY); a.writetext('g_would'); a.yesorno(); a.iffalse('no')
    a.db(0x24, 0, 0x00, 0x01, 0xF4); a.ifequal(2, 'poor')                   # checkmoney YOUR_MONEY, 500 ; HAVE_LESS
    a.db(0x23, 0, 0x00, 0x01, 0xF4); a.special(SPECIAL_MONEY)               # takemoney
    a.writetext('g_pay'); a.waitbutton(); a.closetext()
    a.callasm(SAF, LBL['start']); a.clearevent(game_over); a.db(0x14, 1)     # setscene 1
    a.applymovement(0, 'mv_uu'); a.warp(*center, 15, 25); a.end()
    a.label('poor'); a.writetext('g_poor'); a.waitbutton()
    a.label('no'); a.writetext('g_again'); a.waitbutton(); a.closetext()
    a.applymovement(0, 'mv_d'); a.end()
    # scene 1: back from the Safari Zone (Red: SCRIPT_SAFARIZONEGATE_LEAVING_SAFARI)
    a.label('back'); a.checkevent(game_over); a.iffalse('early')
    a.clearevent(game_over); a.callasm(SAF, LBL['stop'])
    a.opentext(); a.writetext('g_haul'); a.waitbutton(); a.closetext()
    a.applymovement(0, 'mv_ddd'); a.db(0x14, 0); a.end()
    a.label('early'); a.opentext(); a.writetext('g_leave'); a.yesorno(); a.iffalse('stay')
    a.writetext('g_ret'); a.waitbutton(); a.closetext(); a.callasm(SAF, LBL['stop'])
    a.applymovement(0, 'mv_ddd'); a.db(0x14, 0); a.end()
    a.label('stay'); a.writetext('g_luck'); a.waitbutton(); a.closetext(); a.warp(*center, 15, 25); a.end()
    a.label('mv_r'); a.db(Rr, 0x47)
    a.label('mv_d'); a.db(D, 0x47)
    a.label('mv_uu'); a.db(U, U, 0x47)
    a.label('mv_ddd'); a.db(D, D, D, 0x47)
    scenes.extend(['end', 'back'])


LBL = {}


class JAsm(Asm):
    """Asm with relative jumps to labels"""
    def __init__(s, base):
        super().__init__(base); s.rel = []
    def jr(s, op, lab):
        s.db(op); s.rel.append((len(s.b), lab)); s.db(0)
    def fin(s):
        b = bytearray(s.done())
        for pos, lab in s.rel:
            d = s.labels[lab] - (s.base + pos + 1); assert -128 <= d < 128, lab
            b[pos] = d & 0xFF
        return bytes(b)


if __name__ == '__main__':
    main()
