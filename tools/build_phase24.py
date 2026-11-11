#!/usr/bin/env python3
"""Phase 24: Route 23 and the Indigo Plateau as in Red / the Pikachu full-color hack, for good (also after the Hall
of Fame):
 * Red's long Route 23 (Gen I Plateau tileset) in place of Crystal's short one, with Red's seven badge guards: stepping
   on a guard's row (or talking to him) checks his badge (Cascade ... Earth); without it, Red's lines, the "wrong"
   sound and one step back down; with it, Red's lines and the "got item" jingle, and he lets the player through for
   good.  Red's sign, the statues (セキエイ　こうげん...), hidden items, wild Pokémon, and the Victory Road boulders reset
   when Route 23 is entered (as in Red).
 * Red's Indigo Plateau (outside) as a new map north of Route 23; its door leads to Crystal's Pokémon League lobby.
   Fly / the last Pokémon Center point there, and it registers the fly point.
 * Crystal's Victory Road Gate stays; its north door leads to the south end of Route 23.  Route 23's caves lead to
   Red's Victory Road (phase 23).
usage: build_phase24.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
import portmaps as PM
import pairwalls
import redtexts
import build_phase10 as P10
import build_phase12 as P12
import build_phase15 as P15
import build_phase17 as P17
import build_phase21 as P21
import build_phase22 as P22

FIRST_FLAG = 195                   # 163-194: phase 23
INDIGO_MAP = 71                    # 26:68-70 = Victory Road (phase 23)
V1, V2 = (26, 68), (26, 69)
BANK = 0x64                        # free in the JP original
SCENE_R23 = 0xDA5F                 # phase 15: EXT_FLAGS end at DA5E
W23, H23, WI, HI = 10, 72, 10, 9
ENV_TOWN, ENV_ROUTE = 1, 2
SPAWN_INDIGO = 0x1537A             # SpawnPoints (JP) entry SPAWN_INDIGO
SPR_OFFICER, SPR_SWIMMER = 0x43, 0x31
SFX_WRONG = 0x19
VAR_X, VAR_Y = 0x12, 0x13
STATUE = 0x30                      # Red: bookshelf_tile PLATEAU, $30, IndigoPlateauStatues (read facing up)
# Red Route23GuardsYCoords / badges (guard 1 = Earth ... guard 7 = Cascade); Crystal engine flags of the Kanto badges
GUARDS = [(35, 0x2A), (56, 0x29), (85, 0x28), (96, 0x27), (105, 0x26), (119, 0x25), (136, 0x24)]
# JP Red: Route 23's badge names (BadgeTextPointers)
BADGE_NAME = {0x2A: 'グリーン', 0x29: 'クリムゾン', 0x28: 'ゴールド', 0x27: 'ピンク', 0x26: 'レインボー', 0x25: 'オレンジ',
              0x24: 'ブルー'}
RED_BADGE_BYTES = 0x519E4          # the same names, as JP Red stores them (07 d8 e3 ab 50 ...)
RED_NO, RED_YES, RED_SIGN = 0x51ABD, 0x51B23, 0x51B78
RED_STATUE1 = 0xFF13
TEXT_RAM_NAME = bytes([0x50, 0x01, 0x68, 0xCD, 0x00])    # text_end, text_ram wNameBuffer, text_start (JP Red)


def connection(direction, cur_w, cur_h, tgt, tgt_w, tgt_h, off, tgt_blocks):
    """pokecrystal's `connection` macro, north/south"""
    PAD = 3; src = 0; tg = off + PAD
    if tg < 0: src = -tg; tg = 0
    ln = min(cur_w + PAD - off, tgt_w)
    if direction == 'north':
        strip = tgt_blocks + tgt_w * (tgt_h - PAD) + src
        mp = tg; win = (tgt_w + 2 * PAD) * tgt_h + 1; y, x = tgt_h * 2 - 1, -2 * off
    elif direction == 'south':
        strip = tgt_blocks + src
        mp = (cur_w + 2 * PAD) * (cur_h + PAD) + tg; win = tgt_w + 2 * PAD + 1; y, x = 0, -2 * off
    else:
        raise ValueError(direction)
    W = P22.W_OVERWORLDMAPBLOCKS
    return bytes([*tgt, strip & 0xFF, strip >> 8, (W + mp) & 0xFF, (W + mp) >> 8, ln - src, tgt_w, y & 0xFF, x & 0xFF,
                  (W + win) & 0xFF, (W + win) >> 8])


