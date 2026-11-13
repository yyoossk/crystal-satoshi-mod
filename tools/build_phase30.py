#!/usr/bin/env python3
"""Phase 30: Route 1 and Pallet Town as in Red / the Pikachu full-color hack, with Red's start of the journey:
 * Ledges on the Gen I overworld tileset (Red's ledge tiles: down $36/$37, left $27, right $0D/$1D), so Red's maps
   (Route 1, Route 2, Viridian, Pewter, Cerulean, ...) have their one-way jumps instead of walls.
 * Route 1 (Red): the Poké Mart clerk with the Potion sample, the boy who explains ledges, the sign, Red's wild Pokémon.
 * Pallet Town (Red's layout, people and signs; Crystal's houses and Oak's lab behind the doors).  Route 21 (Crystal's)
   shows its edge drawn with the other tileset (blockxlat).
 * Without a Pokémon, walking north out of Pallet: Oak calls "Hey! Wait!", comes up, takes the player along to his lab;
   in the lab Oak walks to his desk with the player behind him, Shigeru is fed up with waiting, Oak's speech, then the
   player chooses.  Before that Oak is not in his lab (Shigeru: "Gramps isn't around"), the balls are only looked at,
   and the player may not leave the lab before choosing ("Hey! Don't go away yet!").
usage: build_phase30.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
import portmaps as PM
import pairwalls
import blockxlat as X
import redmap as RM
import redtexts as RT
from evedit import MapEvents
import build_phase10 as P10
import build_phase12 as P12
import build_phase15 as P15
import build_phase17 as P17
import build_phase21 as P21
import build_phase24 as P24
import build_phase25 as P25
import build_phase26 as P26
import build_phase27 as P27
import build_phase28 as P28
import build_phase29 as P29

P15.TS_CAP = P27.TS_CAP
FIRST_FLAG = 262                   # 256-261: phase 29
BANK = 0x71                        # free in the JP original
OVERWORLD_TS = 40
RED_PALLET, RED_ROUTE1, RED_LAB = 0x00, 0x0C, 0x28
EV_GOT_STARTER = P29.EV_GOT_STARTER
SPR_OAK = 0x05
MUSIC_PROF_OAK = 0x1E
COLL_HOP = {0x36: 0xA3, 0x37: 0xA3, 0x27: 0xA1, 0x0D: 0xA0, 0x1D: 0xA0}    # COLL_HOP_DOWN / LEFT / RIGHT
U, D, L, R_ = 0x0D, 0x0C, 0x0E, 0x0F
TU, TD, TL, TR = 1, 0, 2, 3
SPR = dict(P29.SPR); SPR['SPRITE_OAK'] = SPR_OAK
PALLET_WARPS = [(5, 5, 'RedsHouse1F'), (13, 5, 'BluesHouse'), (12, 11, 'OaksLab')]   # Crystal's maps (same doors)
# Oak (Red: from (8,5)) comes up below the player at the north exit, then leads him to the lab door (Red's route)
OAK_START = (8, 5)
OAK_TO = {10: [U, U, U, R_, R_], 11: [U, U, U, R_, R_, R_]}
OAK_LEAD = {10: [D] * 5 + [L] + [D] * 5 + [R_] * 3 + [U], 11: [L] + [D] * 5 + [L] + [D] * 5 + [R_] * 3 + [U]}
LAB_DOOR_IN = (4, 11)              # the lab's warp 1


# Red: a ledge is jumped only from the right tile (LedgeTiles: standing tile, ledge tile); elsewhere the same tiles are
# cliff walls.  Over all of Red's overworld maps each (block, quarter) is always one or the other.
LEDGE_REQ = {0x36: (0, -1, {0x39}), 0x37: (0, -1, {0x2C, 0x39}), 0x27: (1, 0, {0x2C, 0x39}),
             0x0D: (-1, 0, {0x2C, 0x39}), 0x1D: (-1, 0, {0x2C})}


def ledge_keys(ow):
    """{(block's 16 tile bytes, quarter)} of the real ledges"""
    import glob
    cs = open(PY + '/constants/map_constants.asm').read(); st = {}
    for f in sorted(glob.glob(PY + '/data/maps/headers/*.asm')):
        m = re.search(r'map_header (\w+), (\w+), OVERWORLD', open(f).read())
        if not m: continue
        n, c = m.groups(); mm = re.search(r'map_const %s,\s*(\d+),\s*(\d+)' % c, cs)
        w, h = int(mm.group(1)), int(mm.group(2)); mp = MapPort(n, ow, w, h, n + '.blk')
        for y in range(2 * h):
            for x in range(2 * w):
                b, q = mp.block_at(x, y); t = ow.quad_tile(b, q)
                if t not in LEDGE_REQ: continue
                dx, dy, ok = LEDGE_REQ[t]; nx, ny = x + dx, y + dy
                v = 0 <= nx < 2 * w and 0 <= ny < 2 * h and ow.quad_tile(*mp.block_at(nx, ny)) in ok
                st.setdefault((bytes(ow.blocks[16 * b:16 * b + 16]), q), set()).add(v)
    assert all(len(v) == 1 for v in st.values())
    return {k for k, v in st.items() if True in v}


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (0x2A, BANK):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1 if f > b * 0x4000 else f, b * 0x4000 + 0x4000)
    log = []
    FL = PM.Flags(FIRST_FLAG)
    pal, r1, r21, vir = mapid('PalletTown'), mapid('Route1'), mapid('Route21'), mapid('ViridianCity')
    lab_id = mapid('OaksLab')
    TS = PM.Tilesets(rom, sp)
    got_potion, pal_oak_hide, oak_led, intro_done, oak_away = (FL.new() for _ in range(5))

    def hl(mapid_, tid, **kw):
        return [RM.crystal_text(b, p) for b, p in RM.asm_hl(mapid_, tid, **kw) if RM.R[RM.fo(b, p)] in (0x00, 0x17)]
    def rt(mapid_, tid):
        b, p = RM.text_ptr(mapid_, tid); k, v = RM.text_body(b, p)
        if k == 'text': return RM.crystal_text(b, p)
        return hl(mapid_, tid)[0]
    def riv(b): return P29.riv(b)
    def put_texts(a, texts):
        for k_, v in texts.items():
            assert k_ not in a.labels, k_
            a.label(k_); a.raw(v if v[-1] in (0x50, 0x57, 0x58) else P12.text(v))

    # ================= the Gen I overworld tileset: Red's ledges, the doors of Pallet Town
    ow = Tileset('Overworld', 0, 'overworld.bst', SC + '/out/pk_overworld.pkl', water=0x14, grass=0x52)
    town = MapPort('PalletTown', ow, 10, 9, 'PalletTown.blk')
    route = MapPort('Route1', ow, 10, 18, 'Route1.blk')
    e = TS.entry(OVERWORLD_TS); am_, ac_ = e[4] | e[5] << 8, e[7] | e[8] << 8
    assert e[3] == e[6]; nb0 = (ac_ - am_) // 16
    meta = bytes(rom[fo(e[3], am_):fo(e[3], am_) + 16 * nb0]); coll = bytearray(rom[fo(e[6], ac_):fo(e[6], ac_) + 4 * nb0])
    nl = 0; hop_ok = ledge_keys(ow)
    for b_ in range(nb0):
        for q in range(4):
            r_, c_ = ((1, 0), (1, 2), (3, 0), (3, 2))[q]
            t = meta[16 * b_ + 4 * r_ + c_]
            if (bytes(meta[16 * b_:16 * b_ + 16]), q) in hop_ok and coll[4 * b_ + q] == COLL_WALL:
                coll[4 * b_ + q] = COLL_HOP[t]; nl += 1
    ow.coll = bytearray(coll[:4 * ow.nblocks])
    ov = {'PalletTown': {(x, y): P25.warp_override(ow, town, x, y) for x, y, d in PALLET_WARPS}}
    meta2, coll2, blks = pairwalls.variants(ow, meta, bytes(coll), {'PalletTown': town, 'Route1': route}, [], ov)
    meta2, coll2, blks = P27.block0_copy(meta2, coll2, blks)
    assert len(coll2) // 4 <= 256
    am = sp.put(BANK, meta2 + coll2); t0 = TS.tab + 15 * OVERWORLD_TS
    rom[t0 + 3] = BANK; w16(t0 + 4, am); rom[t0 + 6] = BANK; w16(t0 + 7, am + len(meta2))
    town.blk, route.blk = blks['PalletTown'], blks['Route1']
    log.append('tileset Overworld: %d ledge quarters, %d blocks (+%d)' % (nl, len(coll2) // 4, len(coll2) // 4 - nb0))

    # ================= Route 1
    objs, warps, bgl = P25.red_objects('Route1'); assert not warps
    me = MapEvents(rom, 'Route1')
    a = Asm(sp.here(BANK)); a.bank = BANK; texts = {}
    me.objs = []; me.bgs = []; me.coords = []; me.callbacks = []; me.scenes = []
    for idx, o in enumerate(objs):
        tid = idx + 1; L_ = 'o%d' % tid; mv, rng = P25.face((0, 0, 0, o['move'], o['face']))
        me.objs.append([bytearray([SPR[o['sprite']], o['y'] + 4, o['x'] + 4, mv, rng, 0xFF, 0xFF, 0, 0, 0, 0, 0xFF, 0xFF]), L_])
    # the clerk's Potion sample
    b6, _ = RM.text_ptr(RED_ROUTE1, 1)
    texts.update(o1g=RM.crystal_text(b6, 0x4437), o1f=RM.crystal_text(b6, 0x44D1), o1x=RM.crystal_text(b6, 0x44A6))
    a.label('o1'); a.faceplayer(); a.opentext(); a.checkevent(got_potion); a.iftrue('o1e')
    a.writetext('o1g'); a.verbosegiveitem(P15.item_id('POTION'), 1); a.iffalse('o1z'); a.setevent(got_potion)
    a.closetext(); a.end()
    a.label('o1z'); a.writetext('o1f'); a.waitbutton(); a.closetext(); a.end()
    a.label('o1e'); a.writetext('o1x'); a.waitbutton(); a.closetext(); a.end()
    a.label('o2'); a.jumptextfaceplayer('o2t'); texts['o2t'] = rt(RED_ROUTE1, 2)
    for k, (x, y, tconst) in enumerate(bgl):
        L_ = 'rs%d' % k; a.label(L_); a.jumptext(L_ + 't'); texts[L_ + 't'] = rt(RED_ROUTE1, len(objs) + 1 + k)
        me.bgs.append((y, x, 0, L_))
    put_texts(a, texts)
    me.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    me.install(a)
    log.append('Route1: Red events %X:%04X (%d bytes)' % (BANK, base, len(blob)))

    # ================= Pallet Town
    objs, warps_red, bgl = P25.red_objects('PalletTown')
    assert [(x, y) for x, y, *_ in warps_red] == [(x, y) for x, y, d in PALLET_WARPS]
    me = MapEvents(rom, 'PalletTown')
    old_warps = list(me.warps)
    assert [(w[1], w[0]) for w in old_warps] == [(x, y) for x, y, d in PALLET_WARPS]
    a = Asm(sp.here(BANK)); a.bank = BANK; texts = {}
    me.objs = []; me.bgs = []; me.coords = []
    a.label('end'); a.end()
    for idx, o in enumerate(objs):
        tid = idx + 1; L_ = 'p%d' % tid; mv, rng = P25.face((0, 0, 0, o['move'], o['face']))
        fl = pal_oak_hide if tid == 1 else 0xFFFF
        me.objs.append([bytearray([SPR[o['sprite']], o['y'] + 4, o['x'] + 4, mv, rng, 0xFF, 0xFF, 0, 0, 0, 0,
                                   fl & 0xFF, fl >> 8]), L_])
        if tid == 1: a.label(L_); a.end()
        else: a.label(L_); a.jumptextfaceplayer(L_ + 't'); texts[L_ + 't'] = rt(RED_PALLET, tid)
    assert objs[0]['sprite'] == 'SPRITE_OAK' and (objs[0]['x'], objs[0]['y']) == OAK_START
    for k, (x, y, tconst) in enumerate(bgl):
        L_ = 'ps%d' % k; a.label(L_); a.jumptext(L_ + 't'); texts[L_ + 't'] = riv(rt(RED_PALLET, len(objs) + 1 + k))
        me.bgs.append((y, x, 0, L_))
    # Oak stops the player at the north exit (no Pokémon yet)
    texts['hey'] = P28.jp(RM.fo(6, 0x4FB0)); texts['unsafe'] = RM.crystal_text(6, 0x4FE2)
    oak = 2
    for x in (10, 11):
        L_ = 'stop%d' % x; me.coords.append((0xFF, 1, x, L_))
        a.label(L_); a.checkevent(EV_GOT_STARTER); a.iftrue('end'); a.checkevent(oak_led); a.iftrue('end')
        a.playmusic(MUSIC_PROF_OAK); a.turnobject(0, TD)
        a.opentext(); a.writetext('hey'); a.waitbutton(); a.closetext()
        a.showemote(0, 0, 15)
        a.moveobject(oak, *OAK_START); a.appear(oak); a.applymovement(oak, 'oto%d' % x); a.turnobject(0, TD)
        a.opentext(); a.writetext('unsafe'); a.waitbutton(); a.closetext()
        a.db(0x6F, oak, 0)                                                     # follow Oak, PLAYER
        a.applymovement(oak, 'olead%d' % x); a.db(0x70)                        # stopfollow
        a.disappear(oak); a.setevent(oak_led); a.warp(*lab_id, *LAB_DOOR_IN); a.end()
        a.label('oto%d' % x); a.db(*OAK_TO[x], 0x47)
        a.label('olead%d' % x); a.db(*OAK_LEAD[x], 0x47)
    a.label('pcb'); a.setevent(pal_oak_hide); a.endcallback()
    me.callbacks.append((2, 'pcb'))
    me.warps = [bytes([y, x, w[2], w[3], w[4]]) for (x, y, d), w in zip(PALLET_WARPS, old_warps)]
    put_texts(a, texts)
    me.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    me.install(a)
    log.append('PalletTown: Red events %X:%04X (%d bytes)' % (BANK, base, len(blob)))

    # ================= blocks and connections: Route 1 joins Viridian and Pallet directly; Route 21 translated
    e = TS.entry(OVERWORLD_TS); co = fo(e[6], e[7] | e[8] << 8)
    g1side = X.gen1_side(ow, bytes(rom[co:co + 4 * 128])); crside = X.crystal_side(rom, TS)
    def conns(hdr):
        a_ = attrs(rom, hdr); o2 = a_['attr_off']
        return [o2 + 12 + 12 * k for k in range(bin(a_['conn'] & 0xF).count('1'))]
    hpal, hr1, hr21, hvir = hdr_index('PalletTown'), hdr_index('Route1'), hdr_index('Route21'), hdr_index('ViridianCity')
    avir, ar21 = attrs(rom, hvir), attrs(rom, hr21)
    assert (ar21['w'], ar21['h']) == (10, 18)
    pblk = sp.put(BANK, town.blk); rblk = sp.put(BANK, route.blk)
    xpal = sp.put(BANK, X.translate(MapPort('PalletTown', ow, 10, 9, 'PalletTown.blk').blk, g1side, crside))
    r21blk = bytes(rom[fo(ar21['blkbank'], ar21['blk']):][:180])
    assert ar21['blkbank'] == 0x2A
    x21 = sp.put(0x2A, X.translate(r21blk[:30], crside, g1side))            # its top rows: Pallet's strip
    for h_, nm, border, blk in ((hpal, 'PalletTown', border_of('PalletTown'), pblk), (hr1, 'Route1', border_of('Route1'), rblk)):
        a_ = attrs(rom, h_); ao = a_['attr_off']
        rom[h_ + 1] = OVERWORLD_TS; rom[ao] = border; rom[ao + 3] = BANK; w16(ao + 4, blk)
    want = {(hr1, vir): P24.connection('north', 10, 18, vir, 20, 18, -5, avir['blk']),
            (hr1, pal): P24.connection('south', 10, 18, pal, 10, 9, 0, pblk),
            (hvir, r1): P24.connection('south', 20, 18, r1, 10, 18, 5, rblk),
            (hpal, r1): P24.connection('north', 10, 9, r1, 10, 18, 0, rblk),
            (hpal, r21): P24.connection('south', 10, 9, r21, 10, 18, 0, x21),
            (hr21, pal): P24.connection('north', 10, 18, pal, 10, 9, 0, xpal)}
    assert avir['blkbank'] == P29.BANK
    done = set()
    for (h_, tgt), cb in want.items():
        for c in conns(h_):
            if (rom[c], rom[c + 1]) == tgt: rom[c:c + 12] = cb; done.add((h_, tgt))
    assert len(done) == len(want), set(want) - done

    # ================= Route 1's wild Pokémon (Red)
    kg = P27.kanto_grass(rom); p = kg
    while (rom[p], rom[p + 1]) != r1:
        assert rom[p] != 0xFF; p += 47
    t = open(PR + '/data/wild/maps/Route1.asm', encoding='utf-8').read()
    t = re.sub(r'IF DEF\(_BLUE\).*?ENDC', '', t, flags=re.S)
    rate = int(re.search(r'def_grass_wildmons (\d+)', t).group(1))
    slots = [(int(l_), s) for l_, s in re.findall(r'db\s+(\d+), (\w+)', t.split('end_grass_wildmons')[0])]
    pick = [slots[i] for i in (0, 1, 2, 3, 6, 8, 9)]
    rom[p:p + 47] = bytes([*r1, rate, rate, rate]) + bytes(sum(([lv, PM.MON[P10.MON_ALIAS.get(s, s)]] for lv, s in pick), [])) * 3

    # ================= Oak's lab: Red's arrival with Oak, Oak away before it, the balls, "don't go away yet"
    lab = MapEvents(rom, 'OaksLab')
    assert lab.objs[0][0][0] == SPR_OAK; oak_ref = P29.oak_talk(lab)
    lab.objs[0][0][11] = oak_away & 0xFF; lab.objs[0][0][12] = oak_away >> 8
    rv = [i for i, (o_, r) in enumerate(lab.objs) if o_[0] == P17.SPR_BLUE][0] + 2
    a = Asm(sp.here(BANK)); a.bank = BANK; texts = {}
    a.label('end'); a.end()
    t5 = hl(RED_LAB, 5, n=400, stop=False)
    texts.update(fedup=riv(rt(RED_LAB, 17)), choose=riv(rt(RED_LAB, 18)), meto=riv(rt(RED_LAB, 19)),
                 patient=riv(rt(RED_LAB, 20)), dontgo=riv(hl(RED_LAB, 12)[0]), which=riv(t5[1]),
                 ball=hl(RED_LAB, 2)[0])
    # objects callback: Oak away until he brought the player; at the door when he comes in with him
    old_cb = [r for t_, r in lab.callbacks if t_ == 2]; assert len(old_cb) == 1
    a.label('lcb'); a.clearevent(oak_away)
    a.checkevent(EV_GOT_STARTER); a.iftrue('lcb_x'); a.checkevent(oak_led); a.iftrue('lcb_l')
    a.setevent(oak_away); a.sjump('lcb_x')
    a.label('lcb_l'); a.checkevent(intro_done); a.iftrue('lcb_x'); a.moveobject(2, LAB_DOOR_IN[0], LAB_DOOR_IN[1] - 1)
    a.label('lcb_x'); a.farsjump(old_cb[0][1], old_cb[0][2])
    lab.callbacks = [(t_, r) for t_, r in lab.callbacks if t_ != 2] + [(2, 'lcb')]
    # scene: Oak walks to his desk, the player behind him; Shigeru and Oak talk
    a.label('lsc'); a.checkevent(oak_led); a.iffalse('end'); a.checkevent(intro_done); a.iftrue('end')
    a.checkevent(EV_GOT_STARTER); a.iftrue('end')
    a.db(0x6F, 2, 0); a.applymovement(2, 'lmv'); a.db(0x70)
    a.turnobject(2, TD); a.turnobject(0, TU); a.turnobject(rv, TU); a.playmapmusic()
    for k in ('fedup', 'choose', 'meto', 'patient'):
        a.opentext(); a.writetext(k); a.waitbutton(); a.closetext()
    a.setevent(intro_done)
    a.loadmem(P17.W_FW_SLOT, 0xFF)    # no follower until Shigeru left the lab (phase 17 sets it back to 0)
    a.end()
    a.label('lmv'); a.db(*([U] * 8), 0x47)
    lab.scenes = ['lsc']
    # "don't go away yet" (Red: the row in front of the bookshelves)
    for x in (4, 5):
        L_ = 'dg%d' % x; lab.coords.append((0xFF, 6, x, L_))
        a.label(L_); a.checkevent(EV_GOT_STARTER); a.iftrue('end'); a.checkevent(intro_done); a.iffalse('end')
        a.turnobject(2, TD); a.opentext(); a.writetext('dontgo'); a.waitbutton(); a.closetext()
        a.applymovement(0, 'mv_u'); a.end()
    a.label('mv_u'); a.db(U, 0x47)
    # the balls: only looked at until Oak asked to choose
    for i in (1, 2, 3):
        ref = lab.objs[i][1]; assert ref[0] == 'far'
        L_ = 'ball%d' % i; lab.objs[i][1] = L_
        a.label(L_); a.checkevent(intro_done); a.iftrue(L_ + 'g'); a.checkevent(EV_GOT_STARTER); a.iftrue(L_ + 'g')
        a.jumptext('ball')
        a.label(L_ + 'g'); a.farsjump(ref[1], ref[2])
    # Oak, no Pokémon yet (after the arrival): "which one, <PLAYER>?"
    a.label('owhich'); a.writetext('which'); a.waitbutton(); a.closetext(); a.end()
    put_texts(a, texts)
    lab.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    lab.install(a)
    log.append('OaksLab: events %X:%04X (%d bytes)' % (BANK, base, len(blob)))
    # phase 29's Oak script: no starter -> Red's line instead of the base mod's speech (faceplayer / opentext first)
    p_ = fo(*oak_ref); assert rom[p_] == 0x04 and rom[p_ + 1] == P29.BANK
    s29 = fo(P29.BANK, r16(p_ + 2)); seg = bytes(rom[s29:s29 + 0x600])
    pre = seg.index(bytes([0x04, *P29.OAK_BASE_PRE[:1], P29.OAK_BASE_PRE[1] & 0xFF, P29.OAK_BASE_PRE[1] >> 8]))
    b2 = Asm(sp.here(BANK)); b2.bank = BANK
    b2.faceplayer(); b2.opentext(); b2.farsjump(BANK, a.labels['owhich'])
    q = sp.put(BANK, b2.done())
    rom[s29 + pre:s29 + pre + 4] = bytes([0x04, BANK, q & 0xFF, q >> 8])

    # ================= scene table: the lab's arrival scene (shares phase 28's always-0 scene byte)
    sr = P21.SCENES_REF
    tb = fo(rom[sr], r16(sr + 3)); n_ = 0
    while rom[tb + 4 * n_] != 0xFF: n_ += 1
    tab = bytes(rom[tb:tb + 4 * n_])
    assert all(tab[4 * i:4 * i + 2] != bytes(lab_id) for i in range(n_))
    tab += bytes([*lab_id, P28.SCENE_AREAS & 0xFF, P28.SCENE_AREAS >> 8])
    assert rom[sr] == 0x61 and tb + len(tab) + 1 <= 0x61 * 0x4000 + 0x4000 and not any(rom[tb + 4 * n_ + 1:tb + len(tab) + 1])
    rom[tb:tb + len(tab) + 1] = tab + b'\xff'                                # grown in place (free bytes after it)

    P17.fix_outdoor_sprites(rom, log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    assert FL.i < 8 * (P28.SCENE_AREAS - 0xDA01)
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
