#!/usr/bin/env python3
"""Phase 12: Rocket Game Corner + Rocket Hideout B1F-B4F + elevator (Pikachu full-color hack maps, Red trainers,
Pikachu-version Jessie & James), new key items Silph Scope / Lift Key, Pokémon Tower wild Pokémon (Yellow),
Lavender door -> Kanto Radio Tower after the Kanto Hall of Fame.
usage: build_phase12.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode, decode
import pkmap
import build_phase11 as P11
import build_phase10 as P10

ITEM = load_consts(PC + '/constants/item_constants.asm')
MON = load_consts(PC + '/constants/pokemon_constants.asm')
FREE_EV = json.load(open(SC + '/out/free_events.json'))
EVI = [24]                      # 0-21 phase 11, 22 tower 5F zone, 23 ghost Marowak
def newflag():
    f = FREE_EV[EVI[0]]; EVI[0] += 1; return f

GRUNTM, GIOVANNI, JJ = 31, 71, 72
SILPH_SCOPE, LIFT_KEY, COIN_CASE = 0x87, 0x88, ITEM['COIN_CASE']
SILPH_CARD_KEY = 0x89                   # Silph Co.'s card key (Crystal's own CARD_KEY is for the Radio Tower)
HELIX_FOSSIL, DOME_FOSSIL, OLD_AMBER = 0x8D, 0x8E, 0x91
EV_KANTO_HOF = 0x34A
W_EVENTFLAGS = 0xDA65; W_WARPS_PTR = 0xDBC2; W_XCOORD = 0xDC7E
ITEMNAMES_PTR = 0x3380          # NamesPointers[ITEM_NAME]
ITEMATTR = 0x69FA               # ItemAttributes (bank 1), 7 bytes/item
ITEMDESC = 0x2C02D              # ItemDescriptions (bank 0x0B)
KANTO_GRASS = 0x2B297
KANTO_WATER_BLOCK = (0x2B81A, 0x2B953)   # KantoWater + SwarmGrass + SwarmWater
WILD_REFS = [(0x2A03C, 0x21, 0x781A), (0x2A21A, 0x11, 0x781A), (0x2A1F5, 0x21, 0x78F3), (0x2A20D, 0x21, 0x7952)]
GC_SLOT = (0x1A, 0x7023)        # Crystal's CeladonGameCornerLuckySlotMachineScript
SFX_ELEVATOR, SFX_ENTER_DOOR = 0x6E, 0x1F
MUSIC_HIDEOUT = 0x48

SPR = {'SPRITE_ROCKET': 0x35, 'SPRITE_GIOVANNI': 0x3F, 'SPRITE_JAMES': 0x35, 'SPRITE_JESSIE': 0x36,
       'SPRITE_POKE_BALL': 0x54, 'SPRITE_BEAUTY': 0x2A, 'SPRITE_CLERK': 0x39, 'SPRITE_MIDDLE_AGED_MAN': 0x2D,
       'SPRITE_FISHING_GURU': 0x3B, 'SPRITE_MIDDLE_AGED_WOMAN': 0x2E, 'SPRITE_GYM_GUIDE': 0x48,
       'SPRITE_GAMBLER': 0x40}
FACE = {'DOWN': 6, 'UP': 7, 'LEFT': 8, 'RIGHT': 9, 'NONE': 6, 'ANY_DIR': 2}
DIRS = {'PAD_DOWN': 0, 'PAD_UP': 1, 'PAD_LEFT': 2, 'PAD_RIGHT': 3}

HIDEOUT = [('RocketHideoutB1F', 0xC7), ('RocketHideoutB2F', 0xC8), ('RocketHideoutB3F', 0xC9),
           ('RocketHideoutB4F', 0xCA), ('RocketHideoutElevator', 0xCB)]
GEN1_TM = {'TM_RAZOR_WIND': 2, 'TM_HORN_DRILL': 7, 'TM_DOUBLE_EDGE': 10}


def tm_item(n):
    return 0xBF + n - 1 if n <= 4 else 0xC4 + n - 5 if n <= 28 else 0xDD + n - 29


def item_id(name):
    if name in GEN1_TM: return tm_item(GEN1_TM[name])
    if name == 'SILPH_SCOPE': return SILPH_SCOPE
    if name == 'LIFT_KEY': return LIFT_KEY
    return ITEM[name]


def text(body): return bytes(body) + b'\x57'


def asm_texts(g, tid, n=200):
    """text bodies referenced by `ld hl, text` inside a Gen I text_asm"""
    b, p = pkmap.text_ptr(g, tid); k, o = pkmap.text_body(b, p)
    assert k == 'asm'
    out = []
    for i in range(o, o + n):
        if pkmap.F[i] == 0x21:
            pp = pkmap.F[i + 1] | pkmap.F[i + 2] << 8
            if 0x4000 <= pp < 0x8000:
                kk, bb = pkmap.text_body(b, pp)
                if kk == 'text' and bb not in out:
                    out.append(bb)
    return out


def trainer_texts(g, tid):
    b, p = pkmap.text_ptr(g, tid); k, so = pkmap.text_body(b, p)
    assert k == 'asm' and pkmap.F[so + 1] == 0x21, (hex(g), tid)
    h = pkmap.fo(b, pkmap.F[so + 2] | pkmap.F[so + 3] << 8); hb = pkmap.F[h:h + 12]
    sight = hb[1] >> 4
    def tb(p):
        k, v = pkmap.text_body(b, p)
        if k == 'text': return v
        for i in range(v, v + 60):                     # text_asm: first `ld hl, text`
            if pkmap.F[i] == 0x21:
                kk, vv = pkmap.text_body(b, pkmap.F[i + 1] | pkmap.F[i + 2] << 8)
                if kk == 'text': return vv
        raise ValueError(hex(p))
    return sight, tb(hb[4] | hb[5] << 8), tb(hb[6] | hb[7] << 8), tb(hb[8] | hb[9] << 8)


def spinner_table(mapname):
    src = open(PY + '/scripts/%s.asm' % mapname, encoding='utf-8').read()
    lists = {}
    for m in re.finditer(r'\n(\w+ArrowMovement\d+):\n(.*?)db -1', src, re.S):
        lists[m.group(1)] = [(DIRS[d], int(c)) for d, c in re.findall(r'db (PAD_\w+), (\d+)', m.group(2))]
    out = []
    for x, y, lab in re.findall(r'map_coord_movement\s+(\d+),\s*(\d+),\s*(\w+)', src):
        out.append((int(x), int(y), list(reversed(lists[lab]))))
    return out


def main():
    src, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    log = []
    for b in (0x13, 0x12, 0x7C, 0x7D, 0x7A, 0x0B, 0x28, 0x78):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1, b * 0x4000 + 0x4000)

    # ================= key items: Silph Scope (0x87) / Lift Key (0x88)
    nb = rom[ITEMNAMES_PTR]; na = r16(ITEMNAMES_PTR + 1); o = fo(nb, na)
    names = []
    for i in range(256):
        e = rom.index(0x50, o); names.append(bytes(rom[o:e + 1])); o = e + 1
    names[SILPH_SCOPE - 1] = encode('シルフスコープ@'); names[LIFT_KEY - 1] = encode('リフトキー@')
    names[SILPH_CARD_KEY - 1] = encode('カードキー@')
    names[HELIX_FOSSIL - 1] = encode('かいのカセキ@'); names[DOME_FOSSIL - 1] = encode('こうらのカセキ@')
    names[OLD_AMBER - 1] = encode('ひみつのコハク@')
    a_names = sp.put(0x7C, b''.join(names))
    rom[ITEMNAMES_PTR] = 0x7C; w16(ITEMNAMES_PTR + 1, a_names)
    key_attr = bytes(rom[ITEMATTR + 7 * (ITEM['CARD_KEY'] - 1):][:7])
    for it in (SILPH_SCOPE, LIFT_KEY, SILPH_CARD_KEY, HELIX_FOSSIL, DOME_FOSSIL, OLD_AMBER):
        rom[ITEMATTR + 7 * (it - 1):ITEMATTR + 7 * it] = key_attr
    for it, d in ((SILPH_SCOPE, 'みえない　ものの　しょうたいを<NEXT>みやぶる　ふしぎな　スコープ@'),
                  (LIFT_KEY, 'ロケットだんの　アジトの<NEXT>エレべーターを　うごかす　カギ@'),
                  (SILPH_CARD_KEY, 'シルフカンパニーの<NEXT>ドアの　ロックを　はずす　カギ@'),
                  (HELIX_FOSSIL, 'まき　がいの　ような<NEXT>こだい　<POKEMON>の　カセキ@'),
                  (DOME_FOSSIL, 'こうらの　ような<NEXT>こだい　<POKEMON>の　カセキ@'),
                  (OLD_AMBER, 'こだい　<POKEMON>の<NEXT>いでんしが　はいった　コハク@')):
        w16(ITEMDESC + 2 * (it - 1), sp.put(0x0B, encode(d)))
    log.append('key items シルフスコープ/リフトキー/カードキー(シルフ) = 0x87/0x88/0x89')

    # ================= Pokémon Tower wild Pokémon (Yellow 3F-7F)
    ws, we = KANTO_WATER_BLOCK
    blk = bytes(rom[ws:we])
    f0a, n0a = bank_free_tail(rom, 0x0A); assert n0a > len(blk) + 2
    new_w = f0a + 1
    rom[new_w:new_w + len(blk)] = blk
    delta = new_w - ws
    for off, opc, addr in WILD_REFS:
        assert rom[off] == opc and r16(off + 1) == addr, hex(off)
        w16(off + 1, addr + delta)
    p = KANTO_GRASS
    while rom[p] != 0xFF: p += 47
    assert p == ws - 1
    tower_ids = {n: (26, 14 + i) for i, (n, g) in enumerate(P11.TOWER)}
    entries = b''
    for fl in range(3, 8):
        t = open(PY + '/data/wild/maps/PokemonTower%dF.asm' % fl, encoding='utf-8').read()
        rate = int(re.search(r'def_grass_wildmons (\d+)', t).group(1))
        slots = [(int(l), s) for l, s in re.findall(r'db\s+(\d+), (\w+)', t.split('end_grass_wildmons')[0])]
        assert len(slots) == 10
        pick = [slots[i] for i in (0, 1, 2, 3, 6, 8, 9)]
        g_, n_ = tower_ids['PokemonTower%dF' % fl]
        e = bytes([g_, n_, rate, rate, rate]) + bytes(sum(([lv, MON[s]] for lv, s in pick), [])) * 3
        assert len(e) == 47
        entries += e
    rom[p:ws] = bytes(ws - p)
    rom[p:p + len(entries) + 1] = entries + b'\xff'
    log.append('tower wild data 3F-7F (%d bytes), Kanto water tables moved to %X' % (len(entries), new_w))

    # ================= Lavender door -> Radio Tower after the Kanto Hall of Fame
    lav_h = hdr_index('LavenderTown'); lav_a = attrs(rom, lav_h)
    lav_ev = parse_events(rom, lav_a['scbank'], lav_a['events'])
    sb = lav_a['scbank']
    w_off = lav_ev['warps'][0][0]
    nwarps = len(lav_ev['warps'])
    alt = bytearray(rom[w_off:w_off + 5 * nwarps])
    o_lav = parse_events(orig, lav_a['scbank'], lav_a['events'])
    for i in range(nwarps):
        if alt[5 * i:5 * i + 5] != orig[o_lav['warps'][i][0]:o_lav['warps'][i][0] + 5]:
            alt[5 * i:5 * i + 5] = orig[o_lav['warps'][i][0]:o_lav['warps'][i][0] + 5]
            log.append('Lavender warp %d -> original (radio tower) after HoF' % (i + 1))
    a_alt = sp.put(sb, bytes(alt))
    # asm in MODBANK: if KANTO_HOF -> wCurMapWarpEventsPointer = alt
    fb = W_EVENTFLAGS + (EV_KANTO_HOF >> 3); bit = EV_KANTO_HOF & 7
    a = Asm(sp.here(0x78))
    a.db(0xFA); a.dw(fb); a.db(0xCB, 0x47 | (bit << 3), 0xC8)          # ld a,[fb]; bit n,a; ret z
    a.db(0x21); a.dw(a_alt); a.db(0x7D, 0xEA); a.dw(W_WARPS_PTR); a.db(0x7C, 0xEA); a.dw(W_WARPS_PTR + 1); a.db(0xC9)
    fn = sp.put(0x78, a.done())
    so = fo(sb, lav_a['scripts'])
    assert rom[so] == 0 and rom[so + 1] == 1 and rom[so + 2] == 5
    old_cb = r16(so + 3)
    a = Asm(sp.here(sb))
    a.db(0x00, 0x02, 0x05); a.dw('nm'); a.db(0x03); a.dw('cq')
    a.label('nm'); a.callasm(0x78, fn); a.sjump(old_cb)
    a.label('cq'); a.callasm(0x78, fn); a.endcallback()
    nh = sp.put(sb, a.done()); assert nh == a.base
    w16(lav_a['attr_off'] + 7, nh)
    log.append('Lavender callbacks -> %X:%04X' % (sb, nh))

    # ================= tilesets FACILITY / LOBBY
    tss = {'Facility': Tileset('Facility', 22, 'facility.bst', SC + '/out/pk_facility.pkl'),
           'Lobby': Tileset('Lobby', 18, 'lobby.bst', SC + '/out/pk_lobby.pkl')}
    for b_ in range(tss['Lobby'].nblocks):
        for q in range(4):
            if tss['Lobby'].quad_tile(b_, q) in (0x15, 0x36):
                tss['Lobby'].coll[4 * b_ + q] = 0x90           # COLL_COUNTER
    maps = {}
    for n, g in HIDEOUT:
        h = pkmap.header(g)
        ts = tss['Lobby'] if n.endswith('Elevator') else tss['Facility']
        maps[n] = MapPort(n, ts, h['w'], h['h'], n + '.blk')
    hg = pkmap.header(0x87)
    maps['GameCorner'] = MapPort('GameCorner', tss['Lobby'], hg['w'], hg['h'], 'GameCorner.blk')
    for n, mp in maps.items():
        objs, warps = P11.objects_of(n)
        for (x, y, dest, wid) in warps:
            b_, q = mp.block_at(x, y)
            ts = mp.ts
            tile = ts.quad_tile(b_, q)
            edge = y == mp.h * 2 - 1 or y == 0 or x == 0 or x == mp.w * 2 - 1
            if n == 'GameCorner' and dest == 'ROCKET_HIDEOUT_B1F':
                b_, q = 0x43, (y % 2) * 2 + (x % 2); tile = ts.quad_tile(b_, q)
            if edge:
                v = COLL_CARPET['down'] if y == mp.h * 2 - 1 else COLL_CARPET['up'] if y == 0 else \
                    COLL_CARPET['left'] if x == 0 else COLL_CARPET['right']
            elif tile in ts.warp_tiles:
                v = COLL_STAIRCASE
            else:
                # Gen I "press into the wall" warp (elevator doors): warp carpet facing the blocked side
                v = None
                for d, (dx, dy) in (('down', (0, 1)), ('up', (0, -1)), ('left', (-1, 0)), ('right', (1, 0))):
                    nb_, nq = mp.block_at(x + dx, y + dy)
                    if ts.quad_tile(nb_, nq) not in ts.passable:
                        v = COLL_CARPET[d]; break
                assert v is not None, (n, x, y)
                log.append('%s warp (%d,%d): carpet %s' % (n, x, y, d))
            old = ts.coll[4 * b_ + q]
            assert old in (COLL_FLOOR, COLL_WALL, v), (n, x, y, hex(old), hex(v))
            ts.coll[4 * b_ + q] = v
    old_tab_ptr = r16(R_TILESETS[0])
    old_tab_o = fo(0x13, old_tab_ptr)
    ntab = 34
    old_tab = bytes(rom[old_tab_o:old_tab_o + 15 * ntab])
    anim_none = old_tab[15 * 5 + 9:15 * 5 + 11]
    ts_id = {}
    new_tab = old_tab
    for k, ts in tss.items():
        gfx = lz(ts.gfx_raw)
        a_gfx = sp.put(0x7D, gfx); a_meta = sp.put(0x7D, ts.blocks); a_coll = sp.put(0x7D, bytes(ts.coll))
        a_pal = sp.put(0x13, ts.palmap)
        new_tab += bytes([0x7D, a_gfx & 0xFF, a_gfx >> 8, 0x7D, a_meta & 0xFF, a_meta >> 8, 0x7D, a_coll & 0xFF, a_coll >> 8]) + \
            anim_none + b'\x00\x00' + bytes([a_pal & 0xFF, a_pal >> 8])
        ts_id[k] = ntab; ntab += 1
        log.append('tileset %s id %d (gfx %d bytes, %d blocks)' % (k, ts_id[k], len(gfx), ts.nblocks))
    rom[old_tab_o:old_tab_o + len(old_tab)] = bytes(len(old_tab))
    a_tab = sp.put(0x13, new_tab)
    for off in R_TILESETS:
        w16(off, a_tab)
    # palette hook chained in front of phase 11's
    assert rom[LSMP] == 0xC3
    prev_hook = r16(LSMP + 1)
    hp = rom[HOUSEPAL_CALL:HOUSEPAL_CALL + 14]
    wbgpals = hp[3:5]; farcopy = hp[12:14]
    ph = fo(0x12, prev_hook); ld_tileset = bytes(rom[ph:ph + 3]); assert ld_tileset[0] == 0xFA
    a_pf = sp.put(0x12, tss['Facility'].pals); a_pl = sp.put(0x12, tss['Lobby'].pals)
    a = Asm(sp.here(0x12))
    a.raw(ld_tileset)
    a.db(0xFE, ts_id['Facility'], 0x28, 0x07)       # cp FAC ; jr z,.f
    a.db(0xFE, ts_id['Lobby'], 0x28, 0x08)          # cp LOB ; jr z,.l
    a.db(0xC3); a.dw(prev_hook)
    a.db(0x21); a.dw(a_pf); a.db(0x18, 0x03)        # .f ld hl,pf ; jr .c
    a.db(0x21); a.dw(a_pl)                          # .l ld hl,pl
    a.db(0x3E, 0x05, 0x11); a.raw(wbgpals); a.db(0x01, 0x40, 0x00, 0xCD); a.raw(farcopy); a.db(0x37, 0xC9)
    hook = sp.put(0x12, a.done())
    w16(LSMP + 1, hook)

    # ================= map headers 26:21-25 (bank 0x25), moving attribute blocks out of the way
    u = US.get(); G = u.groups()
    first_new = 21
    lo = GROUP26_END + 9 * (first_new - G26_COUNT - 1); hi = lo + 9 * len(HIDEOUT)
    moved = 0
    for gi in range(26):
        n_ = (G[gi + 1] - G[gi]) // 9 if gi + 1 < 26 else first_new - 1
        for k in range(n_):
            hdr = G[gi] + 9 * k
            ab = rom[hdr]; ap = r16(hdr + 3); ao = fo(ab, ap)
            nconn = bin(rom[ao + 11] & 0xF).count('1'); size = 12 + 12 * nconn
            if ao < hi and ao + size > lo:
                na_ = sp.put(0x7C, bytes(rom[ao:ao + size]))
                rom[hdr] = 0x7C; w16(hdr + 3, na_); moved += 1
    rom[lo:hi] = bytes(hi - lo)
    log.append('moved %d attribute blocks out of bank 0x25' % moved)
    mapids = {n: (G26, first_new + i) for i, (n, g) in enumerate(HIDEOUT)}
    gc_id = mapid('CeladonGameCorner'); mapids['GameCorner'] = gc_id
    cel = mapid('CeladonCity')
    cel_a = attrs(rom, hdr_index('CeladonCity')); cel_ev = parse_events(rom, cel_a['scbank'], cel_a['events'])
    cel_door = [i + 1 for i, (o_, w) in enumerate(cel_ev['warps']) if (w[3], w[4]) == gc_id][0]

    # ================= trainer parties: Red's Rockets 7-18 (GRUNTM)
    attr_ref = 0x395A4; attr_cur = fo(0x0E, r16(attr_ref + 1))
    P10.OLD_N = 72
    start, Gp, old_end = P10.parse_groups(bytes(rom), attr_cur)
    assert len(Gp[71]) == 4
    rocket = P11.red_parties('RocketData')
    def pb(mons): return b'\x00' + b''.join(bytes([lv, MON[s]]) for lv, s in mons) + b'\xff'
    grunt = {}
    for k in range(7, 19):
        Gp[GRUNTM - 1].append([encode('したっぱ@'), pb(rocket[k - 1])]); grunt[k] = len(Gp[GRUNTM - 1])
    T_G = P10.T_GROUPS; NN = 72
    attr = bytes(rom[attr_cur:attr_cur + NN * 7])
    tbl_end = T_G + NN * 2
    out = bytearray(); ptrs = []
    for gi in range(NN):
        ptrs.append(tbl_end + len(out))
        for nm, d in Gp[gi]:
            out += nm + d
    attr_off = tbl_end + len(out)
    assert attr_off + len(attr) <= 0x3C000, hex(attr_off + len(attr))
    clear_to = max(old_end, attr_cur + len(attr))
    rom[T_G:clear_to] = bytes(clear_to - T_G)
    for gi, p_ in enumerate(ptrs):
        w16(T_G + 2 * gi, 0x4000 + p_ % 0x4000)
    rom[tbl_end:tbl_end + len(out)] = out; rom[attr_off:attr_off + len(attr)] = attr
    old_a = 0x4000 + attr_cur % 0x4000; new_a = 0x4000 + attr_off % 0x4000
    for off, d in P10.R_ATTR:
        assert r16(off + 1) == old_a + d; w16(off + 1, new_a + d)
    log.append('trainer data end %X (bank end 3C000)' % (attr_off + len(attr)))

    # ================= maps
    landmark = rom[hdr_index('CeladonCity') + 5]
    for n, mp in maps.items():
        g = 0x87 if n == 'GameCorner' else dict(HIDEOUT)[n]
        objs, warps = P11.objects_of(n)
        a = Asm(sp.here(0x7A))
        callbacks = []; coords = []; bgs = []; texts = {}
        obj_bytes = []
        # pre-pass: object ids (1-based index) and flags
        oid = {}; oflag = {}
        jjv = None
        for idx, o in enumerate(objs):
            tid = idx + 1
            if o['sprite'] == 'SPRITE_POKE_BALL':
                oid[o['extra'][0]] = tid; oflag[tid] = newflag()
            elif o['sprite'] in ('SPRITE_JESSIE', 'SPRITE_JAMES'):
                oid[o['sprite']] = tid
                if jjv is None: jjv = newflag()
                oflag[tid] = jjv
            elif o['sprite'] == 'SPRITE_GIOVANNI' or (n == 'GameCorner' and o['sprite'] == 'SPRITE_ROCKET'):
                oflag[tid] = newflag()
        keydrop = newflag() if n == 'RocketHideoutB4F' else None
        for idx, o in enumerate(objs):
            tid = idx + 1
            lab = 'o%d' % tid
            sprite = SPR[o['sprite']]; mv = FACE.get(o['face'], 6) if o['move'] == 'STAY' else 2
            flag = oflag.get(tid, 0xFFFF); typ = 0; sight = 0
            if o['sprite'] == 'SPRITE_POKE_BALL':
                typ = 1
                it = o['extra'][0]
                a.label(lab); a.db(item_id(it), 1)
            elif n == 'GameCorner' and o['sprite'] == 'SPRITE_ROCKET':
                tg = asm_texts(g, 11)
                _, t_after = pkmap.text_body(*pkmap.text_ptr(g, 13))
                a.label(lab); a.faceplayer(); a.opentext(); a.writetext('gr1'); a.waitbutton(); a.closetext()
                a.winlosstext('gr2', 0); a.loadtrainer(GRUNTM, grunt[int(o['extra'][1])]); a.startbattle(); a.reloadmapafterbattle()
                a.opentext(); a.writetext('gr3'); a.waitbutton(); a.closetext()
                a.readmem(W_XCOORD); a.ifequal(10, 'gra')
                a.applymovement(tid + 1, 'grm1'); a.sjump('grz')
                a.label('gra'); a.applymovement(tid + 1, 'grm2')
                a.label('grz'); a.disappear(tid + 1); a.setevent(flag); a.end()
                a.label('grm1'); a.db(*([0x0F] * 5), 0x47)
                a.label('grm2'); a.db(0x0C, 0x0F, 0x0F, 0x0F, 0x0D, 0x0F, 0x0F, 0x0F, 0x47)
                texts['gr1'] = tg[0]; texts['gr2'] = tg[1]; texts['gr3'] = t_after
            elif o['sprite'] == 'SPRITE_ROCKET' and o['extra'] and o['extra'][0] == 'OPP_ROCKET':
                typ = 2; fl = newflag()
                sight, seen, aft, win = trainer_texts(g, tid)
                k = int(o['extra'][1])
                a.label(lab); a.dw(fl); a.db(GRUNTM, grunt[k]); a.dw(lab + 's'); a.dw(lab + 'w'); a.dw(0); a.dw(lab + 'x')
                if n == 'RocketHideoutB4F':                 # drops the Lift Key
                    # (the end-of-battle text already says the key was dropped)
                    a.label(lab + 'x'); a.checkevent(keydrop); a.iftrue(lab + 'y')
                    a.setevent(keydrop); a.appear(oid['LIFT_KEY'] + 1); a.end()
                    a.label(lab + 'y')
                else:
                    a.label(lab + 'x')
                if n == 'RocketHideoutB1F' and k == 12:
                    oid['doorrocket'] = fl
                a.endifjustbattled(); a.opentext(); a.writetext(lab + 'a'); a.waitbutton(); a.closetext(); a.end()
                texts[lab + 's'] = seen; texts[lab + 'w'] = win; texts[lab + 'a'] = aft
            elif o['sprite'] == 'SPRITE_GIOVANNI':
                oid['gio'] = (tid, flag)
                tg = asm_texts(g, tid)
                a.label(lab); a.faceplayer(); a.opentext(); a.writetext('gv1'); a.waitbutton(); a.closetext()
                a.winlosstext('gv2', 0); a.loadtrainer(GIOVANNI, 1); a.startbattle(); a.reloadmapafterbattle()
                a.opentext(); a.writetext('gv3'); a.waitbutton(); a.closetext()
                a.disappear(tid + 1); a.setevent(flag); a.appear(oid['SILPH_SCOPE'] + 1); a.end()
                texts['gv1'] = tg[0]; texts['gv2'] = tg[1]; texts['gv3'] = tg[2]
            elif o['sprite'] in ('SPRITE_JESSIE', 'SPRITE_JAMES'):
                a.label(lab); a.end()
            elif n == 'GameCorner' and o['sprite'] == 'SPRITE_CLERK':
                a.label(lab); a.jumpstd(0x32)
            else:
                b_, p_ = pkmap.text_ptr(g, tid); k_, body = pkmap.text_body(b_, p_)
                if k_ == 'text':
                    a.label(lab); a.jumptextfaceplayer(lab + 't'); texts[lab + 't'] = body
                else:
                    tg = asm_texts(g, tid)
                    if n == 'GameCorner' and len(tg) >= 5:          # gives 20 coins once
                        cf = newflag()
                        a.label(lab); a.faceplayer(); a.opentext(); a.checkevent(cf); a.iftrue(lab + 'z')
                        a.writetext(lab + 'a'); a.waitbutton()
                        a.checkitem(COIN_CASE); a.iffalse(lab + 'n')
                        a.givecoins(20); a.writetext(lab + 'b'); a.waitbutton(); a.setevent(cf); a.closetext(); a.end()
                        a.label(lab + 'n'); a.writetext(lab + 'c'); a.waitbutton(); a.closetext(); a.end()
                        a.label(lab + 'z'); a.writetext(lab + 'd'); a.waitbutton(); a.closetext(); a.end()
                        texts[lab + 'a'] = tg[0]; texts[lab + 'b'] = tg[1]; texts[lab + 'd'] = tg[2]; texts[lab + 'c'] = tg[4]
                    elif n == 'GameCorner' and o['sprite'] == 'SPRITE_FISHING_GURU' and len(tg) == 1:   # 10 coins once
                        cf = newflag()
                        a.label(lab); a.faceplayer(); a.opentext(); a.writetext(lab + 'a'); a.waitbutton()
                        a.checkevent(cf); a.iftrue(lab + 'z'); a.checkitem(COIN_CASE); a.iffalse(lab + 'z')
                        a.givecoins(10); a.writetext(lab + 'b'); a.waitbutton(); a.setevent(cf)
                        a.label(lab + 'z'); a.closetext(); a.end()
                        texts[lab + 'a'] = tg[0]; texts[lab + 'b'] = encode('{00}<PLAYER>は　コインを<LINE>10まい　もらった！')
                    else:
                        a.label(lab); a.jumptextfaceplayer(lab + 't'); texts[lab + 't'] = tg[0]
            obj_bytes.append([sprite, o['y'] + 4, o['x'] + 4, mv, 0, 0xFF, 0xFF, typ, sight, lab, flag])

        # ---- map specific events
        if n == 'GameCorner':
            found = newflag()
            tg = asm_texts(g, 12)
            a.label('poster'); a.checkevent(found); a.iftrue('pend')
            a.opentext(); a.writetext('pt'); a.waitbutton(); a.closetext()
            a.playsound(SFX_ENTER_DOOR); a.waitsfx()
            a.changeblock(16, 4, 0x43); a.refreshmap(); a.setevent(found)
            a.label('pend'); a.end()
            texts['pt'] = tg[0]
            a.label('cbt'); a.checkevent(found); a.iftrue('cbe'); a.changeblock(16, 4, 0x2A)
            a.label('cbe'); a.endcallback()
            callbacks.append((1, 'cbt'))
            bgs.append((4, 9, 1, 'poster'))
            a.label('slot'); a.farsjump(*GC_SLOT)
            for x, y in re.findall(r'hidden_event\s+(\d+),\s*(\d+),\s*StartSlotMachine',
                                   open(PY + '/data/events/hidden_events.asm').read().split('hidden_events_for GAME_CORNER')[1].split('hidden_events_for')[0]):
                bgs.append((int(y), int(x), 0, 'slot'))
            nocase = asm_texts(g, 9)[4]
            for i, (x, y, c) in enumerate([(0, 8, 10), (1, 16, 10), (3, 11, 20)]):
                hf = newflag(); L = 'hc%d' % i
                a.label(L); a.checkevent(hf); a.iftrue(L + 'e'); a.opentext(); a.checkitem(COIN_CASE); a.iffalse(L + 'n')
                a.givecoins(c); a.setevent(hf); a.writetext(L + 't'); a.waitbutton(); a.closetext(); a.end()
                a.label(L + 'n'); a.writetext('hcn'); a.waitbutton(); a.closetext()
                a.label(L + 'e'); a.end()
                texts[L + 't'] = encode('{00}<PLAYER>は　コインを<LINE>%dまい　みつけた！' % c)
                bgs.append((y, x, 0, L))
            texts['hcn'] = nocase
        if n == 'RocketHideoutB1F':
            a.label('door'); a.checkevent(oid['doorrocket']); a.iftrue('de'); a.changeblock(24, 16, 0x54)
            a.label('de'); a.endcallback()
            callbacks.append((1, 'door'))
        if n in ('RocketHideoutB2F', 'RocketHideoutB3F'):
            for i, (x, y, mvl) in enumerate(spinner_table(n)):
                L = 'sp%d' % i
                a.label(L); a.applymovement(0, L + 'm'); a.end()
                a.label(L + 'm')
                for d, c in mvl:
                    a.db(*([0x18 + d] * c))
                a.db(0x47)
                coords.append((y, x, L))
        if n == 'RocketHideoutB4F':
            jjf = newflag()
            gio_t, gio_f = oid['gio']
            # hide Jessie & James, keep the Silph Scope / Lift Key hidden until dropped
            a.label('cbo'); a.setevent(jjv)
            a.checkevent(gio_f); a.iftrue('cb1'); a.setevent(oflag[oid['SILPH_SCOPE']])
            a.label('cb1'); a.checkevent(keydrop); a.iftrue('cb2'); a.setevent(oflag[oid['LIFT_KEY']])
            a.label('cb2'); a.endcallback()
            callbacks.append((2, 'cbo'))
            _, t11 = pkmap.text_body(*pkmap.text_ptr(g, 11))
            _, t12 = pkmap.text_body(*pkmap.text_ptr(g, 12))
            _, t13 = pkmap.text_body(*pkmap.text_ptr(g, 13))
            _, tl = pkmap.text_body(0x11, 0x6132)
            texts['j11'] = t11; texts['j12'] = t12; texts['j13'] = bytes(t13).replace(b'\x6e', encode('ィ')); texts['jl'] = tl
            jam, jes = oid['SPRITE_JAMES'] + 1, oid['SPRITE_JESSIE'] + 1
            for side, x in (('L', 24), ('R', 25)):
                L = 'jj' + side
                a.label(L); a.checkevent(jjf); a.iftrue('jje')
                a.playmusic(0x39)
                a.opentext(); a.writetext('j11'); a.waitbutton(); a.closetext()
                a.appear(jam); a.appear(jes)
                # player on the left (x=24): James (x=25) comes down beside, Jessie (x=24) stops in front
                a.applymovement(jam, 'm4' if side == 'L' else 'm3')
                a.applymovement(jes, 'm3' if side == 'L' else 'm4')
                a.sjump('jjb')
                coords.append((14, x, L))
            a.label('m4'); a.db(0x10, 0x10, 0x10, 0x10, 0x47)
            a.label('m3'); a.db(0x10, 0x10, 0x10, 0x47)
            a.label('jjb')
            a.opentext(); a.writetext('j12'); a.waitbutton(); a.closetext()
            a.winlosstext('jl', 0); a.loadtrainer(JJ, 2); a.startbattle(); a.reloadmapafterbattle()
            a.opentext(); a.writetext('j13'); a.waitbutton(); a.closetext()
            a.disappear(jam); a.disappear(jes); a.setevent(jjf)
            a.label('jje'); a.end()
        if n == 'RocketHideoutElevator':
            _, nokey = None, asm_texts(g, 1)[0]
            a.label('elv'); a.opentext(); a.checkitem(LIFT_KEY); a.iffalse('eln')
            a.elevator('eld'); a.closetext(); a.iffalse('ele')
            a.pause(5); a.playsound(SFX_ELEVATOR); a.earthquake(60); a.waitsfx()
            a.label('ele'); a.end()
            a.label('eln'); a.writetext('elt'); a.waitbutton(); a.closetext(); a.end()
            a.label('eld'); a.db(3)
            for fl_, wid, mn in ((3, 5, 'RocketHideoutB1F'), (2, 5, 'RocketHideoutB2F'), (0, 3, 'RocketHideoutB4F')):
                a.db(fl_, wid, *mapids[mn])
            a.db(0xFF)
            texts['elt'] = nokey
            bgs.append((1, 1, 1, 'elv'))

        for k_, v in texts.items():
            assert len(v) < 600, (n, k_, len(v)); a.label(k_); a.raw(text(v))
        # map scripts header
        a.label('mapscripts')
        a.db(0, len(callbacks))
        for t_, l_ in callbacks:
            a.db(t_); a.dw(l_)
        a.label('events')
        a.db(0, 0)
        a.db(len(warps))
        for (x, y, dest, wid) in warps:
            if dest == 'LAST_MAP':
                a.db(y, x, cel_door, *cel)
            elif n == 'RocketHideoutElevator':
                a.db(y, x, 0xFF, *mapids['RocketHideoutB1F'])
            else:
                dn = 'GameCorner' if dest == 'GAME_CORNER' else \
                    re.sub(r'(^|_)(\w)', lambda m: m.group(2).upper(), dest.lower()).replace('B1f', 'B1F').replace('B2f', 'B2F').replace('B3f', 'B3F').replace('B4f', 'B4F')
                a.db(y, x, wid, *mapids[dn])
        a.db(len(coords))
        for (y, x, l_) in coords:
            a.db(0xFF, y, x, 0); a.dw(l_); a.db(0, 0)
        a.db(len(bgs))
        for (y, x, f_, l_) in bgs:
            a.db(y, x, f_); a.dw(l_)
        a.db(len(obj_bytes))
        for ob in obj_bytes:
            a.db(*ob[:9]); a.dw(ob[9]); a.dw(ob[10])
        base = a.base
        blob = a.done()
        got = sp.put(0x7A, blob); assert got == base
        blkp = sp.put(0x7C, mp.blk)
        attr_ = bytes([border_of(n), mp.h, mp.w, 0x7C, blkp & 0xFF, blkp >> 8, 0x7A, a.labels['mapscripts'] & 0xFF, a.labels['mapscripts'] >> 8,
                       a.labels['events'] & 0xFF, a.labels['events'] >> 8, 0])
        aa = sp.put(0x7C, attr_)
        if n == 'GameCorner':
            h = hdr_index('CeladonGameCorner')
            rom[h] = 0x7C; rom[h + 1] = ts_id['Lobby']; w16(h + 3, aa)
        else:
            gnum = mapids[n][1]
            h = GROUP26_END + 9 * (gnum - G26_COUNT - 1)
            env = 3 if n.endswith('Elevator') else 7
            ts = ts_id['Lobby'] if n.endswith('Elevator') else ts_id['Facility']
            rom[h:h + 9] = bytes([0x7C, ts, env, aa & 0xFF, aa >> 8, landmark, MUSIC_HIDEOUT, 0x01, 0x00])
        log.append('%s -> map %d:%d  scripts 7A:%04X (%d bytes)' % (n, mapids[n][0], mapids[n][1], base, len(blob)))

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    log.append('flags used up to index %d of %d' % (EVI[0], len(FREE_EV)))
    print('\n'.join(log))


if __name__ == '__main__':
    main()
