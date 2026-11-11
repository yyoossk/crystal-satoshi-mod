#!/usr/bin/env python3
"""Phase 26: Pewter City as in Red / the Pikachu full-color hack, for good, with the Pewter Museum of Science:
 * Red's town (Gen I overworld tileset) in place of Crystal's: Red's people and signs; the boy who walks the player
   to the gym when leaving east before beating Brock (or when talked to), the man who walks the player to the museum
   when he says he has not been there.  Routes 2 and 3 stay Crystal's for now (each side shows the other's edge drawn
   with its own tileset).  Crystal's Pokémon Center, Mart, Gym and the two houses are used for those doors.
 * Museum 1F / 2F (Gen I museum tileset): the ¥50 ticket (asked when stepping in front of the counter; the ticket is
   good until the player is back in Pewter), the man behind the counter, the fossils (Aerodactyl / Kabutops shown),
   the Old Amber on display and the scientist in the back room who gives it, the space exhibition upstairs.
usage: build_phase26.py IN.gbc OUT.gbc OUT.ips
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
from evedit import MapEvents
import build_phase12 as P12
import build_phase15 as P15
import build_phase17 as P17
import build_phase19 as P19
import build_phase25 as P25

FIRST_FLAG = 227                   # 205-226: phase 25
FIRST_MAP = 79                     # 26:72-78 = phase 25
BANK, BANK2 = 0x67, 0x68           # free in the JP original
OVERWORLD_TS = 40
RED_PEWTER, RED_MUSEUM1F, RED_MUSEUM2F = 0x02, 0x34, 0x35
BOULDER_BADGE = 0x23               # engine flag
SPAWN_TABLE = 0x15346
MUSIC_SHOW_ME_AROUND = 0x11
SPECIAL_MONEY_TOP_RIGHT = 0x5E
SFX_TRANSACTION = 0x22
VAR_X, VAR_Y = 0x12, 0x13
NEIGHBOURS = ['Route2', 'Route3']
U, D, L, R_ = 0x0D, 0x0C, 0x0E, 0x0F                  # step up / down / left / right
MAPS = [('Museum1F', RED_MUSEUM1F), ('Museum2F', RED_MUSEUM2F)]
OLD_AMBER_SPRITE = 0x13C10         # PKFC OldAmberSprite (4 tiles)
SPR = dict(P25.SPR)
TOWN_OBJS = [(8, 15, 'SPRITE_COOLTRAINER_F', 'STAY', 'NONE', 1), (17, 25, 'SPRITE_COOLTRAINER_M', 'STAY', 'NONE', 2),
             (27, 17, 'SPRITE_SUPER_NERD', 'STAY', 'NONE', 3), (26, 25, 'SPRITE_SUPER_NERD', 'WALK', 'LEFT_RIGHT', 4),
             (35, 16, 'SPRITE_YOUNGSTER', 'STAY', 'DOWN', 5)]
TOWN_SIGNS = [(19, 29, 6), (33, 19, 7), (24, 17, 8), (14, 25, 9), (15, 9, 10), (11, 17, 11), (25, 23, 12)]
TOWN_WARPS = [(14, 7, 'Museum1F', 1), (19, 5, 'Museum1F', 3), (16, 17, 'PewterGym', None),
              (29, 13, 'PewterNidoranSpeechHouse', None), (23, 17, 'PewterMart', None),
              (7, 29, 'PewterSnoozeSpeechHouse', None), (13, 25, 'PewterPokecenter1F', None)]
# the museum guy (27,17): the player first gets right below him, then follows him (Red's route)
MUSEUM_GUY = (27, 17)
MUSEUM_PRE = {(27, 16): [L, D]}           # he walks up first: only from above the player has to step aside
MUSEUM_PATH = [U] * 6 + [L] * 13 + [U] * 3 + [L]
# the gym guy (35,16): Red's route (the player follows him; he leaves to the left first)
GYM_GUY = (35, 16)
GYM_TRIGGERS = [(35, 17), (36, 17), (37, 18), (37, 19)]
GYM_PRE = {(35, 17): [R_, U], (36, 17): [U], (37, 18): [U, U, L], (37, 19): [U, U, U, L]}   # he walks down first
GYM_PATH = [D] * 2 + [L] * 15 + [U] * 5 + [L] * 11 + [D] * 5 + [R_] * 3


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (0x05, 0x12, BANK, BANK2):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1 if f > b * 0x4000 else f, b * 0x4000 + 0x4000)
    g0 = fo(0x13, 0x7AAB)                                  # the gap left in bank 13 (palette maps)
    while rom[g0 - 1]: g0 += 1
    g1 = g0
    while g1 < fo(0x13, 0x8000) and not any(rom[g1:g1 + 16]): g1 += 1
    sp.set_area(0x13, g0 + 1, g1)
    log = []
    FL = PM.Flags(FIRST_FLAG)
    pew = mapid('PewterCity')
    mapids = {n: (G26, FIRST_MAP + i) for i, (n, g) in enumerate(MAPS)}
    TS = PM.Tilesets(rom, sp)

    # ================= the Old Amber sprite (second sprite table of phase 14: moved, one entry more)
    import build_phase14 as P14
    import build_phase10 as P10
    pk = open(P10.PKFC, 'rb').read()
    stubs = []
    for off, d in P14.OW_READERS:
        assert rom[off] == 0xCD; s_ = fo(0x05, r16(off + 1))
        assert rom[s_:s_ + 2] == bytes([0xFE, 0x67]) and rom[s_ + 8] == 0x21
        stubs.append((s_, d))
    virt = r16(stubs[0][0] + 9) - stubs[0][1]
    t2 = virt + 0x66 * 6; n2 = len(P14.NEW_SPRITES)
    tab = bytes(rom[fo(0x05, t2):fo(0x05, t2) + 6 * n2])
    ga = sp.put(BANK2, pk[OLD_AMBER_SPRITE:OLD_AMBER_SPRITE + 4 * 16])
    tab += bytes([ga & 0xFF, ga >> 8, 0x40, BANK2, 3, 3])
    nt = sp.put(0x05, tab); nv = nt - 0x66 * 6
    for s_, d in stubs: w16(s_ + 9, nv + d)
    SPR['SPRITE_OLD_AMBER'] = 0x67 + n2
    log.append('Old Amber sprite -> id %02X' % SPR['SPRITE_OLD_AMBER'])

    # ================= tilesets: Museum new; Overworld variant blocks for Pewter's warps
    ow = Tileset('Overworld', 0, 'overworld.bst', SC + '/out/pk_overworld.pkl', water=0x14, grass=0x52)
    mus = Tileset('Museum', 10, 'gate.bst', SC + '/out/pk_museum.pkl')
    for b_ in range(mus.nblocks):                          # Red: people are talked to over tiles $17 / $32
        for q in range(4):
            if mus.quad_tile(b_, q) in (0x17, 0x32): mus.coll[4 * b_ + q] = 0x90      # COLL_COUNTER
    maps = {}; objs_of = {}
    for n, g in MAPS:
        h = RM.header(g); maps[n] = MapPort(n, mus, h['w'], h['h'], n + '.blk')
        objs_of[n] = P25.red_objects(n)
    town = MapPort('PewterCity', ow, 20, 18, 'PewterCity.blk')
    # the stairs (bottom row): warp at once, as in Red, but no step down on arriving (COLL_STAIRCASE_73)
    ov = {n: {(x, y): 0x73 if d.startswith('MUSEUM') else P25.warp_override(mus, maps[n], x, y)
              for x, y, d, w in objs_of[n][1]} for n in maps}
    meta2, coll2, blks = pairwalls.variants(mus, bytes(mus.blocks), bytes(mus.coll), maps, [], ov)
    # Crystal's GetCoordTile takes block 0 for a wall: Red's museum walks on it (the dark floor) -> a copy of it
    z = len(coll2) // 4
    meta2 = meta2 + meta2[:16]; coll2 = coll2 + coll2[:4]
    mus.blocks = meta2; mus.coll = bytearray(coll2); mus.nblocks = len(coll2) // 4
    for n in maps: maps[n].blk = bytes(z if v == 0 else v for v in blks[n])
    mus_ts = TS.add(mus, BANK, log)
    e = TS.entry(OVERWORLD_TS); am_, ac_ = e[4] | e[5] << 8, e[7] | e[8] << 8; nb0 = (ac_ - am_) // 16
    meta = bytes(rom[fo(e[3], am_):fo(e[3], am_) + 16 * nb0]); coll = bytes(rom[fo(e[6], ac_):fo(e[6], ac_) + 4 * nb0])
    tov = {(x, y): P25.warp_override(ow, town, x, y) for x, y, dn, w in TOWN_WARPS}
    meta2, coll2, blks = pairwalls.variants(ow, meta, coll, {'PewterCity': town}, [], {'PewterCity': tov})
    am = sp.put(BANK2, meta2 + coll2); t0 = TS.tab + 15 * OVERWORLD_TS
    rom[t0 + 3] = BANK2; w16(t0 + 4, am); rom[t0 + 6] = BANK2; w16(t0 + 7, am + len(meta2))
    town.blk = blks['PewterCity']
    log.append('tileset Overworld: %d blocks (+%d)' % (len(coll2) // 4, len(coll2) // 4 - nb0))

    def rt(mapid, tid):
        b, p = RM.text_ptr(mapid, tid); k, v = RM.text_body(b, p); assert k == 'text', (hex(mapid), tid)
        return RM.crystal_text(b, p)
    def hl(mapid, tid, **kw):
        return [RM.crystal_text(b, p) for b, p in RM.asm_hl(mapid, tid, **kw) if RM.R[RM.fo(b, p)] in (0x00, 0x17)]
    ticket = FL.new(); got_amber = FL.new()

    # ================= headers 26:79-80 (move what lies there)
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
                rom[hdr] = BANK2; w16(hdr + 3, sp.put(BANK2, bytes(rom[ao_:ao_ + size])))
                log.append('moved map attributes %X:%04X' % (ab, ap))
    rom[lo:hi] = bytes(hi - lo)

    # ================= the museum
    hc = hdr_index('PewterSnoozeSpeechHouse'); hcity = hdr_index('PewterCity')
    for n, g in MAPS:
        objs, warps, bgl = objs_of[n]
        a = Asm(sp.here(BANK)); a.bank = BANK; texts = {}; obj_bytes = []; bgs = []; coords = []
        a.label('end'); a.end()
        amber_oid = next((i + 2 for i, o in enumerate(objs) if o['sprite'] == 'SPRITE_OLD_AMBER'), None)
        for idx, o in enumerate(objs):
            tid = idx + 1; lab = 'o%d' % tid; fl = 0xFFFF
            mv, rng = P25.face((0, 0, 0, o['move'], o['face']))
            spr = SPR[o['sprite']]
            if n == 'Museum1F' and tid == 1:
                museum_counter(a, lab, texts, hl(g, 1, n=400, stop=False)[:9], ticket)
            elif n == 'Museum1F' and tid == 3:
                give, recv, full, again = hl(g, 3, n=200, stop=False)[:4]
                a.label(lab); a.faceplayer(); a.opentext(); a.checkevent(got_amber); a.iftrue(lab + 'a')
                a.writetext(lab + 'g'); a.db(0x1F, P12.OLD_AMBER, 1); a.iffalse(lab + 'f')       # giveitem
                a.setevent(got_amber); a.disappear(amber_oid); a.writetext(lab + 'r'); a.waitbutton(); a.closetext(); a.end()
                a.label(lab + 'f'); a.writetext(lab + 'x'); a.waitbutton(); a.closetext(); a.end()
                a.label(lab + 'a'); a.writetext(lab + 'y'); a.waitbutton(); a.closetext(); a.end()
                texts.update({lab + 'g': give, lab + 'r': recv, lab + 'x': full, lab + 'y': again})
            elif n == 'Museum1F' and o['sprite'] == 'SPRITE_OLD_AMBER':
                fl = got_amber
                a.label(lab); a.jumptext(lab + 't'); texts[lab + 't'] = hl(g, tid)[0]
            elif n == 'Museum1F':
                a.label(lab); a.jumptextfaceplayer(lab + 't'); texts[lab + 't'] = hl(g, tid)[0]
            else:
                a.label(lab); a.jumptextfaceplayer(lab + 't'); texts[lab + 't'] = rt(g, tid)
            obj_bytes.append([spr, o['y'] + 4, o['x'] + 4, mv, rng, 0xFF, 0xFF, 0, 0, lab, fl])
        for k, (x, y, tconst) in enumerate(bgl):
            L_ = 'bg%d' % k; a.label(L_); a.jumptext(L_ + 't'); texts[L_ + 't'] = rt(g, len(objs) + k + 1)
            bgs.append((y, x, 0, L_))
        for k, (x, y, fn, arg) in enumerate(P25.hidden(PM.map_const(n))):
            mon, nm = {'AerodactylFossil': (0x8E, 'プテラの　カセキ'), 'KabutopsFossil': (0x8D, 'カブトプスの　カセキ')}[fn]
            i = RT.R.index(encode(nm).rstrip(b'\x50')); s_ = RT.R.rindex(0x00, i - 40, i)
            assert RT.R[s_ + 1] != 0
            L_ = 'fos%d' % k; a.label(L_); a.callasm(BANK2, fossil_pic(sp, mon, fn)); a.waitbutton(); a.closepokepic()
            a.jumptext(L_ + 't'); texts[L_ + 't'] = RT.raw(s_) + b'\x57'
            bgs.append((y, x, 1, L_))                                                                  # facing up
        if n == 'Museum1F':
            for x in (9, 10):                                      # Red: in front of the counter, no ticket yet
                L_ = 'ct%d' % x; a.label(L_); a.checkevent(ticket); a.iftrue('end'); a.sjump('o1buy')
                coords.append((4, x, L_))
        for k_, v in texts.items():
            a.label(k_); a.raw(v if v[-1] in (0x50, 0x57, 0x58) else P12.text(v))
        a.label('mapscripts'); a.db(0, 0)
        a.label('events'); a.db(0, 0)
        wl = []
        for x, y, dest, wid in warps:
            if dest == 'LAST_MAP': wl.append((y, x, wid, *pew))
            else: wl.append((y, x, wid, *mapids[{'MUSEUM_1F': 'Museum1F', 'MUSEUM_2F': 'Museum2F'}[dest]]))
        a.db(len(wl))
        for w_ in wl: a.db(*w_)
        a.db(len(coords))
        for y_, x_, l_ in coords: a.db(0xFF, y_, x_, 0); a.dw(l_); a.db(0, 0)
        a.db(len(bgs))
        for (y_, x_, t_, l_) in bgs: a.db(y_, x_, t_); a.dw(l_)
        a.db(len(obj_bytes))
        for ob in obj_bytes: a.db(*ob[:9]); a.dw(ob[9]); a.dw(ob[10])
        base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
        mp = maps[n]; blkp = sp.put(BANK, mp.blk)
        aa = sp.put(BANK, bytes([border_of(n), mp.h, mp.w, BANK, blkp & 0xFF, blkp >> 8, BANK,
                                 a.labels['mapscripts'] & 0xFF, a.labels['mapscripts'] >> 8, a.labels['events'] & 0xFF,
                                 a.labels['events'] >> 8, 0]))
        hh = GROUP26_END + 9 * (mapids[n][1] - G26_COUNT - 1)
        rom[hh:hh + 9] = bytes([BANK, mus_ts, 3, aa & 0xFF, aa >> 8, rom[hcity + 5], rom[hc + 6], rom[hc + 7], rom[hc + 8]])
        log.append('%s -> map %d:%d  scripts %X:%04X (%d bytes)' % (n, *mapids[n], BANK, base, len(blob)))

    # ================= Pewter City
    me = MapEvents(rom, 'PewterCity')
    old_warps = list(me.warps)
    a = Asm(sp.here(BANK)); a.bank = BANK; texts = {}
    me.objs = []; me.bgs = []; me.coords = []
    oid = {}
    for o in TOWN_OBJS:
        x, y, sprite, move, fc, tid = o
        L_ = 'p%d' % tid; mv, rng = P25.face(o)
        me.objs.append([bytearray([SPR[sprite], y + 4, x + 4, mv, rng, 0xFF, 0xFF, 0, 0, 0, 0, 0xFF, 0xFF]), L_])
        oid[tid] = len(me.objs) + 1
        if tid in (1, 2):
            a.label(L_); a.jumptextfaceplayer(L_ + 't'); texts[L_ + 't'] = rt(RED_PEWTER, tid)
    # super nerd 2: "do you know what I'm doing?"
    q, yes, no = hl(RED_PEWTER, 4)[:3]
    a.label('p4'); a.faceplayer(); a.opentext(); a.writetext('p4q'); a.yesorno(); a.iffalse('p4n')
    a.writetext('p4y'); a.waitbutton(); a.closetext(); a.end()
    a.label('p4n'); a.writetext('p4no'); a.waitbutton(); a.closetext(); a.end()
    texts.update(p4q=q, p4y=yes, p4no=no)
    # the museum guy
    mq, myes, mgo = hl(RED_PEWTER, 3)[:3]
    texts.update(p3q=mq, p3y=myes, p3go=mgo, p3here=rt(RED_PEWTER, 13))
    mg = oid[3]
    a.label('p3'); a.faceplayer(); a.opentext(); a.writetext('p3q'); a.yesorno(); a.iffalse('p3n')
    a.writetext('p3y'); a.waitbutton(); a.closetext(); a.end()
    a.label('p3n'); a.writetext('p3go'); a.waitbutton(); a.closetext()
    guide(a, 'mg', mg, MUSEUM_GUY, MUSEUM_PRE, MUSEUM_PATH, U)
    a.opentext(); a.writetext('p3here'); a.waitbutton(); a.closetext()
    a.applymovement(mg, 'mg_exit'); a.disappear(mg); a.moveobject(mg, *MUSEUM_GUY); a.appear(mg); a.end()
    a.label('mg_exit'); a.db(D, D, D, D, 0x47)
    # the gym guy: leaving east before beating Brock, or talking to him
    gg = oid[5]
    texts.update(p5t=hl(RED_PEWTER, 5)[0], p5brock=rt(RED_PEWTER, 14))
    for x, y in GYM_TRIGGERS:
        L_ = 'gt%d_%d' % (x, y); me.coords.append((0xFF, y, x, L_))
        a.label(L_); a.checkflag(BOULDER_BADGE); a.iftrue('end'); a.sjump('p5go')
    a.label('p5'); a.faceplayer()
    a.label('p5go'); a.opentext(); a.writetext('p5t'); a.waitbutton(); a.closetext()
    guide(a, 'gg', gg, GYM_GUY, GYM_PRE, GYM_PATH, R_)
    a.turnobject(gg, 2)
    a.opentext(); a.writetext('p5brock'); a.waitbutton(); a.closetext()
    a.applymovement(gg, 'gg_exit'); a.disappear(gg); a.moveobject(gg, *GYM_GUY); a.appear(gg); a.turnobject(gg, 0); a.end()
    a.label('gg_exit'); a.db(*([R_] * 5), 0x47)
    a.label('end'); a.end()
    # signs
    for k, (x, y, tid) in enumerate(TOWN_SIGNS):
        L_ = 'ps%d' % k; a.label(L_); a.jumptext(L_ + 't'); texts[L_ + 't'] = rt(RED_PEWTER, tid); me.bgs.append((y, x, 0, L_))
    # Red: back in Pewter, the museum ticket is gone
    a.label('pw_cb'); a.clearevent(ticket); a.endcallback()
    old_cb = [r for t_, r in me.callbacks if t_ == 5]
    assert len(old_cb) == 1                                            # Crystal's fly point
    me.callbacks = [(t_, r) for t_, r in me.callbacks if t_ != 5] + [(5, 'pw_cb5')]
    a.label('pw_cb5'); a.clearevent(ticket)
    if old_cb[0][0] == 'far': a.farsjump(old_cb[0][1], old_cb[0][2])
    else: a.endcallback()
    dest_of = {(w[3], w[4]): w[2] for w in old_warps}
    me.warps = []
    for x, y, dn, wid in TOWN_WARPS:
        if wid is None: d = mapid(dn); me.warps.append(bytes([y, x, dest_of[d], *d]))
        else: me.warps.append(bytes([y, x, wid, *mapids[dn]]))
    for k, v in texts.items():
        a.label(k); a.raw(v if v[-1] in (0x50, 0x57, 0x58) else P12.text(v))
    me.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    me.install(a)
    log.append('PewterCity: Red events %X:%04X (%d bytes)' % (BANK, base, len(blob)))

    # ================= Red's blocks; the neighbours' edges translated
    ca = attrs(rom, hcity); ao = ca['attr_off']; assert (ca['w'], ca['h']) == (20, 18)
    old_city = ca['blk']
    rom[hcity + 1] = OVERWORLD_TS
    rom[ao] = border_of('PewterCity'); rom[ao + 3] = BANK; w16(ao + 4, sp.put(BANK, town.blk))
    e = TS.entry(OVERWORLD_TS); co = fo(e[6], e[7] | e[8] << 8)
    g1side = X.gen1_side(ow, bytes(rom[co:co + 4 * 128])); crside = X.crystal_side(rom, TS)
    xcity = sp.put(BANK, X.translate(MapPort('PewterCity', ow, 20, 18, 'PewterCity.blk').blk, g1side, crside))
    allhdr = [G[gi] + 9 * k for gi in range(26) for k in range((G[gi + 1] - G[gi]) // 9 if gi + 1 < 26 else FIRST_MAP + len(MAPS) - 1)]
    allhdr = [h_ for h_ in allhdr if rom[h_] and attrs(rom, h_)['scbank']]
    def conns(hdr):
        a_ = attrs(rom, hdr); o2 = a_['attr_off']
        return [o2 + 12 + 12 * k for k in range(bin(a_['conn'] & 0xF).count('1'))]
    for nn in NEIGHBOURS:
        na_ = attrs(rom, hdr_index(nn)); size = na_['w'] * na_['h']; ob, oa = na_['blkbank'], na_['blk']
        blk = bytes(rom[fo(ob, oa):fo(ob, oa) + size])
        nbp = sp.put(BANK2, blk); xl = sp.put(BANK2, X.translate(blk, crside, g1side))
        rom[na_['attr_off'] + 3] = BANK2; w16(na_['attr_off'] + 4, nbp)
        tgt = mapid(nn)
        for hdr in allhdr:
            for c in conns(hdr):
                if (rom[c], rom[c + 1]) == tgt:
                    s_ = r16(c + 2); assert oa <= s_ < oa + size, (nn, hex(hdr))
                    w16(c + 2, (xl if hdr == hcity else nbp) + s_ - oa)
        for c in conns(hdr_index(nn)):
            if (rom[c], rom[c + 1]) == pew:
                s_ = r16(c + 2); assert old_city <= s_ < old_city + 360; w16(c + 2, xcity + s_ - old_city)
    for i, (x, y, dn, wid) in enumerate(TOWN_WARPS):
        if wid is not None: continue
        a_ = attrs(rom, hdr_index(dn)); ev = parse_events(rom, a_['scbank'], a_['events']); n_ = 0
        for o_, w in ev['warps']:
            if (w[3], w[4]) == pew: rom[o_ + 2] = i + 1; n_ += 1
        assert n_, dn
    sp_i = [i for i in range(40) if (rom[SPAWN_TABLE + 4 * i], rom[SPAWN_TABLE + 4 * i + 1]) == pew]
    assert len(sp_i) == 1
    rom[SPAWN_TABLE + 4 * sp_i[0] + 2:SPAWN_TABLE + 4 * sp_i[0] + 4] = bytes([13, 26])

    P17.fix_outdoor_sprites(rom, log)
    trim_outdoor_sprites(rom, pew[0], log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


POKEPIC = 0x244F4                 # JP Pokepic (09:44F4)
GET2BPP = 0x0F6C
W_CUR_PARTY_SPECIES = 0xD0C8


def fossil_pic(sp, mon, fn):
    """Red: the fossil's own picture (a skeleton) in the Pokémon picture box; Pokepic with the picture copied from
    here instead of the species' front picture (the box takes the species' colours)"""
    from PIL import Image
    name = {'AerodactylFossil': 'fossilaerodactyl', 'KabutopsFossil': 'fossilkabutops'}[fn]
    im = Image.open(PR + '/gfx/pokemon/front/%s.png' % name).convert('L')
    w, h = im.size[0] // 8, im.size[1] // 8
    ox, oy = (8 - w) // 2, 7 - h                           # Gen I: centred, bottom-aligned in 7x7
    big = Image.new('L', (56, 56), 255); big.paste(im, (8 * ox, 8 * oy))
    px = big.load(); data = bytearray()
    for tx in range(7):
        for ty in range(7):
            for r in range(8):
                lo = hi = 0
                for c in range(8):
                    v = 3 - px[8 * tx + c, 8 * ty + r] // 85
                    lo |= (v & 1) << (7 - c); hi |= (v >> 1) << (7 - c)
                data += bytes([lo, hi])
    gfx = sp.put(BANK2, bytes(data))
    rom = sp.rom; src = bytes(rom[POKEPIC:POKEPIC + 0x45])
    assert src[0] == 0x21 and src[0x20:0x24] == bytes.fromhex('1100883E') and src[0x25] == 0xCD and src[-1] == 0xC9   # ld de, vTiles1 / predef GetMonFrontpic
    hdr = sp.put(BANK2, bytes(rom[fo(0x09, src[1] | src[2] << 8):][:8]))
    code = bytes([0x3E, mon, 0xEA, W_CUR_PARTY_SPECIES & 0xFF, W_CUR_PARTY_SPECIES >> 8, 0x21, hdr & 0xFF, hdr >> 8]) + \
        src[3:0x20] + bytes([0x21, 0x00, 0x88, 0x11, gfx & 0xFF, gfx >> 8, 0x06, BANK2, 0x0E, 49, 0xCD,
                             GET2BPP & 0xFF, GET2BPP >> 8]) + src[0x28:]
    return sp.put(BANK2, code)


def trim_outdoor_sprites(rom, group, log):
    """Red's Pewter has more walking people than Crystal's: the sprites of the group that no outdoor map uses go
    (repeated entries load nothing), so that all of them fit in VRAM"""
    u = US.get(); G = u.groups(); tab = fo(*P17.OUTDOOR_SPRITES_PTR); gi = group - 1
    lp = fo(5, rom[tab + 2 * gi] | rom[tab + 2 * gi + 1] << 8)
    used = set()
    for k in range((G[gi + 1] - G[gi]) // 9):
        hdr = G[gi] + 9 * k
        if rom[hdr + 2] not in (1, 2): continue
        a = attrs(rom, hdr); ev = parse_events(rom, a['scbank'], a['events'])
        used |= {o[0] for _, o in ev['objs']}
    lst = list(rom[lp:lp + 23]); keep = [x for x in lst if x in used]
    assert set(keep) == {x for x in used if x < 0x67 or x >= 0xF0}
    rom[lp:lp + 23] = bytes(keep + [keep[0]] * (23 - len(keep)))
    log.append('outdoor sprites group %d: %d kept' % (group, len(keep)))


def guide(a, tag, obj, home, pre, path, last_turn):
    """the player gets behind the guide, then follows him along Red's route"""
    a.playmusic(MUSIC_SHOW_ME_AROUND)
    for (x, y), mv in pre.items():
        a.db(0x1C, VAR_X); a.ifnotequal(x, '%s_n%d_%d' % (tag, x, y))
        a.db(0x1C, VAR_Y); a.ifnotequal(y, '%s_n%d_%d' % (tag, x, y))
        if mv: a.applymovement(0, '%s_m%d_%d' % (tag, x, y))
        a.sjump(tag + '_go')
        a.label('%s_n%d_%d' % (tag, x, y))
    a.label(tag + '_go')
    a.db(0x6F, obj, 0)                                                 # follow obj, PLAYER
    a.applymovement(obj, tag + '_path')
    a.db(0x70)                                                         # stopfollow
    a.turnobject(0, {D: 0, U: 1, L: 2, R_: 3}[last_turn])
    a.playmapmusic()
    a.sjump(tag + '_done')
    for (x, y), mv in pre.items():
        if mv: a.label('%s_m%d_%d' % (tag, x, y)); a.db(*mv, 0x47)
    a.label(tag + '_path'); a.db(*path, 0x47)
    a.label(tag + '_done')


