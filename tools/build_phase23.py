#!/usr/bin/env python3
"""Phase 23: Red's Victory Road (1F-3F, ported from the Pikachu full-color hack), for good (also after the Hall of
Fame), working like Red:
 * Strength boulders on the switches open the way (1F: reset when the player enters 2F, as in Red; 2F: two
   switches; 3F: one switch), the 3F hole (boulders and the player fall to 2F), Red's elevation edges.
 * Red's trainers (Tamer = phase 10's もうじゅうつかい class), items, hidden items, Moltres (Lv 50), wild Pokémon.
Crystal's Victory Road Gate (north door) and Route 23 (cave) lead there instead of Crystal's Victory Road.
usage: build_phase23.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
import pkmap
import portmaps as PM
import pairwalls
import build_phase10 as P10
import build_phase12 as P12
import build_phase13 as P13
import build_phase15 as P15
import build_phase20 as P20
import build_phase21 as P21

FIRST_FLAG = 163
FIRST_MAP = 68                     # 26:63-67 = Seafoam Islands (phase 21)
CAVERN_TS = 37
V1, V2, V3 = 'VictoryRoad1F', 'VictoryRoad2F', 'VictoryRoad3F'
MAPS = [(V1, 0x6C), (V2, 0xC2), (V3, 0xC6)]
CONST = {'VICTORY_ROAD_1F': V1, 'VICTORY_ROAD_2F': V2, 'VICTORY_ROAD_3F': V3}
# Red's map scripts: boulder switches (x, y) -> (block x, block y, new block)
SWITCHES = {V1: [((17, 13), (4, 6, 0x1D))], V2: [((1, 16), (3, 4, 0x15)), ((9, 16), (11, 7, 0x1D))],
            V3: [((3, 5), (3, 5, 0x1D))]}
HOLE_3F, LAND_2F = (23, 15), (22, 16)
SCENE_BYTE = {V1: 0xDA60, V2: 0xDA61, V3: 0xDA62}
SPR_BOULDER, SPR_BIRD, SPR_BALL, MV_BOULDER, STD_BOULDER = 0x5A, 0x4E, 0x54, 0x19, 0x0E
COLL_PIT = 0x60
W_SCRIPTVAR, W_OBJECTSTRUCT1 = 0xC2DD, 0xD4C9 + 0x28
MON = PM.MON


def boulder_at_asm(base, table):
    """callasm: wScriptVar = (a standing Strength boulder at table[wScriptVar])"""
    c = bytearray(); L = {}; J = []
    def e(*b): c.extend(b)
    def jr(op, lab): e(op); J.append((len(c), lab)); e(0)
    def lab(n): L[n] = len(c)
    tab_at = None
    e(0xFA, W_SCRIPTVAR & 0xFF, W_SCRIPTVAR >> 8, 0x87, 0x5F, 0x16, 0x00)   # ld a,[wScriptVar] ; add a ; ld e,a ; ld d,0
    e(0x21); J.append((len(c), 'TAB16')); e(0, 0); e(0x19)                  # ld hl, table ; add hl, de
    e(0x2A, 0xC6, 4, 0x47, 0x7E, 0xC6, 4, 0x4F)                             # b = x+4 ; c = y+4
    e(0x21, W_OBJECTSTRUCT1 & 0xFF, W_OBJECTSTRUCT1 >> 8, 0x16, 12)         # ld hl, struct 1 ; ld d, 12
    lab('loop'); e(0x7E, 0xA7); jr(0x28, 'next')                            # sprite
    e(0xE5, 0x23, 0x23, 0x23, 0x7E, 0xFE, MV_BOULDER); jr(0x20, 'pop')       # movement type
    e(0x23, 0x23, 0x23, 0x23, 0x7E, 0xFE, 0xFF); jr(0x20, 'pop')             # walking: standing
    e(0x7D, 0xC6, 9, 0x6F, 0x7C, 0xCE, 0, 0x67)                              # hl += 9 (-> map x)
    e(0x2A, 0xB8); jr(0x20, 'pop'); e(0x7E, 0xB9); jr(0x20, 'pop')
    e(0xE1, 0x3E, 1); jr(0x18, 'done')
    lab('pop'); e(0xE1)
    lab('next'); e(0x7D, 0xC6, 0x28, 0x6F, 0x7C, 0xCE, 0, 0x67, 0x15); jr(0x20, 'loop')
    e(0xAF)
    lab('done'); e(0xEA, W_SCRIPTVAR & 0xFF, W_SCRIPTVAR >> 8, 0xC9)
    lab('table')
    for x, y in table: e(x, y)
    for p, n in J:
        if n == 'TAB16':
            t = base + L['table']; c[p] = t & 0xFF; c[p + 1] = t >> 8
        else:
            d = L[n] - (p + 1); assert -128 <= d < 128; c[p] = d & 0xFF
    return bytes(c)


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (0x60, 0x61, 0x62, 0x63, 0x78, 0x79):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1, b * 0x4000 + 0x4000)
    log = []
    FL = PM.Flags(FIRST_FLAG)
    mapids = {n: (G26, FIRST_MAP + i) for i, (n, g) in enumerate(MAPS)}
    objs_of = {n: PM.objects_of(n) for n, g in MAPS}

    # ================= Crystal's doors -> Red's Victory Road
    vr = mapid('VictoryRoad')
    door = {}
    for owner, dest in (('VictoryRoadGate', (V1, 1)), ('Route23', (V2, 2))):
        a_ = attrs(rom, hdr_index(owner)); ev = parse_events(rom, a_['scbank'], a_['events'])
        ws = [i for i, (o_, w) in enumerate(ev['warps']) if (w[3], w[4]) == vr]
        assert len(ws) == 2, (owner, ws)
        for i in ws:
            o_ = ev['warps'][i][0]; rom[o_ + 2] = dest[1]; rom[o_ + 3], rom[o_ + 4] = mapids[dest[0]]
        door[owner] = (ws[0] + 1, mapid(owner))
    last = {3: door['VictoryRoadGate'], 4: door['Route23']}       # Red: LAST_MAP warp 3 (1F) / 4 (2F)

    # ================= Cavern tileset: warps, the hole, switch states, Red's elevation edges
    TS = PM.Tilesets(rom, sp)
    cav = Tileset('Cavern', 17, 'cavern.bst', SC + '/out/pk_cavern.pkl')
    e = TS.entry(CAVERN_TS)
    am_, ac_ = e[4] | e[5] << 8, e[7] | e[8] << 8
    assert e[3] == e[6] and ac_ > am_ and (ac_ - am_) % 16 == 0
    nb0 = (ac_ - am_) // 16                                       # phase 21: meta then collision, back to back
    mo, co = fo(e[3], am_), fo(e[6], ac_)
    meta = bytes(rom[mo:mo + 16 * nb0]); coll = bytearray(rom[co:co + 4 * nb0])
    assert meta[:16 * cav.nblocks] == bytes(cav.blocks)
    maps = {}
    for n, g in MAPS:
        h = pkmap.header(g); maps[n] = MapPort(n, cav, h['w'], h['h'], n + '.blk')
    for n, g in MAPS:
        mp = maps[n]
        for (x, y, dest, wid) in objs_of[n][1]:
            b_, q = mp.block_at(x, y); tile = cav.quad_tile(b_, q)
            if tile in cav.warp_tiles: v = COLL_STAIRCASE
            elif y == mp.h * 2 - 1 or y == 0 or x == 0 or x == mp.w * 2 - 1:
                v = COLL_CARPET['down'] if y == mp.h * 2 - 1 else COLL_CARPET['up'] if y == 0 else \
                    COLL_CARPET['left'] if x == 0 else COLL_CARPET['right']
            else: raise AssertionError((n, x, y, hex(tile)))
            old = coll[4 * b_ + q]
            assert old in (COLL_FLOOR, COLL_WALL, v), (n, x, y, hex(old), hex(v))
            coll[4 * b_ + q] = v
    allmaps = dict(maps); ov = {V3: {HOLE_3F: COLL_PIT}}
    for n, sws in SWITCHES.items():
        for k, (xy, (bx, by, nb_)) in enumerate(sws):
            m2 = MapPort(n, cav, maps[n].w, maps[n].h, n + '.blk')
            blk = bytearray(m2.blk); blk[by * m2.w + bx] = nb_; m2.blk = bytes(blk)
            allmaps['%s#%d' % (n, k)] = m2
            if n == V3: ov['%s#%d' % (n, k)] = {HOLE_3F: COLL_PIT}
    meta2, coll2, blks = pairwalls.variants(cav, meta, bytes(coll), allmaps, P21.PAIRS, ov)
    if len(coll2) // 4 > 128: pairwalls.fix_loadmetatiles(rom)
    am = sp.put(0x62, meta2 + coll2); ac = am + len(meta2)
    t0 = TS.tab + 15 * CAVERN_TS
    rom[t0 + 3] = 0x62; w16(t0 + 4, am); rom[t0 + 6] = 0x62; w16(t0 + 7, ac)
    log.append('Cavern tileset: %d blocks (+%d), metatiles 62:%04X collision 62:%04X'
               % (len(coll2) // 4, (len(coll2) - len(coll)) // 4, am, ac))
    changes = {}                                                   # (map, switch #) -> [(x, y, block)]
    for n, sws in SWITCHES.items():
        base = blks[n]; w_ = maps[n].w
        for k in range(len(sws)):
            alt = blks['%s#%d' % (n, k)]
            changes[(n, k)] = [(2 * (i % w_), 2 * (i // w_), alt[i]) for i in range(len(base)) if alt[i] != base[i]]
            assert changes[(n, k)], (n, k)

    # ================= boulder check (asm) for the switches
    table = [xy for n, g in MAPS for xy, _ in SWITCHES[n]]
    ab = sp.here(0x63); code = boulder_at_asm(ab, table); assert sp.put(0x63, code) == ab
    sw_index = {}; i_ = 0
    for n, g in MAPS:
        for k in range(len(SWITCHES[n])): sw_index[(n, k)] = i_; i_ += 1
    sw_fl = {key: FL.new() for key in sw_index}

    # ================= trainer parties (bank 7E)
    groups = P13.read_groups7e(rom)
    def pb(mons): return b'\x00' + b''.join(bytes([lv, MON[P10.MON_ALIAS.get(s, s)]]) for lv, s in mons) + b'\xff'
    party_of = {}; ti = 0
    for n, g in MAPS:
        for i, o in enumerate(objs_of[n][0]):
            if o['extra'] and o['extra'][0].startswith('OPP_'):
                c = o['extra'][0][4:]; k = int(o['extra'][1]); cid = PM.TCLS[c]
                groups[cid - 1].append([encode(PM.NAMEPOOL[(ti + 5) % len(PM.NAMEPOOL)] + '@'), pb(PM.red_party(c, k))])
                party_of[(n, i)] = (cid, len(groups[cid - 1])); ti += 1
    log.append('trainer parties added (bank 7E free %d)' % P13.write_groups7e(rom, groups))

    # ================= scripts / events
    nred = {n: len(objs_of[n][1]) for n, g in MAPS}
    for n, g in MAPS:
        objs, warps, skip, bgl = objs_of[n]
        a = Asm(sp.here(0x63)); texts = {}; obj_bytes = []; bgs = []; callbacks = []
        a.label('end'); a.end()
        pushable = []
        for idx, o in enumerate(objs):
            tid = idx + 1; lab = 'o%d' % tid; oid = idx + 2
            if o['sprite'] == 'SPRITE_BOULDER':
                pushable.append(tid)
                fl = FL.new() if n == V3 else 0xFFFF
                a.label(lab); a.jumpstd(STD_BOULDER)
                obj_bytes.append([SPR_BOULDER, o['y'] + 4, o['x'] + 4, MV_BOULDER, 0, 0xFF, 0xFF, 0, 0, lab, fl])
            elif o['sprite'] == 'SPRITE_BIRD':
                P20.red_wild(a, lab, oid, 'mo', MON['MOLTRES'], int(o['extra'][1]))
                texts['mo'] = encode('{00}ギャーオ！')
                obj_bytes.append([SPR_BIRD, o['y'] + 4, o['x'] + 4, P12.FACE['UP'], 0, 0xFF, 0xFF, 0, 0, lab, FL.new()])
            elif o['sprite'] == 'SPRITE_POKE_BALL':
                fl = FL.new(); a.label(lab); a.db(PM.item_id(o['extra'][0]), 1)
                obj_bytes.append([SPR_BALL, o['y'] + 4, o['x'] + 4, 6, 0, 0xFF, 0xFF, 1, 0, lab, fl])
            else:
                sight, seen, aft, win = P12.trainer_texts(g, tid)
                fl = FL.new(); cid, pid = party_of[(n, idx)]
                a.label(lab); a.dw(fl); a.db(cid, pid); a.dw(lab + 's'); a.dw(lab + 'w'); a.dw(0); a.dw(lab + 'x')
                a.label(lab + 'x'); a.endifjustbattled(); a.opentext(); a.writetext(lab + 'a'); a.waitbutton(); a.closetext(); a.end()
                texts[lab + 's'] = seen; texts[lab + 'w'] = win; texts[lab + 'a'] = aft
                obj_bytes.append([PM.SPR[o['sprite']], o['y'] + 4, o['x'] + 4, P12.FACE.get(o['face'], 6), 0, 0xFF, 0xFF,
                                  2, sight, lab, fl])
        for k, (x, y, fn, arg) in enumerate(PM.hidden_events(PM.map_const(n))):
            assert fn == 'HiddenItems'
            L = 'hi%d' % k; a.label(L); a.dw(FL.new()); a.db(PM.item_id(arg)); bgs.append((y, x, 7, L))
        # ---- switches: Red's per-frame check of a boulder on the switch; the blocks stay changed on reload
        a.label('scene0')
        for k, (xy, _) in enumerate(SWITCHES[n]):
            a.checkevent(sw_fl[(n, k)]); a.iftrue('sw%dn' % k)
            a.db(0x15, sw_index[(n, k)]); a.callasm(0x63, ab); a.iffalse('sw%dn' % k)        # setval ; callasm
            a.setevent(sw_fl[(n, k)])
            for (x_, y_, b_) in changes[(n, k)]: a.changeblock(x_, y_, b_)
            a.refreshmap(); a.end()
            a.label('sw%dn' % k)
        a.end()
        a.label('cb_tiles')
        for k in range(len(SWITCHES[n])):
            a.checkevent(sw_fl[(n, k)]); a.iffalse('cbt%d' % k)
            for (x_, y_, b_) in changes[(n, k)]: a.changeblock(x_, y_, b_)
            a.label('cbt%d' % k)
        a.endcallback()
        callbacks.append((1, 'cb_tiles'))                                          # MAPCALLBACK_TILES
        if n == V2:                                                                # Red: entering 2F resets 1F's switch
            a.label('cb_new'); a.clearevent(sw_fl[(V1, 0)]); a.endcallback()
            callbacks.append((5, 'cb_new'))                                        # MAPCALLBACK_NEWMAP
        if n == V3:                                                                # the hole: boulders fall to 2F
            a.label('cb_cq')
            a.db(0x7C); a.dw('cq'); a.endcallback()                               # writecmdqueue
            a.label('cq'); a.db(2); a.dw('stones'); a.dw(0)
            a.label('stones')
            for i in pushable: a.db(nred[n] + 1, i + 1); a.dw('fall%d' % i)
            a.db(0xFF)
            hole_fl = FL.new()
            for i in pushable:
                a.label('fall%d' % i); a.disappear(i + 1); a.setevent(hole_fl); a.end()
            callbacks.append((3, 'cb_cq'))
        for k_, v in texts.items():
            a.label(k_); a.raw(P12.text(v))
        a.label('mapscripts'); a.db(1); a.dw('scene0'); a.dw(0)
        a.db(len(callbacks))
        for t_, l_ in callbacks: a.db(t_); a.dw(l_)
        a.label('events'); a.db(0, 0)
        wl = []
        for x, y, dest, wid in warps:
            if dest == 'LAST_MAP': wl.append((y, x, last[wid][0], *last[wid][1]))
            else: wl.append((y, x, wid, *mapids[CONST[dest]]))
        if n == V3: wl.append((HOLE_3F[1], HOLE_3F[0], nred[V2] + 1, *mapids[V2]))
        if n == V2: wl.append((LAND_2F[1], LAND_2F[0], nred[V3] + 1, *mapids[V3]))
        a.db(len(wl))
        for w_ in wl: a.db(*w_)
        a.db(0)
        a.db(len(bgs))
        for (y_, x_, t_, l_) in bgs: a.db(y_, x_, t_); a.dw(l_)
        a.db(len(obj_bytes))
        for ob in obj_bytes: a.db(*ob[:9]); a.dw(ob[9]); a.dw(ob[10])
        base = a.base; blob = a.done(); assert sp.put(0x63, blob) == base
        mp = maps[n]
        blkp = sp.put(0x62, blks[n])
        aa = sp.put(0x62, bytes([border_of(n), mp.h, mp.w, 0x62, blkp & 0xFF, blkp >> 8, 0x63, a.labels['mapscripts'] & 0xFF,
                                 a.labels['mapscripts'] >> 8, a.labels['events'] & 0xFF, a.labels['events'] >> 8, 0]))
        hh = GROUP26_END + 9 * (mapids[n][1] - G26_COUNT - 1)
        hv = hdr_index('VictoryRoad')
        rom[hh:hh + 9] = bytes([0x62, CAVERN_TS, 4, aa & 0xFF, aa >> 8, rom[hv + 5], rom[hv + 6], 0x01, 0x00])
        log.append('%s -> map %d:%d  scripts 63:%04X (%d bytes)' % (n, *mapids[n], base, len(blob)))

    # ================= scene bytes (map scene table, bank 0x61 since phase 21)
    sr = P21.SCENES_REF
    tb = fo(rom[sr], r16(sr + 3)); n_ = 0
    while rom[tb + 4 * n_] != 0xFF: n_ += 1
    tab = bytes(rom[tb:tb + 4 * n_])
    for n, g in MAPS: tab += bytes([*mapids[n], SCENE_BYTE[n] & 0xFF, SCENE_BYTE[n] >> 8])
    at = sp.put(0x61, tab + b'\xff'); rom[sr] = 0x61; w16(sr + 3, at)
    rom[tb:tb + 4 * n_ + 1] = b'\xff' * (4 * n_ + 1)

    # ================= wild Pokémon (Red) -> Kanto grass table
    p = P15.KANTO_GRASS
    while rom[p] != 0xFF: p += 47
    ent = b''
    for n, g in MAPS:
        t = open(PR + '/data/wild/maps/%s.asm' % n, encoding='utf-8').read()
        t = re.sub(r'IF DEF\(_BLUE\).*?ENDC', '', t, flags=re.S)
        rate = int(re.search(r'def_grass_wildmons (\d+)', t).group(1))
        slots = [(int(l), s) for l, s in re.findall(r'db\s+(\d+), (\w+)', t.split('end_grass_wildmons')[0])]
        assert len(slots) == 10, n
        pick = [slots[i] for i in (0, 1, 2, 3, 6, 8, 9)]
        ent += bytes([*mapids[n], rate, rate, rate]) + bytes(sum(([lv, MON[P10.MON_ALIAS.get(s, s)]] for lv, s in pick), [])) * 3
    assert not any(rom[p + 1:p + 1 + len(ent)])
    rom[p:p + len(ent) + 1] = ent + b'\xff'
    log.append('Victory Road wild data (%d bytes)' % len(ent))

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