def red_raw(o, stop):
    R = redtexts.R; e = R.index(stop, o); return bytes(R[o:e])


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (0x12, 0x13, 0x61, 0x79, BANK):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1 if f > b * 0x4000 else f, b * 0x4000 + 0x4000)
    g0, g1 = fo(0x13, 0x77CD), fo(0x13, 0x77CC + 511)            # bank 13's free gap (phase 19): what is left of it
    while rom[g0] or any(rom[g0:g0 + 0x70]): g0 += 1
    assert not any(rom[g0:g1]); sp.set_area(0x13, g0, g1)
    log = []
    FL = PM.Flags(FIRST_FLAG)
    p23 = json.load(open(os.path.join(os.path.dirname(os.path.abspath(src_rom)), 'p23_flags.json')))
    assert p23['next_flag'] == FIRST_FLAG
    r23, gate, lobby = mapid('Route23'), mapid('VictoryRoadGate'), mapid('IndigoPlateauPokecenter1F')
    indigo = (G26, INDIGO_MAP)
    h23 = hdr_index('Route23'); old = attrs(rom, h23)
    assert (old['w'], old['h'], old['conn']) == (10, 9, 0)
    so = fo(old['scbank'], old['scripts'])
    assert rom[so:so + 3] == bytes([0, 1, 5])                         # Crystal: Route23FlypointCallback (NEWMAP)
    cbo = fo(old['scbank'], r16(so + 3)); assert rom[cbo] == 0x36 and rom[cbo + 3] == 0x8F
    flypoint = r16(cbo + 1)

    # ================= Plateau tileset (Gen I), warp collision per place
    ts = Tileset('Plateau', 23, 'plateau.bst', SC + '/out/pk_plateau.pkl', water=0x14, grass=0x45)
    maps = {'Route23': MapPort('Route23', ts, W23, H23, 'Route23.blk'),
            'IndigoPlateau': MapPort('IndigoPlateau', ts, WI, HI, 'IndigoPlateau.blk')}
    objs_of = {n: PM.objects_of(n) for n in maps}
    tile = lambda mp, x, y: ts.quad_tile(*mp.block_at(x, y))
    ov = {}
    for n, mp in maps.items():
        d = ov[n] = {}
        for x, y, dest, wid in objs_of[n][1]:
            t = tile(mp, x, y)
            if t in ts.warp_tiles and tile(mp, x, y + 1) in ts.passable:
                d[(x, y)] = COLL_STAIRCASE
            else:
                for dd, (dx, dy) in (('down', (0, 1)), ('up', (0, -1)), ('left', (-1, 0)), ('right', (1, 0))):
                    if tile(mp, x + dx, y + dy) not in ts.passable: d[(x, y)] = COLL_CARPET[dd]; break
            assert (x, y) in d, (n, x, y)
    meta2, coll2, blks = pairwalls.variants(ts, bytes(ts.blocks), bytes(ts.coll), maps, [], ov)
    assert len(coll2) // 4 <= 128
    ts.blocks = meta2; ts.coll = bytearray(coll2); ts.nblocks = len(coll2) // 4
    TS = PM.Tilesets(rom, sp)
    plateau = TS.add(ts, BANK, log, anim_src=9)                      # TilesetPortAnim: water only
    for n, mp in maps.items(): mp.blk = blks[n]

    # ================= texts (JP Red)
    names = {}
    R = redtexts.R; o = RED_BADGE_BYTES
    for f in (0x2A, 0x29, 0x28, 0x27, 0x26, 0x25, 0x24):                 # stored in this order in Red
        e = R.index(0x50, o); names[f] = bytes(R[o:e]); o = e + 1
    no_t = red_raw(RED_NO, bytes([0x50, 0x08]))                         # ... text_asm (SFX_DENIED)
    yes_t = red_raw(RED_YES, b'\x57')
    assert no_t.count(TEXT_RAM_NAME) == 2 and yes_t.count(TEXT_RAM_NAME) == 2
    assert yes_t.count(bytes([0x50, 0x0B, 0x00])) == 1
    yes_t = yes_t.replace(bytes([0x50, 0x0B, 0x00]), bytes([0x50, 0x0F, 0x00]))   # sound_get_item_1 -> sound_item
    sign_t = red_raw(RED_SIGN, b'\x57')
    st1 = red_raw(RED_STATUE1, b'\x58')
    o2 = RED_STATUE1 + len(st1) + 1; st2 = red_raw(o2, b'\x57')
    o3 = o2 + len(st2) + 1; st3 = red_raw(o3, b'\x57')
    assert st1[0] == st2[0] == st3[0] == 0

    # ================= Route 23 + Indigo Plateau scripts / events
    a = Asm(sp.here(BANK)); texts = {}
    a.label('end'); a.end()
    # ---- guards
    objs, warps, skip, bgl = objs_of['Route23']
    assert len(objs) == len(GUARDS)
    passed = []
    obj_bytes = []
    for i, ((row, badge), o) in enumerate(zip(GUARDS, objs)):
        assert o['y'] == row
        fl = FL.new(); passed.append(fl)
        spr = SPR_SWIMMER if o['sprite'] == 'SPRITE_SWIMMER' else SPR_OFFICER
        obj_bytes.append([spr, o['y'] + 4, o['x'] + 4, P12.FACE[o['face']], 0, 0xFF, 0xFF, 0, 0, 'o%d' % i, 0xFFFF])
        a.label('o%d' % i); a.faceplayer(); a.sjump('t%d' % i)
        a.label('g%d' % i); a.checkevent(fl); a.iftrue('end')
        a.label('t%d' % i)
        a.opentext(); a.checkflag(badge); a.iftrue('y%d' % i)
        a.writetext('no%d' % i); a.playsound(SFX_WRONG); a.waitsfx(); a.waitbutton(); a.closetext()
        a.applymovement(0, 'mdown'); a.end()
        a.label('y%d' % i); a.writetext('yes%d' % i); a.waitbutton(); a.closetext(); a.setevent(fl); a.end()
        texts['no%d' % i] = no_t.replace(TEXT_RAM_NAME, names[badge])
        texts['yes%d' % i] = yes_t.replace(TEXT_RAM_NAME, names[badge])
    a.label('mdown'); a.db(0x0C, 0x47)
    # Red: Route23DefaultScript, every frame
    a.label('scene0')
    a.db(0x1C, VAR_Y)                                                         # readvar
    for i, (row, badge) in enumerate(GUARDS):
        a.ifequal(row, 'g%d' % i if i else 'r35')
    a.end()
    a.label('r35'); a.db(0x1C, VAR_X); a.db(0x0A, 13); a.dw('end'); a.sjump('g0')   # ifgreater 13: past Victory Road
    # Red: Route23SetVictoryRoadBoulders (entering Route 23)
    a.label('cb_new')
    for f in p23['v2_sw'] + p23['v3_sw'] + [p23['hole']] + p23['v3_boulders']: a.clearevent(f)
    a.setevent(p23['v2_boulder3'])
    a.endcallback()
    # ---- statues, sign, hidden items
    def statue_bgs(mp):
        out = []
        for y in range(mp.h * 2 - 1):
            for x in range(mp.w * 2):
                if tile(mp, x, y) == STATUE and tile(mp, x, y + 1) in set(ts.passable) | {ts.water}:
                    out.append((y, x, 1, 'statue_odd' if x % 2 else 'statue_even'))   # BGEVENT_UP
        return out
    a.label('statue_odd'); a.jumptext('st_odd'); a.label('statue_even'); a.jumptext('st_even')
    texts['st_odd'] = st1 + b'\x51' + st2[1:]
    texts['st_even'] = st1 + b'\x51' + st3[1:]
    bgs = {'Route23': [], 'IndigoPlateau': []}
    for k, (x, y, tconst) in enumerate(bgl):
        a.label('sign%d' % k); a.jumptext('signt'); bgs['Route23'].append((y, x, 0, 'sign%d' % k))
    texts['signt'] = sign_t
    for k, (x, y, fn, arg) in enumerate(PM.hidden_events('ROUTE_23')):
        assert fn == 'HiddenItems'
        L = 'hi%d' % k; a.label(L); a.dw(FL.new()); a.db(PM.item_id(arg)); bgs['Route23'].append((y, x, 7, L))
    for n, mp in maps.items(): bgs[n] += statue_bgs(mp)
    # ---- Indigo Plateau: the fly point
    a.label('cb_fly'); a.setflag(flypoint); a.endcallback()
    for k_, v in texts.items():
        a.label(k_); a.raw(P12.text(v))
    # map scripts / events
    a.label('ms23'); a.db(1); a.dw('scene0'); a.dw(0); a.db(1, 5); a.dw('cb_new')
    a.label('msi'); a.db(0, 1, 5); a.dw('cb_fly')
    a.label('ev23'); a.db(0, 0)
    w23 = []
    for x, y, dest, wid in warps:
        if dest == 'ROUTE_22_GATE': w23.append((y, x, wid + 2, *gate))          # Red gate warps 3/4 = Crystal gate 5/6
        elif dest == 'VICTORY_ROAD_1F': w23.append((y, x, wid, *V1))
        elif dest == 'VICTORY_ROAD_2F': w23.append((y, x, wid, *V2))
        else: raise AssertionError(dest)
    a.db(len(w23))
    for w_ in w23: a.db(*w_)
    a.db(0)
    a.db(len(bgs['Route23']))
    for (y_, x_, t_, l_) in bgs['Route23']: a.db(y_, x_, t_); a.dw(l_)
    a.db(len(obj_bytes))
    for ob in obj_bytes: a.db(*ob[:9]); a.dw(ob[9]); a.dw(ob[10])
    a.label('evi'); a.db(0, 0)
    wi = objs_of['IndigoPlateau'][1]
    assert [(x, y, d) for x, y, d, w in wi] == [(9, 5, 'INDIGO_PLATEAU_LOBBY'), (10, 5, 'INDIGO_PLATEAU_LOBBY')]
    a.db(2); a.db(5, 9, 1, *lobby); a.db(5, 10, 2, *lobby)
    a.db(0)
    a.db(len(bgs['IndigoPlateau']))
    for (y_, x_, t_, l_) in bgs['IndigoPlateau']: a.db(y_, x_, t_); a.dw(l_)
    a.db(0)
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    L = a.labels
    log.append('Route 23 / Indigo Plateau scripts %X:%04X (%d bytes), statues %d + %d'
               % (BANK, base, len(blob), sum(1 for b in bgs['Route23'] if b[3].startswith('statue')),
                  len(bgs['IndigoPlateau'])))

    # ================= blocks, attributes, connections, headers
    b23 = sp.put(BANK, maps['Route23'].blk); bi = sp.put(BANK, maps['IndigoPlateau'].blk)
    north = connection('north', W23, H23, indigo, WI, HI, 0, bi)
    south = connection('south', WI, HI, r23, W23, H23, 0, b23)
    def attr(border, h, w, blk, ms, ev, conn, conns):
        return bytes([border, h, w, BANK, blk & 0xFF, blk >> 8, BANK, ms & 0xFF, ms >> 8, ev & 0xFF, ev >> 8, conn]) + conns
    a23 = sp.put(BANK, attr(border_of('Route23'), H23, W23, b23, L['ms23'], L['ev23'], 0x08, north))
    ai = sp.put(BANK, attr(border_of('IndigoPlateau'), HI, WI, bi, L['msi'], L['evi'], 0x04, south))
    hl = hdr_index('IndigoPlateauPokecenter1F')
    landmark_indigo = rom[hl + 5]
    rom[h23:h23 + 9] = bytes([BANK, plateau, ENV_ROUTE, a23 & 0xFF, a23 >> 8, rom[h23 + 5], rom[h23 + 6], rom[h23 + 7], rom[h23 + 8]])
    # header 26:71 (after the last group's headers; move what lies there)
    u = US.get(); G = u.groups()
    lo = GROUP26_END + 9 * (INDIGO_MAP - G26_COUNT - 1); hi = lo + 9
    for gi in range(26):
        n_ = (G[gi + 1] - G[gi]) // 9 if gi + 1 < 26 else INDIGO_MAP - 1
        for k in range(n_):
            hdr = G[gi] + 9 * k
            ab = rom[hdr]; ap = r16(hdr + 3); ao = fo(ab, ap)
            nconn = bin(rom[ao + 11] & 0xF).count('1'); size = 12 + 12 * nconn
            if ao < hi and ao + size > lo:
                rom[hdr] = 0x79; w16(hdr + 3, sp.put(0x79, bytes(rom[ao:ao + size])))
                log.append('moved map attributes %X:%04X' % (ab, ap))
    rom[lo:hi] = bytes([BANK, plateau, ENV_TOWN, ai & 0xFF, ai >> 8, landmark_indigo, rom[h23 + 6], rom[h23 + 7], rom[h23 + 8]])
    log.append('Route23 -> Red (%dx%d), attributes %X:%04X; Indigo Plateau -> map %d:%d, attributes %X:%04X'
               % (W23, H23, BANK, a23, *indigo, BANK, ai))

    # ================= the doors around
    def patch_warps(owner, fix):
        a_ = attrs(rom, hdr_index(owner)); ev = parse_events(rom, a_['scbank'], a_['events'])
        for i, (wid, tgt) in fix.items():
            o_ = ev['warps'][i - 1][0]; rom[o_ + 2] = wid; rom[o_ + 3], rom[o_ + 4] = tgt
    ag = attrs(rom, hdr_index('VictoryRoadGate')); evg = parse_events(rom, ag['scbank'], ag['events'])
    assert [bytes(evg['warps'][i][1][:2]) for i in (4, 5)] == [bytes([0, 9]), bytes([0, 10])]
    patch_warps('VictoryRoadGate', {5: (1, r23), 6: (2, r23)})
    al = attrs(rom, hl); evl = parse_events(rom, al['scbank'], al['events'])
    assert [(w[3], w[4]) for _, w in evl['warps'][:2]] == [r23, r23]
    patch_warps('IndigoPlateauPokecenter1F', {1: (1, indigo), 2: (2, indigo)})
    assert rom[SPAWN_INDIGO:SPAWN_INDIGO + 4] == bytes([*r23, 9, 6])
    rom[SPAWN_INDIGO:SPAWN_INDIGO + 4] = bytes([*indigo, 9, 6])

    # ================= scene byte for Route 23 (map scene table, bank 0x61)
    sr = P21.SCENES_REF
    tb = fo(rom[sr], r16(sr + 3)); n_ = 0
    while rom[tb + 4 * n_] != 0xFF: n_ += 1
    tab = bytes(rom[tb:tb + 4 * n_]) + bytes([*r23, SCENE_R23 & 0xFF, SCENE_R23 >> 8])
    assert max(P15.EXT_FLAGS) < 0x800 + 8 * (SCENE_R23 - 0xDA01)
    at = sp.put(0x61, tab + b'\xff'); rom[sr] = 0x61; w16(sr + 3, at)
    rom[tb:tb + 4 * n_ + 1] = b'\xff' * (4 * n_ + 1)

    # ================= wild Pokémon (Red's grass; no water ones) -> Kanto grass table
    p = P15.KANTO_GRASS
    while rom[p] != 0xFF: p += 47
    t = open(PR + '/data/wild/maps/Route23.asm', encoding='utf-8').read()
    t = re.sub(r'IF DEF\(_BLUE\).*?ENDC', '', t, flags=re.S)
    rate = int(re.search(r'def_grass_wildmons (\d+)', t).group(1))
    slots = [(int(l), s) for l, s in re.findall(r'db\s+(\d+), (\w+)', t.split('end_grass_wildmons')[0])]
    assert len(slots) == 10
    pick = [slots[i] for i in (0, 1, 2, 3, 6, 8, 9)]
    ent = bytes([*r23, rate, rate, rate]) + bytes(sum(([lv, PM.MON[P10.MON_ALIAS.get(s, s)]] for lv, s in pick), [])) * 3
    assert not any(rom[p + 1:p + 1 + len(ent)])
    rom[p:p + len(ent) + 1] = ent + b'\xff'

    P17.fix_outdoor_sprites(rom, log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
