#!/usr/bin/env python3
"""Phase 32: Routes 3 and 4 as in Red / the Pikachu full-color hack, with the Mt. Moon Pokémon Center:
 * Route 3 (Red, 35x9 blocks): Red's eight trainers (bug catchers, youngsters, lasses), the resting super nerd, the sign.
   Joined to Pewter City (west) and Route 4 (north), as in Red.
 * Route 4 (Red, 45x9 blocks): the Pokémon Center, both Mt. Moon entrances, the lass trainer, TM Whirlwind, the hidden
   Great Ball, the girl and the signs.  Joined to Route 3 (south) and Cerulean City (east).
 * Mt. Moon Pokémon Center (new map, Crystal's Pokémon Center interior): the nurse, Red's people and the Magikarp
   salesman (¥500, once).  Blacking out after healing there returns to it (Crystal's unused debug spawn point).
 * Mt. Moon: the ported one (phase 15) before the Hall of Fame, Crystal's afterwards, both from Red's entrances.
 * Red's wild Pokémon on both routes.
usage: build_phase32.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
import portmaps as PM
import pairwalls
import redmap as RM
import redtexts as RT
from evedit import MapEvents
import build_phase10 as P10
import build_phase12 as P12
import build_phase13 as P13
import build_phase15 as P15
import build_phase17 as P17
import build_phase22 as P22
import build_phase24 as P24
import build_phase25 as P25
import build_phase26 as P26
import build_phase27 as P27
import build_phase28 as P28
import build_phase29 as P29
import build_phase30 as P30

P15.TS_CAP = P27.TS_CAP
FIRST_FLAG = 267                   # 262-266: phase 30
FIRST_MAP = 99                     # 26:97-98 = phase 29
BANK = 0x73                        # free in the JP original
OVERWORLD_TS = 40
RED_ROUTE3, RED_ROUTE4, RED_CENTER = 0x0E, 0x0F, 0x44
W3, H3, W4, H4 = 35, 9, 45, 9
MAGIKARP = 129
SPAWN_DEBUG = P26.SPAWN_TABLE + 4  # SPAWN_DEBUG: unused
SPECIAL_MONEY = 0x51               # PlaceMoneyTopRight
SFX_TRANSACTION = 0x22
SPR = dict(P30.SPR)
SPR.update({'SPRITE_NURSE': 0x37, 'SPRITE_GENTLEMAN': 0x48, 'SPRITE_MIDDLE_AGED_MAN': 0x2D})
CENTER_OBJS = [(1, 3, 'SPRITE_YOUNGSTER', 'UP', 2), (7, 2, 'SPRITE_GENTLEMAN', 'DOWN', 3), (7, 6, 'MAGIKARP', 'LEFT_RIGHT', 4)]


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b_ in (BANK, 0x78):
        f, n = bank_free_tail(rom, b_); sp.set_area(b_, f + 1 if f > b_ * 0x4000 else f, b_ * 0x4000 + 0x4000)
    log = []
    FL = PM.Flags(FIRST_FLAG)
    r3, r4, pew, cer, mm = (mapid(n) for n in ('Route3', 'Route4', 'PewterCity', 'CeruleanCity', 'MountMoon'))
    center = (G26, FIRST_MAP)
    moon1f, moonb1f = (G26, 37), (G26, 38)                 # phase 15
    TS = PM.Tilesets(rom, sp)
    got_karp = FL.new()

    def hl(mapid_, tid, **kw):
        return [RM.crystal_text(b, p) for b, p in RM.asm_hl(mapid_, tid, **kw) if RM.R[RM.fo(b, p)] in (0x00, 0x17)]
    def rt(mapid_, tid):
        b, p = RM.text_ptr(mapid_, tid); k, v = RM.text_body(b, p)
        if k == 'text': return RM.crystal_text(b, p)
        return hl(mapid_, tid)[0]
    def put_texts(a, texts):
        for k_, v in texts.items():
            assert k_ not in a.labels, k_
            a.label(k_); a.raw(v if v[-1] in (0x50, 0x57, 0x58) else P12.text(v))

    # ================= tileset: the doors of Route 4
    ow = Tileset('Overworld', 0, 'overworld.bst', SC + '/out/pk_overworld.pkl', water=0x14, grass=0x52)
    rt3 = MapPort('Route3', ow, W3, H3, 'Route3.blk'); rt4 = MapPort('Route4', ow, W4, H4, 'Route4.blk')
    objs4 = P25.red_objects('Route4')
    e = TS.entry(OVERWORLD_TS); am_, ac_ = e[4] | e[5] << 8, e[7] | e[8] << 8
    assert e[3] == e[6]; nb0 = (ac_ - am_) // 16
    meta = bytes(rom[fo(e[3], am_):fo(e[3], am_) + 16 * nb0]); coll = bytes(rom[fo(e[6], ac_):fo(e[6], ac_) + 4 * nb0])
    ow.coll = bytearray(coll[:4 * ow.nblocks])
    ov = {'Route4': {(x, y): P25.warp_override(ow, rt4, x, y) for x, y, d, w in objs4[1]}}
    meta2, coll2, blks = pairwalls.variants(ow, meta, coll, {'Route3': rt3, 'Route4': rt4}, [], ov)
    meta2, coll2, blks = P27.block0_copy(meta2, coll2, blks)
    assert len(coll2) // 4 <= 256
    am = sp.put(BANK, meta2 + coll2); t0 = TS.tab + 15 * OVERWORLD_TS
    rom[t0 + 3] = BANK; w16(t0 + 4, am); rom[t0 + 6] = BANK; w16(t0 + 7, am + len(meta2))
    rt3.blk, rt4.blk = blks['Route3'], blks['Route4']
    log.append('tileset Overworld: %d blocks (+%d)' % (len(coll2) // 4, len(coll2) // 4 - nb0))

    # ================= trainer parties (bank 7E)
    groups = P13.read_groups7e(rom)
    def pb(mons): return b'\x00' + b''.join(bytes([lv, PM.MON[P10.MON_ALIAS.get(s, s)]]) for lv, s in mons) + b'\xff'
    party_of = {}; ti = 0
    for nm in ('Route3', 'Route4'):
        for i, o in enumerate(P25.red_objects(nm)[0]):
            if o['extra'] and o['extra'][0].startswith('OPP_'):
                c = o['extra'][0][4:]; k = int(o['extra'][1]); cid = PM.TCLS[c]
                groups[cid - 1].append([encode(PM.NAMEPOOL[(ti + 5) % len(PM.NAMEPOOL)] + '@'), pb(PM.red_party(c, k))])
                party_of[(nm, i)] = (cid, len(groups[cid - 1])); ti += 1
    log.append('trainer parties added (bank 7E free %d)' % P13.write_groups7e(rom, groups))

    # ================= headers 26:99 (move what lies there)
    u = US.get(); G = u.groups()
    lo, hi = GROUP26_END + 9 * (FIRST_MAP - G26_COUNT - 1), GROUP26_END + 9 * (FIRST_MAP - G26_COUNT)
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

    # ================= the routes' events
    def route_events(nm, g, a, texts):
        objs, warps, bgl = P25.red_objects(nm)
        obj_bytes = []; bgs = []
        for idx, o in enumerate(objs):
            tid = idx + 1; lab = nm[-1] + 'o%d' % tid; fl = 0xFFFF; typ = 0; sight = 0
            mv, rng = P25.face((0, 0, 0, o['move'], o['face']))
            if o['sprite'] == 'SPRITE_POKE_BALL':
                typ = 1; fl = FL.new(); a.label(lab); a.db(PM.item_id(o['extra'][0]), 1)
            elif o['extra'] and o['extra'][0].startswith('OPP_'):
                sight, seen, aft, win = P27.red_trainer_texts(g, tid)
                fl = FL.new(); cid, pid = party_of[(nm, idx)]; typ = 2
                a.label(lab); a.dw(fl); a.db(cid, pid); a.dw(lab + 's'); a.dw(lab + 'w'); a.dw(0); a.dw(lab + 'x')
                a.label(lab + 'x'); a.endifjustbattled(); a.opentext(); a.writetext(lab + 'a'); a.waitbutton(); a.closetext(); a.end()
                texts[lab + 's'] = seen; texts[lab + 'w'] = win; texts[lab + 'a'] = aft
            else:
                a.label(lab); a.jumptextfaceplayer(lab + 't'); texts[lab + 't'] = rt(g, tid)
            obj_bytes.append([SPR[o['sprite']], o['y'] + 4, o['x'] + 4, mv, rng, 0xFF, 0xFF, typ, sight, lab, fl])
        for k, (x, y, tconst) in enumerate(bgl):
            L_ = nm[-1] + 'bg%d' % k; a.label(L_); a.jumptext(L_ + 't'); texts[L_ + 't'] = rt(g, len(objs) + k + 1)
            bgs.append((y, x, 0, L_))
        for k, (x, y, fn, arg) in enumerate(P25.hidden(PM.map_const(nm))):
            assert fn == 'HiddenItems'
            L_ = nm[-1] + 'hi%d' % k; a.label(L_); a.dw(FL.new()); a.db(PM.item_id(arg)); bgs.append((y, x, 7, L_))
        return obj_bytes, warps, bgs

    def emit_events(a, label, warp_bytes, bgs, obj_bytes, callbacks):
        a.label(label + 'ms'); a.db(0, len(callbacks))
        for t_, l_ in callbacks: a.db(t_); a.dw(l_)
        a.label(label + 'ev'); a.db(0, 0)
        a.db(len(warp_bytes))
        for w_ in warp_bytes: a.raw(w_)
        a.db(0)
        a.db(len(bgs))
        for (y_, x_, t_, l_) in bgs: a.db(y_, x_, t_); a.dw(l_)
        a.db(len(obj_bytes))
        for ob in obj_bytes: a.db(*ob[:9]); a.dw(ob[9]); a.dw(ob[10])

    a = Asm(sp.here(BANK)); a.bank = BANK; texts = {}
    ob3, w3, bg3 = route_events('Route3', RED_ROUTE3, a, texts); assert not w3
    ob4, w4, bg4 = route_events('Route4', RED_ROUTE4, a, texts)
    assert [(d, w) for x, y, d, w in w4] == [('MT_MOON_POKECENTER', 1), ('MT_MOON_1F', 1), ('MT_MOON_B1F', 8)]
    # (Crystal's Route 3 / 4 have no callbacks of their own: phase 15's warp switch is made anew below)
    cbs = {'Route3': [], 'Route4': []}
    put_texts(a, texts)
    warps4 = [bytes([y, x, 1, *center]) for x, y, d, w in w4[:1]] + \
             [bytes([w4[1][1], w4[1][0], 1, *moon1f]), bytes([w4[2][1], w4[2][0], 8, *moonb1f])]
    emit_events(a, 'r3', [], bg3, ob3, cbs['Route3'])
    emit_events(a, 'r4', warps4, bg4, ob4, cbs['Route4'])
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    log.append('Route3 / Route4: Red events %X:%04X (%d bytes)' % (BANK, base, len(blob)))

    # ================= blocks, attributes and connections (Red: Route 3 north of it Route 4; Pewter / Cerulean)
    hp, hc, h3, h4 = (hdr_index(n) for n in ('PewterCity', 'CeruleanCity', 'Route3', 'Route4'))
    ap, ac = attrs(rom, hp), attrs(rom, hc)
    b3 = sp.put(BANK, rt3.blk); b4 = sp.put(BANK, rt4.blk)
    # (a strip is read from the bank of the blocks of the map it shows: all of them are Red's)
    c3 = P24.connection('north', W3, H3, r4, W4, H4, 25, b4) + \
        P22.connection('west', W3, H3, pew, 20, 18, -4, ap['blk'] + P22.strip_src('west', 20, -4))
    c4 = P24.connection('south', W4, H4, r3, W3, H3, -25, b3) + \
        P22.connection('east', W4, H4, cer, 20, 18, -4, ac['blk'] + P22.strip_src('east', 20, -4))
    for h_, nm, bb, w_, hh_, conn, cb_ in ((h3, 'Route3', b3, W3, H3, 0x08 | 0x02, c3), (h4, 'Route4', b4, W4, H4, 0x04 | 0x01, c4)):
        lab = 'r3' if nm == 'Route3' else 'r4'
        at = sp.put(BANK, bytes([border_of(nm), hh_, w_, BANK, bb & 0xFF, bb >> 8, BANK, a.labels[lab + 'ms'] & 0xFF,
                                 a.labels[lab + 'ms'] >> 8, a.labels[lab + 'ev'] & 0xFF, a.labels[lab + 'ev'] >> 8, conn]) + cb_)
        rom[h_] = BANK; w16(h_ + 3, at); rom[h_ + 1] = OVERWORLD_TS
    def conns(hdr):
        a_ = attrs(rom, hdr); o2 = a_['attr_off']
        return [o2 + 12 + 12 * k for k in range(bin(a_['conn'] & 0xF).count('1'))]
    n_ = 0
    for c in conns(hp):
        if (rom[c], rom[c + 1]) == r3:
            rom[c:c + 12] = P22.connection('east', 20, 18, r3, W3, H3, 4, b3 + P22.strip_src('east', W3, 4)); n_ += 1
    for c in conns(hc):
        if (rom[c], rom[c + 1]) == r4:
            rom[c:c + 12] = P22.connection('west', 20, 18, r4, W4, H4, 4, b4 + P22.strip_src('west', W4, 4)); n_ += 1
    assert n_ == 2

    # ================= Mt. Moon: the exits lead to Red's entrances; after the Hall of Fame Crystal's Mt. Moon
    for nm, wid in (('MtMoon1F', 2), ('MtMoonB1F', 3)):
        i_ = {'MtMoon1F': 37, 'MtMoonB1F': 38}[nm]; hh = GROUP26_END + 9 * (i_ - G26_COUNT - 1)
        a_ = attrs(rom, hh); ev = parse_events(rom, a_['scbank'], a_['events']); k_ = 0
        for o_, w in ev['warps']:
            if (w[3], w[4]) in (r3, r4): rom[o_ + 2] = wid; rom[o_ + 3:o_ + 5] = bytes(r4); k_ += 1
        assert k_, nm
    a_ = attrs(rom, hdr_index('MountMoon')); ev = parse_events(rom, a_['scbank'], a_['events']); k_ = 0
    for o_, w in ev['warps']:
        if (w[3], w[4]) == r3: rom[o_ + 2] = 2; rom[o_ + 3:o_ + 5] = bytes(r4); k_ += 1
        elif (w[3], w[4]) == r4: rom[o_ + 2] = 3; k_ += 1
    assert k_ == 2
    P15.install_hof_switch(rom, sp, 'Route4', {1: bytes([warps4[1][0], warps4[1][1], 1, *mm]),
                                               2: bytes([warps4[2][0], warps4[2][1], 2, *mm])}, log)

    # ================= the Mt. Moon Pokémon Center (Crystal's Pokémon Center interior, Red's people)
    src = MapEvents(rom, 'Route10Pokecenter1F'); hsrc = hdr_index('Route10Pokecenter1F'); asrc = attrs(rom, hsrc)
    nurse = src.objs[0]; assert nurse[0][0] == 0x37
    a = Asm(sp.here(BANK)); a.bank = BANK; texts = {}
    obj_bytes = [[0x37, 5, 7, 6, 0, 0xFF, 0xFF, 0, 0, 'nurse', 0xFFFF]]
    a.label('nurse'); a.farsjump(nurse[1][1], nurse[1][2])
    deal, poor, no_, refund = hl(RED_CENTER, 4)[:4]
    texts.update(kd=deal, kp=poor, kn=no_, kr=refund)
    for x, y, spr, face, tid in CENTER_OBJS:
        lab = 'c%d' % tid
        if spr == 'MAGIKARP':
            obj_bytes.append([SPR['SPRITE_MIDDLE_AGED_MAN'], y + 4, x + 4, 0x05, 0x01, 0xFF, 0xFF, 0, 0, lab, 0xFFFF])
            a.label(lab); a.faceplayer(); a.opentext(); a.checkevent(got_karp); a.iftrue(lab + 'r')
            a.special(SPECIAL_MONEY); a.writetext('kd'); a.yesorno(); a.iffalse(lab + 'n')
            a.db(0x24, 0, 0x00, 0x01, 0xF4); a.ifequal(2, lab + 'p')                    # checkmoney YOUR_MONEY, 500
            a.db(0x2D, MAGIKARP, 5, 0, 0)                                              # givepoke MAGIKARP, 5
            a.iffalse(lab + 'z')
            a.db(0x23, 0, 0x00, 0x01, 0xF4); a.special(SPECIAL_MONEY)                  # takemoney
            a.playsound(SFX_TRANSACTION); a.waitsfx(); a.setevent(got_karp)
            a.label(lab + 'z'); a.closetext(); a.end()
            a.label(lab + 'p'); a.writetext('kp'); a.waitbutton(); a.closetext(); a.end()
            a.label(lab + 'n'); a.writetext('kn'); a.waitbutton(); a.closetext(); a.end()
            a.label(lab + 'r'); a.writetext('kr'); a.waitbutton(); a.closetext(); a.end()
        else:
            obj_bytes.append([SPR[spr], y + 4, x + 4, P12.FACE[face], 0, 0xFF, 0xFF, 0, 0, lab, 0xFFFF])
            a.label(lab); a.jumptextfaceplayer(lab + 't'); texts[lab + 't'] = rt(RED_CENTER, tid)
    put_texts(a, texts)
    wl = [bytes([w[0], w[1], 1, *r4]) if (w[3], w[4]) == mapid('Route10North') else bytes(w) for w in src.warps]
    assert sum(1 for w in wl if (w[3], w[4]) == r4) == 2
    emit_events(a, 'pc', wl, [], obj_bytes, [])
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    aa = sp.put(BANK, bytes([rom[asrc['attr_off']], asrc['h'], asrc['w'], asrc['blkbank'], asrc['blk'] & 0xFF,
                             asrc['blk'] >> 8, BANK, a.labels['pcms'] & 0xFF, a.labels['pcms'] >> 8,
                             a.labels['pcev'] & 0xFF, a.labels['pcev'] >> 8, 0]))
    hh = GROUP26_END + 9 * (FIRST_MAP - G26_COUNT - 1)
    rom[hh:hh + 9] = bytes([BANK, rom[hsrc + 1], rom[hsrc + 2], aa & 0xFF, aa >> 8, rom[h4 + 5]]) + rom[hsrc + 6:hsrc + 9]
    log.append('MtMoonPokecenter -> map %d:%d  scripts %X:%04X' % (*center, BANK, base))
    # blacking out after entering it: back to its door (the unused debug spawn point)
    rom[SPAWN_DEBUG:SPAWN_DEBUG + 4] = bytes([*r4, 11, 6])

    # ================= wild Pokémon (Red)
    kg = P27.kanto_grass(rom)
    for mp, nm in ((r3, 'Route3'), (r4, 'Route4')):
        p = kg
        while (rom[p], rom[p + 1]) != mp:
            assert rom[p] != 0xFF; p += 47
        t = open(PR + '/data/wild/maps/%s.asm' % nm, encoding='utf-8').read()
        t = re.sub(r'IF DEF\(_BLUE\).*?ENDC', '', t, flags=re.S)
        rate = int(re.search(r'def_grass_wildmons (\d+)', t).group(1))
        slots = [(int(l_), s) for l_, s in re.findall(r'db\s+(\d+), (\w+)', t.split('end_grass_wildmons')[0])]
        pick = [slots[i] for i in (0, 1, 2, 3, 6, 8, 9)]
        rom[p:p + 47] = bytes([*mp, rate, rate, rate]) + bytes(sum(([lv, PM.MON[P10.MON_ALIAS.get(s, s)]] for lv, s in pick), [])) * 3

    P17.fix_outdoor_sprites(rom, log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    assert FL.i < 8 * (P28.SCENE_AREAS - 0xDA01)
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
