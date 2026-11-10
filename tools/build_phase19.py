#!/usr/bin/env python3
"""Phase 19: Cinnabar Island before the Kanto Hall of Fame (ported from the Pikachu full-color hack, Red's events).
 * Cinnabar Island itself: before the Hall of Fame the map uses Red's layout and the Gen I overworld tileset
   (blocks / tileset / border are switched from a NEWMAP callback); afterwards it is Crystal's volcanic island.
 * Pokémon Mansion 1F-3F, B1F: trainers, items, diaries, the secret switches (doors), the Secret Key.
 * Cinnabar Lab (4 rooms): fossil revival (Helix / Dome Fossil, Old Amber -> Lv 30), TM35 from the scientist.
 * Cinnabar Mart.  The Gym door is locked (the gym itself: phase 20).
usage: build_phase19.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
import pkmap
import portmaps as PM
import build_phase11 as P11
import build_phase12 as P12
import build_phase13 as P13
import build_phase14 as P14
import build_phase15 as P15
import redtexts as RT
from evedit import MapEvents

FIRST_FLAG = 68
FIRST_MAP = 52                     # 26:40-51 = S.S. Anne etc. (phase 16)
MAPS = [('CinnabarMart', 0xAC, 'Pokecenter'), ('CinnabarLab', 0xA7, 'Lab'),
        ('CinnabarLabTradeRoom', 0xA8, 'Lab'), ('CinnabarLabMetronomeRoom', 0xA9, 'Lab'),
        ('CinnabarLabFossilRoom', 0xAA, 'Lab'),
        ('PokemonMansion1F', 0xA5, 'Facility'), ('PokemonMansion2F', 0xD6, 'Facility'),
        ('PokemonMansion3F', 0xD7, 'Facility'), ('PokemonMansionB1F', 0xD8, 'Facility'),
        ('CinnabarGym', 0xA6, 'Facility')]
CONST = {'CINNABAR_MART': 'CinnabarMart', 'CINNABAR_LAB': 'CinnabarLab', 'CINNABAR_LAB_TRADE_ROOM': 'CinnabarLabTradeRoom',
         'CINNABAR_LAB_METRONOME_ROOM': 'CinnabarLabMetronomeRoom', 'CINNABAR_LAB_FOSSIL_ROOM': 'CinnabarLabFossilRoom',
         'POKEMON_MANSION_1F': 'PokemonMansion1F', 'POKEMON_MANSION_2F': 'PokemonMansion2F',
         'POKEMON_MANSION_3F': 'PokemonMansion3F', 'POKEMON_MANSION_B1F': 'PokemonMansionB1F', 'CINNABAR_GYM': 'CinnabarGym'}
TOWN_WARP = {'PokemonMansion1F': 2, 'CinnabarLab': 3, 'CinnabarMart': 4, 'CinnabarGym': 5}   # index (1-based) in the town
EV_HOF = 0x34A
SECRET_KEY = 0x93                  # unused item slot -> key item ひみつのカギ
FACILITY_TS = 34
# Red: PokemonMansion3F .holeCoords and DungeonWarpData (where the player lands)
MANSION_HOLES = [((16, 14), 'PokemonMansion1F'), ((17, 14), 'PokemonMansion1F'), ((19, 14), 'PokemonMansion2F')]
MANSION_LAND = {'PokemonMansion1F': (16, 14), 'PokemonMansion2F': (18, 14)}
SPR = dict(PM.SPR)
SPR.update({'SPRITE_SILPH_PRESIDENT': 0x0D, 'SPRITE_CLERK': 0x39, 'SPRITE_FISHING_GURU': 0x3B, 'SPRITE_POKEDEX': 0x55, 'SPRITE_GAMBLER': 0x2D,
            'SPRITE_GYM_GUIDE': 0x48})
W_TILESET, W_BORDER, W_BLKBANK = 0xD1CA, 0xD1CE, 0xD1D1      # wMapTileset, wMapBorderBlock, wMapBlocksBank/Pointer
MART_SAFFRON = 30
FOSSILS = [(P12.HELIX_FOSSIL, 0x8A, 'かいのカセキ', 'オムナイト'), (P12.DOME_FOSSIL, 0x8C, 'こうらのカセキ', 'カブト'),
           (P12.OLD_AMBER, 0x8E, 'ひみつのコハク', 'プテラ')]
STRBUF = 0xD071
ENGINE_VOLCANO = 0x29
NPC_TRADES = (0x3F, 0x4E57); NPC_TRADES_REF = 0xFCDCF      # ld hl, NPCTrades (16 bytes per trade, 7 trades)
# Red's Cinnabar Lab trades: (map, object, dialog set, give, get, Red table entry with the nickname, OT name)
RED_TRADES = [('CinnabarLabTradeRoom', 2, 0, 0x1A, 0x65, 0x7207B, 'ハカセ'),     # Raichu  -> Electrode
              ('CinnabarLabTradeRoom', 3, 3, 0x30, 0x72, 0x72083, 'ミナコ'),     # Venonat -> Tangela
              ('CinnabarLabFossilRoom', 2, 0, 0x4D, 0x56, 0x7205B, 'タケシ')]    # Ponyta  -> Seel
GYM_GATES = [(9, 3, 0x54), (6, 3, 0x54), (6, 6, 0x54), (3, 8, 0x5F), (2, 6, 0x54), (2, 3, 0x54)]   # gate 1-6 (blocks)
SWITCH_BLOCKS = {   # map: [(block x, block y, block when off, block when on)]  (pokered scripts)
    'PokemonMansion1F': [(12, 6, 0x0E, 0x2D), (8, 3, 0x2D, 0x0E), (10, 8, 0x2D, 0x0E), (13, 13, 0x2D, 0x0E)],
    'PokemonMansion2F': [(4, 2, 0x0E, 0x5F), (9, 4, 0x54, 0x0E), (3, 11, 0x5F, 0x0E)],
    'PokemonMansion3F': [(7, 2, 0x0E, 0x5F), (7, 5, 0x5F, 0x0E)],
    'PokemonMansionB1F': [(13, 8, 0x0E, 0x2D), (6, 11, 0x0E, 0x5F), (4, 3, 0x5F, 0x0E), (8, 8, 0x54, 0x0E)]}


def red_seq(o, n):
    """n consecutive Red texts from o (each up to its terminator)"""
    out = []
    for _ in range(n):
        b = RT.raw(o); out.append(b); o += len(b) + 1
    return out


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (0x0B, 0x12, 0x13, 0x60, 0x61, 0x62, 0x63, 0x78, 0x79, 0x7C):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1, b * 0x4000 + 0x4000)
    sp.set_area(0x13, fo(0x13, 0x77CD), fo(0x13, 0x77CC + 511))   # free gap of bank 13 (also free in the JP original)
    log = []
    FL = PM.Flags(FIRST_FLAG)

    # ================= key item ひみつのカギ
    nb = rom[P12.ITEMNAMES_PTR]; na = r16(P12.ITEMNAMES_PTR + 1); o = fo(nb, na)
    names = []
    for i in range(256):
        e = rom.index(0x50, o); names.append(bytes(rom[o:e + 1])); o = e + 1
    names[SECRET_KEY - 1] = encode('ひみつのカギ@')
    a_names = sp.put(0x61, b''.join(names)); rom[P12.ITEMNAMES_PTR] = 0x61; w16(P12.ITEMNAMES_PTR + 1, a_names)
    rom[P12.ITEMATTR + 7 * (SECRET_KEY - 1):P12.ITEMATTR + 7 * SECRET_KEY] = rom[P12.ITEMATTR + 7 * (P12.LIFT_KEY - 1):][:7]
    w16(P12.ITEMDESC + 2 * (SECRET_KEY - 1), sp.put(0x0B, encode('グレン　ジムの　ドアを<NEXT>あける　ための　カギ@')))

    # ================= tilesets
    TS = PM.Tilesets(rom, sp)
    tss = {'Overworld': Tileset('Overworld', 0, 'overworld.bst', SC + '/out/pk_overworld.pkl', water=0x14, grass=0x52),
           'Pokecenter': Tileset('Pokecenter', 2, 'pokecenter.bst', SC + '/out/pk_mart.pkl'),
           'Lab': Tileset('Lab', 20, 'lab.bst', SC + '/out/pk_lab.pkl'),
           'Facility': Tileset('Facility', 22, 'facility.bst', SC + '/out/pk_facility.pkl')}
    coll = {k: t.coll for k, t in tss.items()}
    coll['Facility'] = bytearray(rom[TS.coll_off(FACILITY_TS):TS.coll_off(FACILITY_TS) + 4 * tss['Facility'].nblocks])
    maps = {}
    for n, g, tk in MAPS:
        h = pkmap.header(g); maps[n] = MapPort(n, tss[tk], h['w'], h['h'], n + '.blk')
    town = MapPort('CinnabarIsland', tss['Overworld'], 10, 9, 'CinnabarIsland.blk')
    allmaps = dict(maps); allmaps['CinnabarIsland'] = town
    PM.warp_collisions(allmaps, lambda n: PM.objects_of(n)[:3], log, coll)
    co = TS.coll_off(FACILITY_TS); rom[co:co + len(coll['Facility'])] = coll['Facility']
    ts_id = {'Facility': FACILITY_TS}
    # Pokémon Mansion 3F: the holes (Crystal pits) -- 3F's hole blocks get their own copies
    import pairwalls
    vb = pairwalls.install(rom, sp, TS, FACILITY_TS, tss['Facility'], {'PokemonMansion3F': maps['PokemonMansion3F']}, [],
                           {'PokemonMansion3F': {p: 0x60 for p, d in MANSION_HOLES}}, 0x61, log)
    maps['PokemonMansion3F'].blk = vb['PokemonMansion3F']
    for k in ('Overworld', 'Pokecenter', 'Lab'):
        tss[k].coll = coll[k]
        ts_id[k] = TS.add(tss[k], 0x60, log, anim_src=3 if k == 'Overworld' else 5)

    # ================= map headers (group 26)
    u = US.get(); G = u.groups()
    lo, hi = GROUP26_END + 9 * (FIRST_MAP - G26_COUNT - 1), GROUP26_END + 9 * (FIRST_MAP - G26_COUNT - 1 + len(MAPS))
    for gi in range(26):
        n_ = (G[gi + 1] - G[gi]) // 9 if gi + 1 < 26 else FIRST_MAP - 1
        for k in range(n_):
            hdr = G[gi] + 9 * k
            ab = rom[hdr]; ap = r16(hdr + 3); ao = fo(ab, ap)
            nconn = bin(rom[ao + 11] & 0xF).count('1'); size = 12 + 12 * nconn
            if ao < hi and ao + size > lo:
                rom[hdr] = 0x79; w16(hdr + 3, sp.put(0x79, bytes(rom[ao:ao + size])))
    rom[lo:hi] = bytes(hi - lo)
    mapids = {n: (G26, FIRST_MAP + i) for i, (n, g, tk) in enumerate(MAPS)}
    cin = mapid('CinnabarIsland')

    # ================= trainer parties (bank 7E)
    groups = P13.read_groups7e(rom)
    def pb(mons): return b'\x00' + b''.join(bytes([lv, PM.MON[P15.P10.MON_ALIAS.get(s, s)]]) for lv, s in mons) + b'\xff'
    party_of = {}; ni = 0
    for n, g, tk in MAPS:
        for o in P11.objects_of(n)[0]:
            if o['extra'] and o['extra'][0].startswith('OPP_'):
                c = o['extra'][0][4:]; k = int(o['extra'][1]); cid = PM.TCLS[c]
                nm = 'カツラ' if c == 'BLAINE' else PM.NAMEPOOL[ni % len(PM.NAMEPOOL)]; ni += 1
                groups[cid - 1].append([encode(nm + '@'), pb(PM.red_party(c, k))])
                party_of[(n, o['text'])] = (cid, len(groups[cid - 1]))
    log.append('trainer parties added (bank 7E free %d)' % P13.write_groups7e(rom, groups))

    # ================= Red's in-game trades (appended to Crystal's NPC trade table)
    f3f, _ = bank_free_tail(rom, 0x3F); sp.set_area(0x3F, f3f + 1, 0x3F * 0x4000 + 0x4000)
    to = fo(*NPC_TRADES); assert rom[NPC_TRADES_REF:NPC_TRADES_REF + 3] == bytes([0x21, 0x57, 0x4E])
    table = bytearray(rom[to:to + 16 * 7]); trade_id = {}
    for k, (mn, tid, dlg, give, get, red_e, ot) in enumerate(RED_TRADES):
        nick = bytes(RT.R[red_e + 3:red_e + 7])
        e = bytes([dlg, give, get]) + nick + bytes([0x96, 0x66, 0x00]) + (31415 + 1111 * k).to_bytes(2, 'little') + encode(ot)[:3] + b'\x00'
        assert len(e) == 16
        table += e; trade_id[(mn, tid)] = 7 + k
    nt = sp.put(0x3F, bytes(table)); rom[NPC_TRADES_REF + 1] = nt & 0xFF; rom[NPC_TRADES_REF + 2] = nt >> 8
    log.append('NPC trades: table moved to 3F:%04X, Red trades = %s' % (nt, sorted(trade_id.values())))

    # ================= interior maps
    sw_on = FL.new()                                        # Pokémon Mansion switch
    fossil_pend = {f[0]: FL.new() for f in FOSSILS}; fossil_ready = FL.new()
    got_tm35 = FL.new()
    extra = {}                                              # map -> list of hooks called with (a, ...)
    for n, mp in maps.items():
        g = [x[1] for x in MAPS if x[0] == n][0]
        objs, warps, skip, bgl = PM.objects_of(n)
        sb = 0x63
        a = Asm(sp.here(sb))
        callbacks = []; coords = []; bgs = []; texts = {}; obj_bytes = []
        if n == 'CinnabarGym':
            gates = [FL.new() for _ in GYM_GATES]; tr_flag = {}
            def open_gate(a, gi):
                x, y, blk = GYM_GATES[gi]
                a.setevent(gates[gi]); a.changeblock(2 * x, 2 * y, 0x0E); a.refreshmap()
        for idx, o in enumerate(objs):
            tid = idx + 1; lab = 'o%d' % tid
            sprite = SPR[o['sprite']]
            if o['move'] == 'STAY': mv, rng = P12.FACE.get(o['face'], 6), 0
            elif o['face'] == 'LEFT_RIGHT': mv, rng = 0x04, 0x10
            elif o['face'] == 'UP_DOWN': mv, rng = 0x05, 0x01
            else: mv, rng = 0x02, 0x11
            flag = 0xFFFF; typ = 0; sight = 0
            if o['sprite'] == 'SPRITE_POKE_BALL':
                typ = 1; flag = FL.new(); a.label(lab)
                a.db(SECRET_KEY if o['extra'][0] == 'SECRET_KEY' else PM.item_id(o['extra'][0]), 1)
            elif o['extra'] and o['extra'][0].startswith('OPP_') and o['extra'][0] != 'OPP_BLAINE':
                typ = 2; fl = FL.new()
                if n == 'CinnabarGym':
                    tg = P14.asm_block_texts(g, tid); sight, seen, win, aft = 0, tg[0], tg[1], tg[2]
                else:
                    sight, seen, aft, win = P12.trainer_texts(g, tid)
                cid, pid = party_of[(n, o['text'])]
                a.label(lab); a.dw(fl); a.db(cid, pid); a.dw(lab + 's'); a.dw(lab + 'w'); a.dw(0); a.dw(lab + 'x')
                a.label(lab + 'x')
                if n == 'CinnabarGym':
                    tr_flag[tid] = fl
                    if 3 <= tid <= 8:                          # beating a quiz trainer opens his gate
                        a.checkevent(gates[tid - 3]); a.iftrue(lab + 'y'); a.playsound(0x0019); open_gate(a, tid - 3)
                        a.label(lab + 'y')
                a.endifjustbattled(); a.opentext(); a.writetext(lab + 'a'); a.waitbutton(); a.closetext(); a.end()
                texts[lab + 's'] = seen; texts[lab + 'w'] = win; texts[lab + 'a'] = aft
            elif n == 'CinnabarGym' and o['sprite'] == 'SPRITE_SILPH_PRESIDENT':
                cid, pid = party_of[(n, o['text'])]; badge_done = FL.new()
                a.label(lab); a.faceplayer(); a.opentext(); a.checkevent(badge_done); a.iftrue(lab + 'g')
                a.writetext(lab + 'i'); a.waitbutton(); a.closetext()
                a.winlosstext(lab + 'w', 0); a.loadtrainer(cid, pid); a.startbattle(); a.reloadmapafterbattle()
                for t_ in tr_flag.values(): a.setevent(t_)
                for gi in range(len(GYM_GATES)): open_gate(a, gi)
                a.opentext(); a.writetext(lab + 'b'); a.playsound(0x009C); a.waitsfx(); a.setflag(ENGINE_VOLCANO)
                a.writetext(lab + 'n'); a.promptbutton(); a.verbosegiveitem(P12.tm_item(38), 1); a.iffalse(lab + 'z')
                a.setevent(badge_done)
                a.label(lab + 'g'); a.writetext(lab + 'a'); a.waitbutton()
                a.label(lab + 'z'); a.closetext(); a.end()
                texts[lab + 'i'] = RT.raw(0x761D8); texts[lab + 'w'] = RT.raw(0x76240)
                texts[lab + 'b'] = encode('{00}<PLAYER>は　カツラから<LINE>クりムゾンバッジを　もらった！')
                texts[lab + 'n'] = RT.raw(0x762B8); texts[lab + 'a'] = RT.raw(0x7626A)
            elif n == 'CinnabarGym' and o['sprite'] == 'SPRITE_GYM_GUIDE':
                a.label(lab); a.jumptextfaceplayer(lab + 't'); texts[lab + 't'] = RT.raw(0x766ED)
            elif (n, tid) in trade_id:
                a.label(lab); a.faceplayer(); a.opentext(); a.db(0x95, trade_id[(n, tid)]); a.waitbutton(); a.closetext(); a.end()
            elif n == 'CinnabarMart' and o['sprite'] == 'SPRITE_CLERK':
                a.label(lab); a.faceplayer(); a.opentext(); a.db(0x93, 0x00); a.dw(MART_SAFFRON); a.closetext(); a.end()
            elif n == 'CinnabarLabMetronomeRoom' and tid == 1:
                tg = P14.asm_block_texts(g, tid)
                a.label(lab); a.faceplayer(); a.opentext(); a.checkevent(got_tm35); a.iftrue(lab + 'g')
                a.writetext(lab + 'a'); a.promptbutton(); a.verbosegiveitem(P12.tm_item(35), 1); a.iffalse(lab + 'z')
                a.setevent(got_tm35)
                a.label(lab + 'g'); a.writetext(lab + 'c'); a.waitbutton()
                a.label(lab + 'z'); a.closetext(); a.end()
                texts[lab + 'a'] = tg[0]; texts[lab + 'c'] = tg[3]
            elif n == 'CinnabarLabFossilRoom' and tid == 1:
                none, wait, rev1, rev2 = RT.raw(0x76C98), RT.raw(0x76CA4), RT.raw(0x76CD1), RT.raw(0x76CF5)
                intro = RT.raw(RT.R.index(encode('はいー！'), 0x76C3E) - 1)
                give = RT.raw(0x61874)
                a.label(lab); a.faceplayer(); a.opentext()
                a.checkevent(fossil_ready); a.iftrue('fr_ready')
                for it, sp_, iname, mname in FOSSILS:
                    a.checkevent(fossil_pend[it]); a.iftrue('fr_wait')
                a.writetext('fr_intro'); a.waitbutton()
                for it, sp_, iname, mname in FOSSILS:
                    L = 'fr%02X' % it
                    a.checkitem(it); a.iffalse(L + 'n')
                    a.writetext(L + 'q'); a.yesorno(); a.iffalse(L + 'n')
                    a.writetext(L + 'g'); a.waitbutton(); a.db(0x20, it, 1)          # takeitem
                    a.setevent(fossil_pend[it]); a.writetext('fr_wait_t'); a.waitbutton(); a.closetext(); a.end()
                    a.label(L + 'n')
                    texts[L + 'q'] = encode('{00}おお！<LINE>それは　%s！<PARA>おお　むかしの　<POKEMON><LINE>%s　いう　カセキね！' % (iname, mname)) + \
                        b'\x51' + encode('わたしの　つくった<LINE>カセキ　さいせい　マシンで<PARA>これ！<LINE>いきかえらせて　みせるね！')
                    texts[L + 'g'] = bytes(give) + encode(iname) + encode('を　あずけた！')
                a.writetext('fr_none'); a.waitbutton(); a.closetext(); a.end()
                a.label('fr_wait'); a.writetext('fr_wait_t'); a.waitbutton(); a.closetext(); a.end()
                a.label('fr_ready')
                for it, sp_, iname, mname in FOSSILS:
                    L = 'fg%02X' % it
                    a.checkevent(fossil_pend[it]); a.iffalse(L + 'n')
                    a.getmonname(sp_); a.writetext('fr_rev'); a.waitbutton()
                    a.givepoke(sp_, 30); a.clearevent(fossil_pend[it]); a.clearevent(fossil_ready); a.closetext(); a.end()
                    a.label(L + 'n')
                a.clearevent(fossil_ready); a.closetext(); a.end()
                texts['fr_intro'] = intro; texts['fr_none'] = none; texts['fr_wait_t'] = wait
                assert rev2[0] == 0x01; texts['fr_rev'] = bytes(rev1) + b'\x50\x01' + bytes([STRBUF & 0xFF, STRBUF >> 8]) + bytes(rev2[3:])
                # coming back into the room: the fossil is ready
                a.label('fr_cb')
                for it, sp_, iname, mname in FOSSILS:
                    a.checkevent(fossil_pend[it]); a.iffalse('fr_cb%02X' % it); a.setevent(fossil_ready); a.endcallback()
                    a.label('fr_cb%02X' % it)
                a.endcallback()
                callbacks.append((2, 'fr_cb'))
            else:
                b_, p_ = pkmap.text_ptr(g, tid); k_, body = pkmap.text_body(b_, p_)
                if k_ != 'text':
                    tg = P14.asm_block_texts(g, tid) or PM.follow_farcall_texts(g, tid)
                    body = tg[0] if tg else encode('{00}<……>')
                a.label(lab); a.jumptextfaceplayer(lab + 't'); texts[lab + 't'] = body
            obj_bytes.append([sprite, o['y'] + 4, o['x'] + 4, mv, rng, 0xFF, 0xFF, typ, sight, lab, flag])

        for k, (x, y, tconst) in enumerate(bgl):
            b_, p_ = pkmap.text_ptr(g, len(objs) + k + 1); k_, body = pkmap.text_body(b_, p_)
            if k_ != 'text': continue
            L = 'bg%d' % k; a.label(L); a.jumptext(L + 't'); texts[L + 't'] = body
            bgs.append((y, x, 0, L))
        qbattle = []
        hev = PM.hidden_events(PM.map_const(n))
        if n == 'CinnabarGym':
            import re as _re
            src_ = open(PY + '/data/events/hidden_events.asm', encoding='utf-8').read()
            blk_ = _re.search(r'hidden_events_for CINNABAR_GYM\n(.*?)db -1', src_, _re.S).group(1)
            hev = [(int(x_), int(y_), 'PrintCinnabarQuiz', a_.strip())
                   for x_, y_, a_ in _re.findall(r'hidden_event\s+(\d+),\s*(\d+),\s*PrintCinnabarQuiz,\s*([^\n]+)', blk_)]
            assert len(hev) == 6
        for k, (x, y, fn, arg) in enumerate(hev):
            if fn == 'HiddenItems':
                L = 'hi%d' % k; a.label(L); a.dw(FL.new()); a.db(PM.item_id(arg))
                bgs.append((y, x, 7, L))
            elif fn == 'PrintCinnabarQuiz':
                import re as _re
                mm = _re.match(r'\(?(TRUE|FALSE)\s*<<\s*4\)?\s*\|\s*(\d)', arg)
                ans_no, gi = mm.group(1) == 'TRUE', int(mm.group(2)) - 1
                L = 'qz%d' % gi
                a.label(L); a.opentext()
                if gi == 0: a.writetext('qz_intro'); a.promptbutton()
                a.writetext('qz_q%d' % gi); a.yesorno()
                if ans_no: a.iftrue(L + 'x')
                else: a.iffalse(L + 'x')
                a.writetext('qz_ok'); a.waitbutton(); a.closetext()
                a.checkevent(gates[gi]); a.iftrue(L + 'e'); a.playsound(0x0019); open_gate(a, gi)
                a.label(L + 'e'); a.end()
                a.label(L + 'x'); a.playsound(0x0034); a.writetext('qz_ng'); a.waitbutton(); a.closetext()
                a.checkevent(tr_flag[gi + 3]); a.iftrue(L + 'e')
                a.sjump(L + 'b')
                bgs.append((y, x, 1, L))
                qbattle.append((gi, L + 'b'))
            elif 'Switches' in fn:
                L = 'sw%d' % k
                a.label(L); a.opentext(); a.writetext('swq'); a.yesorno(); a.iffalse(L + 'n')
                a.writetext('swy'); a.waitbutton(); a.closetext()
                a.checkevent(sw_on); a.iftrue(L + 'off'); a.setevent(sw_on); a.sjump('swdo')
                a.label(L + 'off'); a.clearevent(sw_on); a.sjump('swdo')
                a.label(L + 'n'); a.writetext('swn'); a.waitbutton(); a.closetext(); a.end()
                bgs.append((y, x, 1, L))
        if n == 'CinnabarGym':
            for gi, L in qbattle:
                tid = gi + 3; cid, pid = party_of[(n, objs[tid - 1]['text'])]
                a.label(L)
                a.opentext(); a.writetext('o%ds' % tid); a.waitbutton(); a.closetext()
                a.winlosstext('o%dw' % tid, 0); a.loadtrainer(cid, pid); a.startbattle(); a.reloadmapafterbattle()
                a.setevent(tr_flag[tid]); open_gate(a, gi); a.end()
            a.label('gy_cb')
            for gi, (x, y, blk) in enumerate(GYM_GATES):
                a.checkevent(gates[gi]); a.iftrue('gy_cb%d' % gi); a.changeblock(2 * x, 2 * y, blk); a.sjump('gy_cn%d' % gi)
                a.label('gy_cb%d' % gi); a.changeblock(2 * x, 2 * y, 0x0E)
                a.label('gy_cn%d' % gi)
            a.endcallback()
            callbacks.append((1, 'gy_cb'))
            qo = RT.R.index(encode('クイズ！'), 0x1FB00) - 3
            texts['qz_intro'] = RT.raw(qo)
            for gi, o_ in enumerate((0x1FBC0, 0x1FBDC, 0x1FBF9, 0x1FC11, 0x1FC3D, 0x1FC64)): texts['qz_q%d' % gi] = RT.raw(o_)
            texts['qz_ok'] = RT.raw(0x1FCD6)
            texts['qz_ng'] = RT.raw(RT.R.index(encode('ばか　はずれです'), 0x1FCED) - 1)
        if n in SWITCH_BLOCKS:
            q, y_, no = red_seq(RT.R.index(encode('ひみつの　スイッチが'), 0x447A0) - 1, 3)
            texts['swq'] = q; texts['swy'] = y_; texts['swn'] = no
            def blocks(a, on):
                for bx, by, off_b, on_b in SWITCH_BLOCKS[n]:
                    a.changeblock(2 * bx, 2 * by, on_b if on else off_b)
            a.label('swdo'); a.checkevent(sw_on); a.iffalse('swdo0'); blocks(a, True); a.refreshmap(); a.end()
            a.label('swdo0'); blocks(a, False); a.refreshmap(); a.end()
            a.label('swcb'); a.checkevent(sw_on); a.iffalse('swcb0'); blocks(a, True); a.endcallback()
            a.label('swcb0'); blocks(a, False); a.endcallback()
            callbacks.append((1, 'swcb'))

        for k_, v in texts.items():
            assert isinstance(v, (bytes, bytearray)) and len(v) < 800, (n, k_)
            a.label(k_); a.raw(P12.text(v))
        a.label('mapscripts'); a.db(0, len(callbacks))
        for t_, l_ in callbacks: a.db(t_); a.dw(l_)
        a.label('events'); a.db(0, 0)
        wl = []
        for wi, (x, y, dest, wid) in enumerate(warps):
            if dest == 'LAST_MAP': wl.append((y, x, TOWN_WARP[n]) + cin)
            elif wi in skip or dest not in CONST: wl.append((y, x, 1) + mapids[n])
            else: wl.append((y, x, wid) + mapids[CONST[dest]])
        if n == 'PokemonMansion3F':                              # the holes, after Red's warps
            for (x, y), dn in MANSION_HOLES:
                wl.append((y, x, len(PM.objects_of(dn)[1]) + 1) + mapids[dn])
        if n in MANSION_LAND:                                    # where the player lands (a warp of its own)
            x, y = MANSION_LAND[n]; wl.append((y, x, len(warps) + 1) + mapids['PokemonMansion3F'])
        a.db(len(wl))
        for w in wl: a.db(*w)
        a.db(len(coords))
        for (y, x, l_) in coords: a.db(0xFF, y, x, 0); a.dw(l_); a.db(0, 0)
        a.db(len(bgs))
        for (y, x, f_, l_) in bgs: a.db(y, x, f_); a.dw(l_)
        a.db(len(obj_bytes))
        for ob in obj_bytes: a.db(*ob[:9]); a.dw(ob[9]); a.dw(ob[10])
        base = a.base; blob = a.done(); assert sp.put(sb, blob) == base
        blkp = sp.put(0x60, mp.blk)
        aa = sp.put(0x60, bytes([border_of(n), mp.h, mp.w, 0x60, blkp & 0xFF, blkp >> 8, sb, a.labels['mapscripts'] & 0xFF,
                                 a.labels['mapscripts'] >> 8, a.labels['events'] & 0xFF, a.labels['events'] >> 8, 0]))
        tk = [x[2] for x in MAPS if x[0] == n][0]
        hh = GROUP26_END + 9 * (mapids[n][1] - G26_COUNT - 1)
        hc = hdr_index('CinnabarPokecenter1F')
        rom[hh:hh + 9] = bytes([0x60, ts_id[tk], 3, aa & 0xFF, aa >> 8, rom[hc + 5], rom[hc + 6], 0x01, 0x00])
        if n.startswith('PokemonMansion'): rom[hh + 6] = rom[hdr_index('BurnedTower1F') + 6]   # a spooky tune
        log.append('%s -> map %d:%d  scripts %X:%04X (%d bytes)' % (n, *mapids[n], sb, base, len(blob)))

    # ================= Cinnabar Island: Red's town before the Hall of Fame
    me = MapEvents(rom, 'CinnabarIsland')
    a = Asm(sp.here(0x62)); a.bank = 0x62
    blkp = sp.put(0x60, town.blk)
    # Red's layout and the Gen I overworld tileset for good (also after the Hall of Fame)
    h_ = hdr_index('CinnabarIsland'); ao = me.a['attr_off']
    rom[h_ + 1] = ts_id['Overworld']
    rom[ao] = 0x43; rom[ao + 3] = 0x60; rom[ao + 4] = blkp & 0xFF; rom[ao + 5] = blkp >> 8
    # Routes 20/21 draw Cinnabar's edge with their own (Crystal) tileset: show sea there instead of Red's blocks
    sea = sp.put(0x60, b'\x43' * 128)
    for rn in ('Route21', 'Route20'):
        ra = attrs(rom, hdr_index(rn)); rao = ra['attr_off']
        for k in range(bin(ra['conn'] & 0xF).count('1')):
            c = rao + 12 + 12 * k
            if (rom[c], rom[c + 1]) == cin: rom[c + 2] = sea & 0xFF; rom[c + 3] = sea >> 8
    # ... and Cinnabar draws Route 21's south edge (Crystal blocks) with Red's tileset: sea as well
    r21 = attrs(rom, hdr_index('Route21')); f2a, n2a = bank_free_tail(rom, r21['blkbank']); assert n2a > 40
    sea21 = 0x4000 + (f2a + 1) % 0x4000; rom[f2a + 1:f2a + 1 + 3 * r21['w']] = b'\x43' * (3 * r21['w'])
    for k in range(bin(me.a['conn'] & 0xF).count('1')):
        c = ao + 12 + 12 * k
        if (rom[c], rom[c + 1]) == mapid('Route21'): rom[c + 2] = sea21 & 0xFF; rom[c + 3] = sea21 >> 8
    # warps: Crystal's Pokémon Center door (11,11) is also Red's; Red's other doors only work on Red's map
    gym_x, gym_y = 18, 3
    for nm, (x, y) in (('PokemonMansion1F', (6, 3)), ('CinnabarLab', (6, 9)), ('CinnabarMart', (15, 11))):
        me.warps.append(bytes([y, x, 1 if nm != 'PokemonMansion1F' else 2]) + bytes(mapids[nm]))
    assert len(me.warps) == 4
    me.warps.append(bytes([gym_y, gym_x, 1]) + bytes(mapids['CinnabarGym']))
    # Crystal's Blue (who talks about the volcano) is not on Red's island
    assert me.objs[0][0][0] == 0x07; del me.objs[0]
    FL.new(); FL.new()                                       # (flags kept reserved)
    # Red's townspeople
    tobjs = PM.objects_of('CinnabarIsland')[0]
    texts = {}
    for i, o in enumerate(tobjs):
        L = 'cn_o%d' % i
        b_, p_ = pkmap.text_ptr(0x08, i + 1); _, body = pkmap.text_body(b_, p_); texts[L + 't'] = body
        a.label(L); a.jumptextfaceplayer(L + 't')
        if o['move'] == 'STAY': me.add_object(SPR[o['sprite']], o['x'], o['y'], P12.FACE.get(o['face'], 6), L)
        else: me.add_object(SPR[o['sprite']], o['x'], o['y'], 0x04, L, rng=0x10)
    # signs: Red's (Crystal's signs belonged to the volcanic island; its hidden item stays)
    me.bgs = [e for e in me.bgs if e[2] not in (0, 1, 2, 3, 4)]
    for k, (x, y, tconst) in enumerate(PM.objects_of('CinnabarIsland')[3]):
        b_, p_ = pkmap.text_ptr(0x08, len(tobjs) + k + 1); _, body = pkmap.text_body(b_, p_)
        L = 'cn_s%d' % k; texts[L + 't'] = body
        a.label(L); a.jumptext(L + 't'); me.bgs.append((y, x, 0, L))
    # the Gym door is locked (phase 20 opens it with the Secret Key)
    texts['cn_lock'] = pkmap.text_body(*pkmap.text_ptr(0x08, 8))[1]
    me.coords.append((0xFF, gym_y + 1, gym_x, 'cn_gym'))
    a.label('cn_gym'); a.checkitem(SECRET_KEY); a.iftrue('cn_gyme')
    a.db(0x1C, 9); a.ifnotequal(1, 'cn_gyme')                     # readvar VAR_FACING: only when walking up
    a.opentext(); a.writetext('cn_lock'); a.waitbutton(); a.closetext(); a.applymovement(0, 'cn_down')
    a.label('cn_gyme'); a.end()
    a.label('cn_down'); a.db(0x0C, 0x47)
    for k, v in texts.items():
        a.label(k); a.raw(P12.text(v))
    me.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(0x62, blob) == base
    me.install(a)
    log.append('CinnabarIsland: Red layout (tileset %d), events at 62:%04X' % (ts_id['Overworld'], base))
    import build_phase17 as P17
    P17.fix_outdoor_sprites(rom, log)

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
