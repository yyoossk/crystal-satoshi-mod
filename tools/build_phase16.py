#!/usr/bin/env python3
"""Phase 16: S.S. Anne (+ Vermilion dock) and Bill's house (Sea Cottage), ported from the Pikachu full-color hack.
Red's trainers (sailors, gentlemen, ...; Shigeru on 2F), the captain gives HM01 (Cut), Bill gives the S.S. Ticket,
the ship leaves after you got Cut.  Before the Kanto Hall of Fame the Vermilion port passage leads to the dock and
Route 25's cottage door to Bill's house; afterwards Crystal's own port / cottage.
usage: build_phase16.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode, decode
import pkmap
import portmaps as PM
import build_phase11 as P11
import build_phase12 as P12
import build_phase13 as P13
import build_phase14 as P14
import build_phase15 as P15

MAPS = [('VermilionDock', 0x5E, 'ShipPort'), ('SSAnne1F', 0x5F, 'Ship'), ('SSAnne2F', 0x60, 'Ship'),
        ('SSAnne3F', 0x61, 'Ship'), ('SSAnneB1F', 0x62, 'Ship'), ('SSAnneBow', 0x63, 'Ship'),
        ('SSAnneKitchen', 0x64, 'Ship'), ('SSAnneCaptainsRoom', 0x65, 'Ship'), ('SSAnne1FRooms', 0x66, 'Ship'),
        ('SSAnne2FRooms', 0x67, 'Ship'), ('SSAnneB1FRooms', 0x68, 'Ship'), ('BillsHouse', 0x58, 'Interior')]
CONST = {'VERMILION_DOCK': 'VermilionDock', 'SS_ANNE_1F': 'SSAnne1F', 'SS_ANNE_2F': 'SSAnne2F', 'SS_ANNE_3F': 'SSAnne3F',
         'SS_ANNE_B1F': 'SSAnneB1F', 'SS_ANNE_BOW': 'SSAnneBow', 'SS_ANNE_KITCHEN': 'SSAnneKitchen',
         'SS_ANNE_CAPTAINS_ROOM': 'SSAnneCaptainsRoom', 'SS_ANNE_1F_ROOMS': 'SSAnne1FRooms',
         'SS_ANNE_2F_ROOMS': 'SSAnne2FRooms', 'SS_ANNE_B1F_ROOMS': 'SSAnneB1FRooms', 'BILLS_HOUSE': 'BillsHouse'}
FIRST_FLAG = 24                    # extended flags used by phase 15
BLUE = 64
S_S_TICKET, HM01 = 0x44, 0xF3
EV_OAK_GOT = {'fire': 0x343, 'water': 0x344, 'grass': 0x345}


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (0x12, 0x13, 0x60, 0x61, 0x75, 0x76, 0x77, 0x78, 0x79, 0x7A, 0x7C, 0x7D):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1, b * 0x4000 + 0x4000)
    log = []
    FL = PM.Flags(FIRST_FLAG)

    # ================= tilesets
    TS = PM.Tilesets(rom, sp)
    tss = {'Ship': Tileset('Ship', 13, 'ship.bst', SC + '/out/pk_ship.pkl'),
           'ShipPort': Tileset('ShipPort', 14, 'ship_port.bst', SC + '/out/pk_shipport.pkl'),
           'Interior': Tileset('Interior', 16, 'interior.bst', SC + '/out/pk_interior.pkl')}
    coll = {k: t.coll for k, t in tss.items()}
    coll['Interior'] = bytearray(rom[TS.coll_off(36):TS.coll_off(36) + 4 * tss['Interior'].nblocks])
    maps = {}
    for n, g, tk in MAPS:
        h = pkmap.header(g); maps[n] = MapPort(n, tss[tk], h['w'], h['h'], n + '.blk')
    PM.warp_collisions(maps, lambda n: PM.objects_of(n)[:3], log, coll)
    co = TS.coll_off(36); rom[co:co + len(coll['Interior'])] = coll['Interior']
    data_bank = 0x60
    ts_id = {'Interior': 36}
    for k in ('Ship', 'ShipPort'):
        tss[k].coll = coll[k]
        ts_id[k] = TS.add(tss[k], data_bank, log)

    # ================= map headers (group 26)
    u = US.get(); G = u.groups()
    first = 40                         # 26:37-39 = Mt. Moon (phase 15)
    lo, hi = GROUP26_END + 9 * (first - G26_COUNT - 1), GROUP26_END + 9 * (first - G26_COUNT - 1 + len(MAPS))
    for gi in range(26):
        n_ = (G[gi + 1] - G[gi]) // 9 if gi + 1 < 26 else first - 1
        for k in range(n_):
            hdr = G[gi] + 9 * k
            ab = rom[hdr]; ap = r16(hdr + 3); ao = fo(ab, ap)
            nconn = bin(rom[ao + 11] & 0xF).count('1'); size = 12 + 12 * nconn
            if ao < hi and ao + size > lo:
                rom[hdr] = 0x79; w16(hdr + 3, sp.put(0x79, bytes(rom[ao:ao + size])))
    rom[lo:hi] = bytes(hi - lo)
    mapids = {n: (G26, first + i) for i, (n, g, tk) in enumerate(MAPS)}

    # ================= trainer parties (bank 7E)
    groups = P13.read_groups7e(rom)
    def pb(mons): return b'\x00' + b''.join(bytes([lv, PM.MON[P15.P10.MON_ALIAS.get(s, s)]]) for lv, s in mons) + b'\xff'
    party_of = {}; ni = 0
    for n, g, tk in MAPS:
        for o in P11.objects_of(n)[0]:
            if o['extra'] and o['extra'][0].startswith('OPP_') and o['extra'][0] != 'OPP_RIVAL1':
                c = o['extra'][0][4:]; k = int(o['extra'][1]); cid = PM.TCLS[c]
                groups[cid - 1].append([encode(PM.NAMEPOOL[ni % len(PM.NAMEPOOL)] + '@'), pb(PM.red_party(c, k))]); ni += 1
                party_of[(n, o['text'])] = (cid, len(groups[cid - 1]))
    riv2 = P11.red_parties('Rival2Data')
    riv_ids = {}
    for i, key in enumerate(['fire', 'water', 'grass']):
        groups[BLUE - 1].append([encode('シゲル@'), pb(riv2[i])]); riv_ids[key] = len(groups[BLUE - 1])
    log.append('trainer parties added (bank 7E free %d)' % P13.write_groups7e(rom, groups))

    # ================= connections in Crystal
    passage = mapid('VermilionPortPassage'); port = mapid('VermilionPort'); r25 = mapid('Route25'); bhc = mapid('BillsHouse')
    pa = attrs(rom, hdr_index('VermilionPortPassage')); pev = parse_events(rom, pa['scbank'], pa['events'])
    pass_idx = [i for i, (o_, w) in enumerate(pev['warps']) if (w[3], w[4]) == port][0]
    ra = attrs(rom, hdr_index('Route25')); rev = parse_events(rom, ra['scbank'], ra['events'])
    r25_idx = [i for i, (o_, w) in enumerate(rev['warps']) if (w[3], w[4]) == bhc][0]

    # ================= maps
    got_hm01 = FL.new(); ship_left = FL.new()
    landmark_v = rom[hdr_index('VermilionCity') + 5]; landmark_r = rom[hdr_index('Route25') + 5]
    music_v = rom[hdr_index('VermilionPort') + 6]
    for n, mp in maps.items():
        g = [x[1] for x in MAPS if x[0] == n][0]
        objs, warps, skip, bgl = PM.objects_of(n)
        sb = 0x61
        a = Asm(sp.here(sb))
        callbacks = []; coords = []; bgs = []; texts = {}; obj_bytes = []
        oflag = {}; oid = {}
        for idx, o in enumerate(objs):
            tid = idx + 1; oid.setdefault(o['sprite'], []).append(tid)
            if o['sprite'] == 'SPRITE_POKE_BALL': oflag[tid] = FL.new()
        for idx, o in enumerate(objs):
            tid = idx + 1; lab = 'o%d' % tid
            sprite = PM.SPR[o['sprite']]
            mv = P12.FACE.get(o['face'], 6) if o['move'] == 'STAY' else 2
            flag = oflag.get(tid, 0xFFFF); typ = 0; sight = 0
            if o['sprite'] == 'SPRITE_POKE_BALL':
                typ = 1; a.label(lab); a.db(PM.item_id(o['extra'][0]), 1)
            elif o['extra'] and o['extra'][0] == 'OPP_RIVAL1':
                rflag = FL.new(); flag = rflag; a.label(lab); a.end(); rival_tid = tid
            elif o['extra'] and o['extra'][0].startswith('OPP_'):
                typ = 2; fl = FL.new()
                sight, seen, aft, win = P12.trainer_texts(g, tid)
                cid, pid = party_of[(n, o['text'])]
                a.label(lab); a.dw(fl); a.db(cid, pid); a.dw(lab + 's'); a.dw(lab + 'w'); a.dw(0); a.dw(lab + 'x')
                a.label(lab + 'x'); a.endifjustbattled(); a.opentext(); a.writetext(lab + 'a'); a.waitbutton(); a.closetext(); a.end()
                texts[lab + 's'] = seen; texts[lab + 'w'] = win; texts[lab + 'a'] = aft
            elif n == 'SSAnneCaptainsRoom' and o['sprite'] == 'SPRITE_CAPTAIN':
                tg = P14.asm_block_texts(g, tid)
                a.label(lab); a.faceplayer(); a.opentext(); a.checkevent(got_hm01); a.iftrue(lab + 'g')
                a.writetext(lab + 'a'); a.waitbutton(); a.writetext(lab + 'b'); a.waitbutton()
                a.verbosegiveitem(HM01, 1); a.iffalse(lab + 'z'); a.setevent(got_hm01)
                a.label(lab + 'g'); a.writetext(lab + 'c'); a.waitbutton()
                a.label(lab + 'z'); a.closetext(); a.end()
                texts[lab + 'a'] = tg[0]; texts[lab + 'b'] = tg[1]; texts[lab + 'c'] = tg[4]
            elif n == 'BillsHouse':
                a.label(lab); a.end()                          # scripts below
            else:
                b_, p_ = pkmap.text_ptr(g, tid); k_, body = pkmap.text_body(b_, p_)
                if k_ != 'text':
                    tg = P14.asm_block_texts(g, tid) or PM.follow_farcall_texts(g, tid)
                    body = tg[0] if tg else encode('{00}<……>')
                a.label(lab); a.jumptextfaceplayer(lab + 't'); texts[lab + 't'] = body
            obj_bytes.append([sprite, o['y'] + 4, o['x'] + 4, mv, 0, 0xFF, 0xFF, typ, sight, lab, flag])

        # signs / bg events from the objects file, hidden items
        for k, (x, y, tconst) in enumerate(bgl):
            b_, p_ = pkmap.text_ptr(g, len(objs) + k + 1); k_, body = pkmap.text_body(b_, p_)
            if k_ != 'text': continue
            L = 'bg%d' % k; a.label(L); a.jumptext(L + 't'); texts[L + 't'] = body
            bgs.append((y, x, 0, L))
        for k, (x, y, fn, arg) in enumerate(PM.hidden_events(PM.map_const(n) if n != 'BillsHouse' else 'BILLS_HOUSE')):
            if fn == 'HiddenItems':
                L = 'hi%d' % k; a.label(L); a.dw(FL.new()); a.db(PM.item_id(arg))
                bgs.append((y, x, 7, L))

        if n == 'VermilionDock':
            _, t_wel = pkmap.text_body(0x06, 0x6331 + 0x4000 - 0x4000) if False else (None, None)
            F = pkmap.F
            def raw(o):
                e = o
                while F[e] not in (0x57, 0x58, 0x50): e += 1
                return F[o:e]
            t_welcome, t_showed, t_noticket, t_left = raw(0x1A331), raw(0x1A35C), raw(0x1A393), raw(0x1A3DF)
            shown = FL.new()
            a.label('gate'); a.checkevent(got_hm01); a.iftrue('gleave')
            a.checkevent(shown); a.iftrue('gend')
            a.opentext(); a.writetext('twel'); a.waitbutton(); a.checkitem(S_S_TICKET); a.iffalse('gno')
            a.writetext('tshow'); a.waitbutton(); a.closetext(); a.setevent(shown); a.end()
            a.label('gno'); a.writetext('tno'); a.waitbutton(); a.closetext(); a.applymovement(0, 'gup'); a.end()
            a.label('gleave'); a.checkevent(ship_left); a.iftrue('gend')
            a.setevent(ship_left); a.opentext(); a.writetext('tleft'); a.waitbutton(); a.closetext()
            for bx in range(5, 9):
                a.changeblock(2 * bx, 2, 0x01); a.changeblock(2 * bx, 4, 0x0D)
            a.refreshmap()
            a.label('gend'); a.end()
            a.label('gup'); a.db(0x0D, 0x47)
            a.label('cbt'); a.checkevent(ship_left); a.iffalse('cbe')
            for bx in range(5, 9):
                a.changeblock(2 * bx, 2, 0x01); a.changeblock(2 * bx, 4, 0x0D)
            a.label('cbe'); a.endcallback()
            callbacks.append((1, 'cbt'))
            texts['twel'] = t_welcome; texts['tshow'] = t_showed; texts['tno'] = t_noticket; texts['tleft'] = t_left
            coords.append((1, 14, 'gate'))
        if n == 'SSAnne2F':
            rt = rival_tid; tg = P14.asm_block_texts(g, rt)
            ebt = PM.end_battle_texts(g)
            _, t_after = pkmap.text_body(*pkmap.text_ptr(g, 3))
            def riv(bb): return bytes(bb).replace(b'\x53', encode('シゲル'))
            a.label('cbo'); a.setevent(rflag); a.endcallback(); callbacks.append((2, 'cbo'))
            beat = FL.new()
            for x, steps in ((36, 3), (37, 4)):
                L = 'rv%d' % x
                a.label(L); a.checkevent(beat); a.iftrue('rve')
                a.appear(rt + 1); a.applymovement(rt + 1, 'rm%d' % steps); a.sjump('rvb')
                coords.append((8, x, L))
            a.label('rm4'); a.db(0x0C, 0x0C, 0x0C, 0x0C, 0x47)
            a.label('rm3'); a.db(0x0C, 0x0C, 0x0C, 0x47)
            a.label('rvb'); a.opentext(); a.writetext('rvi'); a.waitbutton(); a.closetext()
            a.winlosstext('rvw', 0)
            a.checkevent(EV_OAK_GOT['fire']); a.iftrue('rvf')
            a.checkevent(EV_OAK_GOT['water']); a.iftrue('rvv')
            a.loadtrainer(BLUE, riv_ids['grass']); a.sjump('rvg')
            a.label('rvf'); a.loadtrainer(BLUE, riv_ids['fire']); a.sjump('rvg')
            a.label('rvv'); a.loadtrainer(BLUE, riv_ids['water'])
            a.label('rvg'); a.startbattle(); a.reloadmapafterbattle()
            a.opentext(); a.writetext('rva'); a.waitbutton(); a.closetext()
            a.disappear(rt + 1); a.setevent(beat)
            a.label('rve'); a.end()
            texts['rvi'] = riv(tg[0]); texts['rvw'] = riv(ebt[0][0]); texts['rva'] = riv(t_after)
        if n == 'BillsHouse':
            bt = PM.follow_farcall_texts(g, 1); bt3 = PM.follow_farcall_texts(g, 3)
            F = pkmap.F; e = 0x1FE53
            while F[e] not in (0x57, 0x58, 0x50): e += 1
            t_pc = F[0x1FE53:e]
            mon, hum, hum2 = oid['SPRITE_MONSTER'][0], oid['SPRITE_SUPER_NERD'][0], oid['SPRITE_SUPER_NERD'][1]
            s1, s2, s3 = FL.new(), FL.new(), FL.new()
            h1, h2, h3 = FL.new(), FL.new(), FL.new()
            obj_bytes[mon - 1][10] = h1; obj_bytes[hum - 1][10] = h2; obj_bytes[hum2 - 1][10] = h3
            a.label('cbo')
            a.checkevent(s2); a.iftrue('c1'); a.setevent(h2)
            a.label('c1'); a.checkevent(s3); a.iftrue('c2'); a.setevent(h3); a.endcallback()
            a.label('c2'); a.setevent(h2); a.endcallback()
            callbacks.append((2, 'cbo'))
            obj_bytes[mon - 1][9] = 'bmon'; obj_bytes[hum - 1][9] = 'bhum'; obj_bytes[hum2 - 1][9] = 'bhum2'
            a.label('bmon'); a.faceplayer(); a.opentext(); a.writetext('b0'); a.yesorno(); a.iffalse('bno')
            a.writetext('b1'); a.waitbutton(); a.closetext(); a.disappear(mon + 1); a.setevent(s1); a.end()
            a.label('bno'); a.writetext('b2'); a.waitbutton(); a.closetext(); a.end()
            a.label('bpc'); a.checkevent(s1); a.iffalse('bpce'); a.checkevent(s2); a.iftrue('bpce')
            a.opentext(); a.writetext('bp'); a.waitbutton(); a.closetext(); a.playsound(0x1F); a.waitsfx()
            a.appear(hum + 1); a.setevent(s2)
            a.label('bpce'); a.end()
            a.label('bhum'); a.faceplayer(); a.opentext(); a.writetext('b3'); a.waitbutton()
            a.verbosegiveitem(S_S_TICKET, 1); a.iffalse('bhz'); a.setevent(s3)
            a.writetext('b5'); a.waitbutton(); a.closetext(); a.disappear(hum + 1); a.appear(hum2 + 1); a.end()
            a.label('bhz'); a.closetext(); a.end()
            a.label('bhum2'); a.faceplayer(); a.opentext(); a.checkevent(s3); a.iffalse('bh2'); a.writetext('b6'); a.waitbutton()
            a.label('bh2'); a.closetext(); a.end()
            texts['b0'] = bt[0]; texts['b1'] = bt[1]; texts['b2'] = bt[2]; texts['b3'] = bt[3]; texts['b5'] = bt[5]
            texts['b6'] = bt3[0]; texts['bp'] = t_pc
            for (x, y, fn, arg) in PM.hidden_events('BILLS_HOUSE'):
                if fn == 'BillsHousePC': bgs.append((y, x, 1, 'bpc'))

        for k_, v in texts.items():
            assert isinstance(v, (bytes, bytearray)) and len(v) < 700, (n, k_)
            a.label(k_); a.raw(P12.text(v))
        a.label('mapscripts'); a.db(0, len(callbacks))
        for t_, l_ in callbacks: a.db(t_); a.dw(l_)
        a.label('events'); a.db(0, 0)
        wl = []
        for wi, (x, y, dest, wid) in enumerate(warps):
            if dest == 'LAST_MAP':
                if n == 'VermilionDock': wl.append((y, x, pass_idx + 1) + passage)
                else: wl.append((y, x, r25_idx + 1) + r25)
            elif wi in skip or dest not in CONST: wl.append((y, x, 1) + mapids[n])
            else: wl.append((y, x, wid) + mapids[CONST[dest]])
        a.db(len(wl))
        for w in wl: a.db(*w)
        a.db(len(coords))
        for (y, x, l_) in coords: a.db(0xFF, y, x, 0); a.dw(l_); a.db(0, 0)
        a.db(len(bgs))
        for (y, x, f_, l_) in bgs: a.db(y, x, f_); a.dw(l_)
        a.db(len(obj_bytes))
        for ob in obj_bytes: a.db(*ob[:9]); a.dw(ob[9]); a.dw(ob[10])
        base = a.base; blob = a.done(); assert sp.put(sb, blob) == base
        db_ = 0x60
        blkp = sp.put(db_, mp.blk)
        aa = sp.put(db_, bytes([border_of(n), mp.h, mp.w, db_, blkp & 0xFF, blkp >> 8, sb, a.labels['mapscripts'] & 0xFF,
                                a.labels['mapscripts'] >> 8, a.labels['events'] & 0xFF, a.labels['events'] >> 8, 0]))
        tk = [x[2] for x in MAPS if x[0] == n][0]
        hh = GROUP26_END + 9 * (mapids[n][1] - G26_COUNT - 1)
        env = 3
        lm = landmark_r if n == 'BillsHouse' else landmark_v
        mu = rom[hdr_index('BillsHouse') + 6] if n == 'BillsHouse' else music_v
        rom[hh:hh + 9] = bytes([db_, ts_id[tk], env, aa & 0xFF, aa >> 8, lm, mu, 0x01, 0x00])
        log.append('%s -> map %d:%d  scripts %X:%04X (%d bytes)' % (n, *mapids[n], sb, base, len(blob)))

    # ================= entrances (before the Hall of Fame)
    for mname, idx, target, twarp in (('VermilionPortPassage', pass_idx, 'VermilionDock', 1), ('Route25', r25_idx, 'BillsHouse', 1)):
        a_ = attrs(rom, hdr_index(mname)); ev = parse_events(rom, a_['scbank'], a_['events'])
        o_, w = ev['warps'][idx]
        fix = {idx: bytes(w)}
        rom[o_ + 2] = twarp; rom[o_ + 3], rom[o_ + 4] = mapids[target]
        P15.install_hof_switch(rom, sp, mname, fix, log)

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
