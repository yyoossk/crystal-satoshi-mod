#!/usr/bin/env python3
"""Phase 27: Route 2 as in Red / the Pikachu full-color hack, for good, with Viridian Forest:
 * Red's Route 2 (Gen I overworld tileset, 10x36 blocks) in place of Crystal's: the road through Viridian Forest in the
   west, the gate and the road to Diglett's Cave and the trade house in the east (behind trees that Cut clears),
   Red's items and signs.  Pewter City (Red, phase 26) is joined to it directly, Viridian City (Crystal's) shows its
   edge drawn with the other tileset (blockxlat).
 * Red's buildings: Route 2 gate (Oak's aide gives HM05 for 10 kinds of Pokémon caught), the trade house (Abra for
   Mr. Mime), the forest's south and north gates, the entrance of Diglett's Cave (leads into Crystal's Diglett's Cave).
 * Viridian Forest: Red's bug catchers, items, hidden items, signs and wild Pokémon (Pikachu too).
 * Cut on the Gen I overworld tileset: Red's cut trees (tile $3D) and grass, Red's block swaps.
 * The tileset table gets room for 64 tilesets (new: Gate, Forest gate, Forest).
usage: build_phase27.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
import portmaps as PM
import pairwalls
import blockxlat as X
import redmap as RM
import redtexts as RT
import build_phase10 as P10
import build_phase12 as P12
import build_phase13 as P13
import build_phase15 as P15
import build_phase17 as P17
import build_phase19 as P19
import build_phase21 as P21
import build_phase24 as P24
import build_phase25 as P25

FIRST_FLAG = 229                   # 227-228: phase 26
FIRST_MAP = 81                     # 26:79-80 = phase 26
BANK, BANK2, BANK3 = 0x69, 0x6A, 0x6B   # free in the JP original
TS_CAP = 64
OVERWORLD_TS, HOUSE_TS, CAVERN_TS = 40, 44, 37
RED_ROUTE2 = 0x0D
W2, H2 = 10, 36
HM05 = 0xF7
W_DEX_CAUGHT, W_SCRIPT_VAR = 0xDE2D, 0xC2DD
ABRA, MR_MIME = 63, 122
CUT_LD_HL = 0xC7E1                 # 03:47E1  ld hl, CutTreeBlockPointers (CheckMapForSomethingToCut)
CUT_TABLE = (0xC862, 0xC8A4)       # 03:4862-48A3  CutTreeBlockPointers + its lists
COLL_CUT_TREE = 0x12
RED_CUT = [(0x32, 0x6D), (0x33, 0x6C), (0x34, 0x6F), (0x35, 0x4C), (0x60, 0x6E), (0x0B, 0x0A), (0x3C, 0x35),
           (0x3F, 0x35), (0x3D, 0x36)]           # pokered CutTreeBlockSwaps ($0B: grass)
FOREST_PAIRS = [(0x30, 0x2E), (0x52, 0x2E), (0x55, 0x2E), (0x56, 0x2E), (0x20, 0x2E), (0x5E, 0x2E), (0x5F, 0x2E)]
SPR = dict(P25.SPR); SPR['SPRITE_GAMEBOY_KID'] = 0x03
# (name, Red map id, tileset key)
MAPS = [('Route2Gate', 0x31, 'Gate'), ('Route2TradeHouse', 0x30, 'House'), ('ViridianForestSouthGate', 0x32, 'ForestGate'),
        ('ViridianForest', 0x33, 'Forest'), ('ViridianForestNorthGate', 0x2F, 'ForestGate'),
        ('DiglettsCaveRoute2', 0x2E, 'Cavern')]
CONST = {'ROUTE_2_GATE': 'Route2Gate', 'ROUTE_2_TRADE_HOUSE': 'Route2TradeHouse',
         'VIRIDIAN_FOREST_SOUTH_GATE': 'ViridianForestSouthGate', 'VIRIDIAN_FOREST': 'ViridianForest',
         'VIRIDIAN_FOREST_NORTH_GATE': 'ViridianForestNorthGate', 'DIGLETTS_CAVE_ROUTE_2': 'DiglettsCaveRoute2'}
# Crystal map whose header gives landmark / music / palette / fishing group; environment (the forest: GATE = encounters
# only in the grass, the bicycle allowed, no roof colours of the town / route environments)
HDR_FROM = {'Route2Gate': ('Route2Gate', 6), 'Route2TradeHouse': ('Route2NuggetHouse', 3),
            'ViridianForestSouthGate': ('Route2Gate', 6), 'ViridianForestNorthGate': ('Route2Gate', 6),
            'ViridianForest': ('IlexForest', 6), 'DiglettsCaveRoute2': ('DiglettsCave', 4)}
KG_REFS = [0x2A036, 0x2A4AE, 0x2A555]      # ld hl, KantoGrassWildMons
JW_REFS = [0x2A026, 0x2A217]               # ld hl, JohtoWaterWildMons
JOHTO_WATER_N = 38
DIGLETT_ROUTE2_WARP = 3            # Crystal's Diglett's Cave: warp 3 = the Route 2 end


def kanto_grass(rom):
    """the Kanto grass wild table (phase 27 moved it: later phases read its place from the code)"""
    return fo(0x0A, rom[KG_REFS[0] + 1] | rom[KG_REFS[0] + 2] << 8)


def red_trainer_texts(g, tid):
    """build_phase12.trainer_texts for JP Red: (sight, seen, after, win)"""
    R = RM.R
    b, p = RM.text_ptr(g, tid); k, so = RM.text_body(b, p)
    assert k == 'asm' and R[so + 1] == 0x21, (hex(g), tid)
    h = RM.fo(b, R[so + 2] | R[so + 3] << 8); hb = R[h:h + 12]
    def tb(p):
        k, v = RM.text_body(b, p)
        if k == 'text': return RM.crystal_text(b, p)
        for i in range(v, v + 60):
            if R[i] == 0x21:
                pp = R[i + 1] | R[i + 2] << 8
                if 0x4000 <= pp < 0x8000 and RM.text_body(b, pp)[0] == 'text': return RM.crystal_text(b, pp)
        raise ValueError(hex(p))
    return hb[1] >> 4, tb(hb[4] | hb[5] << 8), tb(hb[6] | hb[7] << 8), tb(hb[8] | hb[9] << 8)


def gen1_text(o, subs):
    """a Gen I text_far body at o (several segments, text_ram / text_decimal) as Crystal text; subs maps the
    ('ram'|'dec', addr) of the Gen I commands to Crystal bytes"""
    R = RT.R; out = bytearray()
    while True:
        c = R[o]
        if c == 0x00:
            e = o + 1
            while R[e] not in (0x50, 0x57, 0x58): e += 1
            out += R[o:e + 1]
            if R[e] != 0x50: return bytes(out)
            o = e + 1
        elif c == 0x01: out += subs[('ram', R[o + 1] | R[o + 2] << 8)]; o += 3
        elif c == 0x09: out += subs[('dec', R[o + 1] | R[o + 2] << 8)]; o += 4
        elif c in (0x0B, 0x11): out.append(0x0F); o += 1
        elif c == 0x50: out.append(0x50); return bytes(out)
        else: raise ValueError('%02X at %X' % (c, o))


def lit(s): return b'\x00' + encode(s).rstrip(b'\x50') + b'\x50'


def block0_copy(meta, coll, blks):
    """Crystal's GetCoordTile takes block 0 for a wall: maps that walk on it get a copy"""
    if not any(0 in b for b in blks.values()): return meta, coll, blks
    z = len(coll) // 4
    return meta + meta[:16], coll + coll[:4], {n: bytes(z if v == 0 else v for v in b) for n, b in blks.items()}


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (0x03, 0x0A, 0x12, 0x3F, BANK, BANK2, BANK3):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1 if f > b * 0x4000 else f, b * 0x4000 + 0x4000)
    runs = []; i = fo(0x13, 0x7900)                       # bank 13 (palette maps): the largest free run there
    while i < fo(0x13, 0x8000):
        if rom[i] == 0:
            j = i
            while j < fo(0x13, 0x8000) and rom[j] == 0: j += 1
            runs.append((j - i, i, j)); i = j
        else: i += 1
    n_, g0, g1 = max(runs); sp.set_area(0x13, g0 + 1, g1)
    log = []
    FL = PM.Flags(FIRST_FLAG)
    r2 = mapid('Route2'); vir = mapid('ViridianCity'); pew = mapid('PewterCity')
    mapids = {n: (G26, FIRST_MAP + i) for i, (n, g, tk) in enumerate(MAPS)}

    # ================= the tileset table: room for TS_CAP tilesets
    TS = PM.Tilesets(rom, sp)
    old = TS.tab; size = 15 * P15.TS_CAP
    nt_ = sp.put(BANK2, bytes(rom[old:old + size]) + bytes(15 * (TS_CAP - P15.TS_CAP)))
    w16(PM.R_TILESETS[0], nt_); rom[PM.TILESETS_BANK] = BANK2
    rom[old:old + size] = bytes(size)
    P15.TS_CAP = TS_CAP
    TS = PM.Tilesets(rom, sp)

    # ================= tilesets
    tss = {'Gate': Tileset('Gate', 12, 'gate.bst', SC + '/out/pk_gate.pkl'),
           'ForestGate': Tileset('ForestGate', 9, 'gate.bst', SC + '/out/pk_forestgate.pkl'),
           'Forest': Tileset('Forest', 3, 'forest.bst', SC + '/out/pk_forest.pkl', grass=0x20),
           'House': Tileset('House', 8, 'house.bst', SC + '/out/pk_house.pkl'),
           'Cavern': Tileset('Cavern', 17, 'cavern.bst', SC + '/out/pk_cavern.pkl'),
           'Overworld': Tileset('Overworld', 0, 'overworld.bst', SC + '/out/pk_overworld.pkl', water=0x14, grass=0x52)}
    for tk in ('Gate', 'ForestGate'):
        ts = tss[tk]
        for b_ in range(ts.nblocks):
            for q in range(4):
                if ts.quad_tile(b_, q) in (0x17, 0x32): ts.coll[4 * b_ + q] = 0x90      # COLL_COUNTER
    maps = {}; objs_of = {}
    for n, g, tk in MAPS:
        h = RM.header(g); maps[n] = MapPort(n, tss[tk], h['w'], h['h'], n + '.blk')
        objs_of[n] = P25.red_objects(n)
    route = MapPort('Route2', tss['Overworld'], W2, H2, 'Route2.blk')
    red_route_blk = route.blk
    objs_of['Route2'] = P25.red_objects('Route2')
    ov = {n: {(x, y): P25.warp_override(maps[n].ts, maps[n], x, y, maps[n].ts.name == 'Cavern')
              for x, y, d, w in objs_of[n][1]} for n in maps}
    ov['Route2'] = {(x, y): P25.warp_override(route.ts, route, x, y) for x, y, d, w in objs_of['Route2'][1]}
    ts_id = {'House': HOUSE_TS, 'Cavern': CAVERN_TS, 'Overworld': OVERWORLD_TS}
    for tk in ('Gate', 'ForestGate', 'Forest'):
        ts = tss[tk]; mm = {n: maps[n] for n, g, k in MAPS if k == tk}
        meta2, coll2, blks = pairwalls.variants(ts, bytes(ts.blocks), bytes(ts.coll), mm,
                                                FOREST_PAIRS if tk == 'Forest' else [], {n: ov[n] for n in mm})
        meta2, coll2, blks = block0_copy(meta2, coll2, blks)
        ts.blocks = meta2; ts.coll = bytearray(coll2); ts.nblocks = len(coll2) // 4
        for n in mm: maps[n].blk = blks[n]
        ts_id[tk] = TS.add(ts, BANK2, log)
    for tk in ('House', 'Cavern', 'Overworld'):
        ts = tss[tk]; e = TS.entry(ts_id[tk])
        am_, ac_ = e[4] | e[5] << 8, e[7] | e[8] << 8
        assert e[3] == e[6] and ac_ > am_
        nb0 = (ac_ - am_) // 16
        meta = bytes(rom[fo(e[3], am_):fo(e[3], am_) + 16 * nb0]); coll = bytearray(rom[fo(e[6], ac_):fo(e[6], ac_) + 4 * nb0])
        assert meta[:16 * ts.nblocks] == bytes(ts.blocks)
        if tk == 'Overworld':                                   # Red: Cut works on tile $3D
            for b_ in range(nb0):
                for q in range(4):
                    r_, c_ = ((1, 0), (1, 2), (3, 0), (3, 2))[q]
                    if meta[16 * b_ + 4 * r_ + c_] == 0x3D and coll[4 * b_ + q] == COLL_WALL: coll[4 * b_ + q] = COLL_CUT_TREE
            ts.coll = bytearray(coll[:4 * ts.nblocks])
            mm = {'Route2': route}
        else:
            mm = {n: maps[n] for n, g, k in MAPS if k == tk}
        meta2, coll2, blks = pairwalls.variants(ts, meta, bytes(coll), mm, P21.PAIRS if tk == 'Cavern' else [],
                                                {n: ov[n] for n in mm})
        assert len(coll2) // 4 <= 256
        am = sp.put(BANK3, meta2 + coll2); ac = am + len(meta2)
        t0 = TS.tab + 15 * ts_id[tk]
        rom[t0 + 3] = BANK3; w16(t0 + 4, am); rom[t0 + 6] = BANK3; w16(t0 + 7, ac)
        for n in mm: mm[n].blk = blks[n]
        log.append('tileset %s: %d blocks (+%d)' % (tk, len(coll2) // 4, len(coll2) // 4 - nb0))

    # ================= Cut: Red's block swaps for the Gen I overworld tileset (bank 3)
    lo_, hi_ = CUT_TABLE; reg = bytes(rom[lo_:hi_])
    assert rom[CUT_LD_HL] == 0x21 and r16(CUT_LD_HL + 1) == 0x4000 + lo_ % 0x4000
    tab = [(reg[3 * i], reg[3 * i + 1] | reg[3 * i + 2] << 8) for i in range(5)]; assert reg[15] == 0xFF
    lists = {}
    for t_, p_ in tab:
        o_ = fo(0x03, p_); e_ = rom.index(0xFF, o_); lists[t_] = bytes(rom[o_:e_ + 1])
    kanto = lists[3]
    have = {kanto[i] for i in range(0, len(kanto) - 1, 3)}
    extra = b''.join(bytes([b_, r_, 0]) for b_, r_ in RED_CUT if b_ not in have)
    body = bytearray(); ptr = {}
    base3 = 0x4000 + lo_ % 0x4000
    for t_, p_ in tab:
        if t_ == 3: continue
        ptr[t_] = base3 + len(body); body += lists[t_]
    ptr[OVERWORLD_TS] = base3 + len(body); body += extra
    ptr[3] = base3 + len(body); body += kanto            # Crystal's Kanto list = the tail of Red's
    assert len(body) <= hi_ - lo_
    rom[lo_:hi_] = bytes(body) + bytes(hi_ - lo_ - len(body))
    newtab = b''.join(bytes([t_, ptr[t_] & 0xFF, ptr[t_] >> 8]) for t_ in [t for t, p in tab] + [OVERWORLD_TS]) + b'\xff'
    at = sp.put(0x03, newtab); w16(CUT_LD_HL + 1, at)
    log.append('Cut: block swaps of tileset %d (table 03:%04X)' % (OVERWORLD_TS, at))

    # ================= trainer parties (bank 7E): the bug catchers
    groups = P13.read_groups7e(rom)
    def pb(mons): return b'\x00' + b''.join(bytes([lv, PM.MON[P10.MON_ALIAS.get(s, s)]]) for lv, s in mons) + b'\xff'
    party_of = {}; ti = 0
    for n, g, tk in MAPS:
        for i, o in enumerate(objs_of[n][0]):
            if o['extra'] and o['extra'][0].startswith('OPP_'):
                c = o['extra'][0][4:]; k = int(o['extra'][1]); cid = PM.TCLS[c]
                groups[cid - 1].append([encode(PM.NAMEPOOL[(ti + 2) % len(PM.NAMEPOOL)] + '@'), pb(PM.red_party(c, k))])
                party_of[(n, i)] = (cid, len(groups[cid - 1])); ti += 1
    log.append('trainer parties added (bank 7E free %d)' % P13.write_groups7e(rom, groups))

    # ================= Red's trade: Abra -> Mr. Mime
    ref = P19.NPC_TRADES_REF; assert rom[ref] == 0x21
    to = fo(0x3F, r16(ref + 1)); nt = 7 + len(P19.RED_TRADES) + 1                     # + phase 25's
    table = bytearray(rom[to:to + 16 * nt])
    nick = bytes(RT.R[0x7204B + 3:0x7204B + 7])
    table += bytes([0, ABRA, MR_MIME]) + nick + bytes([0x96, 0x66, 0x00]) + (31415 + 1111 * nt).to_bytes(2, 'little') + \
        encode('ミツル')[:3] + b'\x00'
    trade_marcel = nt
    na = sp.put(0x3F, bytes(table)); w16(ref + 1, na)

    def hl(mapid_, tid, **kw):
        return [RM.crystal_text(b, p) for b, p in RM.asm_hl(mapid_, tid, **kw) if RM.R[RM.fo(b, p)] in (0x00, 0x17)]
    def rt(mapid_, tid):
        b, p = RM.text_ptr(mapid_, tid); k, v = RM.text_body(b, p)
        if k == 'text': return RM.crystal_text(b, p)
        return hl(mapid_, tid)[0]

    # ================= headers 26:81-86 (move what lies there)
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

    # ================= the aide's routine: kinds of Pokémon caught -> wScriptVar
    count = sp.put(BANK, bytes([0x21, W_DEX_CAUGHT & 0xFF, W_DEX_CAUGHT >> 8, 0x06, 0x20, 0x0E, 0x00,
                                0x2A, 0x16, 0x08, 0xCB, 0x3F, 0x30, 0x01, 0x0C, 0x15, 0x20, 0xF8, 0x05, 0x20, 0xF2,
                                0x79, 0xEA, W_SCRIPT_VAR & 0xFF, W_SCRIPT_VAR >> 8, 0xC9]))
    aide_subs = {('dec', 0xFFDB): lit('10'), ('dec', 0xFFDD): bytes([0x09, W_SCRIPT_VAR & 0xFF, W_SCRIPT_VAR >> 8, 0x13]),
                 ('ram', 0xCC5B): lit('ひでんマシン05')}
    i_ = RT.R.index(encode('ぼく　おぼえてます').rstrip(b'\x50')); hi_t = RT.R.rindex(0x00, i_ - 8, i_)
    aide = {k: gen1_text(o, aide_subs) for k, o in
            (('hi', hi_t), ('uhoh', 0x58E80), ('back', 0x58ED3), ('here', 0x58F05), ('got', 0x58F44), ('full', 0x58F5F))}

    # ================= the interiors and the forest
    got_hm05 = FL.new()
    for n, g, tk in MAPS:
        objs, warps, bgl = objs_of[n]
        a = Asm(sp.here(BANK)); texts = {}; obj_bytes = []; bgs = []
        a.label('end'); a.end()
        for idx, o in enumerate(objs):
            tid = idx + 1; lab = 'o%d' % tid; fl = 0xFFFF; typ = 0; sight = 0
            mv, rng = P25.face((0, 0, 0, o['move'], o['face']))
            spr = SPR[o['sprite']]
            if o['sprite'] == 'SPRITE_POKE_BALL':
                typ = 1; fl = FL.new(); a.label(lab); a.db(PM.item_id(o['extra'][0]), 1)
            elif o['extra'] and o['extra'][0].startswith('OPP_'):
                sight, seen, aft, win = red_trainer_texts(g, tid)
                fl = FL.new(); cid, pid = party_of[(n, idx)]; typ = 2
                a.label(lab); a.dw(fl); a.db(cid, pid); a.dw(lab + 's'); a.dw(lab + 'w'); a.dw(0); a.dw(lab + 'x')
                a.label(lab + 'x'); a.endifjustbattled(); a.opentext(); a.writetext(lab + 'a'); a.waitbutton(); a.closetext(); a.end()
                texts[lab + 's'] = seen; texts[lab + 'w'] = win; texts[lab + 'a'] = aft
            elif n == 'Route2Gate' and tid == 1:
                flash = hl(g, 1, n=200, stop=False)[-1]
                texts.update({'a_' + k: v for k, v in aide.items()}); texts['a_flash'] = flash
                a.label(lab); a.faceplayer(); a.opentext(); a.checkevent(got_hm05); a.iftrue('a_fl')
                a.writetext('a_hi'); a.yesorno(); a.iffalse('a_no')
                a.callasm(BANK, count); a.db(0x0B, 10); a.dw('a_few')                          # ifless 10
                a.writetext('a_here'); a.db(0x1F, HM05, 1); a.iffalse('a_nf')                 # giveitem
                a.writetext('a_got'); a.waitbutton(); a.setevent(got_hm05)
                a.label('a_fl'); a.writetext('a_flash'); a.waitbutton(); a.closetext(); a.end()
                a.label('a_few'); a.writetext('a_uhoh'); a.waitbutton(); a.closetext(); a.end()
                a.label('a_no'); a.writetext('a_back'); a.waitbutton(); a.closetext(); a.end()
                a.label('a_nf'); a.writetext('a_full'); a.waitbutton(); a.closetext(); a.end()
            elif n == 'Route2TradeHouse' and tid == 2:
                a.label(lab); a.faceplayer(); a.opentext(); a.db(0x95, trade_marcel); a.waitbutton(); a.closetext(); a.end()
            else:
                a.label(lab); a.jumptextfaceplayer(lab + 't'); texts[lab + 't'] = rt(g, tid)
            obj_bytes.append([spr, o['y'] + 4, o['x'] + 4, mv, rng, 0xFF, 0xFF, typ, sight, lab, fl])
        for k, (x, y, tconst) in enumerate(bgl):
            L_ = 'bg%d' % k; a.label(L_); a.jumptext(L_ + 't'); texts[L_ + 't'] = rt(g, len(objs) + k + 1)
            bgs.append((y, x, 0, L_))
        for k, (x, y, fn, arg) in enumerate(P25.hidden(PM.map_const(n))):
            assert fn == 'HiddenItems'
            L_ = 'hi%d' % k; a.label(L_); a.dw(FL.new()); a.db(PM.item_id(arg)); bgs.append((y, x, 7, L_))
        for k_, v in texts.items():
            a.label(k_); a.raw(v if v[-1] in (0x50, 0x57, 0x58) else P12.text(v))
        a.label('mapscripts'); a.db(0, 0)
        a.label('events'); a.db(0, 0)
        wl = []
        for x, y, dest, wid in warps:
            if dest == 'LAST_MAP': wl.append((y, x, wid, *r2))
            elif dest == 'DIGLETTS_CAVE': wl.append((y, x, DIGLETT_ROUTE2_WARP, *mapid('DiglettsCave')))
            else: wl.append((y, x, wid, *mapids[CONST[dest]]))
        a.db(len(wl))
        for w_ in wl: a.db(*w_)
        a.db(0)
        a.db(len(bgs))
        for (y_, x_, t_, l_) in bgs: a.db(y_, x_, t_); a.dw(l_)
        a.db(len(obj_bytes))
        for ob in obj_bytes: a.db(*ob[:9]); a.dw(ob[9]); a.dw(ob[10])
        base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
        mp = maps[n]; blkp = sp.put(BANK, mp.blk)
        aa = sp.put(BANK, bytes([0x0A if tk != 'Forest' else 0x03, mp.h, mp.w, BANK, blkp & 0xFF, blkp >> 8, BANK,
                                 a.labels['mapscripts'] & 0xFF, a.labels['mapscripts'] >> 8, a.labels['events'] & 0xFF,
                                 a.labels['events'] >> 8, 0]))
        src_n, env = HDR_FROM[n]; hs = hdr_index(src_n)
        hh = GROUP26_END + 9 * (mapids[n][1] - G26_COUNT - 1)
        rom[hh:hh + 9] = bytes([BANK, ts_id[tk], env, aa & 0xFF, aa >> 8, rom[hs + 5], rom[hs + 6], 0x01 if tk == 'Forest' else rom[hs + 7],
                                 rom[hs + 8]])     # the forest: day colours (Red's)
        log.append('%s -> map %d:%d  scripts %X:%04X (%d bytes)' % (n, *mapids[n], BANK, base, len(blob)))

    # ================= Route 2
    objs, warps, bgl = objs_of['Route2']
    a = Asm(sp.here(BANK)); texts = {}; obj_bytes = []; bgs = []
    for idx, o in enumerate(objs):
        assert o['sprite'] == 'SPRITE_POKE_BALL'
        lab = 'o%d' % (idx + 1); a.label(lab); a.db(PM.item_id(o['extra'][0]), 1)
        obj_bytes.append([SPR['SPRITE_POKE_BALL'], o['y'] + 4, o['x'] + 4, 6, 0, 0xFF, 0xFF, 1, 0, lab, FL.new()])
    for k, (x, y, tconst) in enumerate(bgl):
        L_ = 'bg%d' % k; a.label(L_); a.jumptext(L_ + 't'); texts[L_ + 't'] = rt(RED_ROUTE2, len(objs) + k + 1)
        bgs.append((y, x, 0, L_))
    for k_, v in texts.items():
        a.label(k_); a.raw(v if v[-1] in (0x50, 0x57, 0x58) else P12.text(v))
    a.label('mapscripts'); a.db(0, 0)
    a.label('events'); a.db(0, 0)
    a.db(len(warps))
    for x, y, dest, wid in warps:
        a.db(y, x, wid, *mapids[CONST[dest]])
    a.db(0)
    a.db(len(bgs))
    for (y_, x_, t_, l_) in bgs: a.db(y_, x_, t_); a.dw(l_)
    a.db(len(obj_bytes))
    for ob in obj_bytes: a.db(*ob[:9]); a.dw(ob[9]); a.dw(ob[10])
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    rblk = sp.put(BANK, route.blk)
    log.append('Route2: Red events %X:%04X (%d bytes)' % (BANK, base, len(blob)))

    # ================= connections: Pewter (Red) directly, Viridian (Crystal) translated
    # (a strip is read from the bank of the blocks of the map it shows)
    hr2, hpw, hvi = hdr_index('Route2'), hdr_index('PewterCity'), hdr_index('ViridianCity')
    apw, avi = attrs(rom, hpw), attrs(rom, hvi)
    assert (apw['w'], apw['h'], avi['w'], avi['h']) == (20, 18, 20, 18)
    pw_blk = (apw['blkbank'], apw['blk']); vi_blk = (avi['blkbank'], avi['blk'])
    e = TS.entry(OVERWORLD_TS); co = fo(e[6], e[7] | e[8] << 8)
    g1side = X.gen1_side(tss['Overworld'], bytes(rom[co:co + 4 * 128])); crside = X.crystal_side(rom, TS)
    allhdr = [G[gi] + 9 * k for gi in range(26) for k in range((G[gi + 1] - G[gi]) // 9 if gi + 1 < 26 else FIRST_MAP + len(MAPS) - 1)]
    allhdr = [h_ for h_ in allhdr if rom[h_] and attrs(rom, h_)['scbank']]
    def conn_list(a_):
        o2 = a_['attr_off']; return [o2 + 12 + 12 * k for k in range(bin(a_['conn'] & 0xF).count('1'))]
    # Viridian's blocks move to BANK, next to their Gen I translation
    vblk = bytes(rom[fo(*vi_blk):fo(*vi_blk) + 360]); nvb = sp.put(BANK, vblk)
    for h_ in allhdr:
        for c in conn_list(attrs(rom, h_)):
            if (rom[c], rom[c + 1]) == vir:
                s_ = r16(c + 2); assert vi_blk[1] <= s_ < vi_blk[1] + 360, hex(h_); w16(c + 2, nvb + s_ - vi_blk[1])
    rom[avi['attr_off'] + 3] = BANK; w16(avi['attr_off'] + 4, nvb)
    x_vir = sp.put(BANK, X.translate(vblk, crside, g1side))                                  # Viridian in Gen I blocks
    x_r2 = sp.put(BANK, X.translate(red_route_blk, g1side, crside))                          # Route 2 in Crystal blocks
    north = P24.connection('north', W2, H2, pew, 20, 18, -5, pw_blk[1])
    south = P24.connection('south', W2, H2, vir, 20, 18, -5, x_vir)
    att = bytes([0x0F, H2, W2, BANK, rblk & 0xFF, rblk >> 8, BANK, a.labels['mapscripts'] & 0xFF,
                 a.labels['mapscripts'] >> 8, a.labels['events'] & 0xFF, a.labels['events'] >> 8, 0x0C]) + north + south
    aat = sp.put(BANK, att)
    rom[hr2 + 1] = OVERWORLD_TS; rom[hr2] = BANK; w16(hr2 + 3, aat)
    n_ = 0
    for c in conn_list(apw):
        if (rom[c], rom[c + 1]) == r2: rom[c:c + 12] = P24.connection('south', 20, 18, r2, W2, H2, 5, rblk); n_ += 1
    for c in conn_list(attrs(rom, hvi)):
        if (rom[c], rom[c + 1]) == r2: rom[c:c + 12] = P24.connection('north', 20, 18, r2, W2, H2, 5, x_r2); n_ += 1
    assert n_ == 2
    # Crystal's Diglett's Cave: its Route 2 end leads to Red's entrance
    a_ = attrs(rom, hdr_index('DiglettsCave')); ev = parse_events(rom, a_['scbank'], a_['events'])
    o_, w = ev['warps'][DIGLETT_ROUTE2_WARP - 1]; assert (w[3], w[4]) == r2
    rom[o_ + 2] = 3; rom[o_ + 3:o_ + 5] = bytes(mapids['DiglettsCaveRoute2'])

    # ================= wild Pokémon (Red): Route 2 replaced, Viridian Forest added
    # room: Johto's water table (just before) moves to the end of bank 0A, the Kanto grass table starts at its place
    kg = P15.KANTO_GRASS; jw = kg - 1 - 9 * JOHTO_WATER_N
    assert rom[kg - 1] == 0xFF and all(r16(o_ + 1) == 0x4000 + kg % 0x4000 for o_ in KG_REFS)
    assert all(rom[o_] == 0x21 and r16(o_ + 1) == 0x4000 + jw % 0x4000 for o_ in JW_REFS)
    njw = sp.put(0x0A, bytes(rom[jw:kg]))
    for o_ in JW_REFS: w16(o_ + 1, njw)
    p = kg; ents = []
    while rom[p] != 0xFF: ents.append(bytes(rom[p:p + 47])); p += 47
    end_old = p + 1
    rom[jw:end_old] = bytes(end_old - jw)
    for o_ in KG_REFS: w16(o_ + 1, 0x4000 + jw % 0x4000)
    p = jw; ents_ = ents; ents = []
    ents = ents_
    def red_wild(name, mp):
        t = open(PR + '/data/wild/maps/%s.asm' % name, encoding='utf-8').read()
        t = re.sub(r'IF DEF\(_BLUE\).*?ENDC', '', t, flags=re.S)
        rate = int(re.search(r'def_grass_wildmons (\d+)', t).group(1))
        slots = [(int(l), s) for l, s in re.findall(r'db\s+(\d+), (\w+)', t.split('end_grass_wildmons')[0])]
        assert len(slots) == 10, name
        pick = [slots[i] for i in (0, 1, 2, 3, 6, 8, 9)]
        return bytes([*mp, rate, rate, rate]) + bytes(sum(([lv, PM.MON[P10.MON_ALIAS.get(s, s)]] for lv, s in pick), [])) * 3
    assert any((x[0], x[1]) == r2 for x in ents)
    ents = [red_wild('Route2', r2) if (x[0], x[1]) == r2 else x for x in ents]
    ents.append(red_wild('ViridianForest', mapids['ViridianForest']))
    blob = b''.join(ents) + b'\xff'
    assert len(blob) <= end_old - jw + 7
    rom[jw:jw + len(blob)] = blob
    log.append('Kanto grass table 0A:%04X (%d entries), Johto water table 0A:%04X' % (0x4000 + jw % 0x4000, len(ents), njw))

    P17.fix_outdoor_sprites(rom, log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