def museum_counter(a, lab, texts, t, ticket):
    """Red: Museum1FScientist1Text"""
    other, take, would, poor, thanks, again, amberq, lab_t, sap = t
    texts.update({lab + k: v for k, v in zip(('ot', 'tk', 'wd', 'pr', 'th', 'ag', 'aq', 'lb', 'sp'),
                                              (other, take, would, poor, thanks, again, amberq, lab_t, sap))})
    a.label(lab); a.faceplayer()
    a.db(0x1C, VAR_Y); a.ifequal(4, lab + 'y4'); a.ifequal(3, lab + 'y3'); a.sjump(lab + 'oth')
    a.label(lab + 'y4'); a.db(0x1C, VAR_X); a.ifequal(13, lab + 'bh'); a.sjump(lab + 'chk')
    a.label(lab + 'y3'); a.db(0x1C, VAR_X); a.ifequal(12, lab + 'bh')
    a.label(lab + 'oth'); a.checkevent(ticket); a.iftrue(lab + 'take'); a.jumptext(lab + 'ot')
    a.label(lab + 'chk'); a.checkevent(ticket); a.iftrue(lab + 'take')
    a.label(lab + 'buy')
    a.opentext(); a.special(SPECIAL_MONEY_TOP_RIGHT); a.writetext(lab + 'wd'); a.yesorno(); a.iffalse(lab + 'no')
    a.db(0x24, 0, 0, 0, 50); a.ifequal(2, lab + 'poor')                # checkmoney YOUR_MONEY, 50 ; HAVE_LESS
    a.writetext(lab + 'th'); a.setevent(ticket); a.db(0x23, 0, 0, 0, 50)    # takemoney
    a.special(SPECIAL_MONEY_TOP_RIGHT); a.playsound(SFX_TRANSACTION); a.waitsfx(); a.waitbutton(); a.closetext(); a.end()
    a.label(lab + 'poor'); a.writetext(lab + 'pr'); a.waitbutton()
    a.label(lab + 'no'); a.writetext(lab + 'ag'); a.waitbutton(); a.closetext()
    a.applymovement(0, lab + 'down'); a.end()
    a.label(lab + 'down'); a.db(D, 0x47)
    a.label(lab + 'take'); a.jumptext(lab + 'tk')
    a.label(lab + 'bh'); a.opentext(); a.writetext(lab + 'aq'); a.yesorno(); a.iffalse(lab + 'ex')
    a.writetext(lab + 'lb'); a.waitbutton(); a.closetext(); a.end()
    a.label(lab + 'ex'); a.writetext(lab + 'sp'); a.waitbutton(); a.closetext(); a.end()


if __name__ == '__main__':
    main()
