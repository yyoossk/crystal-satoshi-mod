#!/usr/bin/env python3
"""Phase 25: Cerulean City as in Red / the Pikachu full-color hack, for good (also after the Hall of Fame), with its
houses and Cerulean Cave:
 * Red's town (Gen I overworld tileset) in place of Crystal's: Red's people, signs and hidden item, the Rocket who
   stole TM28 (battle, then he gives the TM back and the guards change places), the guards (also moved by Bill's
   S.S. Ticket), Slowbro and its trainer, the man who guards Cerulean Cave until the Kanto Hall of Fame.  The rival
   battle of phase 17 is kept.  Routes 4, 5, 9 and 24 stay Crystal's: each side shows the other's edge drawn with its
   own tileset (blockxlat).
 * Red's houses: the trashed house (Dig TM thief; the hole in the wall), the trade house (Poliwhirl for Jynx), the
   badge house (the man explains the eight badges), the bike shop (Bike Voucher -> Bicycle; ¥1000000 otherwise).
   Crystal's Pokémon Center, Mart and Gym are used for those doors.
 * The Fan Club chairman gives Red's Bike Voucher (a new key item) instead of the Bicycle.
 * Cerulean Cave 1F / 2F / B1F: items, hidden items, Mewtwo (Lv 70), Red's wild Pokémon; open after the Hall of Fame.
usage: build_phase25.py IN.gbc OUT.gbc OUT.ips
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
import build_phase10 as P10
import build_phase12 as P12
import build_phase13 as P13
import build_phase15 as P15
import build_phase17 as P17
import build_phase19 as P19
import build_phase20 as P20
import build_phase21 as P21

FIRST_FLAG = 205                   # 195-204: phase 24
FIRST_MAP = 72                     # 26:71 = Indigo Plateau (phase 24)
BANK, BANK2 = 0x65, 0x66           # free in the JP original
OVERWORLD_TS, SHIP_TS, CAVERN_TS = 40, 38, 37
EV_HOF = 0x34A
RED_CERULEAN = 0x03
VOUCHER, BICYCLE = 0x94, 0x07      # unused item slot -> key item ひきかえけん
SECRET_KEY = P19.SECRET_KEY
POLIWHIRL, JYNX = 61, 124
FANCLUB_JUMP = (0x1D, 0x7FA0)      # the chairman's object script: farsjump 78:5100 (the base mod's)
FANCLUB_TEXTS = {'intro': 0x512E, 'story': 0x5194, 'no': 0x528B, 'again': 0x52A9}
EV_FANCLUB = 0x0341                # Crystal: EVENT_LISTENED_TO_FAN_CLUB_PRESIDENT
SPAWN_TABLE = 0x15346              # SpawnPoints (JP), 4 bytes each
FADE_OUT_BLACK, FADE_IN_BLACK = 0x30, 0x32
SFX_WRONG = 0x19
NEIGHBOURS = ['Route24', 'Route5', 'Route4', 'Route9']
SPR = dict(P19.SPR)
SPR.update({'SPRITE_GUARD': 0x43, 'SPRITE_GRANNY': 0x30, 'SPRITE_MIDDLE_AGED_WOMAN': 0x2E, 'SPRITE_BIKE_SHOP_CLERK': 0x40,
            'SPRITE_GAMBLER': 0x2D, 'SPRITE_MIDDLE_AGED_MAN': 0x2D})
# interiors / caves: (name, Red map id, tileset key, Red's .blk (pokered) or None = the Pikachu hack's)
MAPS = [('CeruleanTrashedHouse', 0x3E, 'House', None), ('CeruleanTradeHouse', 0x3F, 'House', 'red'),
        ('BikeShop', 0x42, 'Club', None), ('CeruleanBadgeHouse', 0xE6, 'Ship', None),
        ('CeruleanCave1F', 0xE4, 'Cavern', None), ('CeruleanCave2F', 0xE2, 'Cavern', None),
        ('CeruleanCaveB1F', 0xE3, 'Cavern', None)]
CONST = {'CERULEAN_TRASHED_HOUSE': 'CeruleanTrashedHouse', 'CERULEAN_TRADE_HOUSE': 'CeruleanTradeHouse',
         'BIKE_SHOP': 'BikeShop', 'CERULEAN_BADGE_HOUSE': 'CeruleanBadgeHouse', 'CERULEAN_CAVE_1F': 'CeruleanCave1F',
         'CERULEAN_CAVE_2F': 'CeruleanCave2F', 'CERULEAN_CAVE_B1F': 'CeruleanCaveB1F'}
# Red's Cerulean City (pokered objects): (x, y, sprite, move, face, text id)
TOWN_OBJS = [(30, 8, 'SPRITE_ROCKET', 'STAY', 'DOWN', 2), (31, 20, 'SPRITE_COOLTRAINER_M', 'STAY', 'DOWN', 3),
             (15, 18, 'SPRITE_SUPER_NERD', 'WALK', 'UP_DOWN', 4), (9, 21, 'SPRITE_SUPER_NERD', 'WALK', 'LEFT_RIGHT', 5),
             (28, 12, 'SPRITE_GUARD', 'STAY', 'DOWN', 6), (29, 26, 'SPRITE_COOLTRAINER_F', 'STAY', 'LEFT', 7),
             # the rival (phase 17) is the 7th object
             (28, 26, 'SLOWBRO', 'STAY', 'DOWN', 8), (9, 27, 'SPRITE_COOLTRAINER_F', 'WALK', 'LEFT_RIGHT', 9),
             (4, 12, 'SPRITE_SUPER_NERD', 'STAY', 'DOWN', 10), (27, 12, 'SPRITE_GUARD', 'STAY', 'DOWN', 11)]
TOWN_SIGNS = [(23, 19, 12), (17, 29, 13), (26, 25, 14), (20, 17, 15), (11, 25, 16), (27, 21, 17)]
TOWN_WARPS = [(27, 11, 'CeruleanTrashedHouse', 1), (13, 15, 'CeruleanTradeHouse', 1), (19, 17, 'CeruleanPokecenter1F', None),
              (30, 19, 'CeruleanGym', None), (13, 25, 'BikeShop', 1), (25, 25, 'CeruleanMart', None),
              (4, 11, 'CeruleanCave1F', 1), (27, 9, 'CeruleanTrashedHouse', 3), (9, 11, 'CeruleanBadgeHouse', 2),
              (9, 9, 'CeruleanBadgeHouse', 1)]


def face(o):
    if o[3] == 'STAY': return P12.FACE.get(o[4], 6), 0
    # Crystal: SPRITEMOVEDATA_WALK_UP_DOWN = 4, WALK_LEFT_RIGHT = 5, WANDER = 2; radius byte = (y << 4) | x
    if o[4] == 'LEFT_RIGHT': return 0x05, 0x01
    if o[4] == 'UP_DOWN': return 0x04, 0x10
    return 0x02, 0x11


def red_objects(name):
    out, w = [], []
    src = open(PR + '/data/maps/objects/%s.asm' % name, encoding='utf-8').read()
    for m in re.finditer(r'object_event\s+([^\n;]*)', src):
        v = [x.strip() for x in m.group(1).split(',')]
        out.append(dict(x=int(v[0]), y=int(v[1]), sprite=v[2], move=v[3], face=v[4], text=v[5], extra=v[6:]))
    for m in re.finditer(r'warp_event\s+(\d+),\s*(\d+),\s*(\w+),\s*(\d+)', src):
        w.append((int(m.group(1)), int(m.group(2)), m.group(3), int(m.group(4))))
    bgs = [(int(x), int(y), t) for x, y, t in re.findall(r'bg_event\s+(\d+),\s*(\d+),\s*(\w+)', src)]
    return out, w, bgs


def hidden(mapconst):
    src = open(PR + '/data/events/hidden_events.asm', encoding='utf-8').read()
    m = re.search(r'hidden_events_for %s\n(.*?)db -1' % mapconst, src, re.S)
    if not m: return []
    return [(int(x), int(y), fn, arg.strip()) for x, y, fn, arg in
            re.findall(r'hidden_event\s+(\d+),\s*(\d+),\s*(\w+),\s*([\w+]+)', m.group(1))]


def warp_override(ts, mp, x, y, cave=False):
    t = ts.quad_tile(*mp.block_at(x, y))
    below = y + 1 < mp.h * 2 and ts.quad_tile(*mp.block_at(x, y + 1)) in ts.passable
    if t in ts.warp_tiles and (below or cave): return COLL_STAIRCASE
    if y == mp.h * 2 - 1: return COLL_CARPET['down']
    if y == 0: return COLL_CARPET['up']
    if x == 0: return COLL_CARPET['left']
    if x == mp.w * 2 - 1: return COLL_CARPET['right']
    for d, (dx, dy) in (('down', (0, 1)), ('up', (0, -1)), ('left', (-1, 0)), ('right', (1, 0))):
        if ts.quad_tile(*mp.block_at(x + dx, y + dy)) not in ts.passable: return COLL_CARPET[d]
    raise AssertionError((mp.name, x, y))


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (0x0B, 0x12, 0x3F, BANK, BANK2):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1 if f > b * 0x4000 else f, b * 0x4000 + 0x4000)
    g0, g1 = fo(0x13, 0x77CD), fo(0x13, 0x77CC + 511)
    while any(rom[g0:g0 + 0x70]): g0 += 1
    sp.set_area(0x13, g0, g1)
    log = []
    FL = PM.Flags(FIRST_FLAG)
    bdir = os.path.dirname(os.path.abspath(src_rom))
    p16 = json.load(open(os.path.join(bdir, 'p16_flags.json')))
    cer = mapid('CeruleanCity')
    mapids = {n: (G26, FIRST_MAP + i) for i, (n, g, tk, b) in enumerate(MAPS)}
    TS = PM.Tilesets(rom, sp)
    # the tileset table (phase 15, bank 0x13) moves to BANK2: its place takes palette maps
    assert rom[PM.TILESETS_BANK] == 0x13
    old = TS.tab; size = 15 * P15.TS_CAP
    nt_ = sp.put(BANK2, bytes(rom[old:old + size])); w16(PM.R_TILESETS[0], nt_); rom[PM.TILESETS_BANK] = BANK2
    rom[old:old + size] = bytes(size); sp.set_area(0x13, old, old + size)
    TS = PM.Tilesets(rom, sp)

    # ================= tilesets: House / Club new (Gen I), variant blocks for the warps of the others
    tss = {'House': Tileset('House', 8, 'house.bst', SC + '/out/pk_house.pkl'),
           'Club': Tileset('Club', 21, 'club.bst', SC + '/out/pk_club.pkl'),
           'Ship': Tileset('Ship', 13, 'ship.bst', SC + '/out/pk_ship.pkl'),
           'Cavern': Tileset('Cavern', 17, 'cavern.bst', SC + '/out/pk_cavern.pkl'),
           'Overworld': Tileset('Overworld', 0, 'overworld.bst', SC + '/out/pk_overworld.pkl', water=0x14, grass=0x52)}
    maps = {}; objs_of = {}
    for n, g, tk, b in MAPS:
        h = RM.header(g)
        blk = n + '.blk' if b is None else '../../pokered/maps/%s.blk' % n
        maps[n] = MapPort(n, tss[tk], h['w'], h['h'], blk)
        if b is None:
            o, w, s, bg = PM.objects_of(n); objs_of[n] = (o, w, bg)
        else:
            objs_of[n] = red_objects(n)
    town = MapPort('CeruleanCity', tss['Overworld'], 20, 18, 'CeruleanCity.blk')
    ov = {n: {(x, y): warp_override(maps[n].ts, maps[n], x, y, maps[n].ts.name == 'Cavern') for x, y, d, w in objs_of[n][1]}
          for n in maps}
    ov['CeruleanCity'] = {(x, y): warp_override(town.ts, town, x, y) for x, y, d, w in TOWN_WARPS}
    ts_id = {'Ship': SHIP_TS, 'Cavern': CAVERN_TS, 'Overworld': OVERWORLD_TS}
    for tk in ('House', 'Club'):
        ts = tss[tk]; mm = {n: maps[n] for n, g, k, b in MAPS if k == tk}
        meta2, coll2, blks = pairwalls.variants(ts, bytes(ts.blocks), bytes(ts.coll), mm, [], {n: ov[n] for n in mm})
        ts.blocks = meta2; ts.coll = bytearray(coll2); ts.nblocks = len(coll2) // 4
        for n in mm: maps[n].blk = blks[n]
        ts_id[tk] = TS.add(ts, BANK, log)
    for tk in ('Ship', 'Cavern', 'Overworld'):
        ts = tss[tk]; e = TS.entry(ts_id[tk])
        am_, ac_ = e[4] | e[5] << 8, e[7] | e[8] << 8
        assert e[3] == e[6] and ac_ > am_
        nb0 = (ac_ - am_) // 16
        meta = bytes(rom[fo(e[3], am_):fo(e[3], am_) + 16 * nb0]); coll = bytes(rom[fo(e[6], ac_):fo(e[6], ac_) + 4 * nb0])
        assert meta[:16 * ts.nblocks] == bytes(ts.blocks)
        mm = {n: maps[n] for n, g, k, b in MAPS if k == tk}
        if tk == 'Overworld': mm = {'CeruleanCity': town}
        meta2, coll2, blks = pairwalls.variants(ts, meta, coll, mm, P21.PAIRS if tk == 'Cavern' else [],
                                                {n: ov[n] for n in mm})
        assert len(coll2) // 4 <= 256
        if len(coll2) // 4 > 128: pairwalls.fix_loadmetatiles(rom)
        am = sp.put(BANK2, meta2 + coll2); ac = am + len(meta2)
        t0 = TS.tab + 15 * ts_id[tk]
        rom[t0 + 3] = BANK2; w16(t0 + 4, am); rom[t0 + 6] = BANK2; w16(t0 + 7, ac)
        for n in mm: mm[n].blk = blks[n]
        log.append('tileset %s: %d blocks (+%d)' % (tk, len(coll2) // 4, len(coll2) // 4 - nb0))

    # ================= trainer party (bank 7E): the Rocket
    groups = P13.read_groups7e(rom)
    def pb(mons): return b'\x00' + b''.join(bytes([lv, PM.MON[P10.MON_ALIAS.get(s, s)]]) for lv, s in mons) + b'\xff'
    rk_cls = PM.TCLS['ROCKET']
    groups[rk_cls - 1].append([encode('ロケットだん@') if False else encode(PM.NAMEPOOL[7] + '@'), pb(PM.red_party('ROCKET', 5))])
    rk_party = len(groups[rk_cls - 1])
    log.append('trainer parties added (bank 7E free %d)' % P13.write_groups7e(rom, groups))

    # ================= the Bike Voucher (key item)
    nb = rom[P12.ITEMNAMES_PTR]; o = fo(nb, r16(P12.ITEMNAMES_PTR + 1)); names = []
    for i in range(256):
        e_ = rom.index(0x50, o); names.append(bytes(rom[o:e_ + 1])); o = e_ + 1
    names[VOUCHER - 1] = encode('ひきかえけん@')
    an = sp.put(BANK, b''.join(names)); rom[P12.ITEMNAMES_PTR] = BANK; w16(P12.ITEMNAMES_PTR + 1, an)
    rom[P12.ITEMATTR + 7 * (VOUCHER - 1):P12.ITEMATTR + 7 * VOUCHER] = rom[P12.ITEMATTR + 7 * (SECRET_KEY - 1):][:7]
    w16(P12.ITEMDESC + 2 * (VOUCHER - 1), sp.put(0x0B, encode('ハナダの　じてんしゃやで<NEXT>じてんしゃと　かえられる@')))

    # ================= Red's trade: Poliwhirl -> Jynx (appended to the NPC trade table)
    ref = P19.NPC_TRADES_REF; assert rom[ref] == 0x21
    to = fo(0x3F, r16(ref + 1)); nt = 7 + len(P19.RED_TRADES)
    table = bytearray(rom[to:to + 16 * nt])
    nick = bytes(RT.R[0x72073 + 3:0x72073 + 7])
    table += bytes([0, POLIWHIRL, JYNX]) + nick + bytes([0x96, 0x66, 0x00]) + (31415 + 1111 * nt).to_bytes(2, 'little') + \
        encode('マサコ')[:3] + b'\x00'
    trade_lola = nt
    na = sp.put(0x3F, bytes(table)); w16(ref + 1, na)

    # ================= texts
    def rt(mapid, tid):
        b, p = RM.text_ptr(mapid, tid); k, v = RM.text_body(b, p); assert k == 'text', (hex(mapid), tid)
        return RM.crystal_text(b, p)
    def hl(mapid, tid, **kw): return [RM.crystal_text(b, p) for b, p in RM.asm_hl(mapid, tid, **kw) if RM.R[RM.fo(b, p)] in (0x00, 0x17)]

    # ================= headers 26:72-78: move what lies there
    u = US.get(); G = u.groups()
    lo, hi = GROUP26_END + 9 * (FIRST_MAP - G26_COUNT - 1), GROUP26_END + 9 * (FIRST_MAP - G26_COUNT - 1 + len(MAPS))
    for gi in range(26):
        n_ = (G[gi + 1] - G[gi]) // 9 if gi + 1 < 26 else FIRST_MAP - 1
        for k in range(n_):
            hdr = G[gi] + 9 * k
            ab = rom[hdr]; ap = r16(hdr + 3); ao_ = fo(ab, ap)
            nconn = bin(rom[ao_ + 11] & 0xF).count('1'); size = 12 + 12 * nconn
            if ao_ < hi and ao_ + size > lo:
                rom[hdr] = BANK2; w16(hdr + 3, sp.put(BANK2, bytes(rom[ao_:ao_ + size])))
                log.append('moved map attributes %X:%04X' % (ab, ap))
    rom[lo:hi] = bytes(hi - lo)

    # ================= scripts / events of the interiors and caves
    hc = hdr_index('CeruleanTradeSpeechHouse'); hv = hdr_index('VictoryRoad'); hcity = hdr_index('CeruleanCity')
    got_bike = FL.new()
    for n, g, tk, b in MAPS:
        objs, warps, bgl = objs_of[n]
        a = Asm(sp.here(BANK)); texts = {}; obj_bytes = []; bgs = []; callbacks = []
        a.label('end'); a.end()
        for idx, o in enumerate(objs):
            tid = idx + 1; lab = 'o%d' % tid; oid = idx + 2; fl = 0xFFFF; typ = 0
            mv, rng = face((0, 0, 0, o['move'], o['face']))
            spr = SPR.get(o['sprite'], 0)
            if o['sprite'] == 'SPRITE_POKE_BALL':
                typ = 1; fl = FL.new(); a.label(lab); a.db(PM.item_id(o['extra'][0]), 1)
            elif n == 'CeruleanCaveB1F' and o['sprite'] == 'SPRITE_MONSTER':
                fl = FL.new(); mv = P12.FACE['DOWN']
                P20.red_wild(a, lab, oid, 'mw', PM.MON['MEWTWO'], int(o['extra'][1]))
                texts['mw'] = bytes([0x00, 0x9E, 0xAE, 0xE3, 0x57])
            elif n == 'CeruleanTrashedHouse' and tid == 1:
                lost, stole = hl(g, 1)
                a.label(lab); a.faceplayer(); a.opentext(); a.checkitem(P12.tm_item(28)); a.iftrue(lab + 'g')
                a.writetext(lab + 's'); a.waitbutton(); a.closetext(); a.end()
                a.label(lab + 'g'); a.writetext(lab + 'l'); a.waitbutton(); a.closetext(); a.end()
                texts[lab + 's'] = stole; texts[lab + 'l'] = lost
            elif n == 'CeruleanTradeHouse' and tid == 2:
                a.label(lab); a.faceplayer(); a.opentext(); a.db(0x95, trade_lola); a.waitbutton(); a.closetext(); a.end()
            elif n == 'BikeShop' and tid == 1:
                bike_shop(a, lab, texts, hl(g, 1, n=240, stop=False), got_bike)
            elif n == 'BikeShop' and tid == 3:
                cool, dear = hl(g, 3)[:2]
                a.label(lab); a.faceplayer(); a.opentext(); a.checkevent(got_bike); a.iftrue(lab + 'c')
                a.checkitem(BICYCLE); a.iftrue(lab + 'c')
                a.writetext(lab + 'd'); a.waitbutton(); a.closetext(); a.end()
                a.label(lab + 'c'); a.writetext(lab + 'k'); a.waitbutton(); a.closetext(); a.end()
                texts[lab + 'd'] = dear; texts[lab + 'k'] = cool
            elif n == 'BikeShop' and tid == 2:
                a.label(lab); a.jumptextfaceplayer(lab + 't'); texts[lab + 't'] = hl(g, 2)[0]
            elif n == 'CeruleanBadgeHouse':
                badge_house(a, lab, texts, g)
            else:
                a.label(lab); a.jumptextfaceplayer(lab + 't'); texts[lab + 't'] = rt(g, tid)
            obj_bytes.append([spr, o['y'] + 4, o['x'] + 4, mv, rng, 0xFF, 0xFF, typ, 0, lab, fl])
        for k, (x, y, tconst) in enumerate(bgl):
            L = 'bg%d' % k; a.label(L); a.jumptext(L + 't'); texts[L + 't'] = rt(g, len(objs) + k + 1)
            bgs.append((y, x, 0, L))
        for k, (x, y, fn, arg) in enumerate(hidden(PM.map_const(n))):
            if fn == 'HiddenItems':
                L = 'hi%d' % k; a.label(L); a.dw(FL.new()); a.db(PM.item_id(arg)); bgs.append((y, x, 7, L))
            elif fn == 'PrintNewBikeText':
                bgs.append((y, x, 0, 'newbike'))
            else: raise AssertionError(fn)
        if n == 'BikeShop':
            j = RT.R.index(encode('ピッカピカの').rstrip(b'\x50')) - 1; assert RT.R[j] == 0
            a.label('newbike'); a.jumptext('nbt'); texts['nbt'] = RT.raw(j) + b'\x57'
        for k_, v in texts.items():
            a.label(k_); a.raw(v if v[-1] in (0x50, 0x57, 0x58) else P12.text(v))
        a.label('mapscripts'); a.db(0); a.db(len(callbacks))
        for t_, l_ in callbacks: a.db(t_); a.dw(l_)
        a.label('events'); a.db(0, 0)
        wl = []
        for x, y, dest, wid in warps:
            if dest == 'LAST_MAP': wl.append((y, x, wid, *cer))
            else: wl.append((y, x, wid, *mapids[CONST[dest]]))
        a.db(len(wl))
        for w_ in wl: a.db(*w_)
        a.db(0)
        a.db(len(bgs))
        for (y_, x_, t_, l_) in bgs: a.db(y_, x_, t_); a.dw(l_)
        a.db(len(obj_bytes))
        for ob in obj_bytes: a.db(*ob[:9]); a.dw(ob[9]); a.dw(ob[10])
        base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
        mp = maps[n]
        blkp = sp.put(BANK, mp.blk)
        aa = sp.put(BANK, bytes([border_of(n) if b is None else 0x0A, mp.h, mp.w, BANK, blkp & 0xFF, blkp >> 8, BANK,
                                 a.labels['mapscripts'] & 0xFF, a.labels['mapscripts'] >> 8, a.labels['events'] & 0xFF,
                                 a.labels['events'] >> 8, 0]))
        hh = GROUP26_END + 9 * (mapids[n][1] - G26_COUNT - 1)
        if tk == 'Cavern':
            hdr = [BANK, ts_id[tk], 4, aa & 0xFF, aa >> 8, rom[hcity + 5], rom[hv + 6], 0x01, 0x00]
        else:
            hdr = [BANK, ts_id[tk], 3, aa & 0xFF, aa >> 8, rom[hcity + 5], rom[hc + 6], rom[hc + 7], rom[hc + 8]]
        rom[hh:hh + 9] = bytes(hdr)
        log.append('%s -> map %d:%d  scripts %X:%04X (%d bytes)' % (n, *mapids[n], BANK, base, len(blob)))

    # ================= Cerulean City
    me = MapEvents(rom, 'CeruleanCity')
    old_warps = list(me.warps)
    a = Asm(sp.here(BANK)); a.bank = BANK; texts = {}
    assert len(me.objs) == 7 and me.objs[6][0][0] == P17.SPR_BLUE                # Crystal's six people + the rival
    rival = me.objs[6]
    me.objs = []
    beat_rk, rk_gone, g1_hide, g2_hide, cave_hide = FL.new(), FL.new(), FL.new(), FL.new(), FL.new()
    oid = {}
    for o in TOWN_OBJS:
        if len(me.objs) == 6: me.objs.append(rival)
        x, y, sprite, move, fc, tid = o
        L = 'c%d' % tid; mv, rng = face(o)
        spr = 0x45 if sprite == 'SLOWBRO' else SPR[sprite]
        flag = {2: rk_gone, 6: g1_hide, 11: g2_hide, 10: cave_hide}.get(tid, 0xFFFF)
        me.objs.append([bytearray([spr, y + 4, x + 4, mv, rng, 0xFF, 0xFF, 0, 0, 0, 0, flag & 0xFF, flag >> 8]), L])
        oid[tid] = len(me.objs) + 1
        if tid == 2: continue
        if tid == 7:
            ts_ = hl(RED_CERULEAN, 7)
            a.label(L); a.faceplayer(); a.opentext(); a.db(0x17, 64)                        # random 64
            a.db(0x0A, 44); a.dw(L + 'a'); a.db(0x0A, 24); a.dw(L + 'b'); a.writetext(L + 'tc'); a.sjump(L + 'e')
            a.label(L + 'a'); a.writetext(L + 'ta'); a.sjump(L + 'e')
            a.label(L + 'b'); a.writetext(L + 'tb')
            a.label(L + 'e'); a.waitbutton(); a.closetext(); a.end()
            texts[L + 'ta'], texts[L + 'tb'], texts[L + 'tc'] = ts_[:3]
        elif tid == 8:
            ts_ = hl(RED_CERULEAN, 8)
            a.label(L); a.opentext(); a.db(0x17, 64)
            for k, th in enumerate((44, 29, 14)):
                a.db(0x0A, th); a.dw(L + 'x%d' % k)
            a.writetext(L + 't3'); a.sjump(L + 'e')
            for k in range(3):
                a.label(L + 'x%d' % k); a.writetext(L + 't%d' % k); a.sjump(L + 'e')
            a.label(L + 'e'); a.waitbutton(); a.closetext(); a.end()
            for k in range(4): texts[L + 't%d' % k] = ts_[k]
        else:
            a.label(L); a.jumptextfaceplayer(L + 't'); texts[L + 't'] = rt(RED_CERULEAN, tid)
    # the Rocket (Red: steps on (30,7) / (30,9) or talking)
    rk = oid[2]
    rkt = [RM.crystal_text(RM.text_ptr(RED_CERULEAN, 2)[0], p) for p in (0x5F0C, 0x5FB9, 0x5FD9, 0x5F94, 0x5F55)]
    texts.update(rk_t=rkt[0], rk_w=rkt[1], rk_ill=rkt[2], rk_full=rkt[3], rk_recv=rkt[4])
    a.label('c2'); a.checkevent(beat_rk); a.iftrue('rk_give'); a.faceplayer(); a.sjump('rk_fight')
    for y_, pdir, rdir in ((7, 0, 1), (9, 1, 0)):
        L = 'rk_c%d' % y_; me.coords.append((0xFF, y_, 30, L))
        a.label(L); a.checkevent(beat_rk); a.iftrue('end'); a.turnobject(0, pdir); a.turnobject(rk, rdir)
    a.label('rk_fight')
    a.opentext(); a.writetext('rk_t'); a.waitbutton(); a.closetext()
    a.winlosstext('rk_w', 0); a.loadtrainer(rk_cls, rk_party); a.startbattle(); a.reloadmapafterbattle()
    a.setevent(beat_rk)
    a.label('rk_give')
    a.opentext(); a.writetext('rk_ill'); a.db(0x1F, P12.tm_item(28), 1); a.iffalse('rk_nf')     # giveitem
    a.writetext('rk_recv'); a.closetext()
    a.special(FADE_OUT_BLACK); a.disappear(rk); a.disappear(oid[11]); a.appear(oid[6]); a.special(FADE_IN_BLACK); a.end()
    a.label('rk_nf'); a.writetext('rk_full'); a.waitbutton(); a.closetext(); a.end()
    a.label('end'); a.end()
    # guards (Red: the Rocket beaten or Bill's S.S. Ticket) and the Cerulean Cave guard (until the Hall of Fame)
    a.label('cr_obj')
    a.checkevent(rk_gone); a.iftrue('cr_sw'); a.checkevent(p16['got_ss_ticket']); a.iftrue('cr_sw')
    a.setevent(g1_hide); a.clearevent(g2_hide); a.sjump('cr_cave')
    a.label('cr_sw'); a.clearevent(g1_hide); a.setevent(g2_hide)
    a.label('cr_cave'); a.checkevent(EV_HOF); a.iftrue('cr_c1'); a.clearevent(cave_hide); a.sjump('cr_next')
    a.label('cr_c1'); a.setevent(cave_hide)
    a.label('cr_next')
    old_cb = [r for t_, r in me.callbacks if t_ == 2]
    assert len(old_cb) == 1 and old_cb[0][0] == 'far'                          # phase 17's (the rival)
    a.farsjump(old_cb[0][1], old_cb[0][2])
    me.callbacks = [(t_, r) for t_, r in me.callbacks if t_ != 2] + [(2, 'cr_obj')]
    # signs, hidden item
    me.bgs = []
    for k, (x, y, tid) in enumerate(TOWN_SIGNS):
        L = 'cs%d' % k; a.label(L); a.jumptext(L + 't'); texts[L + 't'] = rt(RED_CERULEAN, tid); me.bgs.append((y, x, 0, L))
    for k, (x, y, fn, arg) in enumerate(hidden('CERULEAN_CITY')):
        fl = FL.new(); me.bgs.append((y, x, 7, ('data', bytes([fl & 0xFF, fl >> 8, PM.item_id(arg)]))))
    # warps
    dest_of = {}
    for w in old_warps: dest_of[(w[3], w[4])] = w[2]
    me.warps = []
    for x, y, dn, wid in TOWN_WARPS:
        if wid is None:
            d = mapid(dn); me.warps.append(bytes([y, x, dest_of[d], *d]))
        else:
            me.warps.append(bytes([y, x, wid, *mapids[dn]]))
    for k, v in texts.items():
        a.label(k); a.raw(v if v[-1] in (0x50, 0x57, 0x58) else P12.text(v))
    # chairman of the Fan Club: Red's Bike Voucher
    fan_club(a, texts, rom)
    me.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    me.install(a)
    fb, fa = FANCLUB_JUMP; o_ = fo(fb, fa); assert rom[o_] == 0x04
    rom[o_ + 1] = BANK; w16(o_ + 2, a.labels['fanclub'])
    log.append('CeruleanCity: Red events %X:%04X (%d bytes)' % (BANK, base, len(blob)))

    # ================= Cerulean City: Red's blocks; the neighbours' edges translated
    ca = attrs(rom, hcity); ao = ca['attr_off']
    assert (ca['w'], ca['h']) == (20, 18)
    old_cer = (ca['blkbank'], ca['blk'])
    cblk = sp.put(BANK, town.blk)
    rom[hcity + 1] = OVERWORLD_TS
    rom[ao] = border_of('CeruleanCity'); rom[ao + 3] = BANK; w16(ao + 4, cblk)
    e = TS.entry(OVERWORLD_TS); co = fo(e[6], e[7] | e[8] << 8)
    g1side = X.gen1_side(tss['Overworld'], bytes(rom[co:co + 4 * 128]))
    crside = X.crystal_side(rom, TS)
    xcer = sp.put(BANK, X.translate(MapPort('CeruleanCity', tss['Overworld'], 20, 18, 'CeruleanCity.blk').blk, g1side, crside))           # Red's Cerulean in Crystal's tileset
    # the neighbours' blocks move to BANK2, next to their Gen I translations
    allhdr = [G[gi] + 9 * k for gi in range(26) for k in range((G[gi + 1] - G[gi]) // 9 if gi + 1 < 26 else FIRST_MAP + len(MAPS) - 1)]
    allhdr = [h_ for h_ in allhdr if rom[h_] and attrs(rom, h_)["scbank"]]
    def conns(hdr):
        a_ = attrs(rom, hdr); o2 = a_['attr_off']
        return [o2 + 12 + 12 * k for k in range(bin(a_['conn'] & 0xF).count('1'))]
    xl = {}
    for nn in NEIGHBOURS:
        na_ = attrs(rom, hdr_index(nn)); size = na_['w'] * na_['h']; ob, oa = na_['blkbank'], na_['blk']
        blk = bytes(rom[fo(ob, oa):fo(ob, oa) + size])
        nbp = sp.put(BANK2, blk); xl[nn] = (oa, sp.put(BANK2, X.translate(blk, crside, g1side)))
        rom[na_['attr_off'] + 3] = BANK2; w16(na_['attr_off'] + 4, nbp)
        tgt = mapid(nn)
        for hdr in allhdr:
            for c in conns(hdr):
                if (rom[c], rom[c + 1]) == tgt:
                    s_ = r16(c + 2); assert oa <= s_ < oa + size, (nn, hex(hdr))
                    if hdr == hcity: w16(c + 2, xl[nn][1] + s_ - oa)        # Red's Cerulean: the translation
                    else: w16(c + 2, nbp + s_ - oa)
    for nn in NEIGHBOURS:                                                     # the neighbours see Red's Cerulean
        for c in conns(hdr_index(nn)):
            if (rom[c], rom[c + 1]) == cer:
                s_ = r16(c + 2); assert old_cer[1] <= s_ < old_cer[1] + 360; w16(c + 2, xcer + s_ - old_cer[1])
    # Route 9: Red's offset (Red's road east of the town is 4 blocks higher than Crystal's)
    import build_phase22 as P22
    r9 = mapid('Route9'); a9 = attrs(rom, hdr_index('Route9'))
    for c in conns(hcity):
        if (rom[c], rom[c + 1]) == r9:
            rom[c:c + 12] = P22.connection('east', 20, 18, r9, 30, 9, 4, xl['Route9'][1] + P22.strip_src('east', 30, 4))
    for c in conns(hdr_index('Route9')):
        if (rom[c], rom[c + 1]) == cer:
            rom[c:c + 12] = P22.connection('west', 30, 9, cer, 20, 18, -4, xcer + P22.strip_src('west', 20, -4))
    # Crystal's Pokémon Center / Gym / Mart lead back to Red's doors
    for i, (x, y, dn, wid) in enumerate(TOWN_WARPS):
        if wid is not None: continue
        a_ = attrs(rom, hdr_index(dn)); ev = parse_events(rom, a_['scbank'], a_['events'])
        n_ = 0
        for o_, w in ev['warps']:
            if (w[3], w[4]) == cer: rom[o_ + 2] = i + 1; n_ += 1
        assert n_, dn
    # spawn point (fly / last Pokémon Center): in front of Red's Pokémon Center
    sp_i = [i for i in range(40) if (rom[SPAWN_TABLE + 4 * i], rom[SPAWN_TABLE + 4 * i + 1]) == cer]
    assert len(sp_i) == 1
    rom[SPAWN_TABLE + 4 * sp_i[0] + 2:SPAWN_TABLE + 4 * sp_i[0] + 4] = bytes([19, 18])

    # ================= wild Pokémon: Crystal's Victory Road (no longer reached) out, Cerulean Cave in
    p = P15.KANTO_GRASS; ents = []
    while rom[p] != 0xFF: ents.append(bytes(rom[p:p + 47])); p += 47
    vr = mapid('VictoryRoad'); ents = [x for x in ents if (x[0], x[1]) != vr]
    for n in ('CeruleanCave1F', 'CeruleanCave2F', 'CeruleanCaveB1F'):
        t = open(PR + '/data/wild/maps/%s.asm' % n, encoding='utf-8').read()
        t = re.sub(r'IF DEF\(_BLUE\).*?ENDC', '', t, flags=re.S)
        rate = int(re.search(r'def_grass_wildmons (\d+)', t).group(1))
        slots = [(int(l), s) for l, s in re.findall(r'db\s+(\d+), (\w+)', t.split('end_grass_wildmons')[0])]
        assert len(slots) == 10, n
        pick = [slots[i] for i in (0, 1, 2, 3, 6, 8, 9)]
        ents.append(bytes([*mapids[n], rate, rate, rate]) + bytes(sum(([lv, PM.MON[P10.MON_ALIAS.get(s, s)]] for lv, s in pick), [])) * 3)
    blob = b''.join(ents) + b'\xff'
    end_old = p + 1
    assert all(v == 0 for v in rom[end_old:P15.KANTO_GRASS + len(blob)])
    rom[P15.KANTO_GRASS:P15.KANTO_GRASS + len(blob)] = blob
    if len(blob) < end_old - P15.KANTO_GRASS: rom[P15.KANTO_GRASS + len(blob):end_old] = bytes(end_old - P15.KANTO_GRASS - len(blob))

    P17.fix_outdoor_sprites(rom, log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


def bike_shop(a, lab, texts, t, got_bike):
    """Red: BikeShopClerkText"""
    how, oh, exch, full, welcome, like, cant, again = t[:8]
    texts.update({lab + 'how': how, lab + 'oh': oh, lab + 'ex': exch, lab + 'full': full, lab + 'wel': welcome,
                  lab + 'like': like, lab + 'cant': cant, lab + 'again': again})
    a.label(lab); a.faceplayer(); a.opentext()
    a.checkevent(got_bike); a.iftrue(lab + 'h'); a.checkitem(BICYCLE); a.iftrue(lab + 'h')
    a.checkitem(VOUCHER); a.iffalse(lab + 'w')
    a.writetext(lab + 'oh'); a.db(0x1F, BICYCLE, 1); a.iffalse(lab + 'f')                     # giveitem
    a.db(0x20, VOUCHER, 1); a.setevent(got_bike)                                             # takeitem
    a.writetext(lab + 'ex'); a.waitbutton(); a.closetext(); a.end()
    a.label(lab + 'f'); a.writetext(lab + 'full'); a.waitbutton(); a.closetext(); a.end()
    a.label(lab + 'h'); a.writetext(lab + 'how'); a.waitbutton(); a.closetext(); a.end()
    a.label(lab + 'w'); a.writetext(lab + 'wel'); a.writetext(lab + 'like')
    a.db(0x4F); a.dw(lab + 'mh'); a.db(0x58); a.db(0x50)                                     # loadmenu ; verticalmenu ; closewindow
    a.ifnotequal(1, lab + 'c'); a.writetext(lab + 'cant')
    a.label(lab + 'c'); a.writetext(lab + 'again'); a.waitbutton(); a.closetext(); a.end()
    a.label(lab + 'mh'); a.db(0x40, 0, 0, 4, 17); a.dw(lab + 'md'); a.db(1)                  # MENU_BACKUP_TILES, (y,x)-(y,x)
    a.label(lab + 'md'); a.db(0xC0, 2)
    menu = RT.R[0x1dbf6:0x1dd80]; i = menu.index(bytes([0x2C, 0xC3, 0xDE, 0xBC, 0xE0, 0x7F])); j = menu.index(0x4E, i)
    k = menu.index(0x50, j)
    a.raw(bytes(menu[i:j]) + b'\x50' + bytes(menu[j + 1:k]) + b'\x50')


def badge_house(a, lab, texts, g):
    """Red: CeruleanBadgeHouseMiddleAgedManText (the list is a two-column menu; B = cancel)"""
    ptrs = RM.asm_hl(g, 1)
    tl = []
    for b, p in ptrs:
        o = RM.fo(b, p)
        cand = [RM.R[o + 2 * i] | RM.R[o + 2 * i + 1] << 8 for i in range(8)]
        if all(0x4000 <= c < 0x8000 and RM.R[RM.fo(b, c)] in (0x00, 0x17) for c in cand) and RM.R[o] not in (0x00, 0x17):
            tl = [RM.crystal_text(b, c) for c in cand]
    plain = [RM.crystal_text(b, p) for b, p in ptrs if RM.R[RM.fo(b, p)] in (0x00, 0x17)]
    intro, which, visit = plain[:3]
    assert len(tl) == 8
    texts.update({lab + 'i': intro, lab + 'q': which, lab + 'v': visit})
    a.label(lab); a.faceplayer(); a.opentext(); a.writetext(lab + 'i')
    a.label(lab + 'l'); a.writetext(lab + 'q')
    a.db(0x4F); a.dw(lab + 'mh'); a.db(0x57); a.db(0x50)                                     # loadmenu ; _2dmenu ; closewindow
    for k in range(8):
        a.ifequal(k + 1, lab + 'b%d' % k)
    a.writetext(lab + 'v'); a.waitbutton(); a.closetext(); a.end()
    for k in range(8):
        a.label(lab + 'b%d' % k); a.writetext(lab + 't%d' % k); a.waitbutton(); a.sjump(lab + 'l')
        texts[lab + 't%d' % k] = tl[k]
    a.label(lab + 'mh'); a.db(0x40, 0, 0, 8, 19); a.dw(lab + 'md'); a.db(1)
    a.label(lab + 'md'); a.db(0xC0, 0x42, 9, BANK); a.dw(lab + 'mt'); a.db(BANK); a.dw(0)        # 5 rows x 2 columns
    names = RT.R.index(encode('グレーバッジ').rstrip(b'\x50')); out = b''; o = names
    for _ in range(8):
        e = RT.R.index(0x50, o); out += bytes(RT.R[o:e + 1]); o = e + 1
    a.label(lab + 'mt'); a.raw(out)


def fan_club(a, texts, rom):
    """the chairman: Red's story and the Bike Voucher"""
    R = RT.R
    k = R.index(bytes([0x50, 0x11, 0x00, 0x51]), 0x5AE00)
    e = R.index(0x57, k)
    texts_ = {'fc_got': encode('{00}<PLAYER>は　かいちょうから<LINE>ひきかえけんを　もらった！').rstrip(b'\x50') + b'\x50\x0f' +
              bytes(R[k + 2:e + 1])}
    full = R.index(encode('にもつが　いっぱい　じゃ').rstrip(b'\x50')) - 1; assert R[full] == 0
    texts_['fc_full'] = RT.raw(full) + b'\x57'
    a.label('fanclub'); a.faceplayer(); a.opentext(); a.checkevent(EV_FANCLUB); a.iftrue('fc_again')
    a.farwritetext(0x78, FANCLUB_TEXTS['intro']); a.yesorno(); a.iffalse('fc_no')
    a.farwritetext(0x78, FANCLUB_TEXTS['story']); a.promptbutton()
    a.db(0x1F, VOUCHER, 1); a.iffalse('fc_f')
    a.setevent(EV_FANCLUB); a.writetext('fc_got'); a.waitbutton(); a.closetext(); a.end()
    a.label('fc_f'); a.writetext('fc_full'); a.waitbutton(); a.closetext(); a.end()
    a.label('fc_no'); a.farwritetext(0x78, FANCLUB_TEXTS['no']); a.waitbutton(); a.closetext(); a.end()
    a.label('fc_again'); a.farwritetext(0x78, FANCLUB_TEXTS['again']); a.waitbutton(); a.closetext(); a.end()
    for k_, v in texts_.items():
        a.label(k_); a.raw(v)


if __name__ == '__main__':
    main()
